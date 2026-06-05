---
name: devflow-router
description: DevFlow 的可选疑难仲裁 skill（非 happy-path 必经）。当证据冲突、跨子街区切换嫌疑、profile 升级判断、多个 in_progress task / next-ready 不唯一、review 或 gate verdict 无法唯一映射下一步（reroute=true）时使用，把工件证据仲裁成唯一 canonical 下一步。不用于新会话入口发现（用 using-devflow）、不用于 happy-path 顺序推进（由各 leaf 的 Exit Handoff + 证据自路由承担）、不用于 leaf 内部写作/评审/实现。
---

# DevFlow Router（可选疑难仲裁）

DevFlow 2.0 的路由是**去中枢**的：happy path 由各 leaf 的 `Entry Gate`（自查上游证据）+ `Exit Handoff`（按转移表声明唯一 next）+ 证据自路由（读 `progress.md`）驱动，**不经过本 skill**。

本 skill 只在 happy path **走不通**时被显式调用，做**疑难仲裁**：把冲突 / 模糊的工件证据收敛成唯一下一步，或明确停下等待团队角色。它不替模块架构师 / 开发负责人 / 开发人员拍板专业判断。

## When to Use

仅当出现以下任一「疑难信号」时（通常由某个 leaf 标了 `reroute=true`，或编排者识别出冲突）：

- 工件证据冲突（如 `progress.md` 与 `reviews/` 不一致）
- 跨子街区切换嫌疑（SR ↔ 实现 profile）
- profile 升级判断（如改动是否触及组件边界 → 是否升级 `component-impact`）
- 多个 `in_progress` task，或 next-ready task 不唯一
- review / gate verdict 无法唯一映射下一步
- reviewer 子代理返回 `reroute=true`

**When NOT to use**：

- 新会话入口发现 → `using-devflow`
- happy-path 顺序推进 → 各 leaf 的 Exit Handoff + 证据自路由
- leaf 内部 authoring / review / 实现 → 对应 `devflow-*` leaf

## Entry Gate

进入前确认这**确实**是疑难仲裁（命中上面任一信号），而非可由证据自路由直接解决的普通推进。若 `progress.md` 已能唯一确定下一步 → 退出，让编排者直接进对应 leaf，不要多绕一层。

## Core Process

### 1. 读最少必要证据

只读仲裁所需：项目 `AGENTS.md` 路径映射、用户请求、`features/<id>/progress.md`、相关 `reviews/` / `completion.md`、必要时 `docs/component-design.md` / `docs/ar-designs/`。不在仲裁阶段做大范围代码探索。

### 2. 子街区与 profile 仲裁

依 `references/devflow-conventions.md` §4：

- 先定子街区（SR=需求分析；AR/CHANGE/DTS=实现），**禁止跨子街区切换**——SR 拆出的候选 AR 由需求负责人**新建** AR work item。
- profile 单向升级、不降级。证据冲突取更保守：选更上游节点 / 更高 profile。
- 升级到 `component-impact` 时下一步指向 `devflow-component-design`。

### 3. 归一化 Execution Mode

依 conventions §5：用户显式 → `AGENTS.md` 默认 → 已有值 → `interactive`。`auto` 不豁免 review / gate / approval。

### 4. 校验 leaf 的显式 handoff

leaf 返回的 `next_action_or_recommended_skill` 是 bias 不是 authority。校验它是否归一化、是否在当前 profile 合法集合内（conventions §6/§8）、是否与最新 evidence 一致。任一不满足 → 忽略，按转移表（conventions §8）重新决定。`requirement-analysis` 下 leaf 返回实现类节点一律非法 → 停下，由真人决定是否新建 AR。

### 5. 决定唯一 canonical 下一步

按 conventions §8 转移表与 §9 Hard Stops 收敛到唯一节点：支线优先于主链 → review/gate 恢复优先于实现 → 缺失上游优先于下游 → 冲突取更保守。无法唯一映射 → `reroute=true` 停下，写明阻塞原因。

### 6. review / gate 恢复

读最新 record，按 verdict（依 `references/reviewer-dispatch-protocol.md`）：

- `通过` → 转移表的成功后节点；`needs_human_confirmation=true` 时按 Execution Mode 处理
- `需修改` / `阻塞`(内容) → 回授权 authoring 节点做定向回修
- `阻塞`(workflow) → `reroute=true` 停下

completion-gate 通过后先读 `Task Board Path`：唯一 next-ready task → 更新 `Current Active Task` 并指向 `devflow-tdd-implementation`；无剩余 task → `devflow-finalize`；候选不唯一 → 停下。

### 7. reviewer 派发（疑难场景）

仲裁中若需评审，按 `references/reviewer-dispatch-protocol.md` 派发独立 reviewer subagent（不内联、不让作者自审）。日常评审派发由编排者（`/devflow-ship` 等）按 fan-out + merge 承担，不必经本 skill。

## Exit Handoff

输出唯一下一步或显式停下，写入 `progress.md`：

- `Current Stage` / `Workflow Profile` / `Execution Mode`
- `Target Skill`：唯一 canonical `devflow-*` 节点
- `Why`：1-2 条决定性证据
- `reroute`：`false`（已唯一映射，编排者据此进目标 leaf）或 `true`（仍无法唯一映射，停下等团队角色）

非 hard stop → 编排者同一轮进目标 leaf；hard stop → 停下等待。

## Red Flags

- 把本 skill 当成 happy-path 的必经中枢（2.0 中它是**可选仲裁**）
- 在仲裁阶段做大范围代码探索
- 忽略证据冲突沿用旧印象推进
- 把 `auto` 解读为不写 review record / 不要 approval
- 内联 review 而不派发独立 reviewer subagent
- 替团队角色拍板组件边界 / 接口 / 优先级

## Common Rationalizations

| 话术 | 反驳 |
|---|---|
| 「每步都先过 router 更稳」 | 2.0 路由去中枢；happy path 由 leaf 的 Exit Handoff + 证据自路由承担，router 只处理疑难 |
| 「上次走 standard，这次沿用」 | 每次仲裁按当前证据重判 profile；触及 SOA 接口 / 依赖 / 状态机 → 升级 component-impact |
| 「TDD 完成了，直接 code-review」 | 必须先有 `devflow-test-review` 通过 verdict（见 Hard Stops #9） |
| 「证据冲突，挑个顺的节点」 | 取更保守：更上游 / 更高 profile；无法唯一映射 → `reroute=true` 停下 |
| 「这个小 SR 直接进 ar-design」 | 禁止跨子街区；SR 经 finalize analysis closeout，候选 AR 另建 work item |

## Verification

- [ ] 已确认是疑难仲裁（命中 When to Use 信号），非普通推进
- [ ] 已按最新证据决定 profile（含升级判断），未降级 / 未跨子街区
- [ ] 推荐节点在当前 profile 合法集合内（conventions §6/§8）
- [ ] verdict 已按 dispatch 协议消费
- [ ] 无法唯一映射时已置 `reroute=true` 并写明原因
- [ ] 字段统一用 `reroute`

## 约定

本 skill 遵循 `references/devflow-conventions.md` 与 `references/reviewer-dispatch-protocol.md`；项目 `AGENTS.md` 可覆盖等价路径与模板。
