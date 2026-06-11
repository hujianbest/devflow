# DevFlow Core Architecture

> 本文定义 DevFlow 从核心理念到 skill 体系的架构映射。任何 skill、command、agent 的修改都应能回溯到 [`devflow-philosophy.md`](devflow-philosophy.md) 的三层质量模型与 human-on-the-loop 协作姿态。

## 1. 架构目标

DevFlow 的目标一句话：**SDD 范式下生成 Clean Code 的代码，而不是仅仅能运行的代码。**

为此架构遵循两条设计原则：

1. **流程最小化**：流程只保留产生质量的部分——阶段产物、人审把关点、TDD 纪律、独立评审。不维护流程状态机、节点路由器或多字段状态文件；进度从工件本身恢复。
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
  devflow-specify/           # 第一层：可测试的规格
  devflow-design/            # 设计：职责边界、接口契约、错误模型、测试设计
  devflow-tdd/               # 第二层：测试先行实现
  devflow-clean-code/        # 第三层：整洁代码标准与重构目录
  devflow-review/            # 独立评审：四类 rubric（spec/design/test/code）
  devflow-fix/               # 缺陷修复：复现 → 根因 → 最小修复
  c-coding-standards/        # 语言扩展：C 规则与惯用法
  cpp-coding-standards/      # 语言扩展：C++ 规则与惯用法
  embedded-development/      # 领域扩展：嵌入式约束
  automotive-development/    # 领域扩展：车载约束
```

两类 skill：

- **阶段 skill**（specify / design / tdd / review / fix）：有工作流、有产物、有人审把关点。
- **叠加 skill**（clean-code、语言、领域）：提供贯穿各阶段的质量约束与判据，被阶段 skill 引用，自身不是阶段。

依赖方向：阶段 skill 可以引用叠加 skill 与 `using-devflow` 的约定；叠加 skill 之间按「通用 → 语言 → 领域」单向引用（如 `cpp-coding-standards` 建立在 `devflow-clean-code` 之上）；不存在反向依赖。

## 4. 工作流与工件

```text
specify → [人审] → design → [人审] → tdd（叠加 clean-code/语言/领域）→ review → [人审] → done
缺陷旁路：fix（复现→根因→边界）→ tdd → review
```

工件模型（`features/<id>-<slug>/`）：

| 工件 | 产出者 | 内容 |
|---|---|---|
| `spec.md` | devflow-specify | 范围、需求条目、验收标准、接口候选契约 |
| `design.md` | devflow-design | 模块职责、接口契约、错误模型、方案取舍、测试设计 |
| `tasks.md` | devflow-tdd | 任务清单与状态（用例 → 任务映射） |
| `fix.md` | devflow-fix | 复现、根因、修复边界（缺陷工作项） |
| `reviews/` | devflow-review | 评审记录（findings + verdict + 抽查记录） |

进度恢复规则在 `using-devflow` 中定义：按工件存在性与确认状态判断下一步，工件优先于聊天记忆。

## 5. 角色分离

- 作者不自审：评审由 `devflow-review` 派发独立 subagent（角色定义 `agents/devflow-reviewer.md`）执行。
- 评审者不动手修：评审产出 findings 与 verdict，修改由作者执行。
- 人做最终把关：规格确认、设计确认、评审 verdict 闭环都需要人。
- DevFlow 不替团队角色拍板业务方向、优先级、验收阈值、架构边界。

## 6. 平台适配

`commands/` 提供 slash-style 阶段入口（thin pointer，不复制 skill 内容）；`docs/guides/opencode-setup.md` 描述 OpenCode 接入。其他 runtime（Claude Code、Cursor 等）只需让其 skill 发现机制指向 `skills/`。平台适配不改变三层质量模型与工作流。

项目级覆盖：组件仓库根目录的 `AGENTS.md` `## Project overrides` 可覆盖工件路径与模板；不创建时使用 `using-devflow` 内置默认值。

## 7. 与 1.x 的关系

1.x 的 13 个 canonical 流程节点、`devflow-router`、`progress.md` 多字段状态、profile/execution-mode 机制在 2.0 中移除——审计结论是它们让流程样板占据了约半数内容，挤压了真正指导设计与编码的部分。1.x 的高价值内容（EARS/QAS/粒度启发式、TDD 纪律、评审 rule 思想）全部保留并强化为带正反例的形式。
