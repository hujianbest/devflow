# Bundle 契约

本文件是知识形态的唯一权威。`kb.py validate` 实现的就是这里的规则；SKILL 与 hooks 引用本文件而不复述。

## 1. 目录

```text
<bundle-root>/
├── knowledge/                       # OKF Bundle，可独立发布
│   ├── index.md                     # kb.py index 生成；每条：路径、type、一行摘要、status、view、owner
│   ├── log.md                       # 追加式：## [date] bootstrap|ingest|sync|review|audit|expand | 标题
│   ├── domains/{bounded-context}/
│   │   ├── index.md                 # 生成
│   │   ├── overview.md              # type: Bounded Context
│   │   ├── glossary/                # Ubiquitous Term
│   │   ├── capabilities/            # Business Capability
│   │   ├── processes/               # Business Process
│   │   ├── rules/                   # Business Rule
│   │   ├── events/                  # Domain Event
│   │   └── relationships/           # Context Relationship
│   ├── systems/{application}/
│   │   ├── index.md                 # 生成
│   │   ├── overview.md              # type: Application
│   │   ├── repositories/            # Repository
│   │   ├── modules/                 # Module
│   │   ├── interfaces/              # API Endpoint（仅 expand）
│   │   ├── events/                  # Event Channel（仅 expand）
│   │   ├── data-models/             # Data Model（仅 expand）
│   │   └── configurations/          # Configuration（仅 expand）
│   ├── decisions/                   # Architecture Decision
│   ├── playbooks/                   # Playbook
│   └── references/                  # Reference（含契约只读快照，若启用）
├── .kb/                             # 控制面，通用检索不得当正式结论
│   ├── config.yaml
│   ├── source-registry.yaml         # 来源登记：id、resource、role、hash、registered_at、status
│   ├── bootstrap-state.yaml
│   ├── maintenance.lock             # 维护中；hooks 据此放行对 knowledge/ 的写入
│   ├── sources/                     # 原件或不可变快照
│   ├── inventory/                   # kb.py inventory 输出
│   ├── proposals/                   # ③ capture 与 ④ ingest 的输入
│   ├── conflicts/
│   ├── review-queue/
│   ├── audit/                       # kb.py audit 报告
│   └── .sessions/                   # hooks 会话状态，gitignore
└── AGENTS.md                        # 瘦入口，≤ 50 行，由 kb.py init 生成模板
```

## 2. Concept frontmatter

必填：`type`、`title`、`description`、`context`、`view`、`owner`、`sources`、`status`。

```yaml
---
type: Business Rule
title: 已发货订单取消规则
description: 描述订单发货后的取消限制和例外。      # 一行，进 index
tags: [order, cancellation]
context: order-fulfillment                        # Bounded Context slug；systems/ 下可为 system:<app>
view: as-is                                       # as-is | to-be | historical
owner: team:order-platform
applies_to:
  systems: [order-core]
  versions: [">=3.0"]
sources:
  - id: cancel-service
    resource: git+https://example/repo.git@abc123#src/CancelService.java
    role: implementation
    last_modified: 2026-08-10
generated:
  by: domain-kb-agent/<model>
  at: 2026-08-19T16:00:00Z
verified:
  - by: human:order-domain-owner                  # human:<id> | tool:<name>
    at: 2026-08-19T17:00:00Z
status: stable                                    # draft | stable | deprecated
stale_after: 2026-11-19
superseded_by: rules/order-cancel-v2.md           # deprecated 时建议
expanded_by: domain-knowledge-expand              # 实现细节类型必填
---
```

不使用主观 `confidence`。可信度由 `sources[].role`、`verified`、`stale_after`、`applies_to` 推导。

### 类型

| 层 | type | 何时出现 | stable 条件 |
|---|---|---|---|
| 业务 | Bounded Context, Ubiquitous Term, Business Capability, Business Process, Business Rule, Domain Event, Context Relationship | bootstrap 出 draft | `verified[].by` 至少一条 `human:` |
| 实现骨架 | Repository, Application, Module | bootstrap 必出 | `verified` 非空，`tool:` 即可 |
| 实现细节 | API Endpoint, Event Channel, Data Model, Configuration | 仅 expand；必须带 `expanded_by` | `verified` 非空，`tool:` 即可 |
| 决策与操作 | Architecture Decision, Playbook, Reference | ingest 时 | Architecture Decision 需 `human:`；其余 `tool:` 即可 |

### 来源角色

`implementation`、`test-observation`、`runtime-observation`、`contract`、`design-intent`、`business-policy`、`human-confirmation`、`historical`。

### 声明标注

正文每条声明属于且只属于一类，用行首标记：

```text
Observed    源文件中直接存在的事实
Derived     由确定性工具可重复推导的关系
Confirmed   领域人员确认的语义
Inferred    LLM 基于证据提出的解释（必须显式标注）
```

`generated` 存在且 `verified` 为空时，`status` 只能是 `draft`。

## 3. 生命周期

```text
draft → stable → deprecated
```

- 新生成的业务语义默认 `draft`，校验通过即进 Bundle，立刻可检索；
- 首次创建即进最终路径；晋级不移动文件；
- 语义变化清除 `verified`，回 `draft`；
- `deprecated` 保留路径并用 `superseded_by` 链接替代项；不参与默认回答；
- Architecture Decision 的正文状态 `proposed / accepted / rejected / superseded`，旧 ADR 不覆盖。

## 4. 权威矩阵

| 问的是 | 先信谁 | Bundle 里放什么 |
|---|---|---|
| 指定版本代码如何执行 | 代码、测试、静态分析、运行观察 | 指针 |
| HTTP / 消息契约 | 唯一的 OpenAPI / AsyncAPI / Schema Registry | 指针；可选只读快照进 `references/` |
| 当前数据结构 | 实际 Schema、迁移、ORM | 指针 |
| 业务规则 | 业务制度、领域 Owner、已确认知识 | 编译 |
| 为什么这样设计 | ADR、评审记录、设计文档 | 编译 |
| 当前生产配置 | 配置中心或运行系统 | 不放 |
| 系统归属 | Catalog、CODEOWNERS、团队确认 | 编译 |
| 目标架构 | 已批准的 TO-BE 与 ADR | 编译，`view: to-be` |

代码与文档冲突时不自动选边：代码说明 AS-IS，文档说明意图，进 `.kb/conflicts/` 等 Owner 判断。

## 5. 提案（`.kb/proposals/`）

文件名 `<YYYY-MM-DD>-<slug>.md`。

```yaml
---
kind: conflict                   # conflict | refine | new | route-error | stale
concepts: [domains/order-fulfillment/rules/shipped-order-cancel.md]
context: order-fulfillment
task: <任务标识或一句话>
sources:
  - resource: git+https://example/repo.git@def456#src/CancelService.java
    role: implementation
submitted_by: agent:<model>
submitted_at: 2026-09-03T10:00:00Z
---

## 发现
Observed  ...
Inferred  ...

## 建议
...
```

规则：不含试错过程与临时变量；会话本身不能当来源；`route-error` 与 `stale` 由 `kb.py proposals --queue` 同时登记进 `review-queue/`。

## 6. 门禁

`kb.py validate` 检查的确定性门禁：

- 结构：frontmatter 可解析；必填字段齐全；`type` / `status` / `view` / `sources[].role` 取值合法；文件名 kebab-case；相对链接可解析；`superseded_by` 无环；
- 来源：`sources` 非空；`git+` 资源带 `@<rev>`；
- 语义：`stable` 满足类型对应的 `verified` 条件；`generated` 且无 `verified` 时不为 `stable`；实现细节类型带 `expanded_by`；`deprecated` 无 `superseded_by` 给警告；
- 时效：`stale_after` 已过给警告，audit 中计数；
- 索引：`--check-index` 时 `index.md` 与目录一致。

需要人判断、脚本不做的：未标记 Inferred、AS-IS/TO-BE 混写、同名术语强制合并、冲突静默覆盖、敏感材料进发布层。这些由 review 循环和 `domain-knowledge-reviewer` 承担。

## 7. 必须停下等人的场景

- 晋级业务术语、规则、Bounded Context 为 `stable`；
- 裁决同等级来源冲突；
- 覆盖人工确认过的知识；
- 把安全、资金、权限、发布规则的 `draft` 写成可执行策略；
- AS-IS 与 TO-BE 无法区分却要合并回答；
- 扫描范围可能越权；
- 未请求 expand 却要批量建 Endpoint / 配置页。
