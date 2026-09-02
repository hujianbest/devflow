---
name: using-domain-knowledge
description: 在任何设计或实现任务中需要业务语义、系统落点、规则例外或历史决策时使用：按 index → 摘要 → Concept → 原文的顺序读团队领域知识 Bundle，正确标注 draft，并在任务结束或发现矛盾、路由错误、缺失规则、设计取舍、stable 被推翻时把发现写成 .kb/proposals/ 提案。也在用户提到领域知识库、知识包、Bundle、回写知识时使用。不用于建设、摄入、同步、审核知识库（那是 domain-knowledge-maintain），也不直接修改 knowledge/。
---

# Using Domain Knowledge

## 定位

这是任务时的两个循环：② consume 怎么读，③ capture 什么必须写回。任何 Coding Agent 或 Design Agent 在任务里都用它；它不加载维护流程，不改 `knowledge/`。

知识库首先是路由和约束，不是百科。用它决定去哪个领域、哪个应用、找谁，以及哪些规则不能碰；函数怎么实现、契约长什么样、配置现在是什么值，回真源看。

## 按需参考

- 四层读法、两条路径、回答规则：[consume-protocol.md](references/consume-protocol.md)
- 回写触发、分类、边界：[capture-protocol.md](references/capture-protocol.md)
- 提案文件格式：[proposal-template.md](references/proposal-template.md)

## Bundle 在哪

按顺序找：`DOMAIN_KB_ROOT` 环境变量 → 仓库根 `.domain-kb` 指针文件 → 仓库根 `domain-kb/` → 当前仓库根（有 `knowledge/index.md`）。找不到就明说"没有领域知识 Bundle"，不假装读过。

## ② 怎么读

四层，每层都只在上一层判断相关后进入：

| 层 | 读什么 | 何时进入 |
|---|---|---|
| 1 | `knowledge/index.md`：每条带 type、一行摘要、status、view、owner | 每个任务 |
| 2 | 领域 `overview.md` / 系统 `overview.md`、领域 `index.md` | 确定候选 Context 后 |
| 3 | 少量 Concept 正文；必要时沿 Context Relationship 扩一跳 | 判断相关后 |
| 4 | 原文：代码、契约、ADR、制度 | 高风险、冲突、或 Concept 不够用 |

Design Agent（可不持有代码仓）：识别 Context → 根 index → overview / glossary / processes / rules → 按 `view` 分开 AS-IS 与 TO-BE → 少量 Concept → 需要源码级细节时停止，说明缺少代码仓或建议转 Coding Agent。

Coding Agent（持有代码仓）：识别 Context → 根 index → 领域 index 与系统骨架 → 精确匹配 API、Topic、表名、符号 → 回仓库 grep、读契约原文 → 高风险结论回原始证据核对。骨架页上的入口清单指向真源；没装 expand 时不在 Bundle 里找 Endpoint 页。

`.kb/` 是控制面：提案、冲突、审核队列、扫描结果。可以看，不能当正式结论引用。

## 回答规则

- 默认可用 `draft` 与 `stable`；`deprecated` 不参与默认回答；
- 同时存在 `stable` 与 `draft` 时结论跟 `stable`，`draft` 只作未确认变更提示；
- 凡使用 `draft`，回答里必须出现"未确认"并给出 Concept 路径；
- 安全、资金、权限、发布规则的 `draft` 只能当候选，不得写成可执行策略或直接落成代码；
- `view: to-be` 是目标不是现状；目标设计默认走 TO-BE 并显式标注，不与 AS-IS 混答；
- 没有代码仓时不得把 `systems/` 骨架写成源码级事实；
- Concept 过了 `stale_after`、来源已删除、正文标"存在冲突"时，回答先说明这一点，再回真源或找 owner；
- 证据冲突、过期或不足时拒答或请求 owner，不补全故事；
- 知识可读不等于允许操作：Bundle 里写着的开关、账号、路径，不代表可以改。

项目 hooks 会在读到 `draft` / `deprecated` / 过期 / TO-BE 页时追加提醒；没有 hooks 时以上规则同样成立。

## ③ 什么必须写回

任务结束前，或任务中出现以下任一情况，写提案：

| 发现 | kind | 为什么不能丢 |
|---|---|---|
| 两页 Concept 互相矛盾，或 Concept 与真源矛盾 | `conflict` | 下一个 Agent 会选另一边 |
| index 或 overview 把任务路由错了 Context / 应用 | `route-error` | Bundle 在误导 |
| 用到一条 Bundle 里没有、但对任务关键的规则或例外 | `new` | 连续性：同事会变老 |
| 做出了会影响后续任务的设计取舍 | `refine` | 决策动机 grep 不回来 |
| 某条 `stable` 已被代码合并推翻 | `stale` | 漂移是默认故障 |

按 [capture-protocol.md](references/capture-protocol.md) 与 [proposal-template.md](references/proposal-template.md) 写入 `.kb/proposals/<YYYY-MM-DD>-<slug>.md`。任务 Agent 到此为止，由 `domain-knowledge-maintain ingest` 处理。

边界：

- 不直接改 `knowledge/`（项目 hooks 会拦；没有 hooks 也不改）；
- 提案里不放试错过程、临时变量、会话摘要；会话本身不能当来源；
- 每条发现标 `Observed` / `Derived` / `Inferred`，并给出 commit、文件、契约或工单；
- 不放密钥、token、PII、内网地址；
- 回写不阻塞任务交付；没有需要回写的发现时，明确说"无需回写"。

项目 hooks 会在任务结束时检查：读过 `knowledge/` 却没写提案，会追问一次。回答"无需回写"即可结束。

## 完成输出

任务本身的输出照常。涉及知识使用时在末尾附：

```text
领域知识使用
读取: <n> 条 Concept（draft <n> · stable <n>）
未确认引用: <路径列表 | 无>
拒答 / 回真源: <说明 | 无>
回写提案: .kb/proposals/<file> [kind] | 无需回写
```
