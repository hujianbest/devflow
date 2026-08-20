# DevFlow Commands

DevFlow 的 slash-style 阶段入口，属于平台适配层。每个 command 只做一件事：声明用户意图属于哪个阶段，并把对应技能加载进上下文。**仓库内判据与步骤的唯一权威是 `coding-skills/<name>/SKILL.md`，command 不复制其内容。**

| Command | 阶段 | 对应技能 |
|---|---|---|
| [`/devflow`](devflow.md) | 入口 / 恢复进度 | `using-devflow` |
| [`/devflow-init`](devflow-init.md) | 既有组件基线初始化 | `devflow-init` |
| [`/devflow-specify`](devflow-specify.md) | 写 SRS 与 delta spec | `devflow-specify` |
| [`/devflow-design`](devflow-design.md) | 写 delta design | `devflow-design` |
| [`/devflow-build`](devflow-build.md) | TDD 实现 | `devflow-tdd`（默认派发 implementer subagent；叠加 `devflow-clean-code` 与语言/领域技能） |
| [`/devflow-review`](devflow-review.md) | 独立评审 | `devflow-review` |
| [`/devflow-ship`](devflow-ship.md) | 收尾 | `devflow-ship`（DoD + canonical sync + closeout + archive） |
| [`/devflow-fix`](devflow-fix.md) | 缺陷修复 | `devflow-fix` |
| [`/devflow-learn`](devflow-learn.md) | 知识沉淀 | `devflow-learn`（仅处理已归档 change，不属于交付 gate） |

领域 wiki command 是另一组入口，权威在 `domain-knowledge-library/<name>/SKILL.md`，不进入交付阶段表：

| Command | 做什么 | 对应技能 |
|---|---|---|
| [`/domain-knowledge-init`](domain-knowledge-init.md) | 全仓首版编译 | `domain-knowledge-init` |
| [`/domain-knowledge-update`](domain-knowledge-update.md) | 外科更新或补全覆盖 | `domain-knowledge-update` |
| [`/domain-knowledge-query`](domain-knowledge-query.md) | 先读 index 再作答 | `domain-knowledge-query` |
| [`/domain-knowledge-ingest`](domain-knowledge-ingest.md) | 摄入一份原文 | `domain-knowledge-ingest` |
| [`/domain-knowledge-lint`](domain-knowledge-lint.md) | 结构巡检 | `domain-knowledge-lint` |

所有 command 共同遵守 `using-devflow` 的行为准则：工件优先、暴露假设、范围纪律、验证而非声称、作者不自审。`devflow-clean-code` 与语言/领域技能不设独立 command——它们在设计、实现、评审内部被消费；`devflow-learn` 是 Ship 之后的可选工具，不改变交付结果。

