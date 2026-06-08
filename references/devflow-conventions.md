# DevFlow 约定（单一真相源）

> 本文件是 DevFlow 全部 skill 共享的**单一真相源（single source of truth）**：产物布局、`progress.md` canonical 字段、handoff 字段、合法 profile 集合、execution mode、canonical 节点清单、Read-on-presence 与 Promotion 规则。
>
> 所有 `skills/devflow-*/SKILL.md` 以一行 `## DevFlow 约定` 引用本文件，**不再各自复制**这些约定（这是 DevFlow 2.0 的去重设计，见 `docs/devflow-2.0-design-spec.md` §5.4）。
>
> **覆盖优先级**：项目根 `AGENTS.md` 的 `## Project overrides` 可覆盖本文件的等价路径与模板；未覆盖时以本文件为准。

---

## 1. 产物布局（Artifact Layout）

```text
<component-repo>/
  AGENTS.md                         # 项目硬契约与覆盖点（可选）
  docs/
    component-design.md             # 长期组件实现设计
    ar-specs/                       # 长期 AR 需求规格（从 features/<id>/requirement.md 提升）
      AR<id>-<slug>.md
    ar-designs/                     # 长期 AR 实现设计（从 features/<id>/ar-design-draft.md 提升）
      AR<id>-<slug>.md
    interfaces.md                   # 可选；仅团队启用时读取 / 同步
    dependencies.md                 # 可选；仅团队启用时读取 / 同步
    runtime-behavior.md             # 可选；仅团队启用时读取 / 同步

  features/
    AR<id>-<slug>/                  # 单个 AR 的过程产物
    DTS<id>-<slug>/                 # 单个缺陷 / 问题修复的过程产物
    CHANGE<id>-<slug>/              # 单个轻量变更的过程产物
    SR<id>-<slug>/                  # 单个子系统需求分析的过程产物
```

`features/<id>/` 下按需包含的过程产物：

```text
features/<id>/
  README.md
  progress.md
  requirement.md
  component-design-draft.md
  ar-design-draft.md
  tasks.md
  task-board.md
  traceability.md
  implementation-log.md
  reviews/            # spec-review.md / component-design-review.md / ar-design-review.md / test-check.md / code-review.md
  evidence/           # unit/ integration/ static-analysis/ build/
  completion.md
  closeout.md
```

`docs/` 存放随代码提交的长期组件资产；`features/<id>/` 存放单个 work item 的过程产物。

---

## 2. Read-on-presence 规则

- **必需长期资产缺失即阻塞**：component-impact 工作需要 `docs/component-design.md`；implementation closeout 前需要 `docs/ar-designs/AR<id>-<slug>.md`。
- **可选资产按存在性读取**：`docs/interfaces.md`、`docs/dependencies.md`、`docs/runtime-behavior.md` 仅在项目启用时读取 / 同步；缺失记录为 `N/A (project optional asset not enabled)`，不阻塞。
- **过程目录保留在 `features/` 下**：不要把已关闭 work item 移到 `features/archived/`，否则破坏追溯链接。

---

## 3. `progress.md` canonical 字段

所有 skill 读写 `features/<id>/progress.md` 时使用以下 canonical 字段：

- **Work Item Type**：`SR` / `AR` / `DTS` / `CHANGE`
- **Work Item ID**：如 `SR1234` / `AR12345` / `DTS67890` / `CHANGE123`
- **Owning Component**：AR / DTS / CHANGE 必填
- **Owning Subsystem**：SR 必填
- **Workflow Profile**：见 §5
- **Execution Mode**：见 §6
- **Current Stage**：当前 canonical devflow node（见 §7；**craft 透镜不写入此字段**）
- **Pending Reviews And Gates**：待处理 review / gate 列表
- **Next Action Or Recommended Skill**：仅允许一个 canonical node（见 §7）
- **Blockers**：open blockers
- **Last Updated**：timestamp

实现 profile 还需读写：**Task Plan Path**、**Task Board Path**、**Current Active Task**、**Implementer Dispatch Status**、**Implementer Context Pack**、**Implementation Report**。

> **关键不变量**：`Next Action Or Recommended Skill` 与 `Current Stage` 只能是 §7 的 canonical 节点，**不能**是 `using-devflow`、不能是任何 `devflow-*-craft` 透镜、不能是自由文本。

---

## 4. Handoff 字段

skill 完成后返回结构化 handoff，使用以下字段：

- `current_node`
- `work_item_id`
- `owning_component` or `owning_subsystem`
- `result` or `verdict`
- `artifact_paths`
- `record_path`（存在 review / gate / verification record 时）
- `evidence_summary`
- `traceability_links`
- `blockers`
- `next_action_or_recommended_skill`（仅 canonical 节点）
- `reroute_via_router`（`true` / `false`）

> 不要把 `next_action_or_recommended_skill` 设为 `using-devflow`、craft 透镜或自由文本。

---

## 5. 合法 Workflow Profile 与升级规则

| Profile | 子街区 | 适用场景 |
|---|---|---|
| `requirement-analysis` | 需求分析（SR） | 澄清子系统级需求 + 可选组件设计修订；不进入实现 |
| `standard` | 实现 | 既有组件 AR 增量、组件设计稳定、纯组件内修改 |
| `component-impact` | 实现 | 新增组件 / 改 SOA 接口 / 改组件职责 / 改依赖 / 改状态机 / 组件设计缺失或过期 / 跨组件协调 |
| `hotfix` | 实现 | DTS / 紧急缺陷 / 已上线问题修复 |
| `lightweight` | 实现 | 极小、低风险、纯局部修改；保留 specify→completion 全链，仅压缩文档量 |

升级规则：

- **只允许在同一子街区内单向升级**（`standard → component-impact`），不允许降级。
- **禁止跨子街区切换**：同一 work item 不得在 `requirement-analysis` 与任何实现 profile 之间切换。SR 拆出的候选 AR 必须**新建** AR work item，由 router 重新分流。
- Profile 由 `devflow-router` 判定并写入 `progress.md` 后即为单一真相，其余 skill 只读不改。

---

## 6. 合法 Execution Mode

- 取值：`interactive` / `auto`。
- 归一化顺序：用户显式要求 → `AGENTS.md` 默认 → 已有值 → 默认 `interactive`。
- `auto` 仅表示节点之间不停下等真人确认；**不删除** review / gate / approval / 证据要求，也不让 leaf 静默降级。

---

## 7. Canonical 节点清单

13 个 canonical 工作节点（`Current Stage` / `next_action_or_recommended_skill` 只能取这些）：

```text
devflow-router                    （运行时证据路由，非默认必经的作者节点）
devflow-specify
devflow-spec-review
devflow-component-design
devflow-component-design-review
devflow-ar-design
devflow-ar-design-review
devflow-tdd-implementation
devflow-test-review
devflow-code-review
devflow-completion-gate
devflow-finalize
devflow-problem-fix
```

**非 canonical（不进 progress/handoff）**：

- `using-devflow` —— public entry / 发现 + 行为宪法（meta-skill）。
- `devflow-design-craft` / `devflow-coding-craft` / `devflow-test-craft` —— 质量透镜（craft skills），由流程节点在其工作流内部叠加调用，不产生 verdict、不改变流程拓扑。

---

## 8. Promotion 规则（长期资产同步）

仅在 `devflow-finalize` 的 closeout 阶段、且 completion gate 允许时，提升长期资产：

- `features/<id>/requirement.md` → `docs/ar-specs/AR<id>-<slug>.md`
- `features/<id>/ar-design-draft.md` → `docs/ar-designs/AR<id>-<slug>.md`
- `features/<id>/component-design-draft.md` → `docs/component-design.md`（模块架构师 sign-off 后）
- 可选子资产（`docs/interfaces.md` / `dependencies.md` / `runtime-behavior.md`）仅在项目启用且发生变化时同步。

---

## 9. 角色分离不变量

- review 节点必须由 `devflow-router` 派发**独立 reviewer subagent**；不在父会话内联评审；作者不自审。
- implementer subagent 只由 `devflow-tdd-implementation` 派发。
- reviewer 不修改任何生产代码 / 测试 / 设计制品；只产出 findings + verdict。
- DevFlow 不替模块架构师 / 开发负责人 / 开发人员拍板业务、范围、优先级、架构边界或接口契约。
