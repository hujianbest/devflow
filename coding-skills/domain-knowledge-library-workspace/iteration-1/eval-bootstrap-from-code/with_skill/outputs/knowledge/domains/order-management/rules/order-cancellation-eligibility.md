---
type: Business Rule
title: 订单取消资格（候选规则）
description: 当前代码仅允许 CREATED 或 PAID 状态进入取消分支；正式业务规则、例外与资金影响待确认。
tags: [order, cancellation, eligibility, rule-candidate]
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

# 规则

- **Observed implementation fact**：`OrderService.cancel` 仅在状态属于 `{CREATED, PAID}` 时继续；其他值触发 `ValueError`。成功分支把状态改为 `CANCELLED`。[^src-order-service-py]
- **Inferred business semantics**：`CREATED` 与 `PAID` 订单“业务上允许取消”，其他状态“不允许取消”。该解释没有业务政策或人工确认，必须保持候选。

# 适用条件

- 当前固定 Git revision。
- 调用 Python `OrderService.cancel`，且传入对象状态是 `CREATED` 或 `PAID`。

# 不适用条件

- 不得推广到未观察到的生产版本、其他服务或其他 Context。
- 不得据此推断退款、库存、发货拦截或权限规则。

# 不变量

- **Observed in method**：正常返回前状态被赋为 `CANCELLED`。
- **Unknown**：持久化后、并发下或跨服务交互后的不变量。

# 例外和优先级

- 当前实现没有例外分支或规则优先级。
- 这不证明业务上没有管理员强制取消、欺诈、超时、售后或其他例外。

# 违反规则时

- 实现抛出 `ValueError("order cannot be cancelled in current status")`。[^src-order-service-py]
- OpenAPI 声明当前状态不可取消时返回 409。[^contract-openapi]
- 二者的运行时映射未证明。

# 实现与测试证据

- 实现允许集合：`CREATED`、`PAID`。
- 测试源码包含 PAID 成功断言。
- 测试源码包含 SHIPPED 期望 `ValueError` 的断言。[^test-order-service-py]
- 测试未运行；`CREATED` 与 `CANCELLED` 没有测试源码场景。

# 业务来源

- 无。代码、测试和接口契约都不能单独确认正式业务政策。

# 使用前核对

- 当前业务政策和生产版本；
- 全部状态及例外；
- `PAID` 后取消的退款、账务与合规要求；
- 调用权限、幂等、并发和持久化；
- 409 映射和 error schema。

# 待确认

- 订单领域 owner 是否确认允许集合和终态语义。
- 支付/财务责任人是否确认 PAID 订单取消及资金副作用。
- SHIPPED、CANCELLED 和任何扩展状态的正式处理。

[^src-order-service-py]: `src/order_service.py` 第 18–23 行的条件、异常与赋值；只证明当前实现。
[^test-order-service-py]: `tests/test_order_service.py` 的两个静态测试场景；本次未执行。
[^contract-openapi]: `openapi.yaml` 的 200/409 声明；不证明异常映射。
