# 订单取消规则人工确认

- Review ID：REV-ORDER-CANCEL-006
- 确认人：human:order-domain-owner
- 职责范围：order-fulfillment 领域规则 Owner，负责订单状态与取消政策
- 确认时间：2026-08-20T08:30:00Z
- 适用范围：order-fulfillment；order-service；production；普通实物订单
- 证据引用：业务制度 `POL-ORDER-CANCEL-2026-01` 第 4.3 条

## 确认的精确主张

`SHIPPED` 状态的普通实物订单不可取消。

该确认仅覆盖以上主张和适用范围，不确认其他订单状态、例外流程或退款规则。
