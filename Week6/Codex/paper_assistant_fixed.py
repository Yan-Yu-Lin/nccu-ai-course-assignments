#!/usr/bin/env python3
"""Corrected Paper Reading Assistant using the OpenAI Responses API."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Dict, Optional, Any

import gradio as gr
import PyPDF2

try:
    from google.colab import userdata  # type: ignore
except ImportError:  # pragma: no cover - fallback for local runs
    userdata = None

from openai import OpenAI


# --- OpenAI client bootstrap -------------------------------------------------

def _resolve_api_key() -> Optional[str]:
    if userdata is not None:
        key = userdata.get("OpenAI")
        if key:
            return key
    return os.getenv("OPENAI_API_KEY")


api_key = _resolve_api_key()
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key

client = OpenAI()
MODEL_NAME = "gpt-5"


# --- Prompt scaffolding ------------------------------------------------------

SYSTEM_PROMPT = (
    "你是一位專業的論文閱讀助手。運用費曼學習法與蘇格拉底式提問法，用清楚、友善的語氣"
    "協助學生理解論文內容與研究方法；如果問題與上傳的論文無關，也要以一般 AI 助手的身份給予"
    "完整、實用的解答。"
)

PDF_CONTEXT_TEMPLATE = (
    "以下是使用者提供的論文內容 (檔名: {filename}, 版本: {version})，回答時務必引用此內容：\n"
    "{content}"
)

MAX_PDF_CHARS = 15000  # 防止超量 token，提醒使用者分段提問


# --- Stateful containers -----------------------------------------------------

@dataclass
class PDFState:
    filename: Optional[str] = None
    content: Optional[str] = None
    version: int = 0

    def context_message(self) -> Optional[Dict[str, str]]:
        if not self.content or not self.filename:
            return None
        return {
            "role": "user",
            "content": PDF_CONTEXT_TEMPLATE.format(
                filename=self.filename,
                version=self.version,
                content=self.content,
            ),
        }


conversation_history: List[Dict[str, str]] = []
last_response_id: Optional[str] = None
pdf_state = PDFState()


# --- Helpers -----------------------------------------------------------------

def extract_pdf_text(pdf_path: str) -> str:
    if not pdf_path:
        raise ValueError("未提供 PDF 檔案")

    text_segments: List[str] = []
    try:
        with open(pdf_path, "rb") as handle:
            pdf_reader = PyPDF2.PdfReader(handle)
            if not pdf_reader.pages:
                raise ValueError("PDF 中沒有可用頁面")

            for index, page in enumerate(pdf_reader.pages, start=1):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    text_segments.append(f"\n--- Page {index} ---\n{page_text.strip()}")

    except Exception as exc:  # PyPDF2 raises many custom exceptions
        raise ValueError(f"PDF 讀取失敗: {exc}") from exc

    if not text_segments:
        raise ValueError("PDF 中沒有可讀取的文字內容")

    combined = "".join(text_segments)
    if len(combined) > MAX_PDF_CHARS:
        combined = combined[:MAX_PDF_CHARS] + "\n\n... (內容過長，已截斷。請分段提問以獲得完整解說。)"
    return combined


def summarise_outputs(response: Any) -> str:
    if getattr(response, "output_text", None):
        return response.output_text

    collected: List[str] = []
    for item in getattr(response, "output", []) or []:
        if item.get("type") != "message":
            continue
        for chunk in item.get("content", []):
            if chunk.get("type") == "output_text" and chunk.get("text"):
                collected.append(chunk["text"])

    return "".join(collected).strip()


def ensure_history(history: Optional[List[List[str]]]) -> List[List[str]]:
    return list(history) if history else []


# --- Core chat logic ---------------------------------------------------------

def chat_with_paper(message: str, history: Optional[List[List[str]]]):
    global conversation_history, last_response_id

    history = ensure_history(history)
    user_message = (message or "").strip()
    if not user_message:
        return history

    messages: List[Dict[str, str]] = [{"role": "developer", "content": SYSTEM_PROMPT}]

    pdf_context = pdf_state.context_message()
    if pdf_context:
        messages.append(pdf_context)

    messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})

    request_payload = {
        "model": MODEL_NAME,
        "input": messages,
        "reasoning": {"effort": "medium"},
        "text": {"verbosity": "medium"},
    }
    if last_response_id:
        request_payload["previous_response_id"] = last_response_id

    try:
        response = client.responses.create(**request_payload)
        assistant_reply = summarise_outputs(response)
        if not assistant_reply:
            assistant_reply = "⚠️ 模型未回傳文字，可再試一次或調整問題。"

        conversation_history.append({"role": "user", "content": user_message})
        conversation_history.append({"role": "assistant", "content": assistant_reply})
        last_response_id = getattr(response, "id", None)

        history.append([user_message, assistant_reply])
        return history

    except Exception as exc:
        error_message = f"❌ 發生錯誤：{exc}\n\n請檢查網路連線與 API 設定後再試一次。"
        history.append([user_message, error_message])
        return history


def upload_pdf(pdf_file: Optional[str]):
    global pdf_state

    if pdf_file is None:
        return "❌ 請選擇 PDF 檔案"

    try:
        content = extract_pdf_text(pdf_file)
    except ValueError as exc:
        pdf_state = PDFState()  # 保持狀態一致
        return f"❌ {exc}"

    pdf_state = PDFState(
        filename=os.path.basename(pdf_file),
        content=content,
        version=pdf_state.version + 1,
    )

    page_count = content.count("--- Page") or "?"
    char_count = len(content)

    note = (
        "✅ PDF 上傳成功！\n\n"
        f"📄 檔名：{pdf_state.filename}\n"
        f"📄 版本：{pdf_state.version}\n"
        f"📄 頁面數：約 {page_count}\n"
        f"🔤 文字長度：約 {char_count:,} 字元\n\n"
        "💬 你可以直接提問，我會依據最新的 PDF 回答。"
    )
    return note


def clear_conversation():
    global conversation_history, last_response_id
    conversation_history = []
    last_response_id = None
    return [], "🔄 對話已清除！PDF 設定保持不變。"


# --- Gradio UI ---------------------------------------------------------------

WELCOME_MESSAGE = (
    "👋 嗨！我是你的論文閱讀助手。\n\n"
    "📄 上傳 PDF 後，我會根據內容用簡單語言講解；若沒有 PDF，也可以直接與我聊天。\n"
    "💡 你可以隨時重新上傳新的 PDF，對話歷史會保留。"
)


with gr.Blocks(title="論文閱讀助手 (Fixed)", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📚 論文閱讀助手 - Paper Reading Assistant (Fixed Edition)")
    gr.Markdown("使用 OpenAI Responses API，支援 PDF 與一般對話雙模式。")

    with gr.Row():
        with gr.Column(scale=3):
            pdf_upload = gr.File(
                label="📄 上傳論文 PDF",
                file_types=[".pdf"],
                type="filepath",
            )
            upload_status = gr.Textbox(
                label="上傳狀態",
                value=WELCOME_MESSAGE,
                interactive=False,
                lines=10,
            )

        with gr.Column(scale=7):
            chatbot = gr.Chatbot(
                label="💬 對話區",
                height=500,
                type="tuples",
            )
            msg_input = gr.Textbox(
                label="輸入你的問題",
                placeholder="例如：這篇論文的主要貢獻是什麼？",
                lines=2,
            )

            with gr.Row():
                submit_btn = gr.Button("📤 送出", variant="primary")
                clear_btn = gr.Button("🔄 清除對話")

    pdf_upload.change(upload_pdf, inputs=pdf_upload, outputs=upload_status)

    submit_btn.click(
        fn=chat_with_paper,
        inputs=[msg_input, chatbot],
        outputs=chatbot,
    ).then(lambda: "", outputs=msg_input)

    msg_input.submit(
        fn=chat_with_paper,
        inputs=[msg_input, chatbot],
        outputs=chatbot,
    ).then(lambda: "", outputs=msg_input)

    clear_btn.click(fn=clear_conversation, outputs=[chatbot, upload_status])

    gr.Markdown(
        """
---
### 使用建議

- 首次提問可先請我用一句話概述論文。
- 如果文字過長被截斷，請嘗試分章節提問。
- 重新上傳 PDF 後，直接提問即可，我會參考最新版本。
        """
    )


if __name__ == "__main__":
    demo.launch(share=True, debug=True)
