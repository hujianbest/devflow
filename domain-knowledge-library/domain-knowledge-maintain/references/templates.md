# 模板

所有 Concept 共用 bundle-contract.md 第 2 节的 frontmatter；下面只给正文骨架和每类必须回答的问题。正文每条声明行首标 `Observed` / `Derived` / `Confirmed` / `Inferred`。

## Bounded Context（`domains/<ctx>/overview.md`）

```markdown
# <名称>

## 边界
Inferred  负责什么、不负责什么。

## 核心术语
- term-a → `glossary/term-a.md` · term-b → `glossary/term-b.md`（正文里用 Markdown 链接）

## 主要流程
- process-x → `processes/process-x.md`

## 上下游
- with-y → `relationships/with-y.md`

## 承载系统
- systems/<app>/overview.md

## 证据
Derived   数据所有权 …
Derived   Git 共变 …
Observed  CODEOWNERS …

## 未知
- …
```

## Ubiquitous Term（`glossary/<term>.md`）

```markdown
# <术语>

## 定义
Confirmed | Inferred  一句话定义。

## 别名与反例
- 别名：…
- 不是：…（其他 Context 中的同名概念见 …）

## 在代码中
Observed  类 / 表 / 枚举：…

## 证据
```

## Business Process（`processes/<process>.md`）

```markdown
# <流程>

## 触发与结束
## 步骤
1. …（涉及系统 / 事件）
## 分支与例外
## 涉及规则
- rule → `../rules/<rule>.md`
## 证据
```

## Business Rule（`rules/<rule>.md`）

```markdown
# <规则>

## 定义
Observed | Confirmed  规则本身。

## 适用范围
- …

## 例外
- …

## 使用前核对
- 当前状态枚举、开关、Topic、生产配置（都回真源查）

## 存在冲突（若有）
- 见 .kb/conflicts/<slug>.md

## 证据
```

## Domain Event（`events/<event>.md`）

```markdown
# <事件>
## 何时发生
## 谁发 / 谁听
## 载荷要点（不复制 schema）
## 证据
```

## Context Relationship（`relationships/<with-x>.md`）

```markdown
# <A> ↔ <B>
## 关系类型
Inferred  上游/下游 · 契约 · 防腐层 · 共享内核 · 分离
## 翻译
- A 的 <term> = B 的 <term'>（差别：…）
## 契约指针
Observed  …
## 证据
```

## Application（`systems/<app>/overview.md`）

```markdown
# <应用>

## 职责
一句话。

## 模块
- module-a → `modules/module-a.md`

## 入口清单（指向真源，不复制正文）
Observed  HTTP 契约：…
Observed  消息 Topic：…
Observed  主表：…
Observed  开关：…

## 构建与部署线索
Observed  构建根 · CI · 容器

## 所属 Context
- domains/<ctx>/overview.md

## 证据
```

## Repository / Module

同 Application，去掉入口清单中不适用的项；Module 增加"对外暴露"与"依赖"两节。

## Architecture Decision（`decisions/<adr>.md`）

```markdown
# ADR: <标题>

- 状态: proposed | accepted | rejected | superseded
- 日期:
- 替代 / 被替代:

## 背景
## 决策
## 备选与放弃原因
## 后果
## 证据
```

## 实现细节类型（仅 expand）

API Endpoint / Event Channel / Data Model / Configuration 的模板在 `domain-knowledge-expand/references/expand-workflow.md`。本技能不生成它们。

## 冲突记录（`.kb/conflicts/<slug>.md`）

```markdown
---
concepts: [domains/<ctx>/rules/<rule>.md]
detected_by: bootstrap | ingest | sync | capture
detected_at: 2026-09-03
status: open | resolved
---

## AS-IS 证据
Observed  …（来源与 rev）

## 意图证据
Observed  …（文档与版本）

## 可能解释
- 漂移 / 兼容路径 / 未完成迁移 / 文档过期

## 裁决（Owner 回填）
- 结论:
- 由:
- 日期:
```

## 提案

见 bundle-contract.md 第 5 节；任务 Agent 侧模板在 `using-domain-knowledge/references/proposal-template.md`。

## config.yaml 与 AGENTS.md

由 `kb.py init` 生成；字段说明见 kb.py 内 `CONFIG_TEMPLATE` 与 `AGENTS_TEMPLATE`。
