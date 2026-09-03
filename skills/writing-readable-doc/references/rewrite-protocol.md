# 保义改写协议

可读性改写只允许改变表达，不允许改变文档承诺的事实。本文给出不可触碰清单、改写步骤、验证方法和典型破坏案例。任何一条验证不通过就回退整次改写，不在解释里辩护。

## 一、两层划分

| 层 | 内容 | 可否改写 |
|---|---|---|
| 规范层 | 需求条目、验收、阈值、契约、稳定 ID、delta 操作的控制信息 | 逐字不动 |
| 表达层 | 导语、背景、理由、影响与风险叙述、方案说明、决策正文、过渡句 | 可改 |

判断不确定时按规范层处理：漏改一句啰嗦的说明，代价远小于改坏一条验收。

## 二、不可触碰清单

### 通用

- 稳定 ID 与编号：`FR-xxx`、`IFR-xxx`、`NFR-xxx`、`CON-xxx`、`ASM-xxx`、`EXC-xxx`、`DS-xxx`、`DD-xxx`、`DEC-xxx`、`TC-xxx`。
- 反引号内的一切内容：标识符、错误码、路径、命令、字段名、接口签名。
- 数字、单位、比较符、统计口径：`50 ms`、`≤`、`P99`、`4 MB`、`3 次`。
- 追溯表的列结构与锚点。
- `change.json` 的任何字段（本技能不改结构化文件）。

### `srs.md`

- EARS Statement 的关键词与结构：`WHEN` / `WHILE` / `IF` / `WHERE` / `THE` / `SHALL`。
- Given/When/Then 验收的条件与预期文本。
- QAS 五要素：Stimulus Source、Stimulus、Environment、Response、Response Measure。删一个要素等于删一条需求。
- Source 引用（单据号、缺陷号、上游需求 ID）。
- `CON-xxx` 的约束与验证方式。

### `delta-spec.md` / `delta-design.md`

- operation 类型：`ADDED` / `MODIFIED` / `REMOVED` / `RENAMED`，及其固定执行顺序。
- target、selector、canonical 章节路径与实体键。
- 基线摘录（base excerpt）与 digest：它是逐字引用，改一个字就让合并证据失效。
- 局部 before/after 内容与 resulting local content。
- preservation clause：明确保留了哪些未涉及语义。
- `RENAMED` 的 from/to。

### `specs/spec.md` / `specs/design.md`

- 章节标题：它是稳定显示名。改标题必须走 delta 的 `RENAMED` 操作，不是润色。
- 章节编号、功能编号、接口与软件单元实体键。
- `baselineStatus`、provenance、评审与确认记录。

### `reviews/` 与 `closeout.md`

- reviewer 原文与 verdict：评审记录按原样落盘，不得改写。
- finding 的位置、严重级、分类、Resolution 文本。
- DoD 结论、人工确认记录、归档路径。

只有在评审记录之外的交接说明里，才可以另写一份更易读的摘要，并注明它是摘要。

## 三、改写步骤

1. **建立基线**：改写前保存一份副本或确认工作树干净，`git status` 无未提交变化，改写单独成一批。
2. **切层**：通读一遍，标出规范层片段。规范层片段在本次改写中只读。
3. **登记内容缺陷**：模糊阈值、缺失事实、互相矛盾的表述，全部记成 Open Question 或 finding，写明去向阶段与 owner。**不在改写中消化。**
4. **结构改写**：按 `doc-smell-catalog.md` 的顺序处理结构层与语义层异味（模板复读、结论后置、术语漂移、无锚点断言）。
5. **句子改写**：拆长句、还原名词化、删空转句（细则见 `zh-writing-rules.md`）。
6. **格式统一**：中英空格、全角标点、单位与统计口径、表格列对齐。
7. **验证**：执行第四节的全部检查。
8. **记录**：给出改写清单与保义证据，格式见第六节。

## 四、验证

```bash
# 1. 逐词 diff：确认改动没有落在规范层片段上
git diff --word-diff -- <doc>

# 2. 稳定 ID 集合
rg -o '\b(FR|IFR|NFR|CON|ASM|EXC|DS|DD|DEC|TC)-[0-9]+' <doc> | sort | uniq -c

# 3. 数字与单位集合（先去空格，避免 50ms → 50 ms 的格式修正误报）
rg -o '[0-9]+(\.[0-9]+)?\s*(ms|us|s|Hz|KB|MB|GB|%|次|条)' <doc> | tr -d ' ' | sort | uniq -c

# 4. 规范关键词计数
rg -c 'SHALL|WHEN|WHILE|WHERE|Given|When|Then' <doc>

# 5. 反引号内容集合
rg -o '`[^`]+`' <doc> | sort | uniq -c

# 6. delta 操作关键词计数
rg -c 'ADDED|MODIFIED|REMOVED|RENAMED' <doc>
```

把改写前后的输出逐项对比，判据分两级：

| 项 | 硬条件 | 允许的变化 |
|---|---|---|
| 2、3、5 | 集合一致：不新增、不丢失任何 ID、数值或反引号内容 | 出现次数可变。拆句、并入表格、改成流程列表都会重复引用同一个 ID 或错误码 |
| 4、6 | 计数不变 | 无。规范关键词与 operation 关键词的数量变化意味着规范层被动过 |
| 1 | 全部差异落在表达层 | 无 |

次数变化必须写进改写记录，并说明是哪次重排造成的。次数减少要逐处指出删掉的是哪句表达层文字；说不清就是删过规范内容，回退。集合出现增减、或第 4、6 项计数变化，一律回退，不解释。

新增内容需要额外一条判断：改写不得引入文档原本没有的事实。补充的原因、目的、影响、数字，只要没有来源，就是幻觉，即使读起来更通顺。

## 五、破坏案例

### 5.1 阈值被“润色”掉

```markdown
❌ 原文：WHEN 收到 SetConfig 请求 THE 配置模块 SHALL 在 50 ms 内返回结果。
   改写：配置模块会尽快响应 SetConfig 请求。
后果：EARS 结构消失、阈值消失，需求不再可测，R1 应判 critical。
```

### 5.2 QAS 要素被合并

```markdown
❌ 原文：Environment：设备处于低功耗模式且持久化区域剩余空间 < 64 KB。
   改写：在资源受限场景下。
后果：Response Measure 失去成立条件，测试 Case 无法复现。
```

### 5.3 基线摘录被重排

```markdown
❌ 原文（base excerpt）：“校验失败时清空配置并继续启动。”
   改写：“原实现在校验失败后会清空配置，然后继续启动。”
后果：摘录不再与 canonical 逐字一致，digest 比对失败，合并证据链断裂。
```

### 5.4 canonical 标题被顺手改

```markdown
❌ 原文：## 4.2 配置持久化
   改写：## 4.2 配置的持久化与恢复
后果：稳定显示名变化未经 RENAMED 操作，delta 的 target 解析和引用同步全部落空。
```

### 5.5 改写补出了没有来源的理由

```markdown
❌ 原文：本次把重试次数从 3 次改为 1 次。
   改写：为避免弱网下打满连接池，本次把重试次数从 3 次改为 1 次。
后果：如果“打满连接池”不是文档已有事实，这是新增断言；即使猜对了，也让评审者
      以为它已被确认。正确做法是向作者或来源确认后，作为内容补充单独提交。
```

### 5.6 模糊词被换成另一个模糊词

```markdown
❌ 原文：系统应快速响应。
   改写：系统应及时响应。
后果：缺陷被藏得更深。正确做法是保留原文并登记 Open Question：阈值、统计口径、来源。
```

## 六、改写记录

改写完成后给出记录，供评审者复核：

```markdown
## 改写记录（表达层）

| # | 位置 | 异味 | 动作 |
|---|---|---|---|
| 1 | srs.md 第 2 节导语 | 空转句 | 删除 3 句，结论提到段首 |
| 2 | delta-design.md 5.1 | 名词化长句 | 拆为 3 步流程列表 |
| 3 | 全文 | 术语漂移 | “链路/连接”统一为“会话（session）”，加术语表 |

## 保义证据

- 稳定 ID：集合一致（FR ×6、DS ×4、DD ×7、TC ×11，无增减）
- 数字与单位：去空格后集合一致；唯一格式变化是 `50ms` → `50 ms`
- 规范关键词：SHALL ×6、Given/When/Then ×18，计数不变
- delta operation 关键词：MODIFIED ×3、ADDED ×1，计数不变
- 反引号内容：集合一致；`ERR_CONFIG_INVALID` 出现次数 2 → 3，源于第 2 项把 DD-007 已有的 after 内容并入对照表
- 未触碰：全部 EARS 语句、全部 QAS 要素、DS/DD 的 selector 与基线摘录、canonical 标题

## 未改写（内容缺陷）

| # | 位置 | 问题 | 去向 | owner |
|---|---|---|---|---|
| 1 | NFR-003 | “必要时重试”缺触发条件与次数 | devflow-specify | @需求负责人 |
| 2 | delta-design 6.2 | 回滚步骤缺失败后的状态说明 | devflow-design | @设计负责人 |
```

## 七、提交纪律

表达层改写与内容修订分属不同 diff。评审者要能只看一个 diff 就知道这次是“换说法”还是“改事实”。混在一起时，reviewer 应按未闭环处理，要求拆分后再审。
