---
type: Module
title: Identity Account Module
description: 定义身份 Account 数据类和 can_authenticate predicate 的 Python 模块。
resource: "git+https://github.com/hujianbest/devflow.git@440bf01d2ea2f0b65813790e0c1febcadf04410e#domain-knowledge-library/evals/fixtures/same-term-contexts/identity-service/src/account.py"
tags: [identity, python, account]
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

# 已观察结构

- Python `dataclass Account` 声明三个字段：`subject_id: str`、`email: str`、`enabled: bool`。[^identity-account-code]
- 函数 `can_authenticate(Account) -> bool` 返回 `enabled` 字段。[^identity-account-code]

# 静态关系

- `can_authenticate` 通过类型注解和属性读取引用同一模块的 `Account`。
- 这是 symbol reference；未证明运行时调用路径或完整认证流程。

# 导航

- [应用概览](../overview.md)
- [Account 数据模型](../data-models/account.md)
- [Context 内术语](../../../domains/identity-access/glossary/account.md)

[^identity-account-code]: `identity-service/src/account.py`，固定 revision 下的实现。
