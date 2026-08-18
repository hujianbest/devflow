# Learning 评审准则

草稿通过机械校验后，在全新的只读上下文中使用本准则。评审者不得编辑文件。

## Review Pack

提供：

- learning 目标路径和完整内容；
- source archive 路径；
- 归档后的 `change.json`、`closeout.md` 和草稿引用的源工件；
- 核对当前行为声明所需的 canonical 摘录、代码和测试；
- overlap 候选的元数据与相关摘录；
- 机械校验器输出。

不要提供作者聊天历史。

## 检查项

### 捕获资格

- Source change 已归档，所有必需 gate 已通过；
- 内容非平凡，并会改变一个可信的未来工程选择；
- 文档只包含一条 learning，不是 AR 总结或多个无关经验的拼接。

### 事实落地

逐个读取 `<!-- claim: ... -->`，不能只给整篇印象：

- `historical`：回到对应 archive locator，引用支持该历史事实的原文；
- `current`：回到当前 canonical、代码或测试的定义位置；
- `guidance`：核对证据能否支持该建议，并检查适用与不适用边界；
- 可计数声明：核对正文列举数量与声明一致；
- 已删除或重命名的路径必须明确标为历史路径；
- 不臆造证据中没有的业务意图或设计理由。

每条 claim 返回：

```text
CLM-001 | historical | verified | <仓库相对路径::anchor + 引文>
CLM-002 | current | contradicted | <定义位置 + 修正方向>
CLM-003 | guidance | unverifiable | <缺失证据 + 缩窄或删除方向>
```

判定只允许 `verified`、`contradicted`、`unverifiable`。`contradicted` 必须按引用证据
修正文档；`unverifiable` 必须缩窄、明确归因或删除，不能用聊天补全。

### 与 canonical 分工

- 草稿解释理由、失败方法、适用范围或预防措施；
- 不重复完整需求、接口定义、状态机、设计章节、gate 状态或任务进度；
- 不把自己表述为比当前 canonical 或代码更高的权威。

### 检索价值

- 标题、ID、tags、component 和 type 足以检索；
- 适用和不适用条件具体；
- 错误签名和符号保持最小，但足以支持未来搜索；
- 示例能说明经验，没有复制大段源码或日志。

### 重叠

- 声明的 overlap 级别符合五维比较；
- 高重叠内容更新同一份权威 learning，而不是创建重复文件；
- 中度重叠文档有真实区别并互相引用；
- 相互矛盾的指导没有伪装成一致内容合并。

### 安全与隐私

- 不包含凭证、secret、连接串、认证头或私钥；
- 不包含无必要的个人/客户数据、内部 URL、工作站名称或绝对路径；
- `sensitivity` 符合仓库策略；
- `restricted` 内容应拒绝写入，不能通过删减成失真的文档来规避。

### 维护

- `lastVerifiedAt` 与本次评审一致；
- source path 和 related learning ID 均可解析；
- `active` 有当前证据支持；存在未确认漂移时使用 `stale`。
- `superseded` 有明确 `supersededBy`，且不存在 replacement cycle；
- refresh 只处理已批准 plan 的写集，审计者没有直接修改文件。

## Verdict

返回：

```text
结论: 通过 | 需修改 | 阻塞

问题:
- 严重级: critical | important | minor
  位置: <字段、章节或声明>
  证据: <archive/current source 引文和路径>
  问题: <错误及影响>
  方向: <有边界的修正方向>

重叠: none | low | moderate | high
敏感级别: public | internal | restricted
Grounding: <已验证数量> verified | <矛盾数量> contradicted | <无法验证数量> unverifiable
```

`通过` 要求没有 critical 或 important finding。`阻塞` 表示缺少必需证据或仓库敏感
信息策略，不能猜测。
