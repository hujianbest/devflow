# 提案模板

文件：`.kb/proposals/<YYYY-MM-DD>-<slug>.md`。`kb.py proposals` 会校验 frontmatter 与声明标注。

```markdown
---
kind: conflict                       # conflict | refine | new | route-error | stale
concepts:                            # 受影响 Concept，相对 knowledge/；kind=new 可为空
  - domains/order-fulfillment/rules/shipped-order-cancel.md
context: order-fulfillment
task: AR042 取消流程重构 · 设计阶段        # 任务标识或一句话
sources:
  - resource: git+https://example/order.git@def456#src/CancelService.java
    role: implementation
  - resource: docs/policies/cancel-2026.md
    role: business-policy
submitted_by: agent:<model>
submitted_at: 2026-09-03T10:00:00Z
---

## 发现

Observed  CancelService 在 def456 起对 status=SHIPPED 且 legacy_b=true 的订单放行取消。
Observed  Concept 正文写"已发货订单原则上不能直接取消"，未提兼容路径。
Inferred  兼容路径可能是业务身份 B 的历史遗留，未见 ADR。

## 建议

- 在 Concept "例外" 节补充 legacy_b 兼容路径，来源指向 def456；
- 是否为正式规则需 Owner 确认；本提案不改变 stable 状态。

## 不确定

- legacy_b 开关是否仍在生产启用（需查配置中心）。
```

## 各 kind 的最小内容

| kind | 必须有 |
|---|---|
| conflict | 双方证据各至少一条 Observed；不写结论 |
| refine | 补充的规则/例外/取舍，及"为什么后续任务会用到" |
| new | 规则/例外本身、来源、适用范围、你是怎么知道的 |
| route-error | 你搜的词、index 把你带去了哪、正确落点是哪、建议改哪个字段 |
| stale | 被推翻的 stable 路径、推翻它的 commit / 契约版本、差异一句话 |

## 不放

试错过程、临时变量、会话摘要、对 Concept 正文的复述、密钥与 PII、内网地址、绝对路径。
