#!/usr/bin/env python3
"""
Python script generated from: Week6/論文閱讀助手.md
Generated on: 1760867432.7444682
Note: Colab-specific commands (!pip, %magic) have been commented out
"""

# COLAB ONLY: !pip install openai gradio pypdf2

from google.colab import userdata
import os

api_key = userdata.get('OpenAI')
os.environ['OPENAI_API_KEY'] = api_key

from openai import OpenAI
import gradio as gr
import PyPDF2
from dataclasses import dataclass
from typing import List, Dict, Optional, Any

client = OpenAI()
MODEL_NAME = "gpt-5"

def extract_pdf_text(pdf_path: str) -> str:
    """
    從上傳的 PDF 檔案中提取文字內容

    這個函數會：
    1. 逐頁讀取 PDF 內容
    2. 過濾掉空白頁面
    3. 標記頁碼方便定位
    4. 限制最大長度避免超過 Token 限制

    Args:
        pdf_path: PDF 檔案路徑

    Returns:
        str: 提取的文字內容

    Raises:
        ValueError: 當 PDF 無法讀取或內容為空時
    """
    if not pdf_path:
        raise ValueError("未提供 PDF 檔案")

    text_segments: List[str] = []

    try:
        with open(pdf_path, "rb") as handle:
            pdf_reader = PyPDF2.PdfReader(handle)

            if not pdf_reader.pages:
                raise ValueError("PDF 中沒有可用頁面")

            # 逐頁提取文字
            for index, page in enumerate(pdf_reader.pages, start=1):
                # 注意：page.extract_text() 可能回傳 None，需要處理
                page_text = page.extract_text() or ""

                # 只加入有內容的頁面
                if page_text.strip():
                    text_segments.append(f"\n--- Page {index} ---\n{page_text.strip()}")

    except Exception as exc:
        raise ValueError(f"PDF 讀取失敗: {exc}") from exc

    if not text_segments:
        raise ValueError("PDF 中沒有可讀取的文字內容")

    # 合併所有頁面
    combined = "".join(text_segments)

    # 防止超過 Token 限制（約 15000 字元）
    MAX_PDF_CHARS = 15000
    if len(combined) > MAX_PDF_CHARS:
        combined = combined[:MAX_PDF_CHARS] + "\n\n... (內容過長，已截斷。請分段提問以獲得完整解說。)"

    return combined

SYSTEM_PROMPT = """你是一位專業的論文閱讀助手，專門幫助學生理解學術論文。

**你的教學原則**：

1. **費曼學習法 (Feynman Technique)**：
   - 用最簡單的語言解釋複雜概念
   - 使用類比和日常生活的例子
   - 避免過度使用專業術語，必要時要先解釋

2. **蘇格拉底式提問 (Socratic Method)**：
   - 不直接給答案，而是引導學生思考
   - 提出啟發性問題，幫助學生自己找到答案
   - 鼓勵批判性思維

3. **結構化分析**：
   - 幫助學生理解論文結構：摘要、引言、方法、結果、結論
   - 指出論文的核心貢獻和創新點
   - 解釋研究方法和實驗設計

4. **友善互動**：
   - 以鼓勵和支持的語氣回應
   - 確認學生理解後再繼續
   - 可以用 emoji 讓對話更生動

**當學生上傳論文後**：
- 等待學生提問，不要主動摘要
- 根據學生的問題，從論文中找到相關內容回答
- 確保回答準確且基於論文內容

**記住**：你的目標是幫助學生「學會如何讀論文」，而不只是「讀懂這篇論文」。"""

WELCOME_MESSAGE = """👋 嗨！我是你的**論文閱讀助手 & AI 對話夥伴**！

📚 **我能幫你做什麼？**

**模式 1：論文閱讀助手** 📄
- 上傳 PDF 論文後，我會幫你：
  - 用簡單的語言解釋論文中的複雜概念
  - 幫你理解研究方法和實驗設計
  - 引導你思考論文的核心貢獻
  - 回答你對論文內容的任何疑問

**模式 2：一般 AI 助手** 💬
- 不上傳 PDF 也可以直接跟我聊天：
  - 學習任何主題
  - 解答問題
  - 討論想法
  - 寫作協助

🚀 **如何開始？**
- **想讀論文？** 點擊上方「上傳 PDF」按鈕
- **想聊天？** 直接開始提問即可！

💡 **提問範例**：
- 📖 論文相關：「這篇論文的主要貢獻是什麼？」
- 💬 一般對話：「解釋一下機器學習的基本概念」

準備好了嗎？開始你的探索之旅吧！ 🚀✨"""

PDF_CONTEXT_TEMPLATE = (
    "以下是使用者提供的論文內容 (檔名: {filename}, 版本: {version})，回答時務必引用此內容：\n"
    "{content}"
)

@dataclass
class PDFState:
    """
    管理 PDF 狀態的資料類別

    Attributes:
        filename: PDF 檔名
        content: 提取的文字內容
        version: PDF 版本號（每次上傳新 PDF 會遞增）
    """
    filename: Optional[str] = None
    content: Optional[str] = None
    version: int = 0

    def context_message(self) -> Optional[Dict[str, str]]:
        """
        產生包含 PDF 內容的訊息物件

        這個訊息會在每次 API 呼叫時插入，確保模型知道當前的 PDF 內容。
        使用版本號可以讓模型區分不同的 PDF。

        Returns:
            包含 PDF 內容的 user 訊息，如果沒有 PDF 則回傳 None
        """
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


# 全域狀態變數
conversation_history: List[Dict[str, str]] = []  # 儲存對話歷史（user 和 assistant 訊息）
last_response_id: Optional[str] = None  # Response API 的 previous_response_id
pdf_state = PDFState()  # PDF 狀態

def summarise_outputs(response: Any) -> str:
    """
    從 Response API 的回應中提取文字內容

    Response API 的輸出格式比較複雜，可能包含：
    - output_text: 直接的文字輸出（最常見）
    - output: 包含多個 message 物件的陣列（需要手動解析）

    這個函數會嘗試兩種方式，確保能取得內容。

    Args:
        response: OpenAI Response API 的回應物件

    Returns:
        str: 提取的文字內容
    """
    # 優先使用 output_text
    if getattr(response, "output_text", None):
        return response.output_text

    # 如果沒有 output_text，手動解析 output 陣列
    collected: List[str] = []
    for item in getattr(response, "output", []) or []:
        if item.get("type") != "message":
            continue
        for chunk in item.get("content", []):
            if chunk.get("type") == "output_text" and chunk.get("text"):
                collected.append(chunk["text"])

    return "".join(collected).strip()


def ensure_history(history: Optional[List[List[str]]]) -> List[List[str]]:
    """
    確保 Gradio history 是有效的列表

    Gradio 在第一次呼叫時可能傳入 None，這會導致錯誤。
    這個函數確保我們總是有一個有效的列表可以操作。

    Args:
        history: Gradio 傳入的對話歷史（可能是 None）

    Returns:
        有效的對話歷史列表
    """
    return list(history) if history else []

def chat_with_paper(message: str, history: Optional[List[List[str]]]):
    """
    處理使用者訊息並產生回應

    **重要改進**（相較於原本的實作）：
    1. ✅ 正確儲存 user 和 assistant 訊息到 conversation_history
    2. ✅ 每次呼叫都重新注入 PDF 內容（支援重新上傳）
    3. ✅ 使用 previous_response_id 維護 Response API 的狀態
    4. ✅ 處理 history=None 的邊界情況
    5. ✅ 處理空白輸出的情況

    支援兩種模式：
    1. 有 PDF：論文閱讀助手模式
    2. 無 PDF：一般 AI 助手模式

    Args:
        message: 使用者當前輸入
        history: Gradio 聊天歷史 [[user_msg, bot_msg], ...]

    Returns:
        list: 更新後的 Gradio 歷史記錄（必須是 list of lists 格式）
    """
    global conversation_history, last_response_id

    # 確保 history 是有效的列表
    history = ensure_history(history)

    # 過濾空白訊息
    user_message = (message or "").strip()
    if not user_message:
        return history

    # === 步驟 1: 建構訊息陣列 ===
    messages: List[Dict[str, str]] = [
        {"role": "developer", "content": SYSTEM_PROMPT}
    ]

    # === 步驟 2: 如果有 PDF，注入 PDF 內容 ===
    # 注意：每次都重新注入，這樣重新上傳 PDF 時模型會知道
    pdf_context = pdf_state.context_message()
    if pdf_context:
        messages.append(pdf_context)

    # === 步驟 3: 加入對話歷史 ===
    # 這裡包含之前所有的 user 和 assistant 訊息
    messages.extend(conversation_history)

    # === 步驟 4: 加入當前使用者訊息 ===
    messages.append({"role": "user", "content": user_message})

    # === 步驟 5: 準備 API 請求 ===
    request_payload = {
        "model": MODEL_NAME,
        "input": messages,
        "reasoning": {"effort": "medium"},
        "text": {"verbosity": "medium"}
    }

    # 如果有上一次的 response_id，加入以維持推理連續性
    if last_response_id:
        request_payload["previous_response_id"] = last_response_id

    try:
        # === 步驟 6: 呼叫 OpenAI Response API ===
        response = client.responses.create(**request_payload)

        # === 步驟 7: 提取回應文字 ===
        assistant_reply = summarise_outputs(response)

        # 如果沒有文字輸出（罕見但可能發生），提供友善的錯誤訊息
        if not assistant_reply:
            assistant_reply = "⚠️ 模型未回傳文字，可再試一次或調整問題。"

        # === 步驟 8: 更新對話歷史（重要！）===
        # 儲存 user 和 assistant 訊息，這樣下次呼叫時模型才知道之前的對話
        conversation_history.append({"role": "user", "content": user_message})
        conversation_history.append({"role": "assistant", "content": assistant_reply})

        # === 步驟 9: 儲存 response_id ===
        last_response_id = getattr(response, "id", None)

        # === 步驟 10: 更新 Gradio 顯示的歷史 ===
        history.append([user_message, assistant_reply])
        return history

    except Exception as exc:
        # 錯誤處理：同樣回傳 Gradio 格式
        error_message = f"❌ 發生錯誤：{exc}\n\n請檢查網路連線與 API 設定後再試一次。"
        history.append([user_message, error_message])
        return history


def upload_pdf(pdf_file: Optional[str]):
    """
    處理 PDF 上傳

    **重要改進**：
    1. ✅ 更新 pdf_state 的版本號，讓模型知道是新的 PDF
    2. ✅ 保留 conversation_history（對話歷史不會因為上傳 PDF 而消失）
    3. ✅ 下次提問時會自動注入新的 PDF 內容

    Args:
        pdf_file: Gradio 上傳的檔案路徑

    Returns:
        str: 上傳狀態訊息
    """
    global pdf_state

    if pdf_file is None:
        return "❌ 請選擇 PDF 檔案"

    try:
        # 提取 PDF 文字
        content = extract_pdf_text(pdf_file)
    except ValueError as exc:
        # 如果提取失敗，重置 PDF 狀態
        pdf_state = PDFState()
        return f"❌ {exc}"

    # 更新 PDF 狀態（版本號遞增）
    pdf_state = PDFState(
        filename=os.path.basename(pdf_file),
        content=content,
        version=pdf_state.version + 1,
    )

    # 計算統計資訊
    page_count = content.count("--- Page") or "?"
    char_count = len(content)

    # 產生友善的成功訊息
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
    """
    清除對話歷史，重新開始

    注意：只清除對話歷史，PDF 設定保持不變

    Returns:
        tuple: (清空的聊天歷史, 狀態訊息)
    """
    global conversation_history, last_response_id

    conversation_history = []
    last_response_id = None

    return [], "🔄 對話已清除！PDF 設定保持不變。"

# 建立 Gradio 介面
with gr.Blocks(title="論文閱讀助手", theme=gr.themes.Soft()) as demo:

    gr.Markdown("# 📚 論文閱讀助手 - Paper Reading Assistant")
    gr.Markdown("基於 OpenAI GPT-5 Response API，結合費曼學習法與蘇格拉底式提問")

    with gr.Row():
        with gr.Column(scale=3):
            # PDF 上傳區
            pdf_upload = gr.File(
                label="📄 上傳論文 PDF",
                file_types=[".pdf"],
                type="filepath"
            )
            upload_status = gr.Textbox(
                label="上傳狀態",
                value=WELCOME_MESSAGE,
                interactive=False,
                lines=10
            )

        with gr.Column(scale=7):
            # 聊天區
            chatbot = gr.Chatbot(
                label="💬 對話區",
                height=500,
                show_label=True,
                type="tuples"  # 明確指定使用 tuples 格式
            )

            msg_input = gr.Textbox(
                label="輸入你的問題",
                placeholder="例如：這篇論文的主要貢獻是什麼？",
                lines=2
            )

            with gr.Row():
                submit_btn = gr.Button("📤 送出", variant="primary")
                clear_btn = gr.Button("🔄 清除對話")

    # 事件綁定
    pdf_upload.change(
        fn=upload_pdf,
        inputs=pdf_upload,
        outputs=upload_status
    )

    submit_btn.click(
        fn=chat_with_paper,
        inputs=[msg_input, chatbot],
        outputs=chatbot
    ).then(
        lambda: "",  # 清空輸入框
        outputs=msg_input
    )

    msg_input.submit(
        fn=chat_with_paper,
        inputs=[msg_input, chatbot],
        outputs=chatbot
    ).then(
        lambda: "",  # 清空輸入框
        outputs=msg_input
    )

    clear_btn.click(
        fn=clear_conversation,
        outputs=[chatbot, upload_status]
    )

    # 說明區
    gr.Markdown("""
    ---
    ### 💡 使用技巧

    - **第一次提問**：建議先問「這篇論文在研究什麼？」了解全貌
    - **深入理解**：針對不懂的章節或概念提問
    - **批判思考**：可以問「這個方法有什麼限制？」
    - **清除對話**：想重新開始時，點擊「清除對話」按鈕
    - **重新上傳 PDF**：可以隨時上傳新的 PDF，對話歷史會保留

    ### ⚙️ 技術說明

    - **模型**：OpenAI GPT-5 (Response API)
    - **推理等級**：Medium (平衡速度與品質)
    - **PDF 處理**：PyPDF2 (完整文字提取)
    - **介面框架**：Gradio 5.x

    ---
    *Made with ❤️ for NCCU AI Course*
    """)

# 啟動 Gradio 應用
demo.launch(share=True, debug=True)

# ❌ 舊版 Chat Completions API
response = client.chat.completions.create(
    model="gpt-4",
    messages=[...]
)
reply = response.choices[0].message.content

# ✅ 新版 Response API
response = client.responses.create(
    model="gpt-5",
    input=[...],
    reasoning={"effort": "medium"},
    text={"verbosity": "medium"}
)
reply = response.output_text

# ❌ 只儲存 assistant 的回應
conversation_history.extend(response.output)

# ✅ 同時儲存 user 和 assistant 訊息
conversation_history.append({"role": "user", "content": user_message})
conversation_history.append({"role": "assistant", "content": assistant_reply})

# ✅ 每次呼叫都重新注入 PDF 內容
pdf_context = pdf_state.context_message()
if pdf_context:
    messages.append(pdf_context)

# ❌ 直接把 response.output 放回 input
conversation_history.extend(response.output)

# ✅ 正確使用 previous_response_id
last_response_id = getattr(response, "id", None)
if last_response_id:
    request_payload["previous_response_id"] = last_response_id

