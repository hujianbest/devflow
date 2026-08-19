---
type: Business Rule
title: Enabled authentication predicate
description: identity-service 当前实现以 Account.enabled 作为 can_authenticate 的返回值。
tags: [identity, authentication, enabled]
context: identity-access
view: as-is
owner: unknown
sensitivity: internal
applies_to:
  systems: [identity-service]
sources:
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

# 规则

已观察实现：`can_authenticate(account)` 返回 `account.enabled`。[^identity-account-code]

将该 predicate 解释为完整或正式认证业务规则属于 Inferred，尚未确认。

# 适用条件

- 仅能证明对传入 `Account` 的此函数行为。

# 不适用条件

- 不能据此推断凭据正确性、锁定、MFA、授权、会话或生产认证结果。

# 不变量

- 无；数据类没有状态转换校验。

# 例外和优先级

- 未发现。

# 违反规则时

- 当 `enabled` 为 `False` 时函数返回 `False`；未观察到异常或副作用。

# 实现与测试证据

- 实现见 `identity-service/src/account.py::can_authenticate`。[^identity-account-code]
- 未发现测试。

# 业务来源

- 无 business-policy 或 human-confirmation 来源。

# 使用前核对

- 此函数是否为认证必经路径，以及凭据/MFA/锁定等其他判断。

# 待确认

- Identity owner 是否认可其为业务规则，以及正式规则名称和例外。

[^identity-account-code]: `identity-service/src/account.py`，固定 revision 下的实现。
