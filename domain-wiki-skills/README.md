# Domain Wiki Skills

编译式领域 wiki 技能：把仓库和原文写成互链 markdown wiki，之后靠索引查询，而不是每次从源码重推。

权威流程在各目录的 `SKILL.md`。各技能自带契约，可单独安装。落盘只保留领域 wiki 结果，不写评审报告。本集合不依赖其他技能集合的流程或产物。

## 技能

| 技能 | 做什么 |
|---|---|
| [domain-wiki-init](domain-wiki-init/SKILL.md) | 有界发现后按栏目编译覆盖全仓的首版 wiki |
| [domain-wiki-update](domain-wiki-update/SKILL.md) | 按 git 窗口外科更新；也可做 completeness pass |
| [domain-wiki-query](domain-wiki-query/SKILL.md) | 先读 index 再作答 |
| [domain-wiki-ingest](domain-wiki-ingest/SKILL.md) | 一次编译一份不可变原文 |
| [domain-wiki-lint](domain-wiki-lint/SKILL.md) | 结构巡检 |

对应 slash 入口在 [`commands/`](../commands/) 下的 `domain-wiki-*.md`。

## Wiki 根

默认 `<repo>/wiki/`。探测顺序：用户给出的目录 → `wiki/INSTRUCTIONS.md` → `index.md` 与 `log.md` 同时存在。

init/update 按各自的 `discovery-protocol.md` 压缩上下文，用骨架和 coverage-gates 覆盖全仓真实领域。接口族、界面、命名流程必须独立成页，总览表格不算覆盖。写完 `status=complete`。

实现证据只来自仓库源码、人手文档、用户点名原文和本 wiki。不要把构建产物或其他编译文档树当源或模板。只写 `wiki/` 和 AGENTS 标记块，不写产品规格或其他文档树。

## 安装

把需要的技能目录复制到 agent 的 skills 搜索路径，并把对应 `commands/domain-wiki-*.md` 复制到 commands 目录。
