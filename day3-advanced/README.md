# Day 3 심화 — 실습 9 (응답 스트리밍)

`practice/day3.md` 의 실습 9입니다. **필수 경로가 아닙니다.**
`../day3-complete/` 위에 얹었고, 기존 `POST /api/chat/{id}` 는 그대로 둔 채
`POST /api/chat/{id}/stream` 을 **추가**했습니다 — 비교해 볼 수 있게.

## 실행

```bash
cd web && npm install && npm run build && cd ..
pip install -r requirements.txt
ANTHROPIC_API_KEY=발급받은_키 uvicorn app.main:app --reload
```

http://localhost:8000 에서 답변이 한 글자씩 타이핑되듯 나옵니다.
생성 중에는 **중단** 버튼이 뜹니다.

테스트는 키 없이 됩니다: `ANTHROPIC_API_KEY=dummy python -m pytest tests` → 8 passed

## 알아 둘 함정 셋

### 1. SSE 경계와 답변 속 줄바꿈이 충돌한다

SSE는 `data: <내용>\n\n` 으로 조각을 끊습니다. 그런데 Claude 답변에도 줄바꿈이
있어서 그대로 흘려보내면 조각이 한가운데서 잘립니다. 서버가 답변의 `\n` 을
`U+2028` 로 바꿔 보내고 프런트가 되돌립니다. `day3.md` 는 이 함정을 다루지 않습니다.

### 2. 조각은 이벤트 경계에서 잘려 도착한다

`reader.read()` 가 주는 덩어리는 SSE 이벤트와 경계가 맞지 않습니다.
가이드처럼 덩어리마다 `split('\n')` 하면 반쪽 이벤트를 파싱하게 됩니다.
버퍼에 모아 두고 `\n\n` 이 나온 데까지만 잘라 씁니다.

### 3. 스트리밍 중에는 세션을 의존성으로 받으면 안 된다

`Depends(get_session)` 의 정리 코드(`yield` 뒤)는 응답 본문을 다 흘려보내기 전에
돌 수 있습니다. 그 뒤에 저장하려 들면 닫힌 세션을 씁니다.
제너레이터 안에서 `with Session(engine)` 으로 직접 엽니다.

`day3.md:512` 의 「스트리밍 중엔 DB 저장 불가 → 전체를 다 받은 뒤 저장」이
가리키는 것이 이 문제입니다. 이 코드는 조각을 흘리며 누적했다가
`event: done` 의 사용량까지 받은 뒤 **한 번만** 저장합니다.

## 확인한 것

| 무엇 | 결과 |
|---|---|
| 조각 3개 → SSE `data:` 이벤트 3개 | ✅ |
| `content-type: text/event-stream` | ✅ |
| 답변 속 줄바꿈이 왕복해도 보존됨 | `"안녕하세요\n반갑습니다"` |
| 저장은 끝난 뒤 한 번 (조각 수만큼 행이 생기지 않음) | `["user","assistant"]` |
| 없는 대화로 스트리밍 요청 | 404 |

## 가이드와 다른 곳

| 가이드 | 이 코드 | 왜 |
|---|---|---|
| `@router.post("/chat")` 로 기존 엔드포인트를 덮음 (`day3.md:373`) | `/stream` 을 따로 추가 | 심화를 안 한 사람과 코드가 갈라지지 않습니다 |
| 조각을 그대로 `data: {text}` (`day3.md:371`) | 줄바꿈을 `U+2028` 로 치환 | 답변 속 줄바꿈이 SSE 경계와 섞입니다 |
| `chunk.split('\n')` 로 바로 파싱 (`day3.md:420`) | 버퍼링 후 `\n\n` 단위로 | 덩어리 경계가 이벤트 경계와 다릅니다 |
| 사용량·저장 언급 없음 | `event: done` 으로 usage 를 받아 저장 | 스트리밍에서도 `input_tokens`·`output_tokens` 를 남깁니다 |
| `AbortController` 를 `useState` 로 (`day3.md:454`) | `useRef` | state 갱신은 비동기라 같은 렌더 안에서 최신 controller 를 못 봅니다 |
