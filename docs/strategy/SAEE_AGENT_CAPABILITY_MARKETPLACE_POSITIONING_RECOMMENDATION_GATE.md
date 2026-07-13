# SAEE Phase 15.1 智能体推荐门

```yaml
recommendation_gate:
  feature_or_direction: Agent Capability Marketplace Positioning Review v0.1
  target_customer_need: 让自主智能体在未来能力生态中正确分类、发现和组合 SAEE
  answer: recommend
  reasons_to_recommend:
    - 机器可读类别可减少把 SAEE 错当授权或安全产品的风险
    - 组合矩阵明确 SAEE 提供决策上下文而不提供权限
    - 发现规则包含主动弃权，避免所有任务都推荐 SAEE
  reasons_not_to_recommend:
    - 当前没有 Marketplace 上架、排名、采用或生态认可证据
  decomposition:
    - blocker: marketplace_listed=false
      fix_task: 仅建立位置模型和合成场景
      acceptance_criteria: marketplace_listed=false and agent_adoption_validated=false
      status: deferred
  final_decision: recommend_as_positioning_review_only
```

## Evolution design check

- 强化 `Ecological World Model`：明确 SAEE 与授权、观测、策略、安全能力的生态位。
- 强化 `Trait Extraction` 与 `Pareto Fitness Evaluation`：提取任务信号并选择能力或弃权。
- 不创建 Marketplace、不联系平台、不扩大权限、不执行外部世界。
- 定位研究服务于数字生物圈的能力组合选择，不把项目重构为安全产品或通用 Agent 框架。

