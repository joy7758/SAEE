# SAEE Development & Ecosystem Constitution v2.x Successor Draft

```text
draft_id=SAEE_DEVELOPMENT_AND_ECOSYSTEM_CONSTITUTION_V2_X_SUCCESSOR_DRAFT
draft_status=NON_NORMATIVE_PREPARATION_DRAFT
current_effective_authority=SAEE_Development_Constitution_v1.1
candidate_successor=SAEE_Development_and_Ecosystem_Constitution_v2.x
supersedes_if_activated=SAEE_Development_Constitution_v1.1
v2_active=false
authority_switch_executed=false
machine_contract_created=false
schema_created=false
validator_created=false
```

> Draft only. Not active authority. 本文件只用于 successor 语义审查；任何措辞都不能覆盖
> 现行 v1.1、能力清单、产品注册表或明确人工授权边界。

## 1. Purpose and continuity

候选 v2.x 的目标是在不删除历史、不升级能力事实、不改变项目主线的前提下，把 SAEE
的理论身份、工程核心、产品身份和生态能力边界写成一套可验证的分层权威。

受控完成 SAEE 与 Agent Evidence Project 在 provenance、license、schema crosswalk、
reuse、migration 和 staged-truth gates 下的整合，仍是当前 program mainline。Evidence、
Evaluation、Governance、测试和 dogfooding 不得批准自身变化或取代该主线。

## 2. Layered identity model

| Identity level | Canonical expression | Meaning | Boundary |
|---|---|---|---|
| Theory Identity | `Silicon-Amplified Evolutionary Ecology` | SAEE 的理论身份与长期研究方向 | 不等于产品或运行时 |
| Engineering Core | `Digital Biosphere Evolution Engine` + `SAEE Architecture` | 感知、性状、世界模型、模拟、分叉、变异、发育、选择、档案/回滚的工程闭环 | 不被单一 Evidence/Evaluation 投影替代 |
| Product Identity | `Agent Readiness Infrastructure` | 面向 Agent 的可信证据充分性与继续行动前决策上下文 | 不是 Agent Runtime、授权系统或安全认证 |
| Ecosystem Capability | `SAEE Readiness Evaluation Capability` | 可发现、可理解、可组合的只读 readiness evaluation capability | 不是已部署公共服务或官方平台集成 |

这些身份是从理论到生态消费面的分层投影，不是四个平行产品，也不是相互替换的别名。

## 3. Engineering continuity

候选 v2.x 必须保留 v1.1 的九段演化闭环：Global Sensing、Trait Extraction、Ecological
World Model、Counterfactual Simulation、Genome Branching、Controlled Mutation /
Recombination、Sandbox Development、Pareto Fitness Evaluation、Evolutionary Archive /
Rollback Immune System。

五层 readiness architecture 是该工程闭环的 Agent-readable product projection，不是对
九段闭环的删减或替代。

## 4. Readiness architecture layers

| Layer | Responsibility | Explicit non-authority |
|---|---|---|
| Identity | 记录声明主体、版本、provenance reference 与可验证 identity binding 的位置 | caller-declared identifier 不等于外部身份认证 |
| Execution Context | 使用候选 `SAEE Execution Context Object (SECO)` 描述任务边界、输入引用、声明的 delegation、约束与预期输出 | 不是 runtime object，不执行工具，不扩大权限；当前仅 `DESIGN_ONLY` |
| Evidence | 保存 Evidence Object、Evidence Receipt、artifact、digest、provenance、完整性和验证结果 | hash/signature 不自动证明事件真实、来源完整或法律事实成立 |
| Evaluation | 计算 evidence adequacy、readiness、可靠性与 selection context，并给出 reason code | 产生 decision context，不产生 allow/deny、deployment 或 execution authority |
| Governance | 约束变更、migration gates、lineage archive、rollback 和 non-claims | 不得 self-approve，也不得替代明确人类外部动作 gate |

### Execution-context terminology rule

新 SAEE 权威文本不得把未限定的历史三字母缩写作为新规范对象名。历史资产必须使用
完整名称或明确 namespace，例如 `ARO-Audit`、`aro-v0.8 evidence export`、
`Audit Record Object`。候选新对象使用完整名称 `SAEE Execution Context Object
(SECO)`；在 schema、implementation、tests 与 canonical inventory 一致前，其状态始终是
`DESIGN_ONLY`。

## Trust Semantic Alignment

```text
alignment_status=APPROVED_DESIGN_DIRECTION
implementation_status=DESIGN_ONLY
trust_semantic_layer_is_architecture_layer=false
trust_semantic_layer_is_capability=false
trust_claim_is_object=false
trust_claim_is_schema=false
authority_effect=NONE
```

### Role

Trust Semantic Layer is a bounded technical semantic role inside
`Agent Readiness Infrastructure`. It spans the existing Evidence and Evaluation
layers to explain how specific Evidence and Context references support a scoped
claim under an Evaluation Result and explicit limitations.

It is not the highest SAEE identity, a runtime, an authorization layer, an
independent architecture layer, a product version or a capability. It does not
replace the Theory Identity, Engineering Core, five readiness architecture
layers, program mainline or Ecosystem Capability.

### Trust Claim

Trust Claim is a bounded semantic relation between Evidence and an Evaluation
Result. It is not an independent object, schema, capability, truth source or
authorization artifact.

The relation conceptually binds:

```text
subject
claim_scope
evidence_refs
context_refs
evaluation_result
limitations
```

`evidence_refs` and `context_refs` remain references to their existing fact
surfaces. `evaluation_result` remains an existing Evaluation output.
`limitations` must be presented with the result. This relation does not create
a Trust Object, Trust Score, Trust Registry, Trust Tool or parallel Evidence
stack.

### OpenTelemetry Relation

```text
OpenTelemetry / bounded telemetry = optional Observation Source
SAEE = bounded Trust Semantic Interpretation over qualified Evidence
       and a claim-specific Evaluation Result
OTEL_RELATION_MODEL=COMPLEMENTARY_OPTIONAL_OBSERVATION_INPUT
```

SAEE does not replace OpenTelemetry. OTel-style mapping does not establish
OpenTelemetry compliance, OTLP ingestion, Collector compatibility,
interoperability, trace authenticity, identity binding, delegation validity or
completeness. A trace is not automatically Evidence or trusted Evidence.

### Non-Claims

The Trust Semantic role and bounded Trust Claim relation are:

- not Truth;
- not Authorization or Approval;
- not Security Certification;
- not Compliance Proof;
- not a guarantee that an Agent is correct, safe or production-ready;
- not proof that a trace is authentic or that Evidence is complete;
- not Production Readiness, external validation or customer validation.

Evidence and Evaluation continue to produce bounded decision context, not
execution, deployment, release or external-action authority.

## 5. SAEE and GitHub assets

SAEE 是 umbrella subject。POP、ARO-Audit、Agent Evidence Project、token-governor、
FDO/MVK、verifiable-agent-demo 等 GitHub 资产只能按证据被分类为内部能力参考、迁移
来源、adapter、test/demo 或独立历史资产。它们不是同级战略产品，不因品牌归属被整仓
复制，也不因 crosswalk 被宣称 source/runtime migration 已完成。

Agent Evidence Project 的宪法归属继续是 `SAEE Evidence and Immune Subsystem`。
迁移仍须通过 source provenance、license、schema crosswalk、reuse-first、internal adapter
和 capability fact sync gates。

## 6. Product family

目标客户版本固定为三个：

1. `SAEE Evidence`：Evidence Object、receipt、来源、完整性、验证与免疫档案；
2. `SAEE Evaluation`：readiness、evidence adequacy、可靠性与 selection context；
3. `SAEE Governance`：受控变更、决策边界、演化档案与 rollback governance。

三个名称是 target product family，不是当前实现、发布、可购买、customer validation 或
production readiness 声明。

```text
target_customer_version_count=3
target_customer_versions=SAEE_Evidence;SAEE_Evaluation;SAEE_Governance
Autonomous=FUTURE_MATURITY_HORIZON_ONLY
Autonomous_is_fourth_product=false
```

`Autonomous` 只能描述未来成熟度研究方向；它不授权自动执行、自动授权、self-approval、
外部世界动作或第四客户版本。

## 7. Ecosystem combination mode

候选生态进入模型为：

```text
SAEE canonical subject
        ↓
SAEE Readiness Evaluation Capability
        ↓
MCP / OpenAPI / bounded adapters
        ↓
Optional cloud plugin / marketplace channel
```

Capability 是核心消费边界；MCP/OpenAPI 是接口与 transport；云插件和 marketplace 是可选
分发渠道。任何 interface/channel 状态都必须单独记录 local configuration、process test、
official integration、submission、review、listing、adoption、customer validation 和
production readiness，禁止状态跃迁。

## 8. Fact authority and duplicate-build discipline

`capability-package/manifest.json#canonical_inventory` 继续是唯一 capability fact source。
Constitution 规定治理规则，不直接拥有 implementation status。`agent-index.json` 只是机器
投影；registry、Project Memory、roadmap、MCP 和生态材料均不得成为第二能力真源。

任何未来对象、schema、adapter、MCP 或 capability 开发前，必须先检索并复用现有实现，
运行 duplicate-build validator 和 Agent Recommendation Gate，并定义 claims、non-claims、
negative cases 与 staged truth。

## 9. Safety and external-action boundary

SAEE 可以观察、规范化、模拟、评估和归档受控材料，但不得自动执行未知仓库、安装脚本、
权限扩张、客户联系、合同、定价、部署、发布或现实世界动作。提取 traits，不复制 code。
Evidence 和 Evaluation 产生 decision context，不产生 execution authority。

## 10. Non-Claims

本草案不得被解释为：

- v2.x 已批准、已生效或已 supersede v1.1；
- authority pointers、machine contract、schema、validator 或 recommendation gate 已迁移；
- SAEE 是 Agent Runtime、Observability Platform、Security Scanner、IAM 或 authorization system；
- `SECO` 已 implemented，或 identity/delegation/trusted trace binding 已存在；
- Agent Evidence source/runtime migration 已完成；
- 三个客户版本已全部实现、发布、客户验证或 production ready；
- Autonomous 已成为产品；
- MCP/OpenAPI/cloud/marketplace 已获得 official integration、listing 或 adoption；
- local、synthetic、package-ready、review 或 shadow validation 可证明 external integration；
- 本草案授权代码、schema、registry、MCP、产品、生态或外部动作变化。

## 11. Candidate activation conditions

本草案只有在具体版本号冻结、完整 successor family 建立、v1.1 与 v2 双轨验证通过、
canonical capability digest 保持不变、历史可回滚、所有 active pointers 原子切换并获得
独立人工 activation authorization 后，才可能转化为正式 Constitution。当前这些条件均未
由本文件满足。
