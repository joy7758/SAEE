# SAEE 3-Minute Customer Validation Field Map

This file maps the short Chinese interview questions to the larger customer
validation answer sheet. It is a friction-reduction surface only.

## Short Questions

| 字段 | 直接问对方的话 | 怎么填 |
| --- | --- | --- |
| `participant_role` | 你现在负责什么？ | 例如 产品负责人 / 算法工程师 / 创始人 / 运营负责人 |
| `current_evaluation_method` | 你现在怎么判断哪个 agent、工作流或策略更靠谱？ | 一句话即可 |
| `candidate_count` | 你通常要比较几个候选方案？ | 填写数字，例如 3 |
| `understanding_score` | 听完后，你能否用自己的话说清 SAEE 是做什么的？ | 1-5 分，5 表示非常清楚 |
| `decision_influence_score` | 这个结果会不会影响你部署、暂缓或重测的决定？ | 1-5 分 |
| `willing_to_test_own_candidates` | 你愿不愿意用自己的候选方案再测一次？ | true/false |
| `top_objection` | 你最大的疑问是什么？ | 一句话 |
| `evidence_missing` | 还缺什么证据，你才更愿意继续试？ | 一句话 |

## Boundary Confirmations

| 字段 | 必须确认 | 怎么填 |
| --- | --- | --- |
| `no_private_core_disclosed` | 没有披露 SAEE 私有核心 | 成立才填 `true` |
| `no_production_ready_claim_made` | 没有声称 SAEE 已生产可用 | 成立才填 `true` |
| `no_customer_data_uploaded` | 没有要求客户上传真实业务数据 | 成立才填 `true` |

## Important Gap

The full answer sheet is still required before any import or customer
validation claim. Current preflight status: `hold_human_answer_sheet_missing`.
