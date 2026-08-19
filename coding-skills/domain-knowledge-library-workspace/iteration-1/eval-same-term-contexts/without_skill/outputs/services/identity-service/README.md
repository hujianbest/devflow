# Identity Service

## 上下文职责

候选描述：该服务管理认证主体的登录信息、启停状态及认证资格判断。

## 领域概念

- [Identity Account](account.md)：由 `subject_id` 标识的认证主体。

## 已观察行为

- `can_authenticate(account)` 依据账户的 `enabled` 状态返回认证资格。

## 上下文边界

服务说明明确指出，本服务的 `Account` 不表示财务台账或余额。它不应与
[Billing Account](../billing-service/account.md) 合并。

## 待确认

- `email` 是否为登录凭据本身、凭据标识，还是联系属性；
- `email` 的唯一性和规范化规则；
- 禁用账户的原因、状态迁移和恢复规则；
- 身份验证方式、密码或其他凭据的存储模型。
