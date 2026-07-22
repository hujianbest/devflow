---
name: using-devflow
description: DevFlow 交付工作流入口。开始或恢复变更、判断规格/设计/实现/评审/归档下一步、处理缺失组件基线，或用户提到 DevFlow、规范驱动开发、AR 交付时使用。每次入口都先执行组件模式与 canonical baseline preflight。
---

# 使用 DevFlow

DevFlow 维护两类真相：

- `specs/spec.md` 与 `specs/design.md` 是组件当前规格和当前设计的唯一 canonical baseline。
- `specs/changes/ARXXX-<topic>/` 只记录一次变更的增量、任务、证据和评审；关闭后完整移动到 `specs/archive/`。

工件拓扑是封闭集合。只接受下述目录和文件名，不解析路径别名、不允许路径覆盖，也不在组件根与 `specs/` 之间插入工件层。

## 每个入口必须执行 baseline preflight

开始、恢复、规格、设计、实现、缺陷修复、评审、同步和归档前，都先执行以下检查。`devflow-init` 也从同一判定开始，只是它是既有组件基线不合格时的修复入口。

1. **解析组件根。** 用户给出目录时以该目录为准；否则用仓库约定识别目标组件。目标仍不唯一就询问，不在当前工作目录猜测。
2. **定位变更。** 新 AR 创建 `specs/changes/ARXXX-<topic>/` 与可解析的 `change.json`；续作先读 `change.json`，再核对磁盘工件。没有明确 AR 的独立初始化可暂不创建变更目录。
3. **确认组件模式。** `change.json.componentMode` 必须是 `new` 或 `existing`。字段缺失、人与仓库证据冲突或无法判断时立即阻塞并询问；不得根据“目录存在”“有一些代码”等单一信号自行推断。
4. **检查既有组件。** `existing` 要求 `specs/spec.md` 和 `specs/design.md` 同时存在，且两份文档都明确标记 `baselineStatus: baseline-ready`。任一缺失、仍为 draft、缺 provenance、独立评审未通过、人工未确认或有 blocking unknown，均把 `change.json.gates.baselinePreflight.status` 记为 `blocked`，停止后续阶段并路由 `devflow-init`。
5. **检查新增组件。** `new` 不运行 `devflow-init`。canonical 文档可以不存在；首个 `delta-spec.md` 与 `delta-design.md` 必须完整到能从空基线生成首版 `specs/spec.md` 与 `specs/design.md`。若仓库证据显示这可能是既有组件，先询问。
6. **记录结果。** 有活动变更时，只在上述事实可核后更新 `change.json.gates.baselinePreflight`。不能读取或写入必需工件时保持阻塞，不在聊天里宣称通过。

canonical 文档的 `baseline-ready` 不是文件存在的同义词。它表示 provenance 完整、影响契约或架构边界的 unknown 已关闭、独立 reviewer 已通过且人已最终确认。

## 交付结构与状态

[交付结构契约](references/delivery-contract.md) 是路径、字段、状态枚举和归档不变量的唯一权威；使用 [change.json 模板](references/change-template.json) 创建 manifest。

- `change.json` 保存身份、模式、不可变 `baseRevision`、profile、artifact graph、门禁和归档状态。
- `tasks.md` 只保存任务、依赖和 RED/GREEN/REFACTOR 证据。
- `reviews/` 保存评审事实与 Resolution；gate 只在对应记录闭环后更新。

恢复时先读 `change.json`，再核对磁盘工件和评审记录。两者冲突或下一步不唯一时阻塞并展示差异；聊天记忆不参与状态裁决。

## 风险 profile

创建变更时，根据范围、接口、数据、并发、安全、部署和可逆性选择 profile，并把证据化理由写入 `change.json.profile`。参考 [风险 profiles](references/risk-profiles.md)。

profile 只增加审查深度、领域 reviewer 和证据，不得删除：

- baseline preflight；
- `srs.md`、两份 delta、`tasks.md`、`traceability.md`；
- R1、R2、R3 独立评审；
- canonical sync diff 与独立复核；
- 人工确认、DoD 和硬归档门禁。

profile 无法可靠选择且选择会改变所需 reviewer 或证据时，列出触发信号并请人确认。

## 生命周期

```text
baseline preflight
  → devflow-specify: srs.md + delta-spec.md + traceability.md
  → R1 独立规格评审
  → devflow-design: delta-design.md
  → R2 独立设计评审
  → devflow-tdd: tasks.md + RED/GREEN/REFACTOR 证据
  → R3 独立测试与代码评审
  → canonical sync: 智能合并两份 delta
  → 独立 sync reviewer
  → 人确认 canonical diff
  → closeout.md + 完整归档
```

### 阶段边界

- `srs.md`：本 AR 的来源、目标、范围、非范围和增量需求。
- `delta-spec.md`：相对 `specs/spec.md` 的规格操作；`new` 的首次变更以空基线解释。
- `delta-design.md`：相对 `specs/design.md` 的设计操作；由已确认的 delta spec 驱动。
- delta spec 使用规格稳定 ID；delta design 使用组件模板章节路径、功能编号、接口/软件
  单元实体键和 base 摘要。两者都使用稳定 operation ID 与 `ADDED`、`MODIFIED`、
  `REMOVED`、`RENAMED`，并声明前置语义和结果，禁止用整篇替换掩盖删除。
- `traceability.md`：需求条目 → Spec Section → Design Section/Case → Task → Code/Test → Evidence。
- `tasks.md`：仅任务和实现证据。
- `reviews/`：R1、R2、R3、复审与 canonical sync 复核记录。
- `closeout.md`：DoD、同步摘要、遗留债务、人工确认和最终归档路径。

### Gate 语义

`change.json.gates.*.status` 只使用：

| 状态 | 含义 | 下一步 |
|---|---|---|
| `pending` | 前置条件未齐或尚未评审 | 完成声明的前置工件或发起对应评审 |
| `blocked` | 缺事实、工具能力、基线或人工决策 | 解决明确 blocker；不得越过 |
| `rework` | reviewer 已给出未闭环 findings | 回责任阶段修复并写 Resolution，再复审 |
| `passed` | 必需记录与确认均满足 | 进入依赖该 gate 的下一节点 |

`attended` 在 reviewer 通过后停下让人确认；`unattended` 可连续执行到必须由人决定的点。两种模式都保留独立评审、记录、critical blocker、canonical diff 人工确认和归档确认。运行模式只记录在 `change.json`。

### 回溯

- R1 rework 回 `devflow-specify`。
- R2 rework 回 `devflow-design`；若根因是规格缺口，先回规格并重开受影响 gate。
- R3 rework 回 `devflow-tdd`；若代码暴露规格或设计错误，先修正 delta 并重开受影响 gate。
- reviewer 不在评审上下文中替作者修改产物。作者修复后逐条回填 Resolution，再由独立上下文复审。
- 同一 gate 自动返工三轮仍未通过，停止并把剩余 findings、证据和需要的专家决策交给人。

## Canonical sync 与归档

R1、R2、R3、追溯和 DoD 闭环后，读取 `devflow-ship` 及其
`sync-archive-protocol.md`。该协议唯一负责并行变化预检、语义同步、canonical-only
diff、独立复核、人工确认、closeout 和整目录归档。运行环境不能完成文件操作时保持阻塞。

## 恢复路由

每次续作先执行 preflight，再按 `change.json` 与实物核对结果选择唯一下一步：

| 首个未通过条件 | 路由 |
|---|---|
| `componentMode` 或目标组件不明确 | 询问用户 |
| `existing` baseline 不合格 | `devflow-init` |
| SRS 或 delta spec 未就绪，或 R1 rework | `devflow-specify` |
| R1 待评审 | `devflow-review` R1 |
| delta design 未就绪，或 R2 rework | `devflow-design` |
| R2 待评审 | `devflow-review` R2 |
| 实现任务未完成，或 R3 rework | `devflow-tdd` |
| R3 待评审 | `devflow-review` R3 |
| canonical sync 未通过 | `devflow-ship` 的同步与复核步骤 |
| 仅 closeout 或 archive 未完成 | `devflow-ship` |

工件状态冲突、多个节点同时看似可执行或依赖不完整时，不自行挑一个；先报告可核事实与最小澄清问题。

## 行为准则

所有 DevFlow 技能遵循：

1. 不补全没有来源的业务规则、设计理由、错误语义或验收阈值；缺失或冲突时列出事实并询问。
2. 发现方案风险时说明证据、影响和可行替代方案。
3. 选择满足规格的最简单方案，不为未来猜想增加抽象。
4. 只修改本变更声明的范围；旁路问题只记录，不顺手修复。
5. 用测试、构建、diff、评审记录和追溯证明结果。
6. 作者不自审；每个阶段由独立上下文评审并落盘记录。运行模式只决定是否在评审后等待人工确认。

语言规范与领域技能是各阶段的叠加约束，不是额外生命周期节点。触及语言 X 时加载可用的 `<x>-coding-standards`；语境命中领域技能 description 时加载该技能。

## 技能地图

| 技能 | 用途 |
|---|---|
| `devflow-init` | 为缺失或未就绪 canonical baseline 的既有组件做只读逆向初始化 |
| `devflow-specify` | 写本 AR 的 SRS 与 delta spec |
| `devflow-design` | 写本 AR 的 delta design 与测试设计 |
| `devflow-tdd` | 按任务执行 RED→GREEN→REFACTOR 并留证据 |
| `devflow-clean-code` | 约束实现与重构质量 |
| `devflow-review` | 独立执行 R1、R2、R3 与 sync 复核 |
| `devflow-ship` | canonical sync、DoD、closeout 与归档 |
| `devflow-fix` | 缺陷复现、根因与最小修复；仍受同一 preflight 和门禁约束 |

## 直接参考

- [交付结构契约](references/delivery-contract.md)
- [change.json 有效模板](references/change-template.json)
- [风险 profiles](references/risk-profiles.md)
