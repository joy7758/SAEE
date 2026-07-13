# SAEE Phase 1.5 Evidence Case Corpus Recommendation Gate

```yaml
recommendation_gate:
  feature_or_direction: SAEE Evidence Case Benchmark Corpus v0.1
  target_customer_need: 验证同一 Evidence Case 转换链是否能稳定覆盖多类合成部署压力
  answer: recommend
  recommendation_scope: local_synthetic_corpus_only
  reasons_to_recommend:
    - 增加 baseline、context drift、tool failure、instruction conflict 和 adversarial input 案例密度
    - 不修改严格 v0.1 Source Contract schema
    - 复用现有 Case Builder 和 Evidence Adequacy evaluator
    - Transformation Integrity Check 防止输入契约、Evidence 引用和边界在派生时丢失
    - 不接入真实 Agent、网络、客户数据或外部 pilot
  deferred_blockers:
    - deployment_grounded_cases
    - externally_calibrated_risk_model
    - customer_controlled_sandbox
    - external_validation
    - customer_validation
    - production_readiness
  final_decision: 推荐作为本地合成基准库；不推荐解释为真实 Agent 验证、自动部署决策或产品 readiness
```

## Required Design Check

1. 强化 `Environment Simulation`、`Counterfactual Simulation`、`Pareto Fitness Evaluation` 和 `Evolutionary Archive / Rollback Immune System`。
2. 改善场景覆盖、选择依据与可回放知识积累，不改变 L1/L2 或 canonical 三层架构。
3. 所有输入固定、合成、离线；不执行未知代码、不安装依赖、不扩权、不访问网络。
4. Evidence 与 Corpus 支撑演化闭环，但不把项目重构为 audit-first benchmark 产品。

