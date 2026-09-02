---
description: 按风险为指定模块或 Context 深化领域知识 Bundle，生成 API Endpoint、Event Channel、Data Model、Configuration 级 Concept；需显式 scope
---

执行领域知识深化。

1. 读取 `domain-knowledge-library/domain-knowledge-expand/SKILL.md` 与 `references/expand-workflow.md`。
2. 要求具体 scope 与 reason；scope 为"全部"或缺失时停止询问。
3. 取锁 `kb.py lock expand`；按事故半径、资金权限、变更频率、跨 Context 密度排序，超上限先给清单让用户裁。
4. 从真源提取 Observed 指针写入 `systems/<app>/{interfaces,events,data-models,configurations}/`，frontmatter 带 `expanded_by: domain-knowledge-expand`、`status: draft`；不复制契约、DDL、生产配置值；更新对应骨架页入口清单为链接。
5. `kb.py validate --check-index`、`kb.py index`、`kb.py log expand "<scope>"`、`kb.py unlock`，报告未深化对象与原因。
