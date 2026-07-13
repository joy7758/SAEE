# SAEE v3.0 System Architecture Recommendation Gate

```yaml
recommendation_gate:
  feature_or_direction: SAEE v3.0 Deployment Assurance Projection
  target_customer_need: 在 AI Agent 进入真实业务前获得场景化模拟、证据、风险和部署决策材料
  answer: recommend
  reasons_to_recommend:
    - 九层 contract 补齐 Governance、Observation、Risk 和 Decision 之间的缺口
    - 环境模拟与长期漂移映射到既有 Digital Biosphere Evolution Engine 优势
    - Evidence Adequacy 可以成为风险与部署建议的 fail-closed gate
    - 场景限定建议比全局排行榜更接近客户决策问题
  reasons_not_to_recommend:
    - 通用 Risk Model 尚未实现或外部验证；Phase 1 只有本地合成 Risk Estimate reference
    - deployment-grounded replay、runtime adapter 和 feedback loop 不存在
    - 当前没有客户数据、客户验证、生产监控或商业 readiness
    - 原始九层若作为 canonical core 会违反 not-audit-first 和 no-external-execution 边界
  decomposition:
    - blocker: 架构权威边界未获得审查确认
      subsystem: Meta-Protocol / Architecture governance
      fix_task: 确认 v3 仅为 L3 Deployment Assurance Projection
      acceptance_criteria: FINAL_ARCHITECTURE_SPEC 不被替换且 reverse dependency 仍被禁止
      status: resolved
    - blocker: 评分到业务风险之间没有实现
      subsystem: Ecological World Model / Pareto Fitness Evaluation
      fix_task: 未来单独实现 local synthetic risk-model vertical slice
      acceptance_criteria: 公式、阈值、uncertainty、evidence gate 和 negative cases 可重复验证
      status: resolved_local_synthetic_reference_only
    - blocker: 真实执行和 feedback 权限不存在
      subsystem: Sandbox Development / Global Sensing
      fix_task: 保持外部客户沙盒与 consent-first feedback gate，不在当前实现
      acceptance_criteria: source、permission、privacy、sandbox、rollback 和 execution ownership 均有批准证据
      status: deferred
  final_decision: 推荐并接受该 L3 架构投影；推荐范围仅包括 Phase 1 本地合成垂直切片，不代表完整架构、客户或生产产品已实现
  evidence:
    docs:
      - docs/architecture/SAEE_V3_SYSTEM_ARCHITECTURE_SPEC.md
      - docs/architecture/SAEE_V3_EVOLUTION_PROPOSAL.md
    tests:
      - scripts/saee_v3_architecture_smoke.py
    examples:
      - agent-interface/architecture/saee-v3-system-architecture.v0.1.json
```

## Required Design Check

1. 强化 Global Sensing、World Model、Counterfactual Simulation、Sandbox、Pareto Fitness 和 Archive/Rollback。
2. 改善感知、模拟、选择、档案和回滚，但不直接运行外部 Agent。
3. 保留安全、许可、供应链和权限边界；真实执行归客户或获批研究沙盒所有。
4. 通过 L3 projection 避免 audit-first 重构；canonical Digital Biosphere Evolution Engine 保持不变。
