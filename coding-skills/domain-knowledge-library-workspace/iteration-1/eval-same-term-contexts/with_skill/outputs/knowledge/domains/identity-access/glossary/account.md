---
type: Ubiquitous Term
title: Account
description: 在 identity-access 中，Account 是以 subject_id 标识、拥有登录凭据与启停状态的认证主体候选。
tags: [identity, authentication, account]
context: identity-access
view: as-is
owner: unknown
sensitivity: internal
sources:
  - id: identity-readme
    resource: "git+https://github.com/hujianbest/devflow.git@440bf01d2ea2f0b65813790e0c1febcadf04410e#domain-knowledge-library/evals/fixtures/same-term-contexts/identity-service/README.md"
    title: Identity Service README
    role: design-intent
  - id: identity-account-code
    resource: "git+https://github.com/hujianbest/devflow.git@440bf01d2ea2f0b65813790e0c1febcadf04410e#domain-knowledge-library/evals/fixtures/same-term-contexts/identity-service/src/account.py"
    title: Identity account implementation
    role: implementation
generated:
  by: domain-knowledge-library/bootstrap
  at: 2026-08-19T17:10:00Z
status: draft
stale_after: 2026-11-19
---

# 定义

候选定义：在 `identity-access` Context 中，`Account` 是由 `subject_id` 标识、拥有登录凭据和 enabled/disabled 状态的 authentication subject。它不表示财务台账或余额。[^identity-readme]

# 适用 Context

仅适用于 `identity-access` 和 identity-service 中相应模型。引用时建议写作 “Identity Account” 或带上 Context 路径。

# 别名

- Identity Account
- Authentication subject
- 登录主体

# 示例

- 具有 `subject_id="sub-123"`、`email` 和 `enabled=true` 的对象。

# 反例

- 具有 `billing_account_id`、余额和币种的计费台账账户。
- Customer 或财务 ledger；README 明确排除 financial ledger/balance。

# 易混淆术语

- [`billing-accounting/Account`](../../billing-accounting/glossary/account.md)：跟踪余额和币种的计费台账账户。

# 代码与契约锚点

- API：未发现。
- Event：未发现。
- Model/Table：[identity-service Account 数据模型](../../../systems/identity-service/data-models/account.md)。
- Symbol：`identity-service/src/account.py::Account`、`::can_authenticate`。[^identity-account-code]

# 跨 Context 翻译

- 不得翻译为 billing `Account`。
- 当前没有证据说明 `subject_id` 与 `billing_account_id` 的关系；如需关联，应新增显式映射/关系 Concept。

# 待确认

- 正式中文名、owner、凭据边界、邮箱约束、状态转换和生命周期。

[^identity-readme]: Identity Service README，固定 revision 下的设计声明。
[^identity-account-code]: `identity-service/src/account.py`，固定 revision 下的实现。
