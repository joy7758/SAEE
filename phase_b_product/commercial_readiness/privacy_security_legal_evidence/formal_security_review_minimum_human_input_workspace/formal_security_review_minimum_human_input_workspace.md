# SAEE Formal Security Review Minimum Human Input Workspace v0.1

`formal_security_review_minimum_human_input_workspace_v0_1: true`

## 目的

这个工作台只回答一个问题：为了让 `formal_security_review` 进入本地 validator，
人类最少需要补哪些字段。它不执行安全审查、不批准安全报告、不联系审查方、
不跑渗透测试、不查看私有核心、不运行 evidence builder、不关闭 blocker。

## 状态

- `status: hold_minimum_human_input_required`
- `target_blocker_id: formal_security_review`
- `minimum_required_field_count: 40`
- `filled_value_count: 0`
- `blank_value_count: 40`
- `formal_security_review_completed: false`
- `formal_security_review_approved: false`
- `private_core_exposed: false`
- `production_ready: false`
- `product_launched: false`

## 最小字段清单

| 字段 | 分组 | 必填 | 填到哪里 | 人工说明 |
| --- | --- | --- | --- | --- |
| `formal_security_review_evidence_input.human_reviewer_name` | metadata | true | `formal_security_review_evidence_input.human_filled.local.json` | 由人填写真实安全审查信息；Codex 不能代填。 |
| `formal_security_review_evidence_input.review_date` | metadata | true | `formal_security_review_evidence_input.human_filled.local.json` | 由人填写真实安全审查信息；Codex 不能代填。 |
| `formal_security_review_evidence_input.security_review_owner` | metadata | true | `formal_security_review_evidence_input.human_filled.local.json` | 由人填写真实安全审查信息；Codex 不能代填。 |
| `formal_security_review_evidence_input.report_reference` | metadata | true | `formal_security_review_evidence_input.human_filled.local.json` | 由人填写真实安全审查信息；Codex 不能代填。 |
| `formal_security_review_evidence_input.decision_summary` | metadata | true | `formal_security_review_evidence_input.human_filled.local.json` | 由人填写真实安全审查信息；Codex 不能代填。 |
| `formal_security_review_evidence_input.evidence_review.auth_and_tenant_boundary_reviewed` | evidence_review | true | `formal_security_review_evidence_input.human_filled.local.json` | 只有人工确认真实安全审查证据存在时才设为 true。 |
| `formal_security_review_evidence_input.source_notes_by_key.auth_and_tenant_boundary_reviewed` | source_note | true | `formal_security_review_evidence_input.human_filled.local.json` | 填写可追溯来源说明；不要写密钥、账号、客户数据或私人凭据。 |
| `formal_security_review_evidence_input.review_artifacts[auth_and_tenant_boundary_reviewed].artifact_reference` | review_artifact | true | `formal_security_review_evidence_input.human_filled.local.json` | 填写人工审查报告、范围记录或审批材料引用。 |
| `formal_security_review_evidence_input.review_artifacts[auth_and_tenant_boundary_reviewed].owner_named` | review_artifact | true | `formal_security_review_evidence_input.human_filled.local.json` | 对应负责人已明确时才设为 true。 |
| `formal_security_review_evidence_input.review_artifacts[auth_and_tenant_boundary_reviewed].reviewed_by_human` | review_artifact | true | `formal_security_review_evidence_input.human_filled.local.json` | 对应材料已由人审过时才设为 true。 |
| `formal_security_review_evidence_input.evidence_review.dependency_review_completed` | evidence_review | true | `formal_security_review_evidence_input.human_filled.local.json` | 只有人工确认真实安全审查证据存在时才设为 true。 |
| `formal_security_review_evidence_input.source_notes_by_key.dependency_review_completed` | source_note | true | `formal_security_review_evidence_input.human_filled.local.json` | 填写可追溯来源说明；不要写密钥、账号、客户数据或私人凭据。 |
| `formal_security_review_evidence_input.review_artifacts[dependency_review_completed].artifact_reference` | review_artifact | true | `formal_security_review_evidence_input.human_filled.local.json` | 填写人工审查报告、范围记录或审批材料引用。 |
| `formal_security_review_evidence_input.review_artifacts[dependency_review_completed].owner_named` | review_artifact | true | `formal_security_review_evidence_input.human_filled.local.json` | 对应负责人已明确时才设为 true。 |
| `formal_security_review_evidence_input.review_artifacts[dependency_review_completed].reviewed_by_human` | review_artifact | true | `formal_security_review_evidence_input.human_filled.local.json` | 对应材料已由人审过时才设为 true。 |
| `formal_security_review_evidence_input.evidence_review.formal_security_review_report` | evidence_review | true | `formal_security_review_evidence_input.human_filled.local.json` | 只有人工确认真实安全审查证据存在时才设为 true。 |
| `formal_security_review_evidence_input.source_notes_by_key.formal_security_review_report` | source_note | true | `formal_security_review_evidence_input.human_filled.local.json` | 填写可追溯来源说明；不要写密钥、账号、客户数据或私人凭据。 |
| `formal_security_review_evidence_input.review_artifacts[formal_security_review_report].artifact_reference` | review_artifact | true | `formal_security_review_evidence_input.human_filled.local.json` | 填写人工审查报告、范围记录或审批材料引用。 |
| `formal_security_review_evidence_input.review_artifacts[formal_security_review_report].owner_named` | review_artifact | true | `formal_security_review_evidence_input.human_filled.local.json` | 对应负责人已明确时才设为 true。 |
| `formal_security_review_evidence_input.review_artifacts[formal_security_review_report].reviewed_by_human` | review_artifact | true | `formal_security_review_evidence_input.human_filled.local.json` | 对应材料已由人审过时才设为 true。 |
| `formal_security_review_evidence_input.evidence_review.private_core_non_exposure_review_completed` | evidence_review | true | `formal_security_review_evidence_input.human_filled.local.json` | 只有人工确认真实安全审查证据存在时才设为 true。 |
| `formal_security_review_evidence_input.source_notes_by_key.private_core_non_exposure_review_completed` | source_note | true | `formal_security_review_evidence_input.human_filled.local.json` | 填写可追溯来源说明；不要写密钥、账号、客户数据或私人凭据。 |
| `formal_security_review_evidence_input.review_artifacts[private_core_non_exposure_review_completed].artifact_reference` | review_artifact | true | `formal_security_review_evidence_input.human_filled.local.json` | 填写人工审查报告、范围记录或审批材料引用。 |
| `formal_security_review_evidence_input.review_artifacts[private_core_non_exposure_review_completed].owner_named` | review_artifact | true | `formal_security_review_evidence_input.human_filled.local.json` | 对应负责人已明确时才设为 true。 |
| `formal_security_review_evidence_input.review_artifacts[private_core_non_exposure_review_completed].reviewed_by_human` | review_artifact | true | `formal_security_review_evidence_input.human_filled.local.json` | 对应材料已由人审过时才设为 true。 |
| `formal_security_review_evidence_input.evidence_review.public_shell_threat_model_reviewed` | evidence_review | true | `formal_security_review_evidence_input.human_filled.local.json` | 只有人工确认真实安全审查证据存在时才设为 true。 |
| `formal_security_review_evidence_input.source_notes_by_key.public_shell_threat_model_reviewed` | source_note | true | `formal_security_review_evidence_input.human_filled.local.json` | 填写可追溯来源说明；不要写密钥、账号、客户数据或私人凭据。 |
| `formal_security_review_evidence_input.review_artifacts[public_shell_threat_model_reviewed].artifact_reference` | review_artifact | true | `formal_security_review_evidence_input.human_filled.local.json` | 填写人工审查报告、范围记录或审批材料引用。 |
| `formal_security_review_evidence_input.review_artifacts[public_shell_threat_model_reviewed].owner_named` | review_artifact | true | `formal_security_review_evidence_input.human_filled.local.json` | 对应负责人已明确时才设为 true。 |
| `formal_security_review_evidence_input.review_artifacts[public_shell_threat_model_reviewed].reviewed_by_human` | review_artifact | true | `formal_security_review_evidence_input.human_filled.local.json` | 对应材料已由人审过时才设为 true。 |
| `formal_security_review_evidence_input.evidence_review.review_findings_triaged` | evidence_review | true | `formal_security_review_evidence_input.human_filled.local.json` | 只有人工确认真实安全审查证据存在时才设为 true。 |
| `formal_security_review_evidence_input.source_notes_by_key.review_findings_triaged` | source_note | true | `formal_security_review_evidence_input.human_filled.local.json` | 填写可追溯来源说明；不要写密钥、账号、客户数据或私人凭据。 |
| `formal_security_review_evidence_input.review_artifacts[review_findings_triaged].artifact_reference` | review_artifact | true | `formal_security_review_evidence_input.human_filled.local.json` | 填写人工审查报告、范围记录或审批材料引用。 |
| `formal_security_review_evidence_input.review_artifacts[review_findings_triaged].owner_named` | review_artifact | true | `formal_security_review_evidence_input.human_filled.local.json` | 对应负责人已明确时才设为 true。 |
| `formal_security_review_evidence_input.review_artifacts[review_findings_triaged].reviewed_by_human` | review_artifact | true | `formal_security_review_evidence_input.human_filled.local.json` | 对应材料已由人审过时才设为 true。 |
| `formal_security_review_evidence_input.evidence_review.storage_backup_and_restore_reviewed` | evidence_review | true | `formal_security_review_evidence_input.human_filled.local.json` | 只有人工确认真实安全审查证据存在时才设为 true。 |
| `formal_security_review_evidence_input.source_notes_by_key.storage_backup_and_restore_reviewed` | source_note | true | `formal_security_review_evidence_input.human_filled.local.json` | 填写可追溯来源说明；不要写密钥、账号、客户数据或私人凭据。 |
| `formal_security_review_evidence_input.review_artifacts[storage_backup_and_restore_reviewed].artifact_reference` | review_artifact | true | `formal_security_review_evidence_input.human_filled.local.json` | 填写人工审查报告、范围记录或审批材料引用。 |
| `formal_security_review_evidence_input.review_artifacts[storage_backup_and_restore_reviewed].owner_named` | review_artifact | true | `formal_security_review_evidence_input.human_filled.local.json` | 对应负责人已明确时才设为 true。 |
| `formal_security_review_evidence_input.review_artifacts[storage_backup_and_restore_reviewed].reviewed_by_human` | review_artifact | true | `formal_security_review_evidence_input.human_filled.local.json` | 对应材料已由人审过时才设为 true。 |

## 复制模板

```bash
cp phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_evidence_input.template.json phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_evidence_input.human_filled.local.json
```

## 人工填写后再运行

```bash
python3 scripts/saee_formal_security_review_approval_input_validator.py --input phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_evidence_input.human_filled.local.json
```

## 仍需单独批准

```bash
python3 scripts/saee_formal_security_review_evidence_builder.py --input phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_evidence_input.human_filled.local.json
```

## 明确边界

- `values_saved_by_workspace: false`
- `form_submission_enabled: false`
- `validator_inputs_exported: false`
- `validators_run: false`
- `evidence_collection_authorized: false`
- `blocker_closure_authorized: false`
- `formal_security_review_completed: false`
- `formal_security_review_approved: false`
- `private_core_inspected_by_codex: false`
- `penetration_test_run_by_codex: false`
- `customer_contacted: false`
- `production_ready: false`
