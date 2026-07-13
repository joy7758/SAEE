# SAEE Production Restore Policy Minimum Human Input Workspace v0.1

`production_restore_policy_minimum_human_input_workspace_v0_1: true`

## 目的

这个工作台只回答一个问题：为了让 `production_restore_policy` 进入本地 validator，
人类最少需要补齐哪些恢复策略审批字段。它不批准策略，不执行恢复，不触碰实时数据路径，
不运行 evidence builder，也不关闭 blocker。

## 当前状态

- status: hold_minimum_human_input_required
- target_blocker_id: production_restore_policy
- minimum_required_field_count: 37
- blank_value_count: 37
- metadata_field_count: 7
- production_restore_policy_evidence_key_count: 6
- policy_evidence_slot_field_count: 18
- production_restore_policy_approved: false
- production_restore_policy_available: false
- live_restore_performed: false
- production_data_path_modified: false
- blocker_closure_authorized: false
- production_ready: false
- product_launched: false
- customer_validated: false

## 人需要填写的字段

| 字段 | 分组 | 填到哪里 | 人工说明 |
| --- | --- | --- | --- |
| `production_restore_policy_approval_input.human_reviewer_name` | metadata | `production_restore_policy_approval_input.human_filled.local.json` | 由人填写真实恢复策略审批信息；Codex 不能代填。 |
| `production_restore_policy_approval_input.review_date` | metadata | `production_restore_policy_approval_input.human_filled.local.json` | 由人填写真实恢复策略审批信息；Codex 不能代填。 |
| `production_restore_policy_approval_input.data_operations_owner` | metadata | `production_restore_policy_approval_input.human_filled.local.json` | 由人填写真实恢复策略审批信息；Codex 不能代填。 |
| `production_restore_policy_approval_input.security_owner` | metadata | `production_restore_policy_approval_input.human_filled.local.json` | 由人填写真实恢复策略审批信息；Codex 不能代填。 |
| `production_restore_policy_approval_input.privacy_legal_owner` | metadata | `production_restore_policy_approval_input.human_filled.local.json` | 由人填写真实恢复策略审批信息；Codex 不能代填。 |
| `production_restore_policy_approval_input.incident_response_owner` | metadata | `production_restore_policy_approval_input.human_filled.local.json` | 由人填写真实恢复策略审批信息；Codex 不能代填。 |
| `production_restore_policy_approval_input.decision_summary` | metadata | `production_restore_policy_approval_input.human_filled.local.json` | 由人填写真实恢复策略审批信息；Codex 不能代填。 |
| `production_restore_policy_approval_input.policy_evidence_review.backup_retention_policy_approved` | policy_evidence_review | `production_restore_policy_approval_input.human_filled.local.json` | 只有人工确认真实恢复策略证据存在且已审查时才设为 true。 |
| `production_restore_policy_approval_input.source_notes_by_key.backup_retention_policy_approved` | source_note | `production_restore_policy_approval_input.human_filled.local.json` | 填写可追溯来源说明；不要写密钥、客户数据、账号或私人凭据。 |
| `production_restore_policy_approval_input.policy_evidence_slots[backup_retention_policy_approved].evidence_reference` | policy_evidence_slot | `production_restore_policy_approval_input.human_filled.local.json` | 填写人工审查材料、政策记录或演练记录引用。 |
| `production_restore_policy_approval_input.policy_evidence_slots[backup_retention_policy_approved].owner_named` | policy_evidence_slot | `production_restore_policy_approval_input.human_filled.local.json` | 对应负责人已明确时才设为 true。 |
| `production_restore_policy_approval_input.policy_evidence_slots[backup_retention_policy_approved].reviewed_by_human` | policy_evidence_slot | `production_restore_policy_approval_input.human_filled.local.json` | 对应材料已由人审过时才设为 true。 |
| `production_restore_policy_approval_input.policy_evidence_review.credential_secret_exclusion_reviewed` | policy_evidence_review | `production_restore_policy_approval_input.human_filled.local.json` | 只有人工确认真实恢复策略证据存在且已审查时才设为 true。 |
| `production_restore_policy_approval_input.source_notes_by_key.credential_secret_exclusion_reviewed` | source_note | `production_restore_policy_approval_input.human_filled.local.json` | 填写可追溯来源说明；不要写密钥、客户数据、账号或私人凭据。 |
| `production_restore_policy_approval_input.policy_evidence_slots[credential_secret_exclusion_reviewed].evidence_reference` | policy_evidence_slot | `production_restore_policy_approval_input.human_filled.local.json` | 填写人工审查材料、政策记录或演练记录引用。 |
| `production_restore_policy_approval_input.policy_evidence_slots[credential_secret_exclusion_reviewed].owner_named` | policy_evidence_slot | `production_restore_policy_approval_input.human_filled.local.json` | 对应负责人已明确时才设为 true。 |
| `production_restore_policy_approval_input.policy_evidence_slots[credential_secret_exclusion_reviewed].reviewed_by_human` | policy_evidence_slot | `production_restore_policy_approval_input.human_filled.local.json` | 对应材料已由人审过时才设为 true。 |
| `production_restore_policy_approval_input.policy_evidence_review.customer_notification_boundary_approved` | policy_evidence_review | `production_restore_policy_approval_input.human_filled.local.json` | 只有人工确认真实恢复策略证据存在且已审查时才设为 true。 |
| `production_restore_policy_approval_input.source_notes_by_key.customer_notification_boundary_approved` | source_note | `production_restore_policy_approval_input.human_filled.local.json` | 填写可追溯来源说明；不要写密钥、客户数据、账号或私人凭据。 |
| `production_restore_policy_approval_input.policy_evidence_slots[customer_notification_boundary_approved].evidence_reference` | policy_evidence_slot | `production_restore_policy_approval_input.human_filled.local.json` | 填写人工审查材料、政策记录或演练记录引用。 |
| `production_restore_policy_approval_input.policy_evidence_slots[customer_notification_boundary_approved].owner_named` | policy_evidence_slot | `production_restore_policy_approval_input.human_filled.local.json` | 对应负责人已明确时才设为 true。 |
| `production_restore_policy_approval_input.policy_evidence_slots[customer_notification_boundary_approved].reviewed_by_human` | policy_evidence_slot | `production_restore_policy_approval_input.human_filled.local.json` | 对应材料已由人审过时才设为 true。 |
| `production_restore_policy_approval_input.policy_evidence_review.incident_response_handoff_approved` | policy_evidence_review | `production_restore_policy_approval_input.human_filled.local.json` | 只有人工确认真实恢复策略证据存在且已审查时才设为 true。 |
| `production_restore_policy_approval_input.source_notes_by_key.incident_response_handoff_approved` | source_note | `production_restore_policy_approval_input.human_filled.local.json` | 填写可追溯来源说明；不要写密钥、客户数据、账号或私人凭据。 |
| `production_restore_policy_approval_input.policy_evidence_slots[incident_response_handoff_approved].evidence_reference` | policy_evidence_slot | `production_restore_policy_approval_input.human_filled.local.json` | 填写人工审查材料、政策记录或演练记录引用。 |
| `production_restore_policy_approval_input.policy_evidence_slots[incident_response_handoff_approved].owner_named` | policy_evidence_slot | `production_restore_policy_approval_input.human_filled.local.json` | 对应负责人已明确时才设为 true。 |
| `production_restore_policy_approval_input.policy_evidence_slots[incident_response_handoff_approved].reviewed_by_human` | policy_evidence_slot | `production_restore_policy_approval_input.human_filled.local.json` | 对应材料已由人审过时才设为 true。 |
| `production_restore_policy_approval_input.policy_evidence_review.production_restore_policy_approved` | policy_evidence_review | `production_restore_policy_approval_input.human_filled.local.json` | 只有人工确认真实恢复策略证据存在且已审查时才设为 true。 |
| `production_restore_policy_approval_input.source_notes_by_key.production_restore_policy_approved` | source_note | `production_restore_policy_approval_input.human_filled.local.json` | 填写可追溯来源说明；不要写密钥、客户数据、账号或私人凭据。 |
| `production_restore_policy_approval_input.policy_evidence_slots[production_restore_policy_approved].evidence_reference` | policy_evidence_slot | `production_restore_policy_approval_input.human_filled.local.json` | 填写人工审查材料、政策记录或演练记录引用。 |
| `production_restore_policy_approval_input.policy_evidence_slots[production_restore_policy_approved].owner_named` | policy_evidence_slot | `production_restore_policy_approval_input.human_filled.local.json` | 对应负责人已明确时才设为 true。 |
| `production_restore_policy_approval_input.policy_evidence_slots[production_restore_policy_approved].reviewed_by_human` | policy_evidence_slot | `production_restore_policy_approval_input.human_filled.local.json` | 对应材料已由人审过时才设为 true。 |
| `production_restore_policy_approval_input.policy_evidence_review.tenant_restore_boundary_approved` | policy_evidence_review | `production_restore_policy_approval_input.human_filled.local.json` | 只有人工确认真实恢复策略证据存在且已审查时才设为 true。 |
| `production_restore_policy_approval_input.source_notes_by_key.tenant_restore_boundary_approved` | source_note | `production_restore_policy_approval_input.human_filled.local.json` | 填写可追溯来源说明；不要写密钥、客户数据、账号或私人凭据。 |
| `production_restore_policy_approval_input.policy_evidence_slots[tenant_restore_boundary_approved].evidence_reference` | policy_evidence_slot | `production_restore_policy_approval_input.human_filled.local.json` | 填写人工审查材料、政策记录或演练记录引用。 |
| `production_restore_policy_approval_input.policy_evidence_slots[tenant_restore_boundary_approved].owner_named` | policy_evidence_slot | `production_restore_policy_approval_input.human_filled.local.json` | 对应负责人已明确时才设为 true。 |
| `production_restore_policy_approval_input.policy_evidence_slots[tenant_restore_boundary_approved].reviewed_by_human` | policy_evidence_slot | `production_restore_policy_approval_input.human_filled.local.json` | 对应材料已由人审过时才设为 true。 |

## 推荐流程

1. 人类复制模板到 `production_restore_policy_approval_input.human_filled.local.json`。
2. 人类只填写已审批的元数据、策略证据标记、来源说明和证据槽引用。
3. 人类运行本地 validator。
4. 如果 validator 通过，仍需单独批准才能运行 evidence builder。

## 禁止事项

- Codex 不得代填人工值。
- 不得从这个工作台执行恢复、触碰实时数据路径或恢复凭据。
- 不得联系客户、供应商或法律/安全审查人。
- 不得关闭 blocker、发布产品或声明生产可用。
