from fastapi.testclient import TestClient


def test_session_workspace_stage_flow(client: TestClient) -> None:
    created = client.post(
        "/api/v1/sessions",
        json={
            "title": "主链路验证",
            "initialQuestion": "最小切片能不能跑通？",
            "tags": [],
        },
    )
    session_id = created.json()["data"]["id"]

    workspace_before = client.get(f"/api/v1/sessions/{session_id}/workspace")
    assert workspace_before.status_code == 200
    assert workspace_before.json()["data"]["currentStage"] == "problem_definition"

    started = client.post(
        f"/api/v1/sessions/{session_id}/stages/problem_definition/start",
        json={"triggeredBy": "user", "contextPatch": {"goal": "需求梳理"}},
    )
    assert started.status_code == 200
    stage_run_id = started.json()["data"]["id"]

    stage_detail = client.get(f"/api/v1/sessions/{session_id}/stages/problem_definition")
    assert stage_detail.status_code == 200
    assert stage_detail.json()["data"]["latestRun"]["id"] == stage_run_id

    stage_run = client.get(f"/api/v1/stage-runs/{stage_run_id}")
    assert stage_run.status_code == 200
    assert stage_run.json()["data"]["status"] == "completed"
