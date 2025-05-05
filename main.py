from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx
from typing import Dict, Optional
import uvicorn

# Initialize FastAPI app
app = FastAPI()

# // CHALLENGE: Managing conversation context across multiple users and sessions
# // SOLUTION: Use in-memory storage (dictionary) keyed by session IDs for simplicity
# For production, consider persistent storage or database

# In-memory store for user sessions
sessions: Dict[str, Dict[str, str]] = {}

# Define supported LLMs
SUPPORTED_MODELS = ["liteLLM"]  # Extend as needed

class Message(BaseModel):
    session_id: str
    message: str
    model: Optional[str] = "liteLLM"

@app.post("/chat")
async def chat_endpoint(msg: Message):
    """
    Handle incoming chat messages, maintain conversation context, and return LLM response.
    """
    # Validate model
    if msg.model not in SUPPORTED_MODELS:
        raise HTTPException(status_code=400, detail="Unsupported model selected.")

    # Retrieve or create session context
    session = sessions.get(msg.session_id, {"history": ""})

    # Append user message to history
    session["history"] += f"User: {msg.message}\n"

    # Generate prompt for LLM
    prompt = session["history"] + "Assistant:"

    try:
        # Call the LLM API (liteLLM)
        # // CHALLENGE: Integrating with external LLM API
        # // SOLUTION: Use httpx to send POST request with prompt
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.liteLLM.com/generate",  # Placeholder URL
                json={
                    "prompt": prompt,
                    "model": msg.model,
                    "max_tokens": 150,
                    "temperature": 0.7
                },
                timeout=10.0
            )
        response.raise_for_status()
        data = response.json()
        reply = data.get("text", "").strip()
        if not reply:
            raise ValueError("Empty response from LLM.")
    except (httpx.HTTPError, ValueError) as e:
        # Handle errors gracefully
        raise HTTPException(status_code=500, detail=f"LLM API error: {str(e)}")

    # Append assistant reply to history
    session["history"] += f"Assistant: {reply}\n"

    # Save updated session
    sessions[msg.session_id] = session

    return JSONResponse(content={"reply": reply})

# Optional: Endpoint to reset session
@app.post("/reset")
async def reset_session(request: Request):
    """
    Reset conversation session.
    """
    data = await request.json()
    session_id = data.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required.")
    sessions.pop(session_id, None)
    return JSONResponse(content={"status": "session reset"})

# # // Note: For deployment on Render.com, run with command: uvicorn main:app --host 0.0.0.0 --port 8000