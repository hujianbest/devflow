---
description: 维护领域知识 Bundle——bootstrap 冷启动、ingest 摄入材料与提案、sync 跟随代码失效、review 整理审核晋级、audit 周期体检
---

执行领域知识维护。

1. 读取 `domain-knowledge-library/domain-knowledge-maintain/SKILL.md`，按本次模式再读对应 reference；知识形态以 `references/bundle-contract.md` 为唯一权威。
2. 解析唯一模式：`bootstrap`、`ingest`、`sync`、`review` 或 `audit`；不明确时询问，非交互环境不猜成会写 `knowledge/` 的模式。
3. 定位 Bundle（无则 `kb.py init`），取维护锁 `kb.py lock <mode>`；锁被持有则 blocked。
4. 按模式执行；写时编译，不复制权威源；业务语义只发 `draft`，冲突写 `.kb/conflicts/` 不选边；任何模式不批量生成 API / 表 / 配置页。
5. 结束前 `kb.py index`、`kb.py validate --check-index`、`kb.py log <mode> "<title>"`、`kb.py unlock`，并按 SKILL 的完成输出报告唯一终止状态。
