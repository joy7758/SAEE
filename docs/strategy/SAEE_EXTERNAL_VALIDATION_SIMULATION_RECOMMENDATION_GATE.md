# SAEE Phase 12.1 智能体推荐门

```yaml
recommendation_gate:
  feature_or_direction: External Validation Simulation v0.1
  target_customer_need: 在真实参与者进入前验证授权、范围、证据、反馈、退出和终止控制流
  answer: recommend
  reasons_to_recommend:
    - 合成参与者可重复触发成功、阻断、拒绝和终止路径
    - 固定本地契约可被智能体发现、理解和组合
    - 失败路径为回滚免疫机制提供可验证输入
  reasons_not_to_recommend:
    - 模拟结果不能证明外部生态兼容、采用或生产能力
  decomposition:
    - blocker: 没有真实参与者和外部证据
      subsystem: Sandbox Development / Evolutionary Archive
      fix_task: 保持 external_validation=false 与 real_participants=0
      acceptance_criteria: 模拟通过且所有外部真值保持 false
      status: deferred
  final_decision: recommend_for_synthetic_process_simulation_only
  evidence:
    docs:
      - docs/ecosystem/SAEE_EXTERNAL_VALIDATION_SIMULATION.md
    tests:
      - scripts/saee_external_validation_simulation_smoke.py
    examples:
      - agent-interface/ecosystem/external-validation-simulation/
```

## Evolution design check

- 强化 `Sandbox Development`、`Pareto Fitness Evaluation`、`Evolutionary Archive / Rollback Immune System`。
- 验证选择、拒绝、终止和归档路径，不执行外部世界。
- 不联网、不扩权、不接收客户数据，不复制外部代码或敏感载荷。
- 这是生态控制流的合成发育测试，不把 SAEE 重构为审计优先系统。

