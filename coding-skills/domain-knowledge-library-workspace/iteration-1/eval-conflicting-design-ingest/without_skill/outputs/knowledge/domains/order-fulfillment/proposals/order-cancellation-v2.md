---
type: Design Proposal
title: 订单取消 V2 设计
description: 未来允许 SHIPPED 订单在仓库未出库时通过仓储拦截流程取消。
tags: [order, cancellation, warehouse, shipped]
context: order-fulfillment
view: to-be
owner: pending:order-domain-owner
sensitivity: internal
applies_to:
  systems: [order-service, warehouse-system]
sources:
  - id: cancel-design-v2
    resource: ../../../sources/cancel-design-v2.md
    role: design
  - id: cancel-code-v1
    resource: ../../../sources/order_service.py
    role: implementation-context
generated:
  by: domain-knowledge-library/ingest
  at: 2026-08-19T17:08:00Z
status: proposed
---

# 目标

未来允许已经进入 `SHIPPED` 的订单在仓库未出库时发起取消。该设计已通过技术评审，但尚未实现，不代表当前生产行为。[^cancel-design-v2]

# 拟议流程

1. `SHIPPED` 订单先向仓储系统申请拦截。
2. 仓储确认拦截成功后，订单转为 `CANCELLED`。
3. 拦截失败时，订单保持 `SHIPPED`。[^cancel-design-v2]

# 实施前置条件

- 订单领域 Owner 确认业务规则。
- 仓储团队确认跨系统契约。[^cancel-design-v2]

# 与当前行为的关系

当前 `order-service` 的 `can_cancel` 只接受 `CREATED` 和 `PAID`，因此 `SHIPPED` 取消尚不可用。[^cancel-code-v1] 本页记录 TO-BE 设计，不覆盖 [AS-IS 规则](../rules/order-cancellation.md)，两者差异保留为[待裁决冲突](../conflicts/shipped-order-cancellation.md)。

[^cancel-design-v2]: 《订单取消 V2 设计》，状态为“已通过技术评审，尚未实现”。
[^cancel-code-v1]: `order_service.py` 中 `can_cancel` 的当前实现。
