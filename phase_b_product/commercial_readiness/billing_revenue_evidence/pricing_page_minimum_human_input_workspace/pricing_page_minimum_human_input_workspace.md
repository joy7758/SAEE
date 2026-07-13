# SAEE Pricing Page Minimum Human Input Workspace v0.1

`pricing_page_minimum_human_input_workspace_v0_1: true`

## 目的

这个工作台只回答一个问题：为了让 `pricing_page` 进入本地 validator，
人类最少需要补哪些字段。它不填写价格、不批准定价、不发布定价页、
不生成销售报价、不配置支付、不联系客户、不运行 evidence builder、不关闭 blocker。

## 状态

- `status: hold_minimum_human_input_required`
- `target_blocker_id: pricing_page`
- `minimum_required_field_count: 34`
- `filled_value_count: 0`
- `blank_value_count: 34`
- `pricing_page_published: false`
- `pricing_page_approved: false`
- `production_ready: false`
- `product_launched: false`

## 最小字段清单

| 字段 | 分组 | 必填 | 填到哪里 | 人工说明 |
| --- | --- | --- | --- | --- |
| `pricing_page_evidence_input.human_reviewer_name` | metadata | true | `pricing_page_evidence_input.human_filled.local.json` | 由人填写真实审批信息；Codex 不能代填。 |
| `pricing_page_evidence_input.review_date` | metadata | true | `pricing_page_evidence_input.human_filled.local.json` | 由人填写真实审批信息；Codex 不能代填。 |
| `pricing_page_evidence_input.commercial_owner` | metadata | true | `pricing_page_evidence_input.human_filled.local.json` | 由人填写真实审批信息；Codex 不能代填。 |
| `pricing_page_evidence_input.product_owner` | metadata | true | `pricing_page_evidence_input.human_filled.local.json` | 由人填写真实审批信息；Codex 不能代填。 |
| `pricing_page_evidence_input.accounting_owner` | metadata | true | `pricing_page_evidence_input.human_filled.local.json` | 由人填写真实审批信息；Codex 不能代填。 |
| `pricing_page_evidence_input.legal_owner` | metadata | true | `pricing_page_evidence_input.human_filled.local.json` | 由人填写真实审批信息；Codex 不能代填。 |
| `pricing_page_evidence_input.billing_owner` | metadata | true | `pricing_page_evidence_input.human_filled.local.json` | 由人填写真实审批信息；Codex 不能代填。 |
| `pricing_page_evidence_input.review_record_reference` | metadata | true | `pricing_page_evidence_input.human_filled.local.json` | 由人填写真实审批信息；Codex 不能代填。 |
| `pricing_page_evidence_input.decision_summary` | metadata | true | `pricing_page_evidence_input.human_filled.local.json` | 由人填写真实审批信息；Codex 不能代填。 |
| `pricing_page_evidence_input.evidence_review.approved_plan_and_usage_terms` | evidence_review | true | `pricing_page_evidence_input.human_filled.local.json` | 只有人工确认真实证据存在时才设为 true。 |
| `pricing_page_evidence_input.source_notes_by_key.approved_plan_and_usage_terms` | source_note | true | `pricing_page_evidence_input.human_filled.local.json` | 填写可追溯来源说明；不要写密钥、账号或付款凭据。 |
| `pricing_page_evidence_input.review_artifacts[approved_plan_and_usage_terms].artifact_reference` | review_artifact | true | `pricing_page_evidence_input.human_filled.local.json` | 填写人工审查材料或审批记录引用。 |
| `pricing_page_evidence_input.review_artifacts[approved_plan_and_usage_terms].owner_named` | review_artifact | true | `pricing_page_evidence_input.human_filled.local.json` | 对应负责人已明确时才设为 true。 |
| `pricing_page_evidence_input.review_artifacts[approved_plan_and_usage_terms].reviewed_by_human` | review_artifact | true | `pricing_page_evidence_input.human_filled.local.json` | 对应材料已由人审过时才设为 true。 |
| `pricing_page_evidence_input.evidence_review.human_approved_pricing_page_copy` | evidence_review | true | `pricing_page_evidence_input.human_filled.local.json` | 只有人工确认真实证据存在时才设为 true。 |
| `pricing_page_evidence_input.source_notes_by_key.human_approved_pricing_page_copy` | source_note | true | `pricing_page_evidence_input.human_filled.local.json` | 填写可追溯来源说明；不要写密钥、账号或付款凭据。 |
| `pricing_page_evidence_input.review_artifacts[human_approved_pricing_page_copy].artifact_reference` | review_artifact | true | `pricing_page_evidence_input.human_filled.local.json` | 填写人工审查材料或审批记录引用。 |
| `pricing_page_evidence_input.review_artifacts[human_approved_pricing_page_copy].owner_named` | review_artifact | true | `pricing_page_evidence_input.human_filled.local.json` | 对应负责人已明确时才设为 true。 |
| `pricing_page_evidence_input.review_artifacts[human_approved_pricing_page_copy].reviewed_by_human` | review_artifact | true | `pricing_page_evidence_input.human_filled.local.json` | 对应材料已由人审过时才设为 true。 |
| `pricing_page_evidence_input.evidence_review.legal_review_completed` | evidence_review | true | `pricing_page_evidence_input.human_filled.local.json` | 只有人工确认真实证据存在时才设为 true。 |
| `pricing_page_evidence_input.source_notes_by_key.legal_review_completed` | source_note | true | `pricing_page_evidence_input.human_filled.local.json` | 填写可追溯来源说明；不要写密钥、账号或付款凭据。 |
| `pricing_page_evidence_input.review_artifacts[legal_review_completed].artifact_reference` | review_artifact | true | `pricing_page_evidence_input.human_filled.local.json` | 填写人工审查材料或审批记录引用。 |
| `pricing_page_evidence_input.review_artifacts[legal_review_completed].owner_named` | review_artifact | true | `pricing_page_evidence_input.human_filled.local.json` | 对应负责人已明确时才设为 true。 |
| `pricing_page_evidence_input.review_artifacts[legal_review_completed].reviewed_by_human` | review_artifact | true | `pricing_page_evidence_input.human_filled.local.json` | 对应材料已由人审过时才设为 true。 |
| `pricing_page_evidence_input.evidence_review.pricing_page_publication_approval_recorded` | evidence_review | true | `pricing_page_evidence_input.human_filled.local.json` | 只有人工确认真实证据存在时才设为 true。 |
| `pricing_page_evidence_input.source_notes_by_key.pricing_page_publication_approval_recorded` | source_note | true | `pricing_page_evidence_input.human_filled.local.json` | 填写可追溯来源说明；不要写密钥、账号或付款凭据。 |
| `pricing_page_evidence_input.review_artifacts[pricing_page_publication_approval_recorded].artifact_reference` | review_artifact | true | `pricing_page_evidence_input.human_filled.local.json` | 填写人工审查材料或审批记录引用。 |
| `pricing_page_evidence_input.review_artifacts[pricing_page_publication_approval_recorded].owner_named` | review_artifact | true | `pricing_page_evidence_input.human_filled.local.json` | 对应负责人已明确时才设为 true。 |
| `pricing_page_evidence_input.review_artifacts[pricing_page_publication_approval_recorded].reviewed_by_human` | review_artifact | true | `pricing_page_evidence_input.human_filled.local.json` | 对应材料已由人审过时才设为 true。 |
| `pricing_page_evidence_input.evidence_review.production_readiness_non_claim_reviewed` | evidence_review | true | `pricing_page_evidence_input.human_filled.local.json` | 只有人工确认真实证据存在时才设为 true。 |
| `pricing_page_evidence_input.source_notes_by_key.production_readiness_non_claim_reviewed` | source_note | true | `pricing_page_evidence_input.human_filled.local.json` | 填写可追溯来源说明；不要写密钥、账号或付款凭据。 |
| `pricing_page_evidence_input.review_artifacts[production_readiness_non_claim_reviewed].artifact_reference` | review_artifact | true | `pricing_page_evidence_input.human_filled.local.json` | 填写人工审查材料或审批记录引用。 |
| `pricing_page_evidence_input.review_artifacts[production_readiness_non_claim_reviewed].owner_named` | review_artifact | true | `pricing_page_evidence_input.human_filled.local.json` | 对应负责人已明确时才设为 true。 |
| `pricing_page_evidence_input.review_artifacts[production_readiness_non_claim_reviewed].reviewed_by_human` | review_artifact | true | `pricing_page_evidence_input.human_filled.local.json` | 对应材料已由人审过时才设为 true。 |

## 复制模板

```bash
cp phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_evidence_input.template.json phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_evidence_input.human_filled.local.json
```

## 人工填写后再运行

```bash
python3 scripts/saee_pricing_page_approval_input_validator.py --input phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_evidence_input.human_filled.local.json
```

## 仍需单独批准

```bash
python3 scripts/saee_pricing_page_evidence_builder.py --input phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_evidence_input.human_filled.local.json
```

## 明确边界

- `values_saved_by_workspace: false`
- `form_submission_enabled: false`
- `validator_inputs_exported: false`
- `validators_run: false`
- `evidence_collection_authorized: false`
- `blocker_closure_authorized: false`
- `pricing_page_approved: false`
- `pricing_page_published: false`
- `payment_provider_configured: false`
- `checkout_enabled: false`
- `customer_contacted: false`
- `production_ready: false`
