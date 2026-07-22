# 缺陷 Change 工件模板

> 缺陷沿用 `specs/changes/ARXXX-<topic>/` 的标准工件。下列片段分别写入现有 `srs.md`、两份 delta 和 `tasks.md`；不要另建平行说明文件。

## srs.md 缺陷章节

```markdown
# <缺陷标题> — 软件需求规格

## 1. 问题与目标

- 当前问题：
- 目标结果：
- 工作项来源：<DTS / 事故 / 报告锚点>
- 整体成功标准：

## 2. 范围与非范围

### 2.1 范围

- <范围条目>

### 2.2 非范围

- `EXC-001`：

## 3. 功能性需求

### 3.1 FR-001 <恢复组件规格行为>
- 需求陈述：当 <缺陷触发条件> 时，组件必须满足 <组件规格 ID 的既有语义>。
- 验收标准：
  - Given <复现环境>；When <触发>；Then <正确结果及不应发生的副作用>。
- 来源：<DTS 锚点> + `specs/spec.md#<stable-id>`
```

## delta-spec.md

纯实现偏离且行为基线不变：

```markdown
---
documentType: change-delta-spec
manifest: change.json
canonicalBase:
  path: specs/spec.md
  baselineRevision: <revision>
  contentDigest: <digest>
  workingTree: clean | <recorded-digest>
provenance:
  srs: srs.md@<revision-or-digest>
  capturedAt: <ISO-8601>
---

# 规格增量

## 无规格变化（仅缺陷恢复适用）

- Canonical target: specs/spec.md#<stable-id>
- 需求条目: FR-001
- 结论: 当前 canonical 已准确规定预期行为，本修复不改变可观察契约。
- 违反证据: <实际行为与 canonical 的差异>
- 不变项: <接口/错误语义/状态机/默认值/阈值/兼容承诺>
- Preservation clause: specs/spec.md 全部语义保持不变。
- 验证义务: `AC-xxx` / `NFR-xxx QAS` / `CON-xxx Verification`；具体 `TC-xxx` 在 delta-design 中建立。
```

行为需要改变时，使用标准稳定 ID 操作，不得写 N/A：

```markdown
## MODIFIED 需求

### DS-001 [MODIFIED] <SPEC-stable-id> <标题>

- 需求条目: `FR-001`
- Selector: <字段/子节稳定 ID>
- Base excerpt or digest: <最小基线内容>
- Replace:
  - <被替换的现行语义>
- With:
  - <批准的新语义>
- Resulting local content:
  - <合并后的完整局部>
- Preservation clause:
  - 保留该 stable ID 的所有其他语义和全部 sibling sections。
- Regression semantics:
  - <必须继续成立的行为与 Acceptance>
- Compatibility / migration:
```

完整 frontmatter、N/A/operation 结构仍使用
`devflow-specify/references/delta-spec-template.md`，不能只复制上述片段。

## delta-design.md

设计基线也不变：

```markdown
---
documentType: change-delta-design
manifest: change.json
canonicalBase:
  path: specs/design.md
  baselineRevision: <revision>
  contentDigest: <digest>
  workingTree: clean | <recorded-digest>
provenance:
  deltaSpec: delta-spec.md@<revision-or-digest>
  canonicalSpec: specs/spec.md@<revision-or-digest>
  capturedAt: <ISO-8601>
---

# 设计增量

## N/A — no canonical design change

- Canonical target: specs/design.md#<stable-id>
- 需求条目 / Spec source: FR-001 / <SPEC-stable-id>
- 结论: 当前设计已正确，本修复只恢复实现一致性。
- 不变项: <结构/依赖/接口/错误模型/所有权/时序>
- Preservation clause: specs/design.md 全部语义保持不变。
- Test strategy: 下列 Case 证明实现恢复到 canonical 契约，不改变设计。

## Case Index

| Case ID | 需求条目 | Spec Section | Design Section | Given/When/Then | Expected result | Level | Coverage type | Verification |
|---|---|---|---|---|---|---|---|---|
| TC-001 | FR-001 | <SPEC-ID> | <章节路径 / 功能编号 / 接口或软件单元实体键> | <复现摘要> | <canonical 预期> | unit / integration | regression | <command> |
```

若根因要求设计变化，完整使用
`devflow-design/references/delta-design-template.md`，以 `DD-xxx` 和
`ADDED / MODIFIED / REMOVED / RENAMED` 记录稳定 ID、selector、before/after、
preservation clause、规格来源、测试设计和回退。

## tasks.md 修复任务

```markdown
## 缺陷分析与复现证据

- 环境：<版本/提交、平台、配置>
- 现象 / 影响 / 严重度：
- 最小复现：

| 步骤 | 操作/输入 | 预期 | 实际 |
|---|---|---|---|
| 1 |  |  |  |

- 日志 / core / trace：
- 复现稳定性：stable / flaky(<频率>) / unreproduced
- 因果链（每步带证据）：
- 直接原因：
- 根本原因：
- 现有测试缺口：
- 波及范围：
- 已排除假设及证据：
- 最小安全修复范围：
- 显式非范围：
- 回退策略：

### T1 <复现并修复>

- Status: pending / in-progress / blocked / done
- Covers: FR-001
- Case IDs: TC-001
- 允许文件:
  - 测试: `<path>`
  - 实现: `<path>`
- 非范围:
- 步骤:
  - [ ] RED: 写自动化复现测试；运行 `<command>`，确认因目标缺陷失败
  - [ ] GREEN: 最小修复；运行 `<full-suite-command>`，确认全绿且无新增警告
  - [ ] REFACTOR: 对照 clean-code 检视任务范围；每步保持全绿，或写 N/A 理由
  - [ ] 更新 traceability，登记同类风险，保存证据
- 证据:
  - RED: `<command>` → `<关键失败>` @ `<code anchor>`
  - GREEN: `<command>` → `<通过摘要>` @ `<code anchor>`
  - REFACTOR: `<摘要 + 验证>` / N/A（<无任务内异味理由>）
```

本片段必须放入 `devflow-tdd/references/tasks-template.md` 的完整 Sources、Execution
Cursor、Case Coverage Audit、Evidence 与 Resume 结构中，不能作为简化版 tasks
文件单独使用。

N/A 只能表达 canonical 无变化，不能替代复现、任务证据、评审、同步复核或收尾。
