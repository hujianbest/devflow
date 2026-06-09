---
name: automotive-embedded-development
description: 当 DevFlow work item 属于车载嵌入式开发，涉及 ASIL、实时性、资源预算、SOA/MDC、启动退出、休眠唤醒、可靠性、车载证据或跨组件车载架构约束时使用。作为第三层代码内在质量的领域约束扩展；不用于 C/C++ 语言规范、运行时路由或写 progress/handoff。
---

# Automotive Embedded Development

## 总览

`automotive-embedded-development` 是 DevFlow 第三层“代码内在质量”的车载嵌入式领域约束扩展。它把车载嵌入式的领域质量要求投射到 DevFlow 全流程：规格、设计、TDD 实现、测试评审、代码评审、完成门禁、收尾和问题修复。

本 skill 不替代 `c-coding-standards` / `cpp-coding-standards`，不产 review verdict，不写 `progress.md` / handoff，也不是 canonical runtime node。

## 适用场景

适用：

- work item 属于车载嵌入式组件、服务、软件单元或 ECU / 域控相关实现。
- 需求涉及 ASIL、实时性、启动退出、休眠唤醒、可靠性、SELinux、MDC、SOA 服务、资源预算或跨组件协调。
- review / gate 需要车载领域证据矩阵。
- DTS / hotfix 根因可能涉及车载运行环境、资源、时序或接口契约。

不适用：

- 纯 C 语言规范 → `c-coding-standards`
- 纯 C++ 语言规范 → `cpp-coding-standards`
- runtime 下一步 → `devflow-router`
- 产品是否要做、优先级或验收阈值决策 → 团队角色

## 硬性门禁

- 不把本 skill 写入 `Next Action Or Recommended Skill`。
- 不替模块架构师、功能安全负责人、开发负责人拍板 ASIL、接口契约或资源预算。
- 不重复 C / C++ 语言规则；语言风险交给对应 coding-standards skill。
- 领域约束必须覆盖全流程，不允许只在 code review 阶段才发现。
- 涉及安全、实时性、资源预算或跨组件接口时，必须在规格/设计阶段前置暴露，不得等实现后补解释。

## 对象契约

- Primary Object: automotive embedded domain constraints
- Frontend Input Object: work item 规格、设计、component docs、runtime behavior、接口/依赖资产、测试证据、问题报告
- Backend Output Object: 领域约束清单、全流程增补检查点、review/gate 增补项
- Boundaries: 不写代码、不改工件、不产 verdict、不做语言规范
- Invariants: 本 skill 提供领域约束，runtime routing 仍由 `devflow-router` 决定

## 领域维度

| 维度 | 关注点 |
|---|---|
| Safety / ASIL | safety goal、ASIL 等级、降级策略、故障可诊断性 |
| Real-time | 时延预算、周期任务、超时、阻塞调用、调度影响 |
| Resource Budget | CPU、RAM、ROM、句柄、线程、队列、带宽、存储 |
| SOA / Interface | 服务契约、错误码、兼容性、消费者影响、版本策略 |
| MDC Scenarios | 并发、启动退出、休眠唤醒、可靠性、SELinux |
| Diagnostics | 日志、DTC、故障注入、可观测性、恢复路径 |
| Cross-Component | 下游 owner、协调状态、依赖方向、变更传播 |

## 全流程投射

### `devflow-specify`

规格阶段必须捕获：

- ASIL / safety 相关约束是否适用。
- 实时性、资源预算和可靠性是否有可判定阈值。
- SOA / 接口 / 错误码 / 消费者影响是否进入 Component Impact Assessment。
- 需要模块架构师或功能安全负责人确认的 USER-INPUT / TEAM-EXPERT 问题。

### `devflow-spec-review`

规格评审增补：

- NFR 是否包含可判定的车载 QAS 阈值。
- 涉及接口时是否给出 provider / consumer / operation / error semantics / compatibility。
- ASIL、实时性、资源预算、MDC 场景是否被显式判断为适用或不适用。

### `devflow-component-design`

组件设计增补：

- 组件职责、SOA 服务、依赖方向、状态机和运行机制是否匹配车载架构约束。
- MDC 五类场景是否有设计说明：并发、启动退出、休眠唤醒、可靠性、SELinux。
- 资源预算是否有估算和监测方案。
- 跨组件影响是否列出 owner 和协调状态。

### `devflow-component-design-review`

组件设计评审增补：

- 组件边界和接口契约是否足以支持下游 AR 设计。
- 实时路径是否避免未解释的阻塞或不可界定耗时。
- 资源预算、错误处理、降级策略是否可审查。

### `devflow-ar-design`

AR 设计增补：

- 功能点分解是否覆盖车载场景和约束。
- 测试设计章节是否包含领域风险用例或明确 N/A 理由。
- 实现设计是否消费组件级车载约束，而不是重新定义组件边界。

### `devflow-ar-design-review`

AR 设计评审增补：

- AR 设计是否越过组件 / SOA 边界。
- 测试设计是否覆盖相关领域风险。
- MDC、资源、实时性和安全相关约束是否可追溯。

### `devflow-tdd-implementation`

TDD 实现增补：

- Implementer Context Pack 必须包含适用的车载约束摘要。
- 测试与 evidence path 应覆盖设计中声明的领域风险。
- 实现不得私自改变接口、时序、资源预算或跨组件契约。

### `devflow-test-review`

测试评审增补：

- 领域风险用例是否实际落地，而不是只在测试设计中列名。
- 实时性、资源、可靠性、故障恢复等证据是否存在或有 N/A 理由。
- mock / stub / simulation 是否没有破坏 SOA 或车载运行边界。

### `devflow-code-review`

代码评审增补：

- 代码是否遵守车载架构边界和接口契约。
- 是否引入未解释的阻塞、资源增长、可靠性退化或跨组件依赖。
- 语言级 C/C++ 规则由 coding-standards skills 判断；本节点只判断车载领域风险。

### `devflow-completion-gate`

完成门禁增补：

- 领域证据矩阵是否齐全。
- 未解释的 ASIL / realtime / resource / SOA / MDC critical 风险是否为零。
- 领域约束相关的 follow-up 是否被记录为可接受债务或阻塞项。

### `devflow-finalize`

收尾增补：

- 长期资产是否同步车载领域约束变化。
- `docs/component-design.md`、`docs/interfaces.md`、`docs/dependencies.md`、`docs/runtime-behavior.md` 是否按项目启用状态同步。
- closeout report 是否列出领域风险审计结果。

### `devflow-problem-fix`

问题修复增补：

- reproduction 是否记录车载运行环境、版本、配置、日志和稳定性。
- root cause 是否分类到领域维度。
- fix boundary 是否明确不扩散到未批准的接口、资源预算或架构变更。

## 反向理由化（Common Rationalizations）

| 话术 | 反驳 |
|---|---|
| 「这是实现细节，车载约束 code review 再看」 | 领域约束必须前置到规格和设计；实现后才发现通常已经太晚 |
| 「只是改一个错误码，下游应该没影响」 | SOA / 接口可观察语义变化必须列出消费者和兼容策略 |
| 「实时性没有明确指标，就先不写」 | 缺阈值是 USER-INPUT / TEAM-EXPERT，不是 N/A |
| 「ASIL 不确定但功能很小」 | safety 适用性由团队角色确认，agent 不自行降级 |
| 「测试环境没法测资源，就跳过」 | 缺真实测试也要有替代证据、仿真或明确阻塞 |

## 验证清单

- [ ] 已明确本 work item 是否启用车载嵌入式领域约束。
- [ ] 规格阶段已捕获适用的 ASIL / realtime / resource / SOA / MDC 约束。
- [ ] 设计阶段已消费领域约束且未重定义未授权组件边界。
- [ ] TDD evidence 覆盖领域风险或提供明确 N/A 理由。
- [ ] test-review / code-review / completion-gate 均消费领域约束。
- [ ] finalize 同步长期资产时保留领域约束变化。

## DevFlow 约定

本 skill 是第三层代码内在质量的领域约束扩展。它不写 `progress.md`、handoff 或 review verdict，不改变 canonical runtime nodes。需要 runtime routing 时回 `devflow-router`。
