# SAEE 标准与认证声明边界

## 明确不声明

SAEE Agent Receipt Crosswalk v0.1 不声明：

- RFC status（RFC 状态）；
- IETF approval（IETF 批准或背书）；
- IETF compliance（IETF 合规）；
- RFC compatibility（RFC 兼容）；
- external standard adoption（外部标准采纳）；
- regulatory certification or approval（监管认证或批准）；
- security certification（安全认证）；
- legal evidence status（法律证据地位）；
- cryptographic identity verification（密码学身份验证），除非未来有独立实现和验证材料；
- production readiness（生产就绪）。

## 为什么必须避免越界表述

可信证据架构首先要对自己的证据边界诚实。语义表格只能说明研究者看到了概念相似性，不能证明：

- 字段语义完全一致；
- 编码、摘要、签名或验证算法一致；
- 不同实现可以互操作；
- 某标准组织审阅或接受了本项目；
- 监管者、法院或第三方审计机构接受相关结论。

如果把“概念对齐”写成“标准兼容”，就会让 crosswalk 本身成为不可靠声明，削弱 SAEE 所强调的证据充分性原则。

## 允许使用的表述

- “SAEE conceptually aligns with …”
- “SAEE 与该概念在研究目标上部分对齐。”
- “This is a semantic analysis against supplied concept labels.”
- “该映射没有核对规范文本，也不构成协议实现。”
- “Potential extension point（潜在扩展点）。”

## 禁止使用的表述

- “SAEE is IETF compliant.”
- “SAEE implements the IETF agent receipt standard.”
- “SAEE is RFC compatible.”
- “SAEE receipts are legally valid evidence.”
- “SAEE has regulatory or security certification.”

这些禁止示例只用于说明不可作出的声明，不表示项目具备相应状态。

## 当前真值面

```yaml
normative_text_verified: false
ietf_compliance_claimed: false
ietf_approval_claimed: false
rfc_status_claimed: false
rfc_compatibility_claimed: false
external_standard_adopted: false
regulatory_approval_claimed: false
security_certification_claimed: false
legal_evidence_status_claimed: false
cryptographic_identity_verification_claimed: false
production_ready: false
```
