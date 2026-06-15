# DevFlow

[English](README.md) | [中文](README.zh-CN.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Version](https://img.shields.io/badge/version-v2.0.0-blue.svg)
![Core](https://img.shields.io/badge/core-three%20quality%20layers-green.svg)

**一套面向 AI coding agent 的开发流程技能：用 SDD 保证做对的事，用 TDD 证明行为正确，用 Clean Code 保证代码值得长期持有。**

DevFlow 把严谨的 AI 辅助工程工作流打包成自包含 Markdown skills：规格、设计、测试先行实现、独立评审、缺陷修复、工程收尾，以及语言/领域质量叠加约束。

## 项目介绍

DevFlow 是一层可复用的工作流能力，面向在真实软件项目中使用 AI coding agent 的团队。它把工程纪律写成可执行的技能指令，让 agent 能够沿着需求、设计、实现、评审、收尾逐步推进，同时保留人工判断所需要的上下文和证据。

项目在设计上不绑定特定运行时。你可以把它作为独立 skill pack 使用，也可以 vendor 到目标仓库中，或按需适配到支持 Markdown agent instructions 的平台。每个 skill 都保持可阅读、可调整、可组合，便于接入项目自己的约定。

## 项目优势

- **让流程替代 prompt 漂移**：DevFlow 为 agent 提供阶段边界、工件规则和恢复行为，减少从模糊意图直接跳到代码的风险。
- **三层质量约束协同工作**：SDD 明确要做什么，TDD 在实现过程中证明行为正确，Clean Code 保证交付后的代码仍然易读、可维护。
- **内置独立评审门禁**：规格、设计、测试和代码都会经过明确的 review gate，并保留作者隔离与 findings 记录。
- **适配真实项目约束**：语言规范和领域叠加约束让同一套流程可以覆盖后端、前端、嵌入式、车载、安全关键等不同类型的工程工作。

![DevFlow workflow loop](docs/asserts/devflow-2-workflow-loop-v3.png)

---

## 命令

DevFlow 提供 slash-style 阶段入口，作为很薄的平台适配层。真正的流程权威在 `skills/<name>/SKILL.md`；命令只表达意图并加载对应技能。

| 你要做什么 | 命令 | 技能 | 核心原则 |
|------------|------|------|----------|
| 进入或恢复 DevFlow | `/devflow` | `using-devflow` | 从工件恢复 |
| 定义要做什么 | `/devflow-specify` | `devflow-specify` | 先 spec 再代码 |
| 规划怎么做 | `/devflow-design` | `devflow-design` | 先设计再实现 |
| 用测试构建 | `/devflow-build` | `devflow-tdd` | RED -> GREEN -> REFACTOR |
| 评审工件 | `/devflow-review` | `devflow-review` | 作者不自审 |
| 关闭工程工作 | `/devflow-ship` | `devflow-ship` | DoD 通过再 closeout |
| 修复缺陷 | `/devflow-fix` | `devflow-fix` | 先复现再修复 |

`devflow-clean-code`、语言规范和领域规范没有独立命令。它们是质量叠加约束，在设计、实现、评审阶段内部被消费。

---

## 快速开始

把 DevFlow 安装到 OpenCode 的用户级配置目录后，所有项目都可以自动发现这些技能、子 agent 和 slash commands。OpenCode 会分别从 `~/.config/opencode/skills/*/SKILL.md`、`~/.config/opencode/agents/*.md`、`~/.config/opencode/commands/*.md` 加载全局资源；更多细节见 [docs/guides/opencode-setup.md](docs/guides/opencode-setup.md)。

```bash
# 克隆 DevFlow 到 OpenCode 用户配置目录
git clone https://github.com/hujianbest/devflow.git ~/.config/opencode/devflow

# 把全部 DevFlow skills、agents 和 commands 安装到 OpenCode 全局目录
mkdir -p ~/.config/opencode/skills ~/.config/opencode/agents ~/.config/opencode/commands
cp -R ~/.config/opencode/devflow/skills/* ~/.config/opencode/skills/
cp ~/.config/opencode/devflow/agents/*.md ~/.config/opencode/agents/
cp ~/.config/opencode/devflow/commands/devflow*.md ~/.config/opencode/commands/
```

试一下：

```text
使用本仓库的 DevFlow。
我想给 notifications 组件增加重试机制。
先澄清需求，不要直接写代码。
```

项目级覆盖：在目标仓库根目录创建带 `## Project overrides` 章节的 `AGENTS.md`，可覆盖工件路径与模板；不创建时使用内置默认值。

---

## 看它如何工作

```text
You:    使用本仓库的 DevFlow。给 notifications API 增加限流。
        不要直接写代码。

DF:     从 `using-devflow` 进入，确认运行模式，解析目标组件根目录；
        由于没有已批准 spec，路由到 `devflow-specify`。

You:    spec 完成后继续 DevFlow。

DF:     运行独立的 `devflow-review` 门禁。规格通过且运行模式允许继续后，
        `devflow-design` 写组件/工作项设计、接口契约、错误模型和测试设计。

You:    构建已批准的设计。

DF:     `devflow-tdd` 细化 `plan.md`，一次实现一个任务，记录
        RED -> GREEN -> REFACTOR 证据，叠加 `devflow-clean-code`
        和适用语言/领域规范，并把证据行更新到磁盘。

You:    验证并关闭工作。

DF:     `devflow-review` 用独立上下文评审测试和代码。`devflow-ship`
        执行 Definition of Done、promotion 长期文档资产，并写入
        `closeout.md`，等待人工最终确认。
```

工作流启动时 DevFlow 只记录一次运行模式：默认 `attended`，评审 verdict 后停下给人确认；也可以选择 `unattended`，长时间连续执行，但独立评审、记录落盘、critical 阻塞和事后人工审计仍然保留。

---

## 全部 Skills

DevFlow 当前包含 17 个随包发布的 skills：7 个阶段技能、若干质量叠加技能、1 个工具技能。质量叠加技能按约定和 description 发现，后续可以继续扩展，不需要改阶段技能。

### 阶段技能

| Skill | 做什么 | 什么时候用 |
|-------|--------|------------|
| [using-devflow](skills/using-devflow/SKILL.md) | 入口、工作流地图、工件约定、恢复规则、行为准则 | 开始、恢复，或不确定 DevFlow 下一步该做什么 |
| [devflow-specify](skills/devflow-specify/SKILL.md) | 把意图写成可测试规格：EARS、BDD 验收、NFR QAS、追溯矩阵 | 功能/变更需要先明确需求 |
| [devflow-design](skills/devflow-design/SKILL.md) | 产出组件/工作项设计、边界、契约、错误模型、取舍和测试设计 | 规格已批准，需要技术设计 |
| [devflow-tdd](skills/devflow-tdd/SKILL.md) | 用 RED -> GREEN -> REFACTOR 实现，记录任务证据，约束断言强度和 mock 边界 | 设计已批准，进入实现 |
| [devflow-review](skills/devflow-review/SKILL.md) | 独立评审规格、设计、测试或代码，产出 findings 和 verdict | 阶段工件准备过门禁 |
| [devflow-ship](skills/devflow-ship/SKILL.md) | 核验 Definition of Done，promotion 长期资产，写 closeout | 评审闭环，工程工作准备收尾 |
| [devflow-fix](skills/devflow-fix/SKILL.md) | 缺陷处理：复现、根因、最小修复边界、TDD 修复 | 遇到回归、bug、hotfix 或已发布行为缺陷 |

### 质量叠加技能

| Skill | 做什么 | 什么时候用 |
|-------|--------|------------|
| [devflow-clean-code](skills/devflow-clean-code/SKILL.md) | 语言无关的整洁代码标准：命名、函数、控制流、错误处理、注释、重构 | 编写、重构或评审实现代码与测试代码 |
| `<language>-coding-standards` 技能 | 语言级规则、惯用法、工具链纪律与正反例 | 工作触及对应语言的源码、测试或构建脚本；按命名约定发现 |
| `<domain>-development` / 领域开发技能 | 领域特有设计约束、实现红线与验证证据 | 工作项语境命中某领域技能的 description |

### 工具技能

| Skill | 做什么 | 什么时候用 |
|-------|--------|------------|
| [coding-standards-creator](skills/coding-standards-creator/SKILL.md) | 把团队内部编码规范转化为新的 `<language>-coding-standards` skill | 团队需要新增或修订某语言规范 |

语言规范按约定扩展：工作触及语言 X，就加载已存在的 `<x>-coding-standards`。新增语言技能遵循同一份[结构契约](skills/coding-standards-creator/references/coding-standards-skill-contract.md)，所以阶段技能不需要为每种语言改写。领域技能按各自 frontmatter description 触发；新增领域技能只要把适用语境、边界和易混淆场景写清楚，就能作为 Quality Stack 的一部分被消费。

---

## DevFlow 方法

DevFlow 不是 prompt 集合，而是一套轻量、基于证据的工作流，用来让 AI agent 产出可审查、可信、可维护的代码。

| 层 | DevFlow 方法 | 为什么重要 |
|----|--------------|------------|
| Intent | Spec-driven development | 防止 agent 靠猜补全需求 |
| Planning | 组件/工作项设计 | 在代码前显式化边界、契约、错误模型和测试 |
| Execution | Test-driven development | 把“看起来对”变成由测试证明的行为 |
| Internal quality | Clean Code 叠加约束 | 保持代码可读、简单、可维护、可评审 |
| Review | 独立门禁 | 分离作者身份和判断权 |
| Recovery | 工件优先状态 | 让另一个 agent 或人能从文件恢复，而不是依赖聊天记忆 |
| Closeout | DoD 与 promotion | 记录改了什么、通过了什么、哪些文档成为长期资产 |

DevFlow 的协作姿态是 **human-on-the-loop**：AI 做具体工作，人审查关键工件和决策。理念见 [docs/devflow-philosophy.md](docs/devflow-philosophy.md)，架构见 [docs/devflow-core-architecture.md](docs/devflow-core-architecture.md)。

---

## Skills 如何工作

每个 skill 都是自包含操作规程：

```text
SKILL.md
├── 触发条件
├── 工作流步骤
├── 必要工件
├── 证据与评审契约
├── 质量规则与正反例
├── 红旗与合理化陷阱
└── 验证清单
```

关键设计选择：

- **流程最小化。** DevFlow 只保留能产生质量的阶段工件、人审把关点、TDD 纪律和独立评审。
- **内容最大化。** 每个 skill 的主体是工程判断：规则、例子、失败模式、清单和评审 rubric。
- **证据优先于记忆。** 进度从 `plan.md`、`reviews/`、`traceability.md` 和工件文件本身恢复。
- **作者不自审。** 创建工件的 agent 不批准自己的工件。

---

## 项目结构

```text
devflow/
├── skills/                         # 17 个核心 skills
│   ├── using-devflow/              # 入口与恢复规则
│   ├── devflow-specify/            # 可测试规格与追溯矩阵
│   ├── devflow-design/             # 组件/工作项设计
│   ├── devflow-tdd/                # 测试先行实现
│   ├── devflow-review/             # 独立评审门禁
│   ├── devflow-ship/               # DoD、promotion、closeout
│   ├── devflow-fix/                # 缺陷路径
│   ├── devflow-clean-code/         # 语言无关 Clean Code
│   ├── *-coding-standards/         # 语言级叠加约束，按命名约定发现
│   ├── *-development/              # 领域开发叠加约束，按 description 发现
│   └── coding-standards-creator/   # 语言规范生成器
├── commands/                       # slash-style 阶段入口
├── agents/                         # devflow-reviewer / devflow-implementer 子代理角色
├── docs/
│   ├── devflow-philosophy.md
│   ├── devflow-core-architecture.md
│   ├── devflow-internal-quality.md
│   ├── guides/
│   └── asserts/
├── scripts/                        # 仓库一致性检查
├── tests/
├── CONTRIBUTING.md
└── README.md
```

每个工作项的过程工件位于目标组件仓库，默认是 `features/<id>-<slug>/`：`spec.md`、`traceability.md`、`design.md`、`plan.md`、`reviews/`、`closeout.md` 或 `fix.md`。长期资产如 `docs/component-design.md`、`docs/ar-specs/`、`docs/ar-designs/` 在 `devflow-ship` 阶段 promotion。

---

## 范围边界

DevFlow 覆盖从已接受需求到完成评审与 closeout 的工程开发段。它不负责产品发现、发布运维、系统/集成/验收测试、线上事故管理或生产 rollout；也不替团队拍板业务方向、优先级、验收阈值和架构边界。

---

## 贡献

见 [CONTRIBUTING.md](CONTRIBUTING.md)。请保持 skills 具体、可验证、带正反例，并尽量减少流程样板。

---

## License

[MIT](LICENSE)
