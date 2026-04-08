# Trellis 项目分析报告

## 项目概览

**定位**：多平台 AI 编码框架（Agent Harness）  
**核心理念**：为 AI 编码助手提供结构化脚手架，让 AI 能力像藤蔓一样沿着规范路径生长  
**开源协议**：AGPL-3.0  
**当前版本**：0.4.0-beta.8  
**Star 数**：4,785（活跃度高）  
**Fork 数**：253  
**仓库地址**：https://github.com/mindfold-ai/Trellis  
**官方文档**：https://docs.trytrellis.app/

### 支持的平台（13 个）

Claude Code, Cursor, OpenCode, iFlow, Codex, Kilo, Kiro, Gemini CLI, Antigravity, Windsurf, Qoder, CodeBuddy, GitHub Copilot

---

## 核心架构

### 1. 目录结构

```
.trellis/
├── spec/              # 规范定义（编码标准、架构约定）
├── tasks/             # 任务管理（PRD、实现上下文、评审）
├── workspace/         # 开发者工作空间（会话日志、上下文）
├── scripts/           # 自动化脚本（Python + Shell）
├── config.yaml        # 项目级配置
└── workflow.md        # 工作流文档
```

### 2. 四大核心组件

#### Specs（规范层）
- 自动注入到 AI 会话中的编码约定
- 按包（package）和层级（layer）组织
- 包含 Pre-Development Checklist
- 团队共享，版本控制

#### Tasks（任务层）
- 结构化工作单元
- 包含 PRD、实现上下文、评审反馈
- 支持生命周期钩子（create/start/archive）
- 可与 Linear 等工具集成

#### Workspace（工作空间）
- 每个开发者独立的会话日志
- 记录历史上下文，实现会话连续性
- 支持多开发者协作（人类 + AI Agent）
- Journal 文件自动轮转（默认 2000 行）

#### Hooks（钩子系统）
- 任务生命周期自动化
- 支持外部工具集成（如 Linear 同步）
- 失败不阻塞主流程

### 3. 技术栈

**CLI 实现**：
- 语言：TypeScript + Python
- 构建：pnpm workspace（monorepo）
- 依赖：
  - commander（CLI 框架）
  - inquirer（交互式提示）
  - chalk（终端样式）
  - figlet（ASCII 艺术）
  - giget（模板下载）

**测试与质量**：
- vitest（单元测试）
- eslint + prettier（代码规范）
- basedpyright（Python 类型检查）
- husky + lint-staged（Git hooks）

**运行环境**：Node.js >= 18.17.0

---

## 核心能力

### 1. 自动注入系统
- 根据任务类型自动加载相关 spec
- 避免重复解释项目约定
- "写一次，永久应用"

### 2. 并行 Agent 执行
- 基于 git worktree 实现工作空间隔离
- 多个 AI 任务并行执行
- 避免单分支拥堵

### 3. 项目记忆
- 会话日志持久化
- 新会话自动加载历史上下文
- 支持跨会话连续性

### 4. 团队协作
- Spec 存储在仓库中
- 一人总结的经验全团队受益
- 支持多开发者身份管理

### 5. 多平台统一
- 一套 Trellis 结构适配 13 个平台
- 避免为每个工具重建工作流

---

## 工作流程

### 初始化
```bash
npm install -g @mindfoldhq/trellis@latest
trellis init -u your-name
trellis init --cursor --opencode --codex -u your-name
```

### 核心命令
- `trellis init` - 初始化项目
- `trellis update` - 更新配置
- `trellis task` - 任务管理
- `tl` - 简写别名

### 开发流程
1. 初始化开发者身份（首次）
2. 获取当前上下文（`get_context.py`）
3. 阅读相关 spec（强制要求）
4. 执行开发任务
5. 记录会话日志
6. 更新任务状态

---

## 设计哲学

### 核心原则
1. **Read Before Write** - 先理解上下文再动手
2. **Follow Standards** - 必须先读 spec 再写代码
3. **Incremental Development** - 一次完成一个任务
4. **Record Promptly** - 立即更新跟踪文件
5. **Document Limits** - Journal 最多 2000 行

### 架构隐喻
> "AI capabilities grow like ivy — Trellis provides the structure to guide them along a disciplined path"

AI 能力像藤蔓一样有机生长，但需要方向引导。Trellis 提供结构化脚手架，让 AI 沿着既定规范路径发展。

---

## 适用场景

1. **多人协作项目** - 统一编码标准和工作流
2. **长期维护项目** - 保留历史上下文和决策记录
3. **复杂架构项目** - 需要严格规范约束
4. **多 AI 工具切换** - 统一工作流，降低切换成本
5. **企业级开发** - 需要可追溯、可审计的开发过程

---

## 技术亮点

### 1. Monorepo 架构
- pnpm workspace 管理
- 支持多包（CLI + docs-site）
- 子模块支持

### 2. 多语言混合
- TypeScript（CLI 核心）
- Python（脚本和工具）
- Shell（自动化任务）

### 3. 生命周期管理
- 任务钩子系统
- 自动化集成（Linear 同步）
- 失败容错设计

### 4. 配置灵活性
- YAML 配置文件
- 可选覆盖默认值
- 支持 monorepo 和单仓库

### 5. 版本管理
- 语义化版本
- 支持 beta/rc 预发布
- 自动化发布流程

---

## 潜在问题与风险

### 1. 学习曲线
- 需要理解 spec/task/workspace 概念
- 强制阅读规范可能降低初期效率
- 多个脚本和配置文件

### 2. 维护成本
- Spec 需要持续更新
- Journal 文件可能快速增长
- 多平台适配的维护负担

### 3. 依赖风险
- 依赖 git worktree（需要 Git 知识）
- Python + Node.js 双环境依赖
- 外部工具集成可能失效

### 4. 性能考虑
- 大量 spec 注入可能影响 token 消耗
- Journal 文件读取开销
- 并行 worktree 的磁盘占用

---

## 竞争对手对比

| 特性 | Trellis | .cursorrules | CLAUDE.md | Skills |
|------|---------|--------------|-----------|--------|
| 规范注入 | ✅ 自动 | ✅ 手动 | ✅ 手动 | ❌ |
| 任务管理 | ✅ | ❌ | ❌ | ❌ |
| 会话记忆 | ✅ | ❌ | ❌ | ❌ |
| 并行执行 | ✅ | ❌ | ❌ | ❌ |
| 多平台 | ✅ 13个 | ❌ Cursor | ❌ Claude | ✅ 部分 |
| 团队协作 | ✅ | ⚠️ 有限 | ⚠️ 有限 | ❌ |

---

## 配置示例

### config.yaml
```yaml
# 会话记录配置
session_commit_message: "chore: record journal"
max_journal_lines: 2000

# Monorepo 包配置
packages:
  cli:
    path: packages/cli
  docs-site:
    path: docs-site
    type: submodule

default_package: cli

# 任务生命周期钩子
hooks:
  after_create:
    - "python3 .trellis/scripts/hooks/linear_sync.py create"
  after_start:
    - "python3 .trellis/scripts/hooks/linear_sync.py start"
  after_archive:
    - "python3 .trellis/scripts/hooks/linear_sync.py archive"

# 更新跳过路径
update:
  skip:
    - .claude/commands/
    - .agents/skills/
    - .cursor/
```

---

## 总结

Trellis 是一个**野心勃勃的 AI 编码框架**，试图解决 AI 辅助开发中的核心痛点：

### 优势
- 系统化的规范管理
- 强大的上下文持久化
- 多平台统一体验
- 团队协作友好

### 挑战
- 概念复杂度较高
- 需要团队纪律配合
- 维护成本不低

### 适合人群
- 需要严格工程规范的团队
- 长期维护的复杂项目
- 频繁切换 AI 工具的开发者
- 重视可追溯性的企业

### 不适合
- 快速原型开发
- 个人小项目
- 不愿意遵守规范的团队

### 核心价值
**将隐性知识显性化、将临时约定持久化、将个人经验团队化**。

---

*分析时间：2026-04-07*  
*分析者：Claude (Opus 4.6)*
