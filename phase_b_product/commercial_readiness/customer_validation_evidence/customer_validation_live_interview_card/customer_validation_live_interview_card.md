# SAEE Customer Validation Live Interview Card v0.1

Status: `ready_for_real_customer_interview`.

This card contains only the 13 questions that must be answered by a real
customer or target user. It is meant for a short live conversation. It does not
contact customers, infer answers, write evidence, close blockers, or claim
customer validation.

## Boundary

- customer_validated=false
- production_ready=false
- product_launched=false
- private_core_exposed=false
- blockers_closed_by_card=0

## 13 Customer Questions

| # | Field | Ask this in plain Chinese |
| --- | --- | --- |
| 1 | `participant_role` | 你现在负责什么？ |
| 2 | `team_type` | 你所在团队大概是什么类型？ |
| 3 | `current_evaluation_method` | 你现在怎么判断哪个 agent、工作流或策略版本更靠谱？ |
| 4 | `candidate_count` | 你通常要比较几个候选方案？ |
| 5 | `understanding_score` | 听完介绍后，你能否用自己的话说清 SAEE 是做什么的？1-5 分。 |
| 6 | `trust_score` | 你现在对这个结果的可信度是多少？1-5 分。 |
| 7 | `decision_influence_score` | 这个结果会不会影响你部署、暂缓或重测的决定？1-5 分。 |
| 8 | `repeat_usage_intent_score` | 你是否愿意后续重复使用这类评测？1-5 分。 |
| 9 | `time_to_value_minutes` | 你大概花了几分钟理解它是否有用？ |
| 10 | `willing_to_test_own_candidates` | 你愿不愿意用自己的候选方案再测一次？true/false。 |
| 11 | `top_objection` | 你最大的疑问或反对点是什么？ |
| 12 | `evidence_missing` | 还缺什么证据，你才更愿意继续试？ |
| 13 | `notes` | 请记录对方最关键的一句话反馈。 |

## Copy Answers Here First

Use:

`phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_live_interview_card/customer_validation_live_interview_answer_block.md`

Then merge the answers into:

`phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_intake_helper/customer_validation_answers.human_filled.md`
