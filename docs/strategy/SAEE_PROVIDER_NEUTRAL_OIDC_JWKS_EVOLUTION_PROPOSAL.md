# SAEE Provider-Neutral OIDC/JWKS Evolution Proposal

状态：两名独立智能体均为 `recommend`；进入本地窄切片实现。未联系身份提供方，未验证生产 token。

## 客户推荐问题

如果中国市场潜在客户需要可商用的 SAEE 受控预览，是否应优先推荐一个 provider-neutral、离线可验证的 signed OIDC/JWKS verifier core，并将其绑定到现有租户授权与 RBAC，而不是先绑定某一家外部 IdP？

当前回答：`recommend`。`recommendation_agent_validation` 与 `observed_trace_recommendation_gate` 独立复核后均推荐优先建设本地离线签名验证核心，并明确否决越过依赖顺序先做 Phase 3 `support_contact`。

推荐门要求先修复三项可执行阻塞：删除 OIDC 合约中的 `email/email_verified`；实现本地 JWKS 签名验证；允许授权上下文记录 `oidc_jwks_offline_verified`。三项均属于本提案验收范围。

## 独立敌对终审

最终结论：`recommend`，`blocker_count=0`。终审前累计发现并修复：RSA 签名代表值可塑性、非规范 Base64URL、时钟偏差无界、verified-principal provenance 可伪造、HTTPS issuer 规范漏洞、JWKS 资源上限、优先级提前自证、超长 JSON 整数异常泄漏和偶数 modulus 等问题。

终审实测为 2 个有效签名/轮换 key、43 个失败关闭负例、10 次确定性复跑、6 个 handler 前终止案例、网络调用 0、token/密钥泄漏 0。该结论仅允许晋级三个本地窄字段，不关闭生产阻塞。

## 演化设计检查

1. 强化子系统：`Evolutionary Archive / Rollback Immune System` 与 `Sandbox Development`。
2. 改善环节：身份感知、授权分叉、失败隔离、档案与回滚；不改变进化引擎核心。
3. 边界：只读取本地 JWKS snapshot；不联网、不安装依赖、不执行外部代码、不自动扩大权限；密钥材料仅含公钥。
4. 审计优先风险：低。身份验证是数字生物受控发育环境的免疫边界，不是产品核心叙事。

## 候选实现

- 仅支持 `RS256`，拒绝 `none`、对称算法、`jku`、`x5u`、内嵌 `jwk` 和未知 header。
- JWKS 精确闭合 schema：唯一 `kid`、`kty=RSA`、`use=sig`、`alg=RS256`、无私钥参数。
- 使用 Python 标准库完成 RSA PKCS#1 v1.5 SHA-256 验签，不新增供应链依赖。
- 精确校验 `iss`、`aud`、`exp`、`iat`、`nbf`、`sub`、`tenant_id`、`roles`；受控预览只接受公开安全标识和合成身份。
- 与现有 `rbac_policy.py`、`authorization_context.py` 绑定，未知角色、未知路由、租户切换、权限降级均 fail closed。
- 支持两个本地公钥重叠窗口，用于验证 rotation 行为；不宣称真实 IdP rotation policy 已审批。

## 本地验收条件

- 有效签名、当前/轮换 key、租户和角色绑定通过。
- 至少覆盖：签名篡改、未知 `kid`、重复 `kid`、错误算法、错误 issuer/audience、过期、未来 iat/nbf、超长寿命、额外 claim、无效 tenant/role、角色越权、跨租户切换。
- 错误不回显 token、claim 值或密钥材料。
- 独立智能体对源码 manifest 与负例重新哈希，最终 `recommend`、0 blocker 后，才允许晋级窄字段。

## 允许的窄字段

```text
provider_neutral_oidc_verifier_core_available: true
local_signed_jwks_validation_completed: true
local_oidc_rbac_binding_reviewed: true
```

## 必须保持 false

```text
production_identity_provider_selected: false
identity_provider_admin_owner_named: false
external_identity_provider_contacted: false
jwks_fetched: false
tokens_validated_in_production: false
oauth_oidc_flow_approved: false
session_expiry_policy_approved: false
admin_recovery_policy_reviewed: false
production_identity_provider_available: false
oauth_oidc_available: false
rbac_available: false
production_auth_ready: false
production_ready: false
customer_validated: false
product_launched: false
```

本提案不能关闭任何 production blocker；它只减少 Phase 1 从“无签名验证核心”到“等待真实 IdP 和生产证据”的工程缺口。
