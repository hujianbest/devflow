# Clean Code 深入参考：代码气味 → 重构手法

> 配套 `devflow-clean-code/SKILL.md`。SKILL 给心法与速查，本文给完整气味目录、Fowler 手法词汇、Tidy First 微整理与端到端示例。按需读取。

## 1. 代码气味 → 重构手法对照表

命中气味时，用对应手法处理；手法名用 Fowler 词汇，便于在 Refactor Note 和 code-review 里对齐。

| 气味 | 信号 | 重构手法 |
|---|---|---|
| 长函数 | 一屏放不下、要靠注释分段 | Extract Function；Decompose Conditional |
| 长参数表 | ≥4 参数、或一串布尔 | Introduce Parameter Object；Preserve Whole Object；Replace Parameter with Query |
| 重复代码 | 真实且稳定的重复 ≥3 处 | Extract Function / Class；Pull Up Method |
| 深嵌套 | if/for 嵌套 >3 层 | Replace Nested Conditional with Guard Clauses；Extract Function |
| 魔法数 / 魔法串 | 字面量散落、含义靠猜 | Replace Magic Literal with Named Constant |
| 神秘命名 | `data`/`tmp`/`mgr`/`do_it` | Rename Variable / Function |
| 注释补偿 | 复杂表达式靠注释才懂 | Extract Variable（解释性变量）；Extract Function |
| 数据泥团 | 同几个字段总是一起出现 | Extract Class / Introduce Parameter Object |
| 基本类型偏执 | 用裸 int/string 表达领域概念 | Replace Primitive with Object（如 `Money`、`UserId`）|
| 发散式变化 | 一个类因多种原因反复改 | Extract Class（按变化理由拆，SRP）|
| 霰弹式修改 | 一个改动要散到很多类 | Move Method/Field 把相关行为聚到一处 |
| 特性依恋 | 方法老操作别的类的数据 | Move Function 到数据所在处 |
| 开关语句重复 | 同样的 switch/if-type 多处出现 | Replace Conditional with Polymorphism（变化轴真实时）|
| 临时字段 | 字段只在某些情况下有意义 | Extract Class；引入 Null Object |
| 死代码 | 永假分支、无人调用、注释掉的代码 | 直接删除（版本控制即历史）|
| 中间人 | 类大部分方法只是转手委托 | Remove Middle Man / Inline |
| 过度暴露 | public 了本该 private 的状态 | Encapsulate Field；收窄可见性 |

## 2. 解释性重构两招（最常用、最便宜）

**Extract Variable（解释性变量）**：给中间结果起个有意义的名字，让复杂表达式自解释。

<Bad>
```js
if (platform.toUpperCase().indexOf("MAC") > -1 &&
    browser.toUpperCase().indexOf("IE") > -1 && wasInitialized() && resize > 0) {
  // ...
}
```
</Bad>

<Good>
```js
const isMacOs = platform.toUpperCase().includes("MAC");
const isIE = browser.toUpperCase().includes("IE");
const wasResized = resize > 0;
if (isMacOs && isIE && wasInitialized() && wasResized) {
  // ...
}
```
</Good>

**Extract Function**：把"做第二件事"的代码段抽成命名函数，函数名表达意图，调用处只剩高层叙事。

## 3. Tidy First：安全的微整理清单（Kent Beck）

这些是**行为不变**的小整理，适合在 REFACTOR 帽下、动手改某段代码前先做，让后续改动更安全。每个都该是独立小提交：

- Guard Clauses：把前置检查提到最前，早返回。
- Dead Code：删。
- Normalize Symmetries：让做同类事的代码长得一样（统一风格/顺序）。
- New Interface, Old Implementation：先给想要的调用方式建一个薄接口，转调旧实现。
- Reading Order：把元素按读者理解的顺序重排。
- Cohesion Order：把会一起改的东西放到一起。
- Move Declaration and Initialization Together：变量声明贴近首次使用并就地初始化。
- Explaining Variables / Constants：见 §2。
- Explicit Parameters：把藏在环境/全局里的输入显式化为参数。
- Chunk Statements：用空行把一段逻辑分块（比注释分段更轻）。

**纪律**：Tidy First 仍受范围约束——只整理当前 task 会触碰的代码，且与功能提交分开。跨模块的结构性整理不属于 Tidy First，登记 escalation。

## 4. 函数设计细则

- **命令查询分离（CQS）**：一个函数要么"做事"（改状态、返回 void），要么"回答问题"（返回值、无副作用），不要既改状态又返回值——否则调用方难以预测。
- **避免输出参数**：要返回结果就 return；用可变参数回传是隐藏副作用。
- **无标志参数**：`render(true)` 不可读；拆成 `renderForPrint()` / `renderForScreen()`，或用枚举。
- **Null 处理**：尽量不返回 null，用空集合 / Optional / Null Object；不接受 null 参数，靠类型/契约挡住。

## 5. 端到端 before/after

需求：解析一行 CSV 记录并求合法数值之和。

<Bad>
```python
def p(s):
    a = s.split(",")           # 神秘命名
    t = 0
    for i in range(len(a)):    # 索引循环、深嵌套
        try:
            if a[i] != "":
                if float(a[i]) >= 0:   # 魔法规则散落
                    t = t + float(a[i]) # 重复 parse
        except:
            pass               # 静默吞错
    return t
```
</Bad>

<Good>
```python
def sum_non_negative(record: str) -> float:
    return sum(v for v in _parse_values(record) if v >= 0)

def _parse_values(record: str) -> list[float]:
    values = []
    for field in record.split(","):
        if field == "":
            continue                      # 卫语句：空字段跳过
        values.append(_to_float(field))   # 解析职责下沉，只算一次
    return values

def _to_float(field: str) -> float:
    try:
        return float(field)
    except ValueError as e:
        raise MalformedRecordError(field) from e   # 不静默吞错，带上下文
```
</Good>

改进点对应清单：意图化命名、单一职责小函数、卫语句压平、消除重复 parse、错误带上下文且不被吞、单一抽象层级（顶层函数只讲"非负求和"这一件事）。

## 6. 参考脉络

- Robert C. Martin, *Clean Code*（命名、函数、注释、错误处理、CQS）。
- Martin Fowler, *Refactoring*（气味目录与手法词汇）。
- Kent Beck, *Tidy First?*（安全微整理、Two Hats、提交粒度）。
- Andrew Hunt & David Thomas, *The Pragmatic Programmer*（DRY、正交性、死代码）。
- John Ousterhout, *A Philosophy of Software Design*（认知负担、把错误设计掉——见 clean-design 参考）。
