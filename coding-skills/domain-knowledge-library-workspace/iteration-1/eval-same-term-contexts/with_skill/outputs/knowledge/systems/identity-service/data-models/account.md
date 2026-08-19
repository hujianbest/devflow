---
type: Data Model
title: Identity Account
description: identity-service 代码中声明的内存登录主体数据结构；持久化和凭据模型未知。
resource: "git+https://github.com/hujianbest/devflow.git@440bf01d2ea2f0b65813790e0c1febcadf04410e#domain-knowledge-library/evals/fixtures/same-term-contexts/identity-service/src/account.py"
tags: [identity, account, authentication]
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

# 模型摘要

- 事实拥有者：代码位置为 identity-service；业务和数据 owner 未知。
- 存储：Python 内存对象；未发现持久化证据。
- 主键：代码未声明主键约束；`subject_id` 是标识字段候选。
- 生命周期：README 提到 enabled/disabled 状态，但转换过程未知。

# Schema

| Field | Type | Meaning | Constraints |
|---|---|---|---|
| `subject_id` | `str` | 认证主体标识候选 | 代码未声明非空/唯一约束 |
| `email` | `str` | 登录主体邮箱候选 | 代码未声明格式或唯一约束 |
| `enabled` | `bool` | 是否启用 | 布尔值 |

字段与类型由实现直接观察。[^identity-account-code]

# 关系

- 未发现与 billing-service Account 的代码关系。

# 状态和不变量

- `can_authenticate` 仅检查 `enabled`；不能据此推断凭据校验、锁定或授权规则。

# 写入与读取入口

- 未发现。

# 迁移、ORM 与实际 Schema 差异

- 未发现迁移、ORM 或数据库 schema，不能把此数据类当作实际持久化 schema。

# 敏感数据

- `email` 和身份标识属于潜在个人信息；访问与保留政策未知。

# 使用前核对

- 实际 schema、标识/邮箱约束、凭据存储、状态转换和数据保留策略。

[^identity-account-code]: `identity-service/src/account.py`，固定 revision 下的实现。
