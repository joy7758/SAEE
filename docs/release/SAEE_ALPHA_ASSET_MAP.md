# SAEE Alpha 资产图

本图服务于 `SAEE Agent Reliability Framework Alpha v0.1` 的本地定位包。它只引用现有规范资产，不把引用关系解释为实现完整性、外部验证或生产就绪。

| 资产 | 规范入口 | 角色 | 公开价值 | 限制 |
|---|---|---|---|---|
| Digital Biosphere Architecture | `docs/theory/DIGITAL_BIOSPHERE_DEFINITION.md`、`docs/architecture/FINAL_ARCHITECTURE_SPEC.md` | 工程核心与演化闭环 | 防止把 SAEE 误解为通用 Agent 框架或审计 SDK | Alpha 不发布私有演化实现 |
| Persona Object Protocol | 未发现本仓库内独立规范文件 | 历史概念关联 | 可解释身份/人格引用的来源背景 | 不是本次可发布的规范资产，不声称已实现 |
| ARO Audit | `docs/adr/0002-audit-as-immune-subsystem.md` | 免疫/证据子系统边界 | 说明审计为何不是项目核心 | 不构成认证或法律审计能力 |
| Agent Evidence | `docs/EVIDENCE_ADEQUACY_PROFILE.md` | 证据充分性评估 | 提供声明、缺失要求和理由码 | 收据或记录存在不等于事件被证明 |
| Reliability Framework | `schemas/saee-agent-reliability-assessment.schema.v1.0.json`、`docs/research/SAEE_AGENT_RELIABILITY_RESEARCH_REPORT_V1.md` | 可靠性评估规范 | 统一执行、证据和边界可靠性语义 | 内部受控研究，不是行业基准 |
| Stateful Rehearsal Runtime | `docs/architecture/SAEE_STATEFUL_REHEARSAL_RUNTIME_ARCHITECTURE.md` | 有状态受控演练 | 展示多轮状态变化与受控终止 | 不执行外部世界，不等于真实客户运行时 |
| Capability Runtime | `docs/architecture/SAEE_CAPABILITY_RUNTIME_ALPHA.md` | 本地能力路由 | 复用现有规范服务 | 本地 Alpha，无公网服务 |
| MCP Adapter | `docs/architecture/SAEE_CAPABILITY_MCP_ADAPTER_ALPHA.md` | 本地 MCP 运输适配 | 便于 Agent 工具发现与调用 | MCP 可用性不授予权限 |
| HTTP Adapter | `docs/architecture/SAEE_CAPABILITY_HTTP_ADAPTER_ALPHA.md` | 本地 HTTP 契约适配 | 展示协议中立调用方式 | 无公网 API、无多租户 |
| Benchmark Corpus | `agent-interface/reliability/saee-internal-reliability-benchmark-result.v1.0.json` | 内部受控案例结果 | 支撑可重复方法说明 | 不产生排行榜或最佳模型结论 |
| Reliability Report | `docs/research/SAEE_INTERNAL_RELIABILITY_BENCHMARK_REPORT_V1.md` | 研究报告 | 展示结果解释方式 | 不能外推为市场采用或生产性能 |
| Evidence Methodology | `docs/EVIDENCE_ADEQUACY_BENCHMARK.md`、`docs/research/SAEE_INTERNAL_RELIABILITY_BENCHMARK_METHODOLOGY_REVIEW_V1.md` | 方法与边界 | 解释为什么失败与缺失证据均需保留 | 未经过独立外部复核 |
| Public Capability Surface | `agent-interface/public/saee-public-capability-surface.v0.1.json` | 机器发现入口 | 让 Agent 理解能力与禁用边界 | 元数据不是信任证明 |
| Agent Quick Start | `docs/public/SAEE_AGENT_QUICK_START.md` | 智能体快速理解 | 面向机器的最短路径 | 只支持本地能力 |
| Developer Quick Start | `docs/public/SAEE_DEVELOPER_QUICK_START.md` | 开发者本地入口 | 可复现实例与验证命令 | 不提供生产部署指南 |

