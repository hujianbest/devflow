# Account：上下文消歧

## 结论

联合知识库保留两个独立概念，不建立全局 `Account` 定义：

1. [Billing Account](../services/billing-service/account.md) 属于 `billing-service`。
2. [Identity Account](../services/identity-service/account.md) 属于 `identity-service`。

## 为什么不能合并

| 维度 | Billing Account | Identity Account |
| --- | --- | --- |
| 领域 | 计费台账 | 身份与认证 |
| 标识 | `billing_account_id` | `subject_id` |
| 数据 | `outstanding_balance`、`currency` | `email`、`enabled` |
| 行为 | `can_charge` | `can_authenticate` |
| 明确排除 | 未说明认证职责 | 明确不是财务台账或余额 |

两者的标识、状态和行为均不相同。仅因 Python 类名同为 `Account` 就合并，会把财务余额错误地放到登录主体上，或把认证状态错误地当作计费账户状态。

## 写作与检索规则

- 服务内部可在上下文明确时使用 `Account`。
- 跨服务材料使用 `Billing Account` 或 `Identity Account`。
- 代码引用使用 `billing-service.Account` 或 `identity-service.Account`。
- 搜索裸词 `Account` 时，应返回两个候选项并要求上下文，不默认选取或合并。

## 尚未建立的关系

输入没有证明以下关系，因此知识库不作断言：

- `subject_id` 是否可关联 `billing_account_id`；
- Identity Account 是否等同于 billing 文档中的 customer；
- 一个登录主体可访问几个计费账户；
- 两个服务之间是否通过 API、事件或共享标识通信。

这些问题需要接口、事件定义、持久化模型或领域专家提供进一步证据。
