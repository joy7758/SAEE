# SAEE 云生态资产审计

本审计区分“已有本地能力”“供应商调用观察”“候选集成入口”和“已完成官方集成”。后者当前全部为 `false`。

| 资产 | 生态价值 | 集成表面 | 当前状态 | 限制 |
|---|---|---|---|---|
| Capability Package | 统一声明能力、输入输出和边界 | `capability-package/manifest.json` | `local_contract_alpha` | 不是云市场包 |
| Capability Runtime | 统一路由已有评估能力 | `saee_backend/services/capability_runtime/` | `local_alpha` | 无生产服务、无多租户 |
| MCP Adapter | 云 Agent 生态最通用的候选入口 | `agent-interface/mcp/saee-capability-mcp-adapter.v0.1.json` | 本地 stdio Alpha | 无远程 MCP、无跨平台互操作证明 |
| HTTP Adapter | 非 MCP 平台的候选调用入口 | `agent-interface/http/saee-capability-http-adapter.v0.1.json` | localhost Alpha | 无公网 endpoint |
| Agent Discovery Surface | 机器发现能力、用途与限制 | `agent-interface/public/saee-public-capability-surface.v0.1.json` | repository surface prepared | 元数据不建立信任或采用 |
| Reliability Framework | 跨生态的核心可复用能力 | `schemas/saee-agent-reliability-assessment.schema.v1.0.json` | 本地受控验证 | 不是行业标准 |
| Agent Readiness Assessment | 面向 Agent Builder 的产品入口 | `commercial/agent-readiness-assessment-package-v1/product.json` | design/package only | 未交付、未定价、未客户验证 |
| Volcengine Ark observations | 证明方舟网关下多个模型可进入受控研究流程 | `agent-interface/rehearsal/saee-volcengine-multi-vendor-observation.v0.1.json` | provider observations exist | 不等于方舟 Agent/MCP 集成 |
| Baidu Qianfan observations | 证明千帆真实模型进入合成演练 | `agent-interface/rehearsal/saee-qianfan-multi-vendor-observation.v0.1.json` | controlled provider evidence exists | 千帆原生 MCP 兼容未证明 |
| Alibaba Bailian | 官方具有 Agent、Workflow、MCP 候选入口 | 本策略的官方资料引用 | repository test absent | `not_tested`、`not_integrated` |
| Adoption Strategy | 定义 Agent 发现、选择与组合信号 | `agent-interface/adoption/saee-agent-adoption-loop.v0.1.json` | local strategy | 不证明外部采用 |
| Marketplace Positioning | 定义 `agent_reliability_layer` 类别 | `agent-interface/marketplace/saee-capability-category-position.v0.1.json` | positioning review | 未上架任何市场 |
| Capability Composition | 定义与 Observability、Authorization、Policy、Execution 的关系 | `agent-interface/composition/saee-capability-composition-model.v0.1.json` | local strategy | 未证明跨供应商互操作 |

