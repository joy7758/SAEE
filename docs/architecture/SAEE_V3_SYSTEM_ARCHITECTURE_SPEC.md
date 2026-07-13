# SAEE v3.0 System Architecture Specification

状态：`accepted_architecture_projection_phase1_local_only`。

```yaml
artifact: SAEE_V3_SYSTEM_ARCHITECTURE_SPEC
architecture_version: 3.0-draft
scope: deployment_assurance_projection
canonical_three_layer_architecture_modified: false
final_architecture_spec_replaced: false
runtime_modified: false
external_agent_executed: false
production_monitoring_available: false
continuous_assurance_implemented: false
production_ready: false
customer_validated: false
architecture_projection_accepted: true
phase1_local_synthetic_vertical_slice_implemented: true
```

## 1. Architecture Decision

SAEE 的 canonical identity 保持不变：理论身份是 Silicon-Amplified Evolutionary Ecology，工程核心是 Digital Biosphere Evolution Engine。既有三层架构继续作为权威结构：

```text
L1  Frozen Scientific Object (LCR-REDS)
 ↓
L2  Meta-Protocol System (SAEE-MP)
 ↓
L3  Engineering / Runtime / Experiment Projection
```

v3.0 不创建第四个权威层，也不把 SAEE 改造成 audit SDK、通用 Agent framework 或生产治理平台。九层架构是 L3 内部面向商业问题的 `Deployment Assurance Projection`：它把演化模拟、评测、证据和部署决策组织成一个可审查的投影。

### Honest product definition

> SAEE is a Deployment Assurance Projection on Evidence-Based Evaluation Architecture.

中文：

> SAEE 是建立在基于证据的评测架构之上的部署保障投影。

该定义已作为 L3 投影接受。它不替换 canonical 三层架构；只有 Phase 1 本地合成垂直切片已经实现，真实 Agent adapter、生产观测、客户验证与持续保障仍未实现。

## 2. Mapping to the Evolution Loop

| v3 capability | Canonical evolution subsystem | Strengthened function |
|---|---|---|
| Governance contract | Evolutionary Archive / Rollback Immune System | 权限、来源、风险等级和审计要求 |
| Task contract | Global Sensing / Trait Extraction | 把业务目标转换为可评测任务边界 |
| Environment simulation | Ecological World Model / Counterfactual Simulation | 构造负载、变化、攻击和漂移场景 |
| External runtime boundary | Sandbox Development | 约束外部执行环境，不让 SAEE 直接执行世界 |
| Observation | Global Sensing | 接收获批、脱敏、结构化观察 |
| Evaluation | Pareto Fitness Evaluation | 对能力、稳定、漂移、安全和成本做多目标评测 |
| Evidence | Evolutionary Archive / Rollback Immune System | 绑定输入、输出、版本、grader 和摘要 |
| Risk estimation | Ecological World Model / Pareto Fitness Evaluation | 将声明的合成输入映射为场景化风险估计 |
| Decision support | Selection / Dormancy / Rollback | 输出限定的 deploy/hold/retest 决策支持 |
| Feedback | Global Sensing → next generation | 把获批反馈转成新一轮任务与环境版本 |

治理、证据和部署建议支撑演化闭环，但不替代闭环身份。

## 3. Nine-Layer Deployment Assurance Projection

### Layer 0: Governance Contract Layer（治理契约层）

回答：谁允许评测、哪些数据可以使用、评测哪个模型版本、风险等级是什么、谁负责审查。

最小字段：

- `policy_ref`；
- `evaluation_authorization_ref`；
- `data_permission_ref`；
- `model_and_agent_version_refs`；
- `risk_class`；
- `audit_requirement_ref`；
- `retention_and_deletion_ref`；
- `stop_authority_ref`。

缺少权限、来源或停止责任时必须 fail closed。Layer 0 不代表法规合规，也不签发真实生产权限。

### Layer 1: Task Contract Layer（任务契约层）

回答：究竟在测什么。

任务契约至少固定：

- 业务目标与禁止目标；
- task category、channel、language；
- context window 和 memory policy；
- tool configuration；
- expected outcomes；
- business impact class；
- candidate set；
- acceptance criteria；
- explicit exclusions。

没有任务契约的 candidate ranking 不得进入 Risk Estimation 或 Decision Support Layer。

### Layer 2: Environment Simulation Layer（环境模拟层）

回答：在哪些世界状态下测试。

包括：

- 普通、激进、错误或对抗用户；
- 长短上下文和多轮负载；
- 工具可用性、权限变化和故障；
- 知识库、政策和数据分布变化；
- memory drift 和 state mutation；
- denial、timeout、partial failure；
- counterfactual branches。

当前仓库只有 synthetic/local simulation 证据，没有 deployment-grounded distribution replay。

### Layer 3: External Agent Runtime Boundary（外部智能体运行边界）

原始提案中的 `Agent Runtime` 必须受 SAEE 安全原则约束：

```text
SAEE observes approved execution.
SAEE does not directly execute the external world.
```

真实候选 Agent、tool、memory 和 workflow 只能由以下主体运行：

- customer-controlled sandbox；或
- separately approved researcher-controlled sandbox。

SAEE 只接收该沙盒输出的结构化 observation/evidence bundle。禁止未知仓库、自动安装、权限扩大、未批准网络和把外部代码复制为 genome。

Layer 3 未来只允许三个 receive-only adapter（只接收适配器），当前均未实现：

- `Runtime Adapter`：接收获批沙盒生成的版本化运行摘要；
- `Memory Adapter`：接收获批、脱敏的记忆状态与变更摘要；
- `Tool Trace Adapter`：接收结构化、allowlist 限定的工具调用观察。

这些 adapter 不启动 Agent、不调用工具、不扩权，也不把外部代码复制为 genome。

### Layer 4: Observation Layer（观测层）

回答：系统观察到了什么，而不是证明了什么。

可观察字段包括：

- latency 和 token usage；
- tool calls 和 tool results；
- state changes；
- memory mutations；
- policy/approval observations；
- resource references；
- failures、timeouts、retries；
- timestamps 和 correlation IDs。

Observation 必须与 Evidence 分离。Trace 不能自动成为真实性、授权或因果证明。

### Layer 5: Evaluation Layer（评测层）

回答：在明确 contract 下表现如何。

多目标评测面：

- capability；
- stability；
- drift；
- safety；
- recoverability；
- cost and latency；
- uncertainty；
- evidence completeness。

Evaluation 对应通用 eval 能力，但不是 SAEE 的全部。结果必须绑定 task、environment、candidate、grader 和 sample versions。

每条 Evaluation result 至少包含：

```text
Score + Reason + Failure Class + Evidence Reference
```

Score 不能脱离解释、失败分类与证据引用单独进入风险估计。

### Layer 6: Evidence Layer（证据层）

回答：结论由哪些可检查材料支持。

最小 evidence bundle：

- input/sample refs；
- output refs；
- observation/trace refs；
- resource、authorization、oversight 和 effect receipts；
- agent/model/tool/environment/grader versions；
- timestamps；
- content and receipt digests；
- provenance and derivation relations；
- privacy、retention、access and deletion refs；
- explicit truth boundaries。

Evidence Layer 复用现有 resource receipt、Evidence Adequacy、candidate mapping 和 crosswalk，不声称真实外部身份已验证。

### Layer 7: Risk Estimation Layer（风险估计层）

回答：测量结果对特定业务意味着什么。

风险不是单一稳定性分数，也不能跨业务直接比较。同样的 failure probability 在退款审批和普通 FAQ 中具有不同影响。

详见第 8 节公式。Risk Estimation Layer 必须输出输入、权重、阈值、置信度、未覆盖场景和 uncertainty penalty。输出是 `Risk Estimate`，不是测得的真实失败概率。

### Layer 8: Decision Support Layer（部署决策支持层）

回答：在本场景与证据边界内下一步做什么。

允许输出：

- `DEPLOY_LIMITED`；
- `HOLD`；
- `RETEST`；
- `DO_NOT_DEPLOY`。

每个 decision 必须包含：

- scenario scope；
- recommended candidate；
- allowed and prohibited use；
- main failure triggers；
- restrictions and required controls；
- confidence；
- evidence refs；
- expiration/retest condition。

Decision Support 是部署建议，不是自动决策、客户最终授权、法律批准或安全认证。

## 4. Architecture and Data-Flow Diagram

```text
Canonical L1/L2 authority
          |
          v
[L0 Governance Contract]
          |
          v
[L1 Task Contract]
          |
          v
[L2 Environment Simulation]
          |
          v
[L3 External Customer/Research Sandbox]
          |
          | approved structured output only
          v
[L4 Observation]
          |
          v
[L5 Evaluation]
          |
          v
[L6 Evidence + Adequacy]
          |
          v
[L7 Scenario Risk Estimation]
          |
          v
[L8 Bounded Deployment Decision Support]
          |
          v
  Deploy / Hold / Retest outside SAEE
          |
          | approved sanitized feedback only
          +------------------------------+
                                         |
                                         v
                               [Global Sensing input]
                                         |
                                         v
                          New task/environment version
```

### Dependency rules

- 下游不能补造上游权限或任务边界；
- Observation 不能跳过 Evidence 直接产生 production decision；
- Evaluation score 不能绕过 Risk Estimation；
- Risk Estimation 缺少 evidence adequacy 或 scenario coverage 时必须 `HOLD/RETEST`；
- Feedback 不能直接修改 LCR-REDS、SAEE-MP 或生产 Agent；
- 每次新 feedback 都生成新版本，而不是静默覆盖历史 case。

## 5. Evaluation Contract Specification

Evaluation Contract 回答“测了什么、怎样测、什么没测”。

必需内容：

```text
evaluation_contract_id
task_contract_ref
environment_contract_ref
candidate_refs
data_source_ref
sample_manifest_ref
testing_criteria
negative_and_adversarial_coverage
tool_and_memory_configuration
grader_refs_and_versions
repeat_and_randomization_policy
stop_conditions
explicit_exclusions
expected_output_schema_ref
```

### Testing criteria

每项 criterion 必须记录：

- metric/criterion ID；
- measurement method；
- direction and threshold；
- aggregation rule；
- missing-data behavior；
- invalid/abstain behavior；
- business relevance；
- known limitations。

不允许只给一个无 contract 的总分或“最佳 Agent”。

## 6. Evidence Contract Specification

Evidence Contract 回答“为什么可以审查这项评测”。

```text
evidence_contract_id
evaluation_contract_ref
input_refs
output_refs
observation_refs
receipt_refs
authorization_and_oversight_refs
version_manifest
grader_manifest
timestamps
digests
relationships
privacy_and_retention_refs
truth_boundary
```

### Adequacy gate

Evidence bundle 必须选择具体 claim profile。Schema validity、receipt validity 和 evidence adequacy 必须分别输出。任一 critical claim adequacy 为 FAIL 时，Risk Estimation 只能输出 uncertainty 增加，Decision Support 只能 `HOLD/RETEST`，不能自动 `DEPLOY_LIMITED`。

## 7. JSON Schema Contract

规范 schema：

`agent-interface/architecture/saee-deployment-assurance-case.v0.1.schema.json`

该 schema 绑定 Governance、Task、Environment、Runtime Boundary、Observation、Evaluation、Evidence、Risk、Decision 和 Feedback contract。它采用严格字段、显式版本和 truth boundary。

Schema 通过只证明对象结构符合 draft contract，不证明 case 存在、执行发生、风险计算正确或 deployment 获批。

### SAEE Evidence Case Object

Phase 1 新增一个严格、可检索的最小 Case Object：

```text
identity
task_contract
environment
agent_reference
observation
evaluation
evidence
risk
decision
```

对应文件：

- schema：`agent-interface/architecture/saee-evidence-case.v0.1.schema.json`；
- 合成输入：`agent-interface/architecture/examples/saee-evidence-case-synthetic-001.json`；
- 本地实现：`saee_backend/services/saee_evidence_case.py`。

其中 `agent_reference` 仅是合成候选引用；`observation` 明确不是 Evidence；`risk` 是估计；`decision` 是场景限定的支持信息。Case Object 不执行真实 Agent，也不授权部署。

## 8. Risk Estimation Specification

### Scenario risk

对每个场景 `s`：

```text
R_s = P_s × I_s × X_s × (1 - C_s) + U_s
```

其中：

- `P_s ∈ [0,1]`：在明确 task/environment 下的 failure estimate；
- `I_s ∈ [0,1]`：业务影响；
- `X_s ∈ [0,1]`：暴露频率或范围；
- `C_s ∈ [0,1]`：已验证控制措施的风险降低效果；
- `U_s ∈ [0,1]`：distribution mismatch、样本不足、evidence 缺失等 uncertainty penalty。

### Aggregate risk

```text
R_total = Σ_s w_s × R_s
```

约束：`w_s ≥ 0` 且 `Σ_s w_s = 1`。权重由 Governance/Task Contract 定义，不是 SAEE 的普适常数。

### Decision-support rule

```text
if critical_evidence_fail:
    decision = HOLD or RETEST
elif R_total <= tau_deploy and controls_verified:
    decision = DEPLOY_LIMITED
elif R_total <= tau_hold:
    decision = RETEST
else:
    decision = HOLD or DO_NOT_DEPLOY
```

`tau_deploy` 和 `tau_hold` 必须按业务风险等级配置。当前没有经客户或外部研究验证的 universal threshold。

### Confidence

Confidence 必须与 risk 分开，至少由以下因素构成：

- scenario/sample coverage；
- deployment-distribution fit；
- provenance completeness；
- grader agreement；
- repeat stability；
- evidence adequacy；
- unresolved uncertainty。

Phase 1 仅实现该公式的本地合成 reference slice。它验证算术、阈值顺序与 evidence fail-closed，不代表外部校准、真实概率测量或通用业务阈值。

## 9. Continuous Assurance Feedback Contract

未来 feedback loop 可接收：

- 获批、脱敏的 post-deployment observation summary；
- failure and incident taxonomy；
- distribution drift signal；
- task/environment version changes；
- human override and rollback outcome。

Feedback 必须：

- 经过 data permission 和 privacy gate；
- 使用稳定 case/version IDs；
- 只进入 Global Sensing；
- 生成新的 task/environment/evaluation case；
- 不自动执行修复；
- 不自动修改生产 Agent；
- 不自动改变 LCR-REDS 或 SAEE-MP；
- 支持撤回、保留和删除规则。

当前 `continuous_assurance_implemented=false`、`post_deployment_monitoring_available=false`。

## 10. Relation to OpenAI Evals and Adjacent Systems

本规范不把 SAEE 定义为 OpenAI Evals 的替代品，也不声称与任何外部产品、标准或 system card 等价。

概念边界：

```text
Generic evaluation capability
        ↓ supplies measurements
SAEE Deployment Assurance Projection
        ↓ adds scenario, evidence, risk and bounded decision contracts
Customer deployment authority
```

SAEE 不应与 observability、IAM/authorization、GRC/SIEM 或通用 runtime 正面竞争。它的窄定位是把已有测量和记录组织为场景限定的部署风险与决策材料。

附件中的外部产品和研究判断属于用户提供的背景，本规范未独立验证，也不以其作为合规或性能声明。

## 11. MVP Development Roadmap

### Phase 0: Architecture Freeze

Goal：审查并冻结本 draft 的层级、contracts、risk semantics 和边界。

Exit criteria：

- 与 canonical three-layer architecture 无冲突；
- schema 与文档一致；
- Agent recommendation gate 给出明确结论；
- 不含 production 或 customer validation 升级。

### Phase 1: Local Synthetic Vertical Slice

Goal：复用现有 synthetic evaluator、receipts 和 adequacy profiles，形成一个完整但不执行外部 Agent 的 assurance case。

Required work：

- Task Contract v0.1；
- Environment Contract v0.1；
- Risk Estimate reference implementation；
- scenario-scoped Decision Support result；
- negative cases 和 replayable synthetic example。

Exit criteria：所有层使用合成输入贯通，Risk/Decision 不绕过 evidence gate，network/external execution 为 0。

### Phase 2: Consent-First Offline Design-Partner Replay

Goal：在 source、permission、privacy、retention、deletion、support 和 quote gate 通过后，用严格脱敏材料验证决策价值。

Exit criteria：一个真实外部用户确认报告帮助其决策；仍不等于 production deployment。

### Phase 3: Customer-Controlled Sandbox Adapter

Goal：由客户沙盒执行候选系统，SAEE 只接收结构化输出。

Exit criteria：执行所有权、网络、权限、审计、rollback 和 deletion 均有外部批准证据。

### Phase 4: Approved Continuous Assurance Loop

Goal：用获批 post-deployment summary 触发新一轮 assurance case。

Exit criteria：feedback 权限、漂移检测、版本化 re-evaluation、人工决策和回滚流程全部验证。

Phase 0 架构投影已接受，Phase 1 本地合成垂直切片已实现。该实现不授权 Phase 2、真实 Adapter、客户数据或生产部署。

## 12. Current Capability Mapping

| v3 layer | Current repository evidence | Current status |
|---|---|---|
| Governance | readiness、privacy、安全和推荐门文件 | local planning/hold only |
| Task Contract | evaluation request/scenario schemas | partial, not v3 frozen |
| Environment Simulation | synthetic descriptor and evolutionary simulators | local synthetic, not deployment-grounded |
| Runtime Boundary | no-external-execution rules | boundary exists; adapter not implemented |
| Observation | sanitized observed trace adapter | partial, file-backed only |
| Evaluation | local deterministic evaluator and benchmark | implemented local synthetic scope |
| Evidence | receipts、adequacy、crosswalk、reproducibility | implemented local synthetic/declared scope |
| Risk Estimation | Phase 1 合成公式与阈值 reference slice | local synthetic estimate only; not externally calibrated |
| Decision Support | Phase 1 evidence-gated scenario recommendation | local synthetic support only; no deployment authority |
| Feedback | sensing concepts and plans | not implemented as continuous assurance |

## 13. Non-Goals and Truth Boundary

本 accepted projection 与 Phase 1 本地切片不：

- 替换 `FINAL_ARCHITECTURE_SPEC.md`；
- 修改 LCR-REDS 或 SAEE-MP；
- 修改外部 Agent runtime、kernel 或 website；
- 创建生产 Agent execution；
- 采集 post-deployment data；
- 声称实现经外部校准的通用 risk model；
- 生成真实 deployment recommendation；
- 声称 OpenAI、客户、监管者或第三方背书；
- 声称 production、enterprise、security、compliance 或 customer readiness。

推荐下一动作：审查 Phase 1 本地合成 Case Object、风险估计与 Decision Support 输出；不要在本阶段实现真实 Agent adapter 或启动外部 pilot。
