# SAEE Agent Rehearsal Runtime MVP v0.1 Recommendation Gate

```yaml
recommendation_gate:
  feature_or_direction: SAEE Agent Rehearsal Runtime MVP v0.1
  target_customer_need: 在 Agent 上线前通过受控场景观察其行为并形成可追踪演练记录
  initial_answer: conditional
  reasons_to_recommend:
    - Rehearsal 是商业战略规定的第一产品入口
    - 现有 Scenario、Lifecycle、Observation 和 Evidence 管线可复用
    - 本地合成 Runtime 能先验证 run-to-trace-to-export 主链
  reasons_not_to_recommend:
    - 真实外部 Agent Adapter 尚无安全且可复现的执行边界
    - 外部 provider credential、成本、隐私和网络授权没有进入本任务
    - Trace 不能自动成为 Evidence 或部署结论
  decomposition:
    - blocker: 缺少可执行的 Agent Rehearsal 主链
      subsystem: sandbox_development_counterfactual_simulation
      fix_task: 实现固定本地 Agent、Scenario Runner、Trace Collector 和 Evidence Export
      acceptance_criteria: 三个受控场景确定性执行且零网络、零 subprocess、零外部副作用
      status: fixed
    - blocker: 真实外部 Agent 尚未接入
      subsystem: sandbox_development
      fix_task: 后续建立独立 External Agent Adapter gate
      acceptance_criteria: provider、credential、cost、privacy、sandbox 和 stop authority 全部获批
      status: deferred
    - blocker: run evidence 尚未被统一 Agent API 评估
      subsystem: pareto_fitness_evaluation
      fix_task: Phase 6.2 实现 evaluate_agent_run
      acceptance_criteria: 只输出 evidence adequacy 与缺口，不输出安全或部署批准
      status: deferred
  final_decision: recommend_for_local_controlled_synthetic_runtime_only
  customer_product_recommendation: conditional
  evidence:
    docs:
      - docs/architecture/SAEE_AGENT_REHEARSAL_RUNTIME_MVP.md
    tests:
      - python3 scripts/saee_agent_rehearsal_runtime_smoke.py
    examples:
      - agent-interface/rehearsal/scenarios/baseline-metadata-inspection.json
      - agent-interface/rehearsal/scenarios/tool-timeout-abstention.json
      - agent-interface/rehearsal/scenarios/instruction-conflict-refusal.json
```

本门没有批准网络、真实外部 Agent、客户数据、生产工具、Capability Alpha、公开
MCP 或商业交付。
