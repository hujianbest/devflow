---
name: cpp-coding-standards
description: 当 DevFlow work item 涉及 C++ 代码、C++ 测试、RAII、对象生命周期、模板、异常策略、ABI、AUTOSAR C++ 或 C++ 静态分析规则时使用。作为第三层代码内在质量的编码规范扩展；不用于 C 规范、车载领域约束、运行时路由或写 progress/handoff。
---

# C++ Coding Standards

## 总览

`cpp-coding-standards` 是 DevFlow 第三层“代码内在质量”的 C++ 语言扩展。它定义 C++ 代码如何保持清晰、可靠、可维护，并为设计、实现、代码评审和完成门禁提供语言级约束。

本 skill 不替代 `devflow-code-review`，不写代码，不产 verdict，不写 `progress.md` / handoff，也不是 canonical runtime node。

## 适用场景

适用：

- work item 涉及 C++ 源码、头文件、模板、类层次、C++ 单元测试或 C++ 工具链。
- `devflow-tdd-implementation` 需要 C++ 实现约束。
- `devflow-code-review` 需要 C++ 语言级 review rubric。
- `devflow-completion-gate` 需要核对 C++ 构建、告警、静态分析和 ABI 证据。

不适用：

- C 语言规则 → `c-coding-standards`
- 车载嵌入式领域约束 → `automotive-embedded-development`
- runtime 下一步 → `devflow-router`
- 测试有效性裁决 → `devflow-test-review`

## 硬性门禁

- 不把 C++ 规则写入 `Next Action Or Recommended Skill`。
- 不替 reviewer 给 verdict。
- 不替项目决定 AUTOSAR C++、C++ Core Guidelines 或异常策略；项目未声明时，只提出需确认项。
- 不把车载实时性、ASIL、SOA/MDC 等领域规则写在本 skill 内。
- C++ 代码若引入未解释的对象生命周期错误、资源泄漏、异常安全破坏、ABI 破坏或过度模板抽象，不得作为“语言层 clean”交付。

## 对象契约

- Primary Object: C++ language quality constraints
- Frontend Input Object: C++ 源码 / 头文件 / 测试代码 / 构建命令 / 静态分析输出 / 项目编码规范
- Backend Output Object: C++ 语言约束清单、review 增补项、verification 增补项
- Boundaries: 不写代码、不改工件、不产 verdict、不做领域判断
- Invariants: C 与 C++ 分开管理；本 skill 只处理 C++

## 方法原则

- **RAII First**: 资源所有权优先用对象生命周期表达，避免裸 acquire/release 分散。
- **Lifetime Clarity**: 引用、指针、move 后对象、返回值生命周期必须可审查。
- **Abstraction Restraint**: 模板、继承、多态必须由真实变化轴支撑。
- **Exception Strategy Consistency**: 是否允许异常、如何传播错误、边界如何转换错误必须符合项目策略。
- **ABI Awareness**: 对外类布局、虚表、符号、inline / template 暴露需考虑兼容性。
- **Static Analysis First**: AUTOSAR C++、C++ Core Guidelines、CERT C++ 或项目规则的告警必须有修复、抑制或解释。

## 工作流叠加点

本 skill 可被以下节点叠加读取：

- `devflow-ar-design` / `devflow-component-design`：设计阶段声明类边界、错误语义、对象生命周期和 ABI 约束。
- `devflow-tdd-implementation`：实现阶段约束 C++ 代码写法、测试 harness 和静态分析命令。
- `devflow-code-review`：评审阶段检查 C++ 语言风险。
- `devflow-completion-gate`：门禁阶段核对 C++ 构建、告警和静态分析证据。

## C++ Review 增补项

| 维度 | 检查点 |
|---|---|
| 生命周期 | RAII、move/copy、引用悬垂、返回值生命周期 |
| 资源 | 智能指针选择、所有权转移、析构路径、失败路径 |
| 抽象 | 继承 vs 组合、模板复杂度、虚接口稳定性 |
| 错误 | 异常策略、错误码转换、noexcept、边界语义 |
| ABI | 对外类型布局、符号、inline/template 暴露、兼容策略 |
| 静态分析 | AUTOSAR C++ / Core Guidelines / 编译告警处理 |

## 反向理由化（Common Rationalizations）

| 话术 | 反驳 |
|---|---|
| 「这个裸指针只是借用，不用写清楚」 | 借用关系也必须可审查；生命周期不清就是缺陷 |
| 「模板抽象以后会复用」 | 第三个真实用例前不为假想未来引入模板复杂度 |
| 「异常不会跨出去」 | 异常策略必须由边界声明或项目规范支撑，不能靠口头假设 |
| 「ABI 变化没人依赖」 | 对外可观察行为都会被依赖；ABI/API 变化必须显式评估 |

## 验证清单

- [ ] C++ 与 C 规则未混合。
- [ ] RAII / 生命周期 / 所有权转移已被设计、实现或 review 覆盖。
- [ ] 模板、继承、多态有真实变化轴支撑。
- [ ] 错误和异常策略符合项目约定或已列为待确认。
- [ ] ABI / API 兼容性已按暴露面评估。
- [ ] C++ 编译告警和静态分析输出已记录并解释。

## DevFlow 约定

本 skill 是第三层代码内在质量的编码规范扩展。它不写 `progress.md`、handoff 或 review verdict，不改变 canonical runtime nodes。需要 runtime routing 时回 `devflow-router`。
