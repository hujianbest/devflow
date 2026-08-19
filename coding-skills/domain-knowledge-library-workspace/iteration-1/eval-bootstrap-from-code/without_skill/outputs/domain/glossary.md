# 领域词汇表

## 已由实现或契约使用的术语

| 术语 | 当前可证实定义 | 类型 | 证据 |
|---|---|---|---|
| Order / 订单 | 一个包含 `order_id` 和 `status` 两个字段的数据对象 | 实现事实 | `src/order_service.py:12-15` |
| order_id / orderId | Python 对象中的字符串字段；HTTP 路径中的必填字符串参数。输入未证明两者的映射实现 | 实现事实 | `src/order_service.py:13-15`; `openapi.yaml:6,9-14` |
| OrderStatus / 订单状态 | 字符串枚举，值为 `CREATED`、`PAID`、`SHIPPED`、`CANCELLED` | 实现事实 | `src/order_service.py:5-9` |
| cancel / cancelOrder / 取消订单 | 服务方法接收一个 `Order`，在允许状态下将其状态改为 `CANCELLED`；契约声明一个对应名称的 HTTP 操作 | 实现事实 | `src/order_service.py:18-23`; `openapi.yaml:6-8` |
| current state / 当前状态 | HTTP 409 描述和异常消息中用于解释不可取消的状态条件 | 实现事实（措辞） | `src/order_service.py:20-21`; `openapi.yaml:18-19` |

## 候选业务语义

以下内容没有被输入材料确认：

| 候选解释 | 可能用途 | 状态 |
|---|---|---|
| `CREATED` 表示订单已建立但未支付 | 解释为何它可取消 | 候选业务语义，待产品/领域专家确认 |
| `PAID` 表示已完成收款 | 解释取消后是否需要退款 | 候选业务语义，待支付负责人确认 |
| `SHIPPED` 表示货物已交运，因此应改走退货流程 | 解释为何不能取消 | 候选业务语义，输入中没有退货能力 |
| `CANCELLED` 是终态 | 推导后续状态约束 | 候选业务语义；当前实现只证明再次取消会失败 |
| “取消”由客户发起 | 定义权限、审计与通知 | 候选业务语义；也可能由客服、系统或商家发起 |

## 需要统一的命名

- Python 使用 `order_id`，OpenAPI 使用 `orderId`。这是常见的语言风格差异，但未发现序列化或路由绑定代码。
- 方法名为 `cancel`，HTTP `operationId` 为 `cancelOrder`。两者看似对应，但输入没有调用链证明。
- 不应把 `ValueError` 当作领域术语；它只是当前实现采用的通用异常类型。
