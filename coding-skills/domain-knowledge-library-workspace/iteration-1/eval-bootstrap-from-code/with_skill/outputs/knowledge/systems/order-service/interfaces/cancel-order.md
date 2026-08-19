---
type: API Endpoint
title: POST /orders/{orderId}/cancel
description: OpenAPI 1.0.0 声明的订单取消 operation，声明 200 与 409 响应。
resource: "git+https://github.com/hujianbest/devflow.git@440bf01d2ea2f0b65813790e0c1febcadf04410e#coding-skills/domain-knowledge-library/evals/fixtures/order-service/openapi.yaml"
tags: [http, openapi, order, cancellation]
view: as-is
owner: unknown
sensitivity: internal
applies_to:
  systems: [order-service]
  versions: ["OpenAPI info.version 1.0.0", "git:440bf01d2ea2f0b65813790e0c1febcadf04410e"]
sources:
  - id: contract-openapi
    resource: "git+https://github.com/hujianbest/devflow.git@440bf01d2ea2f0b65813790e0c1febcadf04410e#coding-skills/domain-knowledge-library/evals/fixtures/order-service/openapi.yaml"
    title: Order Service OpenAPI
    role: contract
    author: process:git
    last_modified: 2026-08-19
  - id: src-order-service-py
    resource: "git+https://github.com/hujianbest/devflow.git@440bf01d2ea2f0b65813790e0c1febcadf04410e#coding-skills/domain-knowledge-library/evals/fixtures/order-service/src/order_service.py"
    title: order_service.py
    role: implementation
    author: process:git
    last_modified: 2026-08-19
generated:
  by: domain-knowledge-library/static-analysis
  at: 2026-08-19T17:09:54Z
status: draft
stale_after: 2026-11-19
---

# 契约摘要

- Method：`POST`。
- Path/Operation：`/orders/{orderId}/cancel` / `cancelOrder`。[^contract-openapi]
- Authentication：OpenAPI 片段未声明 security；不能解释为无需认证。
- Owner：unknown。

# 请求

- 必填 path 参数 `orderId`，schema 类型为 `string`。[^contract-openapi]
- 未声明 request body。

# 响应和错误

- `200`：描述为 `Order cancelled`。
- `409`：描述为 `Order cannot be cancelled in its current state`。[^contract-openapi]
- 当前片段未声明响应 body 或 schema。

# 幂等与副作用

- Unknown。`POST` 和响应描述不足以证明幂等策略。
- 契约表达“取消”结果，但不说明持久化、退款、事件、库存或其他副作用。

# 实现入口

- **Inferred / 未验证**：[`OrderService.cancel`](../modules/order-service-module.md) 名称和动作与 operation 相似。[^src-order-service-py]
- 没有 handler、router 或引用关系，不能把该方法记录为已绑定实现。
- `ValueError` 到 409 的映射未知。

# 消费方

- 未发现。

# 契约与实现差异

- 未发现可确认的直接矛盾。
- 契约使用 `orderId`，Python 方法接收完整 `Order` 对象；中间加载和映射层缺失。
- 契约与实现一致性属于 unknown，不是已证明事实。

# 使用前核对

- 当前部署使用的契约版本；
- 网关路由、鉴权和限流；
- operation 与实现入口的绑定；
- 409 映射、响应 body、幂等和实际副作用。

[^contract-openapi]: `openapi.yaml` 第 1–19 行的 OpenAPI 声明。
[^src-order-service-py]: `src/order_service.py` 第 18–23 行的方法定义；只支持候选映射，不证明 API 调用关系。
