---
name: cpp-coding-standards
description: 在编写、修改或评审 C++ 代码（.cpp/.cc/.hpp、类、模板、RAII、智能指针、C++ 测试、C++ ABI 边界）时使用。提供资源管理、所有权签名、类设计、错误策略、模板纪律与 ABI 的具体规则与正反例。只适用于 C++；C 或其他语言代码使用对应语言自己的 coding-standards 技能。
---

# C++ Coding Standards

## 总览

现代 C++ 的核心承诺：**资源安全可以由结构保证，而不是靠每个人小心。** 本技能在 `devflow-clean-code` 之上叠加 C++ 规则，不能替代通用 clean-code 自检；取向与 C++ Core Guidelines 一致，项目声明了 AUTOSAR C++ / 团队子集时以项目为准。

## RAII：资源唯一正解

每种资源（内存、文件、锁、硬件句柄）由一个对象的生命周期管理，构造获取、析构释放。手动配对调用在第一个提前 return / 异常处就会泄漏：

```cpp
// ❌ 手动配对：中间任何一条提前退出路径都泄漏
void update() {
    mutex_.lock();
    auto *buf = new uint8_t[kFrameSize];
    if (!fetch(buf)) { mutex_.unlock(); return; }  // 忘了 delete[]
    ...
}

// ✅ 结构保证：任何退出路径都正确释放
void update() {
    std::lock_guard<std::mutex> lock(mutex_);
    std::vector<uint8_t> buf(kFrameSize);
    if (!fetch(buf.data())) return;
    ...
}
```

- 新代码不出现裸 `new`/`delete`：容器、`std::make_unique`/`std::make_shared`、或项目的池分配器
- 自定义资源（C API 句柄、寄存器映射）→ 写一个小 RAII 包装类，遵守规则五（见下）
- 锁一律 `lock_guard`/`unique_lock`/`scoped_lock`，不裸 lock/unlock

## 所有权写在签名里

签名就是所有权文档，按下表选型：

| 意图 | 签名 |
|---|---|
| 只读借用，不存指针 | `const T&`（可能为空时 `const T*`） |
| 可变借用 | `T&` |
| 转移唯一所有权 | `std::unique_ptr<T>`（按值传/返回） |
| 共享所有权（确有共享需求才用） | `std::shared_ptr<T>` |
| 观察但不拥有、生命周期由外部保证 | 裸指针/引用 + 契约注释 |

- 默认 `unique_ptr`；`shared_ptr` 必须能回答"谁是第二个 owner"——答不上来就是用它来逃避所有权思考
- **函数参数不用 `const shared_ptr<T>&` 表达借用**——借用就传 `const T&`/`T*`，不强迫调用方持有特定智能指针
- 存储跨生命周期的观察指针（成员里存别人的 this、回调 ctx）是悬垂高发区：要么 `weak_ptr`，要么在契约中写明注销时序并在析构中强制注销

## 类设计

- **规则零优先**：成员全部用 RAII 类型，五个特殊成员函数一个都不写。需要自定义析构 → 规则五：五个全部显式（定义或 `=delete`/`=default`）
- 单参构造一律 `explicit`（隐式转换是事故源）；不打算被继承的类不写 `virtual`；要继承的基类析构 `virtual`，重写函数标 `override`
- 成员初始化用初始化列表/类内默认值，顺序与声明一致；构造完成即不变量成立——需要 `init()` 二段构造的设计先回 `devflow-design` 审视
- 不变量由 private + 成员函数维护；全是 public 数据的聚合就用 `struct` 并保持纯数据

## 错误策略

- 项目先定一件事：异常是否启用（嵌入式/车载常禁用）。**禁用**时：可失败操作返回错误码或 `expected<T, E>`（或项目等价 Result 类型），出错路径显式可见；**启用**时：构造失败抛异常，析构永不抛，边界（C 回调、线程入口、ABI 边界）全部 catch 并翻译
- 无论哪种策略：`[[nodiscard]]` 标注可失败的返回值，让"忘了检查"变成编译警告：

```cpp
[[nodiscard]] Result<void> apply_config(const Config &cfg);
```

- 析构、move 操作、swap 默认 `noexcept`——容器依赖这一点选择 move 还是 copy

## const 与值语义

- 成员函数能 `const` 就 `const`；多线程下 `const` 成员函数必须真的线程安全（内部缓存要加锁或 `mutable atomic`）
- 编译期常量 `constexpr`，查表数据 `constexpr` 数组（进只读段）
- 小对象按值传，大对象 `const&`；返回值直接按值返回（RVO/move 已解决性能顾虑），不为"省拷贝"返回内部引用而泄漏生命周期

## 模板与抽象纪律

- 模板解决**真实存在的多类型需求**，不为"以后可能泛化"模板化；当前只有一个实例化类型 → 写具体类型
- 模板错误信息与编译时间是真实成本：公共接口的模板参数加约束（`static_assert` / concepts，按项目标准版本）
- 继承表达"is-a 且有多态需求"，否则组合；单实现的抽象基类同 `devflow-design` §抽象纪律处理
- 不在头文件暴露只有实现需要的模板辅助（藏进 `detail` 命名空间或 .cpp）

## ABI 与边界（对外交付库时）

- 跨 ABI 边界（动态库接口、跨团队交付）：不暴露 STL 类型/异常/虚表布局敏感的类；用 C 风格接口或 pImpl 隔离
- pImpl 用于需要稳定二进制接口的公共类：头文件只剩不透明指针，实现自由演进
- 改既有公共类的成员/虚函数顺序 = ABI 破坏，必须走 `devflow-specify` 的 modify 流程评估消费者

## 现代惯用法速查

- `auto` 用于右侧类型显然或冗长（迭代器、lambda）；接口边界与数值类型写明确类型
- 范围 for + 算法优先于手写索引循环；`enum class` 优先于裸 enum
- 聚合初始化/统一初始化 `{}` 防窄化；`nullptr` 不用 `NULL`/`0`
- lambda 捕获显式列出（异步/存储的 lambda 禁用 `[&]` 默认捕获——悬垂引用高发区）

## 工具链

- 零警告基线（`-Wall -Wextra`，项目允许时 `-Werror`）；clang-tidy 按项目配置，新增项修复或带理由抑制
- sanitizer（ASan/UBSan/TSan）在单测中可用就开；它们抓的就是本文每节的事故类
- 评审重点：生命周期（悬垂引用/迭代器失效）、异常安全路径、特殊成员函数完整性、模板必要性

## 自检清单

- [ ] 无裸 new/delete、裸 lock/unlock；自定义资源有 RAII 包装
- [ ] 所有权可从签名读出；`shared_ptr` 有真实的第二 owner；存储型观察指针有生命周期契约
- [ ] 规则零或规则五，无中间态；单参构造 explicit；多态基类虚析构 + override
- [ ] 错误策略与项目一致；可失败返回值 `[[nodiscard]]`；析构/move `noexcept`
- [ ] 模板/继承有真实变化轴；无单实现抽象基类
- [ ] ABI 敏感边界已隔离（C 接口 / pImpl）
- [ ] 异步/存储 lambda 无默认引用捕获
- [ ] 零新增警告；静态分析/sanitizer 发现项闭环
