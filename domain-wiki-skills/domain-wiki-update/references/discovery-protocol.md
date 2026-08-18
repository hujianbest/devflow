# 发现协议

init 和需要理解仓库的 update 必须按本协议压缩上下文。目标：主窗口里只有摘要、骨架和当前页，而不是整仓源码；落盘却是覆盖全仓真实领域的 wiki。

## 为什么

大仓库不能靠「再读一轮」撑窗口，也不能靠「先写 8 页、其余进 Backlog」交差。先收集有界 git 摘要，把发现交给按栏目切开的只读子 agent，用骨架覆盖当阀门。同等纪律靠落盘，不把整仓原文留在主对话里。

## 强制顺序

```text
1. 有界 git 摘要     → wiki/.discovery/git-summary.md
2. 仓库盘点         → wiki/.discovery/inventory.md
3. 只读子 agent     → wiki/.discovery/findings-<area>.md
4. 计划             → wiki/.discovery/_plan.md
5. 骨架与覆盖评审   → wiki/.discovery/_skeleton.md
                      wiki/.discovery/skeleton-review.md
6. 按骨架定点重读并写页
7. 删除 .discovery/
8. 写 complete 元数据；不落盘评审报告
```

任一步把原文或子 agent 全文灌进主对话，都算失败。没有骨架不得开写概念页。

## 1. 有界 git 摘要

主 agent 自己跑，不要派子 agent。只收集路径和状态，不贴完整 diff。

```text
git status --short
git rev-parse HEAD
```

再按窗口追加：

- init，或 update 没有 `gitHead` / `updatedAt`：
  `git log --max-count=20 --name-status --oneline`
- update 且有 `gitHead`：
  `git log <gitHead>..HEAD --name-status --oneline`
- update 仅有 `updatedAt`：
  `git log --since <updatedAt> --name-status --oneline`

最后：

```text
git diff --name-status HEAD
```

过滤 `.wikiignore` 命中路径、本 wiki 根自身的变更，以及明显的构建产物或导出文档树。摘要写入 `.discovery/git-summary.md`，格式保持命令名 + 输出，便于回看。

## 2. 仓库盘点

先建地图，再决定读什么。禁止从仓库根 `glob **/*`。

优先看：

1. README、既有 `docs/`、`AGENTS.md`（只读，不在本步改）；
2. 包/构建/配置（`package.json`、`pyproject.toml`、`go.mod`，锁文件只看名字）；
3. 入口、路由、主程序、schema、IDL；
4. 顶层领域目录名，不是目录里每个文件；
5. 测试树骨架（测什么，不读完所有用例）；
6. 运维脚本、技能/playbook、组合根。

盘点页只记：领域、入口路径、似乎重要的文件、开放问题。大文件用 grep 或分段读，不整文件加载。跳过本 wiki 根、忽略路径，以及构建产物或导出文档树。

## 3. 只读子 agent

何时派：

- 小仓、盘点已经够写骨架：不派；
- 中仓：2–3 个；
- 大仓或不熟：按栏目派，默认 4 个，最多 6 个并行。

每个 brief 只覆盖一个面，例如：既有文档、运行时架构、领域模块、接口与界面、数据/存储、测试/运维。

子 agent 必须：

- 只读；
- 不创建、编辑、删除、移动任何文件，尤其是 `wiki/`；
- 不把构建产物或导出文档树当实现证据；
- 回报短发现：结论、源路径、未知项；
- 不贴大段源码。

主 agent 把每份回报写入 `.discovery/findings-<area>.md`。当内部笔记用，不进用户回复，不进概念页。

## 4. 计划

在写概念页之前创建 `.discovery/_plan.md`：

- 拟写页面（按覆盖阀门，不按 8 页上限）；
- 每页的证据锚点（仓库相对路径）；
- 关系：`源概念 -> 关系含义 -> 目标概念`；
- 进 Backlog 的领域及原因（仅证据不足或尚未成型）。

没有计划就开写，视为违反协议。

## 5. 骨架与覆盖评审

按 [skeleton-protocol.md](skeleton-protocol.md) 把计划展开成文件树，做一轮只读覆盖评审，再开写。

## 6. 定点写入

按骨架一次写一页。写某一页时，主上下文保留：

- git 摘要；
- 盘点清单；
- 相关 findings 的要点；
- 骨架里该页的一行职责；
- 当前页已有正文。

不要为了「保持文风一致」把已写完的页面全文再读一遍。需要交叉链接时，只看骨架里的标题和路径。

主张落到已检查的源。现状路径和目标路径不一致时分开写，不要把设计里的目标接口画成已经接在运行路径上。未提交、未完成的切片标 `source-backed`，不要写成已发布。

## 7. 覆盖阀门

成功标准：盘点出的每个真实领域都有**独立概念文件**。总览表格不算。必拆与允许合并见 [coverage-gates.md](coverage-gates.md)。

不要用「先写 8 页」当完成条件。也不要给每个源文件一页。

- 真薄页（没有独立不变量）并入栏目 `overview.md`。
- 小仓（大约不超过 10 个主源）：`quickstart.md` 加至多 1–2 个支持页。
- 大仓：按栏目建目录；每个模块、接口族、界面、适配器、命名流程各一页。这些面禁止收成根上的单文件。

Backlog 只留给：证据不够、切片未成型、或人明确排除的领域。每条仍要领域名、源锚点、一行原因。禁止用 Backlog 消化「已经识别、只是还没写到」的领域。

Update 的普通外科窗口仍窄：少文件变更时最多改 1–2 页；改超过 3 页必须先在计划里写清为什么。用户明确要求补全覆盖时，走 completeness pass，不受 1–2 页限制，但仍要骨架。

## 8. 清理

写入结束后删除整个 `wiki/.discovery/`。计划、骨架、子 agent 笔记都不是概念，不链到它们，也不要改写成评审报告。
