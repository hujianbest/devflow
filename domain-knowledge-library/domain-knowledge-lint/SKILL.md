---
name: domain-knowledge-lint
description: 巡检领域 wiki 的结构健康：断链、孤儿页、stub、过期声明、front matter 与 log 漂移。用户要求检查领域 wiki、lint wiki、清理过期页面时使用。不代替 init/update 后的独立质量评审，也不用于回答领域问题或摄入新源。
---

# 领域 wiki 巡检

查结构，不裁定「这句话在源码里是否为真」，也不写评审报告。真伪靠页面证据，过期主张交给 update。不要打开其他编译文档树来对照。

按需读 [wiki-contract.md](references/wiki-contract.md)。

探测 wiki 根：用户给出的目录 → `wiki/INSTRUCTIONS.md` → `wiki/index.md` 与 `log.md` 同时存在。找不到就询问。领域问题走 `domain-knowledge-query`，不要在本技能里重写架构。

## 检查项

1. 跑 `python <skill-dir>/scripts/validate_wiki.py --wiki-root <repo>/wiki`。
2. 概念页之间的 Markdown 链接是否能落到文件。
3. 没有入链、也不在 quickstart/index 出现的页（孤儿）。
4. stub：几乎只有标题、Source Map 或「待补充」。
5. 正文里的过期标记、断裂的「见某某」却没有链接。
6. 根 `index.md` 和各栏目 `index.md` 是否按磁盘上的概念页列出。
7. `log.md` 是否与最近操作一致。
8. mermaid 围栏：空图、节点 id 为 `end`、标签里未转义的 `<>`。
9. 单文件空壳目录。

先出具报告，再改。破坏性合并、删页、改主张：先问人。
纯机械修复可以在报告后直接做，并追加 log：

- 按磁盘重写各目录 `index.md`（只列本目录真实文件，不加散文）；
- 缺 `type` 时用 H1 推断补上，推断不了就报告，不编造栏目；
- 坏 mermaid：能安全改则改（去掉 `end` 节点 id、给 `<>` 加引号）；改不了就降成普通列表或删掉空围栏，并在页上留一句「图已降级」。

## 不要做

- 不要重写仍然准确的段落；
- 不要把结构修复写成评审报告或 `reviews/`；
- 不要读取 `.env`、忽略路径或导出文档树去「补全」文档。
- 不要改 `.last-update.json` 的 `status`。

## 输出

```text
领域 wiki 巡检

机械校验: 通过 | 失败（列出）
断链: N
孤儿: N
stub: N
坏 mermaid: N
建议修复: ...
已做的机械修复: ...
待确认的破坏性改动: ...
```

追加 `## [YYYY-MM-DD] lint | <short title>`。
lint 本身不改 `.last-update.json` 的 `status`。

## 验证清单

- [ ] 先报告后修改
- [ ] 机械校验已跑；目录 index 已按磁盘对齐
- [ ] 未创建 `reviews/` 或其它评审文件
- [ ] 未改 `.last-update.json` 的 `status`
- [ ] 删页或合并已得到人确认
