# 构建摘要

已从两个服务的 README 和 `src/account.py` 冷启动联合知识库。

## 产出

- 建立根导航、服务导航、术语索引和证据索引。
- 分别建立 [Billing Account](services/billing-service/account.md) 与
  [Identity Account](services/identity-service/account.md) 候选知识页。
- 建立 [Account 上下文消歧页](glossary/account.md)，规定跨服务使用限定名称。
- 记录直接可证实的数据、行为和边界，并将未获证据支持的关系列为未知或待确认。

## 关键结论

`Account` 必须按服务上下文拆分：

- `billing-service.Account` 是计费台账账户，由 `billing_account_id` 标识；
- `identity-service.Account` 是登录认证主体，由 `subject_id` 标识。

二者没有全局统一定义。当前输入也没有证明 Identity Account、customer 与 Billing Account 之间存在何种映射，因此未创建臆测的跨服务关系。

## 建议的后续确认

1. 查明跨服务主体、customer 和计费账户的关联方式。
2. 确认计费金额与余额的正负号、币种和收费规则。
3. 确认身份账户的凭据模型、邮箱约束和状态迁移。
