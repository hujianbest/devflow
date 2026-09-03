---
description: 领域知识入口——按 index → overview → Concept → 原文读团队知识 Bundle，正确标注 draft，回答业务语义、系统落点与规则例外
---

读领域知识 Bundle 回答问题或支撑当前任务。

1. 加载 `using-domain-knowledge` 技能及需要的 references。
2. 定位 Bundle（`DOMAIN_KB_ROOT` → `.domain-kb` → `domain-kb/` → 当前仓库）；没有则明说，不假装读过。
3. 按四层披露读：根 `knowledge/index.md` → 领域 / 系统 overview → 少量 Concept → 原文；Design Agent 与 Coding Agent 走各自路径。
4. `draft` 必须标"未确认"并给路径；`deprecated` 不参与默认回答；`to-be` 不与现状混答；高风险 draft 只当候选；冲突、过期、证据不足时拒答或找 owner。
5. 任务结束前按 ③ capture 检查是否需要写 `.kb/proposals/` 提案（可用 `/domain-knowledge-capture`）；不直接改 `knowledge/`。
