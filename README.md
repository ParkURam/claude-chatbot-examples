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
| `day4-complete/` | 실습 10~12 | 배포 준비 완료 — `.env` 분리·`requirements.txt`·포트 바인딩 |

각 디렉터리는 **그날까지의 완성 상태 전체**입니다. 하루치 차이만 담긴 것이 아니라
그 자체로 돌아가는 프로젝트라, 어느 날 것이든 바로 열어 실행할 수 있습니다.

## 받아서 실행하기

```bash
git clone <저장소_URL>
cd ai-service-dev-examples/day1-complete     # 원하는 날짜로

python -m venv .venv
source .venv/bin/activate                    # Windows는 .venv\Scripts\activate
pip install -r requirements.txt

export ANTHROPIC_API_KEY="발급받은_키"        # Windows CMD는 set, PowerShell은 $env:
uvicorn app.main:app --reload
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
