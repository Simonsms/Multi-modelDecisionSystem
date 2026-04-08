from fastapi.testclient import TestClient


def test_workspace_returns_session_and_stage_summary(
    client: TestClient,
    created_session_id: str,
) -> None:
    response = client.get(f"/api/v1/sessions/{created_session_id}/workspace")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["session"]["id"] == created_session_id
    assert payload["currentStage"] == "problem_definition"
    assert len(payload["stages"]) == 4
