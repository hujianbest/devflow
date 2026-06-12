---
name: devflow-tdd
description: 在实现任何功能或修复任何缺陷、即将编写实现代码时使用；设计确认后的整个实现期都适用。强制测试先行的 RED→GREEN→REFACTOR 循环。不用于规格编写、设计决策或纯文档修改。
---

# DevFlow TDD（第二层）

## 总览

TDD 把"正确"从主观判断变成可执行、可复现的事实。核心原则一句话：

> **没有先看着它失败的测试，就没有实现代码。**

为什么顺序不可妥协：先写实现再补测试，测试一写出来就通过——通过证明不了任何东西。你没见过它失败，就不知道它是否真的在验证目标行为，还是在验证你的实现碰巧做的事。**测试先行回答「代码应该做什么」；测试后补只能回答「代码现在做了什么」。**

写在测试之前的实现代码：删掉，重来。不要"留着当参考"——你会照着它写测试，那就是测试后补。

例外（需向人确认）：一次性探索原型（探索完丢弃，正式实现仍走 TDD）、生成代码、纯配置。想着"就这一次跳过 TDD"？停。那是合理化。

## 计划与任务组织

实现的输入是 design.md 的**测试设计表**；执行的载体是 `features/<id>/plan.md`（模板见 `references/plan-template.md`）。

**进入实现前先细化 plan.md**（specify 阶段已建骨架：运行模式 + 门禁表）：把测试设计表的用例组织成任务，每个任务**自包含**——用例锚点（含 Given/When/Then 摘要）、精确文件路径、RED/GREEN 步骤与验证命令、完成定义全部内联。标准只有一个：**一个全新会话只读 spec.md + design.md + plan.md 就能从任意断点继续执行**。"同上""见前文"式的任务描述使中断恢复失效，按违规处理。

每个任务完成时在 plan.md 附上 RED/GREEN 证据行（命令 + 关键输出摘要 + commit 锚点）——这是评审者和人核验"测试真的失败过、真的在最终代码上跑过"的最低限度证据，不接受只有叙述没有输出的"证据"：

```markdown
- 证据:
  - RED:   `ctest -R ModeServiceTest` → FAIL: SetModeRejectsInvalid…
           (expected ERR_INVALID_ARG, got OK) @ a1b2c3d
  - GREEN: `ctest` → 47/47 passed, 0 warnings @ d4e5f6a
```

规则：

- **一次只有一个 in-progress 任务**。每个任务是一个薄垂直切片：完成后可构建、全部测试通过、可独立提交。
- 任务循环：取 plan.md 第一个未完成任务 → RED → GREEN →（按需）REFACTOR → 补证据行与 traceability → 更新任务状态 → 下一个。**每步勾选实时更新到 plan.md**，断点信息只存在于磁盘，不存在于会话记忆。
- 任务完成时更新 `features/<id>/traceability.md` 对应行的任务 ID、代码文件、测试代码文件、验证证据列。
- plan 是测试设计的执行索引：不得新增 design.md 中没有的用例或业务事实；发现缺用例 → 回 `devflow-design`。
- 实现中发现设计错误或规格漏洞：**停下任务**，在 plan.md 记录阻塞原因，回 `devflow-design` / `devflow-specify` 修正工件并重新评审，不在代码里悄悄绕过。
- 中断恢复：按 plan.md 的「恢复指引」节执行——先看门禁表，再找第一个非 done 任务，以步骤勾选与证据行判断断点。

## 执行模式：默认派发 implementer subagent

runtime 支持 subagent 时，**默认每个任务派发一个全新上下文的 implementer subagent**（角色定义 `agents/devflow-implementer.md`）执行：新上下文只依赖打包的输入工作，天然防止长会话的上下文漂移，也强制设计工件可冷读。

派发时给 subagent 的 **Context Pack**（不传聊天历史）：

- 任务 ID 与对应测试设计用例（Case ID、场景、预期结果）
- design.md 相关章节（接口契约、错误模型摘录）与允许触碰的文件范围
- 测试/构建命令、适用的 coding-standards 与领域技能名
- 返回契约：`DONE`（附证据行）/ `NEEDS_CONTEXT`（缺关键输入，回来重新打包）/ `BLOCKED`（越界或设计问题，附原因）

父会话职责：逐任务派发、校验返回的证据行、更新 plan.md 与 traceability、串联提交。subagent 返回 `BLOCKED` 提示设计问题时，父会话回 `devflow-design`，不催 subagent 硬做。

runtime 无 subagent 时退化为当前会话直接执行循环，纪律不变。

## 循环

### RED：写一个失败的测试

把当前用例的预期结果落成可执行断言。一个测试只验证一个行为，名字直接说出这个行为。

```cpp
// ✅ 名字说明行为；驱动真实代码；断言覆盖返回值、状态、副作用
TEST_F(ModeServiceTest, SetModeRejectsInvalidModeWithoutStateChange) {
  ASSERT_EQ(OK, mode_set(MODE_SAFE));          // Given：处于 SAFE

  EXPECT_EQ(ERR_INVALID_ARG, mode_set((mode_t)42));  // When：非法输入

  EXPECT_EQ(MODE_SAFE, mode_get());            // Then：状态不变
  EXPECT_EQ(0u, fake_event_queue_count());     // Then：没有发出事件
}
```

```cpp
// ❌ 名字空洞；只验证了 mock 被调用，没验证任何真实行为
TEST(ModeTest, Test1) {
  MockQueue q;
  EXPECT_CALL(q, push(_)).Times(0);
  mode_set_with_queue(42, &q);
}
```

**验证 RED（必做，不可跳过）**：运行测试，确认——

- 它**失败**而不是报错（编译错误/段错误要先修到"干净地失败"）
- 失败原因是**目标行为缺失**，不是拼写错误或测试环境问题
- 测试一写就通过？说明它没有验证新行为：要么行为已存在（确认后跳过该用例），要么测试写错了。

把命令与关键失败输出记为 plan.md 的 RED 证据行（含 commit 锚点）。

### GREEN：最小实现

只写让当前 RED 转绿的最少代码。不实现测试没有要求的功能，不引入设计没有批准的抽象，不顺手清理。

```c
/* ✅ 刚好让测试通过 */
int mode_set(mode_t mode) {
    if (mode != MODE_NORMAL && mode != MODE_SAFE) {
        return ERR_INVALID_ARG;
    }
    g_mode = mode;
    event_queue_push(make_mode_changed_event(mode));
    return OK;
}
```

```c
/* ❌ 测试只要求两个模式，却"顺便"做了模式注册表 + 钩子机制 */
int mode_set(mode_t mode) {
    const mode_descriptor_t *desc = mode_registry_lookup(mode);
    if (desc == NULL) return ERR_INVALID_ARG;
    if (desc->pre_hook && desc->pre_hook(mode) != OK) { ... }
    ...
}
```

**验证 GREEN（必做）**：当前测试通过；**完整测试套件**通过（无回归）；构建输出干净（无新增警告）。其他测试挂了 → 现在就修，不带病推进。把命令与通过摘要记为 plan.md 的 GREEN 证据行（含 commit 锚点）。

### REFACTOR：在绿灯上清理

只在全绿后进行。两顶帽子严格分开：GREEN 帽只加行为，REFACTOR 帽只改结构——**重构不改变任何可观察行为，期间不新增任何测试预期**。

做什么：消除本任务引入的重复、改善命名、提取函数、用常量替换魔法数（具体手法与判断见 `devflow-clean-code`）。每做一步跑一次测试，保持全绿。

边界：清理限于当前任务触碰的范围。发现需要跨模块的结构性重构、或想引入设计未声明的新抽象 → 登记为债务或回 `devflow-design`，不在任务内顺手做。REFACTOR 中发现还缺行为 → 摘下帽子，回 RED。

### 提交

每个任务完成（全绿 + 清理完）即提交一次，提交信息说明覆盖了哪些用例。小步提交让失败可定位、可回滚。

## 测试质量内建

评审时测试会被独立检查（`devflow-review`），但质量在编写时就要内建。最常见的三类弱测试：

**弱断言**——测试跑过了但什么都没证明：

```cpp
EXPECT_NE(nullptr, result);            // ❌ 只证明非空
EXPECT_EQ(OK, mode_set(MODE_NORMAL));  // ❌ 只查返回码，不查副作用

// ✅ 断言到具体值和全部可观察结果
EXPECT_EQ(MODE_NORMAL, mode_get());
ASSERT_EQ(1u, fake_event_queue_count());
EXPECT_EQ(MODE_NORMAL, fake_event_queue_last().payload.mode);
```

自检方法（mutation 思维）：**如果把实现里的关键一行改错，这个测试会失败吗？**不会 → 断言不够强。

**Mock 越界**——mock 了不该 mock 的东西：只 mock 真实边界（硬件、外部组件、慢速依赖、时钟）；不 mock 模块内部纯逻辑、不为测试给生产类加 test-only 方法、不验证"mock 被调用了"来代替验证行为结果。

**测试间耦合**——用例依赖执行顺序、共享可变全局状态、依赖真实时间。每个测试独立可重复：自带 setup/teardown，受控时钟。

完整的断言/命名/fixture/mock 判据见 `references/test-quality.md`。

## 合理化反驳

| 话术 | 现实 |
|---|---|
| 「这段太简单不用测」 | 简单代码也会坏。测试 30 秒，调试 30 分钟 |
| 「先写完实现再补测试，效果一样」 | 测试后补一写就过，证明不了任何东西；你失去了"看它失败"这唯一的证据 |
| 「我已经手动验证过了」 | 没有记录、不可复现、下次改动不会自动重跑 |
| 「写了几小时的代码删了可惜」 | 沉没成本。留着没有测试证明的代码才是负债 |
| 「测试太难写」 | 测试难写 = 设计难用。回设计简化接口，而不是绕过测试 |
| 「GREEN 时顺手重构更快」 | 行为变更和结构变更混在一个 diff 里，评审者无法分辨哪些变化是有意的 |
| 「先把后面几个用例的实现一起写了」 | 大切片失败时无法定位；一次一个用例 |

## 风险信号

- 测试一写出来就是绿的，而你说不出为什么
- evidence 里只有"测试通过"，没有它曾经失败的记录
- 一个任务的 diff 同时含行为变更和大量重命名/搬移
- 多个任务同时 in-progress
- 跳过完整套件，只跑新测试就宣布完成
- 为了让测试过而改弱断言，而不是修实现

## 验证清单

任务完成前逐项确认：

- [ ] 每个新行为都有先失败后通过的测试；失败原因当时已确认是行为缺失
- [ ] plan.md 中本任务的 RED/GREEN 证据行齐全（命令 + 关键输出 + commit 锚点），证据来自真实运行
- [ ] 完整测试套件通过；构建无新增警告
- [ ] 断言经得起 mutation 自检（改错实现关键行，测试会红）
- [ ] mock 只用于真实边界；没有 test-only 后门
- [ ] REFACTOR 没有改变行为；清理留在任务范围内
- [ ] plan.md 任务状态与 traceability.md 对应行已更新；本任务已提交
- [ ] 适用的语言/领域规范（coding-standards / embedded / automotive）已在实现中遵循

## 支撑参考

| 文件 | 用途 |
|---|---|
| `references/plan-template.md` | plan.md 模板：运行模式与门禁表、自包含任务结构、恢复指引、证据行 |
| `references/test-quality.md` | 断言强度、测试命名、fixture 设计、mock 边界的详细判据与正反例 |
