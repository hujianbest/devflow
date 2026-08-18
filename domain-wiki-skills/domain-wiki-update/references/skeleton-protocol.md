# 骨架协议

在写概念页之前，把计划展开成文件树。目标：覆盖盘点出的每个真实领域，而不是先写几页再把其余丢进 Backlog。

## 何时

- init 必做。
- update 的 completeness pass 必做。
- 普通外科 update 不做骨架。

## `_skeleton.md`

写在 `wiki/.discovery/_skeleton.md`：

```text
# 骨架

## 树
<拟建目录与文件，不含 index.md / log.md / INSTRUCTIONS.md>

## 页面
| 路径 | 职责（一行） | 证据锚点 | 连到 |
|---|---|---|---|
| quickstart.md | … | … | 每个主栏目 |
```

规则：

- 不要在 `wiki/` 里预建空 stub 文件。骨架只是计划。
- 现状路径和目标路径若不一致，在职责里分开写，不要画成已经实现。
- 单文件空目录先合并，不要为「结构完整」占坑。
- 达到 [coverage-gates.md](coverage-gates.md) 阈值的接口族、界面、命名流程必须在骨架里各占一行路径，禁止写成「见总览表格」。
- 子目录导航页叫 `index.md` 或栏目 `overview.md`，按 [wiki-contract.md](wiki-contract.md) 与 [page-types.md](page-types.md)。

## 覆盖评审

派 1 个只读子 agent，或主 agent 按清单自检。对照 `inventory.md` 与 `findings-*.md`，只回报缺口，不写概念页，不创建 `reviews/`。

必查：

1. 对照 coverage-gates：每个必拆单位是否有独立文件。被收成总览表的，记必改，不得标「已接受的合并」。
2. 是否把未提交、未完成的切片写成已发布。
3. 是否把文档里的过期路径当成当前树。
4. 是否漏掉组合根、适配器边界、安全/平台不变量、决策记录、共享契约、工具与运行入口。
5. 关系边是否在写页前就设计好（`源 -> 含义 -> 目标`），而不是写完再互链凑密度。

把结果写入 `.discovery/skeleton-review.md`：必改项 + 已接受的合并理由。只改骨架，再过一轮，不要循环评审。

必改项解决后才能开写概念页。

## 写完自检

每个骨架条目必须是独立文件。只有 coverage-gates 允许合并的项可以并进总览。缺一条就还没完成。
