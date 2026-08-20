"""selectinload 유무로 실제 SELECT 수가 몇 번인지 센다."""
import os, tempfile
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-dummy"
os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/n1.db"

from sqlalchemy import event
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.core.db import create_db_and_tables, engine
from app.models.conversation import Conversation
from app.models.message import Message

create_db_and_tables()
N = 20
with Session(engine) as s:
    for i in range(N):
        c = Conversation(title=f"대화 {i}")
        s.add(c); s.commit(); s.refresh(c)
        s.add(Message(conversation_id=c.id, role="user", content="q"))
        s.add(Message(conversation_id=c.id, role="assistant", content="a"))
    s.commit()

counter = {"n": 0}
@event.listens_for(engine, "before_cursor_execute")
def _count(conn, cursor, statement, *a):
    if statement.lstrip().upper().startswith("SELECT"):
        counter["n"] += 1

def run(use_selectinload: bool) -> int:
    counter["n"] = 0
    with Session(engine) as s:
        stmt = select(Conversation)
        if use_selectinload:
            stmt = stmt.options(selectinload(Conversation.messages))
        for conv in s.exec(stmt).all():
            len(conv.messages)
    return counter["n"]

print(f"대화 {N}개 · 메시지 {N*2}건")
print(f"selectinload 없이 : SELECT {run(False)}회   ← N+1")
print(f"selectinload 적용 : SELECT {run(True)}회")
