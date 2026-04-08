# 项目进度文件

**最后更新**：2026-04-08  
**用途**：作为本项目的跨会话续接锚点。后续任何新窗口或新会话，优先阅读本文件，再决定继续推进哪一部分。

---

## 1. 项目当前定位

本项目当前要做的是：

**一个面向内部需求梳理、调研分析与产品意图理解场景的，分阶段推进的 AI 决策支持工作台。**

当前不是做：

- 通用聊天机器人
- AI 自治公司平台
- 以代码生成为主的 AI 编码框架

---

## 2. 当前主线

已经确认的产品主线是：

```text
需求梳理 -> 调研分析 -> 方案比较 -> 决策建议
```

第一版主输出：

- `决策建议`

第一版支撑输出：

- `需求简报`
- `调研结论`

方法论支撑：

- MIDAS 的渐进式 ideation

借鉴方向：

- AegisFlow：阶段推进与结构化产物
- Trellis：上下文治理与长期沉淀
- Paperclip：控制台、治理、通信与可追踪性

---

## 3. 当前已确认的重要决策

### 3.1 产品方向

- 第一阶段面向内部使用
- 核心用户先是开发自己，后续扩展到产品经理、项目经理等角色
- GUI 优先，不走纯 CLI
- 需要后台，但后台第一版只做最基础观察与沉淀，不做重型平台

### 3.2 架构方向

已确认推荐架构：

**阶段式编排 + 角色化多模型 + 汇总裁决 + GUI 工作台**

关键原则：

- 阶段间串行
- 阶段内按需局部并行
- 控制平面与执行层分离
- 多模型承担不同角色，而不是无差别并行输出

### 3.3 UI 方向

已确认第一版 GUI 母版页：

- 中文三栏控制台工作台
- 左侧：阶段导航
- 中间：当前阶段工作区
- 右侧：证据、建议、风险、待确认项

该母版页已经可以作为后续页面的设计基线。

---

## 4. 当前已完成资料

### 根目录资料

- [原始需求文档-决策支持系统.md](E:\thinkWhat\原始需求文档-决策支持系统.md)
- [AegisFlow项目分析报告.md](E:\thinkWhat\AegisFlow项目分析报告.md)
- [Trellis项目分析报告.md](E:\thinkWhat\Trellis项目分析报告.md)

### `research/` 资料

- [多模型决策架构草图.md](E:\thinkWhat\research\多模型决策架构草图.md)
- [MVP模块清单与页面信息架构.md](E:\thinkWhat\research\MVP模块清单与页面信息架构.md)
- [GUI工作台设计基线与页面拆解.md](E:\thinkWhat\research\GUI工作台设计基线与页面拆解.md)
- [前端组件树与页面区块层级草案.md](E:\thinkWhat\research\前端组件树与页面区块层级草案.md)
- [后端接口清单与数据表草案.md](E:\thinkWhat\research\后端接口清单与数据表草案.md)
- [P0接口裁剪与实现拆分建议.md](E:\thinkWhat\research\P0接口裁剪与实现拆分建议.md)
- [数据库ER关系与建表草案.md](E:\thinkWhat\research\数据库ER关系与建表草案.md)
- [FastAPI+PostgreSQL后端脚手架设计文档.md](E:\thinkWhat\research\FastAPI+PostgreSQL后端脚手架设计文档.md)
- [FastAPI后端脚手架实施计划.md](E:\thinkWhat\research\FastAPI后端脚手架实施计划.md)
- [paperclip-analysis.md](E:\thinkWhat\research\paperclip-analysis.md)
- [Paperclip项目分析报告-深度版.md](E:\thinkWhat\research\Paperclip项目分析报告-深度版.md)

### `research/UI/` 资料

- [decision-workspace-baseline-v1.png](E:\thinkWhat\research\UI\decision-workspace-baseline-v1.png)
- [ui-design-naming-and-prompts.md](E:\thinkWhat\research\UI\ui-design-naming-and-prompts.md)

---

## 5. 当前 UI 状态

### 5.1 已完成页面设计

以下页面设计图已经产出并确认方向正确：

- 决策工作台母版页
- 首页
- 调研页
- 结果页
- 分析页

### 5.2 UI 状态判断

当前 UI 已经足够作为第一版设计基线，不建议继续在风格层反复打磨。

与 UI 对齐的第一版后端草案也已经补齐，包括：

- 接口清单
- 数据表草案
- 页面与接口/数据映射
- P0 接口裁剪
- 页面字段清单
- 后端模块拆分建议
- 数据库 ER 与建表 SQL 草案
- FastAPI + PostgreSQL 后端脚手架设计文档
- FastAPI 后端脚手架实施计划

说明：

- 当前已经从“设计收敛”切到“前后端契约固化”
- 后续不应再回到纯视觉反复打磨

---

## 6. 埋点与数据采集状态

已经确认：

- 第一版必须保留最小埋点能力
- 埋点优先采结构化关键动作，而不是一开始采集大量原文

已经定义的最小埋点范围包括：

- 会话级事件
- 阶段级事件
- 候选方案事件
- 决策事件
- 模型调用事件

当前状态：

- 已经有原则和事件范围
- 已在接口与数据表草案中预留 `UserAction / UsageMetric / ModelInvocation / trace_ref`
- **尚未展开成正式的数据采集方案**

说明：

- 用户采集方案被明确后置
- 但接口和数据表阶段必须预留字段与表结构口子

---

## 7. 当前下一步

当前已经完成：

1. 设计体系固化
2. 后端接口清单
3. 核心数据表草案
4. 页面与接口/数据表映射
5. P0 接口裁剪
6. 页面字段清单
7. 后端模块拆分建议
8. 数据库 ER 与建表 SQL 草案
9. FastAPI + PostgreSQL 技术栈设计文档
10. FastAPI 后端脚手架实施计划

当前应立即进入的阶段：

**后端代码骨架落地阶段**

建议下一步顺序为：

### 第一步：落后端工程骨架

- 建 `backend/` 目录
- 建 `pyproject.toml`、`.env.example`、`src/app`、`src/core`
- 接 FastAPI 启动与 PostgreSQL 配置

### 第二步：代码骨架搭建

- 建 Alembic 与首批 migration
- 落 `sessions` 与 `stage_runs`
- 打通 `sessions + workspace + stages`

### 第三步：页面联调准备

- 把聚合接口返回结构固定下来
- 明确首页、工作台、调研页、结果页的联调顺序
- 再接 `activities`

---

## 8. 当前待确认项

以下问题还没有最终定：

- FastAPI 是否直接作为最终实现栈，还是先继续保留 Node 备选
- 分析页第一版是否要上真实图表还是先静态指标
- 调研页是否需要第一版就支持自动抓取外部网页
- 是否需要在第一版加入团队协作评论能力

---

## 9. 后续会话建议阅读顺序

如果后续开启新窗口，建议按以下顺序补上下文：

1. 先读本文件：[PROJECT_PROGRESS.md](E:\thinkWhat\PROJECT_PROGRESS.md)
2. 再读架构草图：[多模型决策架构草图.md](E:\thinkWhat\research\多模型决策架构草图.md)
3. 再读 UI 基线：[GUI工作台设计基线与页面拆解.md](E:\thinkWhat\research\GUI工作台设计基线与页面拆解.md)
4. 再读后端草案：[后端接口清单与数据表草案.md](E:\thinkWhat\research\后端接口清单与数据表草案.md)
5. 再读 P0 收敛：[P0接口裁剪与实现拆分建议.md](E:\thinkWhat\research\P0接口裁剪与实现拆分建议.md)
6. 再读数据库草案：[数据库ER关系与建表草案.md](E:\thinkWhat\research\数据库ER关系与建表草案.md)
7. 再读技术设计：[FastAPI+PostgreSQL后端脚手架设计文档.md](E:\thinkWhat\research\FastAPI+PostgreSQL后端脚手架设计文档.md)
8. 再读实施计划：[FastAPI后端脚手架实施计划.md](E:\thinkWhat\research\FastAPI后端脚手架实施计划.md)
9. 如需开发拆分，再读组件树：[前端组件树与页面区块层级草案.md](E:\thinkWhat\research\前端组件树与页面区块层级草案.md)

---

## 10. 当前一句话状态

> 产品方向、架构主线、第一版 UI 基线、P0 接口范围、数据库草案和 FastAPI 实施计划已经收敛完成，项目下一步应进入“后端代码骨架落地阶段”。
