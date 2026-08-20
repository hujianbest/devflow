# Wiki 契约

路径和元数据的权威。落盘只保留领域 wiki 结果，不写评审报告。

## 根与探测

默认根是仓库根下的 `wiki/`。路径写成仓库相对、`/` 分隔，例如 `/wiki/quickstart.md`。

探测顺序：

1. 用户给出的目录；
2. `wiki/INSTRUCTIONS.md`；
3. `wiki/index.md` 与 `wiki/log.md` 同时存在。

找不到就询问，不在当前工作目录猜测，不把 `docs/`、构建产物或导出文档树当成 wiki 根。多个候选同时成立时询问。

## 证据边界

实现证据只来自：

1. 仓库源码和人手维护的文档；
2. 用户点名的一份原文（ingest）；
3. 已探测到的本 wiki 根。

不要把构建产物、站点导出、第三方知识库导出或其他编译文档树当成实现证据、wiki 根或栏目模板。用户没有点名的目录，不要打开来对齐结构或文风。

git 摘要与发现排除：本 wiki 根、`.wikiignore` 命中路径、以及明显的构建/导出目录。

## 保留路径

| 路径 | 角色 | 谁写 |
|---|---|---|
| `INSTRUCTIONS.md` | 用户 brief / schema | init 创建；之后仅用户明确要求时改 |
| `index.md` | 内容目录 | 每次会改概念页的操作之后同步 |
| `log.md` | 只追加操作日志 | 每个操作追加一条 |
| `.last-update.json` | 上次成功或中断的运行状态 | init/update/ingest；no-op 且已是 complete 则不改 |
| `quickstart.md` | 人类与 agent 入口 | init 必写；update 仅导航或产品行为变了才改 |
| `.discovery/` | 临时发现、计划与骨架 | init/update 写入，跑完删除，不提交 |
| `raw/` | 不可变源 | ingest 只新增 |

`index.md`、`log.md`、`INSTRUCTIONS.md`、`.last-update.json`、`.discovery/**` 不是概念节点。
不要创建 `reviews/` 或任何评审报告文件。

## `.last-update.json`

```json
{
  "updatedAt": "2026-08-14T00:00:00Z",
  "command": "init",
  "gitHead": "abc123",
  "status": "complete",
  "language": "zh"
}
```

- `updatedAt`：ISO 8601。内容有变，或从 `interrupted` 恢复完成时更新。
- `command`：`init` | `update` | `ingest`。
- `gitHead`：当时 `git rev-parse HEAD`；非 git 仓库可省略。
- `status`：`interrupted` | `complete`。
- `language`：BCP-47，缺省 `zh`。

写规则：

- 跑到一半失败：`status=interrupted`，保留已写页面，下次不得 no-op。
- init/update/ingest 成功改了概念页：`status=complete`。
- 内容无变化且原状态已是 `complete`：不改本文件。

## `log.md`

```text
## [YYYY-MM-DD] <op> | <title>
```

`op` 为 `init` | `update` | `query` | `ingest` | `lint`。只追加。

## `index.md`

根 index 可以只有 `okf_version: "0.2"`。按类别列出概念页。子目录导航页也叫 `index.md`，不加概念 front matter。

## AGENTS 标记块

只改自己的块。文件不存在则创建最小文件再插入。

```markdown
<!-- DOMAIN-WIKI:START -->
回答仓库问题前，先读 `/wiki/index.md` 和 `/wiki/quickstart.md`。
用 wiki 页面作答并引用链接。wiki 缺失或过期时再下钻源码，并说明依据。
<!-- DOMAIN-WIKI:END -->
```

`AGENTS.md` 与 `CLAUDE.md` 都维护同一段。

## `.wikiignore`

仓库根，gitignore 语法。命中路径：不读、不写进 wiki、不从内容推断实现。查询下钻源码时同样遵守。

## 校验

```text
python <skill-dir>/scripts/validate_wiki.py --wiki-root <repo>/wiki
```

脚本查 schema、log 前缀、概念页 `type`，以及 mermaid 围栏的廉价启发式。不重写文件。
