# review 审核晋级

审核决定 `draft → stable` 与冲突裁决。它不决定能否被读到：`draft` 发布即可检索。

触发：`.kb/review-queue/` 非空；周期性会审。
负责人：领域 Owner；高风险类别强制 Owner 本人。本技能负责整理与记录，不代替 Owner 决定。

## 默认策略

| 内容 | 策略 | verified 要求 |
|---|---|---|
| API 路径、方法签名、Topic、数据模型、模块依赖 | 机器验证后可 `stable` | `tool:<name>` |
| 候选业务术语、Bounded Context 边界、业务规则与例外、历史兼容原因 | draft 先发布；人工审核后 `stable` | `human:<id>` |
| 安全、资金、权限、发布规则（tags 命中 `config.yaml.review.high_risk_tags`） | draft 可引用为候选；当作可执行策略前 Owner 本人 | `human:<owner>` |
| 代码与文档冲突 | 不自动选边。代码说明 AS-IS，文档说明意图；Owner 判断漂移 / 兼容 / 未完成迁移 | 裁决结果写入 Concept 与 conflicts |

机器验证的边界：import 不证明运行时调用；静态调用图不证明路径执行；测试通过只证明该版本该用例；OpenAPI 只证明声明。`tool:` 验证只能覆盖它真正检查过的字段。

## Review Pack

给 Owner（或先给 `domain-knowledge-reviewer`）的材料，一个队列项一份：

```markdown
# Review Pack: <concept path>

- 队列项: .kb/review-queue/<file>
- 来由: bootstrap 候选 | ingest replace | ingest conflict | sync 语义变化 | capture route-error | capture stale
- 当前 status / view / owner
- 声明清单（逐条带 Observed/Derived/Confirmed/Inferred 与来源）
- 冲突（若有）：AS-IS 证据 · 意图证据 · 可能解释
- 相关 Concept：同名术语、上下游、被替代项
- 建议动作：确认 | 否决 | 修改，及理由
- 需要 Owner 回答的最小问题
```

不把整份 Bundle 或整个仓库塞给 reviewer；只放声明引用的短摘录。

## Owner 的三个动作

| 动作 | 写入 |
|---|---|
| 确认 | `verified` 追加 `{by: human:<id>, at}`；`status: stable`；`stale_after` 按 `config.yaml.freshness` 设置 |
| 否决 | 写原因到正文"审核记录"；`draft` 直接删除或 `deprecated` + `superseded_by`（若有替代） |
| 修改 | 改正文；`generated` 保留；`verified` 只记本次确认过的范围；重新 `kb.py validate` |

每个动作追加 `log.md`：`## [date] review | <concept> <动作> by <id>`。队列项处理后移到 `.kb/review-queue/done/`。

## 独立复核

有独立上下文能力时，先派 `domain-knowledge-reviewer`（只读）对 Review Pack 逐声明返回 `verified / contradicted / unverifiable`，再交 Owner。reviewer 不改文件、不运行命令；它的结论附在 Review Pack 末尾。没有独立上下文时，由主控按同一 rubric 执行并注明"独立复核缺失"。

## 停止条件

- 无 owner 的高风险 Concept：不静默，写进 audit 指标，`owner: unassigned` 并在 index 可见；
- Owner 要求跳过验证直接 `stable`：拒绝，说明 `kb.py validate` 会失败；
- 同等级来源冲突 Owner 不裁决：保持 conflict 可见，不合并。
