# audit 体检

触发：周期（建议每周），或大批量 ingest / sync 之后。
负责人：知识维护者。

## 脚本部分

`kb.py audit` 写 `.kb/audit/<date>.md`，覆盖：

- 结构：frontmatter 可解析、必填字段、类型 / 状态 / view 合法、文件名、链接、supersession 无环、index 一致；
- 来源：`sources` 非空、git 资源钉 rev、`stable` 的 `verified` 条件、实现细节类型带 `expanded_by`；
- 时效：过 `stale_after` 的 Concept 数；
- 控制面：提案有效性、review-queue 长度、维护锁状态。

`exit 1` 表示有 error。error 转 ingest 修结构；warning 与 stale 转 review。

## 人工或 reviewer 部分

脚本不能判断的，用抽样（每类至少 5 条，高风险 tags 全查）：

| 检查 | 方法 | 不通过时 |
|---|---|---|
| 未标记 Inferred | 读正文，凡无来源却下结论的行 | 补标注或删除；进 review |
| AS-IS / TO-BE / historical 混写 | 对照 `view` 与正文时态、来源角色 | 拆成两个 Concept |
| 同名术语被强制合并 | 同 title 的 Ubiquitous Term 跨 Context 出现只一份 | 拆分并建 Context Relationship |
| 冲突被静默覆盖 | `.kb/conflicts/` 与 Concept 正文对照；log 中 conflict 是否有裁决记录 | 恢复冲突可见 |
| 敏感材料进发布层 | grep 密钥模式、邮箱、内网 URL、绝对路径 | 立即删除并 tombstone 来源 |
| 复利错误 | 抽 Inferred 声明，回溯其来源是否本身是另一条 Inferred | 断链，回 draft |

## 黄金问题回归

`.kb/golden-questions.md` 维护两组问题，每组至少 5 条：

```markdown
## 设计场景（只给 Bundle，不给仓库）
- Q: 已发货订单能否取消？ 期望路径: domains/order-fulfillment/rules/shipped-order-cancel.md 期望标注: stable
- Q: 履约与仓储的边界在哪？ 期望路径: domains/order-fulfillment/relationships/… 期望标注: draft 未确认

## 实现场景（Bundle + 仓库）
- Q: 取消逻辑改哪个模块？ 期望路径: systems/order-core/modules/cancel.md → src/CancelService.java
```

每次 audit 用 `using-domain-knowledge` 的读法走一遍，记录路由准确率、draft 标注覆盖率、错误引用数。

## 度量（写进报告）

| 职责 | 指标 |
|---|---|
| 路由 | 黄金问题 Context 路由准确率；`route-error` 提案数趋势 |
| 约束 | 高风险 draft 被写成策略的拦截数（hooks 日志）；正确拒答率 |
| 出处 | 未标记推断数（目标 0）；无 owner 高风险 Concept 数；机械事实钉 rev 覆盖率 |
| 连续 | 同一矛盾被重复提案的次数；提案到发布时延；合并到知识可用时延；过 stale_after 命中数 |

不作为核心指标：Concept 数量、Markdown 行数、LLM 自评分。

## 产物

- `.kb/audit/<date>.md`（脚本 + 人工部分追加在"人工检查"节）；
- 发现的问题按类型转 ingest 或 review，并在 `log.md` 记一条 `audit`。
