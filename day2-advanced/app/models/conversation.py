# app/models/conversation.py
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .message import Message


class Conversation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(default="새 대화")
    created_at: datetime = Field(default_factory=datetime.now)

    messages: list["Message"] = Relationship(back_populates="conversation")
