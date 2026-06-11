---
name: devflow-review
description: 在规格、设计、测试或代码需要独立评审时使用：阶段产物完成后的把关、人要求 review、或对既有产物做专项检查时。评审必须由作者之外的独立上下文执行，产出 findings 与 verdict。
---

# DevFlow 评审

## 总览

评审是 human-on-the-loop 的支点：AI 生产，独立评审暴露问题，人做最终把关。两条不变量：

1. **作者不自审。** 写产物的会话/agent 不能给自己出 verdict。评审由独立 subagent 或新会话执行——它没有作者的写作记忆，只能依赖产物本身，这正是"可冷读"的检验方式。
2. **评审者不动手修。** 评审产出 findings 和 verdict，修改由作者根据 findings 执行。裁判不下场。

评审不是流程仪式。一次好的评审 = 带着「这东西哪里会骗我」的怀疑去读：规格会在哪里被两种人读出两种意思？测试会放过哪种错误实现？代码哪里在对读者撒谎？

## 工作流

### 1. 确定目标与 rubric

| 评审目标 | Rubric | 关注核心 |
|---|---|---|
| spec.md | `references/spec-review-rubric.md` | 可测试性、变更风险显式、无走私的实现细节 |
| design.md（及 component-design-draft.md，如适用） | `references/design-review-rubric.md` | 契约完整、复杂度有理由、测试设计覆盖、追溯一致 |
| 测试 | `references/test-review-rubric.md` | 断言强度、覆盖映射、mock 边界、RED 证据 |
| 代码 | `references/code-review-rubric.md` | 正确性、与设计一致、整洁标准、语言/领域规则 |

### 2. 以独立上下文执行

派发 subagent（或开新会话）执行评审，输入只给：被评审产物、它的上游工件（评审设计给 spec，评审代码给 design + diff）、对应 rubric、适用的 coding-standards / 领域技能。**不给**作者的推理过程和聊天历史。

### 3. 产出 findings 与 verdict

每条 finding：`位置 + 问题 + 为什么是问题 + 严重级`。

| 严重级 | 含义 | 例 |
|---|---|---|
| `critical` | 不修不能继续：会导致做错事、留 bug 或不可审 | 验收标准不可测试；测试断言放过 mutation；错误路径资源泄漏 |
| `important` | 完成前应修 | 边界用例缺失；函数职责混杂；命名误导 |
| `minor` | 建议改进 | 措辞、风格微调 |

verdict 三选一：

- `通过`：无 critical/important，或仅剩已被人接受的 minor
- `需修改`：findings 可定向修复，修复后复审
- `重新设计`：问题出在上游（规格漏洞、设计方向错误），打回对应阶段

评审记录写入 `features/<id>/reviews/<目标>-review-<日期>.md`：评审对象（含版本/commit）、findings 列表、verdict、抽查记录（如做了 mutation 自检，写明改了哪行、哪个测试红了）。

### 4. 人做最终把关

把 findings 与 verdict 呈给人。人可以否决评审意见（接受某条债务、放宽某个阈值）——记录在评审文件里即可。**人没有确认前，verdict 不算闭环。**

## 评审者纪律

- 按 rubric 逐项过，不凭整体印象打分；rubric 之外发现的问题照样列出
- 每条 critical/important finding 给出**具体位置**和**可执行的修复方向**，不写"质量有待提高"
- 抽查重于通读：测试评审必做 2-3 个关键用例的 mutation 自检；代码评审优先读错误路径与资源路径——那是问题密度最高的地方
- 不确定的判断标注"待人裁决"，不假装确定
- 发现产物间漂移（代码与 design 不符、测试与 spec 不符）→ 一律 critical：要么改产物，要么改工件，不允许默默不一致

## 风险信号

- 作者会话自己宣布"评审通过"
- findings 全是 minor 措辞建议，对错误路径、断言强度、契约完整性只字不提（评审走过场）
- verdict 为"需修改"但 findings 没有一条具体到位置
- 评审者直接动手改了代码
- 同一产物三轮评审仍在打回 → 停止循环，升级人裁决方向问题

## 支撑参考

| 文件 | 用途 |
|---|---|
| `references/spec-review-rubric.md` | 规格评审检查项 |
| `references/design-review-rubric.md` | 设计评审检查项 |
| `references/test-review-rubric.md` | 测试评审检查项 |
| `references/code-review-rubric.md` | 代码评审检查项 |
