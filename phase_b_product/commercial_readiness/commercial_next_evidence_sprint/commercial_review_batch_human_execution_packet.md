# SAEE 10 行人工执行包

Commercial Review Batch Human Execution Packet v0.1

这是给人看的 10 行执行包。它只帮助人工填写当前商用阻塞项的 10 行模板。

## 当前状态

- status: ready_for_human_10_row_entry
- commercial_status: hold
- production_ready: false
- customer_validated: false
- product_launched: false
- blockers_closed_by_packet: 0
- values_generated_by_codex: false
- human_values_filled_by_codex: false

## 真正填写位置

`phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_input_template.csv`

只填写两列：

- `human_value_to_enter`
- `notes_for_human`（可选）

不要改 `review_batch_row_id`、`quick_fill_row_id`、`blocker_id`、`target_json_pointer` 等结构列。

## 10 行填写清单

| 行 | 字段 | 通俗说明 | 怎么填 | 什么时候留空 |
| --- | --- | --- | --- | --- |
| 1 | `assigned_human_owner` | 谁负责确认支持入口 | 填已确认的负责人姓名、角色或内部负责人标识。 | 没有明确负责人就留空。 |
| 2 | `owner_contact_reference` | 负责人或内部记录在哪里 | 填内部可追溯记录，例如工单、会议纪要、文档路径或审批编号。 | 没有内部记录或审批来源就留空。 |
| 3 | `target_review_date` | 计划哪天确认完 | 填目标日期，建议 YYYY-MM-DD。 | 没有目标日期就留空。 |
| 4 | `owner_acknowledged_scope` | 负责人是否确认范围 | 填负责人已确认的范围，例如只确认支持入口，不代表正式上线。 | 负责人还没确认范围就留空。 |
| 5 | `human_approval_reference` | 人工批准记录编号 | 填人工批准、会议纪要或审查记录编号。 | 没有人工批准记录就留空。 |
| 6 | `human_reviewer_name` | 谁做了本次审查 | 填本次人工审查人的姓名、角色或内部标识。 | 没有实际审查人就留空。 |
| 7 | `review_date` | 审查日期 | 填实际审查日期，建议 YYYY-MM-DD。 | 还没审查就留空。 |
| 8 | `selected_support_contact_channel` | 客户以后从哪里找支持 | 填人工选择的支持入口类型，例如邮箱、表单、工单系统或暂不开放。 | 支持入口尚未人工决定就留空。 |
| 9 | `decision_summary` | 一句话说明选择原因 | 用一句话说明当前支持入口决策，不要写成已经对客户正式开放。 | 还没有形成决策就留空。 |
| 10 | `abuse_handling_path_defined` | 滥用或异常请求由谁处理 | 填是否已有滥用处理路径及负责人；没有人工确认就留空。 | 滥用处理路径还没人工确认就留空。 |

## 填完后的本地检查顺序

填完 10 行后先跑：

1. `python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.py`
2. `python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.local.json`
3. `python3 scripts/mainline_guard.py`
4. `make check-commercial-review-batch-human-execution-packet`

这些检查不调用外部服务，不导入工作簿，不关闭 blocker。

## 明确禁止

- 不要让 Codex 代填真实负责人、邮箱、工单、日期或审批记录。
- 不要导入工作簿。
- 不要关闭 blocker。
- 不要联系客户。
- 不要声称已经正式商用、客户验证完成或生产可用。

## 下一步

Open commercial_review_batch_human_execution_packet.html or .md, then fill only human_value_to_enter and optional notes_for_human in the source 10-row CSV. After all 10 values are present, run the local post-fill dry-run command before any separate workbook import, evidence collection, or blocker-closure request.
