# SAEE Support Contact Minimum Human Input Workspace v0.1

`support_contact_minimum_human_input_workspace_v0_1: true`

## 目的

这个工作台只回答一个问题：为了推进 `support_contact` 这个第一优先商用阻塞项，
人类最少需要补哪些字段。它不填写值、不保存值、不发布支持入口、不联系客户、
不运行证据 builder、不导入工作簿、不关闭 blocker。

## 状态

- `status: hold_minimum_human_input_required`
- `target_blocker_id: support_contact`
- `minimum_required_field_count: 20`
- `filled_value_count: 0`
- `blank_value_count: 20`
- `support_contact_published: false`
- `production_ready: false`
- `product_launched: false`

## 最小字段清单

| 字段 | 分组 | 必填 | 填到哪里 | 人工说明 |
| --- | --- | --- | --- | --- |
| `first_owner_input.assigned_human_owner` | first_owner | true | `support_contact_human_input_bridge_input.human_filled.local.json` | 填写负责推进 support_contact 的人名或内部角色。 |
| `first_owner_input.owner_contact_reference` | first_owner | true | `support_contact_human_input_bridge_input.human_filled.local.json` | 填写内部可追溯的负责人联系方式或工单引用，不要写敏感凭据。 |
| `first_owner_input.target_review_date` | first_owner | true | `support_contact_human_input_bridge_input.human_filled.local.json` | 填写目标审查日期。 |
| `first_owner_input.human_approval_reference` | first_owner | true | `support_contact_human_input_bridge_input.human_filled.local.json` | 填写人工批准来源，例如本地会议纪要或内部审批编号。 |
| `first_owner_input.owner_acknowledged_scope` | first_owner | true | `support_contact_human_input_bridge_input.human_filled.local.json` | 负责人确认只推进支持入口证据，不发布产品、不联系客户。 |
| `support_contact_decision_input.human_reviewer_name` | decision_metadata | true | `support_contact_decision_input.human_filled.local.json` | 填写实际审查人。 |
| `support_contact_decision_input.review_date` | decision_metadata | true | `support_contact_decision_input.human_filled.local.json` | 填写审查日期。 |
| `support_contact_decision_input.selected_support_contact_channel` | decision_metadata | true | `support_contact_decision_input.human_filled.local.json` | 填写被人工选定的支持渠道类型或内部引用。 |
| `support_contact_decision_input.decision_summary` | decision_metadata | true | `support_contact_decision_input.human_filled.local.json` | 用一句话说明为什么该支持入口可进入下一步本地验证。 |
| `support_contact_decision_input.evidence_review.customer_facing_support_contact_configured` | evidence_review | true | `support_contact_decision_input.human_filled.local.json` | 只有人工确认真实证据存在时才设为 true。 |
| `support_contact_decision_input.source_notes_by_key.customer_facing_support_contact_configured` | source_notes | true | `support_contact_decision_input.human_filled.local.json` | 填写人工可追溯来源说明；不要写密钥、密码或私人凭据。 |
| `support_contact_decision_input.evidence_review.support_contact_owner_named` | evidence_review | true | `support_contact_decision_input.human_filled.local.json` | 只有人工确认真实证据存在时才设为 true。 |
| `support_contact_decision_input.source_notes_by_key.support_contact_owner_named` | source_notes | true | `support_contact_decision_input.human_filled.local.json` | 填写人工可追溯来源说明；不要写密钥、密码或私人凭据。 |
| `support_contact_decision_input.evidence_review.abuse_handling_path_defined` | evidence_review | true | `support_contact_decision_input.human_filled.local.json` | 只有人工确认真实证据存在时才设为 true。 |
| `support_contact_decision_input.source_notes_by_key.abuse_handling_path_defined` | source_notes | true | `support_contact_decision_input.human_filled.local.json` | 填写人工可追溯来源说明；不要写密钥、密码或私人凭据。 |
| `support_contact_decision_input.evidence_review.customer_notice_route_defined` | evidence_review | true | `support_contact_decision_input.human_filled.local.json` | 只有人工确认真实证据存在时才设为 true。 |
| `support_contact_decision_input.source_notes_by_key.customer_notice_route_defined` | source_notes | true | `support_contact_decision_input.human_filled.local.json` | 填写人工可追溯来源说明；不要写密钥、密码或私人凭据。 |
| `support_contact_decision_input.evidence_review.support_contact_test_recorded` | evidence_review | true | `support_contact_decision_input.human_filled.local.json` | 只有人工确认真实证据存在时才设为 true。 |
| `support_contact_decision_input.source_notes_by_key.support_contact_test_recorded` | source_notes | true | `support_contact_decision_input.human_filled.local.json` | 填写人工可追溯来源说明；不要写密钥、密码或私人凭据。 |
| `support_contact_decision_input.candidate_contact_slots[minimum_one_complete]` | candidate_contact_slot | true | `support_contact_decision_input.human_filled.local.json` | 至少补全一个候选支持入口槽位；只记录人工批准的公开/可公开信息。 |

## 复制模板

```bash
cp phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge/support_contact_human_input_bridge_input.template.json phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge/support_contact_human_input_bridge_input.human_filled.local.json
cp phase_b_product/commercial_readiness/support_evidence/support_contact_decision_input.template.json phase_b_product/commercial_readiness/support_evidence/support_contact_decision_input.human_filled.local.json
```

## 人工填写后再运行

```bash
python3 scripts/saee_support_contact_human_input_bridge_completion_helper.py --combined-input phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge/support_contact_human_input_bridge_input.human_filled.local.json
python3 scripts/saee_commercial_evidence_sprint_first_owner_input_validator.py --input phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input.human_filled.local.json
python3 scripts/saee_support_contact_approval_input_validator.py --input phase_b_product/commercial_readiness/support_evidence/support_contact_decision_input.human_filled.local.json
python3 scripts/saee_support_contact_readiness_board.py
```

## 明确边界

- `values_saved_by_workspace: false`
- `form_submission_enabled: false`
- `validator_inputs_exported: false`
- `validators_run: false`
- `evidence_collection_authorized: false`
- `blocker_closure_authorized: false`
- `support_contact_configured: false`
- `support_contact_published: false`
- `customer_contacted: false`
- `production_ready: false`
