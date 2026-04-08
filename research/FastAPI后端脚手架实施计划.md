# FastAPI 后端脚手架实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭建一套可承接第一版决策工作台 P0 接口的 `FastAPI + PostgreSQL` 后端脚手架，并优先打通 `sessions + workspace + stages` 主链路。

**Architecture:** 采用单体模块化后端，按业务模块拆分 `router / service / repository / schemas / models`，用 `SQLAlchemy 2.x + Alembic` 承接 PostgreSQL 数据层，用 `FastAPI` 提供 REST 接口。阶段编排和多模型调用先保留清晰边界，先把控制后端骨架立住，再逐步接 research、recommendation 和 analytics。

**Tech Stack:** Python 3.12、FastAPI、Uvicorn、SQLAlchemy 2.x、Alembic、PostgreSQL、Pydantic v2、pytest、httpx

---

## 文件结构

本计划按以下目标文件结构推进：

- Create: `E:\thinkWhat\backend\pyproject.toml`
- Create: `E:\thinkWhat\backend\.env.example`
- Create: `E:\thinkWhat\backend\README.md`
- Create: `E:\thinkWhat\backend\alembic.ini`
- Create: `E:\thinkWhat\backend\migrations\env.py`
- Create: `E:\thinkWhat\backend\migrations\versions\`
- Create: `E:\thinkWhat\backend\src\app\main.py`
- Create: `E:\thinkWhat\backend\src\app\api.py`
- Create: `E:\thinkWhat\backend\src\app\deps.py`
- Create: `E:\thinkWhat\backend\src\core\config.py`
- Create: `E:\thinkWhat\backend\src\core\database.py`
- Create: `E:\thinkWhat\backend\src\core\errors.py`
- Create: `E:\thinkWhat\backend\src\core\enums.py`
- Create: `E:\thinkWhat\backend\src\modules\sessions\router.py`
- Create: `E:\thinkWhat\backend\src\modules\sessions\service.py`
- Create: `E:\thinkWhat\backend\src\modules\sessions\repository.py`
- Create: `E:\thinkWhat\backend\src\modules\sessions\schemas.py`
- Create: `E:\thinkWhat\backend\src\modules\sessions\models.py`
- Create: `E:\thinkWhat\backend\src\modules\stages\router.py`
- Create: `E:\thinkWhat\backend\src\modules\stages\service.py`
- Create: `E:\thinkWhat\backend\src\modules\stages\repository.py`
- Create: `E:\thinkWhat\backend\src\modules\stages\schemas.py`
- Create: `E:\thinkWhat\backend\src\modules\stages\models.py`
- Create: `E:\thinkWhat\backend\src\modules\activities\router.py`
- Create: `E:\thinkWhat\backend\src\modules\activities\service.py`
- Create: `E:\thinkWhat\backend\src\modules\activities\repository.py`
- Create: `E:\thinkWhat\backend\src\modules\activities\schemas.py`
- Create: `E:\thinkWhat\backend\src\modules\activities\models.py`
- Create: `E:\thinkWhat\backend\src\orchestration\stage_orchestrator.py`
- Create: `E:\thinkWhat\backend\src\orchestration\role_router.py`
- Create: `E:\thinkWhat\backend\src\adapters\models\base.py`
- Create: `E:\thinkWhat\backend\tests\contract\test_sessions_api.py`
- Create: `E:\thinkWhat\backend\tests\contract\test_workspace_api.py`
- Create: `E:\thinkWhat\backend\tests\contract\test_stages_api.py`
- Create: `E:\thinkWhat\backend\tests\integration\test_session_stage_flow.py`

---

### Task 1: 初始化工程与基础配置

**Files:**
- Create: `E:\thinkWhat\backend\pyproject.toml`
- Create: `E:\thinkWhat\backend\.env.example`
- Create: `E:\thinkWhat\backend\README.md`
- Create: `E:\thinkWhat\backend\src\core\config.py`
- Create: `E:\thinkWhat\backend\src\core\errors.py`
- Create: `E:\thinkWhat\backend\src\core\enums.py`

- [ ] **Step 1: 写基础配置与依赖清单**

要求：

- 在 `pyproject.toml` 写入 FastAPI、SQLAlchemy、Alembic、Pydantic、pytest 等依赖
- 在 `.env.example` 写入 `DATABASE_URL`、模型 key 和基础 app 配置
- 在 `config.py` 中定义统一 `Settings`

- [ ] **Step 2: 运行依赖安装验证**

Run:

```bash
cd backend
python -m pip install -e .
```

Expected:

- 安装成功
- 没有核心依赖冲突

- [ ] **Step 3: 补最小文档**

要求：

- 在 `README.md` 写清本地启动、迁移、测试命令

- [ ] **Step 4: Commit**

```bash
git add backend/pyproject.toml backend/.env.example backend/README.md backend/src/core
git commit -m "chore: initialize backend project config"
```

### Task 2: 搭建 FastAPI 应用骨架

**Files:**
- Create: `E:\thinkWhat\backend\src\app\main.py`
- Create: `E:\thinkWhat\backend\src\app\api.py`
- Create: `E:\thinkWhat\backend\src\app\deps.py`
- Modify: `E:\thinkWhat\backend\README.md`
- Test: `E:\thinkWhat\backend\tests\contract\test_sessions_api.py`

- [ ] **Step 1: 写应用入口与路由汇总**

要求：

- `main.py` 创建 FastAPI app
- `api.py` 统一注册 `/api/v1`
- 预留健康检查接口，如 `/health`

- [ ] **Step 2: 写最小合同测试**

测试内容：

- `GET /health` 返回 200
- API 应用可正常启动

- [ ] **Step 3: 运行最小测试**

Run:

```bash
cd backend
pytest tests/contract/test_sessions_api.py -q
```

Expected:

- 至少健康检查通过

- [ ] **Step 4: Commit**

```bash
git add backend/src/app backend/tests/contract/test_sessions_api.py backend/README.md
git commit -m "feat: add fastapi app bootstrap"
```

### Task 3: 接入数据库与迁移框架

**Files:**
- Create: `E:\thinkWhat\backend\alembic.ini`
- Create: `E:\thinkWhat\backend\migrations\env.py`
- Create: `E:\thinkWhat\backend\src\core\database.py`
- Modify: `E:\thinkWhat\backend\src\core\config.py`
- Test: `E:\thinkWhat\backend\tests\integration\test_session_stage_flow.py`

- [ ] **Step 1: 建立 SQLAlchemy engine 和 session**

要求：

- 在 `database.py` 定义 `engine`、`SessionLocal` 和 `get_db`
- 使用 PostgreSQL URL

- [ ] **Step 2: 初始化 Alembic**

要求：

- 配好 `alembic.ini`
- 配好 `migrations/env.py`
- 保证 Alembic 能读取项目模型 metadata

- [ ] **Step 3: 运行迁移框架验证**

Run:

```bash
cd backend
alembic current
```

Expected:

- Alembic 可正常连接并执行

- [ ] **Step 4: Commit**

```bash
git add backend/alembic.ini backend/migrations backend/src/core/database.py backend/src/core/config.py
git commit -m "feat: add database and alembic setup"
```

### Task 4: 落 Session 和 StageRun 数据模型

**Files:**
- Create: `E:\thinkWhat\backend\src\modules\sessions\models.py`
- Create: `E:\thinkWhat\backend\src\modules\stages\models.py`
- Create: `E:\thinkWhat\backend\migrations\versions\0001_create_sessions_and_stage_runs.py`
- Test: `E:\thinkWhat\backend\tests\integration\test_session_stage_flow.py`

- [ ] **Step 1: 根据数据库草案写 ORM 模型**

要求：

- 落 `SessionModel`
- 落 `StageRunModel`
- 对齐现有字段：`current_stage`、`status`、`run_id`、`result_snapshot`

- [ ] **Step 2: 写首个 migration**

要求：

- 建 `sessions`
- 建 `stage_runs`
- 建必要索引

- [ ] **Step 3: 执行迁移验证**

Run:

```bash
cd backend
alembic upgrade head
```

Expected:

- 表创建成功
- 索引创建成功

- [ ] **Step 4: Commit**

```bash
git add backend/src/modules/sessions/models.py backend/src/modules/stages/models.py backend/migrations/versions
git commit -m "feat: add session and stage run models"
```

### Task 5: 实现 Sessions 模块 CRUD 与首页接口

**Files:**
- Create: `E:\thinkWhat\backend\src\modules\sessions\schemas.py`
- Create: `E:\thinkWhat\backend\src\modules\sessions\repository.py`
- Create: `E:\thinkWhat\backend\src\modules\sessions\service.py`
- Create: `E:\thinkWhat\backend\src\modules\sessions\router.py`
- Modify: `E:\thinkWhat\backend\src\app\api.py`
- Test: `E:\thinkWhat\backend\tests\contract\test_sessions_api.py`

- [ ] **Step 1: 定义 Sessions 请求与响应模型**

接口目标：

- `GET /api/v1/sessions`
- `POST /api/v1/sessions`
- `GET /api/v1/sessions/{sessionId}`
- `PATCH /api/v1/sessions/{sessionId}`
- `GET /api/v1/home/overview`

- [ ] **Step 2: 写 repository 和 service**

要求：

- repository 只做查询和写入
- service 负责首页概览聚合

- [ ] **Step 3: 写合同测试**

测试内容：

- 新建 session 成功
- 查询 session 列表成功
- 查询单个 session 成功
- 首页 overview 返回结构正确

- [ ] **Step 4: 跑测试**

Run:

```bash
cd backend
pytest tests/contract/test_sessions_api.py -q
```

Expected:

- sessions 相关接口通过

- [ ] **Step 5: Commit**

```bash
git add backend/src/modules/sessions backend/src/app/api.py backend/tests/contract/test_sessions_api.py
git commit -m "feat: add sessions and home overview APIs"
```

### Task 6: 实现 Stages 模块与工作台主链路

**Files:**
- Create: `E:\thinkWhat\backend\src\modules\stages\schemas.py`
- Create: `E:\thinkWhat\backend\src\modules\stages\repository.py`
- Create: `E:\thinkWhat\backend\src\modules\stages\service.py`
- Create: `E:\thinkWhat\backend\src\modules\stages\router.py`
- Create: `E:\thinkWhat\backend\src\orchestration\stage_orchestrator.py`
- Create: `E:\thinkWhat\backend\src\orchestration\role_router.py`
- Test: `E:\thinkWhat\backend\tests\contract\test_workspace_api.py`
- Test: `E:\thinkWhat\backend\tests\contract\test_stages_api.py`
- Test: `E:\thinkWhat\backend\tests\integration\test_session_stage_flow.py`

- [ ] **Step 1: 定义工作台与阶段接口 schema**

接口目标：

- `GET /api/v1/sessions/{sessionId}/workspace`
- `GET /api/v1/sessions/{sessionId}/stages`
- `GET /api/v1/sessions/{sessionId}/stages/{stage}`
- `POST /api/v1/sessions/{sessionId}/stages/{stage}/start`
- `POST /api/v1/sessions/{sessionId}/stages/{stage}/rerun`
- `POST /api/v1/sessions/{sessionId}/stages/{stage}/rollback`
- `PATCH /api/v1/sessions/{sessionId}/stages/{stage}/artifact`
- `GET /api/v1/stage-runs/{stageRunId}`

- [ ] **Step 2: 实现最小 orchestrator**

要求：

- 能创建 `stage_run`
- 能更新状态
- 能写入最小 `result_snapshot`
- 先用 stub 代替真实模型调用

- [ ] **Step 3: 写合同测试与集成测试**

测试内容：

- 工作台聚合接口返回结构符合文档
- start/rerun/rollback 状态变化正确
- stage artifact 可更新

- [ ] **Step 4: 跑测试**

Run:

```bash
cd backend
pytest tests/contract/test_workspace_api.py tests/contract/test_stages_api.py tests/integration/test_session_stage_flow.py -q
```

Expected:

- 工作台与阶段主链路通过

- [ ] **Step 5: Commit**

```bash
git add backend/src/modules/stages backend/src/orchestration backend/tests/contract/test_workspace_api.py backend/tests/contract/test_stages_api.py backend/tests/integration/test_session_stage_flow.py
git commit -m "feat: add workspace and stage orchestration APIs"
```

### Task 7: 接入 Activities 与最小埋点

**Files:**
- Create: `E:\thinkWhat\backend\src\modules\activities\models.py`
- Create: `E:\thinkWhat\backend\src\modules\activities\schemas.py`
- Create: `E:\thinkWhat\backend\src\modules\activities\repository.py`
- Create: `E:\thinkWhat\backend\src\modules\activities\service.py`
- Create: `E:\thinkWhat\backend\src\modules\activities\router.py`
- Create: `E:\thinkWhat\backend\migrations\versions\0002_create_user_actions.py`
- Modify: `E:\thinkWhat\backend\src\app\api.py`

- [ ] **Step 1: 增加 `user_actions` 模型与 migration**

要求：

- 建 `user_actions`
- 为 `session_created`、`stage_started`、`stage_completed` 等事件留入口

- [ ] **Step 2: 实现接口**

接口目标：

- `POST /api/v1/events`
- `GET /api/v1/sessions/{sessionId}/activities`

- [ ] **Step 3: 跑集成验证**

Run:

```bash
cd backend
alembic upgrade head
pytest tests/integration/test_session_stage_flow.py -q
```

Expected:

- 关键动作可写入并查询

- [ ] **Step 4: Commit**

```bash
git add backend/src/modules/activities backend/migrations/versions backend/src/app/api.py
git commit -m "feat: add activities and event logging"
```

### Task 8: 补 Research / Candidates / Recommendations 模块计划入口

**Files:**
- Create: `E:\thinkWhat\backend\src\modules\research\`
- Create: `E:\thinkWhat\backend\src\modules\candidates\`
- Create: `E:\thinkWhat\backend\src\modules\recommendations\`
- Modify: `E:\thinkWhat\backend\README.md`

- [ ] **Step 1: 建模块目录与占位文件**

要求：

- 先建目录与空文件
- 明确后续接口归属

- [ ] **Step 2: 在 README 中写后续开发顺序**

要求：

- 指明第二阶段接 `research + candidates`
- 第三阶段接 `recommendations + analytics`

- [ ] **Step 3: Commit**

```bash
git add backend/src/modules/research backend/src/modules/candidates backend/src/modules/recommendations backend/README.md
git commit -m "chore: prepare next backend modules"
```

### Task 9: 全量最小验证

**Files:**
- Verify: `E:\thinkWhat\backend\`

- [ ] **Step 1: 运行迁移**

Run:

```bash
cd backend
alembic upgrade head
```

Expected:

- 所有 migration 成功

- [ ] **Step 2: 运行合同测试与集成测试**

Run:

```bash
cd backend
pytest tests/contract tests/integration -q
```

Expected:

- 所有 P0 主链路测试通过

- [ ] **Step 3: 启动本地服务**

Run:

```bash
cd backend
uvicorn src.app.main:app --reload
```

Expected:

- 服务正常启动
- `/health` 返回 200

- [ ] **Step 4: Commit**

```bash
git add .
git commit -m "chore: validate backend scaffold baseline"
```

---

## 执行建议

执行顺序不要乱：

1. 先把工程和迁移框架立起来
2. 再做 `sessions`
3. 再做 `workspace + stages`
4. 再补 `activities`
5. 最后再扩 `research / candidates / recommendations / analytics`

不要一开始同时动所有模块，这会直接把骨架做散。
