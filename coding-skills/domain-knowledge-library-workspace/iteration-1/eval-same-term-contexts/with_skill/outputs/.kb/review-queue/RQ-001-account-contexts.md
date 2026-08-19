# RQ-001：确认同名 Account 的 Context 边界

## 争议点

是否接受 `billing-accounting` 与 `identity-access` 为两个 Bounded Context 候选，并在两个 Context 中分别定义 `Account`。

## 证据

- Billing README 明称 `Account` 是以 `billing_account_id` 标识、跟踪余额和币种的 billing ledger account；代码字段与之吻合。
- Identity README 明称 `Account` 是以 `subject_id` 标识、拥有登录凭据及启停状态的 authentication subject，并明确排除财务 ledger/balance；代码字段与之吻合。
- 两侧没有共同标识、映射逻辑、API、事件或关系证据。

## 建议选项

1. 确认两个 Context 和两个局部定义；分别记录 billing 与 identity owner。
2. 修改 Context 名称或范围，但仍保留两个局部术语。
3. 提供跨 Context 映射证据后，新增翻译/关系 Concept；不要用全局定义替代映射。

## 影响范围

- `knowledge/domains/billing-accounting/**`
- `knowledge/domains/identity-access/**`
- 涉及 `Account` 的后续检索和代码生成提示

## 所需确认者

- Billing 领域 owner
- Identity/Access 领域 owner

资金与权限相关语义在确认前均保持 `draft`。
