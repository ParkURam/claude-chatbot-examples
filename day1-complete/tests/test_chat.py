# tests/test_chat.py
from unittest.mock import Mock

from anthropic import Anthropic
from fastapi.testclient import TestClient

from app.core.config import get_claude_client
from app.main import app

client = TestClient(app)


def fake_claude_client(answer: str = "가짜 답변입니다") -> Mock:
    """네트워크 없이 쓸 가짜 Claude 클라이언트."""
    mock_block = Mock()
    mock_block.type = "text"
    mock_block.text = answer

    mock_response = Mock()
    mock_response.content = [mock_block]

    mock_client = Mock(spec=Anthropic)
    mock_client.messages.create.return_value = mock_response
    return mock_client


def test_chat():
    app.dependency_overrides[get_claude_client] = fake_claude_client
    try:
        response = client.post("/chat", json={"question": "테스트 질문"})
        assert response.status_code == 200
        assert response.json() == {
            "answer": "가짜 답변입니다",
            "model": "claude-opus-5",
        }
    finally:
        app.dependency_overrides.clear()


def test_chat_rejects_empty_question():
    response = client.post("/chat", json={"question": ""})
    assert response.status_code == 422


def test_chat_rejects_too_long_question():
    response = client.post("/chat", json={"question": "가" * 2001})
    assert response.status_code == 422
