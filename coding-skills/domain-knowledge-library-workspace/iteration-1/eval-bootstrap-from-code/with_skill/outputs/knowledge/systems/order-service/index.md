# Order Service 系统实现地图

- [devflow 仓库中的 fixture 范围](repository.md)（draft）- 说明来源范围与仓库边界。
- [Order Service 候选 Application](overview.md)（draft）- 汇总声明接口、实现模块、数据模型和未知运行边界。
- [src.order_service 模块](modules/order-service-module.md)（draft）- Python 符号与静态实现关系。
- [POST /orders/{orderId}/cancel](interfaces/cancel-order.md)（draft）- OpenAPI 声明的取消接口。
- [Order 与 OrderStatus](data-models/order.md)（draft）- 内存 dataclass 与状态枚举。

## 未发现

- Event Channel：未发现消息契约、生产者或消费者。
- Configuration：除作为契约文件的 `openapi.yaml` 外，未发现运行配置或环境变量样例。
- Build/deployment：未发现 manifest、lockfile、启动入口、容器或部署文件。
- Persistence：未发现数据库 schema、迁移或 repository。

“未发现”仅适用于当前四个文件的静态范围，不等于生产系统不存在这些资产。
