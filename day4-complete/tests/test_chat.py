# tests/test_chat.py


def new_conversation(client) -> int:
    response = client.post("/api/conversations")
    assert response.status_code == 200
    return response.json()["id"]


def test_create_conversation_returns_id(client):
    assert isinstance(new_conversation(client), int)


def test_chat_answers_and_records_usage(client):
    conv_id = new_conversation(client)

    response = client.post(f"/api/chat/{conv_id}", json={"question": "안녕하세요"})
    assert response.status_code == 200
    assert response.json() == {"answer": "가짜 답변입니다", "model": "claude-opus-5"}

    history = client.get(f"/api/conversations/{conv_id}/messages").json()
    assert [m["role"] for m in history] == ["user", "assistant"]
    assert history[0]["content"] == "안녕하세요"


def test_chat_sends_previous_messages_back_to_claude(client):
    """'내 이름 뭐라고 했지?' 가 통하는 메커니즘 — 이력을 통째로 다시 보낸다."""
    conv_id = new_conversation(client)
    client.post(f"/api/chat/{conv_id}", json={"question": "내 이름은 지훈이야"})
    client.post(f"/api/chat/{conv_id}", json={"question": "내 이름 뭐라고 했지?"})

    history = client.get(f"/api/conversations/{conv_id}/messages").json()
    assert len(history) == 4
    assert history[0]["content"] == "내 이름은 지훈이야"
    assert history[2]["content"] == "내 이름 뭐라고 했지?"


def test_chat_on_missing_conversation_is_404(client):
    response = client.post("/api/chat/99999", json={"question": "안녕"})
    assert response.status_code == 404


def test_chat_rejects_empty_question(client):
    conv_id = new_conversation(client)
    assert client.post(f"/api/chat/{conv_id}", json={"question": ""}).status_code == 422
