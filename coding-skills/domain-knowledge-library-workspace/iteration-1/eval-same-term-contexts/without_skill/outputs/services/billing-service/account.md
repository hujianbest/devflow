# Billing Account

- **上下文**：`billing-service`
- **代码名**：`Account`
- **知识状态**：候选，核心事实由服务说明和实现直接支持

## 定义

Billing Account 是由 `billing_account_id` 标识的计费台账账户。它记录货币余额和币种。服务说明指出，一个 customer 可以拥有多个此类账户。

## 已观察模型

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `billing_account_id` | `str` | 计费账户标识 |
| `outstanding_balance` | `Decimal` | 账户的货币余额 |
| `currency` | `str` | 余额币种 |

实现使用 Python `dataclass`。输入中未观察到字段校验、唯一性约束或持久化规则。

## 已观察行为：收费判断

`can_charge(account, amount)` 返回以下表达式的结果：

```text
account.outstanding_balance + amount >= Decimal("0")
```

因此，函数只在相加结果不小于零时返回 `True`。`amount` 的正负号语义未在输入中说明，不能把该函数进一步解释为透支、扣款或授信规则。

## 关系

- **已观察**：一个 customer 可以拥有多个 Billing Account。
- **未知**：customer 的类型、标识及账户是否只能属于一个 customer。
- **未知**：与 Identity Account 是否存在映射。

## 不应混淆

该概念不是 [Identity Account](../identity-service/account.md)。后者由 `subject_id` 标识，描述认证主体，不含余额或币种。

## 证据

- `billing-service/README.md`
- `billing-service/src/account.py`
