# app/schemas/chat.py
from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    answer: str
    model: str


class MessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime


class ConversationOut(BaseModel):
    id: int
    title: str
    created_at: datetime
    message_count: int


class MessagePage(BaseModel):
    messages: list[MessageOut]
    total: int
    skip: int
    limit: int
