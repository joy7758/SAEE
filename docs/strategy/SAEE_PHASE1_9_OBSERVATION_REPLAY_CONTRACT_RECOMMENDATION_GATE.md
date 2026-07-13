# SAEE Phase 1.9 Observation Replay Contract Recommendation Gate

```yaml
recommendation_gate:
  feature_or_direction: SAEE Observation Replay Contract v0.1
  target_customer_need: 在任何脱敏离线回放前固定来源、目的、Consent、Permission、内容边界、转换来源、环境与人工停止权
  answer: recommend
  recommendation_scope: local_synthetic_governance_contract_only
  reasons_to_recommend:
    - Observation Envelope 通过文件摘要和 observation_id 被稳定引用
    - Consent 与 Data-use Permission 引用成为必填门禁
    - Content Boundary 明确排除 hidden reasoning、private chain of thought、internal state、raw prompt 和 raw output
    - Transformation 必须携带 redaction 和 provenance references
    - Replay 固定为 manual metadata reconstruction，不运行 Agent、Tool 或 Network
    - Deployment、Evidence、Authenticity 和 Authorization 均不能从 Replay 自动推导
  deferred_blockers:
    - real_consent_verification
    - data_use_permission_verification
    - independent_sanitization_and_anonymization_review
    - transformation_provenance_verification
    - replay_engine
    - replay_to_evaluation_input_mapping
    - customer_validation
    - production_readiness
  final_decision: 推荐作为 Phase 1.9 本地合成治理契约；不推荐解释为 Replay 已执行、外部数据获批或 Phase 2 已启动
```

## Required Design Check

1. 强化 `Global Sensing`、`Counterfactual Simulation` 和 `Evolutionary Archive / Rollback Immune System` 的输入门禁。
2. 改善可控重建、来源追踪和停止权，不修改 canonical architecture 或执行外部世界。
3. 保留安全、许可、隐私、Consent、供应链和权限边界；所有真实验证保持 false。
4. Replay Contract 是感知输入治理，不把项目改造成执行平台或 audit-first 产品。

