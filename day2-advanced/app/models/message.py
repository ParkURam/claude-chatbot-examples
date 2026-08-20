# app/models/message.py
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .conversation import Conversation


class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    role: str
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    input_tokens: int | None = None
    output_tokens: int | None = None

    # 문자열 안에는 클래스 이름만 들어가야 한다.
    # "Conversation | None" 처럼 유니언째 따옴표로 묶으면
    # SQLAlchemy 가 그 전체를 클래스 이름으로 찾다가 KeyError 를 낸다.
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
