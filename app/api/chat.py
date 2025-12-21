from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ollama import chat_with_db

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    reply = chat_with_db(request.prompt)
    return {"reply": reply}
