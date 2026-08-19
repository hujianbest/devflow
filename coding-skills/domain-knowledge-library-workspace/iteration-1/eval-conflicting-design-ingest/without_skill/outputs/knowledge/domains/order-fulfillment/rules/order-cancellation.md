---
type: Business Rule
title: 订单取消状态规则
description: 当前实现仅允许 CREATED 和 PAID 订单取消。
tags: [order, cancellation]
context: order-fulfillment
view: as-is
owner: team:order-platform
sensitivity: internal
applies_to:
  systems: [order-service]
sources:
  - id: cancel-code-v1
    resource: ../../../sources/order_service.py
    role: implementation
generated:
  by: domain-knowledge-library/test-fixture
  at: 2026-08-01T09:00:00Z
verified:
  - by: human:order-owner
    at: 2026-08-01T10:00:00Z
status: stable
stale_after: 2026-12-01
---

# 规则

当前实现只允许 `CREATED` 和 `PAID` 状态的订单取消。[^cancel-code-v1]

# 不适用条件

`SHIPPED` 状态不能由当前实现取消。

# 时态与范围

本页只描述当前代码事实（AS-IS），不否定未来设计。未来方案及其未解决事项见[订单取消 V2 设计](../proposals/order-cancellation-v2.md)和[冲突记录](../conflicts/shipped-order-cancellation.md)。

[^cancel-code-v1]: `order_service.py` 中 `can_cancel` 的当前实现。
