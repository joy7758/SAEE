# SAEE 真实客户验证一页执行卡 v0.1

当前唯一不能由 Codex 代办的正式商用阻塞点是：`customer_validated`。

这张卡只把现有材料串成一条人工路径，不新增问题，不自动联系客户，
不导入结果，不关闭 blocker，也不声明 SAEE 已生产可用。

## 6 步人工路径

| 步骤 | 人要做什么 | 打开哪个文件 |
| --- | --- | --- |
| 1 | 先确认对方是不是目标用户 | `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/PARTICIPANT_SCREENING_CHECKLIST.md` |
| 2 | 人工发送邀请，不由 Codex 联系 | `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/INVITATION_MESSAGE_DRAFT.md` |
| 3 | 会前说明边界：不收秘密、不收生产数据、不披露私有核心、不承诺生产可用 | `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/CONSENT_AND_BOUNDARY_SCRIPT.md` |
| 4 | 如果时间很短，先问 3 分钟最小表 | `phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_3_minute_worksheet/customer_validation_3_minute_worksheet.md` |
| 5 | 会后补完整中文答卷，并保存为目标答卷文件 | `phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_plain_chinese_worksheet/customer_validation_plain_chinese_worksheet.md` -> `phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_intake_helper/customer_validation_answers.human_filled.md` |
| 6 | 跑一条本地 pipeline：它会先 preflight，再转换 JSON，再进入后处理 | `python3 scripts/saee_customer_validation_answer_to_evidence_pipeline.py --apply` |

## 完整录入入口

如果要直接整理最终 session-entry JSON，也可以打开：

`phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry_workbench.html`

目标输出路径必须是：

`phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json`

## 当前状态

- current_preflight_status: `hold_human_answer_sheet_missing`
- human_answer_input_exists: `False`
- target_session_entry_exists: `False`
- customer_validated: false
- production_ready: false
- product_launched: false
- private_core_exposed: false
- blockers_closed_by_run_card: 0
