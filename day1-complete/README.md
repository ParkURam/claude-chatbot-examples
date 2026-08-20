# Day 1 완성본 — 실습 1~3

`practice/day1.md` 의 실습 1(프로젝트 뼈대) · 2(스키마) · 3(심화: `Depends`와 테스트)를
끝까지 따라간 상태입니다.

## 실행

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export ANTHROPIC_API_KEY="발급받은_키"
uvicorn app.main:app --reload
```

## 구조

```
app/
├── main.py            앱 조립만 한다 — 라우터를 붙이는 곳
├── core/config.py     설정(Settings)과 Claude 클라이언트 의존성
├── routers/
│   ├── health.py      GET  /health
│   └── chat.py        POST /chat
├── schemas/chat.py    요청·응답 모양(Pydantic)
└── services/chat.py   Claude 호출 — 라우터가 얇게 유지되도록 분리
tests/
├── test_health.py
└── test_chat.py       가짜 클라이언트로 네트워크 없이 검증
```

## 확인해 볼 것

| 무엇 | 어떻게 | 기대 |
|---|---|---|
| 헬스체크 | `curl localhost:8000/health` | `{"status":"ok"}` |
| 스키마 반영 | `/docs` 에서 `POST /chat` | `ChatRequest` · `ChatResponse` |
| 빈 문자열 거부 | `/docs` 에서 `{"question": ""}` | 422 + `detail` 배열 |
| 2000자 초과 거부 | 2001자 보내기 | 422 |
| 호출 실패 처리 | 키를 틀린 값으로 바꾸고 질문 | 502 + `detail` 메시지 |
| 테스트 | `ANTHROPIC_API_KEY=dummy python -m pytest tests` | 4 passed |

## 가이드와 다른 두 곳

1. **`ask_claude` 를 `services/chat.py` 에 두었습니다.** 가이드 실습 3은 이 함수를
   `routers/chat.py` 안에 정의하는데, 같은 절이 「라우터는 얇게 유지합니다」라고
   적고 있어 서로 어긋납니다. 실습 1에서 만든 `services/` 를 살리는 쪽을 골랐습니다.
2. **테스트가 `app.dependency_overrides` 를 씁니다.** 가이드 실습 3의 테스트는
   지역 변수에 `lambda` 를 다시 묶는데, 파이썬에서 그것은 다른 모듈이 보는 이름을
   바꾸지 못해 의존성 교체가 실제로 일어나지 않습니다. 그 테스트는
   `create_chat` 을 직접 부르므로 통과하지만, 나중에 누군가 `TestClient` 로 바꾸면
   조용히 진짜 API를 때립니다. FastAPI 공식 방식으로 바꿨습니다.
