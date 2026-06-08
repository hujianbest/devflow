# devflow Granularity And Split

> 配套 `devflow-specify/SKILL.md`。规定 `features/<id>/requirement.md` 的需求条目过大时如何检测、如何拆分。
>
> devflow 不维护跨工作项的 deferred backlog——候选拆分的去向是「拆出新 AR work item」，由需求负责人决定何时新建。

## 触发时机

出现以下任一信号时，必须做粒度检查：

- 一条 `FR` 包含多个角色 / 多个目标 / 多个独立结果
- 验收标准开始覆盖大量互不相同的路径
- 当前 work item 范围和「以后再做」的能力混在同一条 row 里
- 用户同时提到了 MVP、后续版本、增量补做、第二期能力

## G1-G6 Oversized Row Heuristics（INVEST `Small` + `Independent`）

适用于 row 表中的**单条 row**（任何 work item 类型）。命中后按 Split Rules 拆分。

| ID | Heuristic | Detection Signal | Typical Action |
|---|---|---|---|
| `G1` | 多角色打包 | 同一条 `FR` 里有 ≥ 2 个角色 / 模块做不同动作 | 按角色 / 模块拆分 |
| `G2` | CRUD 打包 | 创建 / 查询 / 修改 / 删除被写成一个泛化能力 | 按独立行为拆分 |
| `G3` | 场景爆炸 | 一条 `FR` 需要 ≥ 4 个彼此独立的验收场景才能说清 | 拆主行为和关键分支 |
| `G4` | 关注点跨层 | 一条 `FR` 同时混了主业务动作 + 后台后处理 + 批量运营动作等独立关注点 | 按用户 / 上游 / 运维各自可感知的独立结果拆分 |
| `G5` | 多状态混写 | 一条 `FR` 覆盖 ≥ 3 个状态 / 模式下的不同规则 | 按状态族拆分 |
| `G6` | 时间耦合 | 触发动作和延迟 / 定时 / 归档 / 异步结果绑定在同一条需求里 | 拆即时结果和延时结果 |

嵌入式补充（devflow-specific）：

| ID | Heuristic | Detection Signal | Typical Action |
|---|---|---|---|
| `GE1` | 中断 / 非中断混写 | 一条 `FR` 同时覆盖中断上下文与任务上下文的相同行为 | 按上下文拆分；中断侧通常只做最小写入 + 调度 |
| `GE2` | 跨编译条件 | 一条 `FR` 同时覆盖多个编译条件 / 目标平台的差异行为 | 按目标平台 / 配置拆分 |

## 拆分规则

- 拆分后子 row 沿用父 row 的主来源与上下文，**不丢失** trace anchor
- 子 row 默认沿用父 row 优先级；若拆分后优先级不同，必须显式重判
- 默认编号 `FR-003a` / `FR-003b` 保留亲缘关系；若团队模板不允许后缀编号，遵循其映射
- 每个子 row 都要重新写自己的 acceptance；不允许只写「同父需求」
- 拆分后若仍命中 G1-G6，继续拆，直到每条 row 通过粒度检查
- 不允许把拆掉的需求暗自移除；移除必须显式记成 `EXC` 或在 Open Questions 中说明

## 机械拆分 vs 范围塑形拆分

机械拆分（authoring 节点可以直接修文）：

- 只是把同一 work item 范围内的复合 row 拆成更清晰的子 row
- 不改变本 work item 范围边界
- 不改变已确认的优先级 / 角色边界 / work item 类型

非机械拆分（必须先回到用户 / 需求负责人确认）：

- 拆分后会把部分子 row 移出当前 work item
- 拆分后会改变已确认的优先级
- 拆分后会改变关键角色边界 / 验收范围
- 拆分后已经构成一个**独立可发布的能力** → 应该拆出新 work item，不再挤进当前 row 表

简化判断：

- **只改表达，不改范围** → 可直接修
- **一旦改范围 / 优先级 / 上下游归属** → 先问需求负责人

## 跨 Work Item 拆分（不进入 deferred backlog）

devflow 不维护 `spec-deferred.md` 等跨工作项 backlog。当一条 row 拆分后构成独立可发布能力时：

| 场景 | 处理 |
|---|---|
| AR / DTS / CHANGE 的 row 拆出后构成独立 AR | **拆出新 AR work item**（由需求负责人新建，由 router 重新分流）；当前 work item 的 `EXC` 中显式注明「该能力已拆出 AR-XXXX」 |
| AR row 拆出后构成独立 DTS / hotfix | 同上，新建 DTS work item |

无论哪种场景，原 work item 的 `requirement.md` 里**必须**留 trace anchor（指向新 work item ID）；不允许「拆掉就不见」。

## 常见失败模式

- 看到「大需求」只在 prose 里说「后面再拆」
- 拆分后没有保留来源 / 优先级 / 验收标准
- AR row 拆出独立可发布能力却仍留在原 work item（应拆出新 AR work item）

## 与其他 reference 的关系

- 单条 row 的最小字段、句式、acceptance、priority、anchor：`requirement-rows-contract.md`
- NFR 行的 QAS 五要素：`nfr-quality-attribute-scenarios.md`
- spec-review 中对粒度的 rubric 检查（含 G1-G6）：the spec-review rubric
