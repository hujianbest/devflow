# Order Fulfillment

## AS-IS

- [订单取消状态规则](./rules/order-cancellation.md) - 当前实现仅允许 `CREATED` 和 `PAID` 订单取消。

## TO-BE

- [订单取消 V2 设计](./proposals/order-cancellation-v2.md) - 已通过技术评审但尚未实现的 `SHIPPED` 订单取消方案。

## 未解决冲突

- [SHIPPED 订单取消能力冲突](./conflicts/shipped-order-cancellation.md) - 当前实现与未来设计的适用时态不同，业务规则和跨系统契约仍待确认。
