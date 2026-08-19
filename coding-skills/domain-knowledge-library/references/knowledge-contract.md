# Knowledge Contract

本文件定义 `domain-knowledge-library` 写入磁盘时必须遵守的目录、类型、元数据和证据契约。

## 1. 标准目录

```text
<kb-root>/
├── knowledge/
│   ├── index.md
│   ├── log.md
│   ├── domains/
│   │   └── <bounded-context>/
│   │       ├── index.md
│   │       ├── overview.md
│   │       ├── glossary/
│   │       ├── capabilities/
│   │       ├── processes/
│   │       ├── rules/
│   │       ├── events/
│   │       └── relationships/
│   ├── systems/
│   │   └── <application>/
│   │       ├── index.md
│   │       ├── overview.md
│   │       ├── modules/
│   │       ├── interfaces/
│   │       ├── events/
│   │       ├── data-models/
│   │       └── configurations/
│   ├── decisions/
│   ├── playbooks/
│   └── references/
└── .kb/
    ├── config.yaml
    ├── source-registry.yaml
    ├── authority-matrix.yaml
    ├── bootstrap-state.yaml
    ├── sources/
    ├── inventory/
    ├── proposals/
    ├── conflicts/
    └── review-queue/
```

`knowledge/` 是 OKF Bundle；`.kb/` 是控制面。检索正式知识时不得把 `.kb/` 当作已发布结论。

## 2. 路径与身份

OKF 使用相对 Bundle 的文件路径（去掉 `.md`）作为 Concept ID。

- 第一次创建时直接选择最终语义路径。
- `draft → stable` 不移动文件。
- 重命名或移动必须保留 deprecated 别名页或明确迁移表。
- 根和子目录导航统一使用小写 `index.md`。
- `index.md` 和 `log.md` 是保留文件，不是普通 Concept。
- 文件名使用稳定、可读的 kebab-case。
- 不把日期放进普通 Concept 文件名；ADR 可保留序号。
- `knowledge/` 内的相对 Markdown 链接必须解析到 Bundle 内部。
- Concept 不得链接 `.kb/`；用 `conflict_id`、`proposal_id` 或 `review_id` 纯文本关联，控制面文件可以单向链接回 Concept。

## 3. 类型 Profile

### 3.1 业务类型

| type | 目录 | 人工确认 |
|---|---|---|
| `Bounded Context` | `domains/<context>/overview.md` | 必须 |
| `Ubiquitous Term` | `domains/<context>/glossary/` | 必须 |
| `Business Capability` | `domains/<context>/capabilities/` | 必须 |
| `Business Process` | `domains/<context>/processes/` | 关键语义必须 |
| `Business Rule` | `domains/<context>/rules/` | 必须 |
| `Domain Event` | `domains/<context>/events/` | 业务含义必须 |
| `Context Relationship` | `domains/<context>/relationships/` | 必须 |

### 3.2 实现类型

| type | 目录 | 默认验证 |
|---|---|---|
| `Repository` | `systems/<application>/` 或 `references/` | 机器 |
| `Application` | `systems/<application>/overview.md` | 职责语义需人工 |
| `Module` | `systems/<application>/modules/` | 机器 |
| `API Endpoint` | `systems/<application>/interfaces/` | 机器 |
| `Event Channel` | `systems/<application>/events/` | 机器 |
| `Data Model` | `systems/<application>/data-models/` | 机器 |
| `Configuration` | `systems/<application>/configurations/` | 机器 |

### 3.3 决策与操作类型

| type | 目录 | 规则 |
|---|---|---|
| `Architecture Decision` | `decisions/` | 只追加或 supersede |
| `Playbook` | `playbooks/` | 操作步骤必须验证 |
| `Reference` | `references/` | 说明来源和适用范围 |

消费者必须容忍未知 `type`，但 Skill 不得在未更新本 Profile 的情况下主动发明新类型。

## 4. OKF Frontmatter

每个 Concept 至少包含：

```yaml
---
type: Application
title: Order Core
description: 负责订单生命周期实现的应用；业务边界仍待领域审核。
generated:
  by: domain-knowledge-library/<model-or-process>
  at: 2026-08-19T16:00:00Z
status: draft
---
```

推荐完整结构：

```yaml
---
type: Business Process
title: 订单取消流程
description: 描述订单取消的触发、校验、状态变化和下游影响。
resource: git+https://example/repo.git@<sha>#<path-or-symbol>
tags: [order, cancellation]

context: order-fulfillment
view: as-is
owner: team:order-platform
sensitivity: internal

applies_to:
  systems: [order-core]
  versions: ["<version-expression>"]
  environments: [production]

sources:
  - id: cancel-service
    resource: git+https://example/repo.git@<sha>#src/CancelService.java
    title: CancelService
    role: implementation
    author: process:git
    last_modified: 2026-08-19

generated:
  by: domain-knowledge-library/<model-or-process>
  at: 2026-08-19T16:00:00Z

verified:
  - by: human:<reviewer-id>
    at: 2026-08-19T17:00:00Z

status: stable
stale_after: 2026-11-19
---
```

### 4.1 标准字段

- `type`：唯一始终必填字段。
- `title`：人类可读标题。
- `description`：一行摘要，用于 index 和检索预览。
- `resource`：Concept 描述的底层资产 URI；抽象概念可省略。
- `tags`：横向分类，不能替代 Context。
- `sources`：Concept 的来源。
- `generated`：当前内容由谁在何时生成。
- `verified`：谁独立核对过当前内容。
- `status`：`draft`、`stable`、`deprecated`。
- `stale_after`：绝对日期，到期后停止默认消费。

### 4.2 团队扩展字段

- `context`：所属 Bounded Context。
- `view`：`as-is`、`to-be`、`historical`。
- `owner`：维护责任。
- `sensitivity`：`public`、`internal`、`restricted`。
- `applies_to`：系统、版本、环境、地区或产品范围。
- `sources[].role`：来源能证明的内容类型。

未知字段应在 round-trip 中保留。

## 5. 来源角色

| role | 能证明什么 | 不能自动证明什么 |
|---|---|---|
| `implementation` | 指定版本当前实现 | 正式业务意图 |
| `test-observation` | 指定条件下的断言或观察 | 所有生产路径 |
| `runtime-observation` | 特定时间、环境和输入的行为 | 永久规则 |
| `contract` | 声明接口或消息契约 | 部署实现完全遵循 |
| `design-intent` | 设计目标和取舍 | 当前已经实现 |
| `business-policy` | 正式制度范围内的规则 | 代码已经遵循 |
| `human-confirmation` | 确认者职责范围内的判断 | 其他 Context 的事实 |
| `historical` | 某一历史时期的信息 | 当前状态 |

来源条目必须有 `resource`。正文引用关键主张时，使用与 `sources[].id` 对应的脚注：

```markdown
订单进入 `SHIPPED` 后不能直接取消。[^cancel-service]

[^cancel-service]: CancelService 在指定 commit 下的实现
```

## 6. 证据等级

在 proposal 和 review 中给每项主张标记：

- `Observed`：直接存在于固定版本来源。
- `Derived`：给定工具、版本和配置可重复得到。
- `Inferred`：模型对一个或多个证据的解释。
- `Confirmed`：有职责的人确认的业务语义。

发布规则：

- `Observed`、`Derived` 技术事实可由独立过程写入 `verified`。
- `Inferred` 保持 draft，正文明确使用“候选”“可能”“待确认”。
- `Confirmed` 记录 `human:` actor、确认时间和范围。
- 同一页面混合 confirmed 与 inferred 时，页面保持 draft，或把未确认内容移入 review queue。

## 7. 生命周期与验证

### 7.1 默认状态

- 新建技术 Concept：`draft`，完成确定性核对后可 `stable`。
- 新建领域 Concept：`draft`。
- 无 `status` 在 OKF 中等价于 stable，但本 Skill 创建的页面必须显式写 status，避免误发布。

### 7.2 语义修改

如果正文含义、适用范围或关键来源发生变化：

1. 保存 Git 历史和 `log.md`。
2. 清除代表旧内容的当前 `verified`。
3. 设置 `status: draft`。
4. 生成 review queue 项。

纯格式、拼写或未改变结论的来源补充不必清除验证，但提案必须解释判断。

### 7.3 废弃和替代

- deprecated 页面保留原路径。
- 正文顶部链接替代 Concept。
- ADR 不改写历史；新 ADR 通过链接 supersede 旧 ADR。
- 删除来源时标记所有派生知识，不能只删除 source registry 条目。

## 8. index 和 log

`index.md` 支持渐进式加载：

```markdown
# 订单履约

- [订单取消流程](processes/order-cancellation.md) - 取消触发、校验和下游影响。
- [订单状态](glossary/order-status.md) - 本 Context 中订单状态的定义。
```

规则：

- index 不列出 `.kb/` 内容。
- 条目描述来自 Concept `description`。
- 默认列出 stable 和 draft，但必须标识 draft；deprecated 放到单独分组。
- 可自动生成，不人工维护第二份分类事实。

根 `log.md` 按日期倒序：

```markdown
# Knowledge Update Log

## 2026-08-19
- **Bootstrap**: 建立 order-core 系统地图。
- **Draft**: 提出订单履约 Bounded Context，等待 owner 审核。
```

## 9. 配置与控制状态

`.kb/config.yaml` 最小结构：

```yaml
schema_version: "1.0"
knowledge_root: knowledge
default_sensitivity: internal
repositories:
  - id: order-core
    path: ../order-core
    include: [src, tests, docs, specs]
    exclude: [vendor, generated, node_modules, dist, build]
policies:
  execute_source_code: false
  publish_inferred_business_semantics: false
```

`.kb/source-registry.yaml` 最小结构：

```yaml
schema_version: "1.0"
sources:
  - id: repo-order-core-abc123
    kind: git-repository
    resource: git+https://example/order-core.git@abc123
    revision: abc123
    role: implementation
    content_hash: null
    sensitivity: internal
    acquired_at: 2026-08-19T16:00:00Z
```

`.kb/bootstrap-state.yaml` 记录阶段和中断原因：

```yaml
schema_version: "1.0"
baseline:
  repositories:
    order-core: abc123
stage: domain-candidates
completed:
  - scope
  - inventory
  - system-map
blocked:
  - id: OQ-001
    reason: 订单履约和订单交易是否为两个 Context 尚未确认
```

## 10. 发布前最低门禁

- Concept YAML 可解析且 `type` 非空。
- `status` 合法。
- `view` 合法。
- source id 唯一，且 source resource 非空。
- `stable` 的业务 Concept 至少有一个 `human:` verifier。
- 关键声明脚注能解析到 `sources[].id`。
- Concept 内部链接不存在意外断链。
- Concept 不存在逃逸 Bundle 或指向 `.kb/` 的相对链接。
- index 与文件一致。
- 不存在循环来源和自我引用。
- `restricted` 内容不进入当前可见仓库。
- 未标记的推断数量为零。
