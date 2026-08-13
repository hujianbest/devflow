# tasks.md 模板

使用说明：写入
`<component-root>/specs/changes/ARXXX-<topic>/tasks.md`。specify 阶段只建立
skeleton；R2 通过后由 `devflow-tdd` 填任务并实时维护。本文件不保存 R1/R2/R3、
canonical sync、DoD 或 archive 状态；也不复制 change/component 身份、profile、
运行模式或 artifact 状态，这些只在 `change.json`。

````markdown
# Tasks and TDD Evidence

## Sources

- SRS: `srs.md@<revision-or-digest>`
- Spec delta: `delta-spec.md@<revision-or-digest>`
- Design delta / Case Index: `delta-design.md@<revision-or-digest>`
- Traceability: `traceability.md@<revision-or-digest>`

## Execution Cursor

- Next task: `T1 | NONE | BLOCKED`
- Selection reason: <唯一 in-progress，或依赖满足后的唯一 pending，或阻塞原因>
- In-progress count: `0 | 1`
- Last completed task: `<Task ID | none>`

规则：

1. 最多一个 `in-progress`。
2. 有一个 `in-progress` 时，Next task 必须指向它。
3. 没有 `in-progress` 时，只能选择依赖已 done、就绪条件满足的唯一 pending。
4. 多个同等候选、依赖环、状态矛盾或外部阻塞时使用 `BLOCKED`，不得猜。
5. 所有正常和返工任务完成时使用 `NONE`。

## Case Coverage Audit

| Case ID from delta design | Owning Task | Task status | Traceability row |
|---|---|---|---|
| TC-001 | T1 | pending | `traceability.md#<anchor>` |

- Case IDs in delta design:
- Case IDs in tasks:
- Set comparison: `equal | mismatch:<details>`

> 任务覆盖集合必须与 Case Index 完全相等。不得在这里新增业务事实或 Case。

## Tasks

### T1 <薄垂直切片标题>

- Status: `pending | in-progress | blocked | done`
- Covers:
  - 需求条目: `FR-001` — <本任务所需的 Statement/Acceptance、QAS 或 Constraint/Verification 摘要>
  - Spec Section: `SPEC-FR-001` (`DS-001`)
  - Design Section/Decision: `6.2.1 / FUNC.001` / `DEC-001`
  - Cases: `TC-001` — <完整 Given/When/Then 和精确预期>
- Contract/error summary:
  - <执行本任务必须知道的输入、输出、错误、失败状态与副作用；不用“见上文”>
- Allowed scope:
  - Test: `<exact/test/path>`
  - Implementation: `<exact/source/path>`
  - Other allowed files: `<exact paths | none>`
- Out of scope:
- Dependencies: `<Task IDs | none>`
- Ready when: <依赖、环境和工件的可判定条件>
- Blocked by: `<none | precise blocker and owner>`
- Execution mode: `implementer-subagent | controller-direct`
- Dispatch record: <subagent/run anchor；direct 时写 runtime 无能力的事实>
- Quality Stack:
  - `<path/to/devflow-tdd/SKILL.md>` — TDD discipline
  - `<path/to/devflow-clean-code/SKILL.md>` — refactor check
  - `<applicable language/domain skill paths>`

#### T1 Steps

- [ ] RED: 写 `<test name>`；运行 `<focused command>`；确认因 `<missing behavior>`
  产生预期断言失败。
- [ ] GREEN: 写满足当前 Case 的最小实现；运行 `<focused command>` 和
  `<full suite/build command>`，确认全绿且无新增 warning。
- [ ] REFACTOR: 对照 Quality Stack 检查本任务触碰范围；只在全绿上清理并重跑
  `<full suite command>`；无改动时记录具体 N/A 理由。
- [ ] TRACE: 更新 traceability 的 Task、Code/Test、Evidence。
- [ ] DONE CHECK: 核对完成定义与所有真实证据后才改为 done。

#### T1 Done definition

- <TC-001 的可判定行为结果>
- RED/GREEN/REFACTOR 证据齐全且来自实际运行。
- 完整测试/构建 `<command>` 通过。
- traceability 对应路径闭合。
- 无 open blocker 或未批准范围变化。

#### T1 Evidence

- RED:
  - Command:
  - Expected failure:
  - Observed key output:
  - Why this proves missing behavior:
  - Timestamp / revision or worktree anchor:
- GREEN:
  - Commands:
  - Observed focused/full-suite/build summary:
  - Changed code/test paths:
  - Timestamp / revision or worktree anchor:
- REFACTOR:
  - Change summary:
  - Clean-code check:
  - Verification output:
  - Timestamp / revision or worktree anchor:
- Traceability:
  - Updated row(s):
- Notes:

### T2 <标题>

<!-- 完整复制 T1 结构并填写本任务内容；禁止写“同 T1”。 -->

## Rework Queue

<!-- R3 rework 时使用。命中已 done 任务时保留原任务及证据，创建 Tn-RWm。 -->

| Rework Task | Finding | Review source | Severity/category | Original task / files | Required RED or REFACTOR | Status | Resolution target |
|---|---|---|---|---|---|---|---|
| T1-RW1 | F-001 | `reviews/<file>#F-001` | critical / important; LLM-FIXABLE / USER-INPUT / TEAM-EXPERT | T1; `src/...`; `test/...` |  | open / in-progress / blocked / resolved | original review Resolution cell |

### T1-RW1 <返工标题>

- Status: `pending | in-progress | blocked | done`
- Finding excerpt and expected resolution:
- Preserved original evidence: `tasks.md#T1-Evidence`
- Covers 需求条目/Spec/Design/Case:
- Allowed scope / exact paths:
- Dependencies / ready / blocker:
- Steps:
  - [ ] RED: <bug/weak-test finding> / `N/A` only for behavior-preserving cleanup with reason
  - [ ] GREEN:
  - [ ] REFACTOR:
  - [ ] TRACE:
  - [ ] RESOLUTION: 回填原 review，附命令和 anchor
- Evidence:
  - RED:
  - GREEN:
  - REFACTOR:
  - Review Resolution:

## Blockers and debt

| ID | Kind | Description | Owner / destination | Affects next task |
|---|---|---|---|---|
| B-001 | blocker / debt |  |  | yes / no |

## Resume checklist

1. 读取 `change.json` 确认 R2/R3 边界，不在本文件推断门禁。
2. 核对 Sources revision 与磁盘工件；冲突先停止。
3. 核对 Case Coverage Audit 集合相等。
4. 按 Execution Cursor 规则确认唯一 next task。
5. 对 in-progress 任务，以步骤勾选和实际 Evidence 判断断点。
6. 任务完成后更新 traceability、状态和 cursor，再继续。
````
