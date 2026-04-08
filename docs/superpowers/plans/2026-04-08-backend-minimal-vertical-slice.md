# Backend Minimal Vertical Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 `sessions + workspace + stages` 落一条最小可运行垂直切片，验证 P0 主链路接口形状与模块边界。

**Architecture:** 保持单体模块化目录，先只接 `FastAPI + Pydantic`，以进程内内存仓储替代数据库，先验证路由、响应结构、状态流转与模块职责。数据库、Alembic、真实 ORM 暂时后置，避免主线被基础设施拖偏。

**Tech Stack:** Python 3.12、FastAPI、Pydantic v2、pytest、httpx

---

### Task 1: 让应用最小可启动

**Files:**
- Modify: `E:\thinkWhat\backend\src\app\main.py`
- Modify: `E:\thinkWhat\backend\src\app\api.py`
- Modify: `E:\thinkWhat\backend\src\app\deps.py`
- Modify: `E:\thinkWhat\backend\src\core\config.py`
- Test: `E:\thinkWhat\backend\tests\contract\test_sessions_api.py`

- [ ] **Step 1: 写健康检查合同测试**

```python
def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "ok"
```

- [ ] **Step 2: 运行测试，确认先失败**

Run: `cd backend; pytest tests/contract/test_sessions_api.py -q`
Expected: `FAIL`，原因是应用或路由尚未实现

- [ ] **Step 3: 写最小应用入口与 `/api/v1` 路由汇总**

要求：

- `main.py` 创建 `FastAPI` 实例
- `api.py` 注册 `/api/v1`
- 提供 `/health`
- 统一响应骨架 `data / meta / error`

- [ ] **Step 4: 重新运行测试，确认通过**

Run: `cd backend; pytest tests/contract/test_sessions_api.py -q`
Expected: `PASS`

### Task 2: 落 sessions 最小读写切片

**Files:**
- Modify: `E:\thinkWhat\backend\src\modules\sessions\schemas.py`
- Modify: `E:\thinkWhat\backend\src\modules\sessions\repository.py`
- Modify: `E:\thinkWhat\backend\src\modules\sessions\service.py`
- Modify: `E:\thinkWhat\backend\src\modules\sessions\router.py`
- Modify: `E:\thinkWhat\backend\src\app\api.py`
- Test: `E:\thinkWhat\backend\tests\contract\test_sessions_api.py`

- [ ] **Step 1: 写 sessions 合同测试**

```python
def test_create_and_get_session(client):
    created = client.post(
        "/api/v1/sessions",
        json={"title": "test", "initialQuestion": "q", "tags": []},
    )
    assert created.status_code == 201
    session_id = created.json()["data"]["id"]

    fetched = client.get(f"/api/v1/sessions/{session_id}")
    assert fetched.status_code == 200
    assert fetched.json()["data"]["id"] == session_id
```

- [ ] **Step 2: 运行测试，确认先失败**

Run: `cd backend; pytest tests/contract/test_sessions_api.py -q`
Expected: `FAIL`，原因是 sessions 接口未实现

- [ ] **Step 3: 写最小 schema / repository / service / router**

要求：

- 仓储先用进程内字典或列表
- 支持 `GET /api/v1/sessions`
- 支持 `POST /api/v1/sessions`
- 支持 `GET /api/v1/sessions/{session_id}`
- 先不做 `PATCH`

- [ ] **Step 4: 重新运行 sessions 测试**

Run: `cd backend; pytest tests/contract/test_sessions_api.py -q`
Expected: `PASS`

### Task 3: 落 workspace + stages 最小状态流

**Files:**
- Modify: `E:\thinkWhat\backend\src\modules\stages\schemas.py`
- Modify: `E:\thinkWhat\backend\src\modules\stages\repository.py`
- Modify: `E:\thinkWhat\backend\src\modules\stages\service.py`
- Modify: `E:\thinkWhat\backend\src\modules\stages\router.py`
- Modify: `E:\thinkWhat\backend\src\modules\sessions\service.py`
- Modify: `E:\thinkWhat\backend\src\orchestration\stage_orchestrator.py`
- Modify: `E:\thinkWhat\backend\src\orchestration\role_router.py`
- Modify: `E:\thinkWhat\backend\src\app\api.py`
- Test: `E:\thinkWhat\backend\tests\contract\test_workspace_api.py`
- Test: `E:\thinkWhat\backend\tests\contract\test_stages_api.py`
- Test: `E:\thinkWhat\backend\tests\integration\test_session_stage_flow.py`

- [ ] **Step 1: 写 workspace 合同测试**

```python
def test_workspace_returns_session_and_stage_summary(client, created_session_id):
    response = client.get(f"/api/v1/sessions/{created_session_id}/workspace")
    assert response.status_code == 200
    assert "session" in response.json()["data"]
    assert "stages" in response.json()["data"]
```

- [ ] **Step 2: 写 stages 合同测试**

```python
def test_start_stage_creates_stage_run(client, created_session_id):
    response = client.post(
        f"/api/v1/sessions/{created_session_id}/stages/problem_definition/start",
        json={"triggeredBy": "user", "contextPatch": {}},
    )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "completed"
```

- [ ] **Step 3: 运行测试，确认先失败**

Run: `cd backend; pytest tests/contract/test_workspace_api.py tests/contract/test_stages_api.py tests/integration/test_session_stage_flow.py -q`
Expected: `FAIL`，原因是 workspace 和 stages 尚未实现

- [ ] **Step 4: 写最小状态模型与 orchestrator stub**

要求：

- 固定四个阶段枚举
- `workspace` 返回会话基础信息、阶段列表、当前阶段
- `start` 创建内存态 `stage_run`
- `stage_run` 先直接从 `running` 转 `completed`
- `result_snapshot` 先写固定结构化 stub
- 支持 `GET /api/v1/sessions/{session_id}/stages`
- 支持 `GET /api/v1/sessions/{session_id}/stages/{stage}`
- 支持 `POST /api/v1/sessions/{session_id}/stages/{stage}/start`
- 支持 `GET /api/v1/stage-runs/{stage_run_id}`

- [ ] **Step 5: 重新运行测试，确认通过**

Run: `cd backend; pytest tests/contract/test_workspace_api.py tests/contract/test_stages_api.py tests/integration/test_session_stage_flow.py -q`
Expected: `PASS`

### Task 4: 收口文档与最小验证

**Files:**
- Modify: `E:\thinkWhat\backend\README.md`
- Verify: `E:\thinkWhat\backend\`

- [ ] **Step 1: 更新 README**

要求：

- 写清当前切片范围
- 写清当前未接数据库
- 写清启动与测试命令

- [ ] **Step 2: 运行最小验证**

Run: `cd backend; pytest tests/contract tests/integration -q`
Expected: 所有当前切片测试通过

- [ ] **Step 3: 启动本地服务**

Run: `cd backend; uvicorn src.app.main:app --reload`
Expected: 服务启动成功，`GET /health` 返回 `200`

