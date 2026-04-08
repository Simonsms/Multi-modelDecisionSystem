# Paperclip 项目分析报告

**项目地址**：https://github.com/paperclipai/paperclip  
**分析日期**：2026-04-07  
**分析目标**：为决策支持系统提供架构和设计参考

---

## 一、项目概述

### 1.1 核心定位

Paperclip 是一个**自治 AI 公司的控制平面**，用于编排和管理多个 AI Agent 协同工作。

**核心理念**：
- 如果 OpenClaw 是一个"员工"，Paperclip 就是"公司"
- 管理业务目标，而不是管理代码
- 控制平面与执行层分离

### 1.2 适用场景

- 协调多个不同的 AI Agent（OpenClaw、Claude Code、Codex、Cursor）
- 需要 Agent 24/7 自主运行，但保留人工审计和介入能力
- 需要监控成本和执行预算控制
- 希望用任务管理器的方式管理 Agent

---

## 二、架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│  Paperclip 控制平面 (Node.js + Express + React)         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  核心功能                                        │   │
│  │  - Agent 注册和组织架构管理                      │   │
│  │  - 任务分配和状态追踪                            │   │
│  │  - 预算和成本追踪                                │   │
│  │  - 目标层级管理                                  │   │
│  │  - 心跳监控                                      │   │
│  │  - 审批流程                                      │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                    ↓ ↑ (API / Webhook / SSE)
┌─────────────────────────────────────────────────────────┐
│  执行层 (外部 Agent)                                     │
│  - OpenClaw                                             │
│  - Claude Code                                          │
│  - Codex                                                │
│  - 自定义 Python/Node 脚本                              │
│  - 任何能调用 API 的进程                                │
└─────────────────────────────────────────────────────────┘
```

**关键设计原则**：
1. **控制平面不执行 Agent**：Paperclip 只负责编排，Agent 在外部运行并回报状态
2. **适配器模式**：通过 Adapter 抽象不同的 Agent 执行方式
3. **公司作为一等公民**：一个 Paperclip 实例可以运行多个"公司"

### 2.2 Agent 执行模式

两种基本执行方式：

**模式 1：运行命令**
```typescript
// Paperclip 启动进程并监控
{
  type: 'process',
  command: 'claude-code --session-id=xxx',
  heartbeat_interval: 300 // 5分钟
}
```

**模式 2：触发通知**
```typescript
// Paperclip 发送 webhook，Agent 自己运行
{
  type: 'webhook',
  url: 'https://openclaw.example.com/wakeup',
  method: 'POST'
}
```

### 2.3 适配器架构

```typescript
// packages/adapters/ 目录结构
interface AgentAdapter {
  type: string;
  createRun(config: AdapterConfig): Promise<Run>;
  getStatus(runId: string): Promise<RunStatus>;
  sendMessage(runId: string, message: string): Promise<void>;
  cancel(runId: string): Promise<void>;
}

// 已实现的适配器
- OpenClaw Adapter
- Claude Code Adapter
- Codex Adapter
- Cursor Adapter
- HTTP Adapter (通用 webhook)
- Bash Adapter (执行脚本)
```

**对决策支持系统的启发**：
```typescript
// 可以实现类似的 LLM 适配器
interface LLMAdapter {
  provider: 'openai' | 'claude' | 'local';
  generateStage0(input: string): Promise<IdeaBrief>;
  generatePRD(requirements: Requirements): Promise<PRD>;
  reviewDesign(design: Design, role: string): Promise<Review>;
}
```

---

## 三、数据模型设计

### 3.1 核心实体关系

```sql
companies (公司)
  ├── agents (员工/Agent)
  │     ├── agent_config_revisions (配置版本)
  │     ├── agent_api_keys (API 密钥)
  │     └── agent_runtime_state (运行时状态)
  │
  ├── projects (项目)
  │     └── project_goals (项目目标)
  │
  ├── goals (目标层级)
  │
  ├── issues (任务)
  │     ├── issue_relations (任务关系)
  │     ├── issue_comments (评论)
  │     ├── issue_approvals (审批)
  │     ├── issue_attachments (附件)
  │     └── issue_documents (文档)
  │
  ├── heartbeat_runs (心跳执行记录)
  │     └── heartbeat_run_events (执行事件)
  │
  ├── cost_events (成本事件)
  ├── finance_events (财务事件)
  ├── budget_policies (预算策略)
  ├── budget_incidents (预算超支事件)
  │
  ├── approvals (审批流程)
  │     └── approval_comments (审批评论)
  │
  ├── activity_log (活动日志)
  │
  └── company_secrets (公司密钥)
```

### 3.2 关键表结构

**agents 表**：
```sql
{
  id, company_id, name, role,
  adapter_type, adapter_config,
  capabilities_description,
  reports_to_agent_id,  -- 组织架构
  status, created_at, updated_at
}
```

**issues 表**（任务）：
```sql
{
  id, company_id, title, description,
  status, priority,
  assigned_agent_id,
  parent_issue_id,  -- 层级结构
  goal_id,          -- 关联目标
  created_at, updated_at
}
```

**heartbeat_runs 表**（执行记录）：
```sql
{
  id, agent_id, issue_id,
  status, started_at, completed_at,
  output, error_message,
  tokens_input, tokens_output, cost_usd
}
```

**cost_events 表**（成本追踪）：
```sql
{
  id, company_id, agent_id, run_id,
  provider, model,
  tokens_input, tokens_output,
  cost_usd, timestamp
}
```

**activity_log 表**（操作日志）：
```sql
{
  id, company_id,
  actor_type: 'agent' | 'user',
  actor_id,
  action: 'issue.created' | 'run.started' | 'approval.granted',
  target_type, target_id,
  metadata: JSON,
  timestamp
}
```

### 3.3 对决策支持系统的映射

```sql
-- 你的系统可以这样设计

sessions (决策会话)
{
  id, user_id, title,
  initial_question,
  current_stage: 0 | 0.5 | 1 | 2 | 3 | 4,
  status: 'in_progress' | 'completed' | 'failed',
  created_at, updated_at
}

stages (阶段记录)
{
  id, session_id,
  stage_number: 0 | 0.5 | 1 | 2 | 3 | 4,
  status: 'pending' | 'in_progress' | 'completed',
  input_data: JSON,
  output_data: JSON,
  duration_ms,
  started_at, completed_at
}

documents (生成的文档)
{
  id, session_id, stage_id,
  type: 'idea_brief' | 'requirement_pack' | 'prd' | 'design',
  content: TEXT,
  version: INT,
  created_at
}

reviews (评审记录)
{
  id, session_id, document_id,
  agent_role: 'tech_lead' | 'product_manager' | 'security_expert',
  verdict: 'approve' | 'needs_discussion' | 'reject',
  findings: JSON,
  open_questions: JSON,
  created_at
}

decisions (最终决策)
{
  id, session_id,
  consensus_points: JSON,
  conflict_points: JSON,
  roundtable_discussion: JSON,
  final_verdict: 'approved' | 'needs_revision' | 'rejected',
  created_at
}

user_actions (用户行为追踪)
{
  id, session_id, user_id,
  stage, action_type,
  input_text, output_text,
  duration_ms, timestamp
}

analytics (数据提炼)
{
  id, session_id,
  question_intent: TEXT,
  decision_category: TEXT,
  decision_path: JSON,
  similar_sessions: JSON[],
  created_at
}
```

---

## 四、技术栈

### 4.1 后端

**核心框架**：
- Node.js 20+
- Express (REST API)
- TypeScript

**数据库**：
- PostgreSQL (生产环境)
- PGlite (开发环境，嵌入式)
- Drizzle ORM

**实时通信**：
- Server-Sent Events (SSE)

**认证**：
- JWT (Agent API Keys)
- Session-based (Board 用户)

### 4.2 前端

**核心框架**：
- React 18
- Vite
- TypeScript

**UI 组件**：
- shadcn/ui (基于 Radix UI)
- Tailwind CSS

**状态管理**：
- TanStack Query (React Query)
- Context API

**路由**：
- React Router

### 4.3 开发工具

**包管理**：
- pnpm (monorepo)

**测试**：
- Vitest (单元测试)
- Playwright (E2E 测试)

**构建**：
- esbuild
- tsx (TypeScript 执行)

---

## 五、核心功能实现

### 5.1 任务层级管理

**设计理念**：所有任务必须追溯到顶层目标

```
公司目标: "打造 #1 AI 笔记应用，3 个月内达到 $1M MRR"
  ↓
战略任务: "本周收入达到 $2,000"
  ↓
执行任务: "新增 100 个用户注册"
  ↓
具体任务: "创建 Facebook 广告"
  ↓
调研任务: "研究 Granola 使用的 Facebook 广告策略"
```

**实现方式**：
- `issues` 表的 `parent_issue_id` 字段
- `goal_id` 关联到顶层目标
- UI 展示任务链路

### 5.2 成本追踪

**追踪维度**：
- 每个 Agent 的 token 消耗
- 每次执行的成本
- 公司级别的总成本
- 预算策略和超支告警

**实现方式**：
```typescript
// 记录成本事件
await db.insert(costEvents).values({
  company_id,
  agent_id,
  run_id,
  provider: 'openai',
  model: 'gpt-4',
  tokens_input: 1500,
  tokens_output: 800,
  cost_usd: 0.045,
  timestamp: new Date()
});

// 检查预算
const totalCost = await db
  .select({ sum: sql`sum(cost_usd)` })
  .from(costEvents)
  .where(eq(costEvents.company_id, companyId));

if (totalCost > budgetPolicy.limit) {
  // 触发预算超支事件
  await pauseAllAgents(companyId);
}
```

### 5.3 审批流程

**触发场景**：
- Agent 提出战略决策
- 需要人工确认的高风险操作
- 预算超支需要批准

**实现方式**：
```typescript
// 创建审批请求
const approval = await db.insert(approvals).values({
  company_id,
  agent_id,
  issue_id,
  approval_type: 'strategic_decision',
  description: 'CEO 提议重新分配资源到营销团队',
  status: 'pending',
  requested_at: new Date()
});

// Agent 等待审批
while (approval.status === 'pending') {
  await sleep(5000);
  // 检查审批状态
}

if (approval.status === 'approved') {
  // 执行决策
}
```

### 5.4 实时状态推送

**使用 SSE 推送更新**：
```typescript
// 服务端
app.get('/api/companies/:id/events', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  const listener = (event) => {
    res.write(`data: ${JSON.stringify(event)}\n\n`);
  };

  eventEmitter.on('company_event', listener);

  req.on('close', () => {
    eventEmitter.off('company_event', listener);
  });
});

// 客户端
const eventSource = new EventSource('/api/companies/123/events');
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // 更新 UI
};
```

---

## 六、UI 设计

### 6.1 核心页面

**Dashboard（仪表盘）**：
- 公司概览
- Agent 状态（运行中/空闲/错误）
- 成本统计（今日/本周/本月）
- 最近活动

**Issues Board（任务看板）**：
- 看板视图（类似 Linear）
- 按状态分组：Backlog / In Progress / Review / Done
- 拖拽排序
- 快速筛选和搜索

**Agent Detail（Agent 详情）**：
- 基本信息（名称、角色、能力描述）
- 组织架构（上级、下级）
- 执行历史
- 成本统计
- 配置管理

**Approval Flow（审批流程）**：
- 待审批列表
- 审批详情
- 批准/拒绝操作
- 审批历史

### 6.2 设计特点

**渐进式信息披露**：
- 顶层：人类可读的摘要
- 中层：步骤/检查清单/产出物
- 底层：原始日志/工具调用/完整记录

**输出优先**：
- 工作完成后必须有可见结果
- 文件、文档、预览链接、截图、计划或 PR

**本地优先，云就绪**：
- 本地单人使用和云端共享的心智模型一致

---

## 七、对决策支持系统的启发

### 7.1 架构借鉴

**控制平面 + 执行层分离**：
```
决策编排引擎 (你的系统)
  ↓ ↑
LLM 执行层 (OpenAI / Claude / 本地模型)
```

**适配器模式**：
- 支持多种 LLM 提供商
- 统一的接口抽象
- 可插拔设计

### 7.2 数据模型借鉴

**层级结构**：
- Paperclip: 公司 → 目标 → 任务 → 子任务
- 你的系统: 会话 → Stage → 文档 → 评审

**成本追踪**：
- 记录每个 Stage 的 token 消耗
- 按会话统计总成本
- 提供成本优化建议

**活动日志**：
- 记录所有用户操作
- 用于数据分析和提炼

### 7.3 UI 设计借鉴

**Stage 流程可视化**：
```
● Stage 0 (完成) → ● Stage 1 (进行中) → ○ Stage 2 → ○ Stage 3 → ○ Stage 4
```

**文档预览**：
- Markdown 渲染
- 版本历史
- 导出功能

**评审结果展示**：
- 卡片式布局
- 按 Agent 角色分组
- 高亮冲突点

### 7.4 技术栈建议

**方案 A：完全复用 Paperclip 技术栈**
- 后端：Node.js + Express + Drizzle + PostgreSQL
- 前端：React + Vite + shadcn/ui
- 优势：生态成熟，已验证可行
- 劣势：如果更熟悉 Python，学习成本高

**方案 B：Python 后端 + React 前端（推荐）**
- 后端：FastAPI + SQLAlchemy + PostgreSQL
- 前端：React + Vite + shadcn/ui
- 优势：Python 生态更适合 AI/LLM 开发
- 劣势：需要自己实现适配器模式

**方案 C：全栈 TypeScript**
- 后端：NestJS + Prisma + PostgreSQL
- 前端：Next.js + shadcn/ui
- 优势：类型安全，前后端共享类型
- 劣势：NestJS 学习曲线陡峭

### 7.5 GUI 客户端建议

**桌面应用框架**：
- Tauri（推荐）：轻量、性能好、体积小
- Electron：生态成熟、社区大

**架构**：
```
Tauri/Electron 壳
  ↓
React 前端（复用 Web 版）
  ↓
本地 API 服务（FastAPI/Express）
  ↓
本地数据库（SQLite/PostgreSQL）
```

---

## 八、关键代码参考

### 8.1 适配器接口

```typescript
// packages/adapter-utils/src/types.ts
export interface AgentAdapter {
  type: string;
  
  createRun(config: {
    agent_id: string;
    issue_id: string;
    adapter_config: Record<string, any>;
  }): Promise<{
    run_id: string;
    status: 'running' | 'completed' | 'failed';
  }>;
  
  getStatus(run_id: string): Promise<{
    status: 'running' | 'completed' | 'failed';
    output?: string;
    error?: string;
  }>;
  
  sendMessage(run_id: string, message: string): Promise<void>;
  
  cancel(run_id: string): Promise<void>;
}
```

### 8.2 成本计算

```typescript
// server/src/services/cost-tracking.ts
export async function recordCostEvent(params: {
  company_id: string;
  agent_id: string;
  run_id: string;
  provider: string;
  model: string;
  tokens_input: number;
  tokens_output: number;
}) {
  const cost_usd = calculateCost(
    params.provider,
    params.model,
    params.tokens_input,
    params.tokens_output
  );
  
  await db.insert(costEvents).values({
    ...params,
    cost_usd,
    timestamp: new Date()
  });
  
  // 检查预算
  await checkBudgetPolicy(params.company_id);
}

function calculateCost(
  provider: string,
  model: string,
  input: number,
  output: number
): number {
  const pricing = {
    'openai/gpt-4': { input: 0.03, output: 0.06 },
    'openai/gpt-3.5-turbo': { input: 0.0015, output: 0.002 },
    'anthropic/claude-3-opus': { input: 0.015, output: 0.075 },
  };
  
  const key = `${provider}/${model}`;
  const rate = pricing[key];
  
  return (input / 1000 * rate.input) + (output / 1000 * rate.output);
}
```

### 8.3 实时事件推送

```typescript
// server/src/realtime/sse.ts
export class SSEManager {
  private connections = new Map<string, Response>();
  
  addConnection(company_id: string, res: Response) {
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    
    this.connections.set(company_id, res);
    
    res.on('close', () => {
      this.connections.delete(company_id);
    });
  }
  
  broadcast(company_id: string, event: any) {
    const res = this.connections.get(company_id);
    if (res) {
      res.write(`data: ${JSON.stringify(event)}\n\n`);
    }
  }
}
```

---

## 九、部署和运维

### 9.1 部署方式

**本地开发**：
```bash
pnpm install
pnpm dev  # 启动 API (3100) 和 UI (3100)
```

**生产部署**：
```bash
pnpm build
pnpm start
```

**Docker 部署**：
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY . .
RUN pnpm install --frozen-lockfile
RUN pnpm build
CMD ["pnpm", "start"]
```

### 9.2 数据库迁移

```bash
# 生成迁移
pnpm db:generate

# 执行迁移
pnpm db:migrate

# 备份数据库
pnpm db:backup
```

---

## 十、总结

### 10.1 Paperclip 的核心价值

1. **清晰的架构分层**：控制平面与执行层分离
2. **灵活的适配器模式**：支持多种 Agent 类型
3. **完善的成本追踪**：token 级别的成本监控
4. **层级化的任务管理**：所有工作追溯到顶层目标
5. **实时状态推送**：SSE 实现低延迟更新
6. **审批流程**：人工介入点设计合理

### 10.2 可直接复用的部分

1. **数据模型设计**：表结构和关系设计
2. **适配器模式**：LLM 提供商抽象
3. **成本追踪逻辑**：token 计算和预算控制
4. **实时通信方案**：SSE 推送
5. **UI 组件库**：shadcn/ui
6. **前端架构**：React + Vite + TanStack Query

### 10.3 需要调整的部分

1. **业务模型**：从"公司-Agent-任务"映射到"会话-Stage-文档-评审"
2. **执行逻辑**：从"Agent 心跳"改为"Stage 流程编排"
3. **评审机制**：增加多 Agent 独立评审和圆桌讨论
4. **数据分析**：增加问题提炼和决策路径分析

---

## 十一、下一步行动

1. **继续调研**：
   - 重点关注 Multi-Agent 编排方式
   - 决策流程可视化
   - 数据分析和提炼方法

2. **技术选型**：
   - 确定前端框架（Electron/Tauri + React/Vue）
   - 确定后端框架（FastAPI/NestJS）
   - 确定 LLM 编排方式（LangGraph/AutoGen/自研）

3. **原型设计**：
   - 主界面布局
   - Stage 流程可视化
   - 文档预览和评审展示

4. **数据库设计**：
   - 参考 Paperclip 的表结构
   - 设计会话、Stage、文档、评审表
   - 设计数据分析表

---

**文档版本**：v1.0  
**最后更新**：2026-04-07
