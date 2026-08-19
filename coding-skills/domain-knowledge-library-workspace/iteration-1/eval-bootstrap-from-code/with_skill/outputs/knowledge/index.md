# Order Service 团队领域知识库

本 Bundle 基于固定 Git 版本进行静态冷启动。`draft` 表示尚未完成相应机器核对或人工语义确认；任何业务规则、领域边界或生产行为都不得仅凭本库执行外部写操作。

## 使用入口

- [分析范围与证据边界](references/analysis-scope.md)（draft）- 基线、来源角色、静态分析限制和可信状态。
- [Order Service 系统实现地图](systems/order-service/index.md) - 源码模块、声明 API 与数据模型。
- [订单管理候选领域](domains/order-management/index.md)（draft）- 候选 Context、术语、能力、流程和规则。

## 当前可信状态

- 当前实现事实：可追溯到 Python 源码固定版本。
- 声明契约事实：可追溯到 OpenAPI 3.1.0 文档；未证明生产实现一致。
- 测试事实：只确认测试源码包含指定断言；测试未运行。
- 候选业务语义：全部为 `Inferred`，`Confirmed` 数量为 0，等待人工门禁。

## 控制面

来源登记、提案、盘点、冲突和审核队列位于 `.kb/`，不属于已确认业务结论。
