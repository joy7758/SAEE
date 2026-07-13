# SAEE Customer Validation Required Questions

Use these questions only during a real external customer or target-user session.
Do not answer them from internal self-review.

1. `session_id` - 这次访谈的内部编号是什么？例如 ECV-001。
2. `session_date` - 访谈日期是什么？格式 YYYY-MM-DD。
3. `human_reviewer_name` - 谁完成并确认了这次访谈记录？
4. `participant_role` - 对方是什么角色？例如 创始人、AI 产品负责人、算法工程师、运营负责人。
5. `team_type` - 对方团队类型是什么？例如 初创团队、企业研发团队、个人开发者。
6. `current_evaluation_method` - 对方现在如何评估 AI agent、工作流或策略版本？
7. `candidate_count` - 对方通常需要比较几个 agent / workflow / policy 候选方案？
8. `understanding_score` - 对方是否理解 SAEE 的用途？1-5 分。
9. `trust_score` - 对方是否信任这个评测/推荐结果？1-5 分。
10. `decision_influence_score` - SAEE 是否会影响对方部署/暂缓/重测决策？1-5 分。
11. `repeat_usage_intent_score` - 对方是否愿意之后继续使用或复测？1-5 分。
12. `time_to_value_minutes` - 对方从开始体验到理解价值大约用了多少分钟？
13. `willing_to_test_own_candidates` - 对方是否愿意用自己的候选方案再测一次？true/false。
14. `top_objection` - 对方最大的疑问或反对意见是什么？
15. `evidence_missing` - 对方认为还缺什么证据才更愿意采用？
16. `notes` - 一句话记录对方最关键反馈。

Boundary confirmations must remain true only if the session actually avoided secrets, production data, uploads, private-core disclosure, and production-ready claims.
