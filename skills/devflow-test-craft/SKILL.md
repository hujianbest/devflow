---
name: devflow-test-craft
description: 旧版 DevFlow 2.0 test craft 兼容说明。仅在迁移旧引用或理解历史测试质量透镜时使用；测试有效性现在归第二层 TDD / devflow-test-review 体系，不属于第三层代码内在质量扩展。
---

# DevFlow 测试匠艺（质量透镜）

## 兼容状态

本 skill 已不再属于 DevFlow 第三层“代码内在质量”。测试有效性、fail-first、测试金字塔、mock 边界和断言强度都服务于第二层 TDD / 功能正确，应迁入 `devflow-tdd-implementation`、`devflow-test-review` 及其 references。

新工作流不应主动叠加本 skill。若旧文档或旧工件引用本 skill，应按以下方式迁移：

- fail-first / RED-GREEN-REFACTOR → `devflow-tdd-implementation`
- 测试有效性裁决 → `devflow-test-review`
- 领域风险测试覆盖 → 适用领域约束 skill，如 `automotive-embedded-development`

## 总览

`devflow-tdd-implementation` 负责*纪律*（fail-first RED、最小 GREEN、fresh evidence），`devflow-test-review` 负责*裁决*（verdict）。本透镜负责两者中间最稀缺的部分：**怎么写出有效、稳健、可维护的测试**。

「测试通过」与「测试有效」是两回事：测交互的测试 refactor 一动就红、过度 mock 的测试在生产崩了还全绿。本透镜把这些判断编码出来。

## 它不是什么

- **不是流程节点**：不写 `progress.md`、不进 `next_action_or_recommended_skill`、不产生 verdict。
- **不替代 test-review**：它让你*写出更好的测试 / 更准地审*，`devflow-test-review` 仍是唯一裁决者。
- **不放宽 fail-first**：每条用例仍必须有真实 RED 失败证据，仍归属 Current Active Task。

## 何时叠加

| 调用方 | 在哪个步骤叠加 |
|---|---|
| `devflow-tdd-implementation` | 「从测试设计落地测试」「RED」步骤——决定写什么用例、怎么断言 |
| `devflow-test-review` | 评分测试有效性时——作为「好测试」的判别标准 |

## 核心判断

### 1. 测试金字塔与 test sizes

按金字塔分配投入——绝大多数应是小而快的：

```
        E2E / 业务场景（~5%）    完整流程、真实环境
     集成 / 接口（~15%）        组件交互、接口边界
  单元（~80%）                 纯逻辑、隔离、毫秒级
```

| Size | 约束 | 速度 |
|---|---|---|
| **Small** | 单进程、无 IO / 网络 / 设备 | 毫秒 |
| **Medium** | 本机多进程、localhost、test fixture | 秒 |
| **Large** | 多机 / 真实外设 / HIL / 仿真 | 分钟 |

决策：纯逻辑无副作用 → 单元（small）；跨接口 / 状态 / 硬件抽象 → 集成（medium）；关键端到端路径 → 业务场景（large，限关键路径）。

### 2. 测状态不测交互（最重要）

断言**结果 / 可观测效果**，不断言「调用了哪个内部函数」。测交互的测试在 refactor（行为不变）时会无故变红，是脆弱之源。

```text
✓ 好（测状态）：调用 sort 后，断言输出数组有序、长度不变
✗ 坏（测交互）：断言内部调用了 compare() 恰好 N 次 / 调了某私有方法
```

**判别 tell**：断言里出现「被调用次数 / 被调用顺序 / 调了哪个 mock 方法」而不是「最终状态 / 返回值 / 可观测副作用」→ 多半在测实现细节。

### 3. DAMP over DRY

测试里**可读性 > 去重**。每个用例应像一段独立规格，不必跟着共享 helper 跳转才看懂。生产代码 DRY，测试代码 DAMP：适度重复 input 构造是可以接受的。

**判别 tell**：要读三层 setup helper 才知道某用例到底在验证什么 → 过度 DRY，摊开。

### 4. Mock 克制

优先用真实实现，越真越能抓真 bug：

```
real（最优，抓真 bug） > fake（内存版依赖） > stub（返回固定值） > mock（验证交互，慎用）
```

只在依赖**慢 / 不确定 / 有不可控副作用**（真实外设、网络、计时、烧写）时才用 test double，且尽量用 fake/stub 而非 interaction mock。过度 mock 会造出「测试全绿、生产全崩」。

**判别 tell**：一个用例里 mock 了 5 个依赖、断言全是「mock 被调用」→ 这测的是「我写的 mock」，不是被测代码。

### 5. AAA + 一断言一概念 + 描述性命名

- **Arrange-Act-Assert**：结构清晰，三段分明。
- **一个用例验证一个概念**：`拒绝空标题` / `裁剪首尾空格` / `超长标题报错` 分开写，不要塞进 `validates correctly`。
- **命名即规格**：`completeTask 对已完成任务是幂等的` 远胜 `test3` / `works`。名字读起来像被测行为的断言。

### 6. 嵌入式测试补充（与 DevFlow 协同）

把上述通用匠艺与 DevFlow 的嵌入式 / 证据要求接起来：

- **覆盖类型**：每个功能点要覆盖 happy / boundary / exception / regression；`modify` row 要有「证明新语义 + 保留旧行为」的用例，`remove` row 要有「旧入口删除后可观察语义」的用例。
- **嵌入式风险矩阵**：内存 / 并发 / 实时性 / 资源 / 错误处理各维度要有用例或显式「不涉及」判定依据。
- **fail-first 证据**：每条用例必须先有真实 RED 失败证据（命令 + 退出码 + 失败摘要），不能用旧 GREEN 冒充新 RED。
- **mock 边界声明**：哪些依赖必须 mock、哪些必须真实运行，要在测试设计里声明且不破组件 SOA 边界。

## 测试反模式速查

| 反模式 | 问题 | 修法 |
|---|---|---|
| 测实现细节 | refactor 即红，行为没变 | 测输入 / 输出 / 状态 |
| flaky（依赖时序 / 顺序） | 侵蚀信任 | 确定性断言、隔离状态 |
| 测框架 / 三方代码 | 浪费 | 只测你自己的代码 |
| 过度 mock | 全绿但生产崩 | real>fake>stub>mock |
| 无隔离 | 单跑过、合跑崩 | 各用例自起自清状态 |
| 首次就通过的「RED」 | 没证明任何东西 | 必须先真实失败 |

## 与 DevFlow 纪律的协同

- 本透镜决定「写什么 / 怎么断言 / 怎么 mock」；fail-first 顺序、单 active task、fresh evidence 仍由 `devflow-tdd-implementation` 强制。
- 测试设计仍是 AR 实现设计的**章节**（不拆独立 `test-design.md`）；本透镜提升其中用例的质量，不改变这条硬约定。
- `devflow-test-review` 仍是唯一有效性裁决者；本透镜给它一套可判别的「好测试」标准。

## 反向理由化（Common Rationalizations）

| 话术 | 反驳 |
|---|---|
| 「断言它调用了某函数，最直接」 | 那是测交互，refactor 即脆。断言最终状态 / 返回值 |
| 「都 mock 掉跑得快」 | 过度 mock = 测你的 mock。real>fake>stub>mock，只在边界 mock |
| 「测试别重复，全抽成 helper」 | 测试 DAMP > DRY；可读性优先，适度重复可接受 |
| 「一个用例多断几个点省事」 | 一断言一概念；失败时才知道是哪条行为坏了 |
| 「类似用例存在，复用旧 GREEN 当新 RED」 | 新行为必须有新的真实 RED 证据 |
| 「只测 happy path，异常以后补」 | boundary / exception / regression 是有效性的核心，缺则 test-review 打回 |

## Red Flags

- 断言「被调用次数 / 顺序 / 私有方法」而非状态。
- 一个用例 mock 一堆依赖且只断 mock 调用。
- 测试名是 `works` / `test3` / `validates correctly`。
- 一个用例塞多个不相关断言。
- 「RED」首跑即过。
- 只有 happy path，无边界 / 异常 / 回归 / 嵌入式风险用例。

## 自检清单（让测试更有效，但不替代 test-review）

- [ ] 用例层级符合金字塔（多数 small）
- [ ] 断言的是状态 / 返回 / 可观测效果，不是内部交互
- [ ] 测试可读、DAMP、AAA 结构清晰、命名即规格
- [ ] 只在必要边界用 test double，优先 real/fake
- [ ] happy / boundary / exception / regression 均覆盖；`modify`/`remove` 覆盖 baseline delta
- [ ] 嵌入式风险矩阵各维度有用例或显式判定依据
- [ ] 每条用例有真实 fail-first RED 证据

## DevFlow 约定

本 skill 遵循 `using-devflow` 的「DevFlow 共同约定」章节（产物布局 / progress 字段 / handoff 字段 / profile / 节点表）；项目 `AGENTS.md` 可覆盖等价路径与模板。本 skill 是 craft 透镜，**不**写 progress/handoff，**不**产生 verdict。
