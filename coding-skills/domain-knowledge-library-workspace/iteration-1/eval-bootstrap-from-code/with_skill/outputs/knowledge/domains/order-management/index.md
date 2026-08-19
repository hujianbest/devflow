# 订单管理候选领域

> 本目录全部是 `draft` 领域候选。代码与契约能证明 AS-IS 实现或声明，不能确认正式业务边界和语义。

- [订单管理候选 Bounded Context](overview.md)（draft）- 范围、边界热点、事实拥有者和审核问题。
- [订单取消候选能力](capabilities/order-cancellation.md)（draft）- 从取消接口与实现归纳的能力候选。
- [订单](glossary/order.md)（draft）- 当前 Context 内的窄定义候选。
- [订单状态](glossary/order-status.md)（draft）- 四个代码值与待确认业务含义。
- [订单取消候选流程](processes/order-cancellation.md)（draft）- 分离契约入口、实现链和未知映射。
- [订单取消资格候选规则](rules/order-cancellation-eligibility.md)（draft）- 分离实现分支与正式规则假设。

## 相关实现

- [Order Service 候选 Application](../../systems/order-service/overview.md)（draft）。

## 人工门禁

审核问题在 `.kb/review-queue/index.md`：RQ-001（Context 边界）、RQ-002（规则与例外）、RQ-003（接口绑定与 owner）。
