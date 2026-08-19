---
type: Business Rule
title: 订单取消状态规则 V2（候选）
description: 候选设计拟在仓库未出库且拦截成功时允许 SHIPPED 订单取消；尚未实现或完成业务确认。
tags: [order, cancellation, warehouse-interception]
context: order-fulfillment
view: to-be
owner: team:order-platform
sensitivity: internal
applies_to:
  systems: [order-service]
sources:
  - id: cancel-design-v2
    resource: ../../../../.kb/sources/cancel-design-v2-d36e5cff.md
    title: 订单取消 V2 设计
    role: design-intent
  - id: cancel-code-v1
    resource: ../../../../.kb/sources/order-service/order_service-f441cddf.py
    title: order_service.py
    role: implementation
generated:
  by: domain-knowledge-library/ingest
  at: 2026-08-19T17:08:00Z
status: draft
stale_after: 2026-11-19
---

# 候选规则

设计目标是未来允许已进入 `SHIPPED`、但仓库尚未出库的订单发起取消。该目标已通过技术评审，但尚未实现，也尚未完成订单领域 Owner 的业务规则确认。[^cancel-design-v2]

# 候选流程

1. `SHIPPED` 订单先向仓储系统申请拦截。[^cancel-design-v2]
2. 仓储确认拦截成功后，订单转为 `CANCELLED`。[^cancel-design-v2]
3. 拦截失败时，订单保持 `SHIPPED`。[^cancel-design-v2]

# AS-IS 对照

当前实现只对 `CREATED` 和 `PAID` 返回可取消，因此 `SHIPPED` 当前不可取消。[^cancel-code-v1] 当前规则见[订单取消状态规则](./order-cancellation.md)。

本页仅记录 TO-BE 设计意图，不代表当前生产行为，也不替代 AS-IS 规则。[^cancel-design-v2]

# 冲突状态

AS-IS 与 TO-BE 对 `SHIPPED` 的取消能力存在有意的时态差异。该差异尚未裁决为已批准业务规则，详见[冲突报告](../../../../.kb/conflicts/order-cancellation-shipped-v2.md)。

# 待确认

- 订单领域 Owner 是否批准该 TO-BE 业务规则及其适用范围。
- “仓库未出库”的权威判定、状态语义和失败/超时处理。
- 仓储团队是否确认拦截请求及结果的跨系统契约。
- 生效版本、上线条件以及 TO-BE 何时可转为 AS-IS。

[^cancel-design-v2]: 《订单取消 V2 设计》第 3-14 行，design-intent 快照，SHA-256 `d36e5cffe43fec25b81c6845b221bc9b900b89a447d438858ad8b2bdfc6cef98`
[^cancel-code-v1]: `can_cancel` 第 11-12 行，implementation 快照，SHA-256 `f441cddfe778ebfa98a0f8a25e2df1b1b313a7d978f5674a7d6bddb7ae65da03`
