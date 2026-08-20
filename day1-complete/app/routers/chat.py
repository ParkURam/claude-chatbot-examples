# app/routers/chat.py
from typing import Annotated

from anthropic import Anthropic
from fastapi import APIRouter, Depends

from ..core.config import get_claude_client
from ..schemas.chat import ChatRequest, ChatResponse
from ..services.chat import MODEL, ask_claude

router = APIRouter(prefix="/chat", tags=["chat"])

ClaudeDep = Annotated[Anthropic, Depends(get_claude_client)]


@router.post("", response_model=ChatResponse)
def create_chat(req: ChatRequest, client: ClaudeDep):
    answer = ask_claude(client, req.question)
    return ChatResponse(answer=answer, model=MODEL)
