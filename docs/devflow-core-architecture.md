# DevFlow Core Architecture

> 本文定义 DevFlow 从核心理念到 skill 体系的架构映射。任何 skill、command、agent 的修改都应能回溯到 [`devflow-philosophy.md`](devflow-philosophy.md) 的三层质量模型与 human-on-the-loop 协作姿态。

## 1. 架构目标

DevFlow 的目标一句话：**SDD 范式下生成 Clean Code 的代码，而不是仅仅能运行的代码。**

为此架构遵循两条设计原则：

1. **流程最小化**：流程只保留产生质量的部分——阶段产物、人审把关点、TDD 纪律、独立评审。不维护额外节点路由器或多字段状态文件；进度从 `plan.md`、`reviews/` 与工件本身恢复。
2. **内容最大化**：每个 skill 的主体是可操作的工程判断（规则 + 正反例 + 自检清单），而不是流程样板。skill 写法遵循 progressive disclosure：frontmatter 描述触发条件，SKILL.md 承载核心判断，references/ 承载详表与模板。

## 2. 三层质量模型到 Skill 的映射

| 层 | 目标 | 承载 |
|---|---|---|
| 第一层 SDD | 意图正确：做对的事 | `devflow-specify`（EARS / BDD 验收 / QAS / Change Type 基线 / 粒度） |
| 第二层 TDD | 功能正确：证明做对 | `devflow-design` 的测试设计章节 + `devflow-tdd`（RED→GREEN→REFACTOR + 测试质量） |
| 第三层 Clean Code | 内在质量：写得好、值得长期持有 | `devflow-design`（结构/契约/错误模型）+ `devflow-clean-code`（命名/函数/控制流/重构）+ 语言/领域扩展 |

第三层不是流程阶段，而是贯穿设计、实现、评审的质量标准。`devflow-review` 在每层出口处提供独立检验，人做最终把关。

## 3. Skill 体系

```text
skills/
  using-devflow/             # 入口：三层模型、工作流、工件约定、行为准则
  devflow-specify/           # 第一层：可测试的规格 + 追溯矩阵初始化
  devflow-design/            # 设计：组件级 + 工作项级两级设计，含企业模板与质量增补章节
  devflow-tdd/               # 第二层：测试先行实现（默认派发 implementer subagent，证据行落盘）
  devflow-clean-code/        # 第三层：整洁代码标准与重构目录
  devflow-review/            # 独立评审：四类 rubric（spec/design/test/code）
  devflow-ship/              # 收尾：DoD 核验 + promotion 长期资产 + closeout
  devflow-fix/               # 缺陷修复：复现 → 根因 → 最小修复
  c-coding-standards/        # 语言扩展：C 规则与惯用法
  cpp-coding-standards/      # 语言扩展：C++ 规则与惯用法
  coding-standards-creator/  # 工具：把团队编码规范转化为新的 <language>-coding-standards
  embedded-development/      # 领域扩展：嵌入式约束
  automotive-coding-standards/    # 领域扩展：车载约束
```

三类 skill：

- **阶段 skill**（specify / design / tdd / review / ship / fix）：有工作流、有产物、有人审把关点。
- **叠加 skill**（clean-code、语言、领域）：提供贯穿各阶段的质量约束与判据，被阶段 skill 引用，自身不是阶段。
- **工具 skill**（coding-standards-creator）：生成与维护扩展技能本身，不参与工作项流程。

依赖方向：阶段 skill 可以引用叠加 skill 与 `using-devflow` 的约定；叠加 skill 之间按「通用 → 语言 → 领域」单向引用（如 `cpp-coding-standards` 建立在 `devflow-clean-code` 之上）；不存在反向依赖。

### 语言规范的扩展机制

语言规范按 `<language>-coding-standards` 命名约定接入（现有 c/cpp，规划 java/python 等）。扩展性由三件事保证：

1. **约定式引用**：所有阶段 skill、rubric、DoD、命令只写「适用的 `<language>-coding-standards`」，不枚举具体语言——新增语言零改动接入。
2. **结构契约**：每个语言技能满足同一份契约（`coding-standards-creator/references/coding-standards-skill-contract.md`）：命名、frontmatter 触发条件、只收语言级规则的边界、规则三要素（可判定 + 事故类 + 正反例）、规模上限、消费点、evals。
3. **生成工具**：`coding-standards-creator` 把团队内部编码规范文档转化为符合契约的新技能：逐条归属判定（语言级收录 / 通用引用 clean-code / 领域移交 / 流程剔除）、规则提炼改写、接入注册、交人验收。

## 4. 工作流与工件

```text
specify → R1 review → design → R2 review → tdd（叠加 clean-code/语言/领域）→ R3 review
   ↑          │          ↑          │          ↑                                     │
   └ rework ──┘          └ rework ──┘          └──── R3 rework: fix findings + re-review
        → ship（DoD 核验 + promotion）→ [人确认关闭] → done
缺陷旁路：fix（复现→根因→边界）→ tdd → R3 review ↔ tdd rework → ship
```

每个 R 节点 = `devflow-review` 独立评审 + 落盘记录（findings + resolution 闭环），是必经门禁。门禁状态存在 `plan.md`：`pending` 表示等待评审，`rework` 表示先回作者阶段修 findings，`passed` 表示可进入下一阶段。运行模式在工作流启动时确认一次并记入 plan.md：`attended`（默认，评审通过后可呈人确认）/ `unattended`（连续执行；评审、记录、critical 阻塞照常，人事后审计 `reviews/`）。

工件模型（默认位于目标组件仓库根目录下的 `features/<id>-<slug>/`；团队可在组件根 `AGENTS.md` 覆盖等价路径）：

| 工件 | 产出者 | 内容 |
|---|---|---|
| `spec.md` | devflow-specify | 范围、需求条目、验收标准、接口候选契约 |
| `traceability.md` | specify 初始化，design/tdd 补列 | 追溯矩阵：需求→设计→测试→代码→证据，spec-design-code 一致性约束 |
| `component-design-draft.md` | devflow-design | 组件级设计修订（影响组件边界时；企业模板） |
| `design.md` | devflow-design | 工作项级设计：职责、接口契约、错误模型、测试设计、质量增补章节 |
| `plan.md` | specify 建骨架，tdd 细化并维护 | 组件根、工件根、运行模式、门禁状态表、自包含任务拆解（用例锚点/精确路径/步骤/完成定义）+ 每任务 RED/GREEN 证据行；中断恢复的单一入口 |
| `fix.md` | devflow-fix | 复现、根因、修复边界（缺陷工作项） |
| `reviews/` | devflow-review | 每轮一份评审记录（findings 含 Resolution 列 + verdict + 抽查记录 + 人工确认） |
| `closeout.md` | devflow-ship | DoD 核验摘要、promotion 路径表、债务去向 |

长期资产（默认位于同一组件根下的 `docs/`）：`component-design.md`、`ar-specs/`、`ar-designs/`。由 `devflow-ship` 在收尾时从过程工件 promotion：保留原 spec/design/component-design 模板主体，只清理 Open Questions、过程笔记和评审应答；其他阶段只读。组件级设计是团队开发流程要求：影响组件边界的工作项必须先修订组件设计并经模块架构师确认。

进度恢复规则在 `using-devflow` 中定义：按工件存在性与确认状态判断下一步，工件优先于聊天记忆。

## 5. 角色分离

- 作者不自审：评审由 `devflow-review` 派发独立 subagent（角色定义 `agents/devflow-reviewer.md`）执行。
- 评审者不动手修：评审产出 findings 与 verdict，修改由作者执行。
- 实现默认隔离：`devflow-tdd` 在 runtime 支持时逐任务派发全新上下文的 implementer subagent（角色定义 `agents/devflow-implementer.md`），输入为打包的 Context Pack 而非聊天历史，防止长会话上下文漂移。
- 人做最终把关：规格确认、设计确认、评审 verdict 闭环、DoD 核验后的关闭都需要人。
- DevFlow 不替团队角色拍板业务方向、优先级、验收阈值、架构边界。

## 6. 平台适配

`commands/` 提供 slash-style 阶段入口（thin pointer，不复制 skill 内容）；`docs/guides/opencode-setup.md` 描述 OpenCode 接入。其他 runtime（Claude Code、Cursor 等）只需让其 skill 发现机制指向 `skills/`。平台适配不改变三层质量模型与工作流。

项目级覆盖：组件仓库根目录的 `AGENTS.md` `## Project overrides` 可覆盖工件路径与模板；不创建时使用 `using-devflow` 内置默认值。路径覆盖只改变组件根内的相对工件位置，不应把工件写到 DevFlow skill 仓库或上级工作区根。

## 7. 与 1.x 的关系

1.x 的 13 个 canonical 流程节点、`devflow-router`、`progress.md` 多字段状态、handoff YAML、profile/execution-mode 机制在 2.0 中移除——审计结论是它们让流程样板占据了约半数内容，挤压了真正指导设计与编码的部分。1.x 的高价值内容（EARS/QAS/粒度启发式、TDD 纪律、评审 rule 思想）全部保留并强化为带正反例的形式。

1.x 中以下**能力**经讨论确认必要后，以最小流程表面积恢复（不恢复其 1.x 样板形态）：收尾与 promotion（`devflow-ship`，含 Definition of Done）、组件级设计与两份企业模板（并入 `devflow-design`，模板增补质量章节）、追溯矩阵（`traceability.md`）、TDD 证据纪律（plan.md 证据行替代 evidence/ 目录）、implementer subagent（`devflow-tdd` 默认执行模式）。
