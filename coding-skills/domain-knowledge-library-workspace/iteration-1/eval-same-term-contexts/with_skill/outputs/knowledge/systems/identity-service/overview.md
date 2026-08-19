---
type: Application
title: Identity Service
description: 静态来源中声明 Account 数据结构和 can_authenticate predicate 的应用候选。
resource: "git+https://github.com/hujianbest/devflow.git@440bf01d2ea2f0b65813790e0c1febcadf04410e#domain-knowledge-library/evals/fixtures/same-term-contexts/identity-service"
tags: [identity, authentication, account]
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

# AI 使用摘要

- 适用场景：定位 identity `Account` 的实现字段与 authentication predicate。
- 关键入口：`src/account.py::Account`、`src/account.py::can_authenticate`。
- 使用前核对：没有 manifest 或启动入口，当前证据不足以确认独立部署边界。

# 已观察的实现职责

- `Account` 数据类持有 `subject_id`、`email`、`enabled`。[^identity-account-code]
- `can_authenticate(account)` 直接返回 `account.enabled`。[^identity-account-code]

# 候选业务职责

- README 将该系统中的 `Account` 描述为拥有登录凭据和启停状态的认证主体。此语义是设计声明，等待 owner 确认。[^identity-readme]

# 不负责什么

- README 明确声明该 `Account` 不表示财务台账或余额。[^identity-readme]
- 不应把本系统 `Account` 当作 billing-service 的计费账户。

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

- [Identity Access（候选）](../../domains/identity-access/overview.md)。

# 限制、冲突和待确认

- owner、部署形态、凭据存储、邮箱约束和实际认证流程均未知。

[^identity-readme]: Identity Service README，固定 revision 下的设计声明。
[^identity-account-code]: `identity-service/src/account.py`，固定 revision 下的实现。
