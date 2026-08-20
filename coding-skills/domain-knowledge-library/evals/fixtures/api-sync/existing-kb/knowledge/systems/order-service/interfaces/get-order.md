---
type: API Endpoint
id: API-ORDER-GET-001
title: Get Order
description: 按订单 ID 查询订单的 HTTP Endpoint。
view: as-is
owner: team:order-platform
sensitivity: internal
applies_to:
  systems: [order-service]
sources:
  - id: order-api-1.4.0
    resource: urn:fixture:api-sync:old-openapi.yaml
    role: contract
generated:
  by: domain-knowledge-library/test-fixture
  at: 2026-07-01T09:00:00Z
status: stable
stale_after: 2026-10-01
---

# Contract

- Method: `GET`
- Path: `/orders/{orderId}`
- Success response: `200`

该事实来自 Order API 1.4.0。[^order-api-1.4.0]

[^order-api-1.4.0]: 固定的旧 OpenAPI 契约。
