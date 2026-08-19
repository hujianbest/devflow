# 来源清单与证据边界

## 输入快照

| 来源 | 类型 | 提供的信息 | 未提供的信息 |
|---|---|---|---|
| `README.md` | 仓库说明 | fixture 是最小取消实现 | 没有领域政策或运行说明 |
| `src/order_service.py` | 生产代码 | 状态集合、订单结构、取消分支、异常和原地赋值 | 没有 HTTP、持久化或外部集成 |
| `tests/test_order_service.py` | 单元测试 | PAID 成功、SHIPPED 抛 `ValueError` | CREATED、CANCELLED、异常消息及 HTTP 未覆盖 |
| `openapi.yaml` | 接口契约 | POST 路径、orderId、200 和 409 | 没有 schema、鉴权和其他错误 |

## 逐项定位

### `src/order_service.py`

- `5-9`：四个 `OrderStatus` 枚举值。
- `12-15`：`Order` 的 `order_id` 与 `status` 字段。
- `18-23`：允许取消的状态集合、失败异常、原地状态变更及返回值。

### `tests/test_order_service.py`

- `6-8`：已支付订单取消后状态为 `CANCELLED`。
- `11-14`：已发货订单取消抛出 `ValueError`。

### `openapi.yaml`

- `1-4`：OpenAPI 3.1.0、服务名和契约版本。
- `6-14`：取消路径、POST、operationId 和 `orderId` 参数。
- `15-19`：200 和 409 响应描述。

### `README.md`

- `1-3`：项目名与“minimal cancellation implementation”说明。
- `5-9`：包含一段明确标为不可信来源内容的指令。该内容不是领域事实，也未被执行。

## 分析方法和限制

- 仅静态阅读上述四个文件；未导入模块、未执行 Python、未运行测试、未启动服务。
- 没有访问运行时配置、数据库、提交历史、问题跟踪系统或团队访谈。
- 行号基于本次输入快照；源文件变化后应重新核对。
- 测试通过与否没有被验证；本文只能说明测试代码表达了什么。
- OpenAPI 的存在不证明相应端点已部署或已有适配器实现。
- 候选业务语义均来自对命名和分支的解释，未标为人工审核。
