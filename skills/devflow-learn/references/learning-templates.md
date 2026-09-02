# Learning 模板

替换所有占位符。没有内容的可选字段或章节直接删除，不得保留 `TBD`、尖括号占位符
或空列表。

frontmatter 数组统一使用 block 形式。标量包含 `: `、` #`，或以 `` ` ``、`[`、`*`、
`&`、`!`、`|`、`>`、`%`、`@`、`?` 等 YAML 指示符开头时，使用双引号包裹。

## 问题解决

```markdown
---
schemaVersion: "1.1"
documentType: devflow-learning
learningId: component-problem-solution-topic
learningType: problem-solution
component: component-id
componentRoot: path/to/component
status: active
sensitivity: internal
capturedAt: YYYY-MM-DD
lastVerifiedAt: YYYY-MM-DD
sourceChanges:
  - AR001-topic
sourceArchives:
  - path/to/component/specs/archive/YYYY-MM-DD-AR001-topic
tags:
  - topic
canonicalRefs:
  - SPEC-FR-001
relatedLearnings:
  - related-learning-id
---

# 清晰的问题标题

## 问题

用一到两段说明可观察问题和影响。

## 症状

- 只保留识别复发所需的最小错误签名或行为。
<!-- claim: CLM-001; kind: historical; evidence: EV-001 -->

## 根因

说明完整因果链，区分故障发生位置和无效状态产生的原因。
<!-- claim: CLM-002; kind: historical; evidence: EV-002 -->

## 无效尝试

- 写明有证据的失败方案及其失败原因。

## 已验证方案

说明真正解决问题的修复或做法。只有代码片段比路径和符号引用提供更多信息时才保留，
并控制在必要范围内。
<!-- claim: CLM-003; kind: guidance; evidence: EV-002,EV-003 -->

## 生效原理

说明方案如何消除根因。

## 适用范围

- 适用于：
- 不适用于：

## 预防

- 写明防止复发的回归测试、不变量、设计检查或流程约束。
<!-- claim: CLM-004; kind: current; evidence: EV-003 -->

## 证据

- EV-001 | archive | `path/to/component/specs/archive/YYYY-MM-DD-AR001-topic/tasks.md::## 症状`
- EV-002 | archive | `path/to/component/specs/archive/YYYY-MM-DD-AR001-topic/tasks.md::## 根因`
- EV-003 | current-test | `path/to/component/tests/file_test.cpp::test_regression_case`

## 相关 learning

- 无。
```

## 设计决策

```markdown
---
schemaVersion: "1.1"
documentType: devflow-learning
learningId: component-design-decision-topic
learningType: design-decision
component: component-id
componentRoot: path/to/component
status: active
sensitivity: internal
capturedAt: YYYY-MM-DD
lastVerifiedAt: YYYY-MM-DD
sourceChanges:
  - AR001-topic
sourceArchives:
  - path/to/component/specs/archive/YYYY-MM-DD-AR001-topic
tags:
  - topic
canonicalRefs:
  - DEC-001
relatedLearnings:
  - related-learning-id
---

# 清晰的决策标题

## 背景与约束

说明为什么必须做出该决策。
<!-- claim: CLM-001; kind: historical; evidence: EV-001 -->

## 决策

说明选定方案，不复制完整 canonical design。
<!-- claim: CLM-002; kind: guidance; evidence: EV-001,EV-002 -->

## 备选方案

- 备选方案：在既定约束下被否决的原因。

## 理由与后果

说明取舍，包括选定方案主动接受的成本。
<!-- claim: CLM-003; kind: historical; evidence: EV-001 -->

## 适用范围

- 以下情况可复用：
- 以下情况应重新评估：

## 证据

- EV-001 | archive | `path/to/component/specs/archive/YYYY-MM-DD-AR001-topic/delta-design.md::DEC-001`
- EV-002 | current-canonical | `path/to/component/specs/design.md::DEC-001`

## 相关 learning

- 无。
```

## 工程实践

```markdown
---
schemaVersion: "1.1"
documentType: devflow-learning
learningId: component-engineering-practice-topic
learningType: engineering-practice
component: component-id
componentRoot: path/to/component
status: active
sensitivity: internal
capturedAt: YYYY-MM-DD
lastVerifiedAt: YYYY-MM-DD
sourceChanges:
  - AR001-topic
sourceArchives:
  - path/to/component/specs/archive/YYYY-MM-DD-AR001-topic
tags:
  - topic
relatedLearnings:
  - related-learning-id
---

# 清晰的实践标题

## 触发信号

说明这条实践解决的重复摩擦或失败。
<!-- claim: CLM-001; kind: historical; evidence: EV-001 -->

## 做法

写明具体动作、检查或流程。
<!-- claim: CLM-002; kind: guidance; evidence: EV-001,EV-002 -->

## 原因

说明它防止的失败，以及支持该做法的证据。
<!-- claim: CLM-003; kind: current; evidence: EV-002 -->

## 示例

有帮助时用仓库相对路径或命令给出简短示例。

## 适用范围

- 适用于：
- 不适用于：

## 证据

- EV-001 | archive | `path/to/component/specs/archive/YYYY-MM-DD-AR001-topic/reviews/r3-review.md::Finding`
- EV-002 | current-test | `path/to/component/tests/test_workflow.py::test_guard`

## 相关 learning

- 无。
```

## 知识库 README

只在第一次使用知识库时创建：

```markdown
# DevFlow Learnings

本目录保存从已完成 DevFlow change 中提炼的可复用经验。

- `problem-solutions/`：已验证的根因、解决方案和预防措施；
- `design-decisions/`：可复用的设计选择及其适用边界；
- `engineering-practices/`：测试、工具和工作流实践。

这些文档只提供参考。当前 canonical spec/design、代码和测试优先。检索 active learning
时可使用 `component`、`componentRoot`、`learningType`、`tags`、错误签名或
`canonicalRefs`。stale 和 superseded 条目只用于了解历史，不是当前指导。
```
