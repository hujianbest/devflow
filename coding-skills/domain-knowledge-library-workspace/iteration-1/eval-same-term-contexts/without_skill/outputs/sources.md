# 证据索引

输入根目录：

```text
/workspace/coding-skills/domain-knowledge-library/evals/fixtures/same-term-contexts
```

| 来源 | 支持的知识 |
| --- | --- |
| `billing-service/README.md` | Billing Account 的台账语义、标识、余额、币种，以及 customer 可拥有多个账户 |
| `billing-service/src/account.py` | Billing Account 字段类型与 `can_charge` 的精确判断式 |
| `identity-service/README.md` | Identity Account 的认证主体语义、标识、登录凭据与启停状态，以及财务语义的明确排除 |
| `identity-service/src/account.py` | Identity Account 字段类型与 `can_authenticate` 的精确判断方式 |

## 证据使用规则

- 服务说明用于解释领域意图。
- 代码用于记录当前可观察的数据结构和行为。
- 说明与代码未覆盖的内容标为“未知”或“待确认”。
- 同名类只有在上下文和语义证据都支持时才可视为同一概念；本输入不满足该条件。
