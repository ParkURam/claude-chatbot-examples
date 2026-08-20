# tests/test_stream.py
from unittest.mock import Mock

from anthropic import Anthropic
from fastapi.testclient import TestClient

from app.core.config import get_claude_client
from app.main import app

LINE_SEP = chr(0x2028)


def fake_streaming_client(pieces):
    """messages.stream(...) 이 컨텍스트 매니저인 점까지 흉내 낸다."""
    stream = Mock()
    stream.text_stream = iter(pieces)

    final = Mock()
    final.usage.input_tokens = 7
    final.usage.output_tokens = 11
    stream.get_final_message.return_value = final

    ctx = Mock()
    ctx.__enter__ = Mock(return_value=stream)
    ctx.__exit__ = Mock(return_value=False)

    mock_client = Mock(spec=Anthropic)
    mock_client.messages.stream.return_value = ctx
    return mock_client


def test_stream_sends_pieces_then_saves(client):
    pieces = ["안녕", "하세요", "\n반갑습니다"]
    app.dependency_overrides[get_claude_client] = lambda: fake_streaming_client(pieces)

    conv_id = client.post("/api/conversations").json()["id"]
    with client.stream(
        "POST", f"/api/chat/{conv_id}/stream", json={"question": "인사해 줘"}
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        body = "".join(response.iter_text())

    # 조각이 각각 별개의 SSE 이벤트로 나갔다
    data_events = [e for e in body.split("\n\n") if e.startswith("data: ")]
    assert len(data_events) == 3

    # 답변 속 줄바꿈은 SSE 경계와 섞이지 않도록 치환되어 나간다
    assert LINE_SEP in body
    assert "event: done" in body

    # 다 받은 뒤 한 번만 저장된다 — 조각 수만큼 행이 생기면 안 된다
    history = client.get(f"/api/conversations/{conv_id}/messages").json()
    assert [m["role"] for m in history] == ["user", "assistant"]
    assert history[1]["content"] == "안녕하세요\n반갑습니다"


def test_stream_on_missing_conversation_is_404(client):
    app.dependency_overrides[get_claude_client] = lambda: fake_streaming_client(["x"])
    response = client.post("/api/chat/99999/stream", json={"question": "안녕"})
    assert response.status_code == 404
