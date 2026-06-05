---
name: devflow-coding-craft
description: 教 agent 如何把代码写好——薄垂直切片、简单性优先（Rule 0）、范围纪律、可读性与命名、保持可编译 / 可回退、嵌入式防御性编码。适用于在 devflow-tdd-implementation 的 GREEN / REFACTOR 步骤内部把「让测试变绿」升级为「写出干净、简单、可维护的实现」。这是质量透镜，不是流程节点：不写 progress/handoff，不产生 review verdict，不替代独立代码评审。
---

# DevFlow 编码匠艺（质量透镜）

## 总览

`devflow-tdd-implementation` 负责*纪律*：单 active task、fail-first RED、最小 GREEN、Two Hats、fresh evidence。本透镜负责*手艺*：让 GREEN 实现与 REFACTOR cleanup 不只是「能跑、测试绿」，而是「简单、可读、外科手术式精确、嵌入式安全」。

「能跑」与「写得好」之间的差距，就是 code-review 反复打回的那些东西。把它们前置到写代码时。

## 它不是什么

- **不是流程节点**：不写 `progress.md`、不进 `next_action_or_recommended_skill`、不产生 verdict。
- **不替代独立评审**：它让你*交出更干净的实现*，`devflow-test-review` / `devflow-code-review` 仍是唯一裁决者。
- **不放宽 TDD 纪律**：RED 必须先失败、GREEN 不做 cleanup、REFACTOR 守 Two Hats、证据必须 fresh——一律不变。

## 何时叠加

| 调用方 | 在哪个步骤叠加 |
|---|---|
| `devflow-tdd-implementation` | GREEN（写最小实现）与 REFACTOR（task 范围内 cleanup）步骤 |
| controller-direct 的极小修改 | 同样适用本透镜 |

## 核心判断

### 1. 简单性优先（Rule 0）

写每段实现前问：「能让这条 RED 变绿的**最简、最显然**的代码是什么？」写完后用 Staff 视角自检：

- 能更少行吗？
- 这些抽象配得上复杂度吗？
- 我是在为当前 task 写，还是在为假想未来写？

| ✗ | ✓ |
|---|---|
| 为一处计算引入「策略 + 工厂」 | 一个直白函数 |
| 提前抽出只用一次的 helper | 内联，等第三次再抽 |
| 用宏 / 模板元编程炫技 | 朴素、明显、可调试的写法 |

三行相似代码 > 一个过早的抽象。先写朴素且显然正确的版本，正确性被测试证明后再考虑优化。

### 2. 薄垂直切片（Incremental）

- 一次只让**一个** task 的一组 Test Design Case 从 RED 到 GREEN，不要一口气铺开整个 AR。
- 每次增量后保持**可编译**、既有测试仍绿——不要在切片之间留下 broken 状态。
- 改动应**可回退**：新增优于就地大改；尽量让一次提交对应一个逻辑变化。

**判别 tell**：在跑测试前写了 > ~100 行 / 一个改动同时动了多个不相关的关注点 → 切得太厚，收回。

### 3. 范围纪律（Scope Discipline）

只动 task 要求动的东西。**不要**：

- 「顺手清理」相邻代码；
- 重构你只是路过读到的文件；
- 删你不完全理解的注释 / 代码（Chesterton's Fence：不懂的栅栏先别拆）；
- 加 spec / task 之外「看起来有用」的功能。

路过发现的问题**登记不顺手改**：

```text
NOTICED BUT NOT TOUCHING:
- foo.c 里有个未使用的静态函数（与本 task 无关）
- bar 的错误信息可以更清楚（单独 task）
→ 登记到 implementation-log / Refactor Note 的 Escalation Triggers，交 router / code-review 处理
```

这与 `devflow-tdd-implementation` 的 Two Hats 直接协同：REFACTOR 只在当前 task 边界内，跨边界一律升级。

### 4. 可读性与命名

- 名字要描述意图：拒绝无语境的 `temp` / `data` / `result` / `tmp2`。
- 控制流直白：避免嵌套三元、深层回调、过长函数；早返回优于深嵌套。
- 相关代码归组，模块边界清晰。
- 注释只解释**非显然的意图 / 约束 / 取舍**，不复述代码在做什么。
- 不留死代码：no-op 变量、`// removed` 残骸、兼容性僵尸 shim——发现即登记清理（在 task 边界内）。

**判别 tell**：函数名是动词缺宾语（`process()` / `handle()`）、或要读完整个函数才知道它干嘛 → 命名 / 拆分有问题。

### 5. 嵌入式防御性编码

把设计阶段定的防御约束落到代码：

- **内存 / 资源**：分配与释放配对；失败路径也释放（goto cleanup / RAII）；检查边界与溢出。
- **并发 / 中断**：尊重中断上下文限制；临界区最小化；按既定锁顺序加锁。
- **错误处理**：检查每个可能失败的调用返回；不吞错误；提供调用方可恢复的错误码。
- **实时性**：实时路径避免不可预测耗时操作（动态分配 / 阻塞 IO）。

**判别 tell**：`malloc` / `open` / `lock` 之后的错误分支没有对应释放 / 解锁 → 资源泄漏 / 死锁隐患。

### 6. 不混合关注点

实现与重构分开（Two Hats）；功能变更与格式 / 重命名分开。一个逻辑变化对应一次提交，便于评审与回滚。

## 与 DevFlow 纪律的协同

- GREEN 阶段只追求「最小让测试变绿」，简单性自检属于此处；**真正的 cleanup 留到 REFACTOR**，且不破 Two Hats。
- 范围纪律与 Refactor Note 的 Escalation Triggers 协同：跨 task / 跨组件的改进登记上抛，不私自扩张。
- 本透镜不生成证据、不下结论；fresh RED/GREEN/REFACTOR evidence 仍由 `devflow-tdd-implementation` 采集，质量仍由独立 review 裁决。

## 反向理由化（Common Rationalizations）

| 话术 | 反驳 |
|---|---|
| 「先把这块抽象好，省得以后改」 | Rule 0：写最简实现。抽象等第三个真实用例。过早抽象比重复更难维护 |
| 「顺手把相邻这个小 bug 改了」 | 违反范围纪律 + Two Hats。登记到 Escalation Triggers，交 router / code-review |
| 「一次把整个 AR 写完更快」 | 薄切片才可测、可定位、可回退。> 100 行未测即过厚 |
| 「这个注释看不懂，删了干净」 | Chesterton's Fence：不懂先别删。问清楚或保留 |
| 「错误分支不重要，先不处理」 | 嵌入式里失败路径与资源释放就是正确性；happy-path-only = 不合格 |
| 「变量名短一点打字快」 | 可读性 > 打字速度。名字要表达意图 |

## Red Flags

- 跑测试前写了 > ~100 行。
- 一次改动混了多个不相关关注点 / 功能 + 重构混提。
- 动了 task 范围外的文件「顺手优化」。
- 资源获取后失败分支无释放 / 无解锁。
- 函数名无宾语、控制流深嵌套、出现无语境的 `temp`/`data`。
- 留下死代码 / `// removed` 残骸 / 单次使用的「可复用」helper。

## 自检清单（让实现更干净，但不替代独立评审）

- [ ] 已用 Rule 0 自检过：这是最简且显然正确的实现吗
- [ ] 本轮只动了当前 task 要求动的文件
- [ ] 没有为假想未来引入的抽象 / helper
- [ ] 命名表达意图，控制流直白，无死代码
- [ ] 每个失败 / 错误 / 中断分支都正确释放资源
- [ ] 实现与重构、功能与格式未混在一起
- [ ] 路过发现的改进点已登记而非顺手改

## DevFlow 约定

本 skill 遵循 `references/devflow-conventions.md`（产物布局 / progress 字段 / handoff 字段 / profile / 节点表）；项目 `AGENTS.md` 可覆盖等价路径与模板。本 skill 是 craft 透镜，**不**写 progress/handoff，**不**产生 verdict。
