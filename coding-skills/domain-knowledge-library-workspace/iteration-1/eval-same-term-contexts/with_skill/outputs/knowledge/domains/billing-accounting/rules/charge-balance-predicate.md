---
type: Business Rule
title: Charge balance predicate
description: billing-service 当前实现仅在 outstanding_balance 与 amount 之和非负时返回可 charge。
tags: [billing, charge, balance]
context: billing-accounting
view: as-is
owner: unknown
sensitivity: internal
applies_to:
  systems: [billing-service]
sources:
  - id: billing-account-code
    resource: "git+https://github.com/hujianbest/devflow.git@440bf01d2ea2f0b65813790e0c1febcadf04410e#domain-knowledge-library/evals/fixtures/same-term-contexts/billing-service/src/account.py"
    title: Billing account implementation
    role: implementation
generated:
  by: domain-knowledge-library/bootstrap
  at: 2026-08-19T17:10:00Z
status: draft
stale_after: 2026-11-19
---

# 规则

已观察实现：`can_charge(account, amount)` 当且仅当 `account.outstanding_balance + amount >= Decimal("0")` 时返回 `True`。[^billing-account-code]

将该 predicate 解释为正式业务规则属于 Inferred，尚未确认。

# 适用条件

- 仅能证明对传入 `Account` 与 `Decimal amount` 的此函数行为。

# 不适用条件

- 不能据此推断支付授权、信用额度、币种匹配、并发余额或生产执行结果。

# 不变量

- 函数比较计算结果与十进制零；数据类本身没有余额不变量。

# 例外和优先级

- 未发现。

# 违反规则时

- 函数返回 `False`；未观察到异常、状态变化或外部调用。

# 实现与测试证据

- 实现见 `billing-service/src/account.py::can_charge`。[^billing-account-code]
- 未发现测试。

# 业务来源

- 无 business-policy 或 human-confirmation 来源。

# 使用前核对

- `amount` 正负方向、余额含义、币种处理及该函数是否为必经路径。

# 待确认

- Billing owner 是否认可其为业务规则，以及正式规则名称和例外。

[^billing-account-code]: `billing-service/src/account.py`，固定 revision 下的实现。
