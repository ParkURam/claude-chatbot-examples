# app/main.py
from fastapi import FastAPI

from .routers import chat, health

app = FastAPI(title="AI 챗봇 서비스")
app.include_router(health.router)
app.include_router(chat.router)
