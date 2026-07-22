---
description: DevFlow 既有组件基线初始化——只读逆向并建立或补齐 specs/spec.md 与 specs/design.md
---

为既有组件执行 DevFlow canonical baseline 初始化。

1. 读取 `skills/using-devflow/SKILL.md`，先解析唯一 `<component-root>` 并执行 component mode preflight。模式缺失、冲突或不确定时询问，不猜。
2. `componentMode: new` 时停止本命令：不创建空 canonical 文档，路由首个 AR 通过 delta 建立首版 baseline。只有 `componentMode: existing` 继续。
3. 读取 `skills/devflow-init/SKILL.md` 及其直接 references，遵守硬规则“澄清而不臆造”。
4. 固定不可变 source revision，只读分析源码、测试、API/IDL、配置、构建、部署和既有说明；不修改业务代码、测试、生成物、锁文件或运行环境。
5. 检查 `<component-root>/specs/spec.md` 与 `<component-root>/specs/design.md`。两份都缺时生成两份；仅缺一份时只补该份，并与已有文档交叉校验；已有 baseline-ready 文档不静默重写。
6. 将每项事实分类为 `verifiable`、`human-confirmed` 或 `unknown`，保留 `/` 路径证据与 provenance。不把实现等同需求，不虚构意图、理由、错误语义、阈值或历史决策。
7. 对影响契约、验收或架构边界的 unknown 保持阻塞，展示证据与影响并提出最小澄清问题。
8. 用 canonical 模板起草文档，初始保持 `baselineStatus: draft`；执行 spec-design 一致性检查。
9. 派发独立 reviewer 检查来源、推断越界、unknown 分级和交叉一致性。有活动 AR 时把完整记录写入其 `reviews/baseline-init-review-YYYY-MM-DD[-rN].md` 并由 canonical/change.json 引用；reviewer 通过后向人展示文档、provenance、findings resolution 与剩余 non-blocking unknown。
10. 只有人明确确认后才把本次生成或补齐的文档标记 `baseline-ready`。若由活动 AR 路由而来，重新核验文件后更新该 AR `change.json` 的 canonical artifact 状态与 `baselinePreflight`，绝不改写 `baseRevision`。
11. 报告创建、保持不变和阻塞的文件，reviewer verdict、人工确认、preflight 结果及未解决问题。无法实际写入或复核文件时，不宣称初始化完成。
