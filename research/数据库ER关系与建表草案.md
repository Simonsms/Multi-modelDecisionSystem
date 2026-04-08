# 数据库 ER 关系与建表草案

**文档日期**：2026-04-08  
**文档目标**：基于当前的后端接口草案与 P0 实现边界，输出第一版数据库实体关系说明与可落地的建表 SQL 草案  
**适用范围**：数据库选型、后端持久层实现、ORM 建模、建表脚本起草

---

## 1. 核心判断

第一版数据库设计要服务的，不是一个“大平台”，而是这条主链路：

```text
Session -> StageRun -> Research/Evidence -> CandidateOption -> DecisionRecommendation
```

数据库设计的目标也只有四个：

1. 支撑会话和阶段推进
2. 支撑调研、证据、候选方案和建议沉淀
3. 支撑模型调用和最小埋点
4. 允许后续扩展，但不提前过度拆表

---

## 2. 数据库选型假设

这一版建表草案默认以 **PostgreSQL** 作为参考方言。

原因：

- 结构化字段和 `jsonb` 混合使用比较顺手
- 对索引、统计和后续聚合支持较稳
- 适合现在这种“主结构明确，局部仍需保留灵活字段”的阶段

说明：

- 这是推荐，不是硬绑定
- 如果后续选 MySQL，核心表关系仍然成立，只需要调整 `jsonb`、时间类型和索引写法

---

## 3. 第一版 ER 关系

## 3.1 主关系

```text
sessions
  ├─< stage_runs
  ├─< research_items
  ├─< candidate_options
  ├─< decision_recommendations
  ├─< model_invocations
  └─< user_actions

research_items
  └─< evidences

evidences
  └─< evidence_candidate_links >─┐
                                 └─ candidate_options

stage_runs
  ├─< model_invocations
  └─< decision_recommendations
```

## 3.2 关系说明

- 一个 `session` 会有多次 `stage_run`
- 一个 `session` 会沉淀多条 `research_item`
- 一个 `research_item` 下会挂多条 `evidence`
- `evidence` 和 `candidate_option` 是多对多
- 一个 `session` 可以生成多条 `decision_recommendation`
- 一个 `stage_run` 会关联多条 `model_invocation`
- 一个 `session` 会产生多条 `user_action`

---

## 4. 第一版建模原则

## 4.1 主实体先实体化，复杂评分先不拆

第一版建议直接实体化：

- `sessions`
- `stage_runs`
- `research_items`
- `evidences`
- `candidate_options`
- `evidence_candidate_links`
- `decision_recommendations`
- `model_invocations`
- `user_actions`
- `usage_metrics`

先不实体化：

- 复杂比较维度表
- 推荐版本差异表
- 协作评论表
- 细粒度 trace 表

## 4.2 适度使用 `jsonb`

第一版这些字段可以先保留在 `jsonb`：

- `tags`
- `input_snapshot`
- `result_snapshot`
- `borrowable_points`
- `avoid_points`
- `fit_stages`
- `pros`
- `risks`
- `score_summary`
- `rationale`
- `alternative_option_ids`
- `open_questions`
- `next_steps`
- `payload`

原因：

- 当前结构已经基本明确，但还没稳定到值得全部拆表
- 现在先追求实现速度和结构清楚

## 4.3 审计先轻量

第一版建议：

- 业务关键动作进 `user_actions`
- 原始模型 trace 只保留 `trace_ref`
- 不额外建超重的审计表簇

---

## 5. 建表 SQL 草案

下面的 SQL 以 PostgreSQL 风格写，目的是让后端开发能直接起步，不是要求你现在立刻执行。

## 5.1 `sessions`

```sql
create table if not exists sessions (
  id uuid primary key,
  title varchar(255) not null,
  initial_question text not null,
  summary text,
  current_stage varchar(64) not null,
  status varchar(32) not null default 'draft',
  owner_id varchar(64),
  tags jsonb not null default '[]'::jsonb,
  latest_recommendation_id uuid,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  archived_at timestamptz
);

create index if not exists idx_sessions_status_updated_at
  on sessions (status, updated_at desc);

create index if not exists idx_sessions_current_stage_updated_at
  on sessions (current_stage, updated_at desc);
```

## 5.2 `stage_runs`

```sql
create table if not exists stage_runs (
  id uuid primary key,
  session_id uuid not null references sessions(id),
  stage varchar(64) not null,
  run_id varchar(64) not null,
  status varchar(32) not null,
  triggered_by varchar(32) not null,
  input_snapshot jsonb not null default '{}'::jsonb,
  result_snapshot jsonb not null default '{}'::jsonb,
  error_message text,
  started_at timestamptz,
  completed_at timestamptz,
  duration_ms bigint,
  created_at timestamptz not null default now()
);

create index if not exists idx_stage_runs_session_stage_created_at
  on stage_runs (session_id, stage, created_at desc);

create index if not exists idx_stage_runs_run_id
  on stage_runs (run_id);
```

## 5.3 `research_items`

```sql
create table if not exists research_items (
  id uuid primary key,
  session_id uuid not null references sessions(id),
  source_type varchar(32) not null,
  title varchar(255) not null,
  source_url text,
  summary text,
  verdict_tag varchar(32),
  borrowable_points jsonb not null default '[]'::jsonb,
  avoid_points jsonb not null default '[]'::jsonb,
  fit_stages jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_research_items_session_source_type
  on research_items (session_id, source_type);

create index if not exists idx_research_items_session_verdict_tag
  on research_items (session_id, verdict_tag);
```

## 5.4 `evidences`

```sql
create table if not exists evidences (
  id uuid primary key,
  research_item_id uuid not null references research_items(id),
  session_id uuid not null references sessions(id),
  summary text not null,
  tag varchar(64),
  source_ref text,
  confidence numeric(4,2),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_evidences_research_item_created_at
  on evidences (research_item_id, created_at desc);

create index if not exists idx_evidences_session_tag
  on evidences (session_id, tag);
```

## 5.5 `candidate_options`

```sql
create table if not exists candidate_options (
  id uuid primary key,
  session_id uuid not null references sessions(id),
  source_stage varchar(64) not null,
  title varchar(255) not null,
  summary text,
  pros jsonb not null default '[]'::jsonb,
  risks jsonb not null default '[]'::jsonb,
  status_label varchar(32) not null default 'active',
  score_summary jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_candidate_options_session_status_label
  on candidate_options (session_id, status_label);

create index if not exists idx_candidate_options_session_created_at
  on candidate_options (session_id, created_at desc);
```

## 5.6 `evidence_candidate_links`

```sql
create table if not exists evidence_candidate_links (
  id uuid primary key,
  evidence_id uuid not null references evidences(id),
  candidate_id uuid not null references candidate_options(id),
  relation_type varchar(32) not null default 'reference',
  created_at timestamptz not null default now(),
  unique (evidence_id, candidate_id, relation_type)
);

create index if not exists idx_evidence_candidate_links_candidate_id
  on evidence_candidate_links (candidate_id);

create index if not exists idx_evidence_candidate_links_evidence_id
  on evidence_candidate_links (evidence_id);
```

## 5.7 `decision_recommendations`

```sql
create table if not exists decision_recommendations (
  id uuid primary key,
  session_id uuid not null references sessions(id),
  based_on_stage_run_id uuid references stage_runs(id),
  title varchar(255) not null,
  summary text,
  status_label varchar(32) not null default 'generated',
  rationale jsonb not null default '[]'::jsonb,
  alternative_option_ids jsonb not null default '[]'::jsonb,
  risks jsonb not null default '[]'::jsonb,
  open_questions jsonb not null default '[]'::jsonb,
  next_steps jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_decision_recommendations_session_created_at
  on decision_recommendations (session_id, created_at desc);

create index if not exists idx_decision_recommendations_status_label_created_at
  on decision_recommendations (status_label, created_at desc);
```

## 5.8 `model_invocations`

```sql
create table if not exists model_invocations (
  id uuid primary key,
  session_id uuid not null references sessions(id),
  stage_run_id uuid not null references stage_runs(id),
  run_id varchar(64) not null,
  role varchar(64) not null,
  provider varchar(64) not null,
  model_name varchar(128) not null,
  status varchar(32) not null,
  input_tokens integer,
  output_tokens integer,
  cost_amount numeric(10,4),
  latency_ms bigint,
  error_code varchar(64),
  error_message text,
  started_at timestamptz,
  completed_at timestamptz,
  trace_ref text,
  created_at timestamptz not null default now()
);

create index if not exists idx_model_invocations_session_created_at
  on model_invocations (session_id, created_at desc);

create index if not exists idx_model_invocations_stage_run_id
  on model_invocations (stage_run_id);

create index if not exists idx_model_invocations_provider_model_created_at
  on model_invocations (provider, model_name, created_at desc);
```

## 5.9 `user_actions`

```sql
create table if not exists user_actions (
  id uuid primary key,
  session_id uuid references sessions(id),
  stage varchar(64),
  actor_type varchar(32) not null,
  actor_id varchar(64),
  action_type varchar(64) not null,
  payload jsonb not null default '{}'::jsonb,
  occurred_at timestamptz not null default now()
);

create index if not exists idx_user_actions_session_occurred_at
  on user_actions (session_id, occurred_at desc);

create index if not exists idx_user_actions_action_type_occurred_at
  on user_actions (action_type, occurred_at desc);
```

## 5.10 `usage_metrics`

```sql
create table if not exists usage_metrics (
  id uuid primary key,
  metric_date date not null,
  metric_name varchar(64) not null,
  metric_group varchar(64) not null,
  dimension_key varchar(64),
  dimension_value varchar(128),
  metric_value numeric(18,4) not null,
  created_at timestamptz not null default now()
);

create index if not exists idx_usage_metrics_date_name
  on usage_metrics (metric_date, metric_name);

create index if not exists idx_usage_metrics_group_dimension_date
  on usage_metrics (metric_group, dimension_key, metric_date);
```

---

## 6. 建表顺序建议

建议按依赖顺序建表：

1. `sessions`
2. `stage_runs`
3. `research_items`
4. `evidences`
5. `candidate_options`
6. `evidence_candidate_links`
7. `decision_recommendations`
8. `model_invocations`
9. `user_actions`
10. `usage_metrics`

原因：

- 避免外键顺序冲突
- 更适合后续拆分 migration

---

## 7. 第一版不建议现在做的数据库设计

## 7.1 不建议提前拆成十几张从表

例如：

- `candidate_pros`
- `candidate_risks`
- `recommendation_next_steps`
- `research_item_fit_stages`

这些现在都能拆，但不值得现在拆。

## 7.2 不建议一开始就做事件总线式事件存储

第一版 `user_actions` 足够承接最小埋点和活动流。

## 7.3 不建议过早做多租户

当前用户角色和组织边界还没有稳定，强上租户字段只会带来噪音。

---

## 8. 后续可以追加的表

当下面这些需求真正成立时，再追加拆分：

- `comparison_dimensions`
- `comparison_scores`
- `recommendation_exports`
- `comments`
- `attachments`
- `trace_bundles`

原则不变：

- 有真实页面需求再拆
- 有真实查询痛点再拆

---

## 9. 当前结论

第一版数据库不应该朝“高度范式化平台底座”走，而应该朝“主链路稳定、局部灵活、后续可演进”的方向走。

如果压缩成一句话：

> 先把 `sessions / stage_runs / research_items / candidate_options / decision_recommendations / model_invocations / user_actions` 这几张主表建稳，第一版数据库就够用了。
