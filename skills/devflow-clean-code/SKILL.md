---
name: devflow-clean-code
description: 在编写、修改或重构任何实现代码与测试代码时使用；也在代码评审需要内在质量判据、或发现命名混乱/函数过长/嵌套过深/错误处理散乱等代码异味时使用。语言无关的整洁代码标准；语言细则见对应的 <language>-coding-standards 技能（如 c-coding-standards、cpp-coding-standards）。
---

# DevFlow Clean Code（第三层）

## 总览

前两层保证代码做对的事、被证明做对；这一层保证代码本身写得好。判断标准只有一个视角：**下一个读者**（评审者、半年后的维护者、也包括下一轮迭代的 AI）。代码是写给人读的，顺便能在机器上运行。

人能持续低成本地审查 AI 的产出（human-on-the-loop 能成立），靠的就是这一层。所以"整洁"不是美学偏好，是协作姿态的前提。

本文是语言无关的标准；语言细则在对应的 `<language>-coding-standards` 技能（现有 `c-coding-standards` / `cpp-coding-standards`，可按同一契约扩展）。示例用 C/C++ 写，原则通用。

## 命名

名字是最廉价的文档。规则：

| 对象 | 规则 | 反例 → 正例 |
|---|---|---|
| 函数 | 动词开头，说出做什么或返回什么 | `process()` → `discard_expired_sessions()` |
| 布尔 | is/has/can/should 开头，肯定语义 | `flag`, `not_ready` → `is_calibrated`, `has_pending_request` |
| 变量 | 名词，带足语义；作用域越大名字越长 | `d`, `tmp2` → `retry_delay_ms`, `merged_config` |
| 常量 | 说出含义而非值 | `TIMEOUT_3S` → `HANDSHAKE_TIMEOUT`（值变了名字不会说谎） |
| 带单位/语义的量 | 单位进名字或进类型 | `timeout` → `timeout_ms`；更好：`duration_ms_t timeout` |

判据：

- **名字撒谎是最高优先级的修复**：`get_config()` 里偷偷做了网络请求和缓存写入，比没有名字更糟。函数做的事超出名字 → 改名或拆函数。
- 同一概念全库一个词：别让 `fetch`/`load`/`read` 混用指同一件事。
- 名字里出现 `data`、`info`、`manager`、`util`、`process`、`handle` 而无修饰 → 几乎总能更具体。
- 需要注释解释名字含义 → 直接把解释写进名字。

## 函数

- **一个函数一件事，一层抽象**。函数体内不应同时出现"调用其他函数表达意图"和"操作位与指针的细节"两个层次——细节下沉成命名函数。
- 经验阈值（超出即审视，不是机械红线）：函数 ≤ 50 行；参数 ≤ 4 个；嵌套 ≤ 3 层。
- 参数结伴出现（同一组 3-4 个参数在多个签名里重复）→ 提取结构体。
- 输出参数能用返回值就用返回值；布尔参数改变函数行为（`render(true)`）→ 拆成两个名字明确的函数。

**怎么拆长函数**：找出函数里的"段落"（通常已有空行或注释分隔），每个段落提取为一个以意图命名的函数。注释 `// validate input` + 十行代码 → `validate_input()`，注释删掉。

```c
/* ❌ 三个抽象层次挤在一起 */
int config_apply(const uint8_t *blob, size_t len) {
    if (blob == NULL || len < 8) return ERR_INVALID_ARG;
    uint32_t crc = 0xFFFFFFFF;                      /* 细节：CRC 计算 */
    for (size_t i = 0; i < len - 4; i++) { crc = crc32_step(crc, blob[i]); }
    if (crc != read_le32(blob + len - 4)) return ERR_CRC;
    ...30 行解析字段...
    ...20 行逐项生效与回滚...
}

/* ✅ 每层一个函数，主函数读起来就是流程本身 */
int config_apply(const uint8_t *blob, size_t len) {
    int rc = config_verify_integrity(blob, len);
    if (rc != OK) return rc;

    parsed_config_t parsed;
    rc = config_parse(blob, len, &parsed);
    if (rc != OK) return rc;

    return config_commit(&parsed);
}
```

## 控制流

让主路径（happy path）保持在最低缩进层级，异常分支尽早离开：

```c
/* ❌ 主逻辑埋在三层嵌套里 */
int session_send(session_t *s, const msg_t *m) {
    if (s != NULL) {
        if (s->state == SESSION_OPEN) {
            if (msg_is_valid(m)) {
                /* 真正的发送逻辑，缩进三层 */
            } else { return ERR_INVALID_ARG; }
        } else { return ERR_BAD_STATE; }
    } else { return ERR_INVALID_ARG; }
}

/* ✅ 卫语句：前置检查依次出场，主逻辑零缩进 */
int session_send(session_t *s, const msg_t *m) {
    if (s == NULL) return ERR_INVALID_ARG;
    if (s->state != SESSION_OPEN) return ERR_BAD_STATE;
    if (!msg_is_valid(m)) return ERR_INVALID_ARG;

    /* 真正的发送逻辑 */
}
```

- 条件复杂到需要思考 → 提取为命名的谓词函数或解释变量：`if (is_retryable(err) && attempts < MAX_RETRIES)`。
- 同一个标志变量控制后面多段逻辑的开关 → 通常应拆成两条直线路径。
- 魔法数字/字符串一律命名常量；`if (mode == 3)` 在评审中按 important 处理。

## 错误处理写法

设计层定了错误模型（`devflow-design`），编码层的纪律：

- **检查每个可失败调用**。忽略返回值必须显式且有理由：`(void)log_write(...);  /* 日志失败不影响主路径 */`
- **错误处理不喧宾夺主**：用卫语句/早返回让错误路径短促清晰，主路径保持直线。
- **失败时资源必须回收**。C 的多资源获取用集中清理出口（goto cleanup 模式，见 `c-coding-standards`）；C++ 用 RAII（见 `cpp-coding-standards`）。
- **不吞错误**：捕获/拦截了错误就必须处理（恢复、降级、上报）之一；空的 catch / 只打日志然后当没发生，按 critical 处理。
- 错误信息带上下文：报「config block 3 CRC mismatch (got 0x1A2B, want 0x3C4D)」而不是「verify failed」。

## 注释

注释解释**为什么**，代码说明**是什么**。

```c
/* ❌ 复述代码 */
i++;  /* i 加一 */

/* ✅ 解释代码说不出的约束、取舍、外部事实 */
/* 先写数据后写索引：掉电时宁可丢这条记录，不可指向垃圾数据 */
record_write(slot, &data);
index_update(slot);
```

值得写注释的场景：非显然的不变量与前置条件、为绕过硬件/第三方缺陷的奇怪写法（带 issue 链接）、有意为之的"看似低效"、并发约束（"只能在任务上下文调用"）。

不写的：版本历史（git 的事）、注释掉的代码（删，git 里有）、段落标题式注释（提取函数代替）、TODO 不带负责人和去向（要么登记成债务，要么删）。

## 重复与死代码

- **三次法则**：第二次复制可以容忍（标记），第三次必须提取。但**只提取真正相同的知识**——两段代码长得像但服务不同业务规则、会因不同理由变化，提取反而制造耦合（错误的抽象比重复更贵）。
- 死代码零容忍：不可达分支、未使用变量/函数/参数、永远为真的条件、"以防万一"保留的旧实现——删。版本控制就是你的"以防万一"。
- 僵尸兼容层（`#if 0`、`legacy_` 前缀但无调用方、deprecated 但无下线计划）：登记并删除或给出下线计划。

## 范围与提交纪律

- **一个 diff 一个目的**：行为变更、重构、格式化分开提交。评审者无法在 500 行混合 diff 里分辨哪个变化是有意的。
- 只改任务要求改的。路过发现的问题：登记（issue / tasks.md 债务节），不顺手修。
- **童子军规则的边界**：触碰范围内的小清理（改个错字命名、删几行死代码）值得做且随手做；超出触碰范围、或清理本身值得独立评审 → 登记。
- 不删不理解的代码、不"顺手统一"无关文件的风格。

## 常见异味与重构手法

完整目录（识别特征 + 操作步骤 + before/after）见 `references/refactoring-catalog.md`。速查：

| 异味 | 识别 | 手法 |
|---|---|---|
| 长函数 | 一屏放不下 / 多个段落注释 | Extract Function（按意图段落拆） |
| 深嵌套 | ≥3 层缩进 | 卫语句 / 提取谓词 / 反转条件 |
| 魔法数 | 裸字面量参与逻辑 | 命名常量（说含义不说值） |
| 数据泥团 | 参数组在多个签名重复 | 提取结构体 |
| 特性依恋 | 函数大量操作别的模块的数据 | Move Function 到数据所在地 |
| 霰弹式修改 | 一个行为变更要改 N 个文件 | 按变化理由重新聚合（回 `devflow-design`） |
| 开关参数 | 布尔参数改变函数行为 | 拆成两个函数 |
| 注释补丁 | 注释解释一段代码在干嘛 | 提取函数，注释变函数名 |

重构永远在绿灯上进行、小步、每步跑测试（纪律见 `devflow-tdd` 的 REFACTOR 节）。

## 合理化反驳

| 话术 | 现实 |
|---|---|
| 「这个命名我自己懂」 | 代码是给下一个读者写的；"自己懂"的名字两周后你自己也不懂 |
| 「先跑起来，以后再清理」 | "以后"不存在。REFACTOR 是循环的一部分，不是可选附录 |
| 「多留个参数/分支，以后可能用」 | 死代码 + 假想需求。YAGNI；要用的时候再加，git 会帮你记住一切 |
| 「注释写多点总没错」 | 复述代码的注释会腐烂成谎言；该改的是代码的表达力 |
| 「顺手把旁边的也改了」 | 范围扩张让 diff 不可审。登记，另开任务 |
| 「这段复制一下改两行就行」 | 第三次复制时逻辑已经悄悄分叉。检查是不是同一个知识点 |

## 自检清单（提交前）

- [ ] 所有新名字：函数名说出全部行为；布尔肯定语义；量有单位
- [ ] 没有函数 >50 行、>4 参数、>3 层嵌套而无登记的理由
- [ ] 主路径零/低缩进；错误路径早返回；无裸魔法数
- [ ] 每个可失败调用被处理或显式注明忽略理由；失败路径资源回收
- [ ] 无注释掉的代码、无未使用符号、无复述型注释
- [ ] diff 单一目的；范围内无未登记的顺手修改
- [ ] 适用语言的 `<language>-coding-standards` 细则已过

## 支撑参考

| 文件 | 用途 |
|---|---|
| `references/refactoring-catalog.md` | 常见异味的识别特征、重构步骤与完整 before/after |
