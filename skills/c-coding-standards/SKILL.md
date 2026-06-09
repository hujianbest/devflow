---
name: c-coding-standards
description: 当 DevFlow work item 涉及 C 语言代码、C 测试、C 工具链、MISRA C、指针/内存/宏/资源生命周期或 C 静态分析规则时使用。作为第三层代码内在质量的编码规范扩展；不用于车载领域约束、C++ 规范、运行时路由或写 progress/handoff。
---

# C Coding Standards

## 总览

`c-coding-standards` 是 DevFlow 第三层“代码内在质量”的 C 语言扩展。它定义 C 代码如何写得清晰、可靠、可审查，并为设计、实现、代码评审和完成门禁提供语言级约束。

本 skill 不替代 `devflow-code-review`，不写代码，不产 verdict，不写 `progress.md` / handoff，也不是 canonical runtime node。

## 适用场景

适用：

- work item 涉及 C 源码、头文件、C 单元测试或 C 构建 / 静态分析。
- `devflow-tdd-implementation` 需要 C 语言实现约束。
- `devflow-code-review` 需要 C 语言级 review rubric。
- `devflow-completion-gate` 需要核对 C 工具链、告警、静态分析和证据。

不适用：

- C++ 语言规则 → `cpp-coding-standards`
- 车载嵌入式领域约束 → `automotive-embedded-development`
- runtime 下一步 → `devflow-router`
- 测试有效性裁决 → `devflow-test-review`

## 硬性门禁

- 不把 C 规则写入 `Next Action Or Recommended Skill`。
- 不替 reviewer 给 verdict。
- 不替项目决定 MISRA C 子集；项目未声明时，只提出需确认项。
- 不把车载实时性、ASIL、SOA/MDC 等领域规则写在本 skill 内。
- C 代码若引入未解释的内存越界、未初始化访问、资源泄漏、宏副作用或未处理错误返回，不得作为“语言层 clean”交付。

## 对象契约

- Primary Object: C language quality constraints
- Frontend Input Object: C 源码 / 头文件 / 测试代码 / 构建命令 / 静态分析输出 / 项目编码规范
- Backend Output Object: C 语言约束清单、review 增补项、verification 增补项
- Boundaries: 不写代码、不改工件、不产 verdict、不做领域判断
- Invariants: C 与 C++ 分开管理；本 skill 只处理 C

## 方法原则

- **Pointer Discipline**: 指针所有权、生命周期、空指针语义、别名关系必须可审查。
- **Memory And Resource Lifecycle**: 分配/释放、打开/关闭、锁/解锁必须成对，失败路径同样成立。
- **Macro Restraint**: 宏只用于必要场景，避免多次求值、副作用、类型不透明和调试困难。
- **Header Hygiene**: 头文件暴露最小接口，include guard / forward declaration / 依赖方向清晰。
- **Error Return Discipline**: 每个可能失败的调用返回值必须处理或显式说明为什么安全忽略。
- **Static Analysis First**: MISRA C、CERT C 或项目规则的告警必须有修复、抑制或解释。

## 工作流叠加点

本 skill 可被以下节点叠加读取：

- `devflow-ar-design` / `devflow-component-design`：设计阶段声明 C 接口、错误码、资源生命周期和可测试边界。
- `devflow-tdd-implementation`：实现阶段约束 C 代码写法、测试 harness 和静态分析命令。
- `devflow-code-review`：评审阶段检查 C 语言风险。
- `devflow-completion-gate`：门禁阶段核对 C 构建、告警和静态分析证据。

## C Review 增补项

| 维度 | 检查点 |
|---|---|
| 指针 | NULL 语义、所有权、别名、越界、悬垂指针 |
| 内存 | 初始化、释放、失败路径、栈/堆边界 |
| 宏 | 多次求值、副作用、括号、类型安全、可调试性 |
| 头文件 | 最小暴露、循环依赖、include guard、extern 可见性 |
| 错误处理 | 返回码、errno/项目错误码、调用方恢复路径 |
| 静态分析 | MISRA C / CERT C / 编译告警的处理状态 |

## 反向理由化（Common Rationalizations）

| 话术 | 反驳 |
|---|---|
| 「这个指针调用链很短，不会为空」 | C 代码要把前置条件写清；边界输入必须防御或证明不可达 |
| 「宏这样写大家都懂」 | 宏副作用和多次求值很难审查；能用函数或 enum 就不要用复杂宏 |
| 「释放失败路径太啰嗦」 | C 的失败路径就是正确性；资源泄漏不是风格问题 |
| 「静态分析是历史问题」 | 历史问题也要分类；本次新增或触碰的告警必须解释 |

## 验证清单

- [ ] C 与 C++ 规则未混合。
- [ ] 指针、内存、资源生命周期已被设计 / 实现 / review 覆盖。
- [ ] 宏使用有明确必要性且无副作用风险。
- [ ] 头文件接口最小且依赖方向清晰。
- [ ] C 编译告警和静态分析输出已记录并解释。

## DevFlow 约定

本 skill 是第三层代码内在质量的编码规范扩展。它不写 `progress.md`、handoff 或 review verdict，不改变 canonical runtime nodes。需要 runtime routing 时回 `devflow-router`。
