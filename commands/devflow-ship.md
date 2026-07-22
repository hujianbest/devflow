---
description: DevFlow 收尾阶段——硬性 DoD、Agent canonical sync、独立复核、人工确认、closeout 与 archive
---

执行 DevFlow 收尾阶段。

1. 读取当前 `specs/changes/ARXXX-<topic>/change.json` 和全部工件。任务未全 done、R1/R2/R3 未通过、Resolution 有空项、traceability 断链或记录与 gate 不一致时，返回责任阶段；不能警告后继续。
2. 读取 `skills/devflow-ship/SKILL.md`、`references/definition-of-done.md` 和 `references/sync-archive-protocol.md`。
3. 核对不可变 `change.json.baseRevision` 和两份 delta 的 canonical base 元数据。base 后有并行变化、现有工作树变化、规格稳定 ID 或组件设计章节/实体键不唯一、或语义歧义时，展示差异并向人追问；得到明确决定前不编辑 canonical，也不改写 `baseRevision`。
4. 主控 Agent 读取 SRS、两份 delta 和两份 canonical，按规格稳定 ID 与组件设计章节/实体键智能合并 `specs/spec.md`、`specs/design.md`，保留未涉及内容；有正文变化的 canonical 先置 draft 并重置评审/确认 metadata。不要新增专用交付脚本。
5. 展示只含两份 canonical 的 Git diff，派只读 `devflow-reviewer` 做 canonical sync 复核；记录写入同一 `reviews/`。漏吸收、误删、冲突、无来源变化或 spec-design 不一致都必须修正并复审。
6. 再核验 DoD：除人工确认、closeout 和目录移动这些顺序项外，其余项目必须全部通过。delta N/A、canonical diff 为空、紧急或 unattended 都不能省略 sync 复核。
7. 向人展示最终 canonical diff、R1-R3/sync 记录、DoD、债务和 archive 目标。取得明确确认后，才把实际修改的 canonical 恢复为 baseline-ready、把 canonicalSync gate 标为 passed；按 `references/closeout-template.md` 写 `closeout.md` 并闭合 closeout gate 后，再将 archive 置为 ready。
8. 确认目标不存在后，用标准文件操作把整个 change 目录移动到 `specs/archive/YYYY-MM-DD-ARXXX-<topic>/`，再在归档后的 manifest 和 closeout 回填 archived 状态、时间与验证结果。不覆盖、不合并、不留活动副本，不使用破坏性 reset。
9. 验证 archive 工件齐全、canonical 仍在 `specs/` 根，展示完整 Git diff 并进入正常 CI。
