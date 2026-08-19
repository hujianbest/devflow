---
id: review-order-cancellation-v2
status: pending
created_at: 2026-08-19T17:08:00Z
conflict: ../conflicts/order-cancellation-shipped-v2.md
proposal: ../proposals/ingest-cancel-design-v2.md
required_reviewers:
  - role: order-domain-owner
    scope: business-rule
  - role: warehouse-team
    scope: cross-system-contract
---

# 审核包：订单取消 V2

## 待确认的精确主张

1. 订单领域 Owner 是否确认：处于 `SHIPPED` 且仓库尚未出库的订单，可以发起取消。
2. 订单领域 Owner 是否确认：只有仓储拦截成功后，订单才能转为 `CANCELLED`；拦截失败时保持 `SHIPPED`。
3. 仓储团队是否确认：仓储系统能够提供支撑上述规则的拦截请求与权威结果契约。

## AS-IS / TO-BE

- **AS-IS**：`can_cancel` 当前只允许 `CREATED` 和 `PAID`。来源：`cancel-code-v1` 第 11-12 行，implementation。
- **TO-BE**：设计拟允许满足仓储条件的 `SHIPPED` 订单发起取消。来源：`cancel-design-v2` 第 3-14 行，design-intent；文档明确“尚未实现”和“不代表当前生产行为”。

## 支持证据与反证

- 支持 TO-BE 设计存在：`cancel-design-v2` 的目标、流程和门禁均为直接文本证据。
- 反对“已实现/已生效”的证据：`cancel-code-v1` 排除 `SHIPPED`，设计文档也明确尚未实现。
- 没有业务 Owner 确认、仓储契约、实现测试或运行证据。

## 审核选择

- `confirmed`：分别确认职责范围内的精确主张。
- `modified-and-confirmed`：写明修订后的条件、例外和范围。
- `rejected`：说明被拒绝的主张；保留审计记录。
- `keep-draft`：保留候选知识，但不作为默认事实。
- `needs-more-evidence`：列出所需契约、测试或状态定义。

在完成两类职责确认前，建议仅维持 AS-IS stable 与 TO-BE draft 的分离状态；这不是对候选业务规则本身的批准或否决。
