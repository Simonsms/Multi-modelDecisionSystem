from fastapi.testclient import TestClient


def test_health_returns_200(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "ok"


def test_create_and_get_session(client: TestClient) -> None:
    created = client.post(
        "/api/v1/sessions",
        json={
            "title": "内部需求梳理工作台",
            "initialQuestion": "第一版应该如何收敛？",
            "tags": ["MVP"],
        },
    )

    assert created.status_code == 201
    created_payload = created.json()["data"]
    session_id = created_payload["id"]
    assert created_payload["title"] == "内部需求梳理工作台"
    assert created_payload["currentStage"] == "problem_definition"

    fetched = client.get(f"/api/v1/sessions/{session_id}")

    assert fetched.status_code == 200
    assert fetched.json()["data"]["id"] == session_id


def test_list_sessions_returns_created_session(client: TestClient) -> None:
    client.post(
        "/api/v1/sessions",
        json={
            "title": "会话 A",
            "initialQuestion": "A?",
            "tags": [],
        },
    )

    response = client.get("/api/v1/sessions")

    assert response.status_code == 200
    assert len(response.json()["data"]["items"]) >= 1
