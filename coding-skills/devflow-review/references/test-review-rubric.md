# R3：测试与证据评审 Rubric

> 评审对象：测试 diff、最终测试代码、`tasks.md` 的 RED/GREEN/REFACTOR 证据。上游：`srs.md`、两份 delta、canonical 基线和 `traceability.md`。
>
> 核心怀疑：**这些测试会放过哪种违反本次需求或既有语义的实现？**

## 覆盖映射（不过 = critical）

- [ ] delta-design 的每个 Case ID 有对应测试；每条 FR/IFR Acceptance、NFR QAS 和 CON Verification 可指到具体测试或明确的静态/构建证据
- [ ] `tasks.md` 覆盖的 Case ID 集合等于批准的测试设计全集
- [ ] `traceability.md` 的需求条目 → Spec → Design/Case → Task → Test → Evidence 链路闭合
- [ ] delta-spec/design 为 N/A 的缺陷仍有复现测试，并覆盖 canonical 中对应预期行为
- [ ] 修改行为有既有语义回归测试；删除有删除后语义测试
- [ ] NFR 验证保留 Stimulus Source、Stimulus、Environment、Response 和 Response Measure 的完整语境，并有量化或可判定结果，不以“未崩溃”代替
- [ ] 边界输入、错误路径、资源失败和依赖失败均按风险覆盖

## 断言强度（不过 = critical）

- [ ] reviewer 为 2-3 个关键测试指定 mutation，并核验主控 Agent 提供的隔离执行证据：改动点、预期失败和实际结果；reviewer 不编辑工作树
- [ ] 断言覆盖返回值、状态变化、外部输出和明确的“不发生”行为
- [ ] 无非空检查、只查返回码、只验证 mock 调用次数或恒真断言等弱证明
- [ ] 无无断言、依赖日志肉眼判断或永远成功的测试
- [ ] 缺陷复现测试在修复前确实因目标缺陷失败，而非编译、环境或拼写错误

## TDD 证据

- [ ] `tasks.md` 每个 done 任务有真实 RED/GREEN/REFACTOR 记录：命令、关键输出、代码锚点
- [ ] RED 发生在对应实现之前，失败原因是行为缺失或缺陷复现
- [ ] GREEN 来自最终实现；完整套件通过且构建无新增警告
- [ ] REFACTOR 在全绿上完成；N/A 明确说明已按 clean-code 检视且无任务内异味
- [ ] R3 返工没有覆盖原证据，而是追加 finding 对应的新证据和 Resolution

## Mock、稳定性与可维护性

- [ ] mock/fake 只位于硬件、外部组件、时钟或慢 IO 等真实边界
- [ ] 未 mock 内部纯逻辑，未添加 test-only 生产接口
- [ ] 测试独立可重复，无顺序依赖、共享可变状态、未受控时间/随机、sleep 或重试掩盖
- [ ] 测试名称描述场景和预期，一个测试聚焦一个行为

## Verdict 指引

- 覆盖、断言、RED 真实性或最终套件证据失败 → `需修改`，默认返工 `devflow-tdd`
- 测试难写暴露设计错误 → `重新设计`，指向 `devflow-design`
- Acceptance 本身不可判定 → `重新设计`，指向 `devflow-specify`
- mutation 隔离执行证据未提供或无法核验时 R3 不能通过；不得让只读 reviewer 直接改工作树补证据
