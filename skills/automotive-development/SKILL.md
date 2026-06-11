---
name: automotive-development
description: 当 DevFlow work item 属于车载软件开发，涉及 ASIL、功能安全、车载 SOA/MDC、DTC/诊断、整车启动/休眠/唤醒、SELinux、车载接口兼容或跨 ECU/域控协同时使用。作为第三层代码内在质量的领域约束扩展；不用于通用嵌入式风险、C/C++ 语言规范、运行时路由或写 progress/handoff。
---

# Automotive Development

## 总览

`automotive-development` 是 DevFlow 第三层“代码内在质量”的车载领域约束扩展。它只承载车载专属约束：功能安全、ASIL、车载 SOA/MDC、DTC/诊断、整车生命周期、SELinux、跨 ECU / 域控协同等。

通用嵌入式约束由 `embedded-development` 承载；C / C++ 语言规范由 `c-coding-standards` / `cpp-coding-standards` 承载。本 skill 不产 review verdict，不写 `progress.md` / handoff，也不是 canonical runtime node。

## 适用场景

适用：

- work item 属于车载软件、ECU、域控、车载服务或整车平台。
- 需求涉及 ASIL / safety goal / fail-safe / fail-operational / DTC / diagnostic / vehicle state。
- 需求涉及车载 SOA 服务、MDC 场景、启动退出、休眠唤醒、SELinux、跨 ECU 或跨域协同。
- review / gate 需要车载领域证据矩阵。

不适用：

- 通用嵌入式内存、实时性、中断、硬件资源约束 → `embedded-development`
- C 语言规范 → `c-coding-standards`
- C++ 语言规范 → `cpp-coding-standards`
- runtime 下一步 → `devflow-router`

## 硬性门禁

- 不把本 skill 写入 `Next Action Or Recommended Skill`。
- 不替功能安全负责人、模块架构师、系统工程师或开发负责人拍板 ASIL、safety goal 或车载接口契约。
- 不重复通用嵌入式规则；通用嵌入式风险交给 `embedded-development`。
- 不重复 C / C++ 语言规则；语言风险交给对应 coding-standards skill。
- 车载约束必须前置到规格和设计，不允许只在 code review 阶段才发现。

## 对象契约

- Primary Object: automotive domain constraints
- Frontend Input Object: work item 规格、设计、component docs、runtime behavior、接口/依赖资产、测试证据、问题报告
- Backend Output Object: 车载领域约束清单、全流程增补检查点、review/gate 增补项
- Boundaries: 不写代码、不改工件、不产 verdict、不做语言规范或通用嵌入式规范
- Invariants: 本 skill 提供车载领域约束，runtime routing 仍由 `devflow-router` 决定

## 领域维度

| 维度 | 关注点 |
|---|---|
| Functional Safety / ASIL | safety goal、ASIL 等级、fail-safe、降级策略、确认 owner |
| Vehicle Lifecycle | 启动、退出、休眠、唤醒、电源状态、网络状态 |
| Automotive SOA / MDC | 服务契约、消费者、错误码、版本策略、MDC 五类场景 |
| Diagnostics / DTC | DTC、日志、故障注入、可观测性、恢复路径 |
| SELinux / Security Policy | 主客体、标签、allow/neverallow、最小权限 |
| Cross-ECU / Domain Coordination | 下游 owner、跨 ECU / 域控影响、协调状态 |

## 全流程投射

### `devflow-specify`

- 捕获 ASIL / safety、车载生命周期、SOA/MDC、DTC/诊断、SELinux、跨 ECU 协调等约束。
- 缺 safety / ASIL / 接口消费者 / 诊断阈值时标 USER-INPUT / TEAM-EXPERT。
- 车载接口变更必须进入 Component Impact Assessment。

### `devflow-spec-review`

- 检查车载 QAS 是否有可判定阈值。
- 检查 ASIL、SOA/MDC、DTC、SELinux、整车生命周期是否显式判断适用或 N/A。
- 检查车载决策是否有 owner，不允许 agent 自行降级。

### `devflow-component-design`

- 组件职责、车载 SOA 服务、依赖方向、状态机和运行机制必须匹配车载架构约束。
- 启用车载约束时，应覆盖 MDC 场景：并发、启动退出、休眠唤醒、可靠性、SELinux。
- 跨组件 / 跨 ECU / 跨域控影响必须列出 owner 和协调状态。

### `devflow-component-design-review`

- 检查组件边界和车载接口契约是否足以支持下游 AR 设计。
- 检查 ASIL / SOA / MDC / DTC / SELinux 约束是否可审查。

### `devflow-ar-design`

- 功能点分解必须覆盖适用车载场景。
- 测试设计章节应包含车载领域风险用例或明确 N/A 理由。
- 实现设计必须消费组件级车载约束，不得重新定义车载接口。

### `devflow-ar-design-review`

- 检查 AR 设计是否越过组件 / SOA / 车载接口边界。
- 检查测试设计是否覆盖车载领域风险。
- 检查 ASIL、MDC、DTC、SELinux、跨 ECU 影响是否可追溯。

### `devflow-tdd-implementation`

- Implementer Context Pack 必须包含适用车载约束摘要。
- 实现不得私自改变车载接口、DTC、ASIL 相关行为、MDC 场景或跨 ECU 契约。

### `devflow-test-review`

- 车载领域风险用例是否实际落地，而不是只在测试设计中列名。
- HIL / SIL / simulation / integration 替代证据是否足以支撑车载约束。
- mock / stub 是否没有掩盖车载接口和整车状态边界。

### `devflow-code-review`

- 代码是否遵守车载架构边界和接口契约。
- 是否引入未解释的车载生命周期、诊断、SELinux 或 SOA/MDC 风险。
- 通用嵌入式和 C/C++ 语言级规则由对应 skills 判断。

### `devflow-completion-gate`

- 车载领域证据矩阵是否齐全。
- 未解释的 ASIL / SOA / MDC / DTC / SELinux critical 风险是否为零。
- 车载约束相关 follow-up 是否被记录为可接受债务或阻塞项。

### `devflow-finalize`

- 长期资产是否同步车载领域约束变化。
- `docs/component-design.md`、`docs/interfaces.md`、`docs/dependencies.md`、`docs/runtime-behavior.md` 是否按项目启用状态同步。
- closeout report 是否列出车载领域风险审计结果。

### `devflow-problem-fix`

- reproduction 是否记录车载运行环境、版本、配置、日志和稳定性。
- root cause 是否分类到车载领域维度。
- fix boundary 是否明确不扩散到未批准的车载接口、诊断、安全或跨 ECU 变更。

## 反向理由化（Common Rationalizations）

| 话术 | 反驳 |
|---|---|
| 「ASIL 不确定但功能很小」 | safety 适用性由团队角色确认，agent 不自行降级 |
| 「只是改一个错误码，下游应该没影响」 | 车载接口可观察语义变化必须列出消费者和兼容策略 |
| 「MDC 场景后面再补」 | 车载场景必须前置到设计，否则实现后才发现通常太晚 |
| 「SELinux 不会变」 | 不变也需要依据；涉及权限访问时必须写明主体、客体和规则基线 |
| 「诊断日志够了，不需要 DTC」 | DTC / 诊断策略属于车载领域决策，缺失时上抛 owner |

## 验证清单

- [ ] 已明确本 work item 是否启用车载领域约束。
- [ ] 规格阶段已捕获适用 ASIL / SOA / MDC / DTC / SELinux / lifecycle 约束。
- [ ] 设计阶段已消费车载约束且未重定义未授权车载边界。
- [ ] TDD evidence 覆盖车载领域风险或提供明确 N/A 理由。
- [ ] test-review / code-review / completion-gate 均消费车载约束。
- [ ] finalize 同步长期资产时保留车载约束变化。

## DevFlow 约定

本 skill 是第三层代码内在质量的领域约束扩展。它不写 `progress.md`、handoff 或 review verdict，不改变 canonical runtime nodes。需要 runtime routing 时回 `devflow-router`。
