# Domain Knowledge Library

一套让 AI Agent 长期维护存量系统时"少猜错落点、不碰不变量、看清出处、记得昨天"的知识管理工作流。它把证据编译成可脱离代码仓独立发布的 OKF Bundle，供 Coding Agent 和 Design Agent 共同消费；Agent 记账，人只裁真假。

集合独立于 `skills/`，不依赖 DevFlow 交付链，也不写产品规格。

## 七个循环与落点

| 循环 | 触发 | 由谁执行 | 落在哪 |
|---|---|---|---|
| ① bootstrap 冷启动 | 还没有 Bundle | `domain-knowledge-maintain bootstrap` | Skill |
| ② consume 消费 | 任何设计或实现任务 | 任务 Agent | `using-domain-knowledge` + hooks（入口注入、draft 提醒） |
| ③ capture 回写 | 任务结束或发现矛盾 | 任务 Agent | `using-domain-knowledge` + hooks（stop 追问、写保护） |
| ④ ingest 摄入 | 新材料或新提案 | `domain-knowledge-maintain ingest` | Skill |
| ⑤ sync 跟代码 | Git 合并 | `domain-knowledge-maintain sync` | Skill（可接 CI） |
| ⑥ review 审核晋级 | review-queue 非空 | `domain-knowledge-maintain review` + `domain-knowledge-reviewer` | Skill + Agent |
| ⑦ audit 体检 | 每周或大批量之后 | `domain-knowledge-maintain audit` | Skill + `kb.py audit` |
| expand 深化 | 骨架不够且被明确请求 | `domain-knowledge-expand` | 可选 Skill |

## 目录

```text
domain-knowledge-library/
├── README.md
├── using-domain-knowledge/        # 任务时：怎么读、什么必须写回
├── domain-knowledge-maintain/     # 维护时：bootstrap / ingest / sync / review / audit
│   ├── references/bundle-contract.md   # 唯一的知识形态契约，其余文件都引用它
│   └── scripts/kb.py                   # 确定性校验、索引、盘点、审计、维护锁
├── domain-knowledge-expand/       # 可选：按风险深化指定模块
└── hooks/                         # Cursor 项目 hooks：入口注入、draft 提醒、写保护、回写追问
```

## 安装

Skills 与 commands 与 DevFlow 同一安装方式；hooks 装进消费 Bundle 的仓库：

```bash
# skills
cp -R domain-knowledge-library/using-domain-knowledge ~/.config/opencode/skills/
cp -R domain-knowledge-library/domain-knowledge-maintain ~/.config/opencode/skills/
cp -R domain-knowledge-library/domain-knowledge-expand ~/.config/opencode/skills/   # 可选
cp commands/domain-knowledge*.md ~/.config/opencode/commands/
cp agents/domain-knowledge-reviewer.md ~/.config/opencode/agents/

# hooks（在目标仓库根目录执行）
bash <devflow>/domain-knowledge-library/hooks/install.sh
```

Cursor 用户把三个 skill 目录放到 `.cursor/skills/` 或 `~/.cursor/skills/` 即可被发现。

## Bundle 在哪

hooks 与 `kb.py` 按以下顺序定位 Bundle 根：

1. 环境变量 `DOMAIN_KB_ROOT`；
2. 仓库根的 `.domain-kb` 指针文件（一行路径）；
3. 仓库根下的 `domain-kb/`；
4. 仓库根本身（存在 `knowledge/index.md` 时）。

Design Agent 不持有业务代码仓时，直接把 Bundle 仓库当工作区即可。

## 首次使用

```text
python3 domain-knowledge-maintain/scripts/kb.py init <bundle-root>
/domain-knowledge-maintain bootstrap --repo <code-repo>
```

之后任务 Agent 在 sessionStart 会收到瘦入口；读到 `draft` 会被提醒；任务结束若读过知识却没写提案，stop hook 会追问一次。
