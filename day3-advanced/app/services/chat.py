# app/services/chat.py
from anthropic import Anthropic
from fastapi import HTTPException

MODEL = "claude-opus-5"
MAX_TOKENS = 16000
# 스트리밍은 연결이 유지되므로 비스트리밍보다 크게 잡을 수 있다.
STREAM_MAX_TOKENS = 64000


def ask_claude_with_history(client: Anthropic, history: list[dict]):
    """대화 이력을 통째로 보내고 응답 객체를 그대로 돌려준다.

    사용량(usage)까지 저장해야 하므로 텍스트만 뽑지 않고 응답을 그대로 넘긴다.
    """
    try:
        return client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=history,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Claude API 호출 실패: {str(e)}")


def first_text(response) -> str:
    for block in response.content:
        if block.type == "text":
            return block.text
    return ""


def stream_answer(client: Anthropic, history: list[dict]):
    """SSE(Server-Sent Events) 로 답변 조각을 흘려보낸다.

    한 조각을 `data: <텍스트>\\n\\n` 으로 감싼다. 답변 안의 줄바꿈이
    SSE 의 줄 구분과 섞이면 프런트에서 조각이 잘리므로,
    줄바꿈은 \\u2028 로 치환해 보내고 프런트에서 되돌린다.
    끝나면 사용량을 담은 done 이벤트를 보낸다 — DB 저장은 그때 한다.
    """
    try:
        with client.messages.stream(
            model=MODEL,
            max_tokens=STREAM_MAX_TOKENS,
            messages=history,
        ) as stream:
            for text in stream.text_stream:
                yield f"data: {text.replace(chr(10), chr(0x2028))}\n\n"
            final = stream.get_final_message()
        usage = final.usage
        yield (
            "event: done\n"
            f'data: {{"input_tokens": {usage.input_tokens}, '
            f'"output_tokens": {usage.output_tokens}}}\n\n'
        )
    except Exception as e:
        yield f"event: error\ndata: 스트리밍 오류: {str(e)}\n\n"
