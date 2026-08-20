# app/models/message.py
from datetime import datetime

from sqlmodel import Field, SQLModel


class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    role: str  # "user" 또는 "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    input_tokens: int | None = None
    output_tokens: int | None = None
