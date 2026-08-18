# 领域 wiki 说明

这是给后续 agent 的 brief，不是生成文档。更新 wiki 时阅读它，不要在普通 init/update/query 里重写。

## 目的

<一句话：这个 wiki 帮谁回答什么问题>

## 模式

- 模式：`code` | `sources` | `both`
- 语言：`zh`

## 范围

优先记录：

- <架构 / 工作流 / 领域概念 / …>

不要记录：

- 密钥与 `.env`
- 生成物、依赖锁的逐文件清单
- 可从源码一眼看出、且没有「为什么」的内容

## 质量

- 主张必须落到源码、既有文档或 git。
- 不确定写进 `quickstart.md` 的 Backlog 或标 `source-backed` / `contested`，不要编。
- 先查 `index.md` 再下钻页面。
