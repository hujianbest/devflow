---
type: Bounded Context
title: Identity Access
description: 围绕登录主体、邮箱和启停状态的候选模型边界。
tags: [identity, authentication, account]
context: identity-access
view: as-is
owner: unknown
sensitivity: internal
applies_to:
  systems: [identity-service]
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

# AI 使用摘要

- 适用场景：处理 `subject_id`、邮箱、主体启停状态和 authentication predicate。
- 先读：[Account](glossary/account.md)。
- 使用前核对：这是候选 Context；身份与访问规则必须经 identity owner 确认。

# 模型边界

## 范围内

- 候选：认证主体标识、邮箱和启停状态。[^identity-readme]
- 已观察实现：根据 `enabled` 返回 authentication predicate。[^identity-account-code]

## 范围外

- 计费台账、货币余额、币种和 `billing_account_id`。[^identity-readme]
- 凭据格式、认证协议、授权、会话和持久化；当前来源未覆盖。

# 核心业务能力

- 候选：表示拥有登录凭据及启停状态的认证主体。[^identity-readme]
- 候选：依据 `enabled` 评估是否可认证；实际凭据校验和完整认证流程未知。

# 统一语言

- [Account](glossary/account.md) — 本 Context 中专指登录/认证主体。

# 事实拥有者

- 代码位于 identity-service；业务 owner 和数据 owner 未知。

# 相关系统

- [Identity Service](../../systems/identity-service/overview.md)。

# Context 关系

- 与 `billing-accounting` 的同名 `Account` 需要显式翻译；当前没有映射或上下游证据。

# 已确认事实

- 无人工确认的领域事实。

# 候选解释与待确认项

- Context 名称和边界为 Inferred。
- README 的业务描述与代码结构相互支持，但仍不等同于 owner 确认。
- 需要确认“拥有登录凭据”对应的数据存储与安全边界。

# 证据

- README 为设计声明；Python 文件为当前实现。二者固定在同一 Git revision。

[^identity-readme]: Identity Service README，固定 revision 下的设计声明。
[^identity-account-code]: `identity-service/src/account.py`，固定 revision 下的实现。
