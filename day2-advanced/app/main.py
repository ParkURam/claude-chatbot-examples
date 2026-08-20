# app/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .core.db import create_db_and_tables
from .routers import chat, conversations, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()   # 시작 시 실행
    yield
    # 종료 시 정리할 것이 있으면 여기에 쓴다


app = FastAPI(title="AI 챗봇 서비스", lifespan=lifespan)
app.include_router(health.router)
app.include_router(conversations.router)
app.include_router(chat.router)
