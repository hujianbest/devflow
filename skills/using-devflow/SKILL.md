---
name: using-devflow
description: DevFlow 的 public entry meta-skill。当新会话进入 DevFlow，或用户表达"继续推进 / 澄清需求 / 做设计 / 做 TDD / 评审 / 收口"等意图但尚未确定具体 devflow 节点时使用，把意图映射到唯一 leaf skill，并施加 DevFlow 共同行为准则。不做权威路由、不持有运行时状态、不替团队角色拍板；疑难仲裁交 devflow-router。
---

# Using DevFlow

DevFlow skill family 的 **public entry meta-skill**。它只做两件事：

1. **发现（discovery）**：把用户意图映射到唯一的 `devflow-*` leaf skill。
2. **共同行为准则（operating behaviors）**：施加一组跨所有 DevFlow skill 永远生效的纪律。

它**不是**调度中枢，也**不是**运行时权威：不决定 profile/execution mode、不消费 verdict、不持有 stage 状态、不做 review 派发。运行时编排由「用户 + 斜杠命令 + 各 leaf skill 自身的 Entry Gate / Exit Handoff + 证据自路由」承担。疑难仲裁交可选的 `devflow-router`。

> `using-devflow` 是 public entry，**永远不写入** `Next Action Or Recommended Skill` 或任何 handoff 字段。

## When to Use

- 新会话进入 DevFlow，不确定从哪个 leaf 开始
- 用户表达泛化意图（"继续 / 推进 / 开始做 / 澄清 / 设计 / 实现 / 评审 / 收口"）但未点到具体节点

**When NOT to use**：

- 已在某个 leaf skill 内部 → 继续该 skill
- 工件已存在、要按证据恢复 → 直接读 `features/<id>/progress.md` 的 `Current Stage` + `Next Action Or Recommended Skill`，进对应 leaf（证据自路由）
- 证据冲突 / 跨子街区嫌疑 / 多个 in_progress task 等疑难 → `devflow-router`
- 产品发现 / 决定要不要做这个 SR / AR → 回需求负责人，DevFlow 不承担产品发现

## Discovery（意图 → leaf）

把请求映射到下表唯一一项；映射不出唯一项 → 用「单事实检查点」补一个判别问题；仍不唯一或属疑难 → `devflow-router`。

```
进入 DevFlow
  ├── 只说"继续推进" ───────────→ 读 progress.md 的 Current Stage + Next Action，按证据恢复到对应 leaf
  ├── 澄清 SR / 子系统需求 ──────→ devflow-specify（profile = requirement-analysis）
  ├── 澄清 AR 规格 ────────────→ devflow-specify（实现 profile）
  ├── 写 / 改组件实现设计 ───────→ devflow-component-design
  ├── 写 / 改 AR 实现设计 ───────→ devflow-ar-design（含测试设计章节）
  ├── TDD 实现 / 改代码 ────────→ devflow-tdd-implementation
  ├── 紧急缺陷 / hotfix 复现根因 →  devflow-problem-fix
  ├── 评审（规格/设计/测试/代码）→  对应 devflow-*-review（由编排者按 fan-out 派发独立 subagent）
  ├── 判断能否完成 ────────────→ devflow-completion-gate
  └── 收口 / closeout ─────────→ devflow-finalize
```

`requirement-analysis` 子街区（SR）只经过 specify → spec-review →（可选）component-design → component-design-review → finalize；实现类节点对 SR 一律非法。

### 命令是 bias，不是 authority

`/devflow-spec`→specify、`/devflow-design`→ar-design、`/devflow-build`→tdd-implementation、`/devflow-fix`→problem-fix、`/devflow-ship`→评审+门禁+收口、`/devflow-route`→router。命令只给默认偏向；与工件证据冲突时按证据走，缺上游工件时进缺失的上游 leaf。

### 单事实检查点

若只差**一个**关键事实就能确定唯一 leaf（如"这是 AR 还是 DTS"、"AR 设计是否已过 review"），先问这一个最小判别问题再进。需要 ≥2 个事实、工件互相冲突、涉及 profile 升级或跨组件协调 → 直接 `devflow-router`。

## DevFlow 共同行为准则（永远生效）

这些准则跨所有 DevFlow skill 生效，不可协商：

1. **Evidence over memory**：决策读磁盘工件（`progress.md` / `reviews/` / `evidence/` / `completion.md`），不读聊天记忆；冲突时工件优先并记入 `Blockers`。
2. **No self-verification**：作者 skill 不评审自己；评审由独立 reviewer subagent 给 verdict，且不改生产代码 / 不补测试。
3. **Respect hard gates**：门禁（见 `references/devflow-conventions.md` §9）不被 `auto` 模式豁免；`auto` 只去掉节点间的人工确认停顿。
4. **Surface assumptions / manage confusion**：先亮出关键假设；遇到矛盾或不一致就停下发问，不带着猜测往前冲。
5. **Team-role boundary**：不替模块架构师 / 开发负责人 / 开发人员拍板业务、范围、架构、接口契约。
6. **Scope discipline & simplicity**：外科手术式修改，不顺手重构无关代码；优先简单直接的做法。

## 正确结束

输出只有两类：

1. 进入唯一合法 `devflow-*` leaf skill，并在**同一回复**继续该 leaf 的 Entry Gate / 第 1 步；
2. 属疑难（证据冲突 / 跨子街区 / profile 升级 / 多 in_progress task）→ 转交 `devflow-router`，只说明为什么不能直接落点。

`clear case` 用 3 行快路径：

```text
1. Target Skill: <canonical devflow-* 节点名>
2. Why: <1-2 条决定性证据>
3. （direct）继续目标 leaf 的 Entry Gate / 第 1 步  ｜ （router）转交原因
```

## Red Flags

- 把 `using-devflow` 写进 `Next Action Or Recommended Skill` 或 handoff
- 在入口层做权威路由 / 决定 profile / 消费 verdict / 派发 reviewer
- 映射不唯一却硬选一个 leaf
- 因为用户报了命令名就跳过工件证据
- 已在 leaf 内部或可证据恢复时仍回入口绕一圈

## Common Rationalizations

| 话术 | 反驳 |
|---|---|
| 「用户给了 `/devflow-build`，直接进 tdd-implementation」 | 命令是 bias。缺 AR 设计 / 缺 design review → 进缺失的上游 leaf；疑难 → router |
| 「上次走过 router，这次直接进入即可」 | 证据恢复读 `progress.md` 即可，不必回入口；但入口也不持有上次状态 |
| 「用户说 auto，可省掉 review 派发」 | `auto` 不豁免 review / gate / approval，只去掉人工确认停顿 |
| 「为响应快，把 using-devflow 写进 handoff」 | 禁止；它是 public entry，永不出现在 handoff |
| 「证据有点冲突，挑个顺的 leaf」 | 冲突属疑难 → `devflow-router` 仲裁，不在入口猜 |

## Verification

- [ ] 已把意图映射到唯一 leaf，或转交 `devflow-router`
- [ ] clear case 用了 3 行快路径并在同一回复进入目标 leaf 的 Entry Gate
- [ ] 未把 `using-devflow` 写进任何 handoff 字段
- [ ] 未在入口做 profile / verdict / 派发决定

## 约定

本 skill 遵循 `references/devflow-conventions.md`（产物布局、字段、profile、节点清单、转移表、Hard Stops、reviewer 派发）；项目 `AGENTS.md` 可覆盖等价路径与模板。
