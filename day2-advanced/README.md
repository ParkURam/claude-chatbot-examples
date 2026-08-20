# Day 2 심화 — 실습 6

`practice/day2.md` 의 실습 6(관계 설정과 조회 최적화)입니다.
**필수 경로가 아닙니다** — 못 해도 3일차 진도에 지장이 없습니다.
`../day2-complete/` 위에 얹은 상태입니다.

## 무엇이 늘었나

- 두 모델에 `Relationship` — `Conversation.messages` ↔ `Message.conversation`
- `GET /conversations` — `selectinload` 로 N+1 을 없앤 목록 조회
- `GET /conversations/{id}/messages` 에 `skip` · `limit` 페이지네이션

## N+1 을 직접 세어 보기

말로만 「쿼리가 줄어든다」고 하면 와닿지 않습니다. 직접 세어 보세요:

```bash
PYTHONPATH="$PWD" python n1_probe.py 2>/dev/null | tail -3
```

이 저장소에서 실제로 나온 값:

```
대화 20개 · 메시지 40건
selectinload 없이 : SELECT 21회   ← N+1
selectinload 적용 : SELECT 2회
```

대화가 20개면 21번(목록 1 + 대화마다 1), 50개면 51번입니다.
`selectinload` 를 붙이면 몇 개든 **2번**입니다 — 목록 1번,
그 대화들의 메시지를 `IN (...)` 으로 한 번에 가져오는 1번.

## 실행과 테스트

```bash
pip install -r requirements.txt
ANTHROPIC_API_KEY=dummy pytest tests     # 9 passed
```

## 가이드와 다른 곳

| 가이드 | 이 코드 | 왜 |
|---|---|---|
| `day2.md:584-613` 페이지네이션 블록 | 다시 씀 | **파싱조차 안 됩니다.** `SyntaxError: parameter without a default follows parameter with a default` — 기본값 있는 `skip`·`limit` 뒤에 기본값 없는 `session` 이 옵니다. 여기에 `select(func.count()).where(...).one()` 의 괄호 불균형과 `func` 미임포트가 겹쳐 있습니다 |
| `.add_columns(Message)` (`day2.md:602`) | 뺌 | 이미 `select(Message)` 인데 같은 것을 또 붙이면 결과가 튜플로 나옵니다 |
| `total` 을 `select(func.count()).where(...)` 로 셈 | `.select_from(Message)` 추가 | `where` 만으로는 어느 테이블을 세는지 정해지지 않습니다 |
| `skip: int = 0, limit: int = 50` | `Query(ge=0)` · `Query(ge=1, le=200)` | 음수 `skip` 이나 `limit=0` 이 그대로 통과합니다 |

한 가지는 가이드가 아니라 **제가 처음에 틀렸던 것**이라 적어 둡니다:
`Message.conversation` 을 `"Conversation | None"` 처럼 유니언째 따옴표로 묶으면
SQLAlchemy 가 그 문자열 전체를 클래스 이름으로 찾다가 `KeyError` 를 냅니다.
따옴표 안에는 클래스 이름만 들어가야 합니다 — `Optional["Conversation"]`.
