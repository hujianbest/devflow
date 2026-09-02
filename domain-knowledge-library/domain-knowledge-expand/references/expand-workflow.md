# expand 工作流

## 选择对象

在 scope 内按下面顺序打分排序，只深化排在前面的、且数量在上限内的：

| 优先级 | 信号 | 从哪看 |
|---|---|---|
| 1 事故半径 | 不可逆数据变更、对外契约、资金流转 | 契约文件、迁移、tags 含 payment |
| 2 资金 / 权限 | 鉴权、限额、审批、发布开关 | tags 含 security / permission / release |
| 3 变更频率 | 近 12 月 commit 次数 | `git log --since=12.months -- <path>` |
| 4 跨 Context 密度 | 被多个 Context 调用或监听 | Context Relationship 页、消费者清单 |

不按仓库清单顺序扫平；不因为"反正都要做"而超出 scope。

## 四类模板

frontmatter 共用 bundle-contract.md 第 2 节；`type` 取以下之一，`context` 用 `system:<app>`，必带 `expanded_by: domain-knowledge-expand`。

### API Endpoint（`systems/<app>/interfaces/<method>-<path-slug>.md`）

```markdown
# <METHOD> <path>

## 契约指针
Observed  `api/openapi.yaml#/paths/...`（git+…@rev）

## 实现指针
Observed  `src/.../Controller.java#method`

## 调用方
Derived   <Context / 系统>（依据：客户端代码 / 网关配置）

## 业务含义
Inferred  对应 domains/<ctx>/processes/<p>.md 的第 n 步

## 改动影响
Derived   影响 <Context 列表>；破坏性变更需通知 <owner>
```

### Event Channel（`systems/<app>/events/<topic-slug>.md`）

```markdown
# <topic>

## 契约指针
Observed  `asyncapi.yaml#/channels/...` 或 schema registry 主题版本

## 生产者 / 消费者
Derived   …

## 领域事件
Inferred  对应 domains/<ctx>/events/<e>.md

## 语义
- 至少一次 / 顺序 / 幂等键（只写来源指向的事实）
```

### Data Model（`systems/<app>/data-models/<table-slug>.md`）

```markdown
# <table>

## 结构指针
Observed  `db/migrations/V12__...sql`（不复制 DDL）

## 所有权
Derived   仅 <模块> 写入；<模块列表> 读取

## 关键字段的业务含义
Inferred  status 枚举对应 domains/<ctx>/glossary/order-status.md

## 变更影响
Derived   迁移涉及 <表 / 服务>
```

### Configuration（`systems/<app>/configurations/<key-slug>.md`）

```markdown
# <key>

## 声明指针
Observed  `config/features.yaml#<key>`（不写当前生产值）

## 影响的行为
Observed  代码读取位置 …

## 关联规则
Inferred  domains/<ctx>/rules/<r>.md 的例外由此开关控制

## 生产值
- 去配置中心查；Bundle 不镜像
```

## 更新入口清单

在对应 Application / Module 页的入口清单里，把纯文本项替换为链接：

```markdown
Observed  HTTP 契约：`api/openapi.yaml`（git+…@rev）→ 详见 `interfaces/post-orders-id-cancel.md`（用 Markdown 链接）
```

## 退出条件

- scope 内排名在上限内的对象都有 Concept；
- 每条 Concept 至少一条 Observed 指针指向真源并钉 rev；
- `kb.py validate --check-index` 通过；
- 未深化对象列在完成输出里，附原因。
