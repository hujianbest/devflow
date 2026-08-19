---
type: Data Model
title: Billing Account
description: billing-service 代码中声明的内存计费账户数据结构；持久化方式未知。
resource: "git+https://github.com/hujianbest/devflow.git@440bf01d2ea2f0b65813790e0c1febcadf04410e#domain-knowledge-library/evals/fixtures/same-term-contexts/billing-service/src/account.py"
tags: [billing, account, balance]
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

# 模型摘要

- 事实拥有者：代码位置为 billing-service；业务和数据 owner 未知。
- 存储：Python 内存对象；未发现持久化证据。
- 主键：代码未声明主键约束；`billing_account_id` 是标识字段候选。
- 生命周期：未知。

# Schema

| Field | Type | Meaning | Constraints |
|---|---|---|---|
| `billing_account_id` | `str` | 计费账户标识候选 | 代码未声明非空/唯一约束 |
| `outstanding_balance` | `Decimal` | 未结余额候选 | 代码未声明字段级范围 |
| `currency` | `str` | 币种候选 | 代码未声明格式或枚举 |

字段与类型由实现直接观察。[^billing-account-code]

# 关系

- 未发现与 Customer 或 identity-service Account 的代码关系。

# 状态和不变量

- 数据类本身没有校验。
- `can_charge` 使用余额加 amount 非负的 predicate；金额符号含义仍未知。

# 写入与读取入口

- 未发现。

# 迁移、ORM 与实际 Schema 差异

- 未发现迁移、ORM 或数据库 schema，不能把此数据类当作实际持久化 schema。

# 敏感数据

- 金额和账户标识可能敏感；分类仍待 owner 确认。

# 使用前核对

- 实际 schema、标识约束、币种规则、金额符号约定和数据保留策略。

[^billing-account-code]: `billing-service/src/account.py`，固定 revision 下的实现。
