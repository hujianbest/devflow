# devflow Code Review Rubric

> 配套 `devflow-code-review/SKILL.md`。展开 8 维度评分细则与 rule IDs。

## 8 维度评分

| 维度 | 关键检查 |
|---|---|
| **CR1 Correctness** | 实现是否真正完成 AR 行为；`modify` / `remove` 是否符合 Existing Behavior / Baseline 的保留、批准破坏或删除语义；逻辑无 off-by-one / 边界遗漏 |
| **CR2 Design Conformance** | 实现是否遵循 AR 设计 + 组件设计；偏离需有理由且可追溯 |
| **CR3 SOA Boundary Conformance** | 不破坏 SOA 边界；不引入未解释跨组件依赖；不绕过组件接口 |
| **CR4 Resource & Lifecycle** | 资源、对象或状态生命周期符合设计；失败路径可审查 |
| **CR5 Concurrency & Timing** | 并发、时序或异步路径符合设计与适用领域约束 |
| **CR6 Error Handling & Defensive Design** | 输入校验；错误语义；降级路径；接口兼容 |
| **CR7 Coding Standard & Static Analysis** | 适用编码规范 skill；编译告警；静态分析 critical 项已闭环 |
| **CR8 Refactor Note & Architectural Health** | Refactor Note 完整；cleanup 守 Two Hats；未触发 escalation 边界 |

任一关键维度 < 6 不得 `通过`；适用编码规范 / 领域约束中标为 critical 的维度不得有未解释风险。

## Rule ID 列表

### Group CR1 - Correctness（正确性）

- `CR1.1` 实现完整覆盖 AR 行为
- `CR1.2` 边界条件处理正确
- `CR1.3` 死代码 / 不可达分支已清理或解释
- `CR1.4` `modify` / `remove` 的 baseline delta 已在实现中正确落地，未产生未批准的既有行为破坏

### Group CR2 - Design Conformance（设计一致性）

- `CR2.1` 实现遵循 ar-design-draft.md
- `CR2.2` 与 component-design.md 一致
- `CR2.3` 偏离设计的部分有显式理由 + 追溯锚点

### Group CR3 - SOA Boundary（SOA 边界）

- `CR3.1` 不绕过组件 SOA 接口
- `CR3.2` 不引入未声明的跨组件依赖
- `CR3.3` 接口实现的错误码 / 时序约束与组件级接口契约一致（项目已启用 `docs/interfaces.md` 时以该文件为准；未启用时以 `docs/component-design.md` 的 SOA 服务 / 接口章节为准）
- `CR3.4` 内部细节未通过公共符号泄漏

### Group CR4 - Resource & Lifecycle（资源与生命周期）

- `CR4.1` 资源 / 对象 / 状态生命周期符合 design
- `CR4.2` 获取与释放、初始化与清理路径配对
- `CR4.3` 异常 / 错误路径下无泄漏或未关闭资源
- `CR4.4` 大对象、缓存、外部资源使用有边界说明
- `CR4.5` 语言级生命周期细节交由适用编码规范 skill 检查

### Group CR5 - Concurrency & Timing（并发与时序）

- `CR5.1` 并发 / 异步 / 时序路径符合设计
- `CR5.2` 锁 / 临界区 / 事务边界遵循项目策略
- `CR5.3` 共享数据访问受保护，无竞态或未解释冲突
- `CR5.4` 适用领域的 timing / latency / deadline 约束有证据或 N/A 理由
- `CR5.5` 阻塞 / 非阻塞语义符合接口约定

### Group CR6 - Error Handling（错误处理）

- `CR6.1` 外部输入有校验；非法输入返回团队规定错误码
- `CR6.2` 错误码不被静默吞掉
- `CR6.3` 降级路径符合 component-design
- `CR6.4` 接口兼容性策略落地（参数变更、错误码扩展、协议语义变化）
- `CR6.5` 日志 / 诊断信息符合团队规范，不暴露敏感数据

### Group CR7 - Coding Standard & Static Analysis（编码规范与静态分析）

- `CR7.1` 符合适用编码规范 skill（命名、注释、格式、工具链规则）
- `CR7.2` 符合适用编码规范 skill 或项目声明的标准
- `CR7.3` 编译告警：critical 项已闭环
- `CR7.4` 静态分析报告：critical / blocker 项已修 / 解释 / 抑制（带理由）
- `CR7.5` 无适用编码规范明确禁止的用法
- `CR7.6` 命名符合项目或编码规范约定
- `CR7.7` 团队错误码 / 类型规范正确使用（按项目声明）
- `CR7.8` CMake / build 配置变更可追溯，无隐藏依赖或未声明链接项

### Group CR8 - Refactor Note & Health（重构记录与架构健康）

- `CR8.1` Refactor Note 完整：Hat Discipline / In-task Cleanups / Architectural Conformance / Documented Debt / Escalation Triggers / Static Analysis Evidence
- `CR8.2` In-task Cleanups 使用 Fowler vocabulary 命名
- `CR8.3` Hat Discipline 守住，GREEN 步无 cleanup
- `CR8.4` 触碰范围内可见 architectural smell（god-class / cyclic-dep / layering-violation / leaky-abstraction）已识别 / 分类
- `CR8.5` 未触发 escalation-bypass（CR8 critical）：跨 ≥3 模块的结构性重构 / 改 ADR / 改组件边界 / 引入设计未声明的新抽象层均不得在 task 内悄悄做掉
- `CR8.6` 触碰文件 Boy Scout：离开时 clean code 健康度未退化

## Severity 分级

- `critical`：阻塞 completion gate（核心逻辑错、未批准的既有行为破坏、适用编码规范 / 领域约束 critical 风险、边界破坏、escalation-bypass、未解释 critical 静态分析项）
- `important`：completion 前应修（边界遗漏、Refactor Note 字段缺、Boy Scout 退化、smell 未分类）
- `minor`：建议改进（命名、注释、风格）

## 项目检查清单补充

评审时优先核对 `docs/devflow-internal-quality.md`、适用编码规范 skill 和适用领域约束 skill。若项目显式启用旧团队代码检视清单，可参考 `team-code-review-checklist.md`；该文件不是 DevFlow Core 默认判据。

| 类别 | 必查项 |
|---|---|
| Clean Code | 命名清晰、函数长度合理（建议 < 50 行）、无明显重复、嵌套不过深（建议 < 3 层）、注释必要且准确 |
| 错误处理 | 所有可能失败操作有处理；错误码使用正确；错误日志含上下文；异常路径无资源泄漏 |
| 类型安全 | 项目特定类型使用正确；类型转换安全；语言级生命周期风险按适用编码规范检查 |
| 边界情况 | 空值、零值、最大 / 最小、越界和异常输入均有处理 |
| 资源管理 | 资源获取 / 释放配对；异常或错误路径无泄漏；语言级细节按适用编码规范检查 |
| 架构设计 | 类职责单一；接口清晰；依赖合理；不破坏开闭原则和 SOA 边界 |
| 性能安全 | 避免不必要拷贝；性能热点有解释；缓冲区溢出、竞态、敏感信息泄露风险已审 |
| 测试代码角度 | 测试命名、fixture / mock 使用、边界 / 异常覆盖与 `devflow-test-review` 结论一致；发现明显测试问题时回 `devflow-test-review` / `devflow-tdd-implementation` |

常见问题模式需要重点检查：只断言返回码、魔法数字、重复测试代码、缺边界值测试，以及适用编码规范 / 领域约束声明的语言或领域风险。

## Classification 分类

- `USER-INPUT`：实现偏离设计且涉及业务取舍 → 上抛开发负责人
- `LLM-FIXABLE`：代码结构 / 错误处理 / 命名 / 边界 / 防御性检查 / Refactor Note 字段补全 / in-task 范围 smell → 由 `devflow-tdd-implementation` 回修
- `TEAM-EXPERT`：组件边界冲突 / 接口冲突 / 领域架构或语言深水区判断 → 上抛模块架构师 / 对应领域专家

## Verdict 决策

| 评分 / findings 状态 | verdict |
|---|---|
| 8 维度均 ≥ 6、CR8 主维度 ≥ 8 / 子维度 ≥ 6、无未解释 critical 静态分析项或扩展约束 critical 项 | `通过` |
| findings 可 1-2 轮定向修订 | `需修改` |
| 核心逻辑错误 / 适用扩展约束 critical 风险 / 边界破坏可在 task 内回修 | `阻塞`（内容） |
| 实质修改 ADR / 组件边界 / SOA 接口 / 跨 ≥3 模块结构性变更 / escalation-bypass / 上游证据冲突 | `阻塞`（workflow） + `reroute_via_router=true` |
