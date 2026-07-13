# SAEE Local HTTP Capability Adapter Alpha v0.1 智能体推荐门

```yaml
recommendation_gate:
  feature_or_direction: SAEE Phase 10.4 Local HTTP Capability Adapter Alpha v0.1
  target_customer_need: 让非 MCP 本地智能体通过 HTTP 调用现有 Capability Runtime
  answer: recommend
  recommendation_scope: localhost_loopback_alpha_only
  reasons_to_recommend:
    - Phase 10.2 Runtime 已统一处理能力、限制和 Invocation Receipt
    - HTTP Adapter 可覆盖非 MCP 本地调用者且无需复制 evaluator
    - 固定 localhost 与三路由可以保持失败闭合
  reasons_not_to_recommend:
    - 不推荐公网、客户接入、生产 SLA 或 SaaS
    - 无认证、OAuth、多租户和生产安全评估
  decomposition:
    - blocker: HTTP 层可能绕过 Runtime
      subsystem: Rollback Immune System
      fix_task: 唯一委托 invoke_capability
      acceptance_criteria: direct_evaluator_imports=0 and runtime_delegation=true
      status: fixed
    - blocker: HTTP listener 可能暴露公网
      subsystem: Sandbox Development
      fix_task: Server 构造器固定 127.0.0.1 且不接受 host 参数
      acceptance_criteria: localhost_binding=true and public_service=false
      status: fixed
    - blocker: 无认证与外部互操作验证
      subsystem: Pareto Fitness Evaluation
      fix_task: 保持本地 Alpha，后续独立评审
      acceptance_criteria: oauth_available=false and external_validation=false
      status: deferred
  final_decision: 推荐本地 loopback Alpha；不授权公网部署、客户数据或外部 Agent
  evidence:
    docs: [docs/architecture/SAEE_CAPABILITY_HTTP_ADAPTER_ALPHA.md]
    tests: [scripts/saee_capability_http_adapter_smoke.py]
```

本功能强化 `Global Sensing`、`Trait Extraction` 和 `Sandbox Development`，不修改 Digital Biosphere Evolution Engine，不把证据子系统提升为项目核心。

