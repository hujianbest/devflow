---
name: embedded-development
description: 当 DevFlow work item 属于通用嵌入式开发，涉及内存/资源约束、中断上下文、实时性、硬件/驱动交互、静态/动态证据、ABI/API 兼容或嵌入式测试证据时使用。作为第三层代码内在质量的领域约束扩展；不用于车载专属 ASIL/SOA/MDC 约束、C/C++ 语言规范、运行时路由或写 progress/handoff。
---

# Embedded Development

## 总览

`embedded-development` 是 DevFlow 第三层“代码内在质量”的通用嵌入式领域约束扩展。它继承旧 DevFlow skills 中分散的通用嵌入式风险内容，并把这些约束投射到规格、设计、TDD 实现、测试评审、代码评审、完成门禁、收尾和问题修复。

本 skill 不替代 `c-coding-standards` / `cpp-coding-standards`，不包含车载专属 ASIL、SOA/MDC、DTC 或整车生命周期约束，不产 review verdict，不写 `progress.md` / handoff，也不是 canonical runtime node。

## 适用场景

适用：

- work item 属于嵌入式组件、固件、驱动、HAL、RTOS task、中断处理、资源受限服务或硬件邻近模块。
- 需求涉及内存预算、资源生命周期、中断上下文、实时性、硬件寄存器、DMA、句柄、缓冲区、跨平台 ABI/API 或嵌入式测试证据。
- review / gate 需要嵌入式风险矩阵。
- DTS / hotfix 根因可能涉及资源、时序、中断、硬件/驱动交互或目标平台差异。

不适用：

- 纯 C 语言规范 → `c-coding-standards`
- 纯 C++ 语言规范 → `cpp-coding-standards`
- 车载专属约束（ASIL、整车 SOA/MDC、DTC、车载启动/休眠等）→ `automotive-development`
- runtime 下一步 → `devflow-router`

## 硬性门禁

- 不把本 skill 写入 `Next Action Or Recommended Skill`。
- 不替模块架构师、系统工程师或平台负责人拍板资源预算、实时性阈值或硬件接口契约。
- 不重复 C / C++ 语言规则；语言风险交给对应 coding-standards skill。
- 不承载车载专属流程；车载约束交给 `automotive-development`。
- 嵌入式约束必须前置到规格和设计，不允许只在 code review 阶段才发现。

## 对象契约

- Primary Object: embedded domain constraints
- Frontend Input Object: work item 规格、设计、component docs、runtime behavior、测试证据、平台/硬件约束、问题报告
- Backend Output Object: 嵌入式约束清单、全流程增补检查点、review/gate 增补项
- Boundaries: 不写代码、不改工件、不产 verdict、不做语言规范
- Invariants: 本 skill 提供领域约束，runtime routing 仍由 `devflow-router` 决定

## 领域维度

| 维度 | 关注点 |
|---|---|
| Memory | 动态分配、栈对象大小、内存池、对齐、buffer 长度与所有权 |
| Interrupt / Concurrency | 中断上下文、锁顺序、原子操作、volatile、barrier、临界区长度 |
| Real-time | deadline、latency、调度优先级、关键路径阻塞、日志 / IO 影响 |
| Resource Lifecycle | 句柄、文件、DMA、定时器、线程、队列、缓冲区的创建 / 销毁 |
| Error Handling | 外部输入校验、错误码传播、降级路径、部分初始化回滚 |
| ABI / API Compatibility | 公共接口签名、数据结构布局、编译条件、配置项、跨平台兼容 |
| Evidence | build、unit、integration/simulation、static-analysis、target 或仿真证据 |

## 全流程投射

### `devflow-specify`

- 捕获内存、资源、实时性、中断/并发、平台约束等 NFR。
- NFR 必须写成可判定 QAS；缺阈值时标 USER-INPUT / TEAM-EXPERT。
- 目标平台、硬件、RTOS、编译条件或 ABI 限制写入 Constraint rows。

### `devflow-spec-review`

- 检查嵌入式 NFR 是否有阈值和环境条件。
- 检查中断上下文 / 实时路径 / 资源约束是否被明确判断适用或 N/A。
- 检查约束是否有来源锚点，而不是模型猜测。

### `devflow-component-design`

- 组件设计必须说明资源模型、并发模型、错误处理、初始化/关闭和平台边界。
- 接口契约需说明 buffer 所有权、长度、错误码、阻塞/非阻塞语义和兼容策略。
- 需要目标平台或硬件约束时，列出来源和 owner。

### `devflow-component-design-review`

- 审查资源生命周期、并发/中断、实时性、错误处理、ABI/API 兼容是否足以被 AR 设计消费。
- 缺领域 owner 或阈值时标 TEAM-EXPERT / USER-INPUT。

### `devflow-ar-design`

- AR 设计消费组件级嵌入式约束，不重新定义组件边界。
- 测试设计包含适用风险覆盖矩阵，或明确 N/A 理由。
- 设计选项比较资源、时延、回滚、平台差异和可验证性。

### `devflow-ar-design-review`

- 检查适用风险覆盖矩阵是否完整。
- 检查错误路径、资源路径、中断/并发路径和实时路径是否可追溯。

### `devflow-tdd-implementation`

- Implementer Context Pack 必须包含适用嵌入式约束摘要。
- RED / GREEN / REFACTOR evidence 应覆盖适用的资源、实时性、并发和错误路径。
- 不得用 sleep、重试或跳过静态分析掩盖嵌入式风险。

### `devflow-test-review`

- 领域风险用例是否实际落地，而不是只在测试设计中列名。
- 仿真、集成、target 或静态分析证据是否支持 completion claim。
- mock / stub / simulation 是否没有掩盖硬件/平台边界。

### `devflow-code-review`

- 按本 skill 的维度检查嵌入式风险。
- C / C++ 语言细节由 `c-coding-standards` / `cpp-coding-standards` 判断。
- 本节点只判断嵌入式领域风险是否被设计、实现和证据闭环。

### `devflow-completion-gate`

- 适用嵌入式风险矩阵必须为 `clean`、`documented-debt` 或有明确 N/A 理由。
- 任一未解释 `critical-open` 阻塞完成。

### `devflow-finalize`

- closeout 必须同步嵌入式约束变化到长期资产。
- 报告中列出适用风险审计状态和未关闭债务。

### `devflow-problem-fix`

- reproduction 记录目标平台、硬件/仿真环境、配置、日志和稳定性。
- root cause 分类到适用嵌入式维度。
- fix boundary 明确不扩散到未批准的平台、资源或接口变更。

## 嵌入式风险速查

### 内存

- 动态分配是否符合组件设计。
- 栈对象大小是否受控，大数组是否在堆 / 静态池。
- 句柄 / 缓冲区 / 文件描述符获取与释放配对。
- 错误路径下无泄漏。
- 指针生命周期清晰，无悬垂指针 / use-after-free。
- 内存对齐符合目标平台。
- 跨边界传递的 buffer 长度与所有权语义清晰。

### 并发 / 中断

- 中断上下文中不调用阻塞 API、长 IO 或动态分配。
- 共享数据访问受锁 / 原子操作保护。
- 锁顺序一致，避免嵌套锁循环 / 死锁。
- `volatile` 仅用于硬件寄存器或中断共享变量。
- memory order / barrier 使用有依据。
- 临界区尽可能短。

### 实时性

- 关键路径无意外阻塞。
- 调度优先级符合组件设计。
- 时钟 / 节拍 / deadline 有测试或证据支撑。
- 硬实时路径不做日志 / 长 IO。

### 资源生命周期

- 资源创建 / 销毁配对。
- 错误路径下资源回收完整。
- 全局 / 静态资源初始化顺序符合设计。

### 错误处理

- 输入校验覆盖外部接口、协议、配置加载。
- 错误码不被静默吞掉。
- 降级路径在设计中有定义且实现一致。
- 失败时副作用已回滚。

### ABI / API 兼容

- 公共接口签名变更已纳入设计修订。
- 新增错误码不破坏既有消费方。
- 数据结构布局变化符合跨版本 / 跨平台兼容策略。
- 编译条件 / 配置项变更与组件级依赖约定一致。

### 编码规范 / 静态分析

- 团队编码规范关键点已检查。
- MISRA / CERT 等语言规范由 `c-coding-standards` / `cpp-coding-standards` 判断。
- 编译 warning level 一致；critical 告警闭环。
- 静态分析 critical / blocker 项闭环。
- suppression 必须带理由和范围。

## 反向理由化（Common Rationalizations）

| 话术 | 反驳 |
|---|---|
| 「这只是实现细节，code review 再看」 | 嵌入式约束必须前置到规格和设计，否则实现后才发现通常已经太晚 |
| 「目标平台上应该不会触发」 | 平台假设必须有来源和证据，不能靠口头判断 |
| 「资源泄漏很小」 | 资源泄漏在长生命周期设备上会累积成可靠性问题 |
| 「中断里调用一次应该没事」 | 中断上下文规则不靠概率豁免，必须符合平台约束 |
| 「静态分析是误报」 | 可以抑制，但必须有理由、范围和 owner |

## 验证清单

- [ ] 已明确本 work item 是否启用嵌入式领域约束。
- [ ] 规格阶段已捕获适用内存 / 资源 / 实时性 / 中断 / 平台约束。
- [ ] 设计阶段已消费约束且未重定义未授权边界。
- [ ] TDD evidence 覆盖适用风险或提供明确 N/A 理由。
- [ ] test-review / code-review / completion-gate 均消费嵌入式约束。
- [ ] finalize 同步长期资产时保留嵌入式约束变化。

## DevFlow 约定

本 skill 是第三层代码内在质量的领域约束扩展。它不写 `progress.md`、handoff 或 review verdict，不改变 canonical runtime nodes。需要 runtime routing 时回 `devflow-router`。
