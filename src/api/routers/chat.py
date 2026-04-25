# src/api/routers/chat.py
from fastapi import APIRouter, WebSocket, Depends, HTTPException
from pydantic import BaseModel
from typing import List
import json
from ..dependencies import get_agent, get_retriever

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    history: List[dict] = []

@router.post("/")
async def chat(req: ChatRequest, agent=Depends(get_agent)):
    answer = await agent.arun(req.query, req.history)
    return {"answer": answer}

@router.websocket("/ws")
async def chat_ws(websocket: WebSocket, agent=Depends(get_agent)):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        try:
            msg = json.loads(data)
            query = msg["query"]
            history = msg.get("history", [])
            answer = await agent.arun(query, history)
            await websocket.send_text(json.dumps({"response": answer}))
        except Exception as e:
            await websocket.send_text(json.dumps({"error": str(e)}))