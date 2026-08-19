# Bootstrap Workflow

从空知识库冷启动时遵循本流程。目标是先建立可导航、可追溯的最小知识产品，再围绕真实任务深化，不追求一次性解释所有代码。

## 1. 阶段状态机

```text
scope
→ inventory
→ system-map
→ domain-candidates
→ reconciliation
→ review
→ publish
→ complete
```

每完成一个阶段，更新 `.kb/bootstrap-state.yaml`。中断后从磁盘状态继续，不依赖聊天历史。

## 2. Scope：固定范围和基线

收集：

- 知识库根目录；
- 来源仓库路径和远程 URL；
- 分支、commit SHA、子模块和 LFS 状态；
- include/exclude 路径；
- 一方代码、测试、文档、迁移、生成代码、vendor 和二进制分类；
- 用户已知的系统名、owner 和关键业务入口；
- 敏感目录与不可读取范围；
- 是否允许执行构建、测试或语言索引器。

默认策略：

- 静态扫描；
- 不执行来源仓库代码；
- 排除 `.git`、vendor、依赖缓存、构建输出和二进制；
- 保留被排除范围和原因；
- 未取得 SHA 时使用文件内容哈希，并报告可重现性下降。

初始化：

```text
.kb/config.yaml
.kb/source-registry.yaml
.kb/authority-matrix.yaml
.kb/bootstrap-state.yaml
.kb/inventory/
.kb/proposals/
.kb/conflicts/
.kb/review-queue/
knowledge/index.md
knowledge/log.md
```

退出条件：

- 范围和限制明确；
- 基线版本可重现或明确说明不能重现；
- 不支持语言、缺失依赖和访问限制可见。

## 3. Inventory：确定性盘点

先运行 `scripts/inventory_repository.py` 获取通用清单，再用可用的语言工具补充。不要因为专用工具不可用而伪造结果。

### 3.1 通用扫描

识别：

- 语言和文件分布；
- manifest、lockfile、workspace 和 build root；
- 入口文件和启动配置；
- CI/CD、容器和部署文件；
- OpenAPI、AsyncAPI、protobuf、GraphQL；
- 数据库迁移和 schema；
- 测试目录、fixture 和快照；
- CODEOWNERS；
- ADR、README 和实现设计文档；
- 配置文件和环境变量样例。

### 3.2 语言与框架补充

仅在工具可用时提取：

- AST 符号；
- 定义和引用；
- 路由和 handler；
- 静态候选调用；
- ORM 实体和 Repository；
- 消息生产者、消费者和 channel；
- 定时任务；
- 状态枚举和显式转换。

每种关系记录提取方法，禁止把不同含义合并成一个“依赖图”：

```text
package dependency
build dependency
import dependency
symbol reference
static candidate call
runtime observation
API dependency
event dependency
data dependency
deployment dependency
```

### 3.3 盘点输出

最小输出：

```text
.kb/inventory/repository.json
.kb/inventory/files.json
.kb/inventory/build-units.json
.kb/inventory/interfaces.json
.kb/inventory/events.json
.kb/inventory/data-models.json
.kb/inventory/tests.json
.kb/inventory/documents.json
.kb/inventory/limitations.json
```

可以合并为较少文件，但字段必须区分事实、推导方法、来源和失败。

退出条件：

- 扫描范围内文件完成盘点；
- 核心构建根、契约、迁移和入口有明确结果；
- 所有失败有路径和原因；
- 没有业务语义被写入稳定知识。

## 4. System Map：生成实现地图

### 4.1 生成顺序

1. `Repository`
2. `Application`
3. `Module`
4. `API Endpoint`
5. `Event Channel`
6. `Data Model`
7. `Configuration`

每个页面链接回固定版本来源。机械字段可由独立过程验证；“负责什么业务”仍是候选语义。

### 4.2 应用边界

候选 Application 可由以下信号组合：

- 可部署单元；
- 启动入口；
- 构建目标；
- 容器或 IaC 资源；
- 独立配置；
- API 或消息边界；
- 数据所有权。

不要仅按顶层目录创建应用。

### 4.3 C4 视图

首版只维护：

- System Context：用户、外部系统和总体边界；
- Container：可部署/运行单元及通信方式；
- Dynamic：仅为关键跨系统流程按需生成。

Component 和 Code 图不作为冷启动长期资产。

退出条件：

- Agent 能从根 index 定位系统、入口、消息和数据；
- 页面来源可追溯；
- 技术关系标明类型和提取方法；
- 应用职责推断明确标为 draft。

## 5. Domain Candidates：提出候选领域模型

领域候选不能仅从类名和目录产生。综合：

- 业务术语及同义词；
- 状态、规则和验证；
- API operation 与事件语义；
- 数据所有权；
- 跨模块事务边界；
- 测试场景；
- owner 和团队边界；
- 共同变更历史；
- 实现设计文档。

### 5.1 候选 Bounded Context

为每个候选输出：

- 名称；
- 模型适用范围；
- 不在范围内的内容；
- 核心术语；
- 事实拥有者；
- 相关系统；
- 上下游候选；
- 支持证据；
- 反证和边界热点；
- 待人工确认问题。

不要把候选边界直接标为 stable。

### 5.2 统一语言

术语必须绑定 Context：

- 正式定义候选；
- 别名；
- 容易混淆的同名词；
- 示例和反例；
- 对应 API、事件、表和代码符号；
- 与相邻 Context 的翻译关系；
- 来源和待确认项。

禁止建立抹平 Context 差异的全局单一词典。

### 5.3 流程和规则

从明确入口构造候选链：

```text
Controller / Consumer / Job
→ Application Service
→ Domain/Business Logic
→ State / Validation
→ Repository / Data Model
→ Event / External Call
→ Tests
```

在正文中分开：

- 已观察实现事实；
- 可重复推导关系；
- 候选业务解释；
- 未知和冲突。

退出条件：

- 候选 Context 和术语有多类证据；
- 未确认语义保持 draft；
- 每项高风险主张有 review queue；
- 没有以代码结构替代领域确认。

## 6. Reconciliation：代码与文档对账

逐项把设计文档主张分类：

| 分类 | 含义 | 动作 |
|---|---|---|
| `support` | 与实现和已有知识一致 | 增加来源 |
| `refine` | 补充代码无法表达的语义 | 更新 draft 或提案 |
| `conflict` | 与实现或同等级来源矛盾 | 写冲突报告 |
| `to-be` | 描述目标设计 | 单独 `view: to-be` |
| `historical` | 描述历史状态 | 单独历史视图 |
| `unknown` | 无法判断 | review queue |

冲突报告使用 `templates/conflict.md`。不要把“较新的日期”自动当作真相。

## 7. Review：分级审核

优先审核：

1. 核心领域边界；
2. 影响开发决策的业务规则；
3. 跨系统契约和事实拥有者；
4. 安全、资金、权限和发布知识；
5. 高频变化或高事故风险区域。

无需逐页人工确认机械事实。人负责业务语义、取舍和冲突裁决。

审核结果：

```text
confirmed
modified-and-confirmed
rejected
keep-draft
needs-more-evidence
```

记录 verifier、时间、职责范围和证据。

## 8. Publish：校验和发布

执行：

```bash
python3 scripts/validate_okf.py <kb-root>/knowledge
python3 scripts/rebuild_indexes.py <kb-root>/knowledge --check
python3 scripts/check_links.py <kb-root>/knowledge
python3 scripts/detect_stale.py <kb-root>/knowledge
```

再检查：

- 无未标记推断；
- 无稳定业务 Concept 缺少 human verifier；
- 无来源循环和自我证明；
- 无 restricted 内容；
- index 和 log 与变更集一致。

全部硬门禁通过后，原子应用 proposal。

## 9. 冷启动完成标准

冷启动完成不等于“仓库全部文档化”，而是：

- 根 index 可导航；
- 核心系统、入口、事件和数据可定位；
- 关键页面可追溯到固定版本来源；
- 候选领域边界和术语已显式列出；
- 高风险未知项进入 review queue；
- Agent 面对证据不足时不会把推断当事实；
- 后续可以通过 expand、ingest 和 sync 增量演进。
