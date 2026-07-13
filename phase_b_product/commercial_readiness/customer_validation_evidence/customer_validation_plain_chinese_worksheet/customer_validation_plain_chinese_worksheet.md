# SAEE 真实客户验证中文填写表 v0.1

用途：把一次真实外部客户或目标用户访谈，整理成可导入的
`customer_validation_answers.human_filled.md`。

这不是内部自评表。只有真实外部客户或目标用户看过 SAEE、听懂用途并给出反馈后，才能填写。

## 访谈主问题

| 字段 | 要问人的话 | 填写建议 |
| --- | --- | --- |
| `session_id` | 这次访谈编号是什么？ | 例如 ECV-001 |
| `session_date` | 访谈日期是哪一天？ | 格式 YYYY-MM-DD |
| `human_reviewer_name` | 谁负责记录和确认这次访谈？ | 填写你的名字 |
| `participant_role` | 对方是什么角色？ | 例如 AI 产品负责人、算法工程师、创始人、运营负责人 |
| `team_type` | 对方属于哪类团队？ | 例如 初创团队、企业研发团队、个人开发者 |
| `current_evaluation_method` | 他们现在怎么判断哪个 agent / 工作流 / 策略更可靠？ | 写一句话即可 |
| `candidate_count` | 他们通常需要比较几个候选方案？ | 填写数字，必须大于 0 |
| `understanding_score` | 听完 SAEE 后，对方是否理解它解决什么问题？ | 1-5 分，5 表示非常理解 |
| `trust_score` | 对方是否信任这个评测和推荐结果？ | 1-5 分 |
| `decision_influence_score` | 这个结果是否会影响对方部署、暂缓或重测的决定？ | 1-5 分 |
| `repeat_usage_intent_score` | 对方是否愿意之后继续使用或复测？ | 1-5 分 |
| `time_to_value_minutes` | 对方从开始体验到理解价值大约用了几分钟？ | 填写分钟数 |
| `willing_to_test_own_candidates` | 对方是否愿意用自己的候选方案再测一次？ | true/false |
| `top_objection` | 对方最大的疑问或反对意见是什么？ | 写一句话 |
| `evidence_missing` | 对方觉得还缺什么证据才更愿意采用？ | 写一句话 |
| `notes` | 这次访谈最关键的一句话反馈是什么？ | 写一句话 |
| `human_source_context` | 这条记录来自什么真实场景？ | 例如 真实目标用户访谈，不是内部自评 |
| `human_entry_confirmed` | 你是否确认以上内容来自真实外部客户或目标用户会话？ | true/false |

## 边界确认

| 字段 | 必须确认的边界 | 填写方式 |
| --- | --- | --- |
| `no_secrets_collected` | 是否确认没有收集密码、密钥、客户秘密？ | 只有事实成立才填 `true` |
| `no_production_data_collected` | 是否确认没有收集生产数据？ | 只有事实成立才填 `true` |
| `no_customer_data_uploaded` | 是否确认没有要求客户上传真实业务数据？ | 只有事实成立才填 `true` |
| `no_private_core_disclosed` | 是否确认没有披露 SAEE 私有核心？ | 只有事实成立才填 `true` |
| `no_production_ready_claim_made` | 是否确认没有声称 SAEE 已生产可用？ | 只有事实成立才填 `true` |

## 人工复核项

| 字段 | 人工复核项 | 填写方式 |
| --- | --- | --- |
| `real_customer_or_target_user_feedback_recorded` | 确实记录了真实外部客户或目标用户反馈 | 复核通过填 `true` |
| `customer_role_and_segment_recorded` | 记录了对方角色和团队类型 | 复核通过填 `true` |
| `customer_problem_fit_reviewed` | 确认对方问题和 SAEE 适配场景有关 | 复核通过填 `true` |
| `recommendation_output_understood` | 对方理解 SAEE 输出的推荐/排序含义 | 复核通过填 `true` |
| `decision_usefulness_observed` | 观察到 SAEE 对部署/暂缓/重测决策有帮助 | 复核通过填 `true` |
| `deployment_decision_value_observed` | 观察到部署前决策价值 | 复核通过填 `true` |
| `failure_summary_usefulness_observed` | 观察到失败摘要有帮助 | 复核通过填 `true` |
| `pain_point_fit_observed` | 观察到对方确有长期稳定性评测痛点 | 复核通过填 `true` |
| `feedback_form_completed` | 访谈记录已填写完整 | 复核通过填 `true` |
| `negative_feedback_recorded` | 负面反馈或疑问也已记录 | 复核通过填 `true` |
| `top_objection` | 最大疑问已记录在 top_objection 字段 | 复核通过填 `true` |
| `evidence_missing` | 缺失证据已记录在 evidence_missing 字段 | 复核通过填 `true` |
| `boundary_flags_reviewed` | 已复核边界标记 | 复核通过填 `true` |
| `claim_scope_approved` | 已确认没有扩大产品能力声明 | 复核通过填 `true` |
| `no_customer_secrets_collected` | 未收集客户秘密 | 复核通过填 `true` |
| `no_customer_upload_required` | 未要求客户上传真实业务数据 | 复核通过填 `true` |
| `no_private_core_disclosed` | 未披露私有核心 | 复核通过填 `true` |
| `no_production_ready_claim_added` | 未新增生产可用声明 | 复核通过填 `true` |
| `no_public_launch_claim_added` | 未新增公开发布声明 | 复核通过填 `true` |
| `pilot_result_template_completed` | 会话结果模板已完成 | 复核通过填 `true` |
| `pilot_result_reviewed_by_human` | 会话结果已由人复核 | 复核通过填 `true` |
| `success_criteria_applied` | 已按成功标准评估 | 复核通过填 `true` |
| `go_hold_pivot_decision_recorded` | 已记录 go/hold/pivot 判断 | 复核通过填 `true` |
| `permission_to_use_feedback_recorded` | 已记录是否允许使用反馈 | 复核通过填 `true` |
| `customer_validation_record_approved_by_human` | 最终记录已由人确认 | 复核通过填 `true` |
| `reviewer_approved_validation_claim` | 审查者确认可以如何表述验证结论 | 复核通过填 `true` |

## 可复制的答卷骨架

```text
# Copy these lines into customer_validation_answers.human_filled.md after the real session.
session_id:
session_date:
human_reviewer_name:
participant_role:
team_type:
current_evaluation_method:
candidate_count:
understanding_score:
trust_score:
decision_influence_score:
repeat_usage_intent_score:
time_to_value_minutes:
willing_to_test_own_candidates:
top_objection:
evidence_missing:
notes:
human_source_context:
human_entry_confirmed:
no_secrets_collected:
no_production_data_collected:
no_customer_data_uploaded:
no_private_core_disclosed:
no_production_ready_claim_made:
real_customer_or_target_user_feedback_recorded: true
customer_role_and_segment_recorded: true
customer_problem_fit_reviewed: true
recommendation_output_understood: true
decision_usefulness_observed: true
deployment_decision_value_observed: true
failure_summary_usefulness_observed: true
pain_point_fit_observed: true
feedback_form_completed: true
negative_feedback_recorded: true
boundary_flags_reviewed: true
claim_scope_approved: true
no_customer_secrets_collected: true
no_customer_upload_required: true
no_private_core_disclosed: true
no_production_ready_claim_added: true
no_public_launch_claim_added: true
pilot_result_template_completed: true
pilot_result_reviewed_by_human: true
success_criteria_applied: true
go_hold_pivot_decision_recorded: true
permission_to_use_feedback_recorded: true
customer_validation_record_approved_by_human: true
reviewer_approved_validation_claim: true
```
