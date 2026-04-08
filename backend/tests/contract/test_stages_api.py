from fastapi.testclient import TestClient


def test_list_stages_returns_four_fixed_stage_nodes(
    client: TestClient,
    created_session_id: str,
) -> None:
    response = client.get(f"/api/v1/sessions/{created_session_id}/stages")

    assert response.status_code == 200
    assert [item["stage"] for item in response.json()["data"]["items"]] == [
        "problem_definition",
        "research_analysis",
        "option_comparison",
        "decision_recommendation",
    ]


def test_start_stage_creates_stage_run(
    client: TestClient,
    created_session_id: str,
) -> None:
    response = client.post(
        f"/api/v1/sessions/{created_session_id}/stages/problem_definition/start",
        json={"triggeredBy": "user", "contextPatch": {}},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["sessionId"] == created_session_id
    assert payload["stage"] == "problem_definition"
    assert payload["status"] == "completed"


def test_get_stage_run_returns_completed_snapshot(
    client: TestClient,
    created_session_id: str,
) -> None:
    started = client.post(
        f"/api/v1/sessions/{created_session_id}/stages/problem_definition/start",
        json={"triggeredBy": "user", "contextPatch": {}},
    )
    stage_run_id = started.json()["data"]["id"]

    response = client.get(f"/api/v1/stage-runs/{stage_run_id}")

    assert response.status_code == 200
    assert response.json()["data"]["resultSnapshot"]["summary"] == "stub result"
