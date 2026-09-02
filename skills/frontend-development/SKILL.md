---
name: frontend-development
description: 在前端/Web UI 工作项（组件、页面、组件架构、状态管理、数据获取、前后端集成与 API 客户端层、表单、交互、样式与响应式、动效、可访问性、前端性能）的规格、设计、实现或评审中使用，涉及组件边界与组合、渲染与状态归属、加载/错误/空态、API 客户端与错误归一、设计令牌与响应式、动效性能、性能预算、a11y、客户端安全边界时。只承载客户端/UI 领域约束；服务端 API、持久化或其他相邻领域规则由命中 description 的领域技能叠加，语言级规则见适用 `<language>-coding-standards`。
---

# Frontend Development

## 总览

前端约束的共同点：**违反时不报错，只让用户体验间歇性地坏**——白屏、卡顿、无障碍用户用不了、状态对不上、样式漂移、动画掉帧。所以这些约束必须前置到规格和设计：在 spec 里有交互态与性能阈值、在 design 里有组件边界、状态归属、集成契约与可访问性策略、在测试里有证据，而不是在 code review 时靠肉眼发现。本技能按维度给出"在哪个阶段定什么、实现红线、用什么证据"，每条红线尽量配最小正反例；详表与扩展模式见末尾参考。语言/框架的写法规则见适用语言技能，本文只承载前端领域维度。

> 维度速览：[组件架构与边界](#组件架构与边界) · [状态与渲染](#状态与渲染) · [数据获取与四态](#数据获取与四态) · [前后端集成与-api-客户端层](#前后端集成与-api-客户端层) · [性能预算](#性能预算) · [动效与运动性能](#动效与运动性能) · [可访问性a11y](#可访问性a11y) · [表单与校验](#表单与校验) · [样式与响应式](#样式与响应式) · [错误隔离与客户端安全](#错误隔离与客户端安全)

## 组件架构与边界

- **设计定**：组件职责划分（展示型 vs 容器/数据型）；客户端交互边界尽量下沉到叶子（服务端渲染框架下 `"use client"` 只包裹真正需要交互的最小子树）；跨层数据传递用组合/上下文而非深层 props 透传；业务逻辑抽到 hooks/纯函数。
- **实现红线**：单组件单一职责，渲染与数据获取/业务规则分离（自定义 hook 或 lib）；交互边界最小化，不把整页标成客户端组件；避免 3 层以上 prop drilling，用组合或 context；组件对外契约（props）稳定、类型完整，不漏 default/可选语义。

```tsx
// ❌ 巨型组件：取数 + 业务 + 渲染全混，且整页 "use client"
"use client";
export default function Page() {
  const [data, setData] = useState();
  useEffect(() => { /* fetch + 业务计算 */ }, []);
  return <div>{/* 几百行 JSX */}</div>;
}

// ✅ 数据/业务进 hook，交互下沉到叶子，页面保持服务端渲染
function useOrders() { /* 取数 + 四态 + 派生值 */ }      // 可独立单测
export default function Page() { return <OrdersView />; } // 服务端组件
// OrdersView 内仅把需要交互的按钮做成 "use client" 叶子
```

- **证据**：hook/纯函数的单测不依赖渲染即可跑；组件测试聚焦渲染与交互契约。组合、边界下沉、状态就近的模式见 [`references/component-and-integration.md`](references/component-and-integration.md)。

## 状态与渲染

- **设计定**：每块状态的**归属**——本地组件态、跨组件共享态、还是服务器数据缓存；单一数据源，派生值就地计算不另存。
- **实现红线**：状态更新不可变；渲染期是纯函数（不在渲染中发请求/改外部变量/读写 DOM，副作用进受控 effect）；effect 依赖完整且引用稳定；列表项有稳定且唯一的 key。

```tsx
// ❌ 就地变异 state + 用数组下标当可变列表的 key + effect 漏依赖
state.items.push(next);           // 变异，React 不重渲染
setActive(state.items);
{items.map((it, i) => <Row key={i} {...it} />)}   // 重排后 key 错位
useEffect(() => { load(id); }, []);                // 漏 id：陈旧闭包

// ✅ 不可变更新 + 稳定唯一 key + 完整依赖
setItems(prev => [...prev, next]);
{items.map(it => <Row key={it.id} {...it} />)}
useEffect(() => { load(id); }, [id]);
```

- **证据**：组件单测覆盖状态转换与边界；对易回归的重渲染问题有断言或快照。

## 数据获取与四态

- **设计定**：每个异步数据源的 **loading / error / empty / success** 四态各有明确 UI；缓存与失效策略；竞态处理（过期响应丢弃）。
- **实现红线**：每个请求都处理 error 与 loading，不只画 success；切换参数时丢弃过期响应；不产生无限请求循环；不在渲染期直接 fetch。

```tsx
// ❌ 只画 success；快速切换 id 时后到的旧响应覆盖新数据
const { data } = useQuery(id);
return <List items={data} />;

// ✅ 四态都画 + 丢弃过期响应
useEffect(() => {
  let active = true;                       // 或用 AbortController
  setState({ status: 'loading' });
  fetchById(id)
    .then(d => active && setState({ status: 'success', data: d }))
    .catch(e => active && setState({ status: 'error', error: e }));
  return () => { active = false; };        // 旧请求结果被忽略
}, [id]);
if (state.status === 'loading') return <Spinner />;
if (state.status === 'error')   return <ErrorView onRetry={refetch} />;
if (isEmpty(state.data))        return <Empty />;
return <List items={state.data} />;
```

- **证据**：四态各有测试（含错误与空数据）；竞态/取消路径有覆盖。

## 前后端集成与 API 客户端层

- **设计定**：统一 API 客户端层（基址来自环境变量、统一附带鉴权、统一错误归一）；前后端类型共享或由契约生成（OpenAPI/tRPC/codegen）；错误码→用户文案映射；401 刷新/跳登录、5xx 重试策略归一在客户端层。
- **实现红线**：不在组件里散写 `fetch` 拼绝对 URL；基址走环境变量不硬编码；鉴权令牌集中注入，不在每个调用手拼 header；把后端错误映射成用户可读文案，不把原始报错/堆栈丢给用户；只对 5xx 重试，4xx 不重试；客户端类型与后端契约一致，不手抄两份（易漂移）。

```ts
// ❌ 组件里硬编码 URL + 裸 fetch + 把原始错误抛给用户
const r = await fetch('http://10.0.0.1:3000/api/orders');
if (!r.ok) throw new Error(await r.text());   // 用户看到 "NullPointerException"

// ✅ 统一客户端层：env 基址 + 注入令牌 + 错误归一
const orders = await api.get<Order[]>('/orders');   // 基址/令牌/错误都在 api 内统一
// api 内：4xx → 映射文案不重试；5xx → 退避重试；401 → 刷新或跳登录
```

- **证据**：API 客户端层的错误映射/重试/401 处理有单测；契约/类型一致性由 codegen 或契约测试保证，服务端侧契约由适用的 API/服务端领域技能覆盖。客户端层结构、错误码→文案映射表、类型一致性方案见 [`references/component-and-integration.md`](references/component-and-integration.md)。

## 性能预算

- **规格定**：关键交互的性能阈值（QAS 格式，见 `devflow-specify`）——首屏（LCP）、交互延迟（INP）、布局稳定（CLS），含测量环境与百分位。
- **设计定**：长列表虚拟化、路由级代码分割与懒加载、昂贵计算与子树的记忆化策略；首屏关键资源与非关键资源拆分。
- **实现红线**：大列表虚拟化渲染；昂贵纯计算 memo、稳定回调记忆化；懒加载重组件并提供占位骨架；不把大同步计算放进渲染路径。
- **证据**：Lighthouse / Web Vitals 实测对照阈值；bundle 体积报告；必要时渲染次数/火焰图。

## 动效与运动性能

- **设计定**：动效强度与场景（仅过渡、滚动叙事、3D/WebGL）、降级策略；尊重 `prefers-reduced-motion` 写进设计输入而非事后补。
- **实现红线**：只动 GPU 友好属性（`transform`/`opacity`/`filter`），不动 `width/height/top/left/margin`（触发重排掉帧）；尊重 `prefers-reduced-motion`，提供减弱/关闭路径；动画订阅（观察器/timeline/RAF/事件）在 effect 清理中注销；持续动画隔离在 memo 叶子组件，重动画库懒加载。

```tsx
// ❌ 动 layout 属性 + 漏清理 + 无视减动偏好
el.style.left = x + 'px';                                 // 改 left → 重排掉帧
useEffect(() => { window.addEventListener('scroll', onScroll); }, []);  // 漏清理

// ✅ 动 transform + 清理 + 尊重减动偏好
el.style.transform = `translateX(${x}px)`;
useEffect(() => {
  window.addEventListener('scroll', onScroll);
  return () => window.removeEventListener('scroll', onScroll);   // 清理订阅
}, []);
// CSS: @media (prefers-reduced-motion: reduce) { 关闭/减弱动画 }
```

- **证据**：减动偏好下的降级有验证；effect 清理有覆盖；帧率/重排相关问题的性能证据见「性能预算」维度。GPU 属性、reduced-motion、清理与隔离详见 [`references/styling-and-motion.md`](references/styling-and-motion.md)。

## 可访问性（a11y）

- **设计定**：语义化 HTML、键盘可达、焦点管理是**设计输入**而非上线前补丁；目标合规级别（如 WCAG AA）写进 spec。
- **实现红线**：交互元素用语义标签；表单控件与 label 配对、错误可被屏幕阅读器感知；模态做焦点陷阱与恢复；`aria-*` 用对、不与原生语义冲突；纯装饰图 `alt=""`。

```tsx
// ❌ div 当按钮（键盘/读屏用不了）+ label 未关联 + 错误是游离文本
<div className="btn" onClick={submit}>Save</div>
<label>Email</label><input type="email" />
<span className="error">Invalid email</span>

// ✅ 语义按钮 + label/htmlFor 配对 + aria 关联错误
<button type="button" onClick={submit}>Save</button>
<label htmlFor="email">Email</label>
<input id="email" type="email" aria-invalid={!!err} aria-describedby="email-err" />
{err && <span id="email-err" role="alert">{err}</span>}
```

- **证据**：axe / eslint-plugin-jsx-a11y 零新增违规；关键流程键盘走查；必要时屏幕阅读器抽查。

## 表单与校验

- **设计定**：字段校验规则、提交态（pending/disabled）、错误展示位置与时机。
- **实现红线**：受控输入有单一数据源；提交期间禁用按钮防重复提交；**客户端校验只为体验，不替代服务端校验**（安全与权威校验由适用的服务端/API 领域技能覆盖）。
- **证据**：校验分支（合法/非法/边界）有测试；重复提交被阻止有覆盖。

## 样式与响应式

- **设计定**：设计令牌（颜色/间距/字号/圆角/阴影）单一来源（主题/变量），组件引用令牌而非散写魔法字面量；断点与移动优先策略；暗色/高对比经令牌切换；安全区与视口处理。
- **实现红线**：颜色/间距等用主题令牌或既定比例尺，不在各处散写魔法值（导致风格漂移、暗色漏改）；布局响应式且移动端不溢出（用动态视口而非写死 `100vh`，用网格/弹性而非百分比硬算）；触控目标尺寸达标；不靠像素级绝对定位硬怼布局。

```tsx
// ❌ 魔法色值/间距散写 + 写死视口高 —— 风格漂移、暗色漏改、移动端溢出
<div style={{ color: '#3b3b3b', padding: '13px', height: '100vh' }} />

// ✅ 令牌 + 比例尺 + 动态视口（暗色随令牌自动生效）
<div className="text-foreground p-4 min-h-[100dvh]" />
```

- **证据**：关键断点（移动/平板/桌面）有视觉或快照检查；令牌使用一致（评审项：无散落魔法色值）。令牌体系、断点与暗色方案见 [`references/styling-and-motion.md`](references/styling-and-motion.md)。

## 错误隔离与客户端安全

- **设计定**：错误边界（error boundary）包裹易错子树，单组件崩溃不白屏整页；降级 UI 是设计输出。
- **实现红线**：不把未净化内容塞进 `dangerouslySetInnerHTML`/`innerHTML`（XSS）；密钥/私密令牌不进前端 bundle；跳转/资源 URL 校验来源（防开放重定向与 `javascript:` 注入）。

```tsx
// ❌ 未净化的用户内容直接注入 DOM → 存储型 XSS
<div dangerouslySetInnerHTML={{ __html: comment.body }} />

// ✅ 默认转义渲染；确需富文本则先服务端/库净化（白名单）
<div>{comment.body}</div>
// 或 <div dangerouslySetInnerHTML={{ __html: sanitize(comment.body) }} />
```

- **证据**：错误边界触发路径有测试；安全相关项在评审清单逐条核对。

## 测试与证据策略

| 层级 | 覆盖什么 | 注意 |
|---|---|---|
| 组件/单测 | 状态转换、四态渲染、校验分支、a11y 属性 | 主力层；查询用可访问性角色（role/label）而非脆弱选择器 |
| 交互/集成 | 用户流程、键盘导航、焦点管理 | 用 Testing Library 风格按用户视角断言 |
| E2E / 视觉 | 关键路径、跨页状态、视觉回归 | 性能阈值与 Web Vitals 在接近生产的环境测 |

- 性能/可访问性类 NFR 不能只靠"开发机上看着挺快"——按声明环境与工具实测。
- 评审时（`devflow-review`）：本文件各维度的"证据"项即检查清单；适用维度无证据且无 N/A 理由 → critical。

## 合理化反驳

| 话术 | 现实 |
|---|---|
| 「先把 success 画出来，加载和错误态后面补」 | 四态是设计输入；缺 error/empty 态是最常见的线上体验事故 |
| 「一个组件写完整页省事」 | 巨型组件 + 整页 client 化不可测、丢失 SSR；职责拆分、交互边界下沉 |
| 「组件里直接 fetch 拼 URL 最直接」 | 散写 fetch/硬编码 URL 难维护、漏鉴权与错误处理；统一 API 客户端层 |
| 「错误把后端 message 直接显示就行」 | 原始报错/堆栈对用户无意义且泄漏内部；映射成可读文案 |
| 「div 加 onClick 也能点，效果一样」 | 键盘与屏幕阅读器用不了；交互元素用语义标签是红线 |
| 「颜色先写死，主题以后再说」 | 散写魔法色值导致风格漂移、暗色漏改；从令牌取色 |
| 「动画动 left/top 也能动起来」 | 改 layout 属性触发重排掉帧；只动 transform/opacity 并尊重减动偏好 |
| 「客户端校验过了就行，省一次请求」 | 客户端校验可被绕过；服务端才是权威校验 |
| 「性能等上线慢了再优化」 | 性能阈值是 spec 输入；虚拟化/分割是设计决策，不是事后补丁 |
| 「依赖数组少写一个，反正能跑」 | 依赖不全会导致陈旧闭包或无限重渲染；依赖完整且引用稳定 |

## 自检清单

- [ ] 组件单一职责；渲染与取数/业务分离（hook/lib）；交互边界下沉；无 3 层以上 prop drilling
- [ ] 状态归属明确、单一数据源；更新不可变；列表 key 稳定唯一；effect 依赖完整
- [ ] loading/error/empty/success 四态都有 UI；过期响应被丢弃；无无限请求循环
- [ ] 统一 API 客户端层：env 基址、集中注入令牌、错误归一映射文案、5xx 才重试；类型与后端契约一致
- [ ] 性能阈值有 QAS；长列表虚拟化、重组件懒加载、昂贵计算记忆化；有 Web Vitals 证据
- [ ] 动效只动 GPU 属性；尊重 `prefers-reduced-motion`；动画订阅有清理；持续动画隔离/重库懒加载
- [ ] 交互用语义标签；label/控件配对、错误用 aria 关联；模态焦点陷阱与恢复；axe/jsx-a11y 零新增违规
- [ ] 受控输入单一数据源；提交防重复；客户端校验未替代服务端校验
- [ ] 颜色/间距用令牌或比例尺，无散落魔法值；响应式移动端不溢出；暗色经令牌；触控目标达标
- [ ] 错误边界隔离易错子树；无未净化 `dangerouslySetInnerHTML`；密钥不入 bundle
- [ ] 适用层级（单测/集成/E2E）覆盖到位；环境相关 NFR 在声明环境测量

## 参考

| 需要… | 参考 |
|---|---|
| 组件组合与边界下沉、状态就近、自定义 hook 抽取、API 客户端层结构、错误码→文案映射、跨边界类型一致性 | [`references/component-and-integration.md`](references/component-and-integration.md) |
| 设计令牌体系、响应式断点与移动优先、暗色模式、动效 GPU 属性、reduced-motion、清理与隔离 | [`references/styling-and-motion.md`](references/styling-and-motion.md) |
