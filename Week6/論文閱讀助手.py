#!/usr/bin/env python3
"""
Python script generated from: Week6/論文閱讀助手.md
Generated on: 1760865755.1443665
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
import io

client = OpenAI()
model = "gpt-5"

def extract_pdf_text(pdf_file):
    """
    從上傳的 PDF 檔案中提取文字內容

    Args:
        pdf_file: Gradio 上傳的檔案物件

    Returns:
        str: 提取的文字內容
    """
    if pdf_file is None:
        return None

    try:
        # 讀取 PDF 檔案
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # 提取所有頁面的文字
        text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"

        return text

    except Exception as e:
        return f"❌ PDF 讀取失敗：{str(e)}"

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

# 全域狀態
pdf_content = None
conversation_history = []

def chat_with_paper(message, history):
    """
    處理使用者訊息並產生回應

    支援兩種模式：
    1. 有 PDF：論文閱讀助手模式
    2. 無 PDF：一般 AI 助手模式

    Args:
        message: 使用者當前輸入
        history: Gradio 聊天歷史 [[user_msg, bot_msg], ...]

    Returns:
        list: 更新後的 Gradio 歷史記錄（必須是 list of lists 格式）
    """
    global pdf_content, conversation_history

    try:
        # 建構訊息列表
        messages = [
            {"role": "developer", "content": SYSTEM_PROMPT}
        ]

        # === 情況 1：有 PDF，論文閱讀模式 ===
        if pdf_content is not None and not pdf_content.startswith("❌"):
            # 第一次提問時，包含 PDF 內容
            if len(conversation_history) == 0:
                messages.append({
                    "role": "user",
                    "content": f"以下是我要閱讀的論文內容：\n\n{pdf_content}\n\n---\n\n現在我的問題是：{message}"
                })
            else:
                # 後續對話，加入歷史訊息
                messages.extend(conversation_history)
                messages.append({
                    "role": "user",
                    "content": message
                })

        # === 情況 2：無 PDF 或 PDF 讀取失敗，一般聊天模式 ===
        else:
            # 加入對話歷史（如果有的話）
            if len(conversation_history) > 0:
                messages.extend(conversation_history)

            # 加入當前使用者訊息
            messages.append({
                "role": "user",
                "content": message
            })

        # 呼叫 OpenAI Response API
        response = client.responses.create(
            model=model,
            input=messages,
            reasoning={"effort": "medium"},
            text={"verbosity": "medium"}
        )

        # 取得回應
        reply = response.output_text

        # 更新對話歷史（包含完整的 output）
        conversation_history.extend(response.output)

        # 更新 Gradio 顯示的歷史（重要！必須回傳 Gradio 格式）
        return history + [[message, reply]]

    except Exception as e:
        # 錯誤處理：同樣回傳 Gradio 格式
        error_msg = f"❌ 發生錯誤：{str(e)}\n\n請檢查您的 API Key 是否正確設定。"
        return history + [[message, error_msg]]


def upload_pdf(pdf_file):
    """
    處理 PDF 上傳

    Args:
        pdf_file: Gradio 上傳的檔案

    Returns:
        str: 上傳狀態訊息
    """
    global pdf_content, conversation_history

    if pdf_file is None:
        return "❌ 請選擇 PDF 檔案"

    # 提取 PDF 文字
    pdf_content = extract_pdf_text(pdf_file)

    # 重置對話歷史
    conversation_history = []

    if pdf_content and not pdf_content.startswith("❌"):
        # 計算字數
        char_count = len(pdf_content)
        page_count = pdf_content.count("--- Page")

        return f"✅ PDF 上傳成功！\n\n📄 共 {page_count} 頁，約 {char_count:,} 字元\n\n💬 現在可以開始向我提問了！"
    else:
        return pdf_content  # 回傳錯誤訊息


def clear_conversation():
    """
    清除對話歷史，重新開始

    Returns:
        tuple: (清空的聊天歷史, 狀態訊息)
    """
    global conversation_history
    conversation_history = []

    return [], "🔄 對話已清除！你可以重新提問，或上傳新的 PDF。"

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
                lines=8
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

