# Day 3 완성본 — 실습 7~8

`practice/day3.md` 의 실습 7(React 채팅 화면) · 8(API 연동과 단일 애플리케이션 통합)입니다.
Day 2 위에 얹은 상태입니다. 실습 9(스트리밍)는 심화라 `../day3-advanced/` 에 따로 있습니다.

## 실행 — 서버 하나로

`web/dist/` 는 빌드 결과물이라 저장소에 담지 않습니다. **먼저 빌드해야 화면이 뜹니다.**

```bash
cd web && npm install && npm run build && cd ..

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export ANTHROPIC_API_KEY="발급받은_키"
uvicorn app.main:app --reload
```

http://localhost:8000 에 접속하면 채팅 화면이, `/docs` 에는 Swagger UI가 뜹니다.
**서버는 하나뿐입니다** — 이것이 실습 8의 결론입니다.

## 화면만 따로 고칠 때 (개발 중)

```bash
cd web
cp .env.example .env      # VITE_API_BASE=http://localhost:8000
npm run dev               # 5173 에서 Hot Reload
```

이때는 출처가 5173 과 8000 으로 갈라져 CORS 가 걸립니다. `app/main.py` 의
`CORSMiddleware` 가 5173 만 허용합니다. 빌드해서 FastAPI 가 서빙하면
같은 출처라 CORS 는 애초에 걸리지 않습니다.

## 순서가 왜 중요한가

```python
app.include_router(conversations.router, prefix="/api")   # 1) API 먼저
app.include_router(chat.router, prefix="/api")
app.mount("/", StaticFiles(directory=WEB_DIST, html=True))  # 2) 정적 파일 나중
```

`mount("/")` 는 **먼저 등록된 경로에 걸리지 않은 모든 요청**을 삼킵니다.
순서를 뒤집으면 `/api/chat/1` 조차 정적 파일 쪽으로 가서 404 가 됩니다.

## 구조

```
app/main.py             CORS · /api 접두사 · StaticFiles 마운트   ← 개조
web/
├── src/api.js          서버 주소를 여기서만 정한다
├── src/App.jsx         대화방 생성 · 메시지 상태 · 오류 상태
├── src/components/
│   ├── MessageList.jsx 말풍선 목록 + 로딩 표시
│   └── InputBox.jsx    입력창 + 전송(엔터도 됨)
└── .env.example        VITE_API_BASE
```

## 확인한 것

| 무엇 | 결과 |
|---|---|
| `GET /` | 200 · `index.html` |
| `/assets/index-*.js` | 200 |
| `POST /api/conversations` | 200 · `{"id":1,...}` |
| `GET /health` | 200 |
| CORS preflight (`Origin: localhost:5173`) | `access-control-allow-origin: http://localhost:5173` |
| CORS preflight (허용 안 된 출처) | allow-origin 헤더 없음 |
| `python -m pytest tests` | 6 passed |

## 가이드와 다른 곳

| 가이드 | 이 코드 | 왜 |
|---|---|---|
| 프런트가 `${API_BASE}/chat` 을 부름 (`day3.md:212`) | `/api/chat/{id}` | 같은 문서 `:296` 이 라우터를 `/api` 로 옮겨 놓고 프런트는 옛 경로를 부릅니다. 그대로면 실습 8 이후 화면이 API에 닿지 못합니다 |
| 본문이 `{conversation_id, question}` (`day3.md:215`) | 경로에 ID, 본문은 `{question}` | Day2가 세운 `POST /chat/{id}` 계약과 맞춥니다 |
| `directory="web/dist"` (`day3.md:299`) | `Path(__file__).parent.parent / "web" / "dist"` | 상대 경로는 **서버를 띄운 디렉터리** 기준이라, 다른 곳에서 띄우면 못 찾습니다 |
| `npm run build` 를 루트에서 (`day4.md:186` 빌드 명령) | `cd web && npm run build` | `package.json` 이 `web/` 에 있습니다 |
| 마운트를 무조건 실행 | `if WEB_DIST.is_dir()` | 빌드 전에는 `web/dist` 가 없어 서버가 기동조차 못 합니다. 테스트도 이 때문에 죽습니다 |
