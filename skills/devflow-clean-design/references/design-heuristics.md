# Clean Design 深入参考

> 配套 `devflow-clean-design/SKILL.md`。SKILL 给心法与速查，本文给度量、落地细则和完整气味目录。按需读取，不必一次读完。

## 1. 复杂度的精确定义

复杂度 = 让系统**难理解、难修改**的一切。可分解为：

- **改动放大（change amplification）**：一个看似简单的改动，需要在很多地方做修改。
- **认知负担（cognitive load）**：开发者要完成一件事必须掌握的信息量。注意：代码行少不等于认知负担低——一行把错误悄悄吞掉的代码，认知负担极高。
- **未知的未知（unknown unknowns）**：必须改某处、或必须掌握某信息，但你**不知道**它存在。这是最坏的一种，因为你连"要去查"都不知道。好设计的最高目标是让系统**显而易见（obvious）**，消灭未知的未知。

**两个根因**：依赖（dependencies）与晦涩（obscurity）。设计的每个决定都应朝"减少依赖、减少晦涩"使劲。

**战术 vs 战略编程**：只为"让这个功能现在能跑"写代码是战术编程，它持续制造一点点复杂度，利滚利成泥潭。战略编程把"产出好设计"也当作工作目标，愿意为更干净的结构多花约 10–20% 的时间——这笔投资在几周内就回本。

## 2. 深模块与信息隐藏

### 深模块判据
- 接口复杂度 ≪ 实现复杂度。
- 调用方"用对它"几乎不需要知道内部。
- 常见情况零配置或极少配置。

### 信息隐藏（information hiding）
每个模块应封装一个**设计决策**，对外不暴露。被泄漏的典型：
- 文件格式 / 协议字节布局散在多个模块。
- 某个算法的中间状态通过 getter 暴露。
- "这个值用完要记得 free / unlock / commit" 这类知识落在调用方身上。

**信息泄漏（information leakage）= 同一设计决策被多个模块知道。** 一旦泄漏，改这个决策就要同时改多处（改动放大）。修法：把决策收进单一模块，对外只给行为接口。

### 临时分解（temporal decomposition）是常见陷阱
按"执行的时间顺序"切模块（读→处理→写）往往导致信息泄漏，因为同一个知识（如文件格式）在读和写里都要用。应按**知识/决策**切模块，而不是按执行步骤切。

### 把错误设计掉（define errors out of existence）
减少异常处理的最好办法不是 catch 得更多，而是重新定义语义让异常不产生：
- `unset(key)` 对不存在的 key 定义为 no-op，而非报错。
- 区间删除把越界部分裁剪到合法范围，而非抛异常。
- 文本编辑器的"删除选区"在无选区时定义为空操作。

每消掉一类错误，就消掉了所有调用方对应的处理分支。

## 3. SOLID 落地（用复杂度视角，而非教条）

| 原则 | 真正在防的复杂度 | 落地信号 |
|---|---|---|
| SRP 单一职责 | 改动放大 | 一个模块只有**一个变化理由**；说不清职责一句话就是要拆 |
| OCP 开闭 | 改动放大 | 新增行为靠加代码而非改老代码——但只在已有真实变化轴时才提前留扩展点 |
| LSP 里氏替换 | 未知的未知 | 子类型不削弱父类型的契约（不抛新异常、不收窄输入、不放宽输出）|
| ISP 接口隔离 | 认知负担 | 调用方不被迫依赖它用不到的方法；宽接口拆成角色接口 |
| DIP 依赖倒置 | 依赖方向 | 高层模块依赖抽象，细节依赖抽象；让"策略"不依赖"机制" |

**反教条提醒**：SOLID 是为了压复杂度，不是为了多造接口。为满足 DIP/OCP 而给单实现造接口，是典型的过度抽象（见 §6）。

## 4. GRASP：职责该放哪

分配职责时的常用判据：

- **Information Expert**：把职责给"拥有完成它所需信息"的那个对象。
- **Creator**：谁聚合/紧密使用 B，就由谁创建 B。
- **Low Coupling / High Cohesion**：每个分配方案都用这两条打分。
- **Controller**：用例的第一个接收者放在一个协调对象里，不要散进 UI。
- **Polymorphism**：按类型分叉的行为用多态替代散落的 if/switch——**前提是变化轴真实存在**。
- **Protected Variations**：在"预期会变"的点用稳定接口包住，挡住波及——同样要求变化是真实预期的，不是臆想。

## 5. 连接度（Connascence）量表

两段代码 connascent = 改一处必须改另一处才能保持正确。强度从弱到强：

| 等级 | 名称 | 例子 | 倾向 |
|---|---|---|---|
| 弱 | Name | 都引用同一个函数名 | 可接受 |
| ↓ | Type | 依赖同一类型 | 可接受 |
| ↓ | Meaning | 都知道"0 表示成功" | 用具名常量消除 |
| ↓ | Position | 依赖参数顺序 | 多于 2-3 参数时用具名参数/对象 |
| ↓ | Algorithm | 两端必须用同一算法（如校验和） | 收进同一模块 |
| 强 | Execution order | 必须按序调用 | 用单一入口消除（时序耦合）|
| 强 | Timing | 依赖时间窗口/时序 | 设计上消除 |
| 强 | Identity | 必须引用同一个实例 | 最危险，尽量本地化 |

**两条规则**：
1. **强连接要本地化**：强连接只允许出现在同一模块内部；跨模块边界只能有弱连接（Name/Type）。
2. **跨边界降级**：把跨模块的强连接重构成弱连接，正是"降耦合"的精确含义。

## 6. 设计气味完整目录 → 重构手法

| 气味 | 更细的信号 | 重构手法 |
|---|---|---|
| 浅模块 | 直通方法、接口≈实现 | Inline、合并相邻层、加深接口 |
| 信息泄漏 | 同一决策在多模块出现 | 把决策收进单模块（Encapsulate）|
| 临时分解 | 按执行步骤切模块导致重复知识 | 按知识/决策重切边界 |
| 时序耦合 | init→use→cleanup 必须手动配对 | 单一入口 / RAII / context manager |
| 上帝模块 / 上帝类 | 多个变化理由、几千行 | Extract Class，按变化理由拆 |
| 特性依恋 | 模块 A 老是操作 B 的数据 | Move Method 到数据所在处 |
| 过度抽象 | 单实现接口、单子类、一次性"通用工具" | Inline，等 Rule of Three |
| 配置爆炸 | 大量 flag/option | 合理默认值、零配置常见路径 |
| 接口契约空泛 | 只有签名 | 补错误语义/副作用/时序/兼容 |
| 双向/环形依赖 | A↔B、模块环 | 倒置依赖、引入稳定第三方抽象 |
| 抽象层错位 | 高层出现底层细节 | 下沉细节，高层只表达意图 |
| 泄漏的抽象 | 必须懂底层才能用对上层 | 把底层差异在模块内吸收掉 |
| 重复决策 | 同一规则在多处各写一遍 | 收敛到单一权威处（SSOT）|

## 7. 一个端到端 before/after

需求：把若干传感器读数按阈值告警。

<Bad>
```python
# 临时分解 + 信息泄漏 + 上帝函数：阈值规则散落，加一种传感器要改三处。
def run():
    raw = open("sensor.bin","rb").read()
    vals = []
    for i in range(0, len(raw), 4):                 # 知道字节布局
        vals.append(int.from_bytes(raw[i:i+4],"big"))
    alerts = []
    for v in vals:
        if v > 100: alerts.append(("temp", v))      # 阈值硬编码 + 散落
    for a in alerts:
        print("ALERT", a)                           # 输出也焊在这
```
</Bad>

<Good>
```python
# 深模块 + 信息隐藏：每个设计决策各有归属，加传感器只动一处。
class SensorFeed:                 # 隐藏字节布局这一决策
    def readings(self) -> list[Reading]: ...

class AlertPolicy:                # 隐藏"什么算告警"这一决策
    def evaluate(self, r: Reading) -> Alert | None: ...

def monitor(feed: SensorFeed, policy: AlertPolicy, sink: AlertSink) -> None:
    for r in feed.readings():
        if (alert := policy.evaluate(r)) is not None:
            sink.emit(alert)
```
</Good>

变化轴一目了然：换数据源改 `SensorFeed`，改规则改 `AlertPolicy`，改输出改 `AlertSink`，`monitor` 表达意图、不含任何底层细节。注意：只有当这些变化轴**真实存在**（确实会换数据源/改规则）时才值得这样拆；若永远只有一种传感器、一条规则，过度拆分同样是浪费。

## 8. 参考脉络

本文的判据综合自这些被广泛验证的来源，便于追溯与深读：

- John Ousterhout, *A Philosophy of Software Design*（复杂度、深模块、信息隐藏、设计两遍、把错误设计掉）。
- Martin Fowler, *Refactoring*（气味与手法词汇）。
- Robert C. Martin, *Clean Code* / *Clean Architecture*（SOLID、边界）。
- Craig Larman, *Applying UML and Patterns*（GRASP）。
- Meilir Page-Jones / Jim Weirich（Connascence）。
- Eric Evans, *Domain-Driven Design*（边界与限界上下文，按需）。
