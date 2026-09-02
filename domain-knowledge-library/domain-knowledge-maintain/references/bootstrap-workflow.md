# bootstrap 冷启动

触发：一组仓库还没有 Bundle，或新仓库要加入已有 Bundle。
输入：仓库路径或 URL、分支、commit、包含/排除路径、CODEOWNERS、已有设计文档。
负责人：知识维护者。

## 阶段

| 阶段 | 做什么 | 产物 | 此时 Agent 能用什么 |
|---|---|---|---|
| 0 基线 | 钉死 SHA、依赖锁、扫描边界、敏感路径、解析器版本；只做静态只读扫描 | `.kb/bootstrap-state.yaml` | 无 |
| 1 盘点 | `kb.py inventory <repo>`：语言、构建根、契约、迁移、测试、CI、容器、CODEOWNERS、入口线索；只记事实、失败、未知 | `.kb/inventory/<repo>.json` | 无 |
| 2 骨架 | Repository / Application / Module 三类 Concept；页面上写入口清单（路径、Topic、主表、开关名）指向真源；候选 C4 Context / Container 描述进 Application 正文 | `systems/<app>/` | 能定位，不能当接口文档 |
| 3 候选领域 | 综合命名聚类、数据所有权、API/消息边界、状态机、Git 共变、团队所有权、测试样例、既有文档，提出 Bounded Context、术语、能力、流程、规则、事件、关系；全部 `draft`，Inferred 逐条标注 | `domains/<ctx>/` | 能用，回答须标未确认 |
| 4 对账 | 仓库内文档的主张分成 support / refine / conflict / to-be / historical / unknown；conflict 写 `.kb/conflicts/` | `.kb/conflicts/` | 冲突可见 |
| 5 发布 | `kb.py validate --check-index` 通过；`kb.py index`；`log.md`；跑黄金问题；登记仓库进 `config.yaml.repositories` | 可消费 Bundle | 双方 Agent 消费 |

## bootstrap-state.yaml

```yaml
repositories:
  - name: order-core
    url: git+https://example/order.git
    rev: abc123def
    default_branch: main
    include: [src/, api/, db/]
    exclude: [src/generated/, "**/testdata/"]
    sensitive: [config/secrets/, "**/*.pem"]
    parsers: { java: tree-sitter-java@0.21 }
    scanned_at: 2026-09-03T10:00:00Z
    inventory: .kb/inventory/order-core.json
phase: 3            # 0-5，中断后从此恢复
```

中断后重跑时读取 `phase`，不重做已完成阶段；SHA 变化则回到阶段 0。

## 阶段 2 骨架写法

Application `overview.md` 必须包含：职责一句话、模块列表、入口清单、真源指针。入口清单示例：

```markdown
## 入口清单（指向真源，不复制正文）
Observed  HTTP 契约：`api/openapi.yaml`（git+…@abc123）
Observed  消息 Topic：`order.created`、`order.shipped`（`src/messaging/Topics.java`）
Observed  主表：`orders`、`order_items`、`shipments`（`db/migrations/`）
Observed  开关：`CANCEL_AFTER_SHIP_LEGACY_B`（`config/features.yaml`）
```

不为每个 Endpoint / 表 / 开关建独立 Concept。这些留给 `domain-knowledge-expand`。

## 阶段 3 候选证据

每个 Bounded Context 至少两类独立证据；只有命名聚类不够。正文按类型模板写，并在"证据"节列出：

```markdown
## 证据
Derived   数据所有权：`orders`、`shipments` 仅被 order-core 写入
Derived   Git 共变：`CancelService` 与 `ShipmentService` 近 12 月共变 31 次
Observed  CODEOWNERS：`src/order/**` → @order-platform
Inferred  "履约"作为 Context 名取自 `docs/design/fulfillment.md`，团队未确认
```

同名术语在不同仓库含义不同时，分别建 Ubiquitous Term，并用 Context Relationship 记录翻译关系；不强制合并。

## 阶段 4 对账分类

| 分类 | 含义 | 去处 |
|---|---|---|
| support | 文档与代码一致 | 作为来源附加到 Concept |
| refine | 文档补充代码未表达的意图 | 合并进 Concept，role: design-intent |
| conflict | 文档与代码矛盾 | `.kb/conflicts/<slug>.md`，Concept 正文写"存在冲突" |
| to-be | 文档描述目标态 | 独立 Concept，`view: to-be` |
| historical | 文档描述已废弃行为 | `view: historical` 或只作来源 |
| unknown | 无法判断 | Concept 正文写 unknown，不猜 |

## 退出标准

不是"完整"，而是四条能力：

1. Coding Agent 能从 `index.md` 走到正确的应用和模块，再回到仓库；
2. Design Agent 不带仓库能说出某 Context 的边界、术语、主要流程和已知规则，并标明哪些是 `draft`；
3. 每条机械事实带 commit 或契约版本；
4. 冲突和 unknown 可见，未标记推断为零。

用两组黄金问题验证（各 5 条起）：设计场景（只给 Bundle）与实现场景（Bundle + 仓库）。问题与期望路径记在 `.kb/golden-questions.md`，供 audit 回归。

## 停止条件

- 扫描范围可能越权或包含敏感材料；
- 不支持的语言超过阈值且没有替代提取器；
- 候选 Context 之间无法给出任何归属证据；
- 用户要求运行仓库内脚本或构建来"看清楚"。

## 明确不做

- 为每个 Endpoint / 字段 / 配置项建 Concept；
- 执行仓库内脚本或构建；
- 把 LLM 推断直接写成 `stable`；
- 等待人工确认后再发布 `draft`。
