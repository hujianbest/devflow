# 长期资产 Promotion 规则

> 配套 `devflow-ship`。规定如何把 `features/<id>/` 的过程产物沉淀到组件仓库 `docs/`。核心原则：**语义化改写，不是复制**——过程内容留在 features/，契约内容进入 docs/。

## 同步对象

| 过程工件 | 长期资产 | 何时同步 |
|---|---|---|
| `spec.md` | `docs/ar-specs/<id>-<slug>.md` | AR / CHANGE 工作项必做；纯缺陷修复（无规格变更）写 N/A |
| `design.md` | `docs/ar-designs/<id>-<slug>.md` | 有正式工作项设计时必做 |
| `component-design-draft.md` | `docs/component-design.md` | 本工作项修订了组件设计时必做；需模块架构师确认 |

项目通过 `AGENTS.md` 声明等价路径时优先遵循团队约定。可选子资产（如团队单独维护的 `docs/interfaces.md`）只在项目已启用且本次触发变化时同步；未启用的把变化合并进 `docs/component-design.md` 对应章节，不自动新建。

## 语义化改写要求

promote 时必须做的转换：

**去掉草稿专属内容**：

- Open Questions 节（应已闭合；保留闭合结果，不留待决项）
- 评审 findings 应答、过程笔记、会议纪要片段
- `TODO` / `待澄清` / 模板提示残留

**保留与补全**：

- 追溯锚点：工作项 ID、上游来源、测试设计用例 ID、评审记录路径（`features/<id>/reviews/...`）
- 文档头部记录 Promoted From（指向过程工件的 commit 锚点）
- 长期文档的「变更记录」表追加本次修订：`(日期, 修订者, 触发工作项, 摘要)`

**组件设计修订的额外纪律**：

- 只更新本次受影响的章节，不顺手重排或"统一"其他章节
- 对外接口、错误码集、状态机的变化必须与 spec 中批准的 `modify`/`remove` 基线一一对应——promotion 不是引入未批准变更的后门

## 反例

```text
❌ 把 spec.md 原样 copy 到 docs/ar-specs/，保留 Open Questions 和过程笔记
❌ 修订了组件状态机，closeout 里写「已修订」但 docs/component-design.md 没动
❌ promotion 时"顺手"改了一个错误码名字（未经 spec modify 流程的变更走私）
❌ 只 promote design 不 promote spec，长期库里设计和规格断链
```
