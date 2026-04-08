import pytest
from fastapi.testclient import TestClient

from app.main import app
from modules.sessions.repository import session_repository
from modules.stages.repository import stage_repository


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_in_memory_state() -> None:
    session_repository.reset()
    stage_repository.reset()


@pytest.fixture
def created_session_id(client: TestClient) -> str:
    response = client.post(
        "/api/v1/sessions",
        json={
            "title": "最小切片会话",
            "initialQuestion": "先把主链路打通",
            "tags": ["backend"],
        },
    )
    return response.json()["data"]["id"]
