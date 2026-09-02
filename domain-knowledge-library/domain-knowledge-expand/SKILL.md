---
name: domain-knowledge-expand
description: 仅在用户或任务明确请求为领域知识 Bundle 深化指定模块、Context 或高风险入口时使用：为选定范围生成 API Endpoint、Event Channel、Data Model、Configuration 级 Concept，并按事故半径、资金权限、变更频率、跨 Context 密度选择对象。不在 bootstrap 中隐式运行；不用于按仓库清单扫平所有接口；不用于普通读知识或写提案（using-domain-knowledge），也不用于摄入、同步、审核（domain-knowledge-maintain）。
---

# Domain Knowledge Expand

## 定位

可选深化。冷启动只出 `systems/` 骨架；当 ② consume 或 ③ capture 反复暴露"骨架不够用"时，才对特定范围生成实现细节 Concept。它是一个显式动作，不是冷启动的隐藏步骤。

未安装或未触发本技能时，任何循环都不得批量生成 API Endpoint / Event Channel / Data Model / Configuration。`kb.py validate` 以 `expanded_by` 字段锁住这一点：没有该字段的实现细节类型直接报错。

## 按需参考

- 选择对象、四类模板、退出条件：[expand-workflow.md](references/expand-workflow.md)
- 知识形态与门禁：`domain-knowledge-maintain/references/bundle-contract.md`

## 入口

```text
/domain-knowledge-expand <scope> [--reason <text>] [--types endpoint,event,data,config]
```

`scope` 必须具体：一个 Module 路径、一个 Bounded Context 的一组入口、或一组明确列出的接口 / 表 / Topic。`--reason` 说明触发来源（哪次任务、哪条提案暴露了骨架不足）。缺 scope 或 scope 为"全部"时停止询问。

## 流程

1. 定位 Bundle，读 `config.yaml`；`expand.enabled` 为 false 时改为 true 并在 log 记录首次启用；
2. 取锁：`kb.py lock expand`；
3. 按 [expand-workflow.md](references/expand-workflow.md) 的优先级对 scope 内候选排序：事故半径、资金/权限、变更频率、跨 Context 调用密度；超出用户给的上限（默认 20 条）时先给清单让用户裁；
4. 对每个对象从真源（契约文件、迁移、配置声明、代码）提取 Observed 事实，写入 `systems/<app>/{interfaces,events,data-models,configurations}/`，frontmatter 带 `expanded_by: domain-knowledge-expand`，`status: draft`；
5. 在对应 Module / Application 页的入口清单里把该项链接到新 Concept；
6. `kb.py validate --check-index`、`kb.py index`、`kb.py log expand "<scope>"`、`kb.py unlock`。

## 规则

- 只写指针与解释，不复制契约正文、DDL、完整配置；每条 Concept 必须能回答"谁调用 / 谁监听 / 谁写这张表 / 改它会影响哪些 Context"；
- 机械事实可由 `tool:` 验证后 `stable`；涉及业务含义（字段的业务语义、Topic 的领域事件含义）的行标 Inferred，保持 draft；
- 不深化 scope 之外的对象，即使"顺手"很容易；
- 深化产物默认 `stale_after` 更短（`config.yaml.freshness.detail`），因为它们随代码变得更快。

## 停止条件

- scope 不具体或要求扫平整个仓库；
- 对象数量超上限且用户未裁；
- 真源缺失（没有契约文件、迁移不可读）却要求生成页；
- 锁被持有。

## 完成输出

```text
知识深化完成

范围: <scope>
原因: <reason>
新建: Endpoint <n> · Event Channel <n> · Data Model <n> · Configuration <n>
更新入口清单: <n> 页
校验: kb.py validate --check-index 通过
未深化（超上限或无真源）: <列表>
锁: 已释放
终止状态: complete | blocked
```
