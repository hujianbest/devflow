# 人工审核队列

## RQ-001：确认领域边界

- 优先级：高
- 决策：`order-management` 是否是恰当的 Bounded Context；订单取消是否属于该 Context，还是更大/更小或相邻模型的一部分。
- 证据：`Order`、`OrderStatus`、取消方法、取消 API 契约和测试场景。
- 反证/限制：只有一个窄 fixture；没有组织、数据所有权、事务边界或相邻系统证据。
- 影响：Bounded Context、所有术语、能力、流程和规则的 `context` 归属。
- 选项：确认；修改边界/名称；拒绝并暂不建立 Context；要求更多仓库或业务材料。
- 所需角色：订单领域 owner。

## RQ-002：确认取消规则与业务语义

- 优先级：高
- 决策：`CREATED`、`PAID` 可取消以及 `SHIPPED`、`CANCELLED` 不可取消，是否为正式规则；是否存在例外、权限、退款或副作用。
- 证据：实现中的允许集合与状态赋值；两个静态测试场景；OpenAPI 的 200/409 描述。
- 反证/限制：没有业务政策；测试未运行；没有退款、库存、支付或履约集成；实现异常没有状态细节。
- 影响：业务规则、流程、术语定义及 Agent 后续编码建议。
- 选项：确认原规则；补充例外后确认；仅保留为实现事实；拒绝；要求更多证据。
- 所需角色：订单业务 owner；涉及付款后取消时还应由支付/财务责任人复核。

## RQ-003：确认接口、实现和所有权

- 优先级：中
- 决策：`cancelOrder` 是否路由到 `OrderService.cancel`，`ValueError` 是否映射为 HTTP 409，以及鉴权、幂等、持久化、事务和 owner。
- 证据：OpenAPI 与 Python 方法具有相近名称和取消语义。
- 反证/限制：没有 handler、router、manifest、启动入口、持久层、配置或 CODEOWNERS。
- 影响：Application 边界、API 使用说明、实现链路和生产可用性判断。
- 选项：提供实现入口/部署仓库；确认当前 fixture 仅为示例；指定 owner；保持 unknown。
- 所需角色：API 或应用 owner。

## 审核记录要求

每项决策必须记录 `human:<actor>`、时间、职责范围、采用的证据和结果。未完成审核前，相关领域 Concept 保持 `draft`。
