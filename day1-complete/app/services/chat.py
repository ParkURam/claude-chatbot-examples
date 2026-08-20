# app/services/chat.py
from anthropic import Anthropic
from fastapi import HTTPException

MODEL = "claude-opus-5"
MAX_TOKENS = 16000


def ask_claude(client: Anthropic, question: str) -> str:
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": question}],
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Claude API 호출 실패: {str(e)}")

    for block in response.content:
        if block.type == "text":
            return block.text
    return ""
