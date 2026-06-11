---
name: devflow-clean-design
description: 当 DevFlow 的设计节点或设计评审需要判断设计是否简单、内聚、低耦合、接口契约清晰、抽象克制、边界稳定时使用。第三层代码内在质量的设计统筹 skill；不用于编码规范、测试有效性、领域约束、runtime routing 或写 progress/handoff。
---

# DevFlow Clean Design

## 总览

`devflow-clean-design` 是 DevFlow 第三层“代码内在质量”的设计统筹 skill。它回答：这份设计是否简单、清晰、边界稳定、接口契约可审查，并且值得长期持有。

本 skill 不是 runtime node，不写 `progress.md` / handoff，不产 review verdict，不替代 `devflow-component-design-review` 或 `devflow-ar-design-review`。它只提供设计质量约束，供设计 authoring 和设计 review 节点消费。

## 适用场景

适用：

- `devflow-component-design` 起草或修订组件设计。
- `devflow-ar-design` 起草或修订代码层设计。
- `devflow-component-design-review` / `devflow-ar-design-review` 判断设计质量。
- 设计中出现过度抽象、边界漂移、接口契约不清、设计选项空泛等问题。

不适用：

- 编码规范 / 语言工具链 → `devflow-clean-code` + 适用 coding-standards skill
- 测试有效性 → `devflow-test-review`
- 车载、前端、后端等领域约束 → 对应 domain-constraints skill
- runtime 下一步 → `devflow-router`

## 硬性门禁

- 不写 `Current Stage` 或 `Next Action Or Recommended Skill`。
- 不替 reviewer 给 verdict。
- 不替模块架构师或开发负责人拍板组件边界、接口契约或架构取舍。
- 不以“设计很干净”为理由跳过 spec、design review、TDD、test review、code review 或 completion gate。
- 不把语言级编码规范或领域约束写成本 skill 的默认规则。

## 对象契约

- Primary Object: clean design constraints
- Frontend Input Object: requirement、component design、AR design、design options、traceability、applicable domain constraints
- Backend Output Object: 设计质量约束清单、设计 review 增补判据
- Boundaries: 不写设计工件、不产 verdict、不做 runtime routing
- Invariants: 只处理通用设计质量；语言/领域规则由扩展 skills 提供

## 核心原则

### 1. 简单性优先

设计必须从当前 requirement 出发，寻找满足当前目标的最少结构。不要为了假想未来需求引入框架、插件层、注册表、策略体系或通用引擎。

Red flags:

- 当前只有一个真实用例，却设计通用框架。
- “以后可能需要”成为主要设计理由。
- 方案对比只是同一方案的不同措辞。

### 2. 抽象克制

抽象必须由真实重复、真实变化轴或稳定公共契约支撑。第三个真实用例出现前，重复通常比错误抽象更便宜。

Red flags:

- 单实现接口。
- 单子类继承层次。
- 只被调用一次的“可复用工具”。
- 为隐藏不清楚的需求而制造抽象。

### 3. 接口契约清晰

接口契约必须描述可观察行为，而不是只列函数名或字段名。

最小契约包括：

- 输入与前置条件。
- 输出与后置条件。
- 错误语义。
- 副作用。
- 并发/时序语义（若适用）。
- 兼容性与迁移策略（modify/remove 时）。

### 4. 高内聚低耦合

模块职责应能一句话说清。依赖方向应稳定，跨模块影响应显式。

Red flags:

- 一个模块有多个独立变化理由。
- 改一个局部行为必须改多个无关模块。
- 实现细节泄漏到公共接口。

### 5. 设计选项有质量

Design Options 必须比较真实可选方案，而不是形式化填表。

每个方案至少说明：

- 改动范围。
- 复杂度。
- 兼容性。
- 回滚成本。
- 长期维护影响。
- 为什么推荐或不推荐。

`Single obvious option` 只在确实没有合理替代方案时使用，并必须写明其它方案为什么不成立。

## 与扩展 skills 的关系

- `embedded-development` 可以给本 skill 增补通用嵌入式设计约束，例如内存、实时性、中断、资源和硬件/驱动边界。
- `automotive-development` 可以给本 skill 增补车载设计约束，例如 ASIL、SOA/MDC、DTC、SELinux 和整车生命周期。
- `c-coding-standards` / `cpp-coding-standards` 只在设计需要语言级接口、ABI、生命周期或工具链约束时提供补充。
- 扩展 skill 不改变本 skill 的非 canonical 地位。

## 反向理由化（Common Rationalizations）

| 话术 | 反驳 |
|---|---|
| 「先把扩展性留足」 | 扩展性来自清晰边界，不来自提前造框架 |
| 「抽象一下更优雅」 | 优雅不是工程理由；必须证明抽象减少的复杂度大于引入的复杂度 |
| 「接口细节实现时再定」 | 接口可观察行为是契约，必须在设计阶段可审查 |
| 「只有一个方案，没必要解释」 | 可以用 Single obvious option，但必须说明其它方案为什么不成立 |

## 验证清单

- [ ] 设计满足当前 requirement，没有为假想未来过度设计。
- [ ] 抽象有真实用例或稳定契约支撑。
- [ ] 接口契约写清输入、输出、错误、副作用和兼容性。
- [ ] 模块职责清晰，依赖方向可解释。
- [ ] Design Options 具有真实取舍。
- [ ] 适用领域约束已消费或明确 N/A。

## DevFlow 约定

本 skill 是第三层代码内在质量的设计统筹 skill。它不写 `progress.md`、handoff 或 review verdict，不改变 canonical runtime nodes。需要 runtime routing 时回 `devflow-router`。
