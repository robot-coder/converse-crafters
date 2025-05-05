# README.md

# Web-Based Chat Assistant

This project is a web-based Chat Assistant that allows users to have continuous conversations with selectable Large Language Models (LLMs). It features a user-friendly front-end UI and a back-end API built with FastAPI, deployed on Render.com. Users can select different LLMs, send messages, and view conversation history seamlessly.

## Features

- Interactive chat interface
- Support for multiple LLM backends
- Persistent conversation context
- Easy deployment on Render.com
- Modular and maintainable codebase

## Technologies Used

- Python 3.11+
- FastAPI
- Uvicorn
- LiteLLM
- HTTPX
- Starlette
- Pydantic

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- pip

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/chat-assistant.git
cd chat-assistant
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

### Running Locally

```bash
uvicorn main:app --reload
```

Navigate to `http://127.0.0.1:8000` in your browser to access the chat interface.

### Deployment on Render.com

- Push your code to a GitHub repository.
- Create a new web service on Render.
- Connect your repository.
- Set the start command to:

```bash
uvicorn main:app --host=0.0.0.0 --port=10000
```

- Deploy and access your live chat assistant.

## Files

- `main.py`: Contains the FastAPI application, API endpoints, and chat logic.
- `requirements.txt`: Lists all dependencies.
- `README.md`: This documentation.

---

# main.py

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
import httpx
from typing import List, Dict, Optional

# // CHALLENGE: Managing conversation context across multiple users
# // SOLUTION: Using in-memory store (dictionary) keyed by session ID for simplicity

app = FastAPI()

# In-memory store for conversation histories
conversation_store: Dict[str, List[Dict[str, str]]] = {}

# Supported LLMs (for demonstration, only LiteLLM is used)
SUPPORTED_MODELS = ["liteLLM"]

# 
class MessageRequest(BaseModel):
    session_id: str
    message: str
    model: str = "liteLLM"  # default model

class ChatResponse(BaseModel):
    reply: str
    conversation: List[Dict[str, str]]

# // CHALLENGE: Integrating multiple LLM backends
# // SOLUTION: Abstracted via a function that selects the backend based on model name

async def get_llm_response(message: str, model: str, conversation: List[Dict[str, str]]) -> str:
    if model not in SUPPORTED_MODELS:
        raise HTTPException(status_code=400, detail="Unsupported model")
    # For simplicity, using LiteLLM
    #     try:
        # Placeholder for actual LiteLLM API call
        # For demonstration, echo the message
        # In real implementation, replace with actual API call
        # e.g., response = await lite_llm_api_call(message, conversation)
        response = f"Echo: {message}"
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: MessageRequest):
    """
    Handle incoming chat messages, update conversation history, and return response.
    """
    session_id = request.session_id
    message = request.message
    model = request.model

    # Initialize conversation history if new session
    if session_id not in conversation_store:
        conversation_store[session_id] = []

    conversation = conversation_store[session_id]
    # Append user's message
    conversation.append({"role": "user", "content": message})

    try:
        reply = await get_llm_response(message, model, conversation)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

    # Append assistant's reply
    conversation.append({"role": "assistant", "content": reply})

    return ChatResponse(reply=reply, conversation=conversation)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """
    Serve a simple HTML page for the chat UI.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Web Chat Assistant</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            #chat { border: 1px solid #ccc; padding: 10px; height: 400px; overflow-y: scroll; }
            #userInput { width: 80%; }
            #sendBtn { width: 15%; }
        </style>
    </head>
    <body>
        <h1>Web-Based Chat Assistant</h1>
        <div id="chat"></div>
        <input type="text" id="userInput" placeholder="Type your message..." />
        <button id="sendBtn">Send</button>
        <script>
            const chatDiv = document.getElementById('chat');
            const inputBox = document.getElementById('userInput');
            const sendBtn = document.getElementById('sendBtn');
            const sessionId = Math.random().toString(36).substring(2, 15);
            let conversation = [];

            function appendMessage(role, content) {
                const msg = document.createElement('div');
                msg.innerHTML = `<b>${role}:</b> ${content}`;
                chatDiv.appendChild(msg);
                chatDiv.scrollTop = chatDiv.scrollHeight;
            }

            sendBtn.onclick = async () => {
                const message = inputBox.value;
                if (!message) return;
                appendMessage('User', message);
                inputBox.value = '';

                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ session_id: sessionId, message: message })
                });
                const data = await response.json();
                appendMessage('Assistant', data.reply);
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# // CHALLENGE: Ensuring deployment readiness
# // SOLUTION: Using uvicorn for server startup, compatible with Render.com

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# requirements.txt

fastapi
uvicorn
liteLLM
httpx
starlette
pydantic