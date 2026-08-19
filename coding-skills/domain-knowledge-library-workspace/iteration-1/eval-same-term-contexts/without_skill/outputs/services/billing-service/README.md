# Billing Service

## 上下文职责

候选描述：该服务负责计费台账账户及其收费资格判断。

## 领域概念

- [Billing Account](account.md)：由 `billing_account_id` 标识，记录余额与币种。
- Customer：服务说明提到一个 customer 可以拥有多个 Billing Account，但输入未给出其模型、标识或行为。

## 已观察行为

- `can_charge(account, amount)` 使用账户当前余额与传入金额判断是否可收费。

## 上下文边界

本服务的 `Account` 是计费概念。它不应与
[Identity Account](../identity-service/account.md) 合并。

## 待确认

- `outstanding_balance` 与 `amount` 的正负号约定；
- 币种如何校验，以及 `amount` 是否隐含与账户相同的币种；
- customer 的标识及其与账户的所有权约束；
- 余额更新、收费落账和并发控制机制。
