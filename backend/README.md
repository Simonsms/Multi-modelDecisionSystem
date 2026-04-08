# thinkWhat backend

This directory now contains a minimal runnable vertical slice for the backend.

Current scope:

- FastAPI app bootstrap
- `/health`
- in-memory `sessions` endpoints
- in-memory `workspace + stages` minimal flow
- contract and integration tests for the P0 main chain slice

Current non-goals:

- no PostgreSQL integration yet
- no Alembic migration execution yet
- no real model invocation yet
- no activities, research, candidates, recommendations, or analytics modules yet

Current commands:

```bash
python -m pip install -e .[test]
pytest tests/contract tests/integration -q
uvicorn app.main:app --reload
```

Current verification target:

1. `GET /health`
2. `POST /api/v1/sessions`
3. `GET /api/v1/sessions/{session_id}`
4. `GET /api/v1/sessions/{session_id}/workspace`
5. `GET /api/v1/sessions/{session_id}/stages`
6. `POST /api/v1/sessions/{session_id}/stages/{stage}/start`
7. `GET /api/v1/stage-runs/{stage_run_id}`
