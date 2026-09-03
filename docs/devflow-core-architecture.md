# DevFlow Core Architecture

> 本文定义 DevFlow 从核心理念到 skill、工件和角色的架构映射。字段、状态、路径与归档规则见 [`delivery-contract.md`](../skills/using-devflow/references/delivery-contract.md)。

## 1. 架构目标

DevFlow 的目标是：**在 SDD 范式下生成 Clean Code，而不是仅仅能运行的代码。**

架构遵循三条原则：

1. **当前真相唯一**：组件当前规格与设计分别只有 `specs/spec.md`、`specs/design.md` 两份 canonical 文档。
2. **变更与历史分离**：活动 AR 位于 `specs/changes/`，完成后整体移动到 `specs/archive/`；canonical 文档不保存重复的按 AR 副本。
3. **内容质量优先**：流程只保留可测试需求、TDD、独立评审、追溯和 DoD 等能产生质量的动作。

## 2. 三层质量模型

| 层 | 目标 | 主要承载 |
|---|---|---|
| SDD | 意图正确：做对的事 | `devflow-init`、`devflow-specify`、R1 |
| TDD | 功能正确：证明做对 | `devflow-design` 测试设计、`devflow-tdd`、R3 |
| Clean Code | 内在质量：值得长期持有 | `devflow-design`、`devflow-clean-code`、语言/领域扩展、R3 |

`devflow-review` 在阶段出口提供独立判断；人负责业务、架构和最终归档确认。人要能审查，前提是文档可以冷读，`devflow-clean-doc` 在 R1、R2 和 canonical diff 确认之前约束文档表达，但不改变规范语义。

## 3. Skill 体系

```text
skills/
  using-devflow/             # 入口、baseline preflight、恢复与工件契约
  devflow-init/              # 既有组件缺基线时，从代码逆向建立 canonical 文档
  devflow-specify/           # srs + delta-spec + traceability 初始化
  devflow-design/            # 工程设计、delta 变换契约与测试设计
  devflow-tdd/               # tasks 驱动的 RED→GREEN→REFACTOR
  devflow-review/            # R1/R2/R3 与 canonical sync 独立评审
  devflow-ship/              # DoD、Agent 智能同步、closeout、archive
  devflow-fix/               # 缺陷复现、根因与最小修复
  devflow-learn/             # archive 之后的可选知识沉淀
  devflow-clean-code/        # 通用整洁代码约束
  devflow-clean-doc/         # 面向中文的交付文档可读性约束
  *-coding-standards/        # 语言扩展
  *-development/             # 领域扩展
  coding-standards-creator/  # 语言规范生成工具
```

`devflow-init` 是进入常规阶段前的基线初始化能力，不是每个工作项都经过的阶段。`devflow-learn` 是 Ship 之后的可选工具，不是生命周期节点或 gate。叠加 skill 提供质量判据，不独立改变生命周期。

## 4. 组件工件模型

```text
<component-root>/
└─ specs/
   ├─ spec.md
   ├─ design.md
   ├─ changes/
   │  └─ ARXXX-<topic>/
   │     ├─ change.json
   │     ├─ srs.md
   │     ├─ delta-spec.md
   │     ├─ delta-design.md
   │     ├─ tasks.md
   │     ├─ traceability.md
   │     ├─ reviews/
   │     └─ closeout.md
   └─ archive/
      └─ YYYY-MM-DD-ARXXX-<topic>/
```

| 工件 | 职责 |
|---|---|
| `specs/spec.md` | 当前组件行为规格的唯一真相 |
| `specs/design.md` | 当前组件设计的唯一真相 |
| `change.json` | 身份、`componentMode`、profile、artifact、门禁与 base revision |
| `srs.md` | 本 AR 的来源、范围和增量需求 |
| `delta-spec.md` | 对当前组件规格的增量意图 |
| `delta-design.md` | 对当前组件设计的增量意图和测试设计 |
| `tasks.md` | 自包含任务、TDD 进度、证据和返工队列 |
| `traceability.md` | SRS→spec→design/case→task→code/test→evidence |
| `reviews/` | 独立评审的 findings、Resolution 与 verdict |
| `closeout.md` | DoD、canonical diff、债务、确认和归档摘要 |

工件拓扑是封闭集合：canonical、活动变更和归档都直接位于组件根的 `specs/` 下，不接受替代根、路径别名或额外工件层。

## 5. Baseline Preflight

开始或恢复工作时先创建或读取 `change.json`：

- `componentMode: existing`：`specs/spec.md` 与 `specs/design.md` 必须同时存在且为 `baseline-ready`；否则只允许进入 `devflow-init`。
- `componentMode: new`：不执行 init；首次 delta 可从空基线创建两份 canonical 文档。
- 模式缺失、与代码现状冲突或无法判断：向人澄清，不自行推断。

`devflow-init` 坚持 **澄清而不臆造**。它只读分析代码、测试、接口、配置和构建资料；每项结论必须是可验证事实、人工确认事实或显式 unknown。阻塞 unknown 未闭合时不能标记 `baseline-ready`。

## 6. 常规工作流

```text
specify → R1 → design → R2 → tdd → R3 → ship
   ↑       │       ↑       │      ↑      │
   └rework─┘       └rework─┘      └rework┘

缺陷：fix → R1/R2（验证 delta 或 N/A）→ tdd → R3 → ship

可选反馈环：archive → learn → 后续 change 开工前按需检索
```

门禁状态只存在 `change.json`；任务状态和 RED/GREEN/REFACTOR 证据只存在 `tasks.md`。恢复时先读 `change.json` 确定阶段，再读 `tasks.md` 确定任务断点，并用 `reviews/` 校验状态没有漂移。

运行模式分为 `attended` 和 `unattended`。后者只移除阶段间人工停顿，不移除独立评审、critical 阻塞、记录或最终人工确认。

## 7. Canonical Sync 与 Archive

`devflow-ship` 采用 Agent 驱动的智能同步：

1. 核验 tasks、R1/R2/R3、Resolution、traceability 和 DoD。
2. 主控 Agent 同时读取 SRS、两份 delta 和两份 canonical 文档。
3. 按规格稳定 ID、组件设计章节/实体键和增量操作直接编辑 canonical，保留未涉及内容；有变化的文档先进入 draft。
4. 对歧义或 base revision 后的并行变化先澄清。
5. 展示 canonical Git diff，派独立 reviewer 检查语义保留与 spec-design 一致性。
6. 人确认后把实际修改的 canonical 恢复为 baseline-ready，写实并核验 closeout。
7. closeout gate 通过后，将 AR 整体移动到日期前缀的 archive 目录。

DevFlow 不提供“警告后继续”、跳过 sync 或带未完成任务归档。同步使用普通文件编辑，Git diff 与历史负责审计、冲突发现和恢复；禁止破坏性 reset。

## 8. 知识反馈环

`devflow-learn` 只从已经完成 gate 并归档的 change 提取非平凡经验，写入仓库级
`docs/learnings/`。知识库按问题解决、设计决策和工程实践分类；Markdown frontmatter
提供稳定 ID、组件、来源、状态、敏感级别和检索标签。

Learning 的权威级别低于当前 canonical、代码和测试。`using-devflow` 在目标组件与主题
明确后执行有界 grep-first 检索，只读取至多五份强匹配的 `active` 文档；截断时必须
收窄查询，冲突时使用当前真相并产生 refresh 候选。每条 learning 用 claim/evidence
关系区分 archive 历史事实、当前行为与工程指导，机械校验 locator，独立 reviewer
逐 claim 核对语义。Refresh 的只读审计与批准后 apply 分权，并用 digest 和 write set
限制修改范围。知识捕获不回写 archive，不增加交付 gate，失败时也不改变 Ship 结果。

## 9. 角色分离

- **主控 Agent**：编排阶段、维护 `change.json`、执行 canonical sync 和目录归档。
- **implementer**：只执行一个 tasks 任务并返回证据，不改变门禁或归档。
- **reviewer**：只读评审 SRS/delta、测试、代码或 canonical diff，不修复。
- **人**：确认业务事实、架构边界、关键评审结果和最终归档。

作者不自审，评审者不动手修，人做最终把关。

## 10. 平台适配

`commands/` 是 thin pointer，仓库内权威步骤位于 `skills/`。安装时可以复制到运行时约定的 skills root；OpenCode、Cursor 等运行时只需发现 skills、commands 与 agents，并具备读取、编辑和移动文件的能力。

组件根 `AGENTS.md` 可以增加项目约束和模板要求，但不能把 canonical、changes 或 archive 移出固定的 `specs/` 契约。
