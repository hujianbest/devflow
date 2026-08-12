---
name: devflow-learn
description: 在 DevFlow change 已成功归档后，将已验证的缺陷根因、设计取舍或工程实践沉淀为可检索 learning 时使用；也用于用户要求复盘、记录解决方案、避免重复踩坑或建立项目知识库。不用于进行中的问题、未验证方案、普通进度总结或修改 canonical spec/design。
---

# DevFlow 知识沉淀

## 定位

`devflow-learn` 是 Ship 之后的可选工具，不是生命周期阶段、质量层或 gate。它从已归档
change 提取一条可复用经验，写入仓库级 `docs/learnings/`。

知识捕获失败或没有合格候选，不改变已经完成的 Ship。不得修改：

- 组件 `specs/spec.md`、`specs/design.md`；
- archive 内任何文件；
- `change.json`、artifact 或 gate 状态；
- 产品代码和测试。

## 真相顺序

形成和使用 learning 时都按以下顺序裁决：

1. 当前 canonical、代码和测试；
2. 已归档 change 的磁盘证据；
3. `status: active` 的 learning；
4. 聊天内容。

聊天只帮助定位主题。行为、根因、验证结果或设计理由没有磁盘证据时，不得写成事实。
Learning 与当前真相冲突时，当前真相优先；报告 stale 信号，不为了匹配 learning 修改代码。

## 按需参考

不要在启动时一次读取全部文件：

- 解析 store、字段和重叠规则时读
  [learning-contract.md](references/learning-contract.md)；
- 生成或更新文档时读
  [learning-templates.md](references/learning-templates.md)；
- 校验字段时以
  [learning-schema.json](references/learning-schema.json) 为机器契约；
- 写入前的只读检查使用
  [learning-review-rubric.md](references/learning-review-rubric.md)。

## 输入与运行方式

入口：

```text
/devflow-learn <archive-path-or-AR> [learning hint]
```

来源解析规则：

1. 用户给出 archive 路径时直接使用；
2. 用户给出 AR ID 时，在已知组件或仓库内精确匹配；
3. 参数省略时，只有当前会话唯一指向刚完成的 archive 才可使用；
4. 多个来源均可能时询问，禁止按目录修改时间或“最新 AR”猜测。

显式用户调用表示用户希望进行捕获，但在多个候选或敏感级别不明确时仍需询问。
调用方明确要求 unattended、report-only、无提示或没有用户可回答时，只生成候选报告，
不创建或更新 learning。

## 捕获门槛

写入前逐项核验：

- archive 目录真实存在；
- archive 内 `change.json.archive.status` 为 `archived`；
- `gates.r1`、`gates.r2`、`gates.r3`、`gates.canonicalSync`、
  `gates.closeout` 均为 `passed`；
- `closeout.md` 存在且无占位符，记录最终人工确认；
- critical/important findings 已闭环；
- 结论有测试、评审、canonical、代码或 traceability 证据；
- 内容非平凡，并能改变未来的调查、设计或工程选择。

任一交付前置条件不满足，停止并返回具体缺口，建议回到 `devflow-ship`。不得在本技能内
补交付工件或修 gate。

以下内容不值得捕获：

- 拼写、格式化、生成文件刷新或机械依赖升级；
- 尚未验证的假设；
- 只对本次命令执行有意义的细节；
- 对 canonical 或 closeout 的重复摘要；
- 无法安全进入当前仓库的信息。

没有合格候选时输出 `知识沉淀已跳过` 和原因，不生成填充文档。

## 一次一条

一次调用只处理一条 learning。一个 archive 中若有多个独立候选：

1. 为每个候选写一句可复用结论；
2. 列出最强证据锚点；
3. 让用户选择一个；
4. 其余候选留给后续调用。

禁止把缺陷根因、设计决策和流程经验拼成一篇“项目总结”。

## 候选提取

根据候选类型读取证据：

- `problem-solution`：优先读取 `tasks.md` 的复现、根因、排除假设、
  RED/GREEN/REFACTOR，以及 R3/traceability；
- `design-decision`：优先读取 `delta-design.md` 的 Design Options、决策、
  R2 与同步后的 canonical；
- `engineering-practice`：优先读取 reviews、Resolution、任务证据和 closeout
  中能证明流程或工具改进的内容。

每个候选必须回答：

- 后续什么场景会用到；
- 它会改变什么选择；
- 哪些证据证明它；
- 哪些场景不适用。

## 知识库与文件名

知识库固定为：

```text
<repo-root>/docs/learnings/
  README.md
  problem-solutions/
  design-decisions/
  engineering-practices/
```

分类由 `learningType` 唯一决定。文件名是稳定、无日期的 kebab-case slug，
并与 `learningId` 完全一致：`<learningId>.md`。

第一次写入时，如果 `docs/learnings/README.md` 不存在，使用模板中的知识库 README
创建它。不要创建 `index.json`、数据库或额外状态文件。

## 去重与更新

写入前必须搜索全部现有 learning。先按 `learningId`、`component`、`componentRoot`、
`learningType`、`tags` 和 `sourceChanges` 过滤候选，再按以下五维判断：

1. 问题或决策；
2. 根因或选择理由；
3. 方案或指导；
4. 代码、测试或 canonical 锚点；
5. 适用边界。

处理：

- 高重叠：更新原文件，保留路径，合并新证据和来源，更新 `lastVerifiedAt`；
- 中度重叠：创建独立文档并相互引用；
- 低重叠：创建新文档；
- 既有指导被当前证据否定：不要静默混写；将旧文档标为 `superseded` 或
  `stale`，写明原因，并创建或链接当前指导。

语义去重不能只靠文件名或标签。

## 隐私与敏感信息

默认只读取仓库中的 archive、canonical、代码和测试，不读取本机会话历史。

最终文档不得包含：

- 私钥、JWT、云密钥、token、认证头或连接串；
- 客户标识、个人邮箱、姓名等不必要 PII；
- 内部 URL、机器用户名、绝对路径；
- 大段原始日志、请求或响应正文；
- 当前仓库策略不允许保存的信息。

错误信息只保留复现和搜索所需的最小签名。`sensitivity: restricted` 禁止写入；
`public` 或 `internal` 必须符合仓库策略。无法判断且选择会改变安全性时询问用户。

## 写入、校验与只读复核

1. 读取模板并组装完整 Markdown；
2. 所有路径写成 repo-relative `/` 路径；
3. 主控 Agent 写入目标文件；研究/复核子代理不得写文件；
4. 运行：

   ```text
   python <skill-dir>/scripts/validate_learning.py <learning-path> --repo-root <repo-root>
   ```

5. 校验失败时修正并重跑，未通过前不得报告完成；
6. 使用 `learning-review-rubric.md` 派一个全新只读上下文复核事实、重复、
   applicability 和敏感信息；
7. 若平台没有独立上下文能力，由主控执行同一 rubric，并在结果中说明独立复核缺失；
8. 语义复核发现 contradicted claim 时以引用的当前证据修正文档，再重跑脚本。

校验或复核只允许修改本次目标 learning，以及首次 bootstrap 的 store README。
不得顺手刷新其他文档、代码或 canonical。

## 完成输出

成功时报告：

```text
知识沉淀完成

文件: docs/learnings/<category>/<learning-id>.md（已创建 | 已更新）
类型: <learningType>
来源: <archive path>
重叠: <none | low | moderate | high — 已更新原文档>
校验: 通过
复核: <独立复核通过 | 自检通过，运行环境不支持独立上下文>
敏感级别: <public | internal>
```

report-only 时报告候选、来源和未写入原因。无合格候选或前置条件失败时以
`知识沉淀已跳过` 结束。
