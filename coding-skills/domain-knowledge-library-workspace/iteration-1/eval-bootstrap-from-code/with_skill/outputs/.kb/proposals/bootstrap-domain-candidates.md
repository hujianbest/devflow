---
proposal_id: bootstrap-domain-candidates-001
mode: bootstrap
created_at: 2026-08-19T17:09:54Z
status: awaiting-human-review
change: create
---

# 订单领域候选知识提案

## 提案范围

基于固定版本的实现、测试源码和 OpenAPI 契约，创建以下 `draft` Concept：

- `domains/order-management/overview`
- `domains/order-management/capabilities/order-cancellation`
- `domains/order-management/glossary/order`
- `domains/order-management/glossary/order-status`
- `domains/order-management/processes/order-cancellation`
- `domains/order-management/rules/order-cancellation-eligibility`

该提案不把 `order-service` 目录、候选 Application 或候选 Bounded Context 视为同义词，也不把 OpenAPI operation 与 Python 方法视为已证明的运行时调用链。

## 主张与证据

| 主张 | 等级 | 证据 | 发布处理 |
|---|---|---|---|
| 实现定义 `Order`、四个 `OrderStatus` 值以及 `OrderService.cancel` | Observed | `src-order-service-py` | 作为 AS-IS 实现事实记录 |
| `cancel` 仅接受 `CREATED`、`PAID`，随后将状态改为 `CANCELLED`；其他枚举状态抛出 `ValueError` | Observed | `src-order-service-py` | 作为 AS-IS 实现事实记录 |
| 测试源码包含 PAID 成功和 SHIPPED 抛错两项断言 | Observed | `test-order-service-py` | 明确标记测试未运行 |
| OpenAPI 声明 `POST /orders/{orderId}/cancel`、200 和 409 | Observed | `contract-openapi` | 只记录声明契约 |
| 测试模块静态导入实现模块 | Derived | Git 固定版本 + 静态 import 阅读 | 不推广为生产调用 |
| API operation 可能由 `OrderService.cancel` 实现 | Inferred | 名称与动作相似 | 保持 unknown，进入 RQ-003 |
| 这些概念可能属于 `order-management` Bounded Context | Inferred | 订单模型、状态、取消接口与测试共同出现 | `draft`，进入 RQ-001 |
| 可取消状态集合可能表达正式业务规则 | Inferred | 实现分支、测试断言、409 契约 | `draft`，进入 RQ-002 |

`Confirmed` 主张：无。

## 反证与缺失

- 没有业务制度、PRD、ADR、owner 或人工确认。
- 没有路由/handler，无法将 OpenAPI 与 Python 方法建立静态调用边。
- 没有 manifest、启动入口或部署定义，无法确认独立 Application 边界。
- 没有 repository、数据库 schema 或迁移，无法判断持久化、并发与事务语义。
- 没有鉴权、幂等、事件或下游调用证据。

## 影响

- 新建 Concept：6 个领域 draft。
- 既有 `verified`：无，不会失效。
- 索引：更新根、领域和系统索引，所有候选项显式标记 `draft`。
- 日志：记录 bootstrap 及人工门禁。
- 反向链接：领域页链接到系统实现页；系统页链接回候选 Context。

## 所需确认者

- 订单领域 owner：确认 Context 边界、术语、规则、例外与状态含义。
- API/应用 owner：确认 Application 边界、路由实现、409 映射、鉴权与持久化。

审核可选结果：`confirmed`、`modified-and-confirmed`、`rejected`、`keep-draft` 或 `needs-more-evidence`。在审核前不得把候选语义晋级为 `stable`。
