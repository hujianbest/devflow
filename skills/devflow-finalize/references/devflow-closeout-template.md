# devflow 收尾记录模板

使用说明：

- 默认保存路径：`features/<工作项ID>-<slug>/closeout.md`。
- 同时必须渲染 HTML 工作报告 `features/<工作项ID>-<slug>/closeout-report.html`（按 `references/closeout-report-template.html`），与本 markdown 一一对应；HTML 报告是给开发负责人 / 模块架构师的可视化交付物，本 markdown 是签字版。
- 用于实现收尾：AR / DTS / CHANGE，基于 `devflow-completion-gate` 通过。

## 收尾摘要

- 工作项类型:                          # AR / DTS / CHANGE
- 工作项 ID:
- 所属组件:                            # 必填
- 工作流 Profile:                      # standard / component-impact / hotfix / lightweight
- 收尾类型: `implementation` | `blocked`
- 收尾结论: `closed` | `blocked`
- 基于的上游结论:                      # features/<id>/completion.md
- 日期:

## 证据矩阵

`N/A`（不适用）不算 blocked。

| 工件 | 路径 | 状态 |
|---|---|---|
| 需求 | `requirement.md` | present |
| 规格评审 | `reviews/spec-review.md` | 通过 |
| 组件设计评审 | `reviews/component-design-review.md` | 通过 / N/A |
| AR 设计评审 | `reviews/ar-design-review.md` | 通过 |
| 任务队列前置检查 | `tasks.md` / `task-board.md` | passed |
| 任务看板 | `task-board.md` | all done / cancelled |
| 测试有效性评审 | `reviews/test-review.md` | 通过 |
| 代码检视 | `reviews/code-review.md` | 通过 |
| 完成门禁 | `completion.md` | 通过 |

## 长期资产同步

| 长期资产 | 路径 | 本次是否同步 | 备注 |
|---|---|---|---|
| 组件实现设计 | `docs/component-design.md` | yes / no / N/A |  |
| AR 规格 | `docs/ar-specs/AR<id>-<slug>.md` | yes / N/A | AR 工作项必填（从 `features/<id>/requirement.md` 升级）；DTS / CHANGE 不修订 AR 规格时写 N/A |
| AR 实现设计 | `docs/ar-designs/AR<id>-<slug>.md` | yes / N/A | AR 工作项必填（从 `features/<id>/ar-design-draft.md` 升级）；DTS 不修改 AR 设计时写 N/A |
| Interfaces（可选） | `docs/interfaces.md` | yes / no / N/A（项目未启用） |  |
| Dependencies（可选） | `docs/dependencies.md` | yes / no / N/A（项目未启用） |  |
| Runtime Behavior（可选） | `docs/runtime-behavior.md` | yes / no / N/A（项目未启用） |  |

## 状态同步

- 最终 `Current Stage`:                   # closed / completed
- 最终 `Next Action Or Recommended Skill（下一步动作或推荐 Skill）`: # null（已完成）
- 未关闭风险记录到:                       # 例：组件级 risk log / backlog 路径

## HTML 工作报告

- 报告路径:                               # features/<工作项ID>-<slug>/closeout-report.html
- 渲染时间:                               # 与本 markdown 同步生成
- 报告与本 markdown 一致性:               # 一致 / 已修复（说明修复点）

## 交接

- 提交 / 合并状态:                         # branch / MR / PR 信息
- 团队同步说明:
- 限制 / 未关闭项:
