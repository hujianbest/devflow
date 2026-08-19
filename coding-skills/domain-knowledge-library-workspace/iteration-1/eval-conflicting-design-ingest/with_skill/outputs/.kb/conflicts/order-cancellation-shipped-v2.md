---
id: order-cancellation-shipped-v2
status: open
classification: as-is-to-be-divergence
created_at: 2026-08-19T17:08:00Z
source_ids: [cancel-code-v1, cancel-design-v2]
affected_concepts:
  - knowledge/domains/order-fulfillment/rules/order-cancellation
  - knowledge/domains/order-fulfillment/rules/order-cancellation-v2
review_queue: ../review-queue/order-cancellation-v2.md
---

# 冲突报告：SHIPPED 订单取消

## 争议点

在未指定时态时，“`SHIPPED` 订单能否取消”会得到相反答案：

- **AS-IS / implementation**：`can_cancel` 只接受 `CREATED` 和 `PAID`，所以当前实现排除 `SHIPPED`。
- **TO-BE / design-intent**：设计目标是在仓库未出库时允许 `SHIPPED` 订单发起取消，并以仓储拦截成功作为转为 `CANCELLED` 的条件。

两者描述不同 view，因而不是可由“较新来源覆盖较旧来源”解决的同一时态事实冲突；但 TO-BE 是否成为获批业务规则、何时生效均未确认。在这些问题解决前，不能把两者合并成一个无时态限定的规则。

## 各方证据

| 视图 | 主张 | 来源 | 角色 | 位置 | 证据状态 |
|---|---|---|---|---|---|
| AS-IS | 当前仅 `CREATED`、`PAID` 可取消，`SHIPPED` 不可取消 | `cancel-code-v1` | implementation | 第 11-12 行 | Observed |
| TO-BE | 仓库未出库的 `SHIPPED` 订单可发起取消 | `cancel-design-v2` | design-intent | 第 3-5 行 | Observed 的设计意图；非当前实现 |
| TO-BE | 拦截成功后转 `CANCELLED`，失败保持 `SHIPPED` | `cancel-design-v2` | design-intent | 第 7-11 行 | Observed 的设计意图；业务语义待确认 |
| 门禁 | 需要订单领域 Owner 和仓储团队分别确认 | `cancel-design-v2` | design-intent | 第 14 行 | Observed |

## 影响范围

- `order-service` 的取消资格判断。
- `order-fulfillment` 中订单取消业务规则。
- 仓储拦截的跨系统请求、结果、超时与幂等契约。
- 使用“SHIPPED 可否取消”但未指定 AS-IS/TO-BE 的检索与 Agent 决策。

## 缺失证据

- 订单领域 Owner 对候选业务规则及例外的确认。
- 仓储团队对跨系统契约和“未出库”权威状态的确认。
- 目标版本、生效条件、迁移/回滚策略。
- 与设计相符的实现、测试或已部署运行证据。

## 可选处理及后果

1. **确认候选规则**：由相应 Owner 明确批准范围；TO-BE 仍应保持独立，直至实现与生效证据支持转为 AS-IS。
2. **修改后确认**：补充状态语义、失败/超时、幂等和契约范围后再审核；当前 TO-BE 保持 draft。
3. **拒绝或撤回**：保留摄入与审核记录，将 TO-BE Concept 标记 deprecated 或记录为 rejected；AS-IS 不受影响。
4. **需要更多证据**：维持当前双视图和 open 冲突，不向 Agent 提供无时态限定的统一结论。

本报告不选择业务方案。
