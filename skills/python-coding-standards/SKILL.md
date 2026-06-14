---
name: python-coding-standards
description: 在编写、修改或评审 Python 代码（模块、包、pytest 测试、pyproject 配置）时使用。提供可变默认参数、类型注解、异常与 EAFP、资源管理、相等与身份、数据容器、导入与 PEP 8 命名、并发的具体规则与正反例。静态类型语言规则见对应语言技能。
---

# Python Coding Standards

## 总览

Python 的核心危险是**动态与隐式：错误延迟到运行期才暴露，可变共享状态在背后累积**。本技能在 `devflow-clean-code` 的通用标准之上叠加 Python（3.9+）语言规则，不能替代通用 clean-code 自检；每条规则针对一类真实事故（跨调用状态污染、运行期类型错误、被吞异常、资源泄漏、身份/相等混淆）。项目声明了 PEP 8 / 团队规范子集时以项目为准，本文是未声明时的默认底线。

## 可变默认参数与共享可变状态

默认参数在函数定义时求值一次，可变默认值会在调用间累积——经典事故：

```python
# ❌ 同一个 list 被所有调用共享，跨调用累积
def append_to(item, items=[]):
    items.append(item)
    return items

# ✅ 用 None 哨兵，每次新建
def append_to(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

- 默认参数只用不可变值（`None`、数字、字符串、元组）
- 类属性上的可变容器会被所有实例共享；实例级可变状态在 `__init__` 里创建，或用 `dataclass` 的 `field(default_factory=list)`
- 不可变数据用元组 / `frozenset` / `frozen=True` 的 dataclass 表达，避免别名修改

## 类型注解

注解是给 mypy 和读者的契约，缺失时类型错误拖到运行期：

```python
# ❌ 无注解，参数与返回类型靠猜，IDE/mypy 无法检查
def process(user_id, data, active=True):
    ...

# ✅ 公共函数签名全注解；3.9+ 用内置泛型，可缺失值用 | None
def process(user_id: str, data: dict[str, Any], active: bool = True) -> User | None:
    ...
```

- 公共函数 / 方法签名必须注解参数与返回值；`mypy`（或 pyright）在 CI 校验
- 不用裸 `Any` 逃避类型检查；确实动态时用 `object` 或 `Protocol` 表达约束
- 接口约束优先用 `typing.Protocol`（结构化鸭子类型）而非继承

## 异常与 EAFP

Python 偏好 EAFP（先做再处理异常）而非过度前置检查；但捕获必须精确：

```python
# ❌ 裸 except 吞掉一切（含 KeyboardInterrupt/SystemExit），掩盖 bug
try:
    risky()
except:
    pass

# ✅ 捕获具体异常；包装时用 from 保留异常链
try:
    return Config.from_json(read(path))
except FileNotFoundError as e:
    raise ConfigError(f"config not found: {path}") from e
except json.JSONDecodeError as e:
    raise ConfigError(f"invalid JSON: {path}") from e
```

- 不写裸 `except:` 或 `except Exception: pass`；捕获最具体的异常
- 重新抛出包装异常时用 `raise NewError(...) from e` 保留 traceback
- 自定义异常建一个应用根类（`class AppError(Exception)`）再派生，便于边界统一捕获
- 不用异常做正常控制流的高频路径（性能与可读性）

## 资源管理

```python
# ❌ 手动 open/close：异常时漏关
f = open(path)
data = f.read()
f.close()

# ✅ with 上下文管理器，异常路径也释放
with open(path) as f:
    data = f.read()
```

- 文件、锁、连接、事务一律用 `with`；多个资源用嵌套或 `with a, b:`
- 自定义资源实现 `__enter__`/`__exit__`，或用 `@contextlib.contextmanager`；`__exit__` 返回 falsy（不吞异常，除非有意）

## 相等与身份

```python
# ❌ 用 == 比较 None / 用 is 比较值
if value == None: ...
if name is "admin": ...   # 字符串驻留是实现细节，不可靠

# ✅ is 只用于 None 和单例；== 用于值比较
if value is None: ...
if name == "admin": ...
```

- `is`/`is not` 只用于 `None`、`True`/`False` 单例的判定；其余值比较用 `==`
- 类型判定用 `isinstance(x, T)`，不用 `type(x) == T`（破坏子类与多态）
- 作为 dict key / set 元素的对象必须可哈希且不可变

## 数据容器

```python
# ❌ 用裸 dict/tuple 在层间传业务对象，字段靠约定，拼写错误静默
user = {"id": "1", "naem": "Alice"}   # 拼错 key 不报错

# ✅ dataclass：字段、类型、__init__/__repr__/__eq__ 自动且受检
from dataclasses import dataclass

@dataclass(frozen=True)
class User:
    id: str
    name: str
    is_active: bool = True
```

- 多字段业务对象用 `@dataclass`（不可变用 `frozen=True`）或 `NamedTuple`，不用裸 dict/tuple 传递
- dataclass 可变默认用 `field(default_factory=...)`，不用裸 `[]`/`{}`
- 热路径上字段固定的小对象用 `__slots__` 降内存（也防止意外加属性）

## 导入与 PEP 8 命名

PEP 8 的命名与导入是 Python 的语言特化规则（不是通用 clean-code）：

```python
# ❌ 通配导入污染命名空间、遮蔽名字、破坏静态分析
from os.path import *

# ✅ 显式导入；顺序：标准库 → 第三方 → 本地，各组间空行
import json
from pathlib import Path

import requests

from mypackage.models import User
```

- 不用 `from module import *`（`__init__.py` 的受控 re-export 除外，且配 `__all__`）
- 命名：`snake_case`（函数/变量/模块）、`PascalCase`（类）、`UPPER_SNAKE_CASE`（常量）
- 导入排序由 `isort`/`ruff` 自动维护；不在函数内部隐藏顶层依赖（循环依赖除外，且注明）

## 并发

GIL 决定了选型：选错模型 = 白忙：

```python
# ❌ 在 async 协程里做阻塞调用，阻塞整个事件循环
async def handler():
    data = requests.get(url).text   # 同步阻塞

# ✅ async 路径全程 await 非阻塞 IO
async def handler():
    async with aiohttp.ClientSession() as s, s.get(url) as r:
        data = await r.text()
```

- IO 密集：`asyncio` 或 `ThreadPoolExecutor`；CPU 密集：`ProcessPoolExecutor`/多进程（线程受 GIL 限制无法并行算）
- 不在 `async` 函数里调用同步阻塞 IO；阻塞调用放线程池（`loop.run_in_executor`）
- 跨线程共享可变状态加锁；`concurrent.futures` 收集结果时处理每个 future 的异常

## 工具链

- 格式化：`black`（或 `ruff format`）；导入：`isort` / `ruff`；行宽随项目（默认 88）
- 静态检查：`ruff check`（含 pyflakes/pycodestyle/isort 规则集）；类型：`mypy`（趋向 `--strict`，至少 `disallow_untyped_defs`）；安全：`bandit`、依赖 `pip-audit`
- 新增 lint / 类型告警必须修复或带理由 + 范围抑制（`# noqa: CODE 理由` / `# type: ignore[code]`），"历史就有"不豁免本次触碰的文件
- 测试：`pytest`（+ `pytest-cov`）；fixture 管理资源，参数化覆盖边界；无隐藏 `time.sleep`
- 配置集中在 `pyproject.toml`（`[tool.ruff]`/`[tool.mypy]`/`[tool.pytest.ini_options]`）

## 自检清单

- [ ] 无可变默认参数；类级可变容器未被实例共享
- [ ] 公共签名有类型注解；无裸 `Any` 逃避；mypy 通过
- [ ] 无裸 `except` / `except: pass`；包装异常用 `from`；捕获具体类型
- [ ] 文件/锁/连接用 `with`；自定义资源实现上下文管理协议
- [ ] `is` 仅用于 None/单例；值比较用 `==`；类型判定用 `isinstance`
- [ ] 业务对象用 dataclass/NamedTuple；可变默认用 `default_factory`
- [ ] 无 `import *`；命名符合 PEP 8；导入分组有序
- [ ] 并发模型与负载匹配；async 路径无阻塞调用
- [ ] ruff/mypy 零新增告警；抑制带理由
