---
type: Business Rule
id: BR-ORDER-CANCEL-006
review_id: REV-ORDER-CANCEL-006
title: 订单发货后取消规则
description: SHIPPED 状态的普通实物订单不可取消。
tags: [order, cancellation, shipped]
context: order-fulfillment
view: as-is
owner: human:order-domain-owner
sensitivity: internal
applies_to:
  systems: [order-service]
  environments: [production]
  products: [physical-order]
sources:
  - id: cancel-policy-2026-01
    resource: urn:policy:POL-ORDER-CANCEL-2026-01
    role: business-policy
generated:
  by: domain-knowledge-library/test-fixture
  at: 2026-08-18T09:00:00Z
status: draft
stale_after: 2026-11-18
---

# 规则

`SHIPPED` 状态的普通实物订单不可取消。[^cancel-policy-2026-01]

# 审核状态

等待 `REV-ORDER-CANCEL-006` 的领域 Owner 确认。

[^cancel-policy-2026-01]: 业务制度 POL-ORDER-CANCEL-2026-01 第 4.3 条。
