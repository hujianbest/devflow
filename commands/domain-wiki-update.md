---
description: 按 git 增量外科更新领域 wiki；补全覆盖时走 completeness pass，无相关变化且已是 complete 时可 no-op
---

更新领域 wiki。

1. 读取 `domain-wiki-skills/domain-wiki-update/SKILL.md` 及其直接 references。
2. 先读现有 wiki 和 `.last-update.json`，用有界 git 窗口做 impact plan。
3. 有内容变化则 `status=complete`；无相关源变化则 no-op。不写评审报告。不要把构建产物或导出文档树当源或模板。
