# app/services/chat.py
from anthropic import Anthropic
from fastapi import HTTPException

MODEL = "claude-opus-5"
MAX_TOKENS = 16000


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
