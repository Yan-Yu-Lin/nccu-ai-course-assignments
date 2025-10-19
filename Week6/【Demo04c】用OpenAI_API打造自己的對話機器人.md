# 【Demo04c】用OpenAI_API打造自己的對話機器人

*This notebook was created for Google Colab*

*Language: python*

---



```python
%matplotlib inline

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
```


### 1. 申請自己的 API 金鑰

我們使用 OpenAI 的 API, 主要原因是因為 OpenAI API 因為早開始, 成為某種標準。但不一定需要用 OpenAI 的服務。因此, 除了 OpenAI 之外, 這裡介紹幾個可能性。

#### (1) Mistral AI 金鑰 (可免費使用)

請至 https://console.mistral.ai/ 註冊，並選擇 plan (可以選免費的), 接著就可以申請 Mistral AI 的金鑰。請把這個鑰存在左方鑰匙的部份, 以 "Mistral" 的名稱存起來。



#### (2) OpenAI API 金鑰

OpenAI 現在沒有免費的 quota 可以使用, 所以要用 OpenAI 的模型, 請自行儲值。一般練習 5 美金就很足夠。

[`https://platform.openai.com`](https://platform.openai.com)

請把這個鑰存在左方鑰匙的部份, 以 "OpenAI" 的名稱存起來。

#### (3) 使用 Groq 金鑰 (可免費使用)

Groq 最大的特點是速度很快, 而且可以免費使用 (只是有流量限制), 企業可以付費使用, 能用許多開源型的 LLM。請至 https://console.groq.com/ 註冊並申請金鑰。

#### (4) 使用 Gemini 金鑰 (可免費使用)

Google Gemini 提供免費使用的 API, 最近更是改成可以和 OpenAI API 相容。請到 https://ai.google.dev/ 申請 API 金鑰。這和 Colab 一樣, 免費版的會有不太清楚的限制, 有時候不能跑。

#### (5) 使用 Together AI 金鑰 (有免費模型, 還有 1 美金啟動基金)

https://api.together.ai/ 有個 (有點兩光的) 免費模型 (如範例), 同時還有 1 美金啟動基金。可以選些便宜的模型, 當然也可以自己儲值試試比較「高級」的模型。

#### (6) 使用 Fireworks AI 金鑰 (有 1 美金啟動基金)

在 https://fireworks.ai/ 註冊之後, 提供 1 美金啟動基金。


**程式的基本設定，請自行修改**

* `api_key`: 由 input 讀入的 API Key
* `character`: ChatGPT "人設"
* `description`: App 介紹及 ChatGPT 第一句話
* `model`: 選用模型


#### 讀入你的金鑰

請依你使用的服務, 決定讀入哪個金鑰



```python
import os
from google.colab import userdata
```



```python
#【使用 Mistral】
# api_key = userdata.get('Mistral')
# base_url = "https://api.mistral.ai/v1"
# model = "ministral-8b-latest"

#【使用 OpenAI】
# api_key = userdata.get('OpenAI')
# model = "gpt-4o"

#【使用 Groq】
api_key = userdata.get('Groq')
model = "llama-3.2-3b-preview"
base_url="https://api.groq.com/openai/v1"

#【使用 Gemini】
# api_key = userdata.get('Gemini')
# model="gemini-1.5-flash"
# base_url="https://generativelanguage.googleapis.com/v1beta/openai/"

#【使用 Together】
# api_key = userdata.get('Together')
# model = "meta-llama/Llama-Vision-Free"
# base_url="https://api.together.xyz/v1"

#【使用 Fireworks】
# api_key = userdata.get('Fireworks')
# model = "accounts/fireworks/models/llama-v3p2-3b-instruct"
# base_url = "https://api.fireworks.ai/inference/v1"
```



```python
os.environ['OPENAI_API_KEY']=api_key
```


### 2. 程式的基本設定



```python
title = "員瑛式思考生成器"
```


給你的機器人一個名字。


請先為你的對話機器人做角色設定。



```python
character = '''請用員瑛式思考, 也就是什麼都正向思維任何使用者寫的事情, 以第一人稱、社群媒體 po 文的口吻說一次, 說為什麼這是一件超幸運的事, 並且以「完全是 Lucky Vicky 呀!」結尾。'''
```


再來是說明文字, 只是讓使用者知道這是做什麼的對話機器人。



```python
description = "嗨！我是你的「員瑛式思考生成器」，專門讓任何事情都能閃閃發亮✨～有什麼事最近讓你覺得有點不順，或是生活中的小小插曲？沒關係，不管大事小事，我都會幫你找到其中的好運氣！🌈無論是忘記帶鑰匙、沒趕上公車，或是工作上遇到困難，其實都可能是幸運的轉折點呢！  只要和我分享一下，我就會用「員瑛式思考」讓這些事變得正能量滿滿，並告訴你為什麼這一切都是「完全是 Lucky Vicky 呀！」"
```


### 2. 使用 OpenAI 的 API

我們先來安裝 `openai` 套件, 還有快速打造 Web App 的 `gradio`。



```python
!pip install openai
!pip install gradio
```

**Output:**
```
Requirement already satisfied: openai in /usr/local/lib/python3.10/dist-packages (1.54.4)
Requirement already satisfied: anyio<5,>=3.5.0 in /usr/local/lib/python3.10/dist-packages (from openai) (3.7.1)
Requirement already satisfied: distro<2,>=1.7.0 in /usr/local/lib/python3.10/dist-packages (from openai) (1.9.0)
Requirement already satisfied: httpx<1,>=0.23.0 in /usr/local/lib/python3.10/dist-packages (from openai) (0.27.2)
Requirement already satisfied: jiter<1,>=0.4.0 in /usr/local/lib/python3.10/dist-packages (from openai) (0.7.1)
Requirement already satisfied: pydantic<3,>=1.9.0 in /usr/local/lib/python3.10/dist-packages (from openai) (2.9.2)
Requirement already satisfied: sniffio in /usr/local/lib/python3.10/dist-packages (from openai) (1.3.1)
Requirement already satisfied: tqdm>4 in /usr/local/lib/python3.10/dist-packages (from openai) (4.66.6)
Requirement already satisfied: typing-extensions<5,>=4.11 in /usr/local/lib/python3.10/dist-packages (from openai) (4.12.2)
Requirement already satisfied: idna>=2.8 in /usr/local/lib/python3.10/dist-packages (from anyio<5,>=3.5.0->openai) (3.10)
Requirement already satisfied: exceptiongroup in /usr/local/lib/python3.10/dist-packages (from anyio<5,>=3.5.0->openai) (1.2.2)
Requirement already satisfied: certifi in /usr/local/lib/python3.10/dist-packages (from httpx<1,>=0.23.0->openai) (2024.8.30)
Requirement already satisfied: httpcore==1.* in /usr/local/lib/python3.10/dist-packages (from httpx<1,>=0.23.0->openai) (1.0.7)
Requirement already satisfied: h11<0.15,>=0.13 in /usr/local/lib/python3.10/dist-packages (from httpcore==1.*->httpx<1,>=0.23.0->openai) (0.14.0)
Requirement already satisfied: annotated-types>=0.6.0 in /usr/local/lib/python3.10/dist-packages (from pydantic<3,>=1.9.0->openai) (0.7.0)
Requirement already satisfied: pydantic-core==2.23.4 in /usr/local/lib/python3.10/dist-packages (from pydantic<3,>=1.9.0->openai) (2.23.4)
Collecting gradio
  Downloading gradio-5.7.1-py3-none-any.whl.metadata (16 kB)
Collecting aiofiles<24.0,>=22.0 (from gradio)
  Downloading aiofiles-23.2.1-py3-none-any.whl.metadata (9.7 kB)
Requirement already satisfied: anyio<5.0,>=3.0 in /usr/local/lib/python3.10/dist-packages (from gradio) (3.7.1)
Collecting fastapi<1.0,>=0.115.2 (from gradio)
  Downloading fastapi-0.115.5-py3-none-any.whl.metadata (27 kB)
Collecting ffmpy (from gradio)
  Downloading ffmpy-0.4.0-py3-none-any.whl.metadata (2.9 kB)
Collecting gradio-client==1.5.0 (from gradio)
  Downloading gradio_client-1.5.0-py3-none-any.whl.metadata (7.1 kB)
Requirement already satisfied: httpx>=0.24.1 in /usr/local/lib/python3.10/dist-packages (from gradio) (0.27.2)
Requirement already satisfied: huggingface-hub>=0.25.1 in /usr/local/lib/python3.10/dist-packages (from gradio) (0.26.2)
Requirement already satisfied: jinja2<4.0 in /usr/local/lib/python3.10/dist-packages (from gradio) (3.1.4)
Collecting markupsafe~=2.0 (from gradio)
  Downloading MarkupSafe-2.1.5-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (3.0 kB)
Requirement already satisfied: numpy<3.0,>=1.0 in /usr/local/lib/python3.10/dist-packages (from gradio) (1.26.4)
Requirement already satisfied: orjson~=3.0 in /usr/local/lib/python3.10/dist-packages (from gradio) (3.10.11)
Requirement already satisfied: packaging in /usr/local/lib/python3.10/dist-packages (from gradio) (24.2)
Requirement already satisfied: pandas<3.0,>=1.0 in /usr/local/lib/python3.10/dist-packages (from gradio) (2.2.2)
Requirement already satisfied: pillow<12.0,>=8.0 in /usr/local/lib/python3.10/dist-packages (from gradio) (11.0.0)
Requirement already satisfied: pydantic>=2.0 in /usr/local/lib/python3.10/dist-packages (from gradio) (2.9.2)
Collecting pydub (from gradio)
  Downloading pydub-0.25.1-py2.py3-none-any.whl.metadata (1.4 kB)
Collecting python-multipart==0.0.12 (from gradio)
  Downloading python_multipart-0.0.12-py3-none-any.whl.metadata (1.9 kB)
Requirement already satisfied: pyyaml<7.0,>=5.0 in /usr/local/lib/python3.10/dist-packages (from gradio) (6.0.2)
Collecting ruff>=0.2.2 (from gradio)
  Downloading ruff-0.8.1-py3-none-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (25 kB)
Collecting safehttpx<1.0,>=0.1.1 (from gradio)
  Downloading safehttpx-0.1.1-py3-none-any.whl.metadata (4.1 kB)
Collecting semantic-version~=2.0 (from gradio)
  Downloading semantic_version-2.10.0-py2.py3-none-any.whl.metadata (9.7 kB)
Collecting starlette<1.0,>=0.40.0 (from gradio)
  Downloading starlette-0.41.3-py3-none-any.whl.metadata (6.0 kB)
Collecting tomlkit==0.12.0 (from gradio)
  Downloading tomlkit-0.12.0-py3-none-any.whl.metadata (2.7 kB)
Requirement already satisfied: typer<1.0,>=0.12 in /usr/local/lib/python3.10/dist-packages (from gradio) (0.13.0)
Requirement already satisfied: typing-extensions~=4.0 in /usr/local/lib/python3.10/dist-packages (from gradio) (4.12.2)
Collecting uvicorn>=0.14.0 (from gradio)
  Downloading uvicorn-0.32.1-py3-none-any.whl.metadata (6.6 kB)
Requirement already satisfied: fsspec in /usr/local/lib/python3.10/dist-packages (from gradio-client==1.5.0->gradio) (2024.10.0)
Collecting websockets<13.0,>=10.0 (from gradio-client==1.5.0->gradio)
  Downloading websockets-12.0-cp310-cp310-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (6.6 kB)
Requirement already satisfied: idna>=2.8 in /usr/local/lib/python3.10/dist-packages (from anyio<5.0,>=3.0->gradio) (3.10)
Requirement already satisfied: sniffio>=1.1 in /usr/local/lib/python3.10/dist-packages (from anyio<5.0,>=3.0->gradio) (1.3.1)
Requirement already satisfied: exceptiongroup in /usr/local/lib/python3.10/dist-packages (from anyio<5.0,>=3.0->gradio) (1.2.2)
Requirement already satisfied: certifi in /usr/local/lib/python3.10/dist-packages (from httpx>=0.24.1->gradio) (2024.8.30)
Requirement already satisfied: httpcore==1.* in /usr/local/lib/python3.10/dist-packages (from httpx>=0.24.1->gradio) (1.0.7)
Requirement already satisfied: h11<0.15,>=0.13 in /usr/local/lib/python3.10/dist-packages (from httpcore==1.*->httpx>=0.24.1->gradio) (0.14.0)
Requirement already satisfied: filelock in /usr/local/lib/python3.10/dist-packages (from huggingface-hub>=0.25.1->gradio) (3.16.1)
Requirement already satisfied: requests in /usr/local/lib/python3.10/dist-packages (from huggingface-hub>=0.25.1->gradio) (2.32.3)
Requirement already satisfied: tqdm>=4.42.1 in /usr/local/lib/python3.10/dist-packages (from huggingface-hub>=0.25.1->gradio) (4.66.6)
Requirement already satisfied: python-dateutil>=2.8.2 in /usr/local/lib/python3.10/dist-packages (from pandas<3.0,>=1.0->gradio) (2.8.2)
Requirement already satisfied: pytz>=2020.1 in /usr/local/lib/python3.10/dist-packages (from pandas<3.0,>=1.0->gradio) (2024.2)
Requirement already satisfied: tzdata>=2022.7 in /usr/local/lib/python3.10/dist-packages (from pandas<3.0,>=1.0->gradio) (2024.2)
Requirement already satisfied: annotated-types>=0.6.0 in /usr/local/lib/python3.10/dist-packages (from pydantic>=2.0->gradio) (0.7.0)
Requirement already satisfied: pydantic-core==2.23.4 in /usr/local/lib/python3.10/dist-packages (from pydantic>=2.0->gradio) (2.23.4)
Requirement already satisfied: click>=8.0.0 in /usr/local/lib/python3.10/dist-packages (from typer<1.0,>=0.12->gradio) (8.1.7)
Requirement already satisfied: shellingham>=1.3.0 in /usr/local/lib/python3.10/dist-packages (from typer<1.0,>=0.12->gradio) (1.5.4)
Requirement already satisfied: rich>=10.11.0 in /usr/local/lib/python3.10/dist-packages (from typer<1.0,>=0.12->gradio) (13.9.4)
Requirement already satisfied: six>=1.5 in /usr/local/lib/python3.10/dist-packages (from python-dateutil>=2.8.2->pandas<3.0,>=1.0->gradio) (1.16.0)
Requirement already satisfied: markdown-it-py>=2.2.0 in /usr/local/lib/python3.10/dist-packages (from rich>=10.11.0->typer<1.0,>=0.12->gradio) (3.0.0)
Requirement already satisfied: pygments<3.0.0,>=2.13.0 in /usr/local/lib/python3.10/dist-packages (from rich>=10.11.0->typer<1.0,>=0.12->gradio) (2.18.0)
Requirement already satisfied: charset-normalizer<4,>=2 in /usr/local/lib/python3.10/dist-packages (from requests->huggingface-hub>=0.25.1->gradio) (3.4.0)
Requirement already satisfied: urllib3<3,>=1.21.1 in /usr/local/lib/python3.10/dist-packages (from requests->huggingface-hub>=0.25.1->gradio) (2.2.3)
Requirement already satisfied: mdurl~=0.1 in /usr/local/lib/python3.10/dist-packages (from markdown-it-py>=2.2.0->rich>=10.11.0->typer<1.0,>=0.12->gradio) (0.1.2)
Downloading gradio-5.7.1-py3-none-any.whl (57.1 MB)
[2K   [90m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[0m [32m57.1/57.1 MB[0m [31m12.1 MB/s[0m eta [36m0:00:00[0m
[?25hDownloading gradio_client-1.5.0-py3-none-any.whl (320 kB)
[2K   [90m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[0m [32m320.1/320.1 kB[0m [31m18.3 MB/s[0m eta [36m0:00:00[0m
[?25hDownloading python_multipart-0.0.12-py3-none-any.whl (23 kB)
Downloading tomlkit-0.12.0-py3-none-any.whl (37 kB)
Downloading aiofiles-23.2.1-py3-none-any.whl (15 kB)
Downloading fastapi-0.115.5-py3-none-any.whl (94 kB)
[2K   [90m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[0m [32m94.9/94.9 kB[0m [31m6.5 MB/s[0m eta [36m0:00:00[0m
[?25hDownloading MarkupSafe-2.1.5-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (25 kB)
Downloading ruff-0.8.1-py3-none-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (11.2 MB)
[2K   [90m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[0m [32m11.2/11.2 MB[0m [31m78.5 MB/s[0m eta [36m0:00:00[0m
[?25hDownloading safehttpx-0.1.1-py3-none-any.whl (8.4 kB)
Downloading semantic_version-2.10.0-py2.py3-none-any.whl (15 kB)
Downloading starlette-0.41.3-py3-none-any.whl (73 kB)
[2K   [90m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[0m [32m73.2/73.2 kB[0m [31m4.4 MB/s[0m eta [36m0:00:00[0m
[?25hDownloading uvicorn-0.32.1-py3-none-any.whl (63 kB)
[2K   [90m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[0m [32m63.8/63.8 kB[0m [31m4.1 MB/s[0m eta [36m0:00:00[0m
[?25hDownloading ffmpy-0.4.0-py3-none-any.whl (5.8 kB)
Downloading pydub-0.25.1-py2.py3-none-any.whl (32 kB)
Downloading websockets-12.0-cp310-cp310-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl (130 kB)
[2K   [90m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[0m [32m130.2/130.2 kB[0m [31m9.5 MB/s[0m eta [36m0:00:00[0m
[?25hInstalling collected packages: pydub, websockets, uvicorn, tomlkit, semantic-version, ruff, python-multipart, markupsafe, ffmpy, aiofiles, starlette, safehttpx, gradio-client, fastapi, gradio
  Attempting uninstall: markupsafe
    Found existing installation: MarkupSafe 3.0.2
    Uninstalling MarkupSafe-3.0.2:
      Successfully uninstalled MarkupSafe-3.0.2
Successfully installed aiofiles-23.2.1 fastapi-0.115.5 ffmpy-0.4.0 gradio-5.7.1 gradio-client-1.5.0 markupsafe-2.1.5 pydub-0.25.1 python-multipart-0.0.12 ruff-0.8.1 safehttpx-0.1.1 semantic-version-2.10.0 starlette-0.41.3 tomlkit-0.12.0 uvicorn-0.32.1 websockets-12.0

```


### 3. 使用 ChatGPT API

首先使用 `openai` 套件。



```python
from openai import OpenAI
```


把自己的金鑰貼上。



```python
client = OpenAI(
    base_url = base_url # 如用 OpenAI 不需要這一行
)
```


ChatGPT API 的重點是要把之前對話的內容送給 ChatGPT, 然後他就會有個適當的回應!

角色 (`role`) 一共有三種, 分別是:

* `system`: 這是對話機器人的「人設」
* `user`: 使用者
* `assistant`: ChatGPT 的回應


基本上過去的對話紀錄長這個樣子。

    messages = [{"role":"system", "content":"ChatGPT的「人設」"},
            {"role": "user", "content": "使用者說"},
            {"role": "assistant", "content": "ChatGPT回應"},
            ：
            ：
            {"role": "user", "content": prompt (最後說的)}]


### 4. 用 Gradio 打造你的對話機器人 Web App!



```python
import gradio as gr
```



```python
messages = [{"role":"system",
             "content":character},
            {"role":"assistant",
            'content':description}]
```



```python
def mychatbot(prompt, history):
    history = history or []
    global messages

    messages.append({"role": "user", "content": prompt})
    chat_completion = client.chat.completions.create(
        messages=messages,
        model=model,
        )
    reply = chat_completion.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    history = history + [[prompt, reply]]

    return history, history
```



```python
chatbot = gr.Chatbot()
```

**Output:**
```
/usr/local/lib/python3.10/dist-packages/gradio/components/chatbot.py:237: UserWarning: You have not specified a value for the `type` parameter. Defaulting to the 'tuples' format for chatbot messages, but this is deprecated and will be removed in a future version of Gradio. Please set type='messages' instead, which uses openai-style dictionaries with 'role' and 'content' keys.
  warnings.warn(

```



```python
iface = gr.Interface(mychatbot,
                     inputs=["text", "state"],
                     outputs=[chatbot, "state"],
                     title=title,
                     description=description)
```



```python
iface.launch(share=True, debug=True)
```

**Output:**
```
Colab notebook detected. This cell will run indefinitely so that you can see errors and logs. To turn off, set debug=False in launch().
* Running on public URL: https://81e3e413e7e50b6ffc.gradio.live

This share link expires in 72 hours. For free permanent hosting and GPU upgrades, run `gradio deploy` from the terminal in the working directory to deploy to Hugging Face Spaces (https://huggingface.co/spaces)

<IPython.core.display.HTML object>
Keyboard interruption in main thread... closing server.
Killing tunnel 127.0.0.1:7860 <> https://81e3e413e7e50b6ffc.gradio.live


```
