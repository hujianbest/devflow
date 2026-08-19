---
type: Repository
title: devflow 仓库中的 order-service fixture 范围
description: order-service 输入是 devflow 仓库内的四文件分析范围，不是独立 Git 仓库。
resource: "git+https://github.com/hujianbest/devflow.git@440bf01d2ea2f0b65813790e0c1febcadf04410e#coding-skills/domain-knowledge-library/evals/fixtures/order-service"
tags: [repository, fixture, scope]
view: as-is
owner: unknown
sensitivity: internal
sources:
  - id: repo-devflow-order-service
    resource: "git+https://github.com/hujianbest/devflow.git@440bf01d2ea2f0b65813790e0c1febcadf04410e#coding-skills/domain-knowledge-library/evals/fixtures/order-service"
    title: devflow 中的 order-service fixture 范围
    role: implementation
    author: process:git
    last_modified: 2026-08-19
generated:
  by: domain-knowledge-library/static-analysis
  at: 2026-08-19T17:09:54Z
status: draft
stale_after: 2026-11-19
---

# 已观察事实

- 输入目录由 Git 仓库 `devflow` 的 revision `440bf01d2ea2f0b65813790e0c1febcadf04410e` 固定。[^repo-devflow-order-service]
- 该范围包含 4 个已跟踪文件：README、OpenAPI、Python 实现和 Python 测试。
- 当前范围没有未提交变更。

# 边界说明

该目录是 fixture 子目录，不能据此认定为独立 Repository、独立部署单元或团队所有权边界。系统页面中的 `order-service` Application 仅是由契约标题、实现类和目录组合提出的技术候选。

# 可重现性

来源登记保存每个文件的 SHA-256 与 Git blob id；详细值见 `.kb/source-registry.yaml` 和 `.kb/inventory/repository.json`。

[^repo-devflow-order-service]: Git revision 和路径范围；目录身份由 Git 索引静态检查得到。
