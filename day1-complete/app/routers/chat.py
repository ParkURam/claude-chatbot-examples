# app/routers/chat.py
from typing import Annotated

from anthropic import Anthropic
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ..core.config import get_claude_client
from ..schemas.chat import ChatResponse
from ..services.chat import MODEL, ask_claude

router = APIRouter(prefix="/chat", tags=["chat"])

ClaudeDep = Annotated[Anthropic, Depends(get_claude_client)]


class QuestionIn(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


@router.post("", response_model=ChatResponse)
def create_chat(req: QuestionIn, client: ClaudeDep):
    answer = ask_claude(client, req.question)
    return ChatResponse(answer=answer, model=MODEL)
