---
name: using-devflow
description: DevFlow 工作流的入口。在以下情况使用：开始一个新的开发任务、不确定当前该做规格/设计/实现中的哪一步、需要从已有工件恢复进度、或用户提到 DevFlow / 规范驱动开发 / 高质量开发流程时。
---

# 使用 DevFlow

## DevFlow 是什么

DevFlow 把「产出高质量代码」拆成由外到内的三层质量。第一、二层有阶段技能承载；第三层是贯穿设计、实现、评审的质量约束：

| 层 | 回答的问题 | 失败模式（无此层时） | 承载技能 |
|---|---|---|---|
| **第一层 SDD** | 做的是不是对的事？ | 需求含糊 → 模型靠猜 → 做错了事 | `devflow-specify` |
| **第二层 TDD** | 功能被证明正确了吗？ | 代码未验证 → 留一堆 BUG 给人 | `devflow-tdd` |
| **第三层 Clean Code** | 代码本身写得好吗？ | 能跑但烂 → 难维护、难审查、难演进 | `devflow-clean-code` + `<language>-coding-standards` + 领域技能 |

前两层保证外部质量（做对的事、做对），第三层保证内在质量（做好）。`devflow-design` 是设计阶段：它通过结构、接口契约、错误模型和测试设计为第三层奠基；实现和评审时仍必须叠加 `devflow-clean-code` 与适用语言/领域技能。三层不是三个产物，而是同一份代码的三个维度。目标一句话：**SDD 范式下生成 Clean Code 的代码，而不是仅仅能运行的代码。**

协作姿态是 **human-on-the-loop**：具体的活由 AI 干，人站在环上审查关键产物（规格、设计、测试、代码）。因此每个阶段的产物都必须**可冷读、可审查**——这是所有技能共同的硬要求。

## 工作流

```text
需求/任务到达 ──→ [0] 确认运行模式（见下）
    |
    v
[1] devflow-specify     写 spec.md + plan.md 骨架 + 初始化 traceability.md
    |
[R1] devflow-review     独立评审规格 → 记录到 reviews/ ──[人工确认]──
    v
[2] devflow-design      影响组件边界时先修订 component-design-draft.md；
    |                   写 design.md：职责、接口契约、错误模型、测试设计
[R2] devflow-review     独立评审设计 → 记录到 reviews/ ──[人工确认]──
    v
[3] devflow-tdd         细化 plan.md 任务计划；按测试设计逐用例
    |                   RED→GREEN→REFACTOR；默认逐任务派发 implementer
    |                   subagent；plan.md 记进度与证据行；叠加
    |                   devflow-clean-code 与适用语言/领域规范技能
[R3] devflow-review     独立评审测试与代码 → 记录到 reviews/ ──[人工确认]──
    v
[4] devflow-ship        DoD 核验 + 追溯终验 + promotion 长期资产 + closeout
    |                   ── 人确认关闭 ──
    v
完成
```

**评审是必经节点，不是可选预审**：每个阶段产物完成后必须经 `devflow-review` 独立评审并把记录写入 `reviews/`，评审通过（且按运行模式获得人工确认）之前不进入下一阶段。跳过任何一个 R 节点直接进入下一阶段，都是流程违规。

### 运行模式（工作流启动时确认一次）

启动工作流时**先问用户一次**：「每个评审节点之后是否需要人工确认？」并把答案记入 plan.md 头部：

| 模式 | 行为 |
|---|---|
| `attended`（默认） | 每个 R 节点后停下，把评审记录与 verdict 呈给人，人同意后才进入下一阶段 |
| `unattended` | R 节点后不停顿连续执行，便于长时间运行 |

**`unattended` 只移除人工停顿，不移除任何质量动作**：独立评审照做、评审记录照写、critical findings 照样阻塞（返工修复并复审，而不是带病推进）、DoD 照核验。所有评审记录留存在 `reviews/`，供人事后统一审计。用户未明确回答时按 `attended` 执行；模式记录后，恢复执行的会话沿用 plan.md 中的模式，不重新猜测。

旁路：**缺陷修复**走 `devflow-fix`（复现 → 根因 → 最小修复），其中修复实现仍回到 TDD（先写复现缺陷的失败测试），修复后的测试与代码同样经 R3 评审，收尾同样经 `devflow-ship`。

阶段允许回溯：写测试时发现规格漏洞就回去补规格；实现时发现设计错误就回去改设计。回溯时更新对应工件并让受影响的评审重新进行，不要让代码与工件漂移。

### 何时可以裁剪

- **微小修改**（几行、无接口变化、风险低）：spec 可压缩成 plan.md 里的一段验收标准，design 可省略（R1/R2 随之合并入 R3），但 TDD、R3 评审与 clean code 不裁剪。
- **纯重构**（行为不变）：不需要 spec/design，但必须有覆盖现有行为的测试先行，且代码评审（R3）照做。
- 拿不准时不裁剪。裁剪的是**文档量**，永远不是**质量门槛**（测试先行、证据行、独立评审与记录、人工确认（attended 模式）、DoD 核验、整洁标准）。微小修改的 DoD 裁剪规则见 `devflow-ship` 的 Definition of Done。

## 工件约定

每个工作项一个目录（`AR<id>`/`DTS<id>`/`CHANGE<id>` 或团队等价编号）：

```text
features/<id>-<slug>/
  spec.md                     # 规格（devflow-specify 产出）
  traceability.md             # 追溯矩阵：spec-design-code 一致性约束（specify 初始化，逐阶段补列）
  component-design-draft.md   # 组件级设计修订（影响组件边界时，devflow-design 产出）
  design.md                   # 工作项级设计（devflow-design 产出）
  plan.md                     # 执行计划：运行模式、阶段门禁状态、任务拆解与证据行；
                              #   中断恢复的单一入口（specify 建骨架，tdd 细化并维护）
  reviews/                    # 评审记录：每轮一份，findings + resolution 闭环（devflow-review 产出）
  closeout.md                 # 收尾记录（devflow-ship 产出）
```

长期资产在 `docs/`（`component-design.md`、`ar-specs/`、`ar-designs/`），由 `devflow-ship` 在收尾时从过程工件 promotion，平时各阶段只读。

恢复进度时**先读 `plan.md`**（运行模式 + 阶段门禁状态 + 当前任务），再按工件状态校验，不依赖聊天记忆：

| 磁盘状态 | 下一步 |
|---|---|
| 目录不存在 / spec.md 缺失 | `devflow-specify`（启动时确认运行模式） |
| spec.md 存在，reviews/ 无通过的 spec 评审（或 attended 下未获人工确认） | `devflow-review`（R1）/ 呈人确认 |
| spec 门禁通过，design.md 缺失（含组件边界受影响但组件设计未修订） | `devflow-design` |
| design.md 存在，reviews/ 无通过的 design 评审（或未获人工确认） | `devflow-review`（R2）/ 呈人确认 |
| design 门禁通过，plan.md 有未完成任务 | `devflow-tdd`（从 plan.md 第一个未完成任务继续） |
| 任务全部完成，reviews/ 缺测试或代码评审（或未获人工确认） | `devflow-review`（R3）/ 呈人确认 |
| 评审有未闭环 findings | 按 findings 返工对应阶段，修复后更新评审记录的 resolution |
| 全部门禁通过，closeout.md 缺失 | `devflow-ship` |

工件与聊天记忆冲突时，以工件为准。项目根 `AGENTS.md` 可以覆盖路径与模板约定。

## 行为准则

适用于所有 DevFlow 技能，不可协商：

1. **不默默补全模糊需求。** 实现任何非平凡内容前显式列出假设，请人确认或写入 spec。最常见的失败是做错假设并在未经检查下继续推进。
2. **困惑时停下，不猜。** 遇到冲突需求、不一致工件、缺失阈值：指出具体困惑，提出澄清问题或交回对应负责人。
3. **方案有问题就说。** 不当 yes-machine：直接指出问题、量化缺点、给替代方案；对方知情后仍坚持则执行。
4. **强制简单。** 完成前自问：能用更少代码吗？抽象配得上它引入的复杂度吗？资深工程师会不会说「为什么不直接……」？
5. **范围纪律。** 只改任务要求改的。路过的问题登记，不顺手修；不删不理解的代码；不在 spec 外加功能。
6. **验证，而非声称。** 「看起来对」永远不够。完成的依据是通过的测试、构建输出、评审记录。
7. **作者不自审，阶段必评审。** 每个阶段产物完成后必须经独立上下文（subagent 或新会话）评审并落盘记录；attended 模式下人工确认后才进入下一阶段，unattended 模式下评审与记录照做、critical 照样阻塞。

## 技能地图

| 技能 | 一句话 | 何时读 |
|---|---|---|
| `devflow-specify` | 把意图写成可测试的规格 | 开始新工作项、规格被评审打回 |
| `devflow-design` | 做出值得长期持有的软件设计；为第三层奠定结构、契约、错误模型和测试设计 | 规格确认后、设计被打回、实现中发现设计问题 |
| `devflow-tdd` | 用 RED→GREEN→REFACTOR 证明功能正确 | 设计确认后的全部实现期 |
| `devflow-clean-code` | 把代码写整洁：命名、函数、错误处理、重构 | 写代码、REFACTOR 与代码评审时必读 |
| `devflow-review` | 独立评审规格/设计/测试/代码 | 每个阶段产物完成后 |
| `devflow-ship` | DoD 核验、promotion 长期资产、closeout | 评审闭环后的收尾 |
| `devflow-fix` | 复现 → 根因 → 最小修复 | 缺陷、回归、线上问题 |
| `<language>-coding-standards` | 语言级规则与惯用法（现有 `c-coding-standards`、`cpp-coding-standards`） | 工作项含对应语言的代码 |
| `embedded-development` | 嵌入式领域约束（内存/中断/实时性/资源） | 嵌入式工作项 |
| `automotive-development` | 车载领域约束（ASIL/SOA/诊断/整车生命周期） | 车载工作项 |
| `coding-standards-creator` | 把团队编码规范转化为新的语言规范技能 | 需要新建或修订某语言的 coding-standards 时 |

语言与领域技能是**叠加约束**：它们在规格、设计、实现、评审各阶段被对应技能引用，自身不是流程阶段。

**语言规范的发现按命名约定**：工作项触及语言 X 的代码 → 叠加 `<x>-coding-standards`（存在时）。约定让新增语言（如 `java-coding-standards`、`python-coding-standards`）无需改动任何阶段技能即可接入；技能尚不存在而团队有该语言规范时，用 `coding-standards-creator` 生成。所有语言技能遵循同一份结构契约（`coding-standards-creator/references/coding-standards-skill-contract.md`）。
