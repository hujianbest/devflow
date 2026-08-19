---
type: Ubiquitous Term
title: 订单（候选术语）
description: 当前候选 Context 中由 order_id 和 OrderStatus 组成的订单对象；业务定义待确认。
tags: [order, term-candidate]
context: order-management
view: as-is
owner: unknown
sensitivity: internal
sources:
  - id: src-order-service-py
    resource: "git+https://github.com/hujianbest/devflow.git@440bf01d2ea2f0b65813790e0c1febcadf04410e#coding-skills/domain-knowledge-library/evals/fixtures/order-service/src/order_service.py"
    title: order_service.py
    role: implementation
    author: process:git
    last_modified: 2026-08-19
  - id: contract-openapi
    resource: "git+https://github.com/hujianbest/devflow.git@440bf01d2ea2f0b65813790e0c1febcadf04410e#coding-skills/domain-knowledge-library/evals/fixtures/order-service/openapi.yaml"
    title: Order Service OpenAPI
    role: contract
    author: process:git
    last_modified: 2026-08-19
generated:
  by: domain-knowledge-library/static-analysis
  at: 2026-08-19T17:09:54Z
status: draft
stale_after: 2026-11-19
---

# 定义

- **Observed implementation**：`Order` 是具有 `order_id: str` 与 `status: OrderStatus` 的 Python dataclass。[^src-order-service-py]
- **Inferred business meaning**：它可能代表可被取消操作识别并改变状态的业务订单；该定义尚未由领域 owner 确认。

# 适用 Context

仅适用于候选 `order-management` Context。不能把此窄定义推广到支付、履约或其他 Context。

# 别名

- 代码名：`Order`。
- 契约路径资源名：`orders`。[^contract-openapi]
- 其他正式别名：unknown。

# 示例

- 实现和测试源码构造带字符串标识与枚举状态的 `Order` 对象。

# 反例

- 仅凭 `orderId` 字符串不能证明已加载完整 `Order` 对象。
- 当前证据不支持把支付记录、发货记录或购物车称为本 Context 的 Order。

# 易混淆术语

- 支付订单、履约订单：当前没有相邻 Context 证据，定义 unknown。

# 代码与契约锚点

- API：`POST /orders/{orderId}/cancel`。
- Event：未发现。
- Model/Table：Python `Order` dataclass；未发现表。
- Symbol：`src.order_service.Order`。

# 跨 Context 翻译

- 未知；需要相邻 Context 和事实拥有者证据。

# 待确认

- 订单的正式定义、生命周期、标识格式和事实拥有者。
- `Order` 是否是聚合、DTO、实体或仅测试模型。
- API 中的 `orderId` 如何解析为实现对象。

[^src-order-service-py]: `src/order_service.py` 第 12–15 行的 dataclass 定义。
[^contract-openapi]: `openapi.yaml` 第 6–14 行的路径与参数声明。
