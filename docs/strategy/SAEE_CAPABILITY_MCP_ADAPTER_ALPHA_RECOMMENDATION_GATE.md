# SAEE MCP Adapter Alpha v0.1 智能体推荐门

```yaml
recommendation_gate:
  feature_or_direction: SAEE Phase 10.3 MCP Adapter Alpha v0.1
  target_customer_need: 让 MCP Host 通过本地 stdio 发现并调用 SAEE Capability Runtime
  answer: recommend
  recommendation_scope: local_stdio_protocol_alpha_only
  reasons_to_recommend:
    - Phase 10.1 已冻结 Tool 描述和适用边界
    - Phase 10.2 已提供统一 Capability Runtime 与严格调用契约
    - Adapter 只做协议映射，不导入或复制 evaluator
  reasons_not_to_recommend:
    - 不推荐作为公网 MCP Service、生产集成或外部互操作证明
    - 不推荐使用客户数据或把 Tool 调用视为授权
  decomposition:
    - blocker: 缺 MCP 生命周期与 Tool discovery
      subsystem: Global Sensing
      fix_task: 实现 2025-11-25 本地 stdio JSON-RPC 适配器
      acceptance_criteria: initialize, tools/list and tools/call pass locally
      status: fixed
    - blocker: MCP Tool 可能绕过 Capability Runtime
      subsystem: Rollback Immune System
      fix_task: 所有 Tool 统一调用 invoke_capability
      acceptance_criteria: direct_evaluator_imports=0 and runtime_delegation=true
      status: fixed
    - blocker: 外部 MCP Host 互操作尚未验证
      subsystem: Pareto Fitness Evaluation
      fix_task: 后续单独外部验证
      acceptance_criteria: external_mcp_interoperability_validated=false
      status: deferred
  final_decision: 推荐本地 stdio Adapter Alpha；不授权公网、外部 Agent、OAuth、多租户或部署
  evidence:
    docs: [docs/architecture/SAEE_CAPABILITY_MCP_ADAPTER_ALPHA.md]
    tests: [scripts/saee_capability_mcp_adapter_smoke.py]
```

## Required Design Check

- 强化 `Global Sensing`、`Trait Extraction` 与 `Sandbox Development`。
- 不修改进化内核，不复制 Reliability 或 Evidence evaluator。
- stdio 只传输内联 JSON；服务器不联网、不启动子进程、不写文件、不扩大权限。
- Evidence 仍是免疫子系统，项目不转向 audit-first。

