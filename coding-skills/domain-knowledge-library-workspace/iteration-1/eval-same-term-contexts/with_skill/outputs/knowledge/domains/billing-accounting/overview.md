---
type: Bounded Context
title: Billing Accounting
description: 围绕计费台账账户、未结余额和币种的候选模型边界。
tags: [billing, ledger, account]
context: billing-accounting
view: as-is
owner: unknown
sensitivity: internal
applies_to:
  systems: [billing-service]
sources:
  - id: billing-readme
    resource: "git+https://github.com/hujianbest/devflow.git@440bf01d2ea2f0b65813790e0c1febcadf04410e#domain-knowledge-library/evals/fixtures/same-term-contexts/billing-service/README.md"
    title: Billing Service README
    role: design-intent
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

# AI 使用摘要

- 适用场景：处理 `billing_account_id`、余额、币种和 charge predicate。
- 先读：[Account](glossary/account.md)。
- 使用前核对：这是候选 Context；资金规则必须经 billing owner 确认。

# 模型边界

## 范围内

- 候选：计费台账账户的标识、未结余额和币种。[^billing-readme]
- 已观察实现：使用账户余额和 amount 计算非负 predicate。[^billing-account-code]

## 范围外

- 登录凭据、邮箱、认证主体启停状态。
- 客户身份、支付执行、账单生命周期、汇率及持久化；当前来源未覆盖。

# 核心业务能力

- 候选：维护一个客户可拥有的一个或多个计费账户。[^billing-readme]
- 候选：依据余额 predicate 评估 charge；predicate 的正式业务名称和金额方向待确认。

# 统一语言

- [Account](glossary/account.md) — 本 Context 中专指计费台账账户。

# 事实拥有者

- 代码位于 billing-service；业务 owner 和数据 owner 未知。

# 相关系统

- [Billing Service](../../systems/billing-service/overview.md)。

# Context 关系

- 与 `identity-access` 的同名 `Account` 需要显式翻译；当前没有映射或上下游证据。

# 已确认事实

- 无人工确认的领域事实。

# 候选解释与待确认项

- Context 名称和边界为 Inferred。
- README 的业务描述与代码结构相互支持，但仍不等同于 owner 确认。
- 需要确认客户、计费账户与身份主体间是否存在其他系统维护的关系。

# 证据

- README 为设计声明；Python 文件为当前实现。二者固定在同一 Git revision。

[^billing-readme]: Billing Service README，固定 revision 下的设计声明。
[^billing-account-code]: `billing-service/src/account.py`，固定 revision 下的实现。
