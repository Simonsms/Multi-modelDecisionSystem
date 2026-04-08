# Paperclip 项目分析报告（深度版）

**项目地址**：<https://github.com/paperclipai/paperclip>  
**分析日期**：2026-04-08  
**分析目的**：围绕“渐进式 AI 决策支持系统”提炼可借鉴的工作台设计、通信方式、多模型决策组织方式，以及用户数据采集策略  
**适用范围**：本项目当前阶段的产品设计、架构选型、后台数据设计、后续开源项目对比分析

---

## 1. 先给结论

Paperclip 最值得借鉴的，不是“零人公司”这个产品叙事，而是它作为**控制平面**的几个硬能力：

1. 把复杂 AI 执行过程变成可管理、可审计、可恢复的工作流
2. 用统一的控制面抽象多种 agent/runtime，而不是绑定某个模型或某个 CLI
3. 用任务线程、运行记录、活动日志、预算和治理，把“AI 在干什么”从黑盒变成可追踪系统
4. 用实时更新机制，把控制台做成真正的“工作台”，而不是静态后台

对你们当前项目的意义是：

- **可以借鉴它的工作台与治理思路**
- **不能照搬它的业务模型**
- **要把它的 agent 控制平面，映射成你们的多模型决策控制平面**

更直接一点：

> Paperclip 适合借来搭“骨架”，不适合直接拿来当“灵魂”。

你们的灵魂不是“经营 AI 公司”，而是“推动问题逐步收敛为决策建议”。

---

## 2. Paperclip 的真实定位

从 README、核心概念文档和 API 文档看，Paperclip 的产品定位非常明确：

- 它是一个 **Node.js server + React UI** 的控制平面
- 它管理的是 **company / agent / issue / heartbeat / governance**
- 它不关心 agent 内部怎么实现，只关心如何协调、追踪、控制、审计它们

源码与文档证据：

- README 明确写的是 “Open-source orchestration for zero-human companies”
- [docs/start/core-concepts.md](https://github.com/paperclipai/paperclip/blob/master/docs/start/core-concepts.md) 把核心对象定义为 `Company`、`Agents`、`Issues`、`Delegation`、`Heartbeats`、`Governance`
- [docs/api/overview.md](https://github.com/paperclipai/paperclip/blob/master/docs/api/overview.md) 明确它暴露的是 RESTful JSON API

对你们来说，这意味着：

- 不要把它看成“聊天产品”
- 也不要只把它看成“多 agent 编排器”
- 更准确的理解是：**它是 AI 执行活动的控制台和治理层**

---

## 3. 你们真正该借鉴的设计模式

## 3.1 控制平面与执行层分离

这是 Paperclip 最值得借鉴的第一原则。

在 Paperclip 里：

- 控制平面负责：任务、状态、预算、审批、审计、实时更新
- 执行层负责：具体跑 Claude、Codex、OpenCode、HTTP agent、process agent

证据：

- [docs/agents-runtime.md](https://github.com/paperclipai/paperclip/blob/master/docs/agents-runtime.md) 明确说明每次 heartbeat 都是启动具体 adapter，再记录结果、token、错误、日志
- [doc/spec/agent-runs.md](https://github.com/paperclipai/paperclip/blob/master/doc/spec/agent-runs.md) 把 `Adapter Registry`、`Wakeup Coordinator`、`Run Executor`、`Runtime State Store`、`RunLogStore`、`Realtime Event Hub` 分成独立组件

映射到你们系统后，应该变成：

- 控制平面：决策会话、阶段流转、候选方案、证据、结论、用户反馈、审计、统计
- 执行层：OpenAI / Claude / Gemini / 本地模型 / 检索模块 / 评估模块

建议抽象：

```ts
interface ModelExecutor {
  provider: string;
  model: string;
  invoke(input: StageInvocationInput): Promise<StageInvocationResult>;
}

interface DecisionControlPlane {
  createSession(input: InitialQuestion): Promise<Session>;
  advanceStage(sessionId: string, stage: DecisionStage): Promise<StageRun>;
  storeEvidence(evidence: EvidenceRecord): Promise<void>;
  emitRecommendation(sessionId: string): Promise<DecisionRecommendation>;
}
```

核心意义：

- 模型可以换
- 流程不能乱
- 工作台要知道过程，不只是知道结果

## 3.2 任务线程化，而不是对话堆叠

Paperclip 的工作单位不是“聊天消息”，而是 **issue / run / activity**。

这是很重要的产品启发。

你们如果直接做成普通 chat 窗口，后面一定会遇到问题：

- 阶段边界不清
- 候选方案无法稳定沉淀
- 决策依据难以复盘
- 用户行为难以分析

更好的做法是：

- 一个问题对应一个 `Session`
- 一个阶段对应一个 `StageRun`
- 一个外部参考或开源项目分析对应一个 `ResearchItem`
- 一个候选思路对应一个 `CandidateOption`
- 一个阶段输出对应一个 `Artifact`

也就是说，你们应该是“线程化的阶段式会话”，而不是“连续滚动的无限长聊天”。

## 3.3 运行有状态，过程可恢复

Paperclip 很重视“session resume”。

证据：

- [docs/agents-runtime.md](https://github.com/paperclipai/paperclip/blob/master/docs/agents-runtime.md) 明确说明可恢复 adapter 会保存 session ID，下次 heartbeat 自动复用
- [doc/spec/agent-runs.md](https://github.com/paperclipai/paperclip/blob/master/doc/spec/agent-runs.md) 单独设计了 `agent_runtime_state` 和 `agent_task_sessions`

对你们的意义不是去保存 Claude/Codex 的 session id 本身，而是要保存：

- 当前会话走到第几阶段
- 当前阶段的摘要
- 已有哪些证据
- 当前有哪些候选方案
- 哪些方案被淘汰，为什么
- 用户最后一次修改了什么判断

换句话说：

> 你们要恢复的不是“聊天上下文”，而是“决策上下文”。

## 3.4 治理优先于炫技

Paperclip 一直在强调治理：

- 预算
- 审批
- 审计日志
- 组织边界
- 权限

证据：

- [docs/start/core-concepts.md](https://github.com/paperclipai/paperclip/blob/master/docs/start/core-concepts.md) 里有 `Governance`
- README 直接列出 `Cost Control`、`Ticket System`、`Governance`
- [docs/api/overview.md](https://github.com/paperclipai/paperclip/blob/master/docs/api/overview.md) 要求 mutating request 在 heartbeat 期间携带 `X-Paperclip-Run-Id`

对你们项目的借鉴是：

- 多模型并行决策一定会带来成本、追责和质量问题
- 所以从第一版起就应该记录：
  - 哪个模型参与了哪个阶段
  - 花了多少 token / cost
  - 产出了什么候选方案
  - 最终建议是否被用户采纳

如果这层不做，后续你们根本没法评估：

- 哪个模型在“问题定义”阶段最好用
- 哪个模型在“方案比较”阶段最稳定
- 哪种组合最省钱

---

## 4. Paperclip 的真实通信方式

这一段需要单独强调，因为它直接影响你们的技术路线。

## 4.1 控制面主通信：REST API

Paperclip 控制面主通信是 REST。

证据：

- [docs/api/overview.md](https://github.com/paperclipai/paperclip/blob/master/docs/api/overview.md) 明确写了 “RESTful JSON API”
- 请求头统一使用 `Authorization: Bearer <token>`
- company-scoped endpoint 通过 `:companyId` 进行隔离

这意味着它的控制动作是典型的：

- 查询状态
- 创建任务
- 更新任务
- 记录评论
- 获取 heartbeat run
- 获取日志和事件

这个设计非常适合你们，因为你们的系统也需要大量“结构化读写”，例如：

- 创建调研会话
- 推进阶段
- 写入候选方案
- 记录用户选择
- 查询阶段历史

## 4.2 实时更新主通道：WebSocket，而不是 SSE

这是你们旧版分析里最需要修正的一点。

Paperclip 的主实时更新通道是 **公司级 WebSocket**。

证据：

- [server/src/realtime/live-events-ws.ts](https://github.com/paperclipai/paperclip/blob/master/server/src/realtime/live-events-ws.ts)
- [ui/src/context/LiveUpdatesProvider.tsx](https://github.com/paperclipai/paperclip/blob/master/ui/src/context/LiveUpdatesProvider.tsx)
- [doc/spec/agent-runs.md](https://github.com/paperclipai/paperclip/blob/master/doc/spec/agent-runs.md) 的 “Realtime Status Delivery” 章节明确写了：  
  `Primary transport: websocket channel per company`

主要路径是：

- 浏览器连接 `GET /api/companies/:companyId/events/ws`
- 服务端鉴权通过后订阅公司级 live events
- 前端收到事件后按事件类型去 invalidate 查询缓存或更新界面

事件类型包括：

- `heartbeat.run.queued`
- `heartbeat.run.status`
- `agent.status`
- `activity.logged`

### 结论

如果你们后面做 GUI 工作台，建议：

- 主工作台实时更新优先用 **WebSocket**
- 某些非核心数据可以轮询兜底
- 不要一开始把所有东西都放在 SSE 上

## 4.3 SSE 在 Paperclip 里不是主控制台通道

源码里确实有 `text/event-stream`，但主要出现于 **plugin bridge** 和个别工具链，不是主控制台运行态同步通道。

证据：

- `gh search code "text/event-stream repo:paperclipai/paperclip"`
- `gh search code "new EventSource repo:paperclipai/paperclip"`

所以你们如果借鉴 Paperclip：

- 不要误以为它的 dashboard runtime update 主要依赖 SSE
- 你们可以把 SSE 保留给特定桥接场景
- 主工作台事件同步建议走 WS

## 4.4 Agent 调用与身份：短时 JWT + Run 关联

Paperclip 的 agent 调用身份设计很值得借鉴。

证据：

- [docs/api/authentication.md](https://github.com/paperclipai/paperclip/blob/master/docs/api/authentication.md)
- [docs/api/overview.md](https://github.com/paperclipai/paperclip/blob/master/docs/api/overview.md)

关键点：

- heartbeat 期间，agent 收到短时 JWT，环境变量名是 `PAPERCLIP_API_KEY`
- 所有 mutating request 应带 `X-Paperclip-Run-Id`
- agent 身份和当前 run 是绑定的

这个设计对你们非常有用。

你们未来如果是多模型/多执行器协作，建议也采用类似思路：

- 每个 `StageRun` 都有自己的 `runId`
- 每个模型调用记录都关联 `runId`
- 每次写入候选方案、证据、评论、评分，都能追溯到对应 run

这样后面才能做：

- 审计
- 重放
- 归因
- 成本分析

---

## 5. 对你们最重要的借鉴：把 Paperclip 的 agent 模型映射成多模型决策模型

你们不是要做“公司里有很多 agent”，但你们明确提到：

- 需求决策希望通过多模型来做
- 这部分必须提前考虑进去

那么正确借鉴方式不是组织结构照抄，而是做**角色化的多模型决策控制平面**。

## 5.1 不建议直接照搬 Agent Hierarchy

Paperclip 的层级是：

- CEO
- 下属 agent
- issue 派发
- 审批与治理

你们如果照搬，会出问题：

- 业务语义错位
- 产品显得过度复杂
- 用户会觉得在操作“AI 组织”，而不是在做“需求决策”

## 5.2 建议改造成“阶段角色 + 模型角色”

更适合你们的方式是：

- 每个阶段允许多个模型参与
- 每个模型在该阶段承担不同角色

例如：

### 阶段一：问题定义

- `clarifier`：澄清问题、提问补洞
- `structurer`：结构化为需求简报

### 阶段二：调研与发散

- `researcher`：总结开源项目、提取要点
- `divergent-thinker`：扩展候选方向

### 阶段三：比较与评估

- `critic`：指出问题和风险
- `evaluator`：按统一维度打分
- `benchmark-checker`：与外部方案对照

### 阶段四：决策收敛

- `synthesizer`：归纳共识
- `recommender`：给出建议
- `dissent-recorder`：保留分歧和未确认项

## 5.3 建议采用的多模型协同模式

### 模式 A：主模型 + 审核模型

适合第一版 MVP。

- 一个主模型负责生成阶段结果
- 一个审核模型负责指出缺口、风险、歧义

优点：

- 成本低
- 系统简单
- 容易调试

缺点：

- 多样性有限

### 模式 B：并行生成 + 汇总裁决

适合你们中期版本。

- 多个模型并行给出候选方案
- 聚合器统一汇总
- 再由评估器打分和保留分歧

优点：

- 更贴近你们“多模型决策”目标
- 更容易比较不同模型的偏好和质量

缺点：

- 成本和复杂度上升

### 模式 C：阶段差异化模型路由

这是我更建议的长期方案。

- 澄清问题时用一个擅长结构化的模型
- 发散时用一个更有创造力的模型
- 评估时用一个更稳定保守的模型
- 收敛时用一个更强总结能力的模型

这比“所有阶段都同时并行跑 3 个模型”更务实。

---

## 6. 用户数据采集：必须提前设计，而不是后补

你特别提到后台要收集用户使用数据，包括“问了什么”，还要能提炼数据。这里必须借鉴 Paperclip 的两个点：

1. **本地/控制面先落库**
2. **原始内容上传必须可控、可区分、可授权**

## 6.1 Paperclip 在数据采集上的两个层次

### 层次一：匿名 telemetry

证据：

- README 的 `Telemetry`
- [packages/shared/src/telemetry/config.ts](https://github.com/paperclipai/paperclip/blob/master/packages/shared/src/telemetry/config.ts)
- [packages/shared/src/telemetry/events.ts](https://github.com/paperclipai/paperclip/blob/master/packages/shared/src/telemetry/events.ts)

它的默认行为是：

- 收集匿名使用事件
- 支持 `DO_NOT_TRACK=1`
- 支持 `PAPERCLIP_TELEMETRY_DISABLED=1`
- CI 默认关闭

事件内容偏“维度数据”，例如：

- 安装完成
- 创建项目
- 创建 agent
- 首次 heartbeat

特点：

- 不默认上传原始 prompt
- 不默认上传正文内容
- 偏产品行为指标

### 层次二：带内容的反馈 trace

证据：

- [docs/feedback-voting.md](https://github.com/paperclipai/paperclip/blob/master/docs/feedback-voting.md)
- [server/src/services/feedback-share-client.ts](https://github.com/paperclipai/paperclip/blob/master/server/src/services/feedback-share-client.ts)

这一层会保存：

- 用户的 helpful / needs work 投票
- 原因
- 被投票对象的上下文快照
- trace bundle

但重点是：

- **默认本地存**
- **分享要显式授权**
- **上传和匿名 telemetry 分开**

这个边界非常对。

## 6.2 对你们系统的直接建议：把数据分三层

### 第一层：产品行为 telemetry

建议默认采集，避免原文内容：

- 会话创建次数
- 阶段完成率
- 平均停留时长
- 模型调用次数
- 每阶段 token/cost
- 决策建议是否被采纳

这层用于：

- 运营统计
- 模型成本分析
- 产品漏斗分析

### 第二层：决策过程结构化数据

建议默认本地/后台落库，但在组织内部可控访问：

- 原始问题摘要
- 需求简报
- 调研项目列表
- 候选方案
- 评分结果
- 推荐方案
- 分歧点

这层是你们真正的知识资产。

### 第三层：高敏感原始 trace

包括：

- 用户原始输入全文
- 模型原始输出全文
- 阶段中间推理过程
- 调用日志
- 附件片段

建议：

- 默认仅本地/私有存储
- 上传或共享需要开关与授权
- 企业环境下要支持脱敏和保留策略

## 6.3 数据表建议

建议提前把下面几张表设计进去：

```ts
Session
StageRun
ModelInvocation
Evidence
CandidateOption
DecisionRecommendation
UserAction
FeedbackVote
FeedbackTrace
UsageMetric
```

重点字段建议：

### `ModelInvocation`

```ts
{
  id,
  sessionId,
  stageRunId,
  role,              // clarifier / evaluator / recommender
  provider,
  model,
  inputTokens,
  outputTokens,
  costUsd,
  latencyMs,
  status,
  traceRef
}
```

### `UserAction`

```ts
{
  id,
  sessionId,
  stage,
  actionType,        // edit_summary / choose_option / discard_option / export_report
  payload,
  createdAt
}
```

### `FeedbackVote`

```ts
{
  id,
  sessionId,
  targetType,        // stage_output / recommendation / report
  targetId,
  vote,              // helpful / needs_work
  reason,
  shared,
  createdAt
}
```

## 6.4 决策系统最关键的不是“问了什么”，而是“怎么走到这个结论的”

这是你们数据设计的关键分界线。

光收集“用户问了什么”，价值有限。真正有价值的是：

- 这个问题被归类为什么类型
- 走了哪些阶段
- 看了哪些参考项目
- 哪些候选方案被提出
- 哪些被淘汰
- 用户在哪一步改变了判断
- 最后为什么采纳某个建议

这个“路径数据”比纯聊天记录更有价值。

---

## 7. 对 GUI 工作台的借鉴建议

Paperclip 对你们最有价值的 GUI 不是视觉风格，而是**控制台的信息组织方式**。

## 7.1 建议借鉴的界面原则

### 原则一：不是聊天页，而是工作台

主界面应该长期可见：

- 当前阶段
- 候选方案
- 关键证据
- 当前结论
- 最近操作

### 原则二：摘要层、中间层、原始层分层展示

可以借鉴 Paperclip 的“控制台 + 详情”结构：

- 顶层：当前建议、当前阶段、关键风险
- 中层：候选方案、对比矩阵、调研摘要
- 底层：模型调用记录、日志、trace、原始输出

### 原则三：运行态要可见

如果你们后面做多模型并行阶段执行，用户必须知道：

- 哪些模型在跑
- 哪个阶段正在处理中
- 哪个结果已经返回
- 哪个模型失败了

这就需要：

- 实时状态区
- 阶段进度条
- 模型执行卡片

## 7.2 你们更适合的页面结构

### 页面 1：决策工作台

- 左侧：阶段导航
- 中间：当前阶段交互与产出
- 右侧：证据摘要、候选方案、当前结论

### 页面 2：调研对比页

- 开源项目卡片
- 可借鉴点 / 不建议借鉴点
- 对应落位阶段

### 页面 3：决策结果页

- 推荐方案
- 依据说明
- 风险与待确认项
- 决策路径摘要

### 页面 4：运营后台

- 会话数
- 阶段完成率
- 热门问题类别
- 模型使用成本
- 常见被采纳方案
- 高价值 idea 聚类

---

## 8. 哪些适合借鉴，哪些不适合

## 8.1 强烈建议借鉴

- 控制平面与执行层分离
- 统一模型/agent 适配层
- 会话与运行的状态化管理
- 实时事件通道
- 运行日志与审计链路
- 成本与预算意识
- 本地优先、可追溯的数据沉淀方式
- 反馈投票与 trace bundle 分层设计

## 8.2 有条件借鉴

- 任务线程模型
说明：
  适合借鉴其线程化思路，但你们要把 `issue` 改造成 `session/stage/artifact`

- 审批机制
说明：
  第一版可以简化为“高风险建议确认”或“人工确认点”，不必一上来搞复杂组织审批

- 插件化扩展
说明：
  后续可做，第一版不必重投入

## 8.3 不建议直接照搬

- 零人公司定位
- CEO / org chart 产品叙事
- 心跳调度作为核心业务模型
- 过重的人事化 agent 组织结构

原因很简单：

- 你们的主线是决策支持，不是 AI 公司运营
- 如果把系统心智模型做成“企业管控 agent”，会稀释你们真正的价值主张

---

## 9. 对现有旧版分析的修正意见

你现有的 [paperclip-analysis.md](E:\thinkWhat\research\paperclip-analysis.md) 大方向是对的，但建议修正以下几点：

1. **实时通信主机制不是 SSE 主导**
实际主通道是公司级 WebSocket，SSE 主要用于插件桥接等场景。

2. **不要把“控制平面不执行 agent”写得过绝对**
更准确的说法是：Paperclip 负责触发和编排执行，具体 agent/runtime 由 adapter 承接；本地 CLI adapter 仍然是 Paperclip 在宿主机上拉起执行。

3. **适配器接口示意可以保留，但要标注为概念映射**
旧版里那段 TypeScript 更像“你们系统的可借鉴抽象”，不是 Paperclip 源码原样接口。

4. **你们系统的数据模型不该直接复刻 issue 模型**
正确做法是把它映射成 `Session / StageRun / Evidence / CandidateOption / Recommendation`

---

## 10. 对你们项目的落地建议

## 10.1 第一版架构建议

建议采用：

- 前端：React + Vite + shadcn/ui
- 后端：FastAPI 或 Node.js 均可
- 实时更新：WebSocket
- 数据库：PostgreSQL

如果你们团队更偏 AI/数据能力，我更倾向：

- 后端：FastAPI
- 前端：React

理由：

- 模型编排、数据分析、后续算法探索会更顺手
- GUI 工作台仍然可复用成熟 React 生态

## 10.2 第一版产品能力建议

必须做：

- 结构化问题定义
- 调研材料管理
- 候选方案比较
- 决策建议生成
- 模型调用记录
- 用户操作记录
- 反馈投票

可以后置：

- 自动自治调度
- 组织级审批体系
- 复杂插件平台
- 多租户商业化

## 10.3 第一版通信建议

- 浏览器到后端：REST + WebSocket
- 后端到模型执行器：统一 Invocation API
- 所有阶段执行都挂 `runId`
- 所有变更都记入 `activity/audit`

## 10.4 第一版数据策略建议

- 遥测数据与原始 trace 分开
- 默认记录结构化决策过程
- 原始全文上传必须有明确策略
- 敏感数据默认私有、可脱敏、可审计

---

## 11. 最终结论

Paperclip 对你们的最大价值，不在于它替你们定义了产品，而在于它证明了一件事：

> 复杂 AI 系统如果没有控制台、运行态、日志、审计、反馈和治理，最后一定不可维护。

你们现在要做的是：

- 用 MIDAS 的渐进式 ideation 做“方法论主线”
- 用 AegisFlow 的阶段推进做“流程参考”
- 用 Trellis 的上下文治理做“长期沉淀”
- 用 Paperclip 的控制台、通信和治理做“系统骨架”

如果压缩成一句话：

> 你们应该借鉴 Paperclip 的“控制平面能力”，而不是复制 Paperclip 的“公司叙事模型”。

---

## 12. 参考证据

- README：<https://github.com/paperclipai/paperclip/blob/master/README.md>
- Core Concepts：<https://github.com/paperclipai/paperclip/blob/master/docs/start/core-concepts.md>
- Agent Runtime：<https://github.com/paperclipai/paperclip/blob/master/docs/agents-runtime.md>
- API Overview：<https://github.com/paperclipai/paperclip/blob/master/docs/api/overview.md>
- Authentication：<https://github.com/paperclipai/paperclip/blob/master/docs/api/authentication.md>
- Agent Runs Spec：<https://github.com/paperclipai/paperclip/blob/master/doc/spec/agent-runs.md>
- Live Updates Provider：<https://github.com/paperclipai/paperclip/blob/master/ui/src/context/LiveUpdatesProvider.tsx>
- Live Events WebSocket：<https://github.com/paperclipai/paperclip/blob/master/server/src/realtime/live-events-ws.ts>
- Telemetry Config：<https://github.com/paperclipai/paperclip/blob/master/packages/shared/src/telemetry/config.ts>
- Telemetry Events：<https://github.com/paperclipai/paperclip/blob/master/packages/shared/src/telemetry/events.ts>
- Feedback Voting：<https://github.com/paperclipai/paperclip/blob/master/docs/feedback-voting.md>
- Feedback Share Client：<https://github.com/paperclipai/paperclip/blob/master/server/src/services/feedback-share-client.ts>

