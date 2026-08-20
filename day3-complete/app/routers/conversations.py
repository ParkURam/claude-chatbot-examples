# app/routers/conversations.py
from fastapi import APIRouter
from sqlmodel import select

from ..core.db import SessionDep
from ..models.conversation import Conversation
from ..models.message import Message
from ..schemas.chat import MessageOut

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("", response_model=Conversation)
def create_conversation(session: SessionDep):
    conv = Conversation()
    session.add(conv)
    session.commit()
    session.refresh(conv)   # DB 가 채운 id 를 객체에 다시 읽어 온다
    return conv


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
def get_messages(conversation_id: int, session: SessionDep):
    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at, Message.id)
    )
    return session.exec(stmt).all()
