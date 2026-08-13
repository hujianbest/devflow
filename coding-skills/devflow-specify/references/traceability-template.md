# traceability.md 模板

使用说明：写入
`<component-root>/specs/changes/ARXXX-<topic>/traceability.md`。列名和顺序固定，
不得把 operation type、owner 或门禁状态插入主链。需要补充的信息放在“备注”。
各阶段只填写自己负责的锚点，不删除已有锚点。

```markdown
# ARXXX Traceability

- Change: `ARXXX-<topic>`
- Component:
- Last verified against: `change.json@<revision-or-digest>`

## Traceability Chain

| 需求条目 | Spec Section | Design Section/Case | Task | Code/Test | Evidence |
|---|---|---|---|---|---|
| `srs.md#FR-001` | `SPEC-FR-001` (`delta-spec.md#DS-001`) | `TBD(design)` | `TBD(tdd)` | `TBD(tdd)` | `TBD(tdd)` |

## Notes

- 每条 `FR-xxx`、`IFR-xxx`、`NFR-xxx` 和可测 `CON-xxx` 至少一行。
- 一条需求条目对应多个 Design Case 或 Task 时可拆成多行，但前两列必须重复，
  使每条路径都能独立冷读；不得在单元格写“同上”。
- specify 填前两列；design 填 `Design Section/Case`；tdd 填后三列。
- `Spec Section` 使用目标 canonical stable ID，并在括号中保留 delta operation 锚点。
- `Design Section/Case` 同时给出组件设计章节路径/功能编号/接口或软件单元实体键、
  `DEC-xxx` 和 `TC-xxx`。
- `Code/Test` 同时列实现与测试的精确路径/符号；只有其中一项适用时写带理由的 `N/A`。
- `Evidence` 指向 `tasks.md` 中实际 RED/GREEN/REFACTOR 输出或其他可复核工件，
  不能只写“测试通过”。
- `TBD(stage)` 只允许在负责阶段尚未开始时存在。对应阶段完成后仍有 TBD，
  该阶段门禁不得进入评审。
- `ASM-xxx`、`EXC-xxx` 不进入主链；必要说明放在本节。
```
