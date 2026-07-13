# SAEE 租户隐私边界智能体推荐门

answer: recommend
recommendation_scope: whole_tenant_api_synthetic_only_controlled_preview
development_blockers: 0
human_validation_used: false
agent_validation_primary: true

## 必答设计检查

1. 强化子系统：`Evolutionary Archive / Rollback Immune System`，通过输入、身份、审计、存储、备份恢复和第三方传输的隐私免疫边界减少不可逆污染。
2. 改善环节：感知输入筛选、沙盒发育、档案与回滚。
3. 安全边界：非本地 preview 必须显式 `SAEE_SYNTHETIC_DATA_ONLY=true`；未知键、自由文本、NFKC 混淆、额外 JWT claim 和不安全 path ID 均 fail closed。
4. 非审计优先：证据适配器只是进化系统的免疫/证据子系统，不改变 SAEE 数字生物圈进化引擎定位。

## 真实复核历史

- round 1: `conditional`, blockers `3`
- round 2: `conditional`, blockers `1`
- round 3: `recommend`, blockers `0`（运行时边界）
- round 4: `recommend`, blockers `0`（证据晋级器）
- evidence-promotion remediation: `16/16` tamper negatives pass；独立 false-escalation `22/22` 拒绝晋级

历史失败不得删除或改写。晋级器必须验证 round 2 的失败历史与 round 3 的通过结论。

## 可晋级字段

```text
agent_privacy_boundary_review_completed: true
agent_privacy_boundary_review_scope: whole_tenant_api_synthetic_only_controlled_preview_independent_agent
```

## 永久限制

```text
general_dlp_available: false
deidentification_proven: false
real_customer_data_allowed: false
privacy_legal_review_completed: false
data_processing_agreement_completed: false
qianfan_provider_legal_approval_completed: false
qianfan_retention_terms_verified: false
customer_data_processing_ready: false
production_ready: false
customer_validated: false
product_launched: false
blockers_closed: 0
```

此推荐只覆盖合成数据受控预览，不是法务意见、DPA、真实客户数据处理许可、生产隐私审批或通用 DLP。
