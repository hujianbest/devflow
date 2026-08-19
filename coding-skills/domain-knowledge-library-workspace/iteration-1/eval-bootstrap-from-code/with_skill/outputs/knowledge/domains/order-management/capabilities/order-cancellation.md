---
type: Business Capability
title: 订单取消（候选能力）
description: 从取消接口、状态变更实现和测试场景归纳的候选业务能力，职责与边界待确认。
tags: [order, cancellation, capability-candidate]
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

# 能力候选

**Inferred**：系统可能向调用方提供“在状态允许时取消订单”的能力。

支持信号：

- 契约声明一个取消 operation 与成功/当前状态冲突响应。[^contract-openapi]
- 实现包含资格分支和到 `CANCELLED` 的赋值。[^src-order-service-py]
- 测试源码包含一个成功与一个失败场景。[^test-order-service-py]

# 当前实现范围

- 输入实现方法的是完整 `Order` 对象，不是 `orderId`。
- 成功时只观察到内存状态修改和对象返回。
- 不可取消时只观察到 `ValueError`。

# 未证明的能力组成

- 订单加载和持久化；
- 调用者授权；
- 退款、库存释放或履约拦截；
- 通知或领域事件；
- 审计、幂等、并发与补偿；
- HTTP 409 映射。

# 相关知识

- [取消流程](../processes/order-cancellation.md)。
- [取消资格规则](../rules/order-cancellation-eligibility.md)。
- [取消 API 契约](../../../systems/order-service/interfaces/cancel-order.md)。

# 人工门禁

领域 owner 需确认该能力的目标、边界、服务对象、事实拥有者和跨 Context 副作用。确认前不得据此实现生产写操作。

[^src-order-service-py]: 指定 Git revision 的取消方法实现。
[^test-order-service-py]: 指定 Git revision 的静态测试断言；未运行。
[^contract-openapi]: OpenAPI 1.0.0 的取消 operation 声明。
