---
name: domain-knowledge-update
description: 按 git 增量或新证据外科更新已有领域 wiki；用户要求补全、建成完整领域 wiki 或对齐全仓覆盖时做 completeness pass。源码刚合入、文档过期、刷新或补全领域 wiki 时使用。不用于首建 wiki、普通提问、摄入一份外部原文，或改写产品代码与规格。
---

# 领域 wiki 更新

刷新已有 `wiki/`，只改被源变化打到的页面。落盘只保留领域 wiki，不写评审报告。
无相关变化且 wiki 已是 `complete` 时，允许 no-op。

按需读 [wiki-contract.md](references/wiki-contract.md)、
[discovery-protocol.md](references/discovery-protocol.md)、
[skeleton-protocol.md](references/skeleton-protocol.md)、
[coverage-gates.md](references/coverage-gates.md)。

探测 wiki 根：用户给出的目录 → `wiki/INSTRUCTIONS.md` → `wiki/index.md` 与 `log.md` 同时存在。找不到则走 `domain-knowledge-init`，不要把本技能假装成 init。

## 硬规则

- 先读现有 wiki 和 `.last-update.json`，再碰源码。
- 先做 impact plan：`源变更 -> 受影响页面 -> 是否改 -> 为什么`。对不上的页不要改。
- 普通更新：少文件变更时最多改 1–2 页。要动超过 3 页，先在计划里写清理由。completeness pass 不受此限，但仍要骨架。
- 一个概念一页。新解释并入已有规范页，不要平行复制。
- 准确的原文和结构予以保留。宁改一句过期的话，不要加一段新散文。
- 不做格式-only 编辑：不为了对齐表格、空行、列表顺序而改页。
- 不改 `quickstart.md`，除非产品行为、安装步骤或栏目导航变了。
- 不刷新 commit hash 列表。某次提交本身解释了历史决策时才写那一次。
- 图过期等于主张过期。改流程句时同步改 Mermaid。节点 id 不用 `end`，标签里的 `<>` 要转义。
- 不编造。冲突时以当前源为准，并标明过期文档。
- 实现证据只来自仓库源码、人手文档和本 wiki。不要把构建产物或其他编译文档树当源或模板。
- 不创建 `reviews/` 或其它评审文件。

## 工作流

### 1. 定位

没有 wiki 根：路由 `domain-knowledge-init`。不要把 update 假装成 init 命令，只是走首建流程。

读 `INSTRUCTIONS.md`、`quickstart.md` 的 Backlog、`.last-update.json`。

用户明确要求补全、建成完整领域 wiki、全仓分析或对齐全仓覆盖时：走第 3b 步 completeness pass，不要当成 no-op，也不要假装成 init 覆盖。

### 2. 判断是否要跑

收集有界 git 窗口，写入 `.discovery/git-summary.md`（若将开写）。

应当跑：

- 没有上次 `gitHead`；
- 上次 `status=interrupted`；
- 工作区有非 wiki、非 ignore 的变更；
- `HEAD` 相对上次有非 wiki 的提交；
- 用户给了明确更新指令。

可以 no-op：

- `status=complete`；
- 工作区与提交都没有相关源变化；
- 现有页面仍然准确。

no-op 时不改文件，报告「wiki 已是 complete」，不要刷新时间戳。

### 3. Impact plan

把 git 窗口里的路径映射到现有页面。写 `.discovery/_plan.md`：

- 要改的页、要加的页、要删的过期主张；
- 每项对应的源路径；
- 是否提升某条 Backlog。

页面若不能连到本次源、工作流、产品或既有文档变化，保持不动。

### 3b. Completeness pass

已有 wiki 太薄、Backlog 里堆着已识别领域、或用户要求完整覆盖时：

1. 按 discovery-protocol 重新盘点（仍禁止根 `glob **/*`）；
2. 对照现有页面写骨架：缺的领域补页，薄页合并，过期主张标出来；
3. 按 skeleton-protocol 做一轮覆盖评审；
4. 按骨架补写，不受 1–2 页外科预算限制；
5. 已识别领域不得继续只留在 Backlog，也不得收成接口或界面总览表。对照 coverage-gates。

保留仍然准确的原文。不要为了「看起来完整」重写所有旧页。

### 4. 外科编辑

只打开计划里的页和对应源。需要理解一大块陌生领域时，才按 discovery-protocol 派只读子 agent，仍然禁止通读。

编辑时：

- 过期句子就地替换；
- 新概念优先并入已有规范页；
- 流程/生命周期页缺少图且你已经在改它：可以补一张有源的 Mermaid（`flowchart` / `sequence` / `state` / `er`）；
- 不要为了「刷新」去改 Source Map 或 git 证据列表。

提升 Backlog：仅当本次变化打到该领域，或更新仍有余量。写完从 Backlog 移除。
普通更新可以把未碰到的已识别领域留在 Backlog。completeness pass 不行。

### 5. 收尾

1. 按磁盘同步根 `index.md` 和各栏目 `index.md`；
2. 自检：断链、孤儿页、仍把已识别领域堆在 Backlog 的条目；
3. 追加 `## [YYYY-MM-DD] update | <title>`；
4. 删除 `.discovery/`；
5. 有内容变化：`status=complete`，更新 `gitHead` 与 `updatedAt`；
6. 跑 `python <skill-dir>/scripts/validate_wiki.py --wiki-root <repo>/wiki`。不要创建评审文件。no-op 不改 metadata。

中途失败：`status=interrupted`。已写出的 diff 留下，供下次续跑。

## 合理化反驳

| 借口 | 为什么不行 |
|---|---|
| 顺便把文风统一一下 | 格式-only 会制造无意义 diff，淹没真正过期的句子 |
| 既然都打开了就多改几页 | 普通更新超预算必须先写进计划；默认 1–2 页 |
| wiki 已 complete 所以不能补全 | complete 只表示上次跑完；用户要全仓覆盖时走 completeness pass |
| complete 了但我想刷新时间戳 | 空转会骗过后续 no-op 判断 |
| 顺手写一份评审记录 | 落盘只留领域 wiki |
| 对照另一棵编译文档树改文风 | 那不是源；只认本 wiki 和仓库源码 |

## 验证清单

- [ ] 已读 wiki、brief、metadata 和 Backlog
- [ ] no-op 只发生在 `complete` 且无相关源变化
- [ ] 每个编辑都能回到 impact plan 或 completeness 骨架
- [ ] 未做格式-only、无关重写，也未无故改 quickstart
- [ ] 未把构建产物或导出文档树当源
- [ ] completeness pass 已覆盖识别出的领域，没有用 Backlog 消化已识别项
- [ ] 有变化则 metadata 为 `complete`，没有 `reviews/`
