---
title: DevFlow Agent 知识沉淀可行方案
status: options
date: 2026-08-23
source-note: 用户给出的微信原文 https://mp.weixin.qq.com/s/JV4-oPP0jjsBCZ4tW3Gy1g 在当前环境被验证墙拦住，正文未能完整读取。下文按该文常见的 2026 知识编译/Skill 过程记忆思路，对齐 DevFlow 已落地的 skill、learn、wiki 三套机制。
---

# DevFlow Agent 知识沉淀可行方案

DevFlow 已经用 skill 把工作流钉死了：先规范、再设计、再 TDD、再独立评审，最后 ship。现在要补的是，agent 做完一次之后，下次还能用上什么。

这篇只谈可行方案，不改生命周期，不加新的 gate。

## 1. 文章里真正能借的，不是“再建一个知识库”

微信原文这边读不到全文。2026 年能对上的公开材料里，Karpathy 的 LLM Wiki、compound engineering 的 compound 步、以及把经验写成 Skill 的做法，都落在同一件事上：

查询时再去理解原文，等于每次重新解释执行。Agent 需要的是提前编译好的、带结构的知识，而不是一大袋片段。

对 DevFlow 有用的只有四条，其余可以丢掉：

1. **编译，不要检索原文凑答案。** 原料进一次，变成互链、带状态、带来源的页面。下次读编译层，不够再下钻源。
2. **Skill 管“怎么干”，不是知识本体。** Skill 是过程记忆：步骤、门槛、停止条件。业务规则、根因、取舍不该塞进 `SKILL.md`。
3. **用知识也要能长知识。** 高价值的综合可以回写，但要有门槛，不能把每次闲聊都存下来。
4. **知识也要 lint。** 过期、冲突、孤儿页、和当前代码打架，都必须能被发现，而不是靠人想起来才改。

Rotifer 那种跨 agent 竞技传播、向量库当主检索、扫描本机会话当事实源，都不适合 DevFlow。仓库里已经否过后两项；第一项会把“当前真相唯一”拆掉。

## 2. 先分四层，否则方案会对不上号

Agent 嘴里的“知识”其实不是同一种东西。混在一个目录里，检索会把过期经验当成现行规格。

| 层 | 回答的问题 | DevFlow 里已经在哪 | 权威 |
|---|---|---|---|
| 过程 | 这一步该怎么走、什么时候停 | `coding-skills/*`、`commands/` | 约束行为，不陈述业务事实 |
| 当前真相 | 现在系统是什么、代码实际做什么 | `specs/spec.md`、`specs/design.md`、代码、测试 | 最高 |
| 情节证据 | 这一次 AR 怎么做成的 | `specs/changes/` → `specs/archive/` | 历史事实，不是现行规格 |
| 编译知识 | 以后还能不能少踩一次坑 | `docs/learnings/`、`wiki/` | 低于当前真相，可失效 |

Skill 继续管第一层。知识沉淀只碰第四层，并且必须能指回第三层或第二层的磁盘证据。聊天可以帮人指出“沉淀哪一条”，不能当事实来源。这条在 `devflow-learn` 里已经写死，后面任何方案都不能松。

## 3. 现状：零件齐了，晋升关系没有

现在仓库里其实已经有三套相关能力：

- **过程约束：** `using-devflow` 到 `devflow-ship` 的阶段 skill，外加语言/领域 overlay。
- **交付经验：** `devflow-learn` 从已归档 AR 抽出一条 learning，写入 `docs/learnings/`。`using-devflow` 开工前做有界 lookup。Ship 之后可以提捕获建议，但不是门禁。
- **领域编译：** `domain-knowledge-library/` 按 Karpathy 那套做 init / update / ingest / query / lint，编译结果落在 `wiki/`。

缺的是中间那一跳：

- 开工只查 `docs/learnings/`，领域问题不会自动走 `wiki/`。
- learning 再高频，也不会晋升成 overlay skill。
- 业务事实、工程经验和过程规则三套东西，使用方没有一张硬边界图。
- 查询回写只存在于领域 wiki 的可选分支，没有接到交付流。
- 两套知识库并存是对的，但 agent 不知道什么问题读哪一套。

所以后面的方案不是“从零建库”，而是选一条编译和晋升路径，把已有零件接上。

## 4. 五条可行路径

### 方案 A：把现有闭环跑满

不新增知识形态。只让已经设计好的环真的转起来。

做什么：

- Ship 成功后的候选判断要稳定：有复用价值才问人，没有就明确 no-op。
- 目标仓库的 `AGENTS.md` / `CLAUDE.md` 必须能让新会话发现 `docs/learnings/`。现在 `discoverability` 只报告 gap，不改文件；需要一条显式的初始化动作，而不是 capture 顺手改指令文件。
- lookup 继续有界：active-only、最多五份、截断必须收窄。
- stale 只进 `refresh-audit`，当前 AR 不准顺手改 learning。

适合谁：已经在用 DevFlow 交付、只是经验留不住的团队。

代价：解决不了“订单取消规则是什么”这种领域问题。那不是 learning 的职责。

这是成本最低、也最符合现有契约的一步。后面无论选哪条，A 都得先做。

### 方案 B：领域问题走编译 wiki，不走 RAG

这就是 `domain-knowledge-library` 已经在走的路，和文章里的知识编译是同一类。

原料是代码、契约、人手文档、点名原文。编译层是 `wiki/`。操作是 ingest / update / query / lint。查询先读 `index.md`，够用就不要打开源码。

硬限制：

- `specs/spec.md` 和 `specs/design.md` 禁止被编译成另一份“当前真相”。wiki 可以解释领域词和跨系统流程，不能取代 canonical。
- 代码证明 AS-IS；设计文档证明意图；两者打架进入冲突，不由模型选边。
- 查询默认不写页。只有综合了多页、以后还会被问、并且人同意，才回写。

适合谁：业务词多、跨服务、规则有例外、新人 agent 每次都要从代码猜语义的仓库。

代价：冷启动贵。没有人工确认的业务语义必须停在 draft。把它做成“全公司本体”会直接失败。

### 方案 C：把改变“怎么干”的经验晋升为 overlay skill

compound engineering 说要把 learning 编码成能 priming 下次会话的指令。DevFlow 里对应的不是再写一篇散文，而是晋升。

判断标准只有一条：这条经验是否改变了以后的工作方式。

- “这个超时要先看网关再看重试队列” → 继续留在 `docs/learnings/`。
- “凡是改通知重试，必须先补契约测试，禁止只改客户端” → 这是过程规则，可以进项目 overlay 或领域 skill。
- “Java 里这类 Optional 用法以后禁止” → 进 `java-coding-standards`，走 `coding-standards-creator` 的契约。

晋升必须人工批准。Skill 变胖是这条路最大的失败模式。一条规则进了 `SKILL.md`，每个相关会话都要付 token，而且会和阶段 skill 抢边界。

适合谁：同一类坑已经在多个 AR 里出现，lookup 每次都能命中，但 agent 还是不改手。

代价：没有晋升门槛就会把 knowledge store 和 workflow 糊成一坨。第一版必须规定：一次只晋升一条，正文仍指向 learning 或 archive，skill 里只留可执行规则。

### 方案 D：按实体做 Claim / Evidence 时间线

`devflow-learn` 的 schema 1.1 已经要求 claim 对 evidence。方案 D 是把这套东西从“一篇经验一篇文件”扩成“一个实体一条时间线”。

同一条业务规则、同一个接口、同一个故障模式，后来的证据进来就重写 compiled truth，旧主张标 `superseded` 或 `disputed`。这是 agent-knowledge / compiled-memory 那一路，用来回答“我们现在怎么做、以前为什么不是这样”。

适合谁：规则会变、历史兼容多、口头传说和代码经常打架的领域。资金、权限、履约这类地方值得。

代价：比 wiki 页更重。要实体 ID、时间线、矛盾检测。第一版如果全仓铺开，维护成本会超过收益。只对少数高风险实体做，别做成通用记忆层。

### 方案 E：晋升阶梯，四层各司其职

这是中期目标架构，不是第一周就要一次落地的大系统。

```text
archive 证据
    → docs/learnings/     可复用的工程经验
    → wiki/ concept       稳定下来的业务事实 / 跨系统语义
    → overlay skill       已经改变工作方式的规则
```

规则：

- 默认只从 archive 抽 learning。没有复用价值就停。
- 一条 learning 被多次 lookup 命中，并且说的是领域事实而不是排障手法，才考虑编进 wiki。
- 一条规则已经在约束“以后怎么干”，才考虑写进 overlay。
- 任何一层和 canonical / 代码冲突，当前真相赢，下层标 stale。
- 禁止回流：learning 不能改 archive，wiki 不能改 spec，skill 不能因为迁就旧经验去改代码。

A、B、C、D 都是这条阶梯上的一段。E 的价值是防止有人把四层焊成一个“超级知识库”。

## 5. 怎么选

按仓库现在的痛点选，不要按概念完整度选。

| 你实际卡在哪 | 选 |
|---|---|
| 交付做过，下次照样踩坑 | 先做 A |
| Agent 每次从代码猜业务词 | 做 B，领域问题走 wiki query |
| 同一条过程红线反复被违反 | 做 C，晋升一条 overlay |
| 同一规则存在多版说法，还在吵 | 对那几个实体做 D |
| 两套库都有了，agent 读串了 | 按 E 画边界，不要再加第五个目录 |

默认建议：把 A 做满，再用 E 把 learn / wiki / skill 的分工写进 `using-devflow` 的入口判断。B 已经有技能集，缺的是开工路由，不是再写一套 wiki。C 和 D 都要有重复命中或真实冲突再开，不要预防性建设。

`using-devflow` 里补一段很便宜的分流就够：

```text
问题是现行行为或设计    → 读 canonical / 代码 / 测试
问题是这次 AR 怎么做成  → 读 archive
问题是以前类似坑怎么解  → lookup docs/learnings/
问题是领域词、跨系统规则 → domain-knowledge-query
问题是这一步怎么走      → 阶段 skill / overlay
```

五路都找不到，就说不知道，不要用聊天记忆补。

## 6. 明确不做

这些方案看起来像“更完整”，但会破坏 DevFlow 已经花代价保住的东西：

- 向量 RAG 当主检索。wiki 和 learning 这个规模，index + 有界 grep 够用。RAG 找不到冲突和 supersede。
- 扫描 Cursor / Claude / Codex 本机会话当事实源。隐私和不可验证是同一类问题。
- 知识捕获失败就挡住 Ship，或把 learn 做成 R4。
- 用 wiki 或 learning 复制一份 `spec.md` / `design.md`。
- capture 自动 commit、自动开 PR、自动全库 refresh。
- 把所有 learning 晋升成 skill。过程约束会胀死。
- 跨仓库、跨 agent 的知识进化网。那是另一套产品，不是 DevFlow 的交付内核。

## 7. 和理念的对齐

`devflow-philosophy.md` 要求人在环上审查，不在环里替模型干活。知识沉淀也得守这条：

- 模型负责从磁盘证据编译候选；
- 人批准学习点、领域语义和 skill 晋升；
- 编译层永远低于 canonical、代码和测试。

`devflow-knowledge-capture-design.md` 和 `team-domain-knowledge-base-design.md` 已经把 A、B 的细节写过了。本文不重复字段和目录，只补一件事：skill、learning、wiki 之间怎么晋升，以及先做哪一段。

若微信原文的重点其实落在某一条（只讲编译 wiki，或只讲把经验写成 skill），选对应的 B 或 C 即可，不必五条一起上。分层本身不依赖那一篇的原话。
