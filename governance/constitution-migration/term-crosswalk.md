# SAEE V2 Term Crosswalk

```text
crosswalk_id=SAEE_V2_TERM_CROSSWALK_PREPARATION
decision_input_status=APPROVED
crosswalk_status=DESIGN_DIRECTION_ONLY
term_change_executed=false
implementation_change=false
```

本 crosswalk 用于消除检索、引用和对象职责歧义。它不重命名历史资产，不创建 schema、
capability、MCP Tool 或 implementation。

## Identity hierarchy

| Term | v2.x layer | Canonical meaning | Status |
|---|---|---|---|
| `Silicon-Amplified Evolutionary Ecology` | Theory Identity | SAEE 的理论身份 | `PRESERVE` |
| `Digital Biosphere Evolution Engine` | Engineering Core | 九段演化闭环的工程核心 | `PRESERVE` |
| `SAEE Architecture` | Engineering Core | 工程结构与模块边界，不是独立产品 | `PRESERVE` |
| `Agent Readiness Infrastructure` | Product Identity | 面向 Agent 的就绪度证据和决策上下文产品身份 | `APPROVED_DIRECTION_NOT_ACTIVE_AUTHORITY` |
| `SAEE Readiness Evaluation Capability` | Ecosystem Capability | 可被 Agent 发现、理解和组合的只读能力边界 | `APPROVED_DIRECTION_NOT_EXTERNAL_INTEGRATION` |

层级关系是 `Theory → Engineering → Product → Ecosystem`。任何下层表达都不得反向覆盖
上层身份或把 SAEE 缩减成 audit/evaluation-only product。

## Object terminology

| Current or historical term | Current meaning/problem | v2.x treatment | Status |
|---|---|---|---|
| bare `ARO` | 至少曾指 `aro-v0.8`、ARO-Audit、Audit Record Object，亦被提议解释为 Agent Runtime Object | 新 SAEE 权威文本禁用；只在 migration/crosswalk/negative-test 语境引用 | `APPROVED_DESIGN_DIRECTION` |
| `aro-v0.8 evidence export` | 历史 evidence export 名称 | 保留完整版本化名称与 provenance | `HISTORICAL_PRESERVE` |
| `ARO-Audit` | 外部 receipt/audit-format 参考资产 | 保留明确 namespace；不作为 SAEE Execution Object | `HISTORICAL_PRESERVE` |
| `Audit Record Object` | demo/历史 record 语义 | 使用完整名称并保留历史 schema/引用 | `HISTORICAL_PRESERVE` |
| `Agent Runtime Object` | 与现有历史含义冲突，且会误示 SAEE 是 runtime | 不采用 | `REJECTED` |
| `SAEE Execution Context Object (SECO)` | 候选只读 execution-context envelope | 未来候选对象；必须另经 duplicate-build、schema、tests、validator 与 capability gate | `DESIGN_ONLY_NOT_IMPLEMENTED` |

```text
SECO_SCHEMA_EXISTS=false
SECO_IMPLEMENTED=false
SECO_CAPABILITY_REGISTERED=false
SECO_MCP_TOOL_EXISTS=false
SAEE_IS_AGENT_RUNTIME=false
```

## Evidence, Evaluation and Governance

| Product layer | Primary object/context | Responsibility | Must not claim |
|---|---|---|---|
| `SAEE Evidence` | Evidence Object, Evidence Receipt, provenance, integrity result | 记录事实材料、来源、完整性与免疫档案 | hash/signature 自动等于真实性、完整性或法律证明 |
| `SAEE Evaluation` | readiness/evidence-adequacy result, reason code, selection context | 依据证据产生可解释的决策上下文 | allow/deny、authorization、deployment 或 runtime control |
| `SAEE Governance` | change gate, lineage archive, rollback context | 管理受控变化、边界、归档与回滚 | self-approval、外部执行或已实现/发布状态 |

三个层级是目标客户版本，不是四阶段 maturity ladder。`Autonomous` 只允许作为
`FUTURE_MATURITY_HORIZON`，不得登记为第四目标版本。

## Trust Semantic alignment

```text
alignment_status=APPROVED_DESIGN_DIRECTION
implementation_status=DESIGN_ONLY
authority_effect=NONE
```

| Term | v2.x role | Status | Explicit boundary |
|---|---|---|---|
| `Trust Semantic Layer` | `Agent Readiness Infrastructure` 内跨 Evidence 与 Evaluation 的 `Technical Semantic Role` | `DESIGN_ONLY_APPROVED_DIRECTION` | 不是最高身份、独立 architecture layer、product 或 capability |
| `Trust Claim` | Evidence 与 Evaluation Result 之间的 bounded semantic relation | `DESIGN_ONLY_APPROVED_DIRECTION` | 不是 Object、Schema、Capability、Truth Source 或 Authorization Artifact |
| OpenTelemetry / bounded telemetry | 可选 `Observation Source`；SAEE 对合格 Evidence 和 claim-specific Evaluation Result 提供 bounded Trust Semantic Interpretation | `COMPLEMENTARY_OPTIONAL_OBSERVATION_INPUT` | 不替代 OpenTelemetry，不声称 compliance、OTLP/Collector interoperability、trace authenticity、identity binding 或 completeness |

`Trust Claim` 只描述以下概念关系：

```text
subject
claim_scope
evidence_refs
context_refs
evaluation_result
limitations
```

其中 `evidence_refs`、`context_refs` 和 `evaluation_result` 仍属于既有事实或输出表面；
该 crosswalk 不创建 Trust Object、Trust Score、Trust Registry、Trust Tool、schema、MCP
或平行 Evidence stack。Trust Semantic 结论不是 Truth、Authorization、Approval、Security
Certification、Compliance Proof、Production Readiness、external validation 或 customer
validation，也不保证 Agent 正确、安全或可用于生产。

## Asset and ecosystem terms

| Term | v2.x relationship | Boundary |
|---|---|---|
| GitHub repositories/assets | internal capability reference、migration source、adapter、demo 或 historical asset | 不等于同级 SAEE 产品，不整仓复制 |
| Agent Evidence Project | `SAEE Evidence and Immune Subsystem` 的受控迁移来源 | architecture ownership 不等于 source/runtime migration |
| Capability Registry | `capability-package/manifest.json#canonical_inventory` | 唯一 capability fact source；不因宪法迁移而改变事实 |
| MCP | capability interface/transport | 不是 SAEE 本体，不等于公共部署或 official integration |
| OpenAPI / adapters | 可选接口投影 | 不得创建第二 canonical capability truth |
| Cloud Channel / marketplace | 可选分发渠道 | application、review、listing、adoption 和 production 分开记录 |

## Combination mode

```text
SAEE_CAPABILITY=CORE_CONSUMPTION_MODE
MCP_OPENAPI=INTERFACE_LAYER
CLOUD_CHANNEL=OPTIONAL_DISTRIBUTION
OFFICIAL_INTEGRATION_CLAIM=false
ECOSYSTEM_DEVELOPMENT_AUTHORIZED=false
```

## Migration rule

术语变化只改变被明确授权的 authority/semantic surfaces，不自动改变 capability status、
product status、source provenance、runtime integration 或外部生态状态。历史对象通过
versioned crosswalk 保留，不批量改写或删除。
