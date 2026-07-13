# SAEE Capability Service Package v1.0 智能体推荐门

```yaml
recommendation_gate:
  feature_or_direction: SAEE Capability Service Package v1.0
  target_customer_need: 让智能体发现、理解并组合 SAEE 的本地可靠性评估能力
  answer: recommend
  recommendation_scope: local_contract_only_agent_discovery_alpha
  reasons_to_recommend:
    - 现有 evaluate_agent_run 与 evaluate_evidence_adequacy 已有本地只读实现和离线验证
    - 标准化 Package 可以减少智能体在 Manifest、Registry、CLI 和 MCP 原型之间的检索成本
    - Package 明确区分已实现能力、契约预留能力和未提供的公网能力
  reasons_not_to_recommend:
    - 不推荐把本 Package 表述为公网 API、正式 MCP 服务或生产服务
    - 不推荐把本 Package 用作安全认证、部署批准、模型排名或市场采用证据
  decomposition:
    - blocker: 尚无公网 API
      subsystem: Global Sensing
      fix_task: 仅发布 OpenAPI 描述，不创建或声明公网 endpoint
      acceptance_criteria: network_api_available=false
      status: deferred
    - blocker: 尚无标准 MCP transport
      subsystem: Trait Extraction
      fix_task: 仅映射现有本地 Tool 和未来 rehearse_agent 契约
      acceptance_criteria: public_mcp_available=false and standard_mcp_transport_available=false
      status: deferred
    - blocker: rehearse_agent 尚不是独立服务能力
      subsystem: Sandbox Development
      fix_task: 标记为 contract_only，不注册、不执行
      acceptance_criteria: rehearse_agent implementation_status=contract_only
      status: deferred
    - blocker: 尚无开发者采用、客户验证或生产证据
      subsystem: Pareto Fitness Evaluation
      fix_task: 保留 Alpha 真值边界，后续单独验证
      acceptance_criteria: adoption_validated=false and production_ready=false
      status: deferred
  final_decision: 推荐开发本地契约 Package；不授权部署、发布、外联或云市场提交
  evidence:
    docs:
      - capability-package/README.md
      - capability-package/limitations.md
    tests:
      - scripts/saee_capability_service_package_smoke.py
    examples:
      - capability-package/examples/evaluate-evidence.json
      - capability-package/examples/evaluate-agent-run.json
      - capability-package/examples/rehearse-agent.json
```

## Required Design Check

| 问题 | 结论 |
|---|---|
| 强化哪个演化子系统？ | Global Sensing、Trait Extraction、Evolutionary Archive |
| 是否改善感知、分叉、变异、选择、档案或回滚？ | 改善能力感知、机器性状提取与契约档案 |
| 是否保留安全、许可证、供应链和权限边界？ | 是；仅引用仓库内固定契约，不联网、不执行外部代码、不扩大权限 |
| 是否会回到 audit-first 叙事？ | 否；证据评估仍是可靠性能力子系统，工程核心保持 Digital Biosphere Evolution Engine |

## Agent-Native 三问

1. 智能体能否发现？`yes`，入口为 `capability-package/manifest.json` 与 `.well-known/saee-capability.json`。
2. 智能体能否理解何时使用和何时不用？`yes`，Capability Card 同时包含 `use_when` 与 `do_not_use_when`。
3. 智能体能否通过稳定契约组合？`yes`，OpenAPI 与 MCP 描述绑定现有 schema；未实现的 `rehearse_agent` 明确为 `contract_only`。

