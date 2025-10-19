Developer quickstart
Take your first steps with the OpenAI API.
The OpenAI API provides a simple interface to state-of-the-art AI models for text generation, natural language processing, computer vision, and more. Get started by creating an API Key and running your first API call. Discover how to generate text, analyze images, build agents, and more.

Create and export an API key
Before you begin, create an API key in the dashboard, which you'll use to securely access the API. Store the key in a safe location, like a 
.zshrc
file or another text file on your computer. Once you've generated an API key, export it as an environment variable in your terminal.

macOS / Linux
Windows
Export an environment variable on macOS or Linux systems
export OPENAI_API_KEY="your_api_key_here"
OpenAI SDKs are configured to automatically read your API key from the system environment.

Install the OpenAI SDK and Run an API Call
JavaScript
Python
.NET
Java
Go
To use the OpenAI API in Python, you can use the official OpenAI SDK for Python. Get started by installing the SDK using pip:

Install the OpenAI SDK with pip
pip install openai
With the OpenAI SDK installed, create a file called example.py and copy the example code into it:

Test a basic API request
from openai import OpenAI
client = OpenAI()

response = client.responses.create(
    model="gpt-5",
    input="Write a one-sentence bedtime story about a unicorn."
)

print(response.output_text)
Execute the code with python example.py. In a few moments, you should see the output of your API request.

Learn more on GitHub
Discover more SDK capabilities and options on the library's GitHub README.

Responses starter app
Start building with the Responses API.
Text generation and prompting
Learn more about prompting, message roles, and building conversational apps.
Analyze images and files
Send image URLs, uploaded files, or PDF documents directly to the model to extract text, classify content, or detect visual elements.

Image URL
File URL
Upload file
Analyze the content of an image
from openai import OpenAI
client = OpenAI()

response = client.responses.create(
    model="gpt-5",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "What teams are playing in this image?",
                },
                {
                    "type": "input_image",
                    "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/3b/LeBron_James_Layup_%28Cleveland_vs_Brooklyn_2018%29.jpg"
                }
            ]
        }
    ]
)

print(response.output_text)
Image inputs guide
Learn to use image inputs to the model and extract meaning from images.

File inputs guide
Learn to use file inputs to the model and extract meaning from documents.

Extend the model with tools
Give the model access to external data and functions by attaching tools. Use built-in tools like web search or file search, or define your own for calling APIs, running code, or integrating with third-party systems.

Web search
File search
Function calling
Remote MCP
Use web search in a response
from openai import OpenAI
client = OpenAI()

response = client.responses.create(
    model="gpt-5",
    tools=[{"type": "web_search"}],
    input="What was a positive news story from today?"
)

print(response.output_text)
Use built-in tools
Learn about powerful built-in tools like web search and file search.

Function calling guide
Learn to enable the model to call your own custom code.

Stream responses and build realtime apps
Use server‑sent streaming events to show results as they’re generated, or the Realtime API for interactive voice and multimodal apps.

Stream server-sent events from the API
from openai import OpenAI
client = OpenAI()

stream = client.responses.create(
    model="gpt-5",
    input=[
        {
            "role": "user",
            "content": "Say 'double bubble bath' ten times fast.",
        },
    ],
    stream=True,
)

for event in stream:
    print(event)
Use streaming events
Use server-sent events to stream model responses to users fast.

Get started with the Realtime API
Use WebRTC or WebSockets for super fast speech-to-speech AI apps.

Build agents
Use the OpenAI platform to build agents capable of taking action—like controlling computers—on behalf of your users. Use the Agents SDK for Python or TypeScript to create orchestration logic on the backend.

Build a language triage agent
from agents import Agent, Runner
import asyncio

spanish_agent = Agent(
    name="Spanish agent",
    instructions="You only speak Spanish.",
)

english_agent = Agent(
    name="English agent",
    instructions="You only speak English",
)

triage_agent = Agent(
    name="Triage agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[spanish_agent, english_agent],
)


async def main():
    result = await Runner.run(triage_agent, input="Hola, ¿cómo estás?")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
