---
type: Ubiquitous Term
title: 订单状态（候选术语）
description: 代码中的 CREATED、PAID、SHIPPED、CANCELLED 四值枚举及其待确认业务含义。
tags: [order, status, term-candidate]
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
  - id: test-order-service-py
    resource: "git+https://github.com/hujianbest/devflow.git@440bf01d2ea2f0b65813790e0c1febcadf04410e#coding-skills/domain-knowledge-library/evals/fixtures/order-service/tests/test_order_service.py"
    title: test_order_service.py
    role: test-observation
    author: process:git
    last_modified: 2026-08-19
generated:
  by: domain-knowledge-library/static-analysis
  at: 2026-08-19T17:09:54Z
status: draft
stale_after: 2026-11-19
---

# 定义

- **Observed implementation**：`OrderStatus` 是字符串枚举，值为 `CREATED`、`PAID`、`SHIPPED`、`CANCELLED`。[^src-order-service-py]
- **Inferred business meaning**：这些名称可能表示订单生命周期阶段，但正式定义、进入条件和责任边界尚未确认。

# 适用 Context

仅适用于候选 `order-management` Context 和当前固定版本。

# 别名

- 代码名：`OrderStatus`。
- 业务别名：unknown。

# 示例

- 测试源码用 `PAID` 构造成功取消场景，用 `SHIPPED` 构造期望失败场景。[^test-order-service-py]
- 测试未运行，不能把场景写成已验证生产行为。

# 反例

- 状态名不证明支付或发货由 Order Service 执行。
- 当前代码没有定义 `CREATED → PAID` 或 `PAID → SHIPPED` 转换，不能据此补全状态机。

# 易混淆术语

- 支付状态、履约状态：可能与订单状态同名或相关，但当前没有相邻 Context 定义。

# 代码与契约锚点

- API：取消接口仅使用“current state”描述 409，未枚举状态。
- Event：未发现。
- Model/Table：`Order.status`；未发现表。
- Symbol：`src.order_service.OrderStatus`。

# 跨 Context 翻译

- 未知。需要支付和履约 Context 的术语与映射证据。

# 待确认

- 每个值的正式业务定义、有效时段和进入条件。
- 是否存在其他生产状态或历史别名。
- `CANCELLED` 是否终态，以及重复取消如何处理。

[^src-order-service-py]: `src/order_service.py` 第 5–9 行的枚举定义。
[^test-order-service-py]: `tests/test_order_service.py` 第 6–14 行的静态场景；本次未执行。
