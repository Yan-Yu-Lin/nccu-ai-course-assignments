"""
Debug script to test data structures
"""
import os
from openai import OpenAI

# Mock API key for structure testing (won't actually call API)
os.environ['OPENAI_API_KEY'] = 'sk-test-mock-key'

# Test data structures
print("=" * 60)
print("Testing Gradio Chatbot data structures")
print("=" * 60)

# Simulated Gradio history format
print("\n1. Gradio Chatbot 期待的格式 (tuples):")
valid_history = [
    ["使用者問題1", "機器人回答1"],
    ["使用者問題2", "機器人回答2"],
]
print(f"Type: {type(valid_history)}")
print(f"Content: {valid_history}")
print(f"First message type: {type(valid_history[0])}")
print(f"First message length: {len(valid_history[0])}")

# What we were returning (WRONG)
print("\n2. 錯誤的回傳格式 (字串):")
wrong_return = "⚠️ 請先上傳 PDF 論文檔案！"
print(f"Type: {type(wrong_return)}")
print(f"Content: {wrong_return}")
print("❌ 這會造成 'Data incompatible with tuples format' 錯誤！")

# Correct error handling
print("\n3. 正確的錯誤處理回傳:")
correct_error_return = [["", "⚠️ 請先上傳 PDF 論文檔案！"]]
print(f"Type: {type(correct_error_return)}")
print(f"Content: {correct_error_return}")
print("✅ 這才是正確的格式！")

# Test appending to history
print("\n4. 測試 history 累加:")
history = []
print(f"初始 history: {history}")

# User says "hi"
new_msg = "hi"
bot_reply = "你好！請先上傳 PDF"
history = history + [[new_msg, bot_reply]]
print(f"第一輪後: {history}")

# User says "test"
new_msg = "test"
bot_reply = "收到測試訊息"
history = history + [[new_msg, bot_reply]]
print(f"第二輪後: {history}")

print("\n" + "=" * 60)
print("OpenAI Response API 回傳結構測試")
print("=" * 60)

# Simulate Response API structure
print("\n5. Response API 的 output 結構:")
print("根據文件，response.output 是一個 list，包含:")
print("- type: 'message' (助手回應)")
print("- type: 'reasoning' (推理過程)")
print("- type: 'function_call' (工具呼叫)")

mock_response_output = [
    {
        "id": "msg_123",
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "output_text",
                "text": "這是 AI 的回應"
            }
        ]
    }
]
print(f"\nMock output: {mock_response_output}")
print(f"Type: {type(mock_response_output)}")

print("\n6. 問題分析:")
print("如果我們做 conversation_history.extend(response.output)")
print("conversation_history 會變成：")
conversation_history = []
conversation_history.extend(mock_response_output)
print(f"conversation_history: {conversation_history}")
print(f"Type: {type(conversation_history)}")
print("\n這個格式是給 OpenAI API 的，不是給 Gradio 的！")
print("Gradio 需要的是: [[user, bot], [user, bot]]")
print("OpenAI 需要的是: [{role: ..., content: ...}, ...]")

print("\n7. 結論:")
print("我們需要維護 **兩個** 不同的歷史記錄：")
print("- conversation_history: OpenAI 格式 (用於 API 呼叫)")
print("- gradio_history: Gradio 格式 (用於 UI 顯示)")
print("\n目前的程式碼混淆了這兩者！")

print("\n" + "=" * 60)
print("修復方案")
print("=" * 60)

print("""
def chat_with_paper(message, history):
    # history 是 Gradio 格式: [[user, bot], [user, bot]]

    # 1. 檢查錯誤時，要回傳 Gradio 格式
    if pdf_content is None:
        # ❌ return "錯誤訊息"
        # ✅ return history + [["", "錯誤訊息"]]
        # 或者 return history (不加新訊息)
        return history + [[message, "⚠️ 請先上傳 PDF！"]]

    # 2. 建構 OpenAI 訊息
    openai_messages = [...]  # OpenAI 格式

    # 3. 呼叫 API
    response = client.responses.create(...)
    reply = response.output_text

    # 4. 更新 OpenAI 歷史
    conversation_history.extend(response.output)

    # 5. 更新 Gradio 歷史並回傳
    return history + [[message, reply]]  # ✅ 正確
""")

print("\n" + "=" * 60)
