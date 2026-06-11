---
name: devflow-clean-code
description: 当 DevFlow 的实现、重构、代码评审或完成门禁需要判断代码是否可读、范围克制、切片薄、重构干净、无死代码、易审查、易维护时使用。第三层代码内在质量的编码统筹 skill；不用于设计统筹、测试有效性、runtime routing 或写 progress/handoff。
---

# DevFlow Clean Code

## 总览

`devflow-clean-code` 是 DevFlow 第三层“代码内在质量”的编码统筹 skill。它回答：这份实现是否简单、可读、范围克制、易审查、易维护，并且没有把未来负担藏进当前 task。

本 skill 不是 runtime node，不写 `progress.md` / handoff，不产 review verdict，不替代 `devflow-code-review`。它只提供代码质量约束，供实现、重构、代码评审和完成门禁消费。

## 适用场景

适用：

- `devflow-tdd-implementation` 的 GREEN / REFACTOR 阶段。
- `devflow-code-review` 判断实现内在质量。
- `devflow-completion-gate` 判断代码质量债务是否可接受。
- 代码出现范围扩张、过度抽象、命名混乱、死代码、功能和重构混杂等问题。

不适用：

- 设计架构统筹 → `devflow-clean-design`
- C 语言规范 → `c-coding-standards`
- C++ 语言规范 → `cpp-coding-standards`
- 测试有效性 → `devflow-test-review`
- 领域约束 → 对应 domain-constraints skill
- runtime 下一步 → `devflow-router`

## 硬性门禁

- 不写 `Current Stage` 或 `Next Action Or Recommended Skill`。
- 不替 reviewer 给 verdict。
- 不替 TDD 纪律：RED 必须先失败，GREEN 不做 cleanup，REFACTOR 不加行为。
- 不把语言级规则写成本 skill 默认规则。
- 不把领域约束写成本 skill 默认规则。

## 对象契约

- Primary Object: clean code constraints
- Frontend Input Object: implementation diff、tests、implementation-log、Refactor Note、applicable coding standards、applicable domain constraints
- Backend Output Object: 代码质量约束清单、code review 增补判据、completion gate 增补判据
- Boundaries: 不写代码、不产 verdict、不做 runtime routing
- Invariants: 只处理通用代码质量；语言/领域规则由扩展 skills 提供

## 核心原则

### 1. Rule 0：最简单可工作的实现

GREEN 阶段只写让当前 RED 变绿的最少代码。不要提前实现未被测试驱动的功能，不要引入未被设计批准的抽象。

Red flags:

- 跑测试前写了大段实现。
- 当前 task 只需要一个分支，却引入策略/工厂/插件体系。
- 代码服务假想未来，而不是当前 acceptance。

### 2. 范围纪律

只修改当前 task 要求修改的范围。路过发现的问题要登记，不顺手改。

不要：

- 顺手修相邻 bug。
- 重构无关文件。
- 删除不理解的旧逻辑。
- 在 spec / design / task 之外加功能。

### 3. 薄垂直切片

一次只完成一个 active task 的一组测试设计用例。每次切片都应可构建、可测试、可回退。

Red flags:

- 一个 task 同时改变多个无关关注点。
- 多个 in-progress task。
- 大范围重构和功能变化混在一起。

### 4. 可读性优先

代码应能让 reviewer 快速理解意图。

要求：

- 命名表达领域和行为意图。
- 控制流直白。
- 函数职责集中。
- 注释解释约束和取舍，不复述代码。
- 无死代码、无注释掉的历史残骸。

### 5. 重构纪律

REFACTOR 只在 GREEN 后进行。重构不能改变行为，且必须留在当前 task 边界内。

Refactor Note 至少记录：

- 做了什么 cleanup。
- 为什么仍在当前 task 范围内。
- 重构后跑了哪些验证。
- 哪些问题登记为后续债务而非本轮处理。

## 与扩展 skills 的关系

- `c-coding-standards` 提供 C 语言级规则。
- `cpp-coding-standards` 提供 C++ 语言级规则。
- `embedded-development` 提供嵌入式领域级约束。
- `automotive-development` 提供车载领域级约束。
- 本 skill 负责统筹代码内在质量，不重复这些扩展内容。

## 反向理由化（Common Rationalizations）

| 话术 | 反驳 |
|---|---|
| 「顺手改一下更干净」 | 不在当前 task 范围内的清理是范围扩张 |
| 「先抽象好以后省事」 | 抽象必须由当前真实用例支撑 |
| 「GREEN 时一起重构更快」 | GREEN 与 REFACTOR 是两顶帽子，混在一起不可审 |
| 「这个命名我自己懂」 | 代码是给 reviewer 和未来维护者读的，不是给当前作者读的 |

## 验证清单

- [ ] 实现只覆盖当前 active task。
- [ ] GREEN 阶段没有 cleanup。
- [ ] REFACTOR 没有改变行为。
- [ ] 命名和控制流可冷读。
- [ ] 没有新增死代码或未解释兼容层。
- [ ] 路过问题已登记，未顺手扩张。
- [ ] 适用编码规范和领域约束已消费或明确 N/A。

## DevFlow 约定

本 skill 是第三层代码内在质量的编码统筹 skill。它不写 `progress.md`、handoff 或 review verdict，不改变 canonical runtime nodes。需要 runtime routing 时回 `devflow-router`。
