---
type: Module
title: Billing Account Module
description: 定义计费 Account 数据类和 can_charge predicate 的 Python 模块。
resource: "git+https://github.com/hujianbest/devflow.git@440bf01d2ea2f0b65813790e0c1febcadf04410e#domain-knowledge-library/evals/fixtures/same-term-contexts/billing-service/src/account.py"
tags: [billing, python, account]
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

# 已观察结构

- Python `dataclass Account` 声明三个字段：`billing_account_id: str`、`outstanding_balance: Decimal`、`currency: str`。[^billing-account-code]
- 函数 `can_charge(Account, Decimal) -> bool` 直接计算余额与金额之和是否非负。[^billing-account-code]

# 静态关系

- `can_charge` 通过类型注解和属性读取引用同一模块的 `Account`。
- 这是 symbol reference；未证明运行时调用路径。

# 导航

- [应用概览](../overview.md)
- [Account 数据模型](../data-models/account.md)
- [Context 内术语](../../../domains/billing-accounting/glossary/account.md)

[^billing-account-code]: `billing-service/src/account.py`，固定 revision 下的实现。
