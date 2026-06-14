---
name: frontend-development
description: 在前端/Web UI 工作项（组件、页面、状态管理、数据获取、表单、交互、可访问性、前端性能）的规格、设计、实现或评审中使用，涉及渲染与状态归属、加载/错误/空态、性能预算、a11y、客户端安全边界时。服务端 API 契约与持久化见 backend-development；语言级规则见适用 `<language>-coding-standards`。
---

# Frontend Development

## 总览

前端约束的共同点：**违反时不报错，只让用户体验间歇性地坏**——白屏、卡顿、无障碍用户用不了、状态对不上。所以这些约束必须前置到规格和设计：在 spec 里有交互态与性能阈值、在 design 里有状态归属与可访问性策略、在测试里有证据，而不是在 code review 时靠肉眼发现。本技能按维度给出"在哪个阶段定什么、实现红线、用什么证据"，每条红线尽量配最小正反例。语言/框架的写法规则见适用语言技能，本文只承载前端领域维度。

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

## 性能预算

- **规格定**：关键交互的性能阈值（QAS 格式，见 `devflow-specify`）——首屏（LCP）、交互延迟（INP）、布局稳定（CLS），含测量环境与百分位。
- **设计定**：长列表虚拟化、路由级代码分割与懒加载、昂贵计算与子树的记忆化策略；首屏关键资源与非关键资源拆分。
- **实现红线**：大列表虚拟化渲染；昂贵纯计算 memo、稳定回调记忆化；懒加载重组件并提供占位骨架；不把大同步计算放进渲染路径。
- **证据**：Lighthouse / Web Vitals 实测对照阈值；bundle 体积报告；必要时渲染次数/火焰图。

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
- **实现红线**：受控输入有单一数据源；提交期间禁用按钮防重复提交；**客户端校验只为体验，不替代服务端校验**（安全与权威校验在 `backend-development`）。
- **证据**：校验分支（合法/非法/边界）有测试；重复提交被阻止有覆盖。

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
| 「div 加 onClick 也能点，效果一样」 | 键盘与屏幕阅读器用不了；交互元素用语义标签是红线 |
| 「客户端校验过了就行，省一次请求」 | 客户端校验可被绕过；服务端才是权威校验 |
| 「性能等上线慢了再优化」 | 性能阈值是 spec 输入；虚拟化/分割是设计决策，不是事后补丁 |
| 「依赖数组少写一个，反正能跑」 | 依赖不全会导致陈旧闭包或无限重渲染；依赖完整且引用稳定 |

## 自检清单

- [ ] 状态归属明确、单一数据源；更新不可变；列表 key 稳定唯一；effect 依赖完整
- [ ] loading/error/empty/success 四态都有 UI；过期响应被丢弃；无无限请求循环
- [ ] 性能阈值有 QAS；长列表虚拟化、重组件懒加载、昂贵计算记忆化；有 Web Vitals 证据
- [ ] 交互用语义标签；label/控件配对、错误用 aria 关联；模态焦点陷阱与恢复；axe/jsx-a11y 零新增违规
- [ ] 受控输入单一数据源；提交防重复；客户端校验未替代服务端校验
- [ ] 错误边界隔离易错子树；无未净化 `dangerouslySetInnerHTML`；密钥不入 bundle
- [ ] 适用层级（单测/集成/E2E）覆盖到位；环境相关 NFR 在声明环境测量
