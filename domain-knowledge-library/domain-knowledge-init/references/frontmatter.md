# 概念页 Front Matter

采用 Google OKF v0.2 的可执行子集。每个非保留 Markdown 概念页必须以 YAML 开头。

```yaml
---
type: Architecture overview
title: 运行时分层
description: 进程如何接请求、落到存储，以及失败时谁负责。
tags: [runtime, storage]
generated: { by: domain-knowledge-init/agent, at: 2026-08-18T00:00:00Z }
---
```

规则：

- 只有 `type` 必填。选短、能自解释的种类，例如 `Architecture overview`、`Workflow`、`Concept`、`Source summary`、`Playbook`。不要自建注册表。消费者必须容忍未知 type。
- 推荐：`title`、面向检索的一句 `description`、`tags`（稳定英文短词）、`generated`。绑到具体资产时加 `resource`（绝对 URI、`/` 开头的 wiki 相对路径，或普通相对路径）。
- `generated` 记录谁、何时写出当前内容。`by` 用 actor：`技能/模型`、`human:<id>`、`process:<名>`。人手写或人手确认必须用 `human:` 前缀。新页不要写 v0.1 的 `timestamp`；读旧页时若没有 `generated`，可回退到 `timestamp`。
- 可选家族（缺了不拒收，但缺本身有含义）：
  - 出处 `sources`：每条必有 `resource`。主张用 `[^id]` 脚注对齐 `sources[].id`，不要写正文 `# Citations`。可选信号：`author`、`usage_count`、`last_modified`。这是 front matter 列表，不是 `sources/` 栏目页。
  - 核验 `verified`：`{ by, at }` 列表；单条可写成裸 mapping，读时当一元素列表。信任档由消费者从 `verified` 推导：无键 = unverified；仅非 `human:` = machine-confirmed；有 `human:` = human-reviewed。
  - 生命周期 `status`：`draft` | `stable` | `deprecated`（缺省 `stable`）。`stale_after` 用绝对日期 `YYYY-MM-DD`，当天及之后算过期，不要写相对 TTL。
- `runtime`、`parameters`、`computation`、`executor`、`attester` 只给 `type: Attested Computation` 用。普通概念页不要写。
- `index.md` 与 `log.md` 不加概念 front matter。根 index 可以只有 `okf_version: "0.2"`。
- 更新时保留已有、仍然正确的扩展字段。不要为了「干净」删未知键。
- 有效 YAML。不要把占位符或解释性注释写进 front matter。
- 本 wiki 的主张置信度是扩展，不是 OKF 信任档：`confirmed`、`source-backed`、`contested`。来源冲突且没有当前源能裁定时，用 `contested`，不要用新旧日期偷偷选边。不要把 `confirmed` 写成 `verified`。

`INSTRUCTIONS.md`、`.discovery/**` 不是概念页。
