# SAEE Agent Readiness Architecture v1.0 Recommendation Gate

```yaml
recommendation_gate:
  feature_or_direction: SAEE Agent Readiness Architecture v1.0
  target_customer_need: 在真实业务前对 Agent 进行受控演练，并用证据支持上线准备判断
  initial_answer: conditional
  reasons_to_recommend:
    - 现有 Evidence Adequacy、Observation、Case Corpus 与 Agent-Native 机器入口可复用
    - Agent Rehearsal 是清晰、可演示且可形成项目制交付的第一产品入口
    - canonical Digital Biosphere Evolution Engine 身份可以保持不变
  reasons_not_to_recommend:
    - 当前没有完整 Agent Rehearsal Runtime
    - Phase 4 和 Phase 5 的治理资产曾被过度前置
    - 本地 MCP 和证据评估不能代表完整 Agent Readiness Platform
  decomposition:
    - blocker: 产品身份与 canonical 工程身份混杂
      subsystem: architecture
      fix_task: 明确工程核心、商业产品、产品入口、护城河和未来接口
      acceptance_criteria: 人类文档与机器清单使用相同五项身份
      status: fixed
    - blocker: 现有 Evidence/Pilot 资产缺少统一归位
      subsystem: evolutionary_archive_rollback_immune_system
      fix_task: 冻结为 Governance and Evidence Control Plane 并声明不是 Runtime
      acceptance_criteria: 资产映射和 truth boundary 可机器验证
      status: fixed
    - blocker: Agent Rehearsal Runtime 缺失
      subsystem: sandbox_development_counterfactual_simulation
      fix_task: Phase 6.1 实现固定场景、受控 Adapter、Trace Collector 与 Evidence Export
      acceptance_criteria: 一个获批本地 Agent 在隔离合成场景中完成 run-to-evidence 闭环
      status: deferred
    - blocker: evaluate_agent_run 缺少真实 run evidence 上游
      subsystem: agent_native_interface
      fix_task: Phase 6.2 在 Phase 6.1 验收后实现 bounded capability alpha
      acceptance_criteria: 调用只评估 run evidence adequacy 且不产生安全或部署批准
      status: deferred
  final_decision: recommend_for_architecture_reunification_only
  product_recommendation_now: conditional
  evidence:
    docs:
      - docs/architecture/FINAL_ARCHITECTURE_SPEC.md
      - docs/architecture/SAEE_V3_SYSTEM_ARCHITECTURE_SPEC.md
      - docs/architecture/SAEE_AGENT_READINESS_ARCHITECTURE_V1.md
    tests:
      - python3 scripts/saee_agent_readiness_architecture_smoke.py
    examples: []
```

## Required Design Check

1. 强化 `Ecological World Model`、`Counterfactual Simulation`、`Sandbox
   Development`、`Pareto Fitness Evaluation` 与 `Evolutionary Archive /
   Rollback Immune System` 的明确依赖关系。
2. Phase 6.0 改善资产归位和回滚免疫边界；Phase 6.1 才改善真实受控演练。
3. 保留许可证、供应链、权限、隔离和禁止未知代码执行边界。
4. `audit_first_reframe=false`；Evidence Intelligence 是护城河和免疫子系统，
   不是工程核心。

本门只批准架构重统一。它没有批准 Runtime 开发以外的外部执行，也没有把完整
产品推荐结论提升为 `recommend`。
