# app/main.py
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .core.db import create_db_and_tables
from .routers import chat, conversations, health

# 프로젝트 루트 기준으로 잡는다 — 서버를 어느 디렉터리에서 띄우든 같은 곳을 가리킨다.
WEB_DIST = Path(__file__).resolve().parent.parent / "web" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="AI 챗봇 서비스", lifespan=lifespan)

# Vite 개발 서버(5173)에서 부를 때만 필요하다.
# 빌드해서 아래 StaticFiles 로 서빙하면 같은 출처라 CORS 자체가 안 걸린다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1) API 를 먼저 등록한다.
app.include_router(health.router)
app.include_router(conversations.router, prefix="/api")
app.include_router(chat.router, prefix="/api")

# 2) 그 다음에 정적 파일을 마운트한다. 순서가 뒤집히면 "/" 마운트가
#    모든 경로를 먼저 삼켜 API 가 404 가 된다.
if WEB_DIST.is_dir():
    app.mount("/", StaticFiles(directory=WEB_DIST, html=True), name="web")


if __name__ == "__main__":
    # 로컬에서 `python -m app.main` 으로 띄울 때 쓴다.
    # 배포에서는 플랫폼이 시작 명령을 직접 준다:
    #   uvicorn app.main:app --host 0.0.0.0 --port $PORT
    import os

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
