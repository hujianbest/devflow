# Learning 契约

## 知识库根目录

先解析 Git 仓库根，再固定使用：

```text
<repo-root>/docs/learnings/
```

不支持自定义根或路径别名。类型和目录一一对应：

- `problem-solution` → `problem-solutions/`
- `design-decision` → `design-decisions/`
- `engineering-practice` → `engineering-practices/`

`README.md` 只说明知识库用法，不参与 learning 检索与去重。

## 身份

`learningId` 是稳定身份：

- 使用小写 kebab-case；
- 首尾必须是字母或数字；
- 通常包含组件、类型和主题；
- 必须等于 Markdown 文件名去掉 `.md` 后的部分；
- 后续用新证据更新文档时保持不变。

文件名和 ID 不带日期。

## 必需元数据

`learning-schema.json` 是机器契约。新文档只使用其中声明的字段。

核心规则：

- `schemaVersion` 固定为 `"1.1"`；
- `documentType` 固定为 `devflow-learning`；
- `learningType` 唯一决定分类目录；
- `component` 来自源 change 的稳定组件标识；
- `componentRoot` 使用仓库相对路径和 `/`，组件位于仓库根时写 `.`；
- `sourceChanges` 至少包含一个 `ARXXX-topic`；
- `sourceArchives` 保存与 source change 对应的仓库相对归档目录；
- `tags` 包含 1–8 个小写 kebab-case 检索词；
- `canonicalRefs` 可选，只保存已经核实的稳定 ID。
- `relatedLearnings` 可选，最多 8 项，禁止自引用；关系必须双向。
- `supersededBy` 只用于 `status: superseded`，至少 1 项、最多 3 项，目标必须存在。
- `statusReason` 在 `stale` 与 `superseded` 时必填，简述证据化原因。

每个 `sourceArchives` 项都必须包含归档状态为 `archived` 的 `change.json`。源 change
的 ID、组件和组件根必须与 learning 元数据一致。

## 状态

- `active`：当前证据仍支持该指导；
- `stale`：有漂移迹象，但还没有可信的替代方案；
- `superseded`：已有明确的新 learning 或当前方案取代它。

检索流程只把 `active` 文档当作指导。`stale` 和 `superseded` 仍可用于了解历史，
但不能覆盖当前 canonical 或代码。

## 敏感级别

- `public`：可以进入公开仓库；
- `internal`：只适合仓库批准的内部受众；
- `restricted`：禁止写入 learning store。

仓库可见性本身不能证明内容安全。分类前先移除凭证、个人或客户数据、内部端点、
工作站路径和不必要的原始日志。

## 声明与证据

Learning 区分三类声明：

- `historical`：由 archive 验证，包括调查步骤、否决方案、review finding、变更期间
  的测试和决策；
- `current`：由当前 canonical、代码或测试验证；
- `guidance`：由历史或当前证据推出的做法，并明确适用与不适用边界。

事实性或指导性段落后紧跟一个机器可读注释：

```markdown
根因是取消路径没有释放重试计时器。
<!-- claim: CLM-001; kind: historical; evidence: EV-001,EV-002 -->
```

证据集中列在 `## 证据`：

```markdown
- EV-001 | archive | `components/retry/specs/archive/2026-08-11-AR001-fix/tasks.md::## 根因`
- EV-002 | current-test | `components/retry/tests/test_timer.py::test_cancel_releases_timer`
```

证据类型只允许：

- `archive`：locator 必须位于某个 `sourceArchives` 目录内；
- `current-canonical`：当前 `specs/spec.md` 或 `specs/design.md`；
- `current-code`：当前实现文件；
- `current-test`：当前测试文件。

每个 claim ID 和 evidence ID 在文档内唯一。每个 claim 至少引用一项证据，引用必须存在；
每项证据至少被一个 claim 使用。`historical` 只能使用 archive 证据，`current` 至少包含
一项 current 证据。`guidance` 必须有证据，并在正文明确适用与不适用条件。

路径使用反引号包裹的仓库相对路径。被 source change 删除的路径必须标明是历史路径。
不要把本地 commit SHA 当作持久身份，优先引用 archive change ID 和路径。

机械校验只证明“声明与证据可定位”，不证明语义蕴含。独立 reviewer 必须逐 claim
给出 `verified`、`contradicted` 或 `unverifiable`，并引用定义位置。

## 与 canonical 分工

Learning 回答：

- 为什么某个选择有效；
- 哪些方法失败以及失败原因；
- 什么时候适用；
- 有什么证据。

它不重复完整需求、接口、状态机、设计章节、gate 状态或任务进度。需要时引用稳定
canonical ID 和源工件。

## 重叠判断

从五个维度比较候选文档：

1. 问题或决策；
2. 根因或选择理由；
3. 方案或指导；
4. source、代码、测试或 canonical 锚点；
5. 适用边界。

分类：

- high：匹配四到五项；
- moderate：匹配二到三项；
- low：匹配零到一项。

只有两份文档表达同一条经验时，高重叠才更新原文件。相互矛盾的指导不能伪装成一致
内容合并；应更新旧文档状态，并指出当前替代项。

## 检索

采用 grep-first：

1. 最多扫描 500 份 learning；超过上限返回 `truncated`，不得当作无匹配；
2. 先只读取 frontmatter，按 `status: active`、`component`、`componentRoot`、
   `learningType`、`tags` 和 `canonicalRefs` 过滤；
3. 元数据候选超过 20 个时要求增加 component、symbol 或精确错误签名；
4. 候选少于 3 个时才扩大到正文术语；
5. 最多返回 5 个结果，并说明每项命中原因；
6. `relatedLearnings` 只扩展一跳，最多增加 8 个节点；
7. stale 与 superseded 只作为诊断信息，不得作为当前指导。

v1 不创建生成式索引，Markdown 文件就是 source of truth。

## Evidence pack

复杂 archive 或 overlap 候选较多时，先构造窄 evidence pack：

- 只包含 claim 引用 anchor 周围的短摘录；
- 每项保留 evidence ID、仓库相对路径和 anchor；
- 最多 12 项、总计 64 KiB；
- 不包含聊天、完整 archive、完整源码或无关日志；
- 写入操作系统临时目录，不进入仓库；失败时回退为短 inline 摘录并报告降级。

## Refresh

Refresh 分为只读审计与显式应用：

- `refresh-audit` 只检查失效 locator、旧 schema、broken related edge、stale 信号和
  supersession；不修改文件；
- 审计动作只允许 `keep`、`mark-stale`、`link-supersession`、`repair-related`、
  `manual-rewrite-required`；
- plan 记录 store digest、每个目标文件 before digest、理由和允许写集；
- `refresh-apply` 需要用户明确批准 plan；digest 变化、写集越界或证据不足时阻塞；
- apply 后重新执行 store 校验和独立逐 claim 复核。

年龄本身不是 stale 证据。无法验证不等于错误；证据不足时标记 stale，不猜替代方案。
核心建议已错误时使用 supersession，不以普通 Update 掩盖。删除、合并、拆分或重写必须
人工决定，不由脚本自动执行。

## YAML 子集

为保持校验器零依赖，frontmatter 只使用严格子集：

- 顶层标量键；
- 顶层字符串 block array；
- 禁止嵌套 map、anchor、alias、tag、flow array 和多行标量；
- 值包含 YAML 标点或以保留指示符开头时加引号。

校验器遇到不支持的结构应拒绝，不能猜测其他 YAML 实现会如何解析。
