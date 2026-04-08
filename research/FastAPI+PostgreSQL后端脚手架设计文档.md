# FastAPI + PostgreSQL 后端脚手架设计文档

**文档日期**：2026-04-08  
**文档目标**：基于当前已经收敛的 P0 接口、数据库草案和 GUI 工作台主链路，给出一版可直接开工的 `FastAPI + PostgreSQL` 后端脚手架设计  
**适用范围**：后端技术选型确认、代码骨架搭建、首批接口开发、数据库迁移落地

---

## 1. 核心判断

当前最合适的第一版后端落地方向是：

> **FastAPI + PostgreSQL + SQLAlchemy 2.x + Alembic**

理由不是“技术新”，而是它刚好匹配你们现在的阶段：

- 需要尽快把 REST 接口和工作台骨架跑起来
- 需要比较稳的结构化建模能力
- 需要后续接多模型调用、阶段编排和活动日志
- 需要用较低复杂度把接口、数据库和 Pydantic 校验串起来

第一版不建议把后端做成复杂微服务，而应该做成：

> **单体模块化后端**

也就是：

- 进程先单体
- 模块按业务边界拆
- 控制住目录和依赖方向
- 真到流量、团队和边界都稳定后，再考虑拆服务

---

## 2. 设计目标

这版脚手架要解决 6 件事：

1. 能承接 P0 页面所需 REST 接口
2. 能稳定落 PostgreSQL 数据
3. 能按业务模块组织代码，而不是一团平铺
4. 能为多模型调用留适配器边界
5. 能记录最小活动日志和模型调用链路
6. 能让后续继续扩功能时不需要推倒重来

---

## 3. 非目标

第一版脚手架明确不解决：

- WebSocket 实时通道
- 分布式任务调度平台
- 多租户权限体系
- 评论协作系统
- 自动网页抓取系统
- 完整导出系统
- 插件化平台

这些都可以后加，但现在做只会把骨架做重。

---

## 4. 推荐技术栈

## 4.1 基础栈

- Web 框架：`FastAPI`
- ASGI Server：`uvicorn`
- 数据库：`PostgreSQL`
- ORM：`SQLAlchemy 2.x`
- 迁移：`Alembic`
- 数据校验：`Pydantic v2`
- 配置管理：`pydantic-settings`
- 测试：`pytest`
- HTTP 测试：`httpx`

## 4.2 可选补充

- 异步数据库驱动：`asyncpg`
- 开发工具：`ruff`、`black`
- 类型检查：`mypy`

## 4.3 为什么不建议第一版先上这些

不建议第一版先上：

- Celery
- Kafka
- Redis Stream
- DDD 重框架
- GraphQL

原因：

- 当前主问题不是吞吐量，而是边界和实现速度
- 现在最值钱的是把工作台主链路打通

---

## 5. 总体架构

```text
Frontend GUI
   │
   ▼
FastAPI Router Layer
   │
   ▼
Service Layer
   │
   ├─ Repository Layer
   │      │
   │      ▼
   │   PostgreSQL
   │
   ├─ Orchestrator Layer
   │      │
   │      ▼
   │   Model Adapters
   │
   └─ Activity / Analytics Writers
```

## 5.1 分层职责

### Router Layer

职责：

- 接收 HTTP 请求
- 做参数校验
- 组织响应模型
- 不写业务主逻辑

### Service Layer

职责：

- 写页面与模块级业务逻辑
- 控制事务边界
- 聚合多个 repository 结果

### Repository Layer

职责：

- 只负责数据库读写
- 不掺业务决策

### Orchestrator Layer

职责：

- 管阶段推进
- 管多模型角色调用
- 管运行状态和活动记录

### Adapter Layer

职责：

- 屏蔽具体模型提供方差异
- 标准化输入输出

---

## 6. 目录骨架设计

建议目录如下：

```text
backend/
├─ pyproject.toml
├─ README.md
├─ .env.example
├─ alembic.ini
├─ migrations/
│  ├─ env.py
│  └─ versions/
├─ src/
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ api.py
│  │  ├─ deps.py
│  │  └─ lifespan.py
│  ├─ core/
│  │  ├─ config.py
│  │  ├─ database.py
│  │  ├─ logging.py
│  │  ├─ errors.py
│  │  └─ enums.py
│  ├─ modules/
│  │  ├─ sessions/
│  │  │  ├─ router.py
│  │  │  ├─ schemas.py
│  │  │  ├─ service.py
│  │  │  ├─ repository.py
│  │  │  └─ models.py
│  │  ├─ stages/
│  │  ├─ research/
│  │  ├─ candidates/
│  │  ├─ recommendations/
│  │  ├─ analytics/
│  │  └─ activities/
│  ├─ orchestration/
│  │  ├─ stage_orchestrator.py
│  │  ├─ role_router.py
│  │  └─ decision_judge.py
│  ├─ adapters/
│  │  └─ models/
│  │     ├─ base.py
│  │     ├─ openai_adapter.py
│  │     ├─ anthropic_adapter.py
│  │     └─ gemini_adapter.py
│  └─ shared/
│     ├─ types.py
│     └─ utils.py
└─ tests/
   ├─ contract/
   ├─ integration/
   └─ unit/
```

## 6.1 目录设计原则

- `app/` 放应用启动和路由汇总
- `core/` 放真正全局共享的基础能力
- `modules/` 放业务模块
- `orchestration/` 放阶段编排逻辑
- `adapters/` 放外部模型或外部服务适配器

不要把所有东西都塞进 `services/`、`utils/` 这种垃圾抽屉。

---

## 7. 模块拆分与依赖方向

## 7.1 业务模块

第一版保留这 6 个业务模块：

- `sessions`
- `stages`
- `research`
- `candidates`
- `recommendations`
- `analytics`

再加一个横切模块：

- `activities`

## 7.2 依赖方向

推荐依赖规则：

- `router -> service -> repository`
- `service -> orchestration`
- `orchestration -> adapters`
- `repository -> database session`

不允许：

- `router -> repository`
- `repository -> service`
- `models.py` 互相循环导入

---

## 8. 核心文件职责

## 8.1 `src/app/main.py`

职责：

- 创建 FastAPI 实例
- 注册 lifespan
- 挂载全局异常处理
- 挂载主路由

## 8.2 `src/app/api.py`

职责：

- 统一组合各模块 router
- 固定 API 前缀为 `/api/v1`

## 8.3 `src/core/config.py`

职责：

- 从环境变量读取配置
- 统一管理数据库、模型、日志相关配置

建议配置项：

- `app_name`
- `app_env`
- `debug`
- `database_url`
- `openai_api_key`
- `anthropic_api_key`
- `gemini_api_key`

## 8.4 `src/core/database.py`

职责：

- 创建 SQLAlchemy `engine`
- 创建 `SessionLocal`
- 提供 `get_db()` 依赖

## 8.5 `src/modules/*/models.py`

职责：

- 放当前模块的 ORM 模型
- 不写业务逻辑

## 8.6 `src/modules/*/schemas.py`

职责：

- 放请求体和响应体的 Pydantic 模型
- 明确接口契约

## 8.7 `src/modules/*/service.py`

职责：

- 写模块主逻辑
- 调用 repository 与其他模块服务

## 8.8 `src/modules/*/repository.py`

职责：

- 封装数据库查询、创建、更新

---

## 9. 路由组织方案

## 9.1 路由前缀建议

```text
/api/v1/home
/api/v1/sessions
/api/v1/stage-runs
/api/v1/research-items
/api/v1/evidences
/api/v1/candidates
/api/v1/recommendations
/api/v1/analytics
/api/v1/events
```

## 9.2 模块与路由对应

### `sessions/router.py`

承接：

- `GET /home/overview`
- `GET /sessions`
- `POST /sessions`
- `GET /sessions/{sessionId}`
- `PATCH /sessions/{sessionId}`
- `GET /sessions/{sessionId}/workspace`

### `stages/router.py`

承接：

- `GET /sessions/{sessionId}/stages`
- `GET /sessions/{sessionId}/stages/{stage}`
- `POST /sessions/{sessionId}/stages/{stage}/start`
- `POST /sessions/{sessionId}/stages/{stage}/rerun`
- `POST /sessions/{sessionId}/stages/{stage}/rollback`
- `PATCH /sessions/{sessionId}/stages/{stage}/artifact`
- `GET /stage-runs/{stageRunId}`

### `research/router.py`

承接：

- `GET /research-items`
- `POST /research-items`
- `GET /research-items/{researchItemId}`
- `PATCH /research-items/{researchItemId}`
- `POST /research-items/{researchItemId}/evidences`
- `PATCH /evidences/{evidenceId}`
- `POST /evidences/{evidenceId}/link-candidates`

### `candidates/router.py`

承接：

- `GET /sessions/{sessionId}/candidates`
- `POST /sessions/{sessionId}/candidates`
- `GET /candidates/{candidateId}`
- `PATCH /candidates/{candidateId}`
- `GET /sessions/{sessionId}/comparison`
- `POST /sessions/{sessionId}/comparison/rebuild`

### `recommendations/router.py`

承接：

- `GET /sessions/{sessionId}/recommendation`
- `POST /sessions/{sessionId}/recommendation/generate`
- `PATCH /recommendations/{recommendationId}`
- `POST /recommendations/{recommendationId}/accept`
- `POST /recommendations/{recommendationId}/reject`
- `POST /recommendations/{recommendationId}/send-back`

### `analytics/router.py`

承接：

- `GET /analytics/overview`
- `GET /analytics/stage-funnel`
- `GET /analytics/model-usage`

### `activities/router.py`

承接：

- `POST /events`
- `GET /sessions/{sessionId}/activities`
- `GET /sessions/{sessionId}/model-invocations`

---

## 10. ORM 建模建议

## 10.1 Base Model

建议统一定义一个 `Base` 和可复用 mixin：

- `TimestampMixin`
- `UUIDPrimaryKeyMixin`

这样可以统一：

- `id`
- `created_at`
- `updated_at`

## 10.2 第一版 ORM 模型

建议和前面数据库草案完全对齐：

- `SessionModel`
- `StageRunModel`
- `ResearchItemModel`
- `EvidenceModel`
- `CandidateOptionModel`
- `EvidenceCandidateLinkModel`
- `DecisionRecommendationModel`
- `ModelInvocationModel`
- `UserActionModel`
- `UsageMetricModel`

## 10.3 ORM 关系建议

- `SessionModel.stage_runs`
- `SessionModel.research_items`
- `SessionModel.candidate_options`
- `SessionModel.recommendations`
- `SessionModel.model_invocations`
- `SessionModel.user_actions`

不要一开始把所有关系都写得极深，避免：

- 级联过重
- 查询隐式膨胀
- 序列化循环

---

## 11. 数据迁移策略

## 11.1 推荐做法

使用 `Alembic` 管迁移。

第一版建议迁移切分：

1. `sessions` 与公共枚举
2. `stage_runs`
3. `research_items` 与 `evidences`
4. `candidate_options` 与关联表
5. `decision_recommendations`
6. `model_invocations`
7. `user_actions` 与 `usage_metrics`

## 11.2 不建议做法

不建议：

- 手写一大坨初始化 SQL 然后长期不管
- 让 ORM 自动建表作为正式方案

开发阶段可以临时自动建表，但正式工程应以迁移为准。

---

## 12. 阶段编排落地方式

## 12.1 `stage_orchestrator.py`

职责：

- 校验当前会话是否允许进入目标阶段
- 创建 `stage_run`
- 调用角色路由
- 记录模型调用
- 写回阶段产物
- 写入活动日志

## 12.2 `role_router.py`

职责：

- 根据 `stage + role` 映射具体模型

第一版可以先写成本地配置映射，例如：

```python
ROLE_MODEL_MAP = {
    "problem_definition": {
        "clarifier": "openai:gpt-4.1",
        "structurer": "anthropic:claude-sonnet",
    },
    "research_analysis": {
        "researcher": "openai:gpt-4.1",
        "divergent_thinker": "gemini:gemini-2.5-pro",
    },
}
```

## 12.3 `decision_judge.py`

职责：

- 将多个模型输出收敛成结构化阶段结果
- 为 recommendation 生成前置聚合结果

第一版建议：

- 规则 + 模型混合
- 不要单纯再叫一个模型“随便总结”

---

## 13. 模型适配器设计

## 13.1 `base.py`

定义统一接口：

```python
class BaseModelAdapter:
    async def invoke(self, *, role: str, prompt: str, metadata: dict) -> dict:
        raise NotImplementedError
```

## 13.2 每个 adapter 的输出结构

统一返回至少这些字段：

```python
{
    "status": "completed",
    "summary": "结构化摘要",
    "raw_output_ref": None,
    "input_tokens": 100,
    "output_tokens": 200,
    "cost_amount": 0.0123,
    "latency_ms": 1800
}
```

这样 `stage_orchestrator` 就能统一写 `model_invocations`。

---

## 14. 配置与环境变量

建议 `.env.example` 至少包含：

```env
APP_NAME=thinkWhat-backend
APP_ENV=development
DEBUG=true
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/thinkwhat
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GEMINI_API_KEY=
LOG_LEVEL=INFO
```

## 14.1 配置原则

- 所有敏感值只走环境变量
- 不把 provider key 写死在代码里
- 所有布尔和枚举配置集中管理

---

## 15. 错误处理策略

第一版建议统一三类错误：

- `ValidationError`
- `DomainError`
- `InfrastructureError`

对应场景：

- 参数不合法
- 业务状态不允许
- 数据库或模型调用失败

FastAPI 层统一转成结构化响应：

```json
{
  "data": null,
  "meta": {
    "requestId": "req_xxx"
  },
  "error": {
    "code": "stage_not_available",
    "message": "当前阶段不允许直接推进"
  }
}
```

---

## 16. 测试策略

第一版测试不求全覆盖，但必须覆盖主链路。

## 16.1 单元测试

重点测：

- `stage_orchestrator`
- `decision_judge`
- 各 service 的状态流转逻辑

## 16.2 集成测试

重点测：

- `sessions`
- `workspace`
- `stages start/rerun/rollback`
- `recommendation generate`

## 16.3 合同测试

重点测：

- 响应结构是否符合页面字段清单
- 聚合接口字段是否稳定

---

## 17. 本地开发流程

推荐本地流程：

1. 启 PostgreSQL
2. 配 `.env`
3. 执行 Alembic migration
4. 启 FastAPI
5. 跑 API 测试

建议命令形态：

```bash
alembic upgrade head
uvicorn src.app.main:app --reload
pytest
```

---

## 18. 第一批应创建的文件

如果下一步开始真正搭骨架，建议先创建这些文件：

- `backend/pyproject.toml`
- `backend/.env.example`
- `backend/alembic.ini`
- `backend/src/app/main.py`
- `backend/src/app/api.py`
- `backend/src/core/config.py`
- `backend/src/core/database.py`
- `backend/src/modules/sessions/router.py`
- `backend/src/modules/sessions/service.py`
- `backend/src/modules/sessions/repository.py`
- `backend/src/modules/sessions/schemas.py`
- `backend/src/modules/sessions/models.py`
- `backend/src/modules/stages/router.py`
- `backend/src/modules/stages/service.py`
- `backend/src/modules/stages/repository.py`
- `backend/src/modules/stages/schemas.py`
- `backend/src/modules/stages/models.py`

第一批目标很明确：

- 先让 `sessions + workspace + stages` 站起来

---

## 19. 推荐的实现顺序

### 第一步

- 起 `FastAPI` 基础应用
- 接数据库连接
- 跑通 Alembic

### 第二步

- 建 `sessions`、`stage_runs`
- 打通首页和工作台骨架接口

### 第三步

- 接 `research`、`candidates`
- 做比较聚合

### 第四步

- 接 `recommendations`
- 接 `activities`、`model_invocations`

### 第五步

- 做 `analytics` 轻量接口

---

## 20. 当前结论

这版 `FastAPI + PostgreSQL` 设计的本质，不是给你一个“后端模板”，而是给你一个和你当前产品阶段匹配的控制后端骨架。

如果压缩成一句话：

> 用 `FastAPI + PostgreSQL` 做一个单体模块化后端，先把 `sessions + stages + workspace` 打通，再逐步接 `research + recommendation + analytics`，这是当前最稳的实现路径。
