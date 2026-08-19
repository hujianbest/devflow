# Billing + Identity 联合知识库

本知识库从 `billing-service` 与 `identity-service` 的现有说明和代码冷启动。内容均为候选领域知识，尚未经过领域专家确认。

## 导航

- [术语索引](glossary/README.md)
  - [Account 的上下文消歧](glossary/account.md)
- [Billing Service](services/billing-service/README.md)
  - [Billing Account](services/billing-service/account.md)
- [Identity Service](services/identity-service/README.md)
  - [Identity Account](services/identity-service/account.md)
- [证据索引](sources.md)
- [构建摘要](summary.md)

## 边界原则

`Account` 不是联合知识库中的单一全局概念：

| 限界上下文 | 推荐名称 | 标识 | 核心职责 |
| --- | --- | --- | --- |
| `billing-service` | Billing Account | `billing_account_id` | 记录币种与货币余额，参与收费判断 |
| `identity-service` | Identity Account | `subject_id` | 表示登录主体，持有登录信息与启停状态 |

跨服务文档不得单独使用裸词 `Account`。应使用限定名称或代码限定名
`billing-service.Account`、`identity-service.Account`。当前证据没有给出两个概念之间的映射关系。

## 可信度约定

- **已观察**：可由输入代码或服务说明直接支持。
- **候选解释**：基于已观察事实组织出的领域表述，需专家确认。
- **未知**：输入没有提供答案，不应自行补全。
