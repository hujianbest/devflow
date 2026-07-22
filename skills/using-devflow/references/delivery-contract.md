# DevFlow 交付结构契约

## 1. 路径根与唯一拓扑

所有路径使用 `/`。先解析 `<component-root>`，再从该目录直接解析 `specs/`：

```text
<component-root>/
└── specs/
    ├── spec.md
    ├── design.md
    ├── changes/
    │   └── ARXXX-<topic>/
    │       ├── change.json
    │       ├── srs.md
    │       ├── delta-spec.md
    │       ├── delta-design.md
    │       ├── tasks.md
    │       ├── traceability.md
    │       ├── reviews/
    │       └── closeout.md
    └── archive/
        └── YYYY-MM-DD-ARXXX-<topic>/
```

这是封闭集合：

- `specs/spec.md` 与 `specs/design.md` 是组件当前真相。
- 一个活动变更只有一个目录，目录名必须与 manifest 的 `changeId`、`topic` 一致。
- 变更关闭时移动整个目录；不复制挑选出的文件，不留下活动副本。
- 不接受替代根、路径别名、团队自定义工件名或中间工件层。
- 所有必需文件都存在才可归档；低风险只允许压缩正文深度。

`changeId` 使用 `AR` 加数字，例如 `AR123`。`topic` 使用小写 kebab-case。日期使用 `YYYY-MM-DD`。

## 2. Canonical baseline 契约

两份 canonical 文档都必须在 YAML frontmatter 中声明：

| 字段 | 要求 |
|---|---|
| `documentType` | `canonical-spec` 或 `canonical-design` |
| `component` | 稳定组件标识 |
| `baselineStatus` | `draft` 或 `baseline-ready` |
| `baselineRevision` | init 的 source revision，或最近一次 canonical sync 使用的 `change.json.baseRevision`；它是 delta 的基准，不声称包含同步后的文件 |
| `baselineChange` | init 写 `null`；canonical sync 写产生当前正文的 `ARXXX-<topic>`，与 revision 和 provenance index 共同标识基线 |
| `provenanceMethod` | `devflow-init`、`canonical-sync` 或团队批准的明确方法 |
| `independentReview.status` | `pending`、`rework` 或 `passed` |
| `humanConfirmation.status` | `pending` 或 `confirmed` |

只有同时满足以下条件，才允许写 `baselineStatus: baseline-ready`：

1. 文档内容可追到代码、测试、API/IDL、配置、构建、部署、既有说明或明确人工回答；
2. 契约、行为、阈值和架构边界没有 blocking unknown；
3. 独立 reviewer 的 verdict 为 passed；
4. 人已检查文档及 reviewer 结果并明确确认；
5. `spec.md` 与 `design.md` 交叉一致。

文件存在、内容很多或与当前实现相似，都不能单独证明 baseline-ready。

canonical 文件不能在自身正文中可靠记录“包含自己的 Git commit hash”。
因此 canonical-sync 后的可复现身份是
`baselineRevision + baselineChange + provenance index`：从该 revision 读取旧
canonical，再应用 archive 中对应 change 的 delta，即可得到当前正文。下一个 AR 的
`change.json.baseRevision` 仍记录它开始时真实的当前仓库 revision，两者不要混用。

## 3. `change.json` 顶层结构

`change.json` 必须是严格、可解析的 JSON，不使用注释、尾逗号或未加引号的占位符。必需顶层字段：

| 字段 | 类型 | 契约 |
|---|---|---|
| `schemaVersion` | string | 当前为 `1.0` |
| `changeId` | string | 与目录前缀一致 |
| `topic` | string | 与目录后缀一致 |
| `component` | string | 稳定组件标识 |
| `componentRoot` | string | 仓库相对路径；组件即仓库根时为 `.` |
| `componentMode` | string | 仅 `new` 或 `existing` |
| `baseRevision` | string | 变更开始时不可变的 VCS revision |
| `executionMode` | string | `attended` 或 `unattended` |
| `profile` | object | 风险 profile 与选择依据 |
| `artifacts` | object | artifact graph |
| `gates` | object | 所有门禁状态 |
| `archive` | object | 活动与归档状态 |

不得把必需字段移入自由文本。需要团队扩展时，只能增加顶层 `extensions` object；扩展不能改变以上字段语义。

### 3.1 身份与 base revision

- `changeId` + `topic` 唯一确定变更目录。
- `componentMode` 缺失、冲突或不确定时，manifest 无效，工作阻塞。
- `baseRevision` 必须是可重新读取该快照的稳定标识。分支名、`HEAD`、`latest`、时间描述和聊天中的 commit 摘要都不合格。
- `baseRevision` 创建后不可改。发现选错时，停止并由人决定废弃重建还是保留审计修正；不得覆盖原值伪装成无并发变化。
- canonical sync 比较 `baseRevision`、当前 canonical 和工作树差异；不能访问该 revision 时 sync 阻塞。

### 3.2 Profile object

必需字段：

```json
{
  "name": "standard",
  "risk": "medium",
  "reasons": [
    "Internal behavior change with bounded rollback"
  ],
  "requiredEvidence": [
    "unit-tests",
    "integration-tests"
  ],
  "requiredReviewers": [
    "independent-generalist"
  ]
}
```

`reasons` 必须基于变更事实，不写泛化结论。profile 细则见 using-devflow 的风险参考。

### 3.3 Artifact graph

`artifacts` 至少声明以下键：

- `canonicalSpec`
- `canonicalDesign`
- `srs`
- `deltaSpec`
- `deltaDesign`
- `tasks`
- `traceability`
- `reviews`
- `closeout`

每个节点包含：

| 字段 | 值 |
|---|---|
| `scope` | `component` 或 `change` |
| `path` | `component` 相对组件根；`change` 相对 `change.json` 所在目录 |
| `status` | 下列 artifact 状态之一 |
| `dependsOn` | artifact key 数组 |

允许的 artifact 状态：

- `unchecked`
- `absent-allowed`
- `not-started`
- `draft`
- `ready-for-review`
- `accepted`
- `baseline-ready`
- `synced`
- `complete`
- `archived`
- `blocked`

状态必须与实物一致。文件缺失却标为完成、评审未通过却标为 accepted、canonical 未获人确认却标为 baseline-ready，均视为 manifest 冲突并阻塞。

`change` scope 保证目录移动后本地路径仍有效；canonical artifacts 使用 `component` scope。

阶段状态转换：

- specify 完成：`srs`、`deltaSpec` 为 `ready-for-review`；
- R1 最终通过且所需人工确认完成：`srs`、`deltaSpec` 为 `accepted`；
- design 完成：`deltaDesign` 为 `ready-for-review`；
- R2 最终通过且所需人工确认完成：`deltaDesign` 为 `accepted`；
- TDD 全部完成：`tasks`、`traceability` 为 `complete`；
- canonical sync 经独立评审和人工确认：实际修改的 canonical artifact 为
  `baseline-ready`，未修改 N/A artifact 保持原状态；
- closeout 写实并核验：`closeout` 为 `complete`；
- 整目录移动并复核：所有 change-scope artifact 为 `archived`。

只有主控 Agent 在对应证据落盘后执行转换；reviewer 只返回记录，不直接写 manifest。

### 3.4 Gates

`gates` 至少包含：

- `baselinePreflight`
- `r1`
- `r2`
- `r3`
- `canonicalSync`
- `closeout`

每个 gate 包含：

```json
{
  "status": "pending",
  "evidence": [],
  "reviewRecords": [],
  "humanConfirmation": "pending"
}
```

`status` 只允许 `pending`、`blocked`、`rework`、`passed`。`humanConfirmation` 只允许 `pending`、`confirmed`、`not-required`。

- `evidence` 保存可定位的测试、构建、diff、追溯或决策锚点。
- `reviewRecords` 保存 `reviews/` 中的相对路径。
- R1、R2、R3、canonicalSync 的 `passed` 必须有与 profile 相符的证据和
  reviewer 记录。
- baselinePreflight 在既有组件由 init 修复时必须引用 baseline review；new 组件的
  preflight 可用人工确认的 mode 与空基线证据。
- closeout 不是独立评审门禁，`reviewRecords` 保持空数组；它的 `passed` 依赖
  已通过的 R1/R2/R3/canonicalSync records、最终人工确认和写实的
  `closeout.md` evidence。
- upstream 工件语义改变时，显式把所有受影响 gate 重新打开为 `pending`，并在 `evidence` 记录原因。
- `canonicalSync` 与 `closeout` 的人工确认不可设为 `not-required`。

`closeout` gate 的唯一转换：

1. canonical sync reviewer 通过、人确认最终 diff/DoD/archive 目标后仍保持
   `pending`；
2. 主控 Agent 写 `closeout.md` 并重新读取核对；
3. 写入失败、占位符残留或与确认内容不一致时写 `blocked`；
4. 内容完整写实时，`artifacts.closeout.status=complete`、
   `gates.closeout.status=passed`、`humanConfirmation=confirmed`，并记录
   closeout 与最终人工确认 evidence；`reviewRecords` 保持空数组，因为既有四类
   review 通过 evidence 引用而不是复制成 closeout reviewer；
5. closeout gate passed 后才允许移动目录。

## 4. `tasks.md` 边界

`tasks.md` 只回答“为什么这样实施、还要实现什么、当前做到哪一步、证据在哪里”，允许包含：

- 缺陷工作项的环境、复现、根因、测试缺口、修复边界与回退证据；
- Task ID、依赖、目标与范围；
- RED 测试及失败证据；
- GREEN 实现及通过证据；
- REFACTOR 动作及回归证据；
- 代码、测试、构建或观测锚点；
- 与 reviewer finding 对应的返工任务。

以下内容只属于 `change.json`，不得复制到 `tasks.md`：

- 变更或组件身份；
- `componentMode`、`baseRevision`、运行模式；
- 风险 profile；
- artifact graph 状态；
- R1/R2/R3/sync/closeout gate 状态；
- 归档状态。

任务完成不自动使 gate 通过；gate 通过也不能伪造任务证据。

## 5. Archive object

活动时：

```json
{
  "status": "active",
  "target": null,
  "confirmedBy": null,
  "archivedAt": null
}
```

归档状态只允许：

- `active`
- `ready`
- `archived`

归档顺序：

1. 所有 artifact、gate、traceability、finding resolution 和 DoD 完成；
2. 检查目标 `specs/archive/YYYY-MM-DD-ARXXX-<topic>/` 不存在；
3. 写入 `status: ready` 与目标，展示 canonical diff 和归档摘要；
4. 人确认；
5. 移动整个目录；
6. 在归档目录中的 manifest 写入 `status: archived`、确认人和时间；
7. 验证活动目录已消失、归档目录完整，再展示完整 Git diff。

任何一步失败都保持可恢复状态；不得删除源目录、覆盖目标目录或用破坏性 Git 操作回退。
