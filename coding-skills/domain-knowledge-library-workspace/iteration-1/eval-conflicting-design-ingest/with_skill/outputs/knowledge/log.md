# Knowledge Update Log

## 2026-08-19

- **Ingest**: 登记《订单取消 V2 设计》及其不可变快照。
- **Draft / TO-BE**: 新增“订单取消状态规则 V2（候选）”，记录 `SHIPPED` 订单经仓储拦截后取消的设计意图。
- **Conflict**: 保留当前实现中 `SHIPPED` 不可取消的 AS-IS 事实，并将其与 TO-BE 设计的时态偏差送入人工审核；未作业务裁决。
- **Source maintenance**: 为既有 AS-IS 规则补充本地固定版本的实现快照引用，正文语义和既有验证未改变。
