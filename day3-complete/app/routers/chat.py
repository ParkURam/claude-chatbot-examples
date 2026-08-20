# app/routers/chat.py
from typing import Annotated

from anthropic import Anthropic
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import select

from ..core.config import get_claude_client
from ..core.db import SessionDep
from ..models.conversation import Conversation
from ..models.message import Message
from ..schemas.chat import ChatResponse
from ..services.chat import MODEL, ask_claude_with_history, first_text

router = APIRouter(prefix="/chat", tags=["chat"])

ClaudeDep = Annotated[Anthropic, Depends(get_claude_client)]


class QuestionIn(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


@router.post("/{conversation_id}", response_model=ChatResponse)
def create_chat(
    conversation_id: int,
    req: QuestionIn,
    session: SessionDep,
    client: ClaudeDep,
):
    conv = session.get(Conversation, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다")

    # 이전 메시지를 읽어 Claude 입력에 붙인다 — 이것이 "기억"의 정체다.
    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at, Message.id)
    )
    history = [
        {"role": m.role, "content": m.content} for m in session.exec(stmt).all()
    ]
    history.append({"role": "user", "content": req.question})

    # 질문을 먼저 저장한다 — 호출이 실패해도 "무엇을 물었다가 실패했는지"가 남는다.
    session.add(
        Message(
            conversation_id=conversation_id,
            role="user",
            content=req.question,
        )
    )
    session.commit()

    response = ask_claude_with_history(client, history)
    answer = first_text(response)

    session.add(
        Message(
            conversation_id=conversation_id,
            role="assistant",
            content=answer,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )
    )
    session.commit()

    return ChatResponse(answer=answer, model=MODEL)
