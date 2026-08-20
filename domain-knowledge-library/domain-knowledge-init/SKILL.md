---
name: domain-knowledge-init
description: 为仓库建立覆盖全仓真实领域的首版领域 wiki。用户要求初始化领域 wiki、生成仓库 wiki、从源码编译完整领域 wiki、全仓分析建设领域 wiki 时使用。不用于刷新已有 wiki、查询已编译 wiki，或撰写产品规格。
---

# 领域 wiki 初始化

为首版 `wiki/` 做一次有界但完整的编译：分析全仓真实领域，按栏目写成互链 wiki。落盘只保留领域 wiki 页面和运行元数据，不写评审报告。

按需读 [wiki-contract.md](references/wiki-contract.md)、
[discovery-protocol.md](references/discovery-protocol.md)、
[skeleton-protocol.md](references/skeleton-protocol.md)、
[coverage-gates.md](references/coverage-gates.md)、
[page-types.md](references/page-types.md)、
[frontmatter.md](references/frontmatter.md)。

探测 wiki 根：用户给出的目录 → `wiki/INSTRUCTIONS.md` → `wiki/index.md` 与 `log.md` 同时存在。找不到就询问。本技能只编译领域 wiki，不写产品规格或其他文档树。

## 硬规则

- 不编造文件、模块、API、业务规则。主张落到已检查的源、既有文档或 git。
- 不把整仓读进一个窗口。发现必须按协议落盘。
- 盘点出的每个真实领域必须成页。表格、总览里的一节不算成页。禁止用「先写 8 页 + Backlog」或「收成一张接口/界面总表」交差。必拆规则见 coverage-gates。
- 现状路径和目标路径分开写。未提交、未完成的切片不要写成已发布。
- 已存在且非空的 wiki 拒绝静默覆盖。用户要重建时先确认，或改走 update 的 completeness pass。
- 只写 `wiki/` 和 AGENTS 标记块。不改产品代码，也不写仓库里其他文档树。
- 实现证据只来自仓库源码、人手文档、用户点名原文和本 wiki。不要把构建产物或其他编译文档树当源或模板。
- `INSTRUCTIONS.md` 只在本次创建；不要把它写成生成文档。

## 工作流

### 1. 确认范围

问清 wiki 主要服务谁，除非用户已经说清：

- `code`：从当前仓库编译；
- `sources`：从 `raw/` 或指定原文编译；
- 两者。

范围写进即将创建的 `INSTRUCTIONS.md`。不确定就询问，不默认「把整个公司记忆都建上」。

### 2. 拒绝覆盖

若 `wiki/` 已有概念页或非空 `index.md`：停止，报告现有状态，建议 `domain-knowledge-update`。用户要补全覆盖时走 update 的 completeness pass，不要假装成一次静默 init。
只有人明确要求重建时才继续，并先说明会替换哪些页面。

### 3. 脚手架

创建：

```text
wiki/INSTRUCTIONS.md
wiki/index.md
wiki/log.md
wiki/quickstart.md
```

`INSTRUCTIONS.md` 用 [instructions-template.md](references/instructions-template.md)，填入用户 brief。
`index.md` 先放根 `okf_version` 和空栏目。
`log.md` 先写一条 `## [YYYY-MM-DD] init | Wiki initialized`。

### 4. 发现

严格按 discovery-protocol：

1. 有界 git 摘要；
2. 盘点，禁止根上 `glob **/*`；
3. 大仓按栏目派只读子 agent（默认 4、最多 6），回报写入 `.discovery/`；
4. 写 `_plan.md`：页面、证据、关系、真正的 Backlog。

### 5. 骨架

按 skeleton-protocol 写 `_skeleton.md`，做一轮覆盖评审，解决必改项。没有骨架不得开写概念页。

### 6. 编译

先写 `quickstart.md`，再按骨架写每一页。每页：

- OKF front matter，`type` 必填；
- 解释它做什么、为什么存在、从哪读起、改时注意什么；
- 内联源路径，不堆 Source Map，除非它真能改善导航；
- 流程/生命周期/数据模型可用 Mermaid，图形必须有源。

写完对照骨架和 coverage-gates 做覆盖自检：每个必拆单位都有独立文件。Backlog 只留给证据不足或未成型的项。
孤立概念要补证据关系、合并，或说明为何独立。

注入 `AGENTS.md` / `CLAUDE.md` 的 `DOMAIN-WIKI` 块。

### 7. 收尾

1. 按磁盘同步 `index.md`；
2. 追加 log（若脚手架那条不够描述本次范围，再补一条具体标题）；
3. 删除 `wiki/.discovery/`；
4. 写 `.last-update.json`：`command=init`，`status=complete`，记下 `gitHead`；
5. 跑 `python <skill-dir>/scripts/validate_wiki.py --wiki-root <repo>/wiki`。不要创建 `reviews/` 或其它评审文件。

中途失败：把已写出的页面留下，metadata 写成 `interrupted`，报告停在哪一步。

## 合理化反驳

| 借口 | 为什么不行 |
|---|---|
| 先把目录都建好再填 | stub 会变成孤儿页和评审噪声 |
| 先写 8 页，其余进 Backlog | 已识别领域必须成页；Backlog 不是进度条 |
| 接口和界面已经在总览里列成表了 | 表不是页；大仓必须按族/面拆文件 |
| 再读一轮就能写全 | 用子 agent 和骨架，不要靠膨胀上下文 |
| 再写一份评审报告备查 | 落盘只留领域 wiki；覆盖靠骨架，质量靠页面和证据 |
| 把子 agent 报告贴进 architecture | 发现笔记不是概念，会污染编译层 |
| 没有 git 就整仓通读 | 仍做盘点与定向读；缺 git 只少历史，不改读法 |
| 设计文档里的目标接口已经 import 了，所以图画成已接通 | 那是目标态；现状以实际调用路径为准 |
| 先打开另一棵编译文档树来对齐目录 | 那不是源；只认本 wiki 根和仓库源码 |

## 验证清单

- [ ] 范围已由人确认或用户指令唯一确定
- [ ] 非空 wiki 未被静默覆盖
- [ ] 发现按协议落盘，主窗口没有整仓原文
- [ ] 有骨架和一轮覆盖评审；必拆单位都是独立文件，不是总览表
- [ ] 每条主张有源；现状/目标分开；无密钥、无 `.env`
- [ ] metadata 为 `complete`，磁盘上没有 `reviews/`
