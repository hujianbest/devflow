# Identity Account

- **上下文**：`identity-service`
- **代码名**：`Account`
- **知识状态**：候选，核心事实由服务说明和实现直接支持

## 定义

Identity Account 是由 `subject_id` 标识的认证主体。它拥有登录凭据和启用/禁用状态。服务说明明确排除财务语义：该账户不表示财务台账或余额。

## 已观察模型

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `subject_id` | `str` | 认证主体标识 |
| `email` | `str` | 与主体关联的电子邮件字段 |
| `enabled` | `bool` | 主体是否启用 |

实现使用 Python `dataclass`。服务说明称主体“拥有登录凭据”，但当前模型只展示 `email`；不能据此断定 `email` 是唯一或完整的登录凭据。

## 已观察行为：认证资格

`can_authenticate(account)` 直接返回 `account.enabled`：

```text
enabled == True  -> 可以通过此项资格检查
enabled == False -> 不能通过此项资格检查
```

这只是当前函数表达的启停检查。输入没有证明完成认证仅需该条件。

## 关系

- **已观察**：Identity Account 表示一个认证主体。
- **未知**：主体与凭据的数量及具体关系。
- **未知**：与 customer 或 Billing Account 是否存在映射。

## 不应混淆

该概念不是 [Billing Account](../billing-service/account.md)。后者由
`billing_account_id` 标识，记录 `outstanding_balance` 和 `currency`。

## 证据

- `identity-service/README.md`
- `identity-service/src/account.py`
