# DevFlow Profile 与路由表

本 reference 属于 `devflow-router`，定义合法 profile 路径、route upgrades 和 hard stops。

DevFlow 处理 AR / DTS / CHANGE work item，使用 `standard` / `component-impact` / `hotfix` / `lightweight` profiles。

Profile 决定 runtime 路径；编码规范 / 领域约束决定质量判据。两者正交。`c-coding-standards`、`cpp-coding-standards`、`automotive-embedded-development` 可以作为 Applicable Constraints 传给 flow/review/gate 节点，但永远不是 `Current Stage` 或 `Next Action Or Recommended Skill`。

## Standard 路由

```text
using-devflow
  -> devflow-router
  -> devflow-specify
  -> devflow-spec-review
  -> devflow-ar-design
  -> devflow-ar-design-review
  -> devflow-tdd-implementation        # 包含 task queue setup/preflight
  -> devflow-test-review
  -> devflow-code-review
  -> devflow-completion-gate
  -> (next-ready task ? devflow-tdd-implementation : devflow-finalize)
```

## Component-Impact 路由

```text
using-devflow
  -> devflow-router
  -> devflow-specify
  -> devflow-spec-review
  -> devflow-component-design
  -> devflow-component-design-review
  -> devflow-ar-design
  -> devflow-ar-design-review
  -> devflow-tdd-implementation        # 包含 task queue setup/preflight
  -> devflow-test-review
  -> devflow-code-review
  -> devflow-completion-gate
  -> (next-ready task ? devflow-tdd-implementation : devflow-finalize)
```

新增组件、SOA / interface / error-code / timing 变化、依赖或状态机变化、跨组件协调、组件设计缺失或过期时，使用 `component-impact`。`Change Type = modify/remove` 若同时触及这些边界，也应走 `component-impact`；仅组件内部行为修改可保持 `standard`，但必须保留 Existing Behavior / Baseline 到设计、测试和证据链路。

## Hotfix / Problem-Fix 路由

```text
using-devflow
  -> devflow-router
  -> devflow-problem-fix
  -> (optional) devflow-ar-design -> devflow-ar-design-review
  -> devflow-tdd-implementation        # 按需包含 task queue setup/preflight
  -> devflow-test-review
  -> devflow-code-review
  -> devflow-completion-gate
  -> devflow-finalize
```

Hotfix 可以压缩文档量，但不能跳过 test-review、code-review 或 completion-gate。

Hotfix 若属于车载嵌入式问题，应叠加 `automotive-embedded-development`；若涉及 C 或 C++ 实现，应叠加对应编码规范 skill。叠加约束不改变 hotfix 路由顺序。

## Lightweight 路由

```text
using-devflow
  -> devflow-router
  -> devflow-specify (minimal)
  -> devflow-spec-review
  -> devflow-ar-design (minimal，仍包含 test design section)
  -> devflow-ar-design-review
  -> devflow-tdd-implementation        # 包含最小 task queue setup/preflight
  -> devflow-test-review
  -> devflow-code-review
  -> devflow-completion-gate
  -> devflow-finalize
```

Lightweight 只压缩文档量，不移除质量门禁，也不移除适用的编码规范 / 领域约束。

## 第三层扩展约束

| 证据 | Applicable Constraints |
|---|---|
| C 源码 / 头文件 / C 测试 / MISRA C | `c-coding-standards` |
| C++ 源码 / C++ 测试 / RAII / 模板 / ABI / AUTOSAR C++ | `cpp-coding-standards` |
| 车载嵌入式 / ASIL / SOA / MDC / realtime / resource budget | `automotive-embedded-development` |

约束可以叠加。例如车载 C++ 变更通常同时适用 `cpp-coding-standards` 与 `automotive-embedded-development`。

## Hard Stops（硬停止）

命中任一项必须停止，并设置 `reroute_via_router=true`：

1. Requirement input 在 scope / acceptance / direction 上不清楚。
2. AR / 上游需求（IR / SR）traceability 冲突。
3. AR / DTS / CHANGE 缺唯一 owning component。
4. 变更影响组件边界，但 component design 缺失或过期。
5. AR design 缺 embedded test design。
6. Task queue preflight 无法产出完整 tasks 或唯一 `Current Active Task`。
7. `task-board.md` 存在多个 in_progress tasks、next-ready tasks 不明确，或与 `progress.md` 冲突。
8. TDD 已完成但测试尚未通过 `devflow-test-review`。
9. 代码变更破坏 SOA boundary，或新增未解释的跨组件依赖。
10. critical static-analysis / build / coding-standard 问题未解释。
11. review / gate verdict 无法映射到唯一 next action。
12. 适用的编码规范 / 领域约束被写成 runtime next action，而不是作为 Applicable Constraints。

## Reviewer 派发锚点

Review 节点必须派发为独立 reviewer subagents：

| 来源节点 | 派发节点 |
|---|---|
| `devflow-specify` | `devflow-spec-review` |
| `devflow-component-design` | `devflow-component-design-review` |
| `devflow-ar-design` | `devflow-ar-design-review` |
| `devflow-tdd-implementation` | `devflow-test-review` |
| `devflow-test-review` pass | `devflow-code-review` |

Task queue preflight 是 `devflow-tdd-implementation` 的内部步骤，不是派发式 review 节点。
