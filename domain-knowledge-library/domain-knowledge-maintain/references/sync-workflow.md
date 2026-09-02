# sync 跟代码同步

触发：Git 合并事件，或手动给出 commit range。
负责人：CI 或知识维护者。

## 步骤

```text
1 取 diff：git diff --name-status <from>..<to>
2 按下表把每个变更文件映射到失效对象
3 找到 sources[].resource 指向这些路径的 Concept（grep "resource: git+…#<path>"）
4 对每个受影响 Concept：
    - 仅路径 / 注释 / 格式变化 → 更新 resource 的 @rev，其余不动
    - 语义变化 → 清除 verified，status 回 draft，正文加"自 <rev> 起需重新确认"，进 review-queue
    - 来源文件被删除 → 移除该来源；若无来源剩余，写明"来源已删除"，status 回 draft
    - 重命名 → 更新 resource，正文加别名
5 LLM 摘要只在其证据集合变化时重新生成
6 kb.py validate --check-index；kb.py index；log.md
7 记录本次 range 到 .kb/bootstrap-state.yaml 的 repositories[].rev
```

## 变更到失效范围

| 变更 | 失效对象 | 默认判定 |
|---|---|---|
| 普通源码 | 引用该文件的 Concept | 语义变化需人判断；默认只更新 rev 并标"待核" |
| 公共签名或类型 | 反向引用与依赖模块 | 语义变化 |
| 构建配置 | 对应 workspace 的骨架页 | 更新 rev |
| manifest、lockfile | 依赖闭包与相关索引 | 更新 rev |
| OpenAPI、AsyncAPI、proto、schema | 契约、实现和消费者关系 | 语义变化 |
| 迁移、ORM | Data Model 与表引用 | 语义变化 |
| 测试 | 测试证据与行为观察 | 更新 rev；断言变化视为语义变化 |
| 删除、重命名 | tombstone、别名和失效链接 | 见步骤 4 |
| CODEOWNERS | owner 与审核路由 | 更新 owner |
| 状态机、枚举、开关名 | Business Rule / Process 中引用它们的行 | 语义变化 |

判断"语义变化"时，只看 diff 里是否触及被 Concept 正文明确引用的符号、字段、枚举值、Topic、路径。不猜测未引用部分的影响。

## 全量对账

每 N 次增量或每月一次，用同一 SHA 重跑 `kb.py inventory` 并与骨架页对照：模块列表、入口清单、契约文件是否一致。不一致率超过 `config.yaml` 阈值（默认 5%）时停止增量，进入人工核对。

## 不做

- 不把生产实时配置或运行状态写成长期事实；
- 不因为测试全绿就把 `draft` 升 `stable`；
- 不在 sync 中新建业务语义 Concept（那是 ingest 或 bootstrap）。

## CI 接法

```yaml
# 示例：合并到 main 后
- run: python3 <skill-dir>/scripts/kb.py --bundle $DOMAIN_KB_ROOT lock sync --holder ci
- run: <agent-cli> "/domain-knowledge-maintain sync --from $BEFORE --to $AFTER --repo order-core"
- run: python3 <skill-dir>/scripts/kb.py --bundle $DOMAIN_KB_ROOT validate --check-index
- run: python3 <skill-dir>/scripts/kb.py --bundle $DOMAIN_KB_ROOT unlock
```

同步延迟（合并到知识可用）是运行指标，记在 `.kb/audit/` 报告里。
