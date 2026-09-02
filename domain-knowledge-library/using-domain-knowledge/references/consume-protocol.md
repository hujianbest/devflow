# consume 协议

## 四层披露与代价

| 层 | 读什么 | 大致代价 | 进入条件 |
|---|---|---|---|
| 1 | 根 `index.md`：路径、type、一行摘要、status、view、owner | 数十至一百 token / 条 | 每个任务 |
| 2 | 领域 `index.md`、`overview.md`；系统 `overview.md` | 数百 token / 页 | 确定候选 Context 后 |
| 3 | 少量 Concept 正文；必要时沿 Context Relationship 扩一跳 | 数百至千 token / 页 | 判断相关后 |
| 4 | 原文：代码、契约、ADR、制度 | 按文件计 | 高风险、冲突、或 Concept 不够用 |

不要一上来 grep 整个 `knowledge/`；先用 index 的 type 与 tags 缩范围。index 命中多个 Context 且无法区分时，读各自 `overview.md` 的"边界"节，仍分不清则在回答里列出候选并说明。

## 两条路径

### Design Agent（可不持有代码仓）

1. 从任务里抽术语，对照根 index 的 description 与 glossary 定位 Context；
2. 读该 Context 的 `overview.md`；
3. 按需读 glossary / processes / rules / relationships；
4. 按 `view` 分开：现状用 `as-is`，目标设计用 `to-be`；两者都要引用时分开写；
5. 需要源码级细节（字段类型、状态枚举值、具体接口形状）时停止：说明缺少代码仓，或建议转 Coding Agent，或指出 `references/` 里是否有契约快照及其版本。

不得把 `systems/` 骨架页写成源码级事实；骨架只告诉你东西在哪。

### Coding Agent（持有代码仓）

1. 同上定位 Context；
2. 读领域 index 与对应系统 `overview.md`、相关 `modules/`；
3. 用骨架页入口清单里的精确名字（API 路径、Topic、表名、开关、符号）回仓库 grep；
4. 读契约原文（OpenAPI / AsyncAPI / schema），不用 Bundle 复述的版本；
5. 高风险结论（资金、权限、发布、不可逆数据变更）回原始证据核对，不只看 Concept。

没装 `domain-knowledge-expand` 时，Bundle 里没有 Endpoint / Data Model 页；不要找，直接回仓库。

## 状态与标注

| 读到 | 处理 |
|---|---|
| `status: draft` | 可用；回答里写"未确认"并给路径 |
| `status: stable` | 直接用；与 draft 同时存在时以 stable 为准 |
| `status: deprecated` | 不参与默认回答；只在被问历史时引用，并指向 `superseded_by` |
| `view: to-be` | 明确标"目标态"，不与现状混写 |
| `view: historical` | 只作背景 |
| 过 `stale_after` | 先说明已过期，再回真源核对 |
| 正文"存在冲突" | 先说明冲突，引用 `.kb/conflicts/`，不选边 |
| 来源已删除 / tombstoned | 视为证据不足 |
| tags 命中 security / payment / permission / release 且 `draft` | 只能当候选；不写成可执行策略、不落代码、不改配置 |

## 拒答格式

```text
无法基于领域知识回答：<原因：冲突 | 过期 | 证据不足 | 需源码级细节>
相关 Concept: <路径>
建议: 回真源 <文件/契约> | 找 owner <id> | 转 Coding Agent
```

## 引用格式

正文里引用 Concept 时给相对路径与状态：

```text
已发货订单原则上不可取消（knowledge/domains/order-fulfillment/rules/shipped-order-cancel.md，stable）。
历史业务身份 B 存在兼容路径（同上，draft，未确认）。
```
