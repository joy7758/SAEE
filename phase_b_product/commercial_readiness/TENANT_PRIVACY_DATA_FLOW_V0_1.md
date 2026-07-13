# SAEE 租户受控预览隐私数据流 v0.1

状态：智能体可读的全租户 API 合成数据流清单；不是法务审批、DPA、通用 DLP 或生产数据处理许可。

## 强制运行边界

- 非本地预览必须显式设置 `SAEE_SYNTHETIC_DATA_ONLY=true`，缺失或关闭时 readiness fail closed。
- `real_customer_data_allowed=false`
- `deidentification_proven=false`
- `general_dlp_available=false`
- `privacy_legal_review_completed=false`
- `data_processing_agreement_completed=false`
- `qianfan_provider_legal_approval_completed=false`
- `production_ready=false`

## 八个数据面

1. 请求 JSON：只接受闭合场景/创建契约；配置仅限 `policy`、`workflow`，字符串值必须是已 NFKC 规范化的 `public-safe identifier`，运行器二次校验。
2. path/query：实验 ID 只允许公开安全标识，错误不回显输入。
3. 租户/角色 header：只允许白名单内公开安全标识。
4. Authorization/API Key：只做瞬时验证，不写审计、不写存储、不回显。
5. 预览 JWT：精确闭合 claim 集，不接受 `email` 或额外 claim；subject/tenant/role 均为公开安全标识。
6. 审计/错误：不记录 body、凭证、原始 tenant ID，验证错误不回显拒绝值。
7. 存储/备份/恢复/保留：只承载合成评估记录和闭合审计元数据。
8. 百度千帆：只发送脱敏数值 fixture、固定工具 schema/receipt；不发送 API Key、客户记录、候选代码或私有演化内核。

机器可读真源：`phase_b_product/commercial_readiness/tenant_privacy_agent_review/tenant_privacy_data_flow.local.json`。
