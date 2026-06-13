---
name: c-coding-standards
description: 在编写、修改或评审 C 代码（源文件、头文件、C 单元测试）时使用。提供指针所有权、内存与资源、缓冲区、整数、宏、头文件、错误返回的具体规则与正反例。C++ 规则见 cpp-coding-standards。
---

# C Coding Standards

## 总览

C 给了你足够的绳子。本技能在 `devflow-clean-code` 的通用标准之上叠加 C 的语言规则，不能替代通用 clean-code 自检；每条规则针对一类真实事故（越界、悬垂、泄漏、未定义行为）。项目声明了 MISRA C / CERT C 子集时以项目为准，本文是未声明时的默认底线。

## 指针与所有权

每个跨函数边界的指针必须能回答：**谁拥有它、它活多久、能否为 NULL**。约定写进签名和头文件注释：

```c
/* 返回的指针由调用方负责 free */
char *config_dump_alloc(const config_t *cfg);

/* 返回内部静态存储的指针：只读、下次调用前有效、不得 free */
const char *err_to_str(int err);

/* item 的所有权转移给队列：入队成功后调用方不得再访问 */
int queue_push_owned(queue_t *q, item_t *item);

/* buf 由调用方提供并保证在调用期间有效（借用） */
int frame_parse(const uint8_t *buf, size_t len, frame_t *out);
```

规则：

- 公共 API 的指针参数必须有 NULL 语义：要么文档写明"不得为 NULL"并在入口校验，要么定义 NULL 时的行为
- 释放后立即置空局部惯用法可用，但**真正的防线是所有权唯一**：一块内存只有一个 owner 负责释放，其余都是借用
- 不返回局部变量地址；不把栈上 buffer 的指针存进生命周期更长的结构
- 函数内部对 `void *` 的强转必须紧邻校验（魔数/类型 tag），跨模块传 `void *ctx` 时注册方与回调方必须是同一约定的两端

## 内存与资源

- 每个 `malloc`/`open`/`lock` 出现时，先写它的释放路径再写中间逻辑。多资源获取用集中清理出口（goto cleanup 模式，完整示例见 `devflow-clean-code` 的重构目录 §8）：获取顺序与释放顺序相反，失败跳到对应标签。
- `malloc` 返回必须检查；分配大小用 `sizeof(*p)` 而不是 `sizeof(type)`（类型改名时不会悄悄错）：

```c
mode_entry_t *e = malloc(sizeof(*e));        /* ✅ */
mode_entry_t *e = malloc(sizeof(mode_entry_t *));  /* ❌ 经典事故：分配了指针大小 */
```

- 结构体含指针成员时提供成对的 `xxx_create`/`xxx_destroy`，destroy 负责全部深层释放且可安全接受 NULL
- 嵌入式语境：动态分配是否允许、允许在哪个阶段（仅初始化期 vs 运行期）由设计声明（见 `embedded-development`）；运行期热路径默认禁用

## 缓冲区与字符串

- 所有写入 buffer 的接口同时传 buffer 与容量；内部用容量做上界，绝不信任"调用方肯定给够了"
- 字符串拼装一律 `snprintf`，并检查返回值是否 ≥ 容量（截断检测）：

```c
/* ❌ strcpy/strcat/sprintf 进入新代码 = critical */
sprintf(path, "%s/%s", dir, name);

/* ✅ */
int n = snprintf(path, sizeof(path), "%s/%s", dir, name);
if (n < 0 || (size_t)n >= sizeof(path)) return ERR_NAME_TOO_LONG;
```

- `memcpy` 的 len 来自外部输入时，先校验 len ≤ 目标容量再拷贝；协议解析中"先读长度字段再按它拷贝"是最高危路径，必须有显式上界检查
- 数组遍历的循环边界用 `sizeof(arr)/sizeof(arr[0])`（或项目的 ARRAY_SIZE 宏），不要手写常数

## 整数

- 边界/长度/索引用 `size_t`；协议与寄存器字段用定宽类型（`uint8_t`/`uint32_t`），不用裸 `int`/`long` 承载有格式要求的数据
- 有符号/无符号混合比较是事故源：`if (len - 1 > 0)` 在 `len==0` 且 len 为无符号时恒真。减法前先确认不下溢：`if (len > 0 && idx < len - 1)` 或改写为加法 `idx + 1 < len`
- 乘法可能溢出的分配：`malloc(n * size)` 在 n 来自外部时先检查 `n <= MAX / size`，或用 `calloc`
- 位运算的操作数显式无符号：`1u << bit`；移位量必须小于位宽

## 宏

能不用宏就不用：常量用 `enum` 或 `static const`，短函数用 `static inline`。必须用宏时：

```c
/* ❌ 多次求值：max(x++, y) 让 x 加了两次 */
#define MAX(a, b) ((a) > (b) ? (a) : (b))

/* ✅ 改用 static inline——有类型检查、可下断点、无求值陷阱 */
static inline int32_t max_i32(int32_t a, int32_t b) { return a > b ? a : b; }
```

- 仍需宏的场景（token 拼接、编译期开关、泛型容器）：参数全部加括号、整体加括号、多语句体包 `do { ... } while (0)`
- 条件编译块尽量小且互斥分支都能编译；`#if 0` 不是注释手段（删）

## 头文件

- 头文件是模块的契约：只放公共 API、公共类型、必要常量。内部函数 `static` 留在 .c；内部结构体用不透明指针隐藏：

```c
/* public.h —— 调用方只见句柄，结构体布局可自由演进 */
typedef struct mode_service mode_service_t;
mode_service_t *mode_service_create(const mode_config_t *cfg);

/* internal .c 里才有 struct mode_service { ... }; */
```

- 每个头文件自包含（include 它需要的一切）、有 include guard、能被单独编译
- 头文件里不定义变量、不放 `static` 函数实现（`static inline` 的小函数除外）
- include 顺序：自己的头文件最先（强制自包含检验），然后系统头、第三方、项目内

## 错误返回

- 模块统一一种错误约定（负 errno 风格 / 项目错误码枚举 / 0=成功），不混用；出参 + 返回码分离：数据走出参，状态走返回值
- 调用方检查每个可失败调用（`devflow-clean-code` §错误处理）；本技能补充 C 特有项：
  - `snprintf`/`read`/`write` 的部分成功（短写）要处理
  - 注册回调的返回值约定写进回调 typedef 的注释
  - 失败路径上的出参状态写进契约（"失败时 *out 不被修改"是最友好的约定，实现也要真的遵守）

## const 与作用域

- 指针参数不修改指向内容 → `const T *`；查表数据 → `static const`（进只读段，嵌入式省 RAM）
- 一切能 `static` 的文件内符号都 `static`（链接期命名空间卫生）
- 变量在首次使用处声明并初始化；未初始化变量 + 复杂分支 = 未定义行为温床

## 工具链

- 新代码零警告基线：至少 `-Wall -Wextra`，项目允许时 `-Werror`；新增告警按 critical 处理
- 静态分析（clang-tidy / cppcheck / MISRA 检查器按项目配置）：新增项必须修复或带理由+范围抑制；"历史上就有"不豁免本次触碰的文件
- 测试与评审中重点盯：本文每节对应的事故类（越界、泄漏、悬垂、截断、溢出、宏陷阱）

## 自检清单

- [ ] 每个跨边界指针的所有权/生命周期/NULL 语义在签名或注释中可读
- [ ] 多资源函数用集中清理出口；malloc 用 `sizeof(*p)`；create/destroy 成对
- [ ] 无 strcpy/strcat/sprintf 新增；外部长度参与的拷贝有上界检查
- [ ] 无有符号/无符号混合比较告警；定宽类型用于协议/寄存器
- [ ] 新增宏有必要性；函数宏满足括号 + do-while(0)，或已改 static inline
- [ ] 头文件自包含、最小暴露、内部结构不透明
- [ ] 错误约定全模块一致；失败路径出参状态符合契约
- [ ] 编译零新增警告；静态分析新增项闭环
