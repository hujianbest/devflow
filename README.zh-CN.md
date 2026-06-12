# DevFlow

[English](README.md) | [中文](README.zh-CN.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Version](https://img.shields.io/badge/version-v2.0.0-blue.svg)
![Core](https://img.shields.io/badge/core-three%20quality%20layers-green.svg)

**一套面向 AI coding agent 的开发流程技能（skills），目标一句话：SDD 范式下生成 Clean Code 的代码，而不是仅仅能运行的代码。**

AI 编码的默认路径是从一句含糊的需求直接跳到代码，稳定地产出三类失败：做错了事（需求靠猜）、做得不对（代码没验证）、做得不好（能跑但烂）。DevFlow 用由外到内的三层质量模型对抗这三类失败：

| 层 | 回答的问题 | 承载技能 |
|---|---|---|
| **第一层 SDD（规范驱动）** | 做的是不是对的事？ | `devflow-specify` |
| **第二层 TDD（测试驱动）** | 功能被证明正确了吗？ | `devflow-tdd` |
| **第三层 Clean Code** | 代码本身写得好吗？ | `devflow-design` + `devflow-clean-code` |

协作姿态是 **human-on-the-loop**：具体的活由 AI 干，人站在环上审查关键产物（规格、设计、测试、代码）。理念详见 [`docs/devflow-philosophy.md`](docs/devflow-philosophy.md)，架构见 [`docs/devflow-core-architecture.md`](docs/devflow-core-architecture.md)。

## 设计取向

DevFlow 2.0 遵循两条原则（也是与常见"流程框架"的区别）：

- **流程最小化**：只保留产生质量的流程——阶段产物、人审把关点、TDD 纪律、独立评审。没有状态机、没有路由器、没有多字段状态文件；进度从磁盘工件恢复。
- **内容最大化**：每个技能的主体是可操作的工程判断——规则、正反例代码、合理化话术的反驳、自检清单——而不是流程样板。

## 工作流

```text
specify ──review──> design ──review──> tdd 实现 ──review──> ship ──[人确认]──> 完成
   写可测试规格        组件级+工作项级设计：      逐用例             DoD 核验、
   plan 骨架与         接口契约/错误模型/        RED→GREEN→         promotion
   追溯矩阵            测试设计                 REFACTOR            长期资产
缺陷旁路：fix（复现 → 根因 → 最小修复）→ tdd → review → ship
```

每个阶段产物完成后都经 `devflow-review` 独立评审并落盘记录（必经门禁）。工作流启动时确认一次**运行模式**：`attended`（默认，每个评审后人工确认再继续）或 `unattended`（连续执行，便于长时间运行——但独立评审、记录落盘、critical 阻塞照常，人事后统一审计 `reviews/`）。

每个工作项的过程工件（`features/<id>-<slug>/`）：`spec.md`、`traceability.md`、`design.md`（影响组件边界时另有 `component-design-draft.md`）、`plan.md`（运行模式、门禁状态、自包含任务拆解与证据行——中断恢复的单一入口）、`reviews/`（每轮评审记录，findings + resolution 闭环）、`closeout.md`（缺陷工作项为 `fix.md`）。长期资产（`docs/component-design.md`、`docs/ar-specs/`、`docs/ar-designs/`）由 ship 阶段沉淀。下一步永远从工件状态恢复，不依赖聊天记忆。

## 技能目录

### 阶段技能

| 技能 | 做什么 |
|---|---|
| [`using-devflow`](skills/using-devflow/SKILL.md) | 入口：三层模型、工作流地图、工件约定、行为准则 |
| [`devflow-specify`](skills/devflow-specify/SKILL.md) | 把意图写成可测试规格：EARS 句式、BDD 验收、NFR QAS、变更基线 |
| [`devflow-design`](skills/devflow-design/SKILL.md) | 两级软件设计（组件级 + 工作项级，企业模板 + 质量增补章节）：职责边界、耦合判断、抽象纪律、接口契约、错误模型、测试设计 |
| [`devflow-tdd`](skills/devflow-tdd/SKILL.md) | 测试先行实现：RED→GREEN→REFACTOR、断言强度、mock 边界；默认逐任务派发 implementer subagent，证据行落盘 |
| [`devflow-review`](skills/devflow-review/SKILL.md) | 独立评审：规格/设计/测试/代码四类 rubric，作者永不自审 |
| [`devflow-ship`](skills/devflow-ship/SKILL.md) | 收尾：Definition of Done 核验、promotion 长期资产、closeout |
| [`devflow-fix`](skills/devflow-fix/SKILL.md) | 缺陷修复：复现 → 根因三层 → 最小修复边界 → TDD 修复 |

### 叠加技能（贯穿各阶段的质量约束）

| 技能 | 做什么 |
|---|---|
| [`devflow-clean-code`](skills/devflow-clean-code/SKILL.md) | 整洁代码标准：命名、函数、控制流、错误处理、注释、重构目录（含 before/after） |
| [`c-coding-standards`](skills/c-coding-standards/SKILL.md) | C 规则：指针所有权、内存与资源、缓冲区、整数、宏、头文件 |
| [`cpp-coding-standards`](skills/cpp-coding-standards/SKILL.md) | C++ 规则：RAII、所有权签名、类设计、错误策略、模板纪律、ABI |
| [`embedded-development`](skills/embedded-development/SKILL.md) | 嵌入式约束：内存、中断、实时性、硬件边界、证据策略 |
| [`automotive-development`](skills/automotive-development/SKILL.md) | 车载约束：ASIL、整车生命周期、SOA、DTC、SELinux、跨 ECU |

语言规范按 `<language>-coding-standards` 命名约定扩展（规划中：java、python 等）：各阶段技能以约定方式引用，新增语言零改动接入；所有语言技能遵循同一份[结构契约](skills/coding-standards-creator/references/coding-standards-skill-contract.md)。

### 工具技能

| 技能 | 做什么 |
|---|---|
| [`coding-standards-creator`](skills/coding-standards-creator/SKILL.md) | 把团队内部编码规范文档转化为新的 `<language>-coding-standards` 技能：归属判定（语言级/通用/领域/流程）、规则提炼（可判定 + 事故类 + 正反例）、接入注册、交人验收 |

## 快速开始

OpenCode 会自动发现 `skills/` 下的每个 `SKILL.md`（详见 [`docs/guides/opencode-setup.md`](docs/guides/opencode-setup.md)）；其他支持 Agent Skills 的 runtime（Claude Code、Cursor 等）同理。

```bash
# 方案 A：旁路 skill pack
git clone https://github.com/hujianbest/devflow.git ~/devflow
cd /path/to/your-repo && ln -s ~/devflow/skills .opencode-skills

# 方案 B：vendor 进仓库
git subtree add --prefix .devflow https://github.com/hujianbest/devflow.git --squash main
```

试一下：

```text
用 DevFlow 开发：为通知组件增加重试机制。先把需求理清楚，不要直接写代码。
```

也可以使用 [`commands/`](commands/README.md) 下的 slash-style 阶段入口：`/devflow`、`/devflow-specify`、`/devflow-design`、`/devflow-build`、`/devflow-review`、`/devflow-ship`、`/devflow-fix`。

项目级覆盖：在你的仓库根目录创建带 `## Project overrides` 章节的 `AGENTS.md`，可覆盖工件路径与模板；不创建时使用内置默认值。

## 项目结构

```text
devflow/
├── skills/            # 7 个阶段技能 + 5 个叠加技能 + 1 个工具技能（见上表）
├── commands/          # slash-style 阶段入口（平台适配层）
├── agents/            # devflow-reviewer / devflow-implementer 子代理角色定义
├── docs/
│   ├── devflow-philosophy.md         # 核心理念（北极星）
│   ├── devflow-core-architecture.md  # 架构映射
│   └── guides/opencode-setup.md
├── scripts/           # 仓库一致性检查
└── tests/
```

## 范围边界

DevFlow 覆盖从已接受的需求到完成评审的工程开发段。它不负责产品发现、发布运维、系统/集成/验收测试和线上事故管理；也不替团队角色拍板业务方向、优先级、验收阈值与架构边界——这些决策属于人。

## 贡献

见 [CONTRIBUTING.md](CONTRIBUTING.md)。请保持技能具体、可验证、带正反例，流程样板最小化。

## License

[MIT](LICENSE)
