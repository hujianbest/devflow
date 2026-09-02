# capture 协议

任务中的发现如果不回流，下一个 Agent 会再发现一次，且可能得出相反结论。回写是把发现变成提案，不是修改知识。

## 触发

任务结束时检查一遍；任务中出现以下任一情况立刻记下，结束时一并写：

| 发现 | kind | 判定线索 |
|---|---|---|
| 两页 Concept 互相矛盾，或 Concept 与代码 / 契约 / 制度矛盾 | `conflict` | 你不得不选一边才能继续 |
| index / overview 的 description、tags、context 把你带到了错的 Context 或系统 | `route-error` | 你在第 2 层读了才发现不对 |
| 任务依赖一条 Bundle 里没有、但决定了做法的规则或例外 | `new` | 你从代码、制度或人那里学到的，而不是从 Bundle |
| 你做了会影响后续任务的设计取舍（选了 A 放弃了 B 及其原因） | `refine` | 三个月后有人会问"为什么" |
| 一条 `stable` 已被合并的代码推翻 | `stale` | 你在真源看到的与 stable 正文不一致 |

不值得写：拼写、格式、你自己的试错、只对本次命令有意义的细节、对 Concept 的复述、未经证据的猜测。

## 步骤

1. 每条发现一个 kind；一个提案文件可以含多条同 kind 的发现，不同 kind 分文件；
2. 每条发现标 `Observed` / `Derived` / `Inferred`，附来源（commit + 路径、契约版本、制度文件、工单号）与 role；
3. 写 `.kb/proposals/<YYYY-MM-DD>-<slug>.md`（模板见 proposal-template.md）；
4. `route-error` 与 `stale` 说明 Bundle 在误导，维护者会同时进 review-queue；你不用自己写队列；
5. 在任务输出末尾列出提案文件。到此为止。

## 边界

- 不改 `knowledge/`；不改 `.kb/` 里除 `proposals/` 以外的任何东西；
- 会话、聊天、你自己的推理过程不是来源；
- 不放密钥、token、连接串、PII、内网 URL、机器绝对路径、大段日志；
- 不把提案写成"已确认"；提案的状态由 ingest 与 review 决定；
- 回写不阻塞交付。没有需要回写的发现时，明确回答"无需回写"。

## 与 hooks 的配合

装了项目 hooks 时：

- 直接写 `knowledge/**` 会被拦并提示改写提案；
- 写 `.kb/proposals/` 时若含密钥模式会被拦；
- 任务结束（stop）时若本会话读过 `knowledge/` 且没写提案，会收到一次追问；回答"无需回写"或写提案即可。

没有 hooks 时，以上仍是你的责任。
