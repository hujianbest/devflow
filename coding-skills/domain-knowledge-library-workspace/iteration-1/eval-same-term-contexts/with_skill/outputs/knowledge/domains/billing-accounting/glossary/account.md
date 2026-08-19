---
type: Ubiquitous Term
title: Account
description: 在 billing-accounting 中，Account 是以 billing_account_id 标识并跟踪余额与币种的计费台账账户候选。
tags: [billing, ledger, account]
context: billing-accounting
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

# 定义

候选定义：在 `billing-accounting` Context 中，`Account` 是由 `billing_account_id` 标识、跟踪货币余额和币种的 billing ledger account。README 还声明一个 customer 可拥有多个此类账户。[^billing-readme]

# 适用 Context

仅适用于 `billing-accounting` 和 billing-service 中相应模型。引用时建议写作 “Billing Account” 或带上 Context 路径。

# 别名

- Billing Account
- Billing ledger account
- 计费账户

# 示例

- 具有 `billing_account_id="ba-123"`、`outstanding_balance` 和 `currency` 的对象。

# 反例

- 以 `subject_id` 标识、持有邮箱和启停状态的登录主体。
- Customer 本身；README 只说 Customer 可以拥有多个 billing accounts，不等同于 Account。

# 易混淆术语

- [`identity-access/Account`](../../identity-access/glossary/account.md)：登录/认证主体，不表示财务台账或余额。

# 代码与契约锚点

- API：未发现。
- Event：未发现。
- Model/Table：[billing-service Account 数据模型](../../../systems/billing-service/data-models/account.md)。
- Symbol：`billing-service/src/account.py::Account`、`::can_charge`。[^billing-account-code]

# 跨 Context 翻译

- 不得翻译为 identity `Account`。
- 当前没有证据说明 `billing_account_id` 与 `subject_id` 的关系；如需关联，应新增显式映射/关系 Concept。

# 待确认

- 正式中文名、owner、客户关系、余额正负约定、币种约束和生命周期。

[^billing-readme]: Billing Service README，固定 revision 下的设计声明。
[^billing-account-code]: `billing-service/src/account.py`，固定 revision 下的实现。
