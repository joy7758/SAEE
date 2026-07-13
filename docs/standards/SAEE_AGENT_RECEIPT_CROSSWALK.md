# SAEE 智能体收据语义 Crosswalk v0.1

## 范围与来源边界

本文是研究级语义分析，不是外部标准实现。本次任务没有访问外部网络，也没有逐条核对任何当前 Internet-Draft、RFC 或规范版本。文中的四类外部概念族来自任务提供的研究标签：

- Agent Audit Trail concepts（智能体审计轨迹概念）；
- Signed Action Receipt concepts（签名动作收据概念）；
- Human Authorization Evidence concepts（人类授权证据概念）；
- Agent Accountability Composition concepts（智能体问责组合概念）。

因此，本文只能使用“概念上对齐”“部分对齐”“范围不同”或“缺少映射”，不能使用“SAEE 实现了某标准”或“SAEE 已兼容某规范”。

当前状态固定为 `production_ready=false`；研究 crosswalk 不改变任何产品或运行时状态。

```text
Compatible ≠ Compliant
Mapping ≠ Standard Adoption
Analysis ≠ Certification
```

## 关系枚举

- `aligned`：本地 SAEE 概念与外部概念标签目标相近，但不表示协议兼容。
- `partially_aligned`：覆盖部分语义，仍缺真实性、互操作或外部验证材料。
- `different_scope`：概念相邻，但对象、摘要范围或结论语义不同。
- `missing_mapping`：当前 SAEE 没有可识别的对应面。

## 必需 Crosswalk

| External Concept | Purpose | SAEE Equivalent | Relationship | Gap |
|---|---|---|---|---|
| Agent Identity | 把动作与智能体标识关联 | `agent_id`、可选 `persona_ref` | 部分对齐 | 只记录标识，不独立验证身份真实性；没有外部标识协议 |
| Action Identity | 区分动作实例并关联证据 | `action_id` 与引用相等关系 | 概念上对齐 | 没有共享外部 action identifier 格式 |
| Action Digest | 对动作表示建立稳定摘要 | `receipt_digest`、`content_digest` | 范围不同 | 现有摘要覆盖收据或内容，不覆盖规范化外部动作对象 |
| Authorization Reference | 将动作绑定到授权决定 | `policy_decision_ref`、授权窗口与范围关系 | 部分对齐 | 引用不证明授权真实、有效或未撤销；没有外部授权收据协议 |
| Human Approval Evidence | 表达人类身份、上下文、范围和时间 | `HUMAN_OVERSIGHT` 充分性剖面 | 部分对齐 | 合成关系检查不认证真实人类，也不处理凭据和撤销 |
| Audit Trail | 组织动作观察和收据序列 | observed trace receipt、`previous_receipt_digest` | 范围不同 | 没有外部审计轨迹 wire protocol；轨迹顺序不等于真实性 |
| Evidence Composition | 组合多个证据关系回答责任问题 | Evidence Adequacy relationship evaluation | 部分对齐 | 只有固定本地剖面，没有通用跨组织组合协议和信任根 |
| Verification Result | 报告验证器是否通过 | `valid`、`result`、`profile_requirements_satisfied` | 部分对齐 | 结果语义属于本地验证器，不是外部 conformance 结果 |
| Accountability Claim | 声明证据准备支持的责任命题 | `claim_type` 与充分性结果 | 范围不同 | v0.1 始终保留 `accountability_claim_established=false`，不形成法律事实 |

## 四类外部概念族与 SAEE 的关系

### Agent Audit Trail concepts

SAEE 的 observed trace 和 receipt 对象与“记录动作观察、顺序和结果”概念相邻。但 SAEE 进一步区分观察、结构验证、摘要一致性和声明充分性。该关系是研究层面的范围比较，不表示审计轨迹协议实现。

### Signed Action Receipt concepts

SAEE 现有资源解析收据包含摘要和完整性块，但没有签名动作对象、外部 canonicalization、证书链或信任根。因此只能说摘要／收据概念相邻，不能说实现“签名动作收据”。

### Human Authorization Evidence concepts

SAEE 的 `HUMAN_OVERSIGHT` 剖面要求身份声明、审批上下文、批准范围、审批时间和动作关系。这比单一 `approved=true` 更严格；但它不认证真实审批人，不验证外部授权凭据，也不处理撤销。

### Agent Accountability Composition concepts

SAEE 的 Evidence Adequacy Profile 把字段与关系组合为声明需求。它与“组合多个证据面”概念部分对齐，但仍是固定、本地、合成范围，不提供跨组织签名组合、共同信任根或争议裁决。

## 机器可读入口

- Crosswalk JSON：`agent-interface/mappings/agent-receipt-crosswalk.v0.1.json`
- 差距分析：`docs/standards/SAEE_AGENT_RECEIPT_GAP_ANALYSIS.md`
- 声明边界：`docs/standards/SAEE_STANDARD_BOUNDARIES.md`
- 验证命令：`python3 scripts/saee_agent_receipt_crosswalk_smoke.py`
