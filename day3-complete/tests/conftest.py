# tests/conftest.py
"""테스트가 진짜 키도, 진짜 DB도 건드리지 않게 만든다.

engine 은 app.core.db 를 import 하는 순간 만들어지므로,
환경 변수는 그 전에 — 즉 이 파일에서 — 정해져야 한다.
"""
import os
import tempfile

_TMP_DB = os.path.join(tempfile.mkdtemp(prefix="chat-test-"), "test.db")
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-dummy-for-tests")
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP_DB}"

from unittest.mock import Mock  # noqa: E402

import pytest  # noqa: E402
from anthropic import Anthropic  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.config import get_claude_client  # noqa: E402
from app.core.db import create_db_and_tables  # noqa: E402
from app.main import app  # noqa: E402


def fake_claude_client(answer: str = "가짜 답변입니다") -> Mock:
    block = Mock()
    block.type = "text"
    block.text = answer

    response = Mock()
    response.content = [block]
    response.usage.input_tokens = 12
    response.usage.output_tokens = 34

    mock_client = Mock(spec=Anthropic)
    mock_client.messages.create.return_value = response
    return mock_client


@pytest.fixture
def client():
    create_db_and_tables()
    app.dependency_overrides[get_claude_client] = fake_claude_client
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
