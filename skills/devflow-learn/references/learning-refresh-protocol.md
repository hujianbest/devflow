# Learning Refresh 协议

只在 `refresh-audit` 或 `refresh-apply` 时读取。年龄、措辞风格或“看起来旧”都不是维护
证据；维护必须降低未来误用或检索成本。

## 角色与授权

- audit 始终只读，只生成 plan；
- apply 需要用户明确批准 plan ID；
- audit 与独立 reviewer 不执行修改；
- 主控只能修改 plan 的 write set；
- digest 漂移、动作升级或发现新入链引用时停止并重新审计。

脚本可以自动建议 `keep`、`mark-stale`、`repair-related`、`link-supersession` 或
`manual-rewrite-required`。以下高影响动作必须由人确认后由主控执行。

## Keep

当前证据仍支持核心指导，locator 和关系均有效时不编辑文件。不要为了刷新日期、措辞、
格式或拼写制造 churn。

## Update

只在核心指导仍正确时原位更新，例如：

- 目录或符号重命名；
- 当前 anchor 漂移但语义未变；
- 修复 related edge 或失效链接；
- 增加新的独立验证来源。

旧做法已成反模式、架构已改变或排查路径实质不同，不属于 Update。

## Consolidate

两份文档表达同一 learning，且合并能提升检索价值时：

1. 选择更完整、当前且准确的文档作为保留项；
2. 提取另一份的独有边界、失败方法或预防规则；
3. 在自然位置合并，不机械追加；
4. 重写全部入链与 related edge；
5. 重新执行 claim/evidence、store 与独立语义复核；
6. 经用户确认后删除被吸收文档。

三个以上候选必须两两顺序处理。共享标签或文件不等于可合并。

## Split

只有一份文档包含多个独立问题，导致检索某一主题时必须阅读大量无关内容，且每个片段
都有独立复用价值时才拆分。长度本身不是理由。

Split 必须逐份执行，为每个 successor 建立完整 claim/evidence 和来源；重写入链后再
删除原文。非交互模式只报告建议，不执行。

## Replace

核心推荐已被当前证据否定时创建 successor，而不是把旧文档原位改成相反结论：

1. 保留旧 learning 的历史证据；
2. successor 使用新的稳定 ID、完整证据和适用边界；
3. 旧文档设为 `superseded`，填写 `statusReason` 与 `supersededBy`；
4. 检查 replacement cycle 和全部入链；
5. 新旧文档都通过 store 校验和独立复核。

证据不足以写 successor 时只把旧文档标为 `stale`，不得猜新方案。

## Delete

只有以下事实明确成立时才能删除：

- 问题域已经消失；
- 内容完全被另一份 learning 吸收且没有独有信息；
- 文档不再表达任何可复用结论。

删除前搜索全部入链、related 与 supersession 关系。发现未在 plan 中的实质引用时停止
并重新分类。不得因为年龄、零命中或 locator 暂时无法验证而删除；Git 历史不能替代
删除前的引用清理。

## 完成条件

- 实际写集没有超出批准 plan；
- 每个目标 before digest 与 plan 一致；
- 单文档和 store 校验通过；
- related 双向、supersession 无环；
- 每个受影响 claim 完成独立复核；
- 输出唯一 `终止状态: complete`，否则为 `blocked`。
