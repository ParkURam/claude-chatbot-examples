# app/models/conversation.py
from datetime import datetime

from sqlmodel import Field, SQLModel


class Conversation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(default="새 대화")
    created_at: datetime = Field(default_factory=datetime.now)
