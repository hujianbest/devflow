---
name: backend-development
description: 在后端/服务端工作项（HTTP/REST/GraphQL API、服务与仓库层、数据库访问、缓存、鉴权、限流、后台任务、可观测性）的规格、设计、实现或评审中使用，涉及接口契约、数据一致性、幂等、认证授权、过载保护时。前端/UI 见 frontend-development；车载 SOA 服务的整车专属约束见 automotive-development；语言级规则见适用 `<language>-coding-standards`。
---

# Backend Development

## 总览

后端约束的共同点：**违反时单次请求看着正常，规模化和并发下才坏**——数据不一致、重复扣款、N+1 拖垮数据库、限流失效被打挂、错误被静默吞掉。所以这些约束必须前置到规格和设计：在 spec 里有接口契约与一致性要求、在 design 里有事务边界与幂等策略、在测试里有证据，而不是在压测或线上事故时才发现。本技能按维度给出"在哪个阶段定什么、实现红线、用什么证据"，每条红线尽量配最小正反例。语言写法见适用语言技能，本文只承载后端领域维度。

## API 契约

- **设计定**：资源命名与 URL 结构、HTTP 方法语义、状态码、统一错误信封、分页/过滤/排序约定、版本策略；接口是组件间契约，变更走 `devflow-specify` 的 IFR + 基线纪律，列出已知消费者与兼容策略。
- **实现红线**：状态码语义化（2xx 成功；400/422 校验、401 未认证、403 无权、404 不存在、409 冲突、429 限流；5xx 服务端错误）；错误响应统一信封且 5xx 不泄漏内部细节；破坏性变更走 `modify`。

```jsonc
// ❌ 一律 200，把失败塞进 body —— 破坏缓存/重试/监控语义
HTTP 200 { "success": false, "error": "not found" }
// 校验失败回 500 也是反模式

// ✅ 用 HTTP 状态码表达结果 + 稳定错误信封
HTTP 404 { "error": { "code": "market_not_found", "message": "Market not found" } }
HTTP 422 { "error": { "code": "validation_failed", "fields": { "name": "required" } } }
```

- **证据**：契约/快照测试或 OpenAPI 校验；状态码与错误信封有用例覆盖。

## 数据访问与一致性

- **设计定**：事务边界与隔离级别、N+1 规避策略、连接池上限、迁移的前后兼容与回滚。
- **实现红线**：多步写入在一个事务内（失败整体回滚）或有显式补偿；列表关联用批量取数消灭 N+1；查询只取需要的列且走索引；schema 迁移可回滚、分步发布。

```ts
// ❌ N+1：列表里逐行查关联 —— 数据量一大就拖垮 DB
const orders = await getOrders();
for (const o of orders) o.user = await getUser(o.userId);   // N 次查询

// ✅ 批量取 + 内存关联 —— 1 次查询
const orders = await getOrders();
const users = await getUsers(orders.map(o => o.userId));    // 1 次
const byId = new Map(users.map(u => [u.id, u]));
orders.forEach(o => { o.user = byId.get(o.userId); });
```

- **证据**：关键查询的执行计划/慢查询日志；事务回滚路径有测试；迁移在预生产演练。

## 幂等与并发

- **设计定**：写接口的幂等键、重试语义、乐观锁（版本号）或悲观锁的选型；超卖/重复扣减的防护点。
- **实现红线**：非幂等的副作用操作（支付、扣减库存、发消息）有幂等保护；不依赖"客户端不会重试"或"网络不会重复投递"。

```ts
// ❌ 无幂等保护：客户端重试/消息重投 → 重复扣款
async function charge(req) { await payments.create(req.amount); }

// ✅ 幂等键去重：同一 key 只生效一次
async function charge(req) {
  const existing = await payments.findByKey(req.idempotencyKey);
  if (existing) return existing;                       // 重试命中已有结果
  return payments.create({ ...req, key: req.idempotencyKey });  // 唯一约束兜底
}
```

- **证据**：重复请求/并发请求下的不变量测试（同一幂等键只生效一次）。

## 认证与授权

- **设计定**：认证机制（token/session）、权限模型（RBAC/ABAC）；授权检查在服务端**每个**入口，不只在 UI 隐藏入口。
- **实现红线**：不信任客户端声明的身份/角色/资源归属，服务端校验对象级权限；鉴权统一拦截不可绕过；密钥/token/PII 不进日志。

```ts
// ❌ 信任客户端传来的 role / 不校验资源归属 —— 越权
if (req.body.role === 'admin') return allOrders();          // 客户端可伪造
return getOrder(req.params.id);                              // 谁都能取别人的单

// ✅ 服务端权威身份 + 对象级授权
const user = await authenticate(req);                        // 从 token 解析
const order = await getOrder(req.params.id);
if (order.ownerId !== user.id && !user.isAdmin) throw new Forbidden();
```

- **证据**：未认证/越权用例返回正确状态码；权限矩阵有测试。安全敏感变更协同 `security-review`/团队安全负责人。

## 缓存与失效

- **设计定**：缓存层（HTTP/CDN/Redis/进程内）、TTL、失效路径、一致性容忍度（能容忍多旧）。
- **实现红线**：写路径同步失效或用短 TTL；**不**跨用户缓存与身份/权限相关的响应（缓存投毒/越权泄漏）；缓存击穿/雪崩有保护（单飞、随机 TTL）。
- **证据**：失效路径有测试；缓存命中/未命中行为一致（缓存只影响延迟不影响正确性）。

## 限流与过载保护

- **设计定**：限流维度（用户/IP/租户/接口）与配额、超额行为、过载时的降级策略。
- **实现红线**：生产限流用**共享存储**，不用进程内计数器；超额返回 `429` + `Retry-After`；关键依赖有超时与熔断。

```ts
// ❌ 进程内内存计数器：多副本各算各的、部署即重置、无服务器下失效
const hits = new Map<string, number>();
if ((hits.get(ip) ?? 0) > LIMIT) return res.status(429).end();

// ✅ 共享存储（Redis/网关/平台原生限流器）跨实例一致
const n = await redis.incr(`rl:${ip}`);
if (n === 1) await redis.expire(`rl:${ip}`, WINDOW);
if (n > LIMIT) return res.status(429).set('Retry-After', WINDOW).end();
```

- **证据**：限流在多实例下生效的验证；超时/熔断路径有测试。

## 可观测性

- **设计定**：结构化日志字段（含 request/trace id）、关键路径指标（延迟、错误率、吞吐）、告警阈值。
- **实现红线**：日志结构化且可关联（贯穿 request id）；错误记录足够定位的上下文，**不**静默吞异常；不在日志/指标里写敏感数据。
- **证据**：关键路径有日志/指标埋点；错误路径产生可观测信号。

## 测试与证据策略

| 层级 | 覆盖什么 | 注意 |
|---|---|---|
| 单元 | 业务逻辑、校验、错误映射、权限判定 | 主力层；外部依赖在边界处 mock |
| 集成 | 仓库/DB、事务回滚、缓存、迁移 | 用真实 DB（容器/Dev Services），不 mock 掉被测的持久化语义 |
| 契约/E2E | API 契约、鉴权、限流、幂等 | 在接近生产的环境验证并发与过载相关维度 |

- 一致性/幂等/限流类维度不能只靠单测充数——并发与多实例行为在集成/接近生产环境验证。
- 评审时（`devflow-review`）：本文件各维度的"证据"项即检查清单；适用维度无证据且无 N/A 理由 → critical。

## 合理化反驳

| 话术 | 现实 |
|---|---|
| 「统一返回 200，错误放 body 里前端好处理」 | 状态码是 HTTP 契约；200 包错误破坏缓存/重试/监控语义 |
| 「下游应该不会依赖这个错误码」 | 可观察的接口语义都有消费者；变更走基线 + 列消费者 |
| 「客户端不会重复提交，不用做幂等」 | 网络重试与重复投递必然发生；副作用操作必须幂等 |
| 「先放宽权限跑通，上线前收紧」 | 越权是高危事故；对象级鉴权从第一天起，且服务端权威 |
| 「限流用内存计数器够了」 | 多副本/无服务器下进程内计数器失效；用共享存储 |
| 「N+1 数据量小，先不管」 | 数据量会增长；N+1 是规模化下的典型拖垮点，设计阶段消灭 |

## 自检清单

- [ ] 状态码语义化、错误信封统一、5xx 不泄漏内部；接口变更走 modify + 列消费者
- [ ] 多步写入有事务/补偿；列表无 N+1；查询取需要的列且走索引；迁移可回滚
- [ ] 副作用写操作有幂等保护；不依赖"客户端不会重试"
- [ ] 身份与对象级授权服务端权威、不可绕过；密钥/PII 不入日志
- [ ] 缓存有失效路径；不跨用户缓存权限相关响应；有击穿/雪崩保护
- [ ] 生产限流用共享存储；超额回 429 + Retry-After；关键依赖有超时/熔断
- [ ] 日志结构化可关联、错误不被吞；关键路径有指标
- [ ] 适用层级（单元/集成/契约）覆盖到位；并发/过载维度在接近生产环境验证
