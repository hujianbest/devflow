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

- `schemaVersion` 固定为 `"1.0"`；
- `documentType` 固定为 `devflow-learning`；
- `learningType` 唯一决定分类目录；
- `component` 来自源 change 的稳定组件标识；
- `componentRoot` 使用仓库相对路径和 `/`，组件位于仓库根时写 `.`；
- `sourceChanges` 至少包含一个 `ARXXX-topic`；
- `sourceArchives` 保存与 source change 对应的仓库相对归档目录；
- `tags` 包含 1–8 个小写 kebab-case 检索词；
- `canonicalRefs` 可选，只保存已经核实的稳定 ID。

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

## 证据

Learning 区分两类证据：

- 历史事实由 archive 验证，包括调查步骤、否决方案、review finding、变更期间的
  测试和决策；
- 当前行为由当前 canonical、代码和测试验证。

路径使用反引号包裹的仓库相对路径。被 source change 删除的路径必须标明是历史路径。
不要把本地 commit SHA 当作持久身份，优先引用 archive change ID 和路径。

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

1. 搜索元数据字段：`status`、`component`、`componentRoot`、`learningType`、`tags`
   和 `canonicalRefs`；
2. 搜索精确错误签名、符号、模块名或决策术语；
3. 读取候选 frontmatter；
4. 只完整读取强匹配项。

v1 不创建生成式索引，Markdown 文件就是 source of truth。

## YAML 子集

为保持校验器零依赖，frontmatter 只使用严格子集：

- 顶层标量键；
- 顶层字符串 block array；
- 禁止嵌套 map、anchor、alias、tag、flow array 和多行标量；
- 值包含 YAML 标点或以保留指示符开头时加引号。

校验器遇到不支持的结构应拒绝，不能猜测其他 YAML 实现会如何解析。
