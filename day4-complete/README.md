# Day 4 완성본 — 실습 10~11

`practice/day4.md` 의 실습 10(키 분리와 저장소 올리기) · 11(배포)입니다.
Day 3 위에 얹었습니다. 실습 12의 심화 선택지(JWT · Docker · PostgreSQL)는
**구현하지 않았습니다** — 아래 「왜 심화를 넣지 않았나」 참조.

## Day 3에서 무엇이 달라졌나

| | Day 3까지 | Day 4 |
|---|---|---|
| API 키 | 셸 환경 변수 (`export`) | `.env` 파일 |
| 의존성 | `requirements.txt` 없음 | 버전 고정된 `requirements.txt` |
| 빌드 | 손으로 `cd web && npm run build` | `build.sh` 한 줄 |
| 포트 | 8000 고정 | `PORT` 환경 변수 |

## 로컬에서 돌리기

```bash
cp .env.example .env        # 그리고 ANTHROPIC_API_KEY 값을 채웁니다
./build.sh                  # pip install + npm ci + npm run build
uvicorn app.main:app --reload
```

`.env` 만 있으면 `export` 없이도 뜹니다. `python -m app.main` 으로 띄우면
`PORT` 환경 변수를 읽습니다.

## Render 에 올릴 때

| 칸 | 값 |
|---|---|
| Build Command | `./build.sh` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Environment | `ANTHROPIC_API_KEY` = 발급받은 키 |

`--host 0.0.0.0` 이 빠지면 컨테이너 안에서만 듣게 되어, 로그는 정상인데
바깥에서 접속이 안 됩니다.

> **SQLite 주의** — 무료 플랜은 영구 디스크가 없어 재배포마다 `chat.db` 가
> 사라집니다. 대화를 남기려면 `DATABASE_URL` 을 PostgreSQL 로 바꾸세요
> (`day4.md` 실습 12 §7). SQLModel 은 연결 문자열만 바꾸면 됩니다.

## 키가 새지 않는지 확인한 것

```
$ git check-ignore -v .env
.gitignore:1:.env	.env
```

| 대상 | 상태 |
|---|---|
| `.env` | ignored |
| `chat.db` | ignored |
| `web/node_modules` | ignored |
| `web/dist` | ignored |
| `.env.example` | **커밋됨** (값은 비어 있음) |

## 왜 심화를 넣지 않았나

실습 12의 세 심화(JWT · Docker · PostgreSQL)는 이 저장소에 코드로 넣지
않았습니다. **셋 다 검증할 수 없기 때문입니다** — JWT 는 실제 사용자 저장소가
있어야 의미가 있고, Docker 는 이 환경에서 빌드를 돌려 확인하지 않았으며,
PostgreSQL 이전은 Render 계정 없이는 「재배포 후에도 데이터가 남는다」를
확인할 방법이 없습니다.

돌려 보지 않은 코드를 정답지에 넣으면 수강생이 그것을 정답으로 믿습니다.
`day4.md` 의 절차와 공식 문서 링크를 따라가는 편이 낫습니다.

JWT 만 한 가지 덧붙이면, `day4.md:337` 이 짚은 대로 **`pyjwt` + `pwdlib`**
입니다. 인터넷 예제 다수가 쓰는 `python-jose` + `passlib` 를 따라가면
설치부터 어긋납니다.

## 가이드와 다른 곳

| 가이드 | 이 코드 | 왜 |
|---|---|---|
| `--host 0.0.0.00` (`day4.md:95`) | `--host 0.0.0.0` | 점이 하나 더 있습니다 |
| Build Command 가 루트에서 `npm run build` (`day4.md:186`) | `build.sh` 안에서 `cd web` | `package.json` 이 `web/` 에 있어 루트에서는 실패합니다 |
| `anthropic==0.122.0` (`day4.md:86`) | `anthropic==0.125.0` | 오늘 설치하면 0.125.0 이 나옵니다. 고정 버전은 실제로 설치되는 값이어야 합니다 |
| `git add .` 로 커밋 (`day4.md:117`) | 경로를 지정해 커밋 | `git add .` 은 의도하지 않은 파일까지 쓸어 담습니다 |
| `requirements.txt` 에 테스트 도구 없음 | `pytest` · `httpx` 를 주석과 함께 포함 | 없으면 받아 간 사람이 테스트를 못 돌립니다 |
