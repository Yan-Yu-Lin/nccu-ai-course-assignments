# 政大 AI 課程作業

學生：北科大 電子四甲 林晏宇 111360128

## 為什麼建立這個 repo？

我平常寫程式都習慣在本地跑，主要是因為本地有我熟悉的 AI 工具像是 Claude Code 和 Codex CLI Agent，它們可以直接讀取檔案、執行指令，協助我寫程式和做實驗。

一開始做作業時發現課程都是用 Google Colab，雖然 Colab 網頁上有 Gemini，但我不太習慣用 Gemini。所以想把作業搬到本地來做，這樣我的 AI 工具可以更好地協助我，而且本地環境我也比較熟悉，可以直接跑程式測試。

## 遇到的問題

把 Jupyter notebook 載下來後遇到一個問題：notebook 是 JSON 格式，裡面有很多 metadata 和輸出結果，當 AI 讀取時會消耗大量的 token，而且不容易編輯。一個簡單的作業檔案可能就要幾十 KB，但實際的程式碼可能只有幾 KB。

## 解決方案：轉換工具

我請 Claude Code 幫我寫了三個轉換腳本：

1. **`convert.py`** - 雙向轉換器，自動判斷檔案格式
2. **`notebook_to_md.py`** - 把 .ipynb 轉成 Markdown（檔案大小減少 96%！）
3. **`md_to_notebook.py`** - 把 Markdown 轉回 .ipynb 和 .py

### 工作流程

1. 從 Colab 下載老師的範例 notebook
2. 用 `convert.py` 轉成 Markdown
3. 在本地用 neovim 編輯，AI 工具可以直接讀取和協助
4. 完成後轉回 notebook 上傳 Colab
5. 同時生成 .py 檔案可以在本地測試

這樣檔案小很多，AI 處理起來更有效率，我編輯也更方便。

## 作業內容

### HW1 - 畫函數圖形
學習用 matplotlib 畫各種數學函數的圖形。

### HW2 - 打造自己的 DNN（全連結）手寫辨識
實作 4 層神經網路做 MNIST 手寫數字辨識。我還找了不同的 AI 工具來幫忙寫不同版本，比較它們的方法和效果：
- 老師版本（我改的）：89.99% 準確率
- Claude Code 版本：87.75%（訓練過程出問題）
- Codex 版本：97.78%（最好的結果）

### HW3 - 認識 Softmax
實作 Softmax 函數，觀察「贏者通吃」的現象。用互動式介面讓使用者輸入不同數值，看看 Softmax 如何把數值轉換成機率分布。

## 心得

在做作業的過程中發現，有一個聰明且有完整系統權限的 AI 在旁邊協助真的很重要。它們可以幫我寫程式、解釋原理、找錯誤，還能做一些我自己辦不到的實驗。

比如 HW2 的時候，我自己改完老師的範例後就沒想法了，但 AI 工具可以提供完全不同的思路和技術，雖然不是每個都成功（Claude Code 的版本就訓練爆炸了），但這個過程讓我學到很多不同的方法。

這個 workflow 讓我可以在熟悉的環境下學習，同時保持跟 Colab 的相容性，對我來說是最好的學習方式。

## 技術細節

- Python 環境管理：使用 `uv`
- 本地 GPU：Apple M3 Pro with Metal acceleration
- 編輯器：Neovim
- AI 工具：Claude Code、Codex CLI Agent

## 檔案結構

```
colab_assignment/
├── script/              # 轉換工具
├── HW 1/               # 第一週作業
├── HW 2/               # 第二週作業（git submodule）
└── HW 3/               # 第三週作業（git submodule）
```

每個作業資料夾都有：
- `.md` - 可編輯的 Markdown 版本
- `.ipynb` - Colab notebook
- `.py` - 本地執行的 Python 腳本