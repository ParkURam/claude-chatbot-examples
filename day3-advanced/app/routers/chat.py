# app/routers/chat.py
import json
from typing import Annotated

from anthropic import Anthropic
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from ..core.config import get_claude_client
from ..core.db import SessionDep, engine
from ..models.conversation import Conversation
from ..models.message import Message
from ..schemas.chat import ChatResponse
from ..services.chat import (
    MODEL,
    ask_claude_with_history,
    first_text,
    stream_answer,
)

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


@router.post("/{conversation_id}/stream")
def create_chat_stream(
    conversation_id: int,
    req: QuestionIn,
    client: ClaudeDep,
):
    """답변을 타이핑되듯 흘려보낸다.

    세션을 Depends 로 받지 않고 제너레이터 안에서 직접 연다.
    Depends(get_session) 의 정리 코드는 응답 본문을 다 흘리기 전에
    돌 수 있어, 그 뒤에 저장하려 들면 닫힌 세션을 쓰게 된다.
    """
    with Session(engine) as session:
        if not session.get(Conversation, conversation_id):
            raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다")

        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at, Message.id)
        )
        history = [
            {"role": m.role, "content": m.content} for m in session.exec(stmt).all()
        ]
        history.append({"role": "user", "content": req.question})

        session.add(
            Message(
                conversation_id=conversation_id,
                role="user",
                content=req.question,
            )
        )
        session.commit()

    def event_stream():
        answer = ""
        usage = {"input_tokens": None, "output_tokens": None}

        for chunk in stream_answer(client, history):
            if chunk.startswith("data: "):
                answer += chunk[len("data: ") : -2].replace(chr(0x2028), "\n")
            elif chunk.startswith("event: done"):
                usage = json.loads(chunk.split("data: ", 1)[1].strip())
            yield chunk

        # 전부 받은 뒤에 저장한다 — 조각마다 저장하면 행이 수백 개 생긴다.
        with Session(engine) as session:
            session.add(
                Message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=answer,
                    input_tokens=usage["input_tokens"],
                    output_tokens=usage["output_tokens"],
                )
            )
            session.commit()

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
