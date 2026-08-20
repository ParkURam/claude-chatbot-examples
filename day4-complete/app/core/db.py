# app/core/db.py
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from .config import settings

# echo=True 이면 실행되는 SQL 이 터미널에 찍힌다 — 실습 6에서 쿼리 수를 셀 때 쓴다.
engine = create_engine(settings.database_url, echo=True)


def get_session():
    """요청마다 세션을 열고, 응답이 끝나면 자동으로 닫는다."""
    with Session(engine) as session:
        yield session


# 여러 엔드포인트에서 재사용하는 별칭
SessionDep = Annotated[Session, Depends(get_session)]


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
