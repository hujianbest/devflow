---
type: Knowledge Conflict
title: SHIPPED 订单取消能力冲突
description: 当前实现禁止 SHIPPED 取消，未来设计要求在仓储拦截成功后支持取消。
tags: [order, cancellation, conflict, shipped]
context: order-fulfillment
view: conflict
owner: pending:order-domain-owner
sensitivity: internal
applies_to:
  systems: [order-service, warehouse-system]
sources:
  - id: cancel-code-v1
    resource: ../../../sources/order_service.py
    role: implementation
  - id: cancel-design-v2
    resource: ../../../sources/cancel-design-v2.md
    role: design
generated:
  by: domain-knowledge-library/ingest
  at: 2026-08-19T17:08:00Z
status: unresolved
---

# 冲突陈述

| 视图 | 有效性 | 关于 `SHIPPED` 取消的陈述 |
| --- | --- | --- |
| AS-IS | 当前代码事实 | `can_cancel` 只允许 `CREATED` 和 `PAID`，因此 `SHIPPED` 不能取消。[^cancel-code-v1] |
| TO-BE | 已通过技术评审、尚未实现 | 仓库未出库时，`SHIPPED` 订单可先申请仓储拦截；仅在拦截成功后转为 `CANCELLED`。[^cancel-design-v2] |

两项陈述属于不同时态，但对“`SHIPPED` 是否可取消”给出不同答案。摄入时不把设计提升为当前规则，也不因当前代码而丢弃未来设计。

# 待裁决事项

1. 订单领域 Owner 是否确认 `SHIPPED` 订单取消的业务规则及适用边界。
2. 仓储团队是否确认拦截请求、成功/失败语义、超时及幂等性等跨系统契约。
3. 实施、发布和验证完成后，何时将 TO-BE 转为 AS-IS，并更新或替代当前规则。

# 当前处理

- [AS-IS 规则](../rules/order-cancellation.md)继续作为当前生产行为的知识。
- [TO-BE 设计](../proposals/order-cancellation-v2.md)独立保存为拟议状态。
- 本冲突保持 `unresolved`；未代替业务 Owner 或仓储团队作出决策。

[^cancel-code-v1]: `order_service.py` 中 `can_cancel` 的当前实现。
[^cancel-design-v2]: 《订单取消 V2 设计》，状态为“已通过技术评审，尚未实现”。
