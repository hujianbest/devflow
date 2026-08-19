---
type: Business Process
title: 订单取消（候选流程）
description: 分离 OpenAPI 取消入口声明与 Python 状态变更实现的 AS-IS 候选流程。
tags: [order, cancellation, process-candidate]
context: order-management
view: as-is
owner: unknown
sensitivity: internal
applies_to:
  systems: [order-service]
  versions: ["git:440bf01d2ea2f0b65813790e0c1febcadf04410e"]
sources:
  - id: src-order-service-py
    resource: "git+https://github.com/hujianbest/devflow.git@440bf01d2ea2f0b65813790e0c1febcadf04410e#coding-skills/domain-knowledge-library/evals/fixtures/order-service/src/order_service.py"
    title: order_service.py
    role: implementation
    author: process:git
    last_modified: 2026-08-19
  - id: test-order-service-py
    resource: "git+https://github.com/hujianbest/devflow.git@440bf01d2ea2f0b65813790e0c1febcadf04410e#coding-skills/domain-knowledge-library/evals/fixtures/order-service/tests/test_order_service.py"
    title: test_order_service.py
    role: test-observation
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

# AI 使用摘要

- 适用场景：理解固定版本中取消动作的契约与方法级实现。
- 关键入口：[OpenAPI 取消 operation](../../../systems/order-service/interfaces/cancel-order.md)和 `OrderService.cancel`。
- 使用前核对：两者路由绑定、owner、规则确认和生产副作用。

# 目标与结果

- **Contract / Observed**：operation 声明成功结果为“Order cancelled”，当前状态不可取消时为 409。[^contract-openapi]
- **Implementation / Observed**：方法成功时把传入对象状态改为 `CANCELLED` 并返回。[^src-order-service-py]
- **Inferred**：二者可能描述同一业务流程，但没有静态调用边。

# 触发条件

- 契约入口需要 `orderId` path 参数。
- 实现入口需要一个 `Order` 对象。
- 从 ID 加载对象、调用方身份和前置权限未知。

# 参与者与事实拥有者

- 声明参与者：HTTP 调用方，但身份类型未声明。
- 实现参与者：`OrderService` 与传入的内存 `Order`。
- 事实拥有者：unknown。

# 主流程

以下只描述 `OrderService.cancel` 的已观察实现：

1. 接收 `Order` 对象。
2. 检查状态是否在 `{CREATED, PAID}`。
3. 若在集合内，把同一对象的状态赋值为 `CANCELLED`。
4. 返回该对象。[^src-order-service-py]

OpenAPI 请求如何到达第 1 步是 unknown。

# 状态和业务规则

- [取消资格候选规则](../rules/order-cancellation-eligibility.md)。
- 允许集合与赋值是实现事实；其作为正式业务规则的解释是 `Inferred`。

# 异步和跨 Context 交互

- 未观察到消息、事件或外部调用。
- 不能据此断言生产流程没有退款、库存、履约或通知交互。

# 失败、补偿和幂等

- 实现：状态不允许时抛出 `ValueError`，消息为 `order cannot be cancelled in current status`。[^src-order-service-py]
- 契约：声明 409，但没有 error schema。[^contract-openapi]
- 异常到 409 的映射、重试、重复取消、补偿和幂等均 unknown。

# 例外与历史兼容

- 未发现。

# 实现锚点

- API：`POST /orders/{orderId}/cancel` / `cancelOrder`。
- Event：未发现。
- Module：`src.order_service`。
- Data：内存 `Order` / `OrderStatus`。
- Test：源码包含 PAID 成功与 SHIPPED 抛错断言；未运行。[^test-order-service-py]

# 已确认事实

- `Confirmed`：无。
- 以上 `Observed` 标签只表示固定来源可定位，不表示业务 owner 已确认。

# 推断与待确认项

- API 与方法是否属于同一运行链路。
- 资格集合、状态含义、错误码和全部例外。
- 持久化、鉴权、退款、事件和跨 Context 副作用。
- 谁拥有取消决策和订单事实。

[^src-order-service-py]: `src/order_service.py` 第 18–23 行的固定版本方法实现。
[^test-order-service-py]: `tests/test_order_service.py` 中的静态测试断言；未执行。
[^contract-openapi]: `openapi.yaml` 中的固定版本 path、参数和响应声明。
