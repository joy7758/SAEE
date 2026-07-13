# SAEE Ecosystem Entry Asset Audit

| 资产 | 进入价值 | 集成表面 | 当前状态 | 限制 |
|---|---|---|---|---|
| Cloud Ecosystem Strategy | 给出 P0/P1/P2 路线和平台边界 | `agent-interface/ecosystem/saee-cloud-ecosystem-priority-matrix.v0.1.json` | strategy complete | 不等于进入执行 |
| Cloud Integration Package | 跨平台总索引 | `ecosystem/cloud-integration-package-v0.1/` | preparation only | 不含平台专属评审材料 |
| Capability Package | 统一能力、操作和协议说明 | `capability-package/manifest.json` | local contract alpha | 不是市场包 |
| Capability Runtime | 唯一规范调用层 | `saee_backend/services/capability_runtime/` | local alpha | 无公网服务 |
| MCP Adapter | P0 工具运输入口 | `agent-interface/mcp/saee-capability-mcp-adapter.v0.1.json` | local stdio alpha | 无远程服务或跨供应商证明 |
| HTTP Adapter | 方舟候选补充入口 | `agent-interface/http/saee-capability-http-adapter.v0.1.json` | localhost alpha | 无鉴权、多租户或公网访问 |
| Public Capability Surface | 机器理解与发现 | `agent-interface/public/saee-public-capability-surface.v0.1.json` | repository surface prepared | 元数据不建立官方支持 |
| Agent Discovery | 验证合成 caller 能正确选择/弃权 | `agent-interface/discovery/saee-external-agent-discovery-validation-result.v0.1.json` | local synthetic validation | 不代表生态采用 |
| Alpha Release | 统一技术定位 | `release/saee-agent-reliability-framework-alpha-v0.1/capabilities.json` | local positioning package | 未执行公开发布 |
| Volcengine observations | 方舟网关与 Function Calling 观察 | `agent-interface/rehearsal/saee-volcengine-multi-vendor-observation.v0.1.json` | provider evidence | 不证明 SAEE 方舟映射 |

## Packaging Decision

- MCP Entry Package 允许把已有本地 Tool Contract 标为 `LOCAL_TESTED`；
- Volcengine Entry Package 只描述候选 Function Calling、MCP、HTTP 映射，状态全部为 `DESIGN_ONLY`；
- 两个包都只引用现有实现，不复制 Runtime、Handler 或 Evaluator。

