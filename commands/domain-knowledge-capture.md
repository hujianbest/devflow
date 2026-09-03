---
description: 把本次任务中发现的知识矛盾、路由错误、缺失规则、设计取舍或被推翻的 stable 写成 .kb/proposals/ 提案，不修改 knowledge/
---

执行领域知识回写（③ capture）。

1. 加载 `using-domain-knowledge` 技能，读它的"③ 什么必须写回"与 `references/capture-protocol.md`、`references/proposal-template.md`。
2. 逐条核对五类触发：conflict、route-error、new、refine、stale；每条发现标 Observed / Derived / Inferred 并附来源（commit + 路径、契约版本、制度、工单）。
3. 同 kind 合并成一个文件，不同 kind 分文件，写入 `.kb/proposals/<YYYY-MM-DD>-<slug>.md`；不放试错过程、会话摘要、密钥、PII。
4. 不修改 `knowledge/`，不写 `.kb/` 其他目录；提案由 `domain-knowledge-maintain ingest` 处理。
5. 没有合格发现时明确回答"无需回写"，不生成空提案。
