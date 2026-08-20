# tests/test_advanced.py


def make_conversation_with_messages(client, n: int) -> int:
    conv_id = client.post("/conversations").json()["id"]
    for i in range(n):
        client.post(f"/chat/{conv_id}", json={"question": f"질문 {i}"})
    return conv_id


def test_list_conversations_counts_messages(client):
    conv_id = make_conversation_with_messages(client, 3)
    rows = client.get("/conversations").json()
    row = next(r for r in rows if r["id"] == conv_id)
    assert row["message_count"] == 6   # 질문 3 + 답변 3


def test_pagination_slices_and_reports_total(client):
    conv_id = make_conversation_with_messages(client, 5)   # 메시지 10건

    page = client.get(f"/conversations/{conv_id}/messages?skip=0&limit=4").json()
    assert page["total"] == 10
    assert len(page["messages"]) == 4
    assert page["skip"] == 0 and page["limit"] == 4

    tail = client.get(f"/conversations/{conv_id}/messages?skip=8&limit=4").json()
    assert len(tail["messages"]) == 2
    assert tail["total"] == 10


def test_pagination_rejects_bad_bounds(client):
    conv_id = make_conversation_with_messages(client, 1)
    assert client.get(f"/conversations/{conv_id}/messages?skip=-1").status_code == 422
    assert client.get(f"/conversations/{conv_id}/messages?limit=0").status_code == 422
