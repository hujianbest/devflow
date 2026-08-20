---
type: Business Rule
id: BR-ORDER-CANCEL-001
title: 订单取消规则
description: 当前规则只说明 CREATED 和 PAID 订单可以取消。
tags: [order, cancellation]
context: order-fulfillment
view: as-is
owner: team:order-platform
sensitivity: internal
applies_to:
  systems: [order-service]
sources:
  - id: cancel-implementation-v1
    resource: urn:fixture:refine-ingest:cancel-implementation-v1
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

`CREATED` 和 `PAID` 状态的订单可以取消。[^cancel-implementation-v1]

[^cancel-implementation-v1]: 固定版本实现仅按订单状态判断是否可取消。
