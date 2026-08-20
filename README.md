# AI 서비스 개발 실무 4일 — 실습 완성본

강의 실습 가이드(`practice/day1~4.md`)를 **끝까지 따라간 결과물**입니다.
막혔을 때 내 코드와 비교해 보거나, 결석한 날의 출발점으로 쓰세요.

> 이 저장소는 **정답지이지 지름길이 아닙니다.** 먼저 직접 만들어 보고,
> 막힌 자리에서만 열어 보는 편이 훨씬 많이 남습니다.

## 무엇이 들어 있나

| 디렉터리 | 어디까지 | 무엇이 되나 |
|---|---|---|
| `day1-complete/` | 실습 1~3 | 질문을 보내면 Claude가 답하는 API. 계층 분리·스키마 검증·테스트 |
| `day2-complete/` | 실습 4~6 | 대화를 기억하는 챗봇. SQLite에 대화·발화를 저장 |
| `day3-complete/` | 실습 7~9 | React 채팅 화면. 서버 하나로 화면과 API가 함께 |
| `day4-complete/` | 실습 10~11 | 배포 준비 완료 — `.env` 분리·`requirements.txt`·포트 바인딩 |

심화 실습은 필수 경로를 흐리지 않도록 따로 두었습니다. 못 해도 다음 날 진도에 지장이 없습니다.

| 디렉터리 | 무엇 |
|---|---|
| `day2-advanced/` | 실습 6 — `Relationship` · `selectinload` 로 N+1 없애기 · 페이지네이션 |
| `day3-advanced/` | 실습 9 — 응답 스트리밍과 중단 버튼 |

실습 12의 심화(JWT · Docker · PostgreSQL)는 코드로 넣지 않았습니다 — 이유는
`day4-complete/README.md` 에 적혀 있습니다.

각 디렉터리는 **그날까지의 완성 상태 전체**입니다. 하루치 차이만 담긴 것이 아니라
그 자체로 돌아가는 프로젝트라, 어느 날 것이든 바로 열어 실행할 수 있습니다.

## 받아서 실행하기

```bash
git clone https://github.com/ParkURam/claude-chatbot-examples.git
cd claude-chatbot-examples/day1-complete     # 원하는 날짜로

python -m venv .venv
source .venv/bin/activate                    # Windows는 .venv\Scripts\activate
pip install -r requirements.txt

export ANTHROPIC_API_KEY="발급받은_키"        # Windows CMD는 set, PowerShell은 $env:
uvicorn app.main:app --reload
```

**Day 3 이후는 화면을 먼저 빌드해야 합니다** — `web/dist/` 는 빌드 결과물이라
저장소에 담지 않았습니다:

```bash
cd web && npm install && npm run build && cd ..
```

http://localhost:8000/docs 를 열면 Swagger UI가 뜹니다.

`day4-complete/` 만은 `.env` 파일을 씁니다 — `cp ../.env.example .env` 후 값을 채우세요.

## API 키가 없어도 되는 것

키 없이도 다음은 확인할 수 있습니다. **테스트에는 진짜 키가 필요 없습니다** —
가짜 클라이언트로 Claude 호출을 대신하기 때문입니다.

```bash
ANTHROPIC_API_KEY=dummy pytest tests
```

키가 있어야만 되는 것은 **실제 답변을 받는 일**뿐입니다.

## 가이드와 다른 곳

실습 가이드와 이 코드가 어긋나면 **가이드가 정본입니다.** 만들면서 가이드 쪽 오류를
찾은 자리는 가이드를 고쳤고, 그 내역은 강의 저장소의 커밋 이력에 남아 있습니다.

## 수강한 기수의 상태로 받기

내용은 기수마다 손질됩니다. 들었던 그 시점 그대로 받으려면 태그를 쓰세요:

```bash
git checkout sesac2-260921     # SESAC 2기 · 2026-09-21
```

`git tag` 로 전체 목록을 볼 수 있습니다.
