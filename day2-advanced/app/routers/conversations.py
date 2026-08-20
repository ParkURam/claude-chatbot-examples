# app/routers/conversations.py
from fastapi import APIRouter, Query
from sqlalchemy.orm import selectinload
from sqlmodel import func, select

from ..core.db import SessionDep
from ..models.conversation import Conversation
from ..models.message import Message
from ..schemas.chat import ConversationOut, MessageOut, MessagePage

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("", response_model=Conversation)
def create_conversation(session: SessionDep):
    conv = Conversation()
    session.add(conv)
    session.commit()
    session.refresh(conv)
    return conv


@router.get("", response_model=list[ConversationOut])
def list_conversations(session: SessionDep):
    """N+1 을 selectinload 로 없앤 목록 조회.

    `.options(selectinload(...))` 를 빼면 대화 50개에 쿼리 51번이 나간다.
    붙이면 2번이다 — 서버 로그의 SELECT 줄을 직접 세어 보라.
    """
    stmt = select(Conversation).options(selectinload(Conversation.messages))
    conversations = session.exec(stmt).all()

    return [
        ConversationOut(
            id=conv.id,
            title=conv.title,
            created_at=conv.created_at,
            message_count=len(conv.messages),   # 이미 로딩되어 있어 쿼리가 안 나간다
        )
        for conv in conversations
    ]


@router.get("/{conversation_id}/messages", response_model=MessagePage)
def get_messages(
    conversation_id: int,
    session: SessionDep,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
):
    total = session.exec(
        select(func.count())
        .select_from(Message)
        .where(Message.conversation_id == conversation_id)
    ).one()

    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at, Message.id)
        .offset(skip)
        .limit(limit)
    )
    messages = session.exec(stmt).all()

    return MessagePage(
        messages=[MessageOut.model_validate(m, from_attributes=True) for m in messages],
        total=total,
        skip=skip,
        limit=limit,
    )
