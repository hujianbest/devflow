# closeout.md 模板

> 在 canonical sync 复核通过、DoD 中所有前置项通过且人明确确认 canonical diff 与归档后，由主控 Agent 写入活动 change 根。closeout 写入和后续目录移动会闭合 DoD 的最后顺序项。

```markdown
# <ARXXX> Closeout

## 身份与确认

| 字段 | 内容 |
|---|---|
| Change | ARXXX-<topic> |
| 组件 | <component-root> |
| componentMode | new / existing |
| 完成日期 | YYYY-MM-DD |
| 最终确认人 | <name/identity> |
| 确认时间 | <timestamp> |
| 确认范围 | canonical Git diff + DoD + archive target |
| Archive 目标 | specs/archive/YYYY-MM-DD-ARXXX-<topic>/ |

## Definition of Done

| 类别 | 结论 | 证据 |
|---|---|---|
| change.json / artifact 完整性 | passed | <锚点> |
| tasks 与 TDD 证据 | passed | tasks.md#... |
| R1 | passed | reviews/r1-review-...md |
| R2 | passed | reviews/r2-review-...md |
| R3 | passed | reviews/r3-review-...md |
| Findings / Resolution | passed | <记录与摘要> |
| Traceability | passed | traceability.md |
| 测试 / 构建 / 静态分析 | passed | <命令、结果、锚点> |
| Canonical sync review | passed | reviews/canonical-sync-review-...md |

> 不允许在 closeout 中把缺口写成 accepted warning。若有未通过项，停止并回责任阶段。

## Canonical Sync 摘要

| Canonical | Base revision | 同步结果 | Git diff 摘要 |
|---|---|---|---|
| specs/spec.md | <revision / empty-new> | <applied operations / N/A> | <summary> |
| specs/design.md | <revision / empty-new> | <applied operations / N/A> | <summary> |

- Canonical metadata:
  - `specs/spec.md`: baseline-ready / unchanged N/A
  - `specs/design.md`: baseline-ready / unchanged N/A
- Delta operations 吸收摘要:
  - `<operation-id>` → `<规格稳定 ID / 组件设计章节路径与实体键>`
- 未涉及语义保留抽查:
  - `<规格 ID / 组件设计章节或实体行>`: unchanged
- 并行变化处理:
  - N/A / <人工决策与 change.json 锚点>
- Spec-design 一致性结论:
  - <reviewer conclusion>

## 评审与 Resolution

| 门禁 | 最终轮次 | Verdict | Open critical/important |
|---|---:|---|---:|
| R1 |  | 通过 | 0 |
| R2 |  | 通过 | 0 |
| R3 |  | 通过 | 0 |
| canonical sync |  | 通过 | 0 |

- 人接受不修的 minor:
  - N/A / <finding + 理由 + 确认人>

## Traceability 与验证

- SRS → Spec → Design/Case → Task → Code/Test → Evidence: closed
- 最终测试命令与结果:
  - `<command>` → `<summary>`
- 构建 / 静态分析:
  - `<command>` → `<summary>`

## 遗留债务

| 项 | 不阻塞理由 | 去向 |
|---|---|---|
| N/A / <debt> | <reason> | <issue / future change ID> |

## 归档结果（移动后在 archive 内回填）

- Archive status: ready / archived
- Archived at: <timestamp after move>
- [ ] archive 目标在移动前不存在
- [ ] 整个 change 已原样移动，不留下活动副本
- [ ] canonical 文件保留在 specs/ 根
- [ ] 移动后展示完整 Git diff 并进入正常 CI
```

模板中的占位符必须替换为真实内容。没有债务时明确写 `N/A`；不得用“后续处理”代替可定位去向。
