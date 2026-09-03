---
description: 从已归档 DevFlow change 中提炼一条有证据、可检索且已校验的工程经验
---

执行 DevFlow 知识沉淀。

1. 加载 `devflow-learn` 技能及本次任务需要的直接 references。
2. 解析唯一模式：`capture`、`lookup`、`report-only`、`refresh-audit` 或
   `refresh-apply`；冲突或不明确时询问。
3. capture 严格执行捕获门槛、claim/evidence grounding、重叠判断、敏感信息检查、
   单文档与 store 校验和只读复核。
4. lookup 与 refresh-audit 只读；refresh-apply 只处理用户批准且 digest 未漂移的
   write set。
5. 一次 capture 只创建或更新一条 learning；不修改 canonical、archive、产品代码或测试。
