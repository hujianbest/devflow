# DevFlow Internal Quality

> 本文定义 DevFlow 第三层“代码内在质量”的架构参考模型。运行时可消费的第三层统筹 skill 是 `devflow-clean-design` 与 `devflow-clean-code`；本文不是 runtime node，也不写 handoff。

## 1. 第三层回答什么

第三层只回答一个问题：

> 这份代码本身是否设计得好、写得好、值得长期持有？

它关注代码的内在质量，而不是外部行为是否正确。外部行为正确由前两层保障：

- SDD：需求意图正确。
- TDD：功能行为被可执行测试证明正确。

第三层关注：

- 设计是否简单、内聚、低耦合。
- 抽象是否克制，是否有真实用例支撑。
- 接口契约是否清晰，包括错误语义和可观察副作用。
- 代码是否可读、可维护、可演进。
- 模块边界是否稳定。
- 变更是否可审查、可回滚。

## 2. 第三层不回答什么

第三层不负责：

- 需求是否正确。这属于 SDD。
- 测试是否 fail-first、是否覆盖行为。这属于 TDD 与 test-review。
- 具体语言语法和工具链规则。这属于编码规范 skills。
- 具体领域风险矩阵。这属于领域约束 skills。
- runtime 下一节点。这属于 `devflow-router`。

## 3. 内在质量统筹 Skills

第三层由两个统筹 skill 承载：

- `devflow-clean-design`：设计内在质量统筹。
- `devflow-clean-code`：编码内在质量统筹。

二者都是非 canonical skill，不绑定语言和领域，不写 `progress.md` / handoff，不产 verdict。

### 3.1 设计质量

`devflow-clean-design` 统筹：

- **简单性优先**：满足当前 requirement 的最少结构。
- **抽象纪律**：抽象必须由真实重复、真实变化轴或明确稳定接口支撑。
- **高内聚低耦合**：一个模块应有清晰职责，跨模块依赖应可解释。
- **接口契约**：输入、输出、错误、时序、副作用和兼容性必须可冷读。
- **边界稳定**：模块边界不能因单个局部需求随意漂移。
- **演进成本可见**：设计选项要说明长期维护、回滚和迁移成本。

### 3.2 代码质量

`devflow-clean-code` 统筹：

- **可读性**：命名表达意图，控制流直白，注释解释非显然约束。
- **局部性**：变更集中在当前 task / 当前设计允许的范围内。
- **可审查性**：功能变更、重构、格式化不混杂。
- **可回退性**：改动切片足够小，失败时能定位和回滚。
- **死代码清理**：无无效变量、僵尸兼容层、注释掉的历史残骸。
- **错误路径完整**：错误处理不只覆盖 happy path，但具体错误规则由语言/领域扩展提供。

## 4. 编码规范 Skills

编码规范 skills 是 `devflow-clean-code` 下的语言扩展。它们把通用 clean-code 约束落到具体语言。

第一批：

- `c-coding-standards`
- `cpp-coding-standards`

编码规范 skill 可以规定：

- 命名、文件组织、格式化和 lint。
- 测试 harness、构建和静态分析命令。
- 语言特有的危险点。
- 代码评审中语言特有的 rubric 增补项。

编码规范 skill 不应规定：

- 嵌入式、车载、前端、后端等领域风险。
- runtime next action。
- DevFlow artifact layout。

## 5. 领域约束 Skills

领域约束 skills 是第三层的领域扩展。它们把通用内在质量落到具体工程领域。

第一批：

- `embedded-development`
- `automotive-development`

领域约束 skill 可以规定：

- 领域风险维度。
- 领域架构边界。
- 领域证据要求。
- 领域术语和模板增补。
- 对每个 DevFlow flow/review/gate 节点的约束投射。

领域约束 skill 不应规定：

- C 或 C++ 的语言规范。
- runtime next action。
- author / reviewer / gate 的角色边界。

## 6. 与 TDD / Test Review 的边界

测试质量服务于第二层“功能正确”。因此：

- fail-first RED / GREEN / REFACTOR 属于 `devflow-tdd-implementation`。
- 测试有效性、断言强度、mock 边界、测试金字塔属于 `devflow-test-review` 和 TDD 支撑材料。
- `devflow-test-craft` 被移除；测试有效性内容迁入第二层，不再作为第三层 skill。

第三层仍可以影响测试设计，但只从“代码是否更可维护、更低耦合、更易审查”的角度提出约束，不裁决测试是否有效。

## 7. 与 Core Flow Nodes 的关系

Core flow nodes 保持通用 workflow 职责：

- `devflow-specify`：把已接受 work item 澄清为可评审规格。
- `devflow-ar-design` / `devflow-component-design`：写设计工件。
- `devflow-tdd-implementation`：执行 TDD 和记录证据。
- review nodes：独立给出 verdict。
- gates / finalize：判断完成和收尾。

第三层扩展不改变这些节点的拓扑。它们只提供额外约束：

- `devflow-clean-design` 提供通用设计质量判断。
- `devflow-clean-code` 提供通用代码质量判断，并统筹编码规范 skills。
- 编码规范 skills 提供语言判断，归属于 `devflow-clean-code` 的扩展。
- 领域约束 skills 提供领域判断。

## 8. 旧 Craft Skills 迁移规则

旧 craft 内容处理方式：

- `devflow-design-craft`：删除；通用设计质量迁入 `devflow-clean-design`；领域内容迁入对应领域约束 skill。
- `devflow-coding-craft`：删除；通用代码质量迁入 `devflow-clean-code`；C 内容迁入 `c-coding-standards`；C++ 内容迁入 `cpp-coding-standards`。
- `devflow-test-craft`：删除；测试有效性迁入第二层 TDD / test-review 体系。

旧 craft skills 不再保留为运行或兼容入口；新体系直接使用 clean design / clean code。

## 9. 最小验收

第三层重写完成时，应满足：

- Core docs 不再把 `devflow-*-craft` 描述为第三层主架构。
- 每个 core flow/review/gate node 都能说明如何叠加 `devflow-clean-design` / `devflow-clean-code`、编码规范 skill 和领域约束 skill。
- C / C++ / 嵌入式 / 车载规则不再作为 core 默认规则散落在 flow nodes 中。
- `devflow-test-craft` 已移除，并且 `devflow-test-review` 仍能裁决测试有效性。
