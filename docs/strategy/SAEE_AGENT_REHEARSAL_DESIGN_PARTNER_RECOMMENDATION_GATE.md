# SAEE Agent Rehearsal Design Partner Protocol Recommendation Gate

```yaml
recommendation_gate:
  feature_or_direction: SAEE Agent Rehearsal Design Partner Validation Protocol v0.1
  target_customer_need: 验证企业是否愿意在 Agent 上线前先进行受控演练和证据审查
  initial_answer: conditional
  reasons_to_recommend:
    - Phase 6.1 v0.2 已记录三次百度千帆真实推理模型在完全合成世界中的演练
    - Phase 6.1 v0.3 已记录一次有状态、多步骤 SaaS 发布世界演练和连续状态摘要链
    - Phase 6.2 到 6.4 已形成评估、Benchmark 和 Tool 调用
    - 全中文演示可让中国市场目标角色理解完整流程
    - 协议先问现状再演示，降低引导偏差
  reasons_not_to_recommend:
    - 尚无外部访谈结果
    - 尚未验证客户 Agent、客户环境或付费意愿
    - 当前 Demo 的世界、工具和数据全部为合成材料
  decomposition:
    - blocker: 旧协议只展示静态 Evidence Review
      subsystem: commercial_validation
      fix_task: 升级为可运行 Rehearsal、Trace、Benchmark 和 MCP 演示
      acceptance_criteria: 本地 Demo 输出三场景、20-case metrics 和两 Tool discovery
      status: fixed
    - blocker: 外部问题认可未知
      subsystem: global_sensing
      fix_task: 人工批准后执行至少五个匿名问题访谈
      acceptance_criteria: 正负结果完整记录且不采集真实数据
      status: deferred
    - blocker: 真实 Agent 和客户环境价值未知
      subsystem: sandbox_development
      fix_task: 只有问题访谈通过后另建 customer-controlled sandbox protocol
      acceptance_criteria: 独立同意、安全、数据和执行批准
      status: deferred
    - blocker: 原 Demo 只展示固定规则 Agent
      subsystem: counterfactual_simulation
      fix_task: 改为展示千帆真实推理模型自主工具选择的已记录运行
      acceptance_criteria: 三个 live run、隐藏评分剖面 3/3、external_world_actions=0
      status: fixed
    - blocker: 原 Demo 缺少多步骤业务世界
      subsystem: ecological_world_model
      fix_task: 增加读取变更、运行测试、检查发布状态和停止部署的真实千帆演练
      acceptance_criteria: provider_rounds=4、state_transitions=3、deployment_tool_called=false
      status: fixed
  final_decision: recommend_for_protocol_review_only
  external_validation_recommendation: conditional
  evidence:
    docs:
      - docs/commercial/SAEE_AGENT_REHEARSAL_DESIGN_PARTNER_PROTOCOL.md
      - docs/commercial/SAEE_AGENT_REHEARSAL_DESIGN_PARTNER_DEMO.md
    tests:
      - python3 scripts/saee_agent_rehearsal_design_partner_protocol_smoke.py
    examples:
      - scripts/saee_design_partner_rehearsal_demo.py
```

本门只批准协议进入人工审查，不批准联系客户、执行访谈、Pilot 或外部 Agent。
