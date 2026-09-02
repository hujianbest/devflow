# R2：Delta Design 评审 Rubric

> 评审对象：`specs/changes/ARXXX-<topic>/delta-design.md`。上游：已通过 R1 的 `srs.md`、`delta-spec.md`，以及不可变 `change.json.baseRevision` 对应快照和两份 delta 的 canonical base 元数据；新组件可为空基线。
>
> 核心怀疑：**设计增量是否完整实现规格增量，又没有重定义或破坏未涉及的 canonical 设计？**

## 基线与增量边界（缺失即阻塞）

- [ ] 不可变 `baseRevision`、spec/design canonical base 元数据、component mode 和 R1 记录可核
- [ ] existing 组件的两份 canonical 均为 `baseline-ready`
- [ ] new 组件的 delta 足以从空基线生成首版设计，并与首版规格增量配套
- [ ] base revision 后存在并行变化时已交人澄清，不自行选边或覆盖

## Delta 操作正确性（不过 = critical）

- [ ] 使用稳定 `DD/DEC/TC`，并以组件模板章节路径、功能编号、接口/软件单元实体键和 base 摘要定位 `ADDED / MODIFIED / REMOVED / RENAMED`
- [ ] 非新增操作的章节路径/实体键在组件设计基线中可唯一定位，旧职责/契约引用准确
- [ ] 每项设计变化能回指 SRS 和 delta spec；没有范围外架构、接口或抽象
- [ ] 每条 delta spec 都有对应设计处理，或有可验证的设计层 `N/A`
- [ ] 未涉及模块、接口、错误模型和设计决策保持不变
- [ ] `REMOVED` 明确处理引用、消费者、迁移和兼容性；`RENAMED` 保持功能编号等稳定业务键与正文不变，并列出 from/to 与引用更新

## AR 设计内容完整性（缺失分析 = important；掩盖风险 = critical）

- [ ] AR identity、变更功能点与动态行为均回指 SRS/Spec/DD/TC
- [ ] 实现思路、正常/异常流程、类/软件单元、包目录和依赖变化足以指导编码
- [ ] 数据库/文件持久化、接口、GUI/HMI、代码设计均有实际内容或 N/A 证据
- [ ] 并发、启动退出、休眠唤醒、可靠性、权限/SELinux 等适用领域场景按 profile 和领域技能展开
- [ ] 重构边界、迁移回滚、软件成本影响和高质量设计检查已闭合
- [ ] 内容章节都通过组件章节路径/实体键与 `DD-xxx` 纳入 delta；没有用一段 operation 摘要替代工程设计

## 契约完整（不过 = critical）

- [ ] 新增或修改接口覆盖输入前置、输出后置、错误语义、副作用、并发时序、兼容性
- [ ] 错误分类、传播策略和失败后状态保证明确
- [ ] 跨边界数据说明分配、释放、所有权和存活期
- [ ] 回调注册类接口明确注销竞态、in-flight callback、ctx 存活与安全释放时点
- [ ] `MODIFIED`/`REMOVED` 的回归、迁移和回退策略与规格一致
- [ ] design 没有重新定义 canonical spec 的业务语义

## 结构与复杂度

- [ ] 模块职责按真实变化理由组织，依赖方向单向，无循环和实现泄漏
- [ ] 每个新增抽象、间接层或配置项有当前真实用例或变化轴
- [ ] 有多个真实方案时比较改动范围、复杂度、兼容、回滚和维护成本，并给出理由
- [ ] 单一方案回答“为什么不是更简单的方案”
- [ ] 不为测试 mock 或未来猜想制造单实现接口

## 组件设计质量检查

- [ ] 职责能用一句话说明，软件单元按真实变化理由聚合；依赖单向，无循环、实现泄漏或知识泄漏
- [ ] 每个新增/语义变更接口逐项检查：输入含义、单位、合法范围、NULL 语义和调用上下文；输出/后置状态；每个错误码触发条件与失败后状态；全部副作用；线程安全/可重入/阻塞/超时；兼容、迁移与废弃计划
- [ ] 错误按调用方编程错误、可预期运行失败、环境/硬件故障、不可恢复矛盾分类；边界翻译、处理层、降级进入/退出和失败状态不变量明确
- [ ] 跨边界缓冲区、句柄和回调上下文明确分配者、释放者、返回后存活期；回调注销竞态、in-flight callback 和 ctx 安全释放条件完整
- [ ] 有限资源预算、耗尽行为、init/shutdown 配对和部分初始化失败的反向回滚顺序明确
- [ ] SRP 回到职责/变化理由；OCP 有真实变化轴；LSP 保持前置条件、错误语义和失败状态；ISP 不强迫调用方依赖无关 API/字段/生命周期；DIP 只用于真实硬件/协议/存储/第三方边界
- [ ] 记录评审者提出的更简单候选、其为何不满足当前规格，以及每个新增抽象/间接层/配置项的当前支撑用例；第三个真实用例前的单实现接口按负债审查
- [ ] 对外兼容承诺、内部自由区、演进接缝和回滚成本清楚；未为未来能力预留无需求实现

reviewer 根据 canonical design、delta-design、canonical diff 与证据形成质量结论，
并把结论写入评审记录。任一关键结论缺少可审查依据时形成 finding。

## 测试设计（不过 = critical）

- [ ] 每条 FR/IFR Acceptance、NFR QAS 和 CON Verification 映射到稳定 Case ID 或明确的静态/构建验证；每个 Case 回指需求与 delta spec
- [ ] FR/IFR 含正向、异常和边界；NFR Case 保留完整五要素与量化度量；CON 验证方法可执行
- [ ] 修改行为有保留语义回归用例；删除有删除后语义用例
- [ ] Case Index 后按适用层展开单元、接口、业务/功能、异常/可靠性和风险覆盖，展开没有新增 Case
- [ ] 用例写明层级、预期结果、验证命令、真实 mock 边界，以及适用的因子组合和逻辑覆盖目标
- [ ] `traceability.md` 的 Design Section/Case 列与 delta 内容一致
- [ ] `tasks.md` 可从 Case ID 继续拆解，不包含 delta-design 之外的业务事实

## N/A 纪律

行为和设计基线均不变的缺陷可在 `delta-design.md` 明确 `N/A`，但必须：

- [ ] 引用 canonical design 中已经正确描述的模块、接口和失败语义
- [ ] 证明修复只是实现恢复到既有设计，不改变结构、依赖、所有权、时序或错误模型
- [ ] 保留唯一 Case Index，给出复现/回归 Case、验证命令和应覆盖的 canonical 契约

缺少上述证据的 N/A 按 critical；N/A 仍需 R2 记录、R3 和 canonical sync 复核。

## Verdict 指引

- 模式、基线或并行变化未澄清 → `阻塞`
- 契约、delta 覆盖、测试设计或 canonical 保留失败 → `需修改`
- 边界划分、架构方向或规格本身错误 → `重新设计`，指向 `devflow-design` 或 `devflow-specify`
- 只有无未闭环 critical/important 才能 `通过`
