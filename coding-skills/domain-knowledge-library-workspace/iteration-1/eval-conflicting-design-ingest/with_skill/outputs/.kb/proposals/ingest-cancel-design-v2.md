---
id: ingest-cancel-design-v2
mode: ingest
status: awaiting-review
change_set: cancel-design-v2-d36e5cff
created_at: 2026-08-19T17:08:00Z
source_ids: [cancel-design-v2, cancel-code-v1]
affected_concepts:
  - knowledge/domains/order-fulfillment/rules/order-cancellation
  - knowledge/domains/order-fulfillment/rules/order-cancellation-v2
---

# 摄入提案：订单取消 V2 设计

## 分类与动作

| 材料声明 | 分类 | 处理 |
|---|---|---|
| 未来允许仓库未出库的 `SHIPPED` 订单发起取消 | `new` + `conflict` | 新建独立的 draft / TO-BE Concept；不覆盖 AS-IS |
| 先申请仓储拦截，成功后转 `CANCELLED` | `new` | 写入 TO-BE 候选流程，等待业务与契约确认 |
| 拦截失败时保持 `SHIPPED` | `new` | 写入 TO-BE 候选不变量，等待确认 |
| 本设计不代表当前生产行为 | `support` | 用于明确 view 和适用时态 |
| 当前实现不允许 `SHIPPED` 取消 | `support` | 保留既有 stable / AS-IS 结论；固定实现快照 |

## 声明与证据

| ID | 声明 | 证据等级 | 来源及位置 |
|---|---|---|---|
| C-01 | 设计文档的目标是未来允许仓库未出库的 `SHIPPED` 订单发起取消 | Observed | `cancel-design-v2` 第 3-5 行 |
| C-02 | 候选流程先申请仓储拦截，成功后转 `CANCELLED`，失败则保持 `SHIPPED` | Observed | `cancel-design-v2` 第 7-11 行 |
| C-03 | 该设计尚未实现，不代表当前生产行为 | Observed | `cancel-design-v2` 第 3、12 行 |
| C-04 | 设计要求订单领域 Owner 确认业务规则，并要求仓储团队确认跨系统契约 | Observed | `cancel-design-v2` 第 14 行 |
| C-05 | 当前 `can_cancel` 仅接受 `CREATED` 和 `PAID`，因而排除 `SHIPPED` | Observed | `cancel-code-v1` 第 11-12 行 |
| C-06 | C-01 与 C-05 是 TO-BE 和 AS-IS 间的未决时态偏差，不应互相覆盖 | Derived | C-01、C-03、C-05 及两来源角色 |

没有把任何声明标记为 Confirmed；也没有从材料推断上线时间、仓储契约字段或“未出库”的权威判定。

## 验证影响

- 既有 `order-cancellation.md` 的 AS-IS 含义、适用范围和关键证据内容未改变，保留其既有 `verified` 和 `stable` 状态。
- 新建 `order-cancellation-v2.md` 是未完成人工门禁的领域规则，保持 `status: draft`，不设置 `verified`。
- 若未来将 TO-BE 转为 AS-IS，必须重新核对实现、清除不再适用的旧验证并执行原子发布。

## 原子变更范围

- 登记并保留设计与实现的不可变来源快照。
- 新增 TO-BE draft Concept。
- 更新 order-fulfillment index 和根 log。
- 新增冲突报告及 review queue，不修改 AS-IS 业务结论。
