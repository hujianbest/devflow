---
name: devflow-clean-code
description: 在 DevFlow 的实现（devflow-tdd-implementation 的 GREEN/REFACTOR）、代码评审或完成门禁里，需要把"测试能过的代码"提升为"读得懂、改得动、值得长期持有的代码"时使用。提供命名、函数、控制流、注释、错误处理、代码气味与重构手法的具体心法与示例。不用于设计统筹、语言专属规范、测试有效性或运行时路由。
---

# DevFlow Clean Code

## 一句话

> **代码被读的次数远多于被写的次数。整洁代码的唯一标准，是让下一个读它的人（包括 review 的人、半年后的你）用最小认知负担读懂、并安全地改对。**

"能跑"是测试（第二层）的事；"好不好"是这一层的事。一段把测试跑绿、却让 reviewer 必须连读五个文件才敢动的代码，是合格的功能、失败的内在质量。

本 skill 是 DevFlow 第三层"代码内在质量"的**编码统筹**。它是被实现 / 代码评审 / 完成门禁**消费的判据库**，不是流程节点：不产出 `Current Stage`、`Next Action Or Recommended Skill` 等运行时字段，不产 review verdict，不替 TDD 纪律（RED 必须先失败、GREEN 不做 cleanup、REFACTOR 不加行为），运行时路由一律回 `devflow-router`。

## 怎么用这个 skill

整洁代码不是写完再"美化"，而是 TDD 节奏里的固定动作：

- **GREEN 时**：写**最简单能让当前 RED 变绿**的代码（§1）。不顺手抽象、不顺手优化、不超范围（§2）。
- **REFACTOR 时**：戴上"重构帽"，在 GREEN 之后、行为不变的前提下，扫一遍 §3-§6（命名、函数、控制流、错误、气味），把这一刀的代码收拾干净再交评审。
- **每次只动一薄片**：一个 active task、一组测试用例、一个可回退的提交（§2）。

深层细节（代码气味 → 重构手法全目录、Tidy First 微整理清单、更多 before/after）在 `references/code-smells-and-refactorings.md`，需要时再读。

---

## 1. Rule 0：最简单能工作的实现

GREEN 阶段只写让当前 RED 变绿的最少代码。这不是"偷懒"，是 YAGNI：未被测试驱动、未被设计批准的代码，是没有需求撑着的负债。

<Bad>
```typescript
// 当前 RED 只要求"重试 3 次"，却提前造了配置体系。
async function retry<T>(fn: () => Promise<T>, opts?: {
  maxRetries?: number; backoff?: "linear" | "exp"; onRetry?: (n: number) => void;
}): Promise<T> { /* 一堆没有测试驱动的分支 */ }
```
</Bad>

<Good>
```typescript
async function retry<T>(fn: () => Promise<T>): Promise<T> {
  for (let i = 0; i < 3; i++) {
    try { return await fn(); } catch (e) { if (i === 2) throw e; }
  }
  throw new Error("unreachable");
}
```
</Good>

需要更多能力时，由**下一个测试**驱动出来——而不是现在凭想象铺开。

---

## 2. 范围纪律与薄切片

> **只改被当前 task 要求改的东西。** 路过发现的问题登记成 follow-up，不顺手改。

不顺手修相邻 bug、不重构无关文件、不删不理解的旧逻辑、不在 spec/design/task 之外加功能。原因有三：(1) 顺手改让 review 无法区分"功能变更"与"清理"，diff 不可审；(2) 失败时无法定位是哪一刀引入的；(3) 范围一旦松动就停不下来。

**薄垂直切片**：一次只完成一个 active task 的一组测试用例，每片可构建、可测试、可回退。多个 in-progress task、大重构和功能改动混在一个提交里，都是切片太厚的信号。

**Two Hats（Kent Beck）**：你要么在"加功能"，要么在"重构"，**绝不同时**。换帽子要明确，且各自是独立的提交。

> 路过看到值得改的东西是好事——但写进 follow-up / Refactor Note 的 escalation，而不是塞进这一刀。

---

## 3. 命名：第一生产力

命名是降低认知负担最便宜、最有效的手段。差命名逼读者去读实现才能懂意图。

| 规则 | 反例 → 正例 |
|---|---|
| 名字表达意图，不表达类型/实现 | `List<int> d` → `List<int> elapsedDays` |
| 用领域词汇，不用泛词 | `data` / `info` / `manager` / `handle()` → `invoice` / `retryBudget` / `chargeCard()` |
| 布尔读起来是判断句 | `flag` / `status` → `isExpired` / `hasPendingWrites` |
| 函数名是动词短语，类名是名词 | `temperature()`（取值却像名词）→ `readTemperature()` |
| 避免缩写与魔法数 | `if (s == 2)` → `if (state == State.CLOSED)` |
| 同一概念同一词，别换着叫 | 一会 `fetch`、一会 `get`、一会 `load` → 统一 |

**测试**：把函数/变量名读给一个不看实现的人听，他能猜对它做什么吗？猜不对就重命名。

---

## 4. 函数：小、单一、单层抽象

- **做一件事**：函数名里有"and"，或你要写注释分段（"// 第一步…… // 然后……"），就是该拆的信号。
- **单一抽象层级（SLAP）**：一个函数里不要既有高层意图（`chargeCustomer()`）又有底层细节（拼 SQL、移位运算）。把细节下沉到被调函数。
- **参数少**：0-2 个最好；≥4 个、或一串布尔开关，往往是"该把它们打包成对象"或"该拆函数"的信号（避免 connascence of position）。
- **没有输出型参数 / 隐藏副作用**：`appendFooter(report)` 偷偷改全局，比返回值更难追。
- **早返回压平嵌套**：

<Bad>
```c
int handle(Req *r) {
  if (r != NULL) {
    if (r->valid) {
      if (has_quota(r->user)) {
        return do_work(r);     // 真正的逻辑被埋在 3 层里
      } else { return ERR_QUOTA; }
    } else { return ERR_INVALID; }
  } else { return ERR_NULL; }
}
```
</Bad>

<Good>
```c
int handle(Req *r) {
  if (r == NULL)            return ERR_NULL;     // 卫语句先排除异常
  if (!r->valid)           return ERR_INVALID;
  if (!has_quota(r->user)) return ERR_QUOTA;
  return do_work(r);                              // 主路径在最外层，一眼可见
}
```
</Good>

---

## 5. 注释与控制流

- **注释解释"为什么"，不复述"做什么"**。`i++; // 加一` 是噪声；`// 跳过 BOM 头，部分编码器会写入它` 是金子。
- **删掉所有死东西**：注释掉的历史代码、僵尸开关、永假分支、没人调的函数——它们是认知噪声和"未知的未知"的温床。版本控制就是历史，不需要用注释当备份。
- **不要用注释补偿坏代码**：需要一段注释才能看懂的复杂表达式，先重命名/抽函数，让代码自解释，注释往往就不需要了。
- **控制流直白**：避免在一个表达式里塞副作用；循环/条件意图明显；嵌套尽量 < 3 层。

---

## 6. 错误处理：不只走 happy path

- **错误不能被静默吞掉**：`catch (e) {}` / 忽略返回码，是把"未知的未知"埋给生产环境。
- **失败路径也要可审**：资源（句柄、锁、内存、事务）在错误路径上同样要释放/回滚——获取与释放成对，最好用 RAII / defer / context manager 绑定。
- **校验外部输入**：来自用户、网络、文件的输入在边界处校验，非法输入返回团队规定的错误语义。
- **能消掉的错误就消掉**：见 `../devflow-clean-design/SKILL.md` §5"把错误设计掉"——错误处理最好的代码是不需要错误处理的代码。
- **错误信息带上下文**：`"open failed"` → `"open failed: %s (path=%s)"`，让排障的人不用再猜。

> 语言专属的错误/资源规则（C 的 errno、C++ 的异常安全与 RAII 细则）由 `c-coding-standards` / `cpp-coding-standards` 提供；本节是通用判据。

---

## 7. 重构纪律与 Refactor Note

REFACTOR 只在 GREEN 之后、**不改变行为**、且留在当前 task 边界内进行。每次 cleanup 后重跑测试保持绿。

Refactor Note（写进 `implementation-log.md`，是 code-review CR8 的核心输入）至少记录：

1. **做了什么 cleanup**：用 Fowler 词汇命名（Extract Function、Rename、Inline、Replace Magic Number…）。
2. **为什么仍在当前 task 范围内**。
3. **重构后重跑了哪些验证**（命令 + 结果）。
4. **登记为后续债务的问题**（escalation triggers）：跨 ≥3 模块的结构重构、改组件边界、引入设计未声明的新抽象层——这些**不能**在 task 内悄悄做，登记上抛。

---

## 反向理由化（Common Rationalizations）

命中任意一条 → 停下，按"反驳"动作执行。

| 话术 | 反驳 |
|---|---|
| 「顺手改一下更干净」 | 不在当前 task 范围的清理就是范围扩张，让 diff 不可审。登记成 follow-up |
| 「先抽象好以后省事」 | 抽象必须由当前真实用例支撑（见 clean-design §4）。无据抽象是负债，不是省事 |
| 「GREEN 时一起重构更快」 | 违反 Two Hats。两顶帽子混戴 → reviewer 无法分辨行为变更与清理 |
| 「这个命名我自己懂」 | 代码是写给 reviewer 和未来维护者的，不是写给现在的你的。读不懂就重命名 |
| 「错误基本不会发生，先不处理」 | "基本不会"在生产环境就是"一定会"。要么处理，要么用设计把它消掉，不能静默吞 |
| 「注释一下就懂了，不用改代码」 | 需要注释才懂的复杂代码，先让代码自解释；注释补偿坏代码是在掩盖问题 |
| 「重构很小，没必要写 Refactor Note」 | 无 note = 不可审，code-review CR8 直接 `需修改`。不存在"没什么好写"的合法情形 |

## Red Flags — 看到就停

- RED 还没失败就开始写实现 / 复用旧 GREEN 当新 RED
- GREEN 阶段在 refactor，或一个提交里既加功能又重构
- 函数名带 "and"、或要靠注释分段
- 嵌套 > 3 层、参数 ≥ 4 个、一串布尔开关
- `catch {}` / 忽略返回码 / 错误信息没有上下文
- 注释掉的代码、永假分支、没人调用的函数被留着
- 改了相邻文件 / 顺手修了无关 bug / 删了不理解的旧逻辑
- 魔法数、`data`/`info`/`tmp`/`mgr` 这类无意义名

**任意一条都意味着：要么违反了 TDD 纪律，要么在给读者增加认知负担。停下修正。**

## 卡住时

| 问题 | 动作 |
|---|---|
| 函数太长不知怎么拆 | 找"做第二件事"的段落 → Extract Function，名字写它的意图 |
| 重复代码要不要抽 | 看是否真重复且稳定（Rule of Three）；偶然相同先别抽 |
| 命名想不出 | 说明职责还不清；先说清这段到底负责什么，名字随之而来 |
| 错误处理铺满 happy path | 用卫语句早返回，或回 clean-design"把错误设计掉" |
| 想顺手改的东西很多 | 全部登记到 follow-up / Refactor Note escalation，本刀只做 task |
| cleanup 会动到组件边界 / 跨多模块 | 停，登记 escalation，交 `devflow-router` / code-review，不在 task 内做 |

## 验证清单

- [ ] 实现只覆盖当前 active task；GREEN 阶段没有 cleanup
- [ ] REFACTOR 没有改变行为，且留在 task 边界内
- [ ] 命名表达意图，可被不看实现的人读懂；无魔法数 / 泛词
- [ ] 函数做一件事、单一抽象层级、嵌套与参数受控
- [ ] 控制流用卫语句压平，主路径一眼可见
- [ ] 错误路径完整：不静默吞错、资源成对释放、外部输入已校验
- [ ] 无死代码、无注释掉的历史残骸；注释解释"为什么"
- [ ] 路过问题已登记，未顺手扩张范围
- [ ] Refactor Note 完整（cleanup / 范围理由 / 验证 / escalation）
- [ ] 适用编码规范（`c-coding-standards` / `cpp-coding-standards`）与领域约束已消费或明确 N/A

## 与扩展 skills、其它层的关系

- 语言级规则（命名约定、格式化、lint、语言危险点、RAII/异常安全/errno 细则）→ `c-coding-standards` / `cpp-coding-standards`。
- 领域级约束（内存/实时性/中断/资源、ASIL/SOA 等）→ `embedded-development` / `automotive-development`。
- 模块/接口/抽象层面的结构问题 → `../devflow-clean-design/SKILL.md`。
- RED/GREEN/REFACTOR 的执行纪律与证据 → `devflow-tdd-implementation`；测试本身是否有效 → `devflow-test-review`。

## 深入参考

| 文件 | 用途 |
|---|---|
| `references/code-smells-and-refactorings.md` | 代码气味 → 重构手法全目录、Tidy First 微整理清单、端到端 before/after |
| `../devflow-clean-design/SKILL.md` | 第三层设计内在质量统筹 |
