# Day 2 완성본 — 실습 4~5

`practice/day2.md` 의 실습 4(모델과 DB) · 5(기억하는 챗봇)를 끝까지 따라간 상태입니다.
**Day 1 위에 얹은 것**이지 처음부터 다시 쓴 것이 아닙니다.

실습 6(관계 설정과 `selectinload`)은 심화라 `../day2-advanced/` 에 따로 두었습니다.

## 실행

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export ANTHROPIC_API_KEY="발급받은_키"
uvicorn app.main:app --reload
```

터미널에 `CREATE TABLE conversation` · `CREATE TABLE message` 가 찍히고
프로젝트 루트에 `chat.db` 가 생기면 정상입니다.

## Day 1에서 무엇이 늘었나

```
app/
├── core/db.py          engine · get_session · SessionDep · create_db_and_tables  ← 새로
├── models/
│   ├── conversation.py 대화방 하나                                               ← 새로
│   └── message.py      그 안의 발화 한 건 (사용량 열 포함)                        ← 새로
├── routers/
│   ├── conversations.py POST /conversations · GET /conversations/{id}/messages   ← 새로
│   └── chat.py          POST /chat/{conversation_id} — 이력을 붙여 보낸다        ← 개조
└── main.py              lifespan 으로 시작 시 테이블 생성                          ← 개조
```

## "기억"의 정체

마법이 아닙니다. `/chat/{id}` 가 하는 일은 이렇습니다:

1. 그 대화의 이전 메시지를 `created_at` 순으로 전부 읽는다
2. 거기에 이번 질문을 덧붙여 **통째로** Claude에 보낸다
3. 질문을 먼저 저장하고 → 호출하고 → 답변과 사용량을 저장한다

3번의 순서가 중요합니다. 질문을 먼저 저장하므로 Claude 호출이 실패해도
"무엇을 물었다가 실패했는지"가 DB에 남습니다.

## 확인해 볼 것

```bash
# 대화 만들기
curl -X POST localhost:8000/conversations

# 첫 질문
curl -X POST localhost:8000/chat/1 \
  -H 'Content-Type: application/json' -d '{"question":"내 이름은 지훈이야"}'

# 기억하는지 확인
curl -X POST localhost:8000/chat/1 \
  -H 'Content-Type: application/json' -d '{"question":"내 이름 뭐라고 했지?"}'

# 이력 조회
curl localhost:8000/conversations/1/messages

# DB 직접 들여다보기
sqlite3 chat.db "SELECT role, content, input_tokens, output_tokens FROM message;"
```

테스트는 키 없이 됩니다: `python -m pytest tests`

## 가이드와 다른 곳

| 가이드 | 이 코드 | 왜 |
|---|---|---|
| `@router.post("/conversations")` 가 `prefix="/chat"` 라우터에 붙음 (`day2.md:272`) | `conversations.py` 라우터로 분리 | 그대로 두면 `/chat/conversations` 가 되어 문서의 curl(`day2.md:397`)·Day4 API 목록과 어긋나고, `/chat/{conversation_id:int}` 와 경로가 충돌합니다 |
| `question` 을 함수 인자로 받음 (`day2.md:300`) | JSON 본문 `{"question": ...}` | 그대로면 쿼리 파라미터가 됩니다. 실습 2에서 세운 `ChatRequest` 와도 어긋나고 Day3 프런트가 보내는 모양과도 다릅니다 |
| `from models.conversation import ...` | `from ..models.conversation import ...` | 최상위 `models/` 를 가리켜 `uvicorn app.main:app` 에서 `ModuleNotFoundError` 가 납니다 |
| `models/message.py` 에 `datetime` 임포트 없음 (`day2.md:47`) | `from datetime import datetime` 추가 | 그대로면 `NameError` |
| `core/config.py` 를 `SQLITE_URL` 로 갈아엎음 (`day2.md:82`) | `Settings` 에 `database_url` 추가 | Day1의 `Settings` 가 사라지고, 환경 변수 이름도 Day4(`DATABASE_URL`)와 어긋납니다 |
| `main.py` 가 health 라우터를 빠뜨림 (`day2.md:115`) | 유지 | 돌던 엔드포인트를 이유 없이 없앨 까닭이 없습니다 |
| `order_by(Message.created_at)` | `order_by(created_at, id)` | 한 커밋에 저장된 질문·답변은 시각이 같을 수 있어 순서가 뒤집힙니다 |
