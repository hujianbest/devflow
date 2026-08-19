---
type: Application
title: Billing Service
description: 静态来源中声明 Account 数据结构和 can_charge predicate 的应用候选。
resource: "git+https://github.com/hujianbest/devflow.git@440bf01d2ea2f0b65813790e0c1febcadf04410e#domain-knowledge-library/evals/fixtures/same-term-contexts/billing-service"
tags: [billing, account]
view: as-is
owner: unknown
sensitivity: internal
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

- 适用场景：定位计费 `Account` 的实现字段与 charge predicate。
- 关键入口：`src/account.py::Account`、`src/account.py::can_charge`。
- 使用前核对：没有 manifest 或启动入口，当前证据不足以确认独立部署边界。

# 已观察的实现职责

- `Account` 数据类持有 `billing_account_id`、`outstanding_balance`、`currency`。[^billing-account-code]
- `can_charge(account, amount)` 返回 `account.outstanding_balance + amount >= Decimal("0")` 的结果。[^billing-account-code]

# 候选业务职责

- README 将该系统中的 `Account` 描述为计费台账账户，可跟踪余额和币种。此语义是设计声明，等待 owner 确认。[^billing-readme]

# 不负责什么

- 没有身份凭据、邮箱、启停状态或认证判断的实现证据。
- 不应把本系统 `Account` 当作 identity-service 的登录主体。

# 运行与构建单元

- 未发现 manifest、启动入口、容器或部署配置；`Application` 身份为候选。

# 上下游

- 未发现 API、事件或静态跨系统调用证据。

# 接口、事件和数据

- 数据：[Account](data-models/account.md)。
- 未发现 API endpoint、event channel 或持久化 schema。

# 关键模块

- [Account 模块](modules/account.md)。

# 相关 Bounded Context

- [Billing Accounting（候选）](../../domains/billing-accounting/overview.md)。

# 限制、冲突和待确认

- owner、部署形态、金额正负约定、币种约束和持久化均未知。

[^billing-readme]: Billing Service README，固定 revision 下的设计声明。
[^billing-account-code]: `billing-service/src/account.py`，固定 revision 下的实现。
