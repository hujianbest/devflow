---
type: Reference
title: Account disambiguation
description: 按 Bounded Context 导航两个同名但不同义的 Account；本库不提供全局 Account 定义。
tags: [account, disambiguation, navigation]
view: as-is
owner: unknown
sensitivity: internal
sources:
  - id: billing-readme
    resource: "git+https://github.com/hujianbest/devflow.git@440bf01d2ea2f0b65813790e0c1febcadf04410e#domain-knowledge-library/evals/fixtures/same-term-contexts/billing-service/README.md"
    title: Billing Service README
    role: design-intent
  - id: identity-readme
    resource: "git+https://github.com/hujianbest/devflow.git@440bf01d2ea2f0b65813790e0c1febcadf04410e#domain-knowledge-library/evals/fixtures/same-term-contexts/identity-service/README.md"
    title: Identity Service README
    role: design-intent
generated:
  by: domain-knowledge-library/bootstrap
  at: 2026-08-19T17:10:00Z
status: draft
stale_after: 2026-11-19
---

# 使用规则

不要脱离 Context 使用 `Account`，也不要建立抹平差异的全局定义。

| Context | Account 含义 | 标识 | 关键字段 | 入口 |
|---|---|---|---|---|
| `billing-accounting` | 计费台账账户 | `billing_account_id` | `outstanding_balance`, `currency` | [Billing Account](../domains/billing-accounting/glossary/account.md) |
| `identity-access` | 登录/认证主体 | `subject_id` | `email`, `enabled` | [Identity Account](../domains/identity-access/glossary/account.md) |

Billing README 将 Account 定义为计费台账账户。[^billing-readme] Identity README 将同名词定义为认证主体，并明确排除财务台账和余额。[^identity-readme]

# 翻译边界

- `billing_account_id` 不等于 `subject_id`。
- 当前来源没有两者间的映射、共享标识、API、事件或上下游关系证据。
- 若业务需要关联，应新增显式 Context Relationship 或映射 Concept，并提供来源；不能靠字符串同名推断。

# 状态

两个 Context 及其术语均为候选，等待各自领域 owner 确认。本页只提供安全导航，不将候选语义晋级为已确认事实。

[^billing-readme]: Billing Service README，固定 revision 下的设计声明。
[^identity-readme]: Identity Service README，固定 revision 下的设计声明。
