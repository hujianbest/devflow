---
name: java-coding-standards
description: 在编写、修改或评审 Java 代码（类、record、枚举、JUnit 测试、Maven/Gradle 构建）时使用。提供 null/Optional、相等性与集合契约、资源管理、异常策略、不可变与封装、泛型、并发、数值/字符串陷阱的具体规则与正反例。Kotlin 规则见对应语言技能；框架（Spring/Quarkus）专属约定见 references/。
---

# Java Coding Standards

## 总览

Java 的核心危险是**到处可能为 null，错误能被悄悄吞掉**。本技能在 `devflow-clean-code` 的通用标准之上叠加 Java（17+）语言规则，不能替代通用 clean-code 自检；每条规则针对一类真实事故（NPE、丢数据、泄漏、被吞的异常、ClassCastException、竞态）。项目声明了 Google Java Style / 团队规范子集时以项目为准，本文是未声明时的默认底线。

## null 与 Optional

NPE 是 Java 头号事故。约定写进签名与返回类型：

```java
// ❌ 集合 / 数组 返回 null，调用方稍后 NPE
public List<Order> findOrders(String userId) {
    if (none) return null;
    ...
}

// ✅ 集合永不返回 null，返回空集合
public List<Order> findOrders(String userId) {
    if (none) return List.of();
    ...
}

// ✅ 单值可能缺失 → 返回 Optional，调用方被迫处理缺失
public Optional<Market> findBySlug(String slug) { ... }
market.map(MarketResponse::from)
      .orElseThrow(() -> new MarketNotFoundException(slug));
```

- `Optional` 只用于返回值表达"可能没有"；**不**用作字段、方法参数或集合元素（增加分配又不阻止 null）
- 不裸调 `optional.get()`：用 `orElse`/`orElseThrow`/`map`/`ifPresent`
- 外部输入与公共 API 边界做 null 校验（`Objects.requireNonNull(x, "x")`），约定写进 javadoc

## 相等性与集合契约

重写 `equals` 必须同时重写 `hashCode`（否则放进 `HashMap`/`HashSet` 后查不到）：

```java
// ❌ 只写 equals，hashCode 用 Object 默认 → 同值对象散列到不同桶，丢数据
@Override public boolean equals(Object o) { ... }

// ✅ 成对实现，且基于同一组字段；优先用 record 让编译器生成
public record Money(BigDecimal amount, Currency currency) {}  // equals/hashCode 自动且一致
```

- 用作 `Map` key 或放进 `Set` 的类型必须不可变，且 `equals`/`hashCode` 只依赖不可变字段
- 实现 `Comparable` 时 `compareTo` 与 `equals` 保持一致（不一致会让 `TreeMap`/`TreeSet` 行为异常）
- 比较对象用 `equals`，不用 `==`（`==` 比较引用）；比较可能为 null 的两值用 `Objects.equals(a, b)`

## 资源管理

实现 `AutoCloseable` 的资源（流、连接、锁包装）一律 try-with-resources，不手写 finally close：

```java
// ❌ 手写 finally：异常叠加时原异常被 close 异常覆盖，且容易漏 close
InputStream in = open(path);
try { return read(in); } finally { in.close(); }

// ✅ try-with-resources：按声明逆序关闭，异常被 suppressed 保留
try (InputStream in = open(path)) {
    return read(in);
}
```

- 多个资源在同一 try 里声明，自动逆序关闭
- 自有资源类实现 `AutoCloseable`，`close()` 幂等（重复调用安全）

## 异常策略

被吞的异常是定位事故的最大障碍：

```java
// ❌ 吞掉异常：catch 空块 / 打印后继续 / 丢失 cause
try { parse(s); }
catch (ParseException e) { /* ignore */ }

// ❌ 包装时丢掉根因，堆栈断链
catch (IOException e) { throw new ConfigException("load failed"); }

// ✅ 处理或上抛；包装时用 cause 保留异常链
catch (IOException e) {
    throw new ConfigException("load failed: " + path, e);
}
```

- 不 `catch (Exception e)` / `catch (Throwable t)` 做泛捕获，除非边界处集中翻译并重新抛出/记录
- 领域错误用专门的非受检异常子类（`MarketNotFoundException`），不用裸 `RuntimeException`/`IllegalStateException` 承载所有情况
- `finally` 块里不 `return`、不抛新异常（会吞掉 try 中的原异常）
- 不在循环里用异常做正常控制流

## 不可变与封装

```java
// ❌ 暴露内部可变集合：调用方能从外部改坏不变量
private final List<Item> items = new ArrayList<>();
public List<Item> getItems() { return items; }

// ✅ 返回不可变视图或防御性拷贝
public List<Item> getItems() { return Collections.unmodifiableList(items); }
```

- 默认 `final` 字段；纯数据载体优先用 `record`
- 构造完成即不变量成立；需要 `init()` 二段构造的设计先回 `devflow-design` 审视
- 单参构造若有隐式转换风险，避免被当作转换路径（Java 无 explicit，用工厂方法表达意图）

## 泛型与类型安全

```java
// ❌ 裸类型：丢失类型检查，运行期 ClassCastException
List items = new ArrayList();
items.add("x"); Integer n = (Integer) items.get(0);  // 运行期炸

// ✅ 声明类型参数
List<String> items = new ArrayList<>();
```

- 不用裸类型；`@SuppressWarnings("unchecked")` 必须最小作用域 + 注释理由
- 可复用工具用有界类型参数；遵循 PECS（生产者 `? extends`、消费者 `? super`）
- 不对泛型数组、`instanceof` 擦除类型做未检查假设

## 并发

```java
// ❌ 非 volatile 的双重检查锁：其他线程可能看到未完成构造的对象
private Service instance;
public Service get() {
    if (instance == null) synchronized (this) {
        if (instance == null) instance = new Service();
    }
    return instance;  // instance 必须 volatile
}
```

- 共享可变状态最小化；能用不可变对象或 `java.util.concurrent`（`ConcurrentHashMap`、`AtomicX`、`ExecutorService`）就不用裸 `synchronized`/`wait`/`notify`
- 跨线程可见的可变字段用 `volatile` 或 `Atomic*`；复合操作（读-改-写）用原子方法或锁，不靠 `volatile`
- 持锁期间不调用外部回调/未知代码（死锁与重入风险）；锁的获取顺序固定
- 不在线程间共享非线程安全集合（`SimpleDateFormat`、普通 `HashMap`）

## 数值与字符串陷阱

- 金额/精确小数用 `BigDecimal`（且用 `String` 构造，不用 `double`）；`double`/`float` 不承载货币
- 自动装箱的 `Integer`/`Long` 可能为 null，参与算术前判空；缓存外的 `Integer` 用 `equals` 比较不用 `==`
- 整数溢出风险路径用更宽类型或 `Math.addExact`/`multiplyExact`
- 循环内拼接字符串用 `StringBuilder`，不用 `+=`

## 工具链

- 编译零警告基线：`-Xlint:all`，项目允许时 `-Werror`；新增告警按 critical 处理
- 格式化与静态分析按项目配置：Checkstyle / Spotless（Google Java Format）、SpotBugs / Error Prone、PMD；新增项必须修复或带理由 + 范围抑制，"历史上就有"不豁免本次触碰的文件
- 空安全注解（`@Nullable`/`@NonNull`）按项目工具链（NullAway / JSpecify）启用并在 CI 校验
- 测试：JUnit 5 + AssertJ；Mockito 做边界 mock；无隐藏 sleep 的确定性测试

## 自检清单

- [ ] 集合/数组不返回 null；可缺失单值用 `Optional` 返回且不裸 `get()`
- [ ] `equals`/`hashCode` 成对且基于同组字段；Map key/Set 元素不可变
- [ ] `AutoCloseable` 资源用 try-with-resources；无手写 finally close
- [ ] 无被吞异常；包装保留 cause；无泛 `catch (Exception/Throwable)` 未翻译
- [ ] 可变内部不外泄（不可变视图/防御性拷贝）；字段默认 final；数据载体用 record
- [ ] 无裸泛型类型；`@SuppressWarnings` 最小化且带理由
- [ ] 共享可变状态用 j.u.concurrent / 原子 / 锁正确保护；持锁不调外部回调
- [ ] 金额用 BigDecimal；装箱判空；对象比较用 equals
- [ ] 编译零新增警告；静态分析新增项闭环

## 支撑参考

| 文件 | 用途 |
|---|---|
| `references/framework-conventions.md` | Spring Boot / Quarkus 的框架专属约定（DI、配置、异常映射、测试切片）——属框架而非语言，按项目栈选用 |
