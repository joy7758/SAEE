# SAEE Commercial Review Batch Human Fill Card v0.1

commercial_review_batch_human_fill_card_v0_1: true
card_scope: human_readable_10_row_review_batch_fill_card_only_no_values_no_import_no_execution
status: ready_for_human_fill_card_review
commercial_status: hold
production_launch_status: hold

## Summary

- fill_card_row_count: 10
- expected_fill_card_row_count: 10
- blank_human_value_row_count: 10
- prefilled_human_value_row_count: 0
- ordinary_user_chinese_fill_guidance: true
- local_static_fill_companion_html: true
- local_static_execution_panel: true
- commercial_fill_card_visual_palette: commercial-warm-graphite-sage-v1
- local_browser_manual_csv_builder: true
- browser_only_csv_text_generation: true
- manual_csv_builder_writes_files: false
- manual_csv_builder_network_calls: false
- manual_csv_builder_imports_workbook: false
- blockers_closed_by_fill_card: 0
- production_ready: false
- customer_validated: false
- product_launched: false

## 给人看的操作说明

这一步只做一件事：让人把 10 行商业化准备信息填到 CSV 里。

1. 打开源 CSV：
   `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_input_template.csv`
2. 只填写两列：
   `human_value_to_enter` 和可选的 `notes_for_human`
3. 也可以在浏览器页面里填写，再点击“生成 CSV 文本”，手动复制保存。
4. 填完后只运行本地 dry-run 检查：
   `python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.py`

不要在这一步导入工作簿、不要收集证据、不要关闭 blocker、不要联系客户、
不要发布产品、不要声明已经生产可用。

## 填完后的本地检查顺序

这些命令只检查本地文件和状态，不导入工作簿、不联系客户、不发布产品、不关闭 blocker。

```bash
python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.py
python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.local.json
python3 scripts/mainline_guard.py
```

## Purpose

This file makes the active 10-row commercial review batch easier for a human to
read before entering values. It is a view over the source template, not the
source of truth for imported values.

For a browser-readable local companion view, open:

`phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_review_batch_human_fill_card.html`

## Human Fill Rows / 人工填写行

### 1. 谁负责确认这个支持入口

- 字段名: assigned_human_owner
- 这行要填什么: 填写已由人确认的负责人姓名、角色或内部负责人标识。
- 什么时候留空: 如果还没有明确负责人，留空。
- review_batch_row_id: QFRB-001
- quick_fill_row_id: QF-001
- blocker_id: support_contact
- input_group: first_owner_input
- expected_value_shape: first-owner coordination field
- fill_instruction: Use human-approved owner, contact-reference, target-date, scope-acknowledgement, or approval-reference text.
- leave_blank_condition: Do not assign an owner or contact anyone from this guidance layer.
- target_json_pointer: /first_owner_input/assigned_human_owner
- human_value_to_enter: 
- notes_for_human: 

### 2. 负责人或内部记录在哪里

- 字段名: owner_contact_reference
- 这行要填什么: 填写内部可追溯记录，例如工单、会议纪要、文档路径或审批编号；不要填未批准的私人联系方式。
- 什么时候留空: 如果没有内部记录或审批来源，留空。
- review_batch_row_id: QFRB-002
- quick_fill_row_id: QF-002
- blocker_id: support_contact
- input_group: first_owner_input
- expected_value_shape: first-owner coordination field
- fill_instruction: Use human-approved owner, contact-reference, target-date, scope-acknowledgement, or approval-reference text.
- leave_blank_condition: Do not assign an owner or contact anyone from this guidance layer.
- target_json_pointer: /first_owner_input/owner_contact_reference
- human_value_to_enter: 
- notes_for_human: 

### 3. 计划哪一天完成确认

- 字段名: target_review_date
- 这行要填什么: 填写计划完成确认的日期，建议使用 YYYY-MM-DD。
- 什么时候留空: 如果还没有目标日期，留空。
- review_batch_row_id: QFRB-003
- quick_fill_row_id: QF-003
- blocker_id: support_contact
- input_group: first_owner_input
- expected_value_shape: first-owner coordination field
- fill_instruction: Use human-approved owner, contact-reference, target-date, scope-acknowledgement, or approval-reference text.
- leave_blank_condition: Do not assign an owner or contact anyone from this guidance layer.
- target_json_pointer: /first_owner_input/target_review_date
- human_value_to_enter: 
- notes_for_human: 

### 4. 负责人是否知道只是在确认支持入口

- 字段名: owner_acknowledged_scope
- 这行要填什么: 填写负责人已确认范围的简短说明，例如只确认支持入口，不代表正式上线。
- 什么时候留空: 如果负责人还没有确认范围，留空。
- review_batch_row_id: QFRB-004
- quick_fill_row_id: QF-004
- blocker_id: support_contact
- input_group: first_owner_input
- expected_value_shape: first-owner coordination field
- fill_instruction: Use human-approved owner, contact-reference, target-date, scope-acknowledgement, or approval-reference text.
- leave_blank_condition: Do not assign an owner or contact anyone from this guidance layer.
- target_json_pointer: /first_owner_input/owner_acknowledged_scope
- human_value_to_enter: 
- notes_for_human: 

### 5. 人工批准记录或会议记录编号

- 字段名: human_approval_reference
- 这行要填什么: 填写人工批准或审查记录的编号、链接名称或文件路径。
- 什么时候留空: 如果没有人工批准记录，留空。
- review_batch_row_id: QFRB-005
- quick_fill_row_id: QF-005
- blocker_id: support_contact
- input_group: first_owner_input
- expected_value_shape: first-owner coordination field
- fill_instruction: Use human-approved owner, contact-reference, target-date, scope-acknowledgement, or approval-reference text.
- leave_blank_condition: Do not assign an owner or contact anyone from this guidance layer.
- target_json_pointer: /first_owner_input/human_approval_reference
- human_value_to_enter: 
- notes_for_human: 

### 6. 谁做了这次人工审查

- 字段名: human_reviewer_name
- 这行要填什么: 填写本次审查人的姓名、角色或内部标识。
- 什么时候留空: 如果没有实际审查人，留空。
- review_batch_row_id: QFRB-006
- quick_fill_row_id: QF-006
- blocker_id: support_contact
- input_group: support_contact_decision_metadata
- expected_value_shape: support-contact decision metadata
- fill_instruction: Use human-reviewed support-contact decision metadata.
- leave_blank_condition: Do not publish support contact details from this guidance layer.
- target_json_pointer: /support_contact_decision_input/human_reviewer_name
- human_value_to_enter: 
- notes_for_human: 

### 7. 审查日期

- 字段名: review_date
- 这行要填什么: 填写实际审查日期，建议使用 YYYY-MM-DD。
- 什么时候留空: 如果还没有实际审查日期，留空。
- review_batch_row_id: QFRB-007
- quick_fill_row_id: QF-007
- blocker_id: support_contact
- input_group: support_contact_decision_metadata
- expected_value_shape: support-contact decision metadata
- fill_instruction: Use human-reviewed support-contact decision metadata.
- leave_blank_condition: Do not publish support contact details from this guidance layer.
- target_json_pointer: /support_contact_decision_input/review_date
- human_value_to_enter: 
- notes_for_human: 

### 8. 以后客户从哪里联系支持

- 字段名: selected_support_contact_channel
- 这行要填什么: 填写已经人工选择的支持入口类型，例如邮箱、表单、工单系统或暂不开放。
- 什么时候留空: 如果支持入口尚未人工决定，留空。
- review_batch_row_id: QFRB-008
- quick_fill_row_id: QF-008
- blocker_id: support_contact
- input_group: support_contact_decision_metadata
- expected_value_shape: support-contact decision metadata
- fill_instruction: Use human-reviewed support-contact decision metadata.
- leave_blank_condition: Do not publish support contact details from this guidance layer.
- target_json_pointer: /support_contact_decision_input/selected_support_contact_channel
- human_value_to_enter: 
- notes_for_human: 

### 9. 一句话说明为什么选这个支持方式

- 字段名: decision_summary
- 这行要填什么: 用一句话说明当前支持入口选择；不要写成已经正式对客户开放。
- 什么时候留空: 如果还没有形成决策，留空。
- review_batch_row_id: QFRB-009
- quick_fill_row_id: QF-009
- blocker_id: support_contact
- input_group: support_contact_decision_metadata
- expected_value_shape: support-contact decision metadata
- fill_instruction: Use human-reviewed support-contact decision metadata.
- leave_blank_condition: Do not publish support contact details from this guidance layer.
- target_json_pointer: /support_contact_decision_input/decision_summary
- human_value_to_enter: 
- notes_for_human: 

### 10. 滥用或异常请求由谁处理

- 字段名: abuse_handling_path_defined
- 这行要填什么: 填写是否已有滥用处理路径及负责人；没有人工确认就留空。
- 什么时候留空: 如果滥用处理路径还没有人工确认，留空。
- review_batch_row_id: QFRB-010
- quick_fill_row_id: QF-010
- blocker_id: support_contact
- input_group: support_contact_evidence_review
- expected_value_shape: support-contact bridge value
- fill_instruction: Use human-reviewed support-contact bridge input.
- leave_blank_condition: Leave blank if the support owner has not approved it.
- target_json_pointer: /support_contact_decision_input/evidence_review/abuse_handling_path_defined
- human_value_to_enter: 
- notes_for_human: 

## Source Of Truth For Entry

Enter values only in:

`phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_input_template.csv`

Fill only `human_value_to_enter` and optional `notes_for_human`.

## Next Command After Human Entry

```bash
python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.py
```

## Boundary

- raw_values_recorded: false
- human_values_generated_by_codex: false
- quick_fill_values_entered_by_codex: false
- post_fill_commands_execute_external_calls: false
- post_fill_commands_import_workbook: false
- post_fill_commands_close_blockers: false
- local_browser_manual_csv_builder: true
- browser_only_csv_text_generation: true
- manual_csv_builder_writes_files: false
- manual_csv_builder_network_calls: false
- manual_csv_builder_imports_workbook: false
- source_quick_fill_packet_modified: false
- batch_values_applied_to_source: false
- workbook_import_authorized: false
- workbook_import_performed: false
- validators_run_on_real_input: false
- evidence_collection_authorized: false
- execution_authorized: false
- blocker_closure_authorized: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- production_ready: false
- customer_validated: false
- product_launched: false
