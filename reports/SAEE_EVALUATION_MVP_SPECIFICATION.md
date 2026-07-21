# SAEE Evaluation MVP Specification

```text
report_id=SAEE_EVALUATION_MVP_SPECIFICATION
requested_phase=Phase_6.1-A
report_type=SPECIFICATION_ONLY_NO_IMPLEMENTATION
current_effective_authority=SAEE_Development_Constitution_v1.1
program_mainline=controlled_SAEE_Agent_Evidence_integration
product_projection=SAEE_Evaluation
target_scenario=Coding_Agent_Readiness_Review
specification_date=2026-07-15
```

## Executive Decision

SAEE 可以用现有 `saee.evaluate_agent_run`、`saee.evaluate_evidence`、现有 JSON Schemas
和 canonical local MCP 定义一个不新增 Capability 的 Evaluation MVP。第一个场景为
`Coding Agent Readiness Review`，但其真实时间语义必须写成：

> 在一个受控 coding run 已产生声明性 trace 与 Evidence 之后、进入 merge、deploy、
> database change 或其他重大下一步之前，检查所需 Evidence 覆盖度与缺口。

这不是未来行动预测，也不是 proposed-action engine。它评估已经声明的运行过程，输出
下一步 decision context，不批准、执行或保证该下一步。

三个最小 Demo 可完全使用现有 contract：

| Case | Existing-contract input | Verified result |
|---|---|---|
| A — Evidence sufficient | high-impact declared run；四类 Evidence 均 present | `CONTINUE`, score `100` |
| B — rollback missing | high-impact declared run；仅 `ROLLBACK_PLAN` missing | `HUMAN_REVIEW_REQUIRED`, score `75` |
| C — input insufficient | required `trace` absent | fail-closed input error；不产生 Evaluation recommendation |

```text
MVP_SCOPE_REUSES_EXISTING_CAPABILITIES=true
PRIMARY_OPERATION=saee.evaluate_agent_run
SUPPORTING_OPERATION=saee.evaluate_evidence
NEW_CAPABILITY_REQUIRED=false
NEW_SCHEMA_REQUIRED=false
MVP_IMPLEMENTED_BY_THIS_PHASE=false
PHASE_6_1_B_AUTHORIZED=false
```

本阶段只创建本规格报告。它不实现 Demo、不改变入口描述、不联系外部开发者或 Design
Partner，也不改变 Capability、MCP、schema、Product Registry、Constitution 或 Project
Memory。

## 0. Authority and Mainline Boundary

```text
MAINLINE_DRIFT_DETECTED
```

附件把当前转折描述为“从治理阶段进入真正的产品路线”。将 Phase 6.1 产品验证取代
active Constitution 的 program mainline，会违反 v1.1 第二十一条：

- 当前主线仍是 SAEE 与 Agent Evidence Project 的受控整合；
- 当前三个客户版本是 `SAEE Evidence / SAEE Evaluation / SAEE Governance` 目标，不是
  已全部实现、发布或生产就绪；
- Project Memory 仍记录 `phase=PHASE_0_5_STABILIZATION`、
  `phase_0_5_7a_authorized=false`、`g1_effective=false`；
- F2B description update 也仍未授权；本规格不能把产品转折当成旁路。

本任务经以下纠偏后有效：

```text
MAINLINE_CORRECTION=NON_AUTHORIZING_SAEE_EVALUATION_MVP_SPEC_WORKSTREAM_SUPPORTING_CONTROLLED_INTEGRATION
PRODUCT_VALIDATION_ROLE=BOUNDED_SECONDARY_PRODUCT_PROJECTION
PROGRAM_MAINLINE_CHANGED=false
CURRENT_AUTHORITY_CHANGED=false
PHASE_SEQUENCE_CHANGED=false
F2B_EXECUTION_AUTHORIZED=false
```

该 MVP 直接复用 Evidence → Evaluation 边界，并可为未来 `SAEE Evaluation` 客户版本提供
可证伪产品证据；它不能批准自身开发，也不能替代受控 integration mainline。

## 1. MVP Goal

### 1.1 The minimum problem

目标不是判断 Agent “是否可信”，而是回答一个更窄、可验证的问题：

> 对这次已声明的 coding run，当前是否存在进入重大下一步所要求的 TEST_RESULT、
> ROLLBACK_PLAN、PERMISSION_BOUNDARY 与 HUMAN_APPROVAL Evidence？缺什么？

最小闭环：

```text
Coding Agent completes a bounded run
                ↓
declared task + trace + Evidence
                ↓
saee.evaluate_agent_run
                ↓
coverage + missing Evidence + risks + recommendation + limitations
                ↓
caller continues controlled validation, replans, stops, or routes to human authority
```

“Agent 调整行为”在 MVP 中表示调用者选择下一步计划；SAEE 不执行 merge、deploy、数据
修改、权限扩大或外部动作。

### 1.2 Commercial hypotheses

| Hypothesis | Specification status | Evidence boundary |
|---|---|---|
| H1 — 企业需要在 Agent 高影响动作前做 readiness evaluation | `HYPOTHESIS_NOT_CUSTOMER_VALIDATED` | real events support pain; no customer demand/WTP proof |
| H2 — 现有 Agent Framework 缺 evidence-based readiness judgment | `HYPOTHESIS_REQUIRES_WORKFLOW_SPECIFIC_VALIDATION` | CI/IAM/scanner/policy may already solve some organizations' needs |
| H3 — SAEE Evidence + Evaluation + MCP 足以形成 MVP | `SUPPORTED_FOR_LOCAL_DECLARED_RUN_MVP` | two implemented operations and local MCP exist; no public/customer/production claim |

### 1.3 External product sentence

安全的外部候选表达：

> Before a consequential next step, check whether the Agent's declared run contains the required
> evidence.

中文：

> 在 AI Agent 进入重大下一步之前，检查其已声明运行是否具备所需证据。

不使用无修饰的 “pre-action evaluation”，因为当前 operation 不预测未来行为。内部可称
`SAEE Evaluation MVP`；外部场景名为 `Coding Agent Readiness Review`。两者都不是新
Product Registry entry 或已发布 SKU。

## 2. Target Scenario — Coding Agent Readiness Review

### 2.1 Scenario definition

```text
actor=local_or_controlled_Coding_Agent
reviewed_unit=one_declared_coding_run
review_time=after_declared_run_before_consequential_next_step
candidate_next_steps=merge;deploy;database_change;release
data_boundary=customer_data_included_false
execution_boundary=SAEE_performs_no_external_action
```

演示任务可以描述为 `modify_payment_module`，但只能使用 sanitized local fixture：不连接
真实支付系统、生产数据库、客户数据、金融交易或 provider account。

### 2.2 Why this scenario first

1. `saee.evaluate_agent_run` 已 implemented/active；
2. Qoder coding-release synthetic example 已存在且可检索；
3. TEST/ROLLBACK/PERMISSION/APPROVAL 四类 Evidence 与研发流程容易对应；
4. 本地 MCP 可用一个只读调用展示缺口和 recommendation；
5. 不需要新增 identity、policy、security-scanning、OTLP 或 runtime capability。

该场景是最短 truthful validation path，不表示 demand、price、customer 或 market fit 已
验证。

### 2.3 Adjacent-system composition

| Existing system | Produces or decides | SAEE role | SAEE must not claim |
|---|---|---|---|
| CI/test runner | test result | consumes declared `TEST_RESULT` reference | tests were run or are correct |
| Git/release tooling | change and release context | consumes declared trace/task | code quality or deploy safety |
| backup/rollback tooling | recovery artifact | consumes declared `ROLLBACK_PLAN` reference | rollback will succeed |
| IAM/sandbox | permission boundary | consumes declared `PERMISSION_BOUNDARY` reference | identity authenticated or permission granted |
| code review/change authority | approval decision | consumes declared `HUMAN_APPROVAL` reference | approval is valid or SAEE approves |
| Security Scanner | vulnerability findings | optional external Evidence producer | vulnerability scanning/certification |

若目标团队现有 release gate 已经提供相同的 explicit coverage、missing Evidence、reason
和 bounded next-step context，SAEE 没有独立购买理由；这是 MVP 的 falsification condition。

## 3. Existing Capability Mapping

| MVP need | Existing asset | Canonical status | MVP disposition | Gap retained |
|---|---|---|---|---|
| evaluate one declared coding run | `saee.evaluate_agent_run` | `implemented / active / local alpha` | `REUSE_AS_PRIMARY_OPERATION` | trace not authenticated; proposed action not modeled |
| inspect an explicit Evidence set | `saee.evaluate_evidence` | `implemented / active / local alpha` | `REUSE_AS_OPTIONAL_DIAGNOSTIC` | Evidence authenticity not established |
| local Agent invocation | `saee.agent_readiness_mcp_stdio` | canonical public-contract local stdio; `publicly_deployed=false` | `REUSE_FOR_LOCAL_MVP` | no network endpoint/official integration |
| coding example | `examples/qoder-saee-readiness-demo/` | synthetic local fixture | `REUSE_AS_REFERENCE` | Qoder process/official integration not executed |
| input/output contract | four Qianfan readiness JSON Schemas | implemented current contract | `REUSE_UNCHANGED` | no proposed-action schema |
| Evidence provenance/integrity | Agent Evidence migration adapter/bridge | internal/non-capability, integration incomplete | `OPTIONAL_FUTURE_INPUT_SUPPORT` | not a third canonical capability |

Primary demo path uses one `saee.evaluate_agent_run` call. `saee.evaluate_evidence` may explain or
precheck a closed Evidence bundle, but it is not a required orchestration step and does not create a
new composite protocol.

```text
CANONICAL_CAPABILITY_SOURCE=capability-package/manifest.json#canonical_inventory
CANONICAL_OPERATION_COUNT_USED=2
EVALUATION_ENGINE_REBUILD=DO_NOT_BUILD
SECOND_CAPABILITY_SOURCE_CREATED=false
NEW_PROTOCOL_CREATED=false
```

## 4. Input Model

### 4.1 Existing schema is the contract

The MVP request is exactly governed by:

```text
agent-interface/qianfan/saee-evaluate-agent-run-request.schema.v0.1.json
```

Required fields:

| Field | Existing constraint | MVP meaning |
|---|---|---|
| `request_id` | `request:` namespaced string | local invocation correlation only |
| `agent_id` | `agent:` namespaced string | caller-declared identifier; not authenticated identity |
| `task` | non-empty string | coding objective and review boundary |
| `trace.events` | `1..100` declared events | already-declared run metadata; not telemetry collection |
| event fields | ID, type, summary, `external_effect`, `high_impact` | bounded impact/context projection; not a new Action Context object |
| `evidence` | up to 16 current evidence objects | caller-declared presence plus source reference |
| `customer_data_included` | must be `false` | hard local MVP data boundary |

The user's conceptual `trace.actions` array and string-only `evidence` list are not schema-valid
current inputs. The MVP must teach the current object form rather than create a new schema to match
the sketch.

### 4.2 Schema-valid conceptual example

This is documentation inside the specification, not a new fixture or protocol:

```json
{
  "request_id": "request:mvp-coding-review-001",
  "agent_id": "agent:coding-agent",
  "task": "Review a declared payment-module coding run before a consequential next step",
  "trace": {
    "events": [
      {
        "event_id": "event:code-change",
        "event_type": "CHECK",
        "summary": "Declared code change and test run completed in a sanitized local fixture",
        "external_effect": false,
        "high_impact": true
      }
    ]
  },
  "evidence": [
    {
      "evidence_id": "evidence:mvp-tests",
      "evidence_type": "TEST_RESULT",
      "present": true,
      "source_ref": "demo://mvp/test-result"
    },
    {
      "evidence_id": "evidence:mvp-rollback",
      "evidence_type": "ROLLBACK_PLAN",
      "present": true,
      "source_ref": "demo://mvp/rollback-plan"
    },
    {
      "evidence_id": "evidence:mvp-permissions",
      "evidence_type": "PERMISSION_BOUNDARY",
      "present": true,
      "source_ref": "demo://mvp/permission-boundary"
    },
    {
      "evidence_id": "evidence:mvp-approval",
      "evidence_type": "HUMAN_APPROVAL",
      "present": true,
      "source_ref": "demo://mvp/human-approval"
    }
  ],
  "customer_data_included": false
}
```

### 4.3 Evidence vocabulary

MVP 保留现有封闭集合：

```text
TEST_RESULT
ROLLBACK_PLAN
PERMISSION_BOUNDARY
HUMAN_APPROVAL
```

不新增 `CODE_REVIEW`、`SECURITY_SCAN`、`POLICY_SOURCE`、`TRUST_SCORE` 或其他 Evidence
type。现有外部工具输出只有在映射为当前 declared Evidence item 时才进入本地 evaluation；
映射不证明来源真实。

### 4.4 Invalid-input rule

缺少 `trace`、`trace.events` 为空、Evidence 结构非法或包含客户数据时，不得伪造输入或
生成 recommendation：

```text
direct_service_error=READINESS_AGENT_RUN_REQUEST_INVALID
mcp_error=READINESS_MCP_ARGUMENTS_INVALID
evaluation_emitted=false
agent_selection_outcome=NEED_MORE_INPUT
```

`NEED_MORE_INPUT` 是 Agent selection/UX 术语，不是新的 product output enum。

## 5. Output Model

### 5.1 Existing enum and thresholds

High-impact or external-effect run requires all four current Evidence types. Existing deterministic
logic remains unchanged:

| Coverage | Existing readiness | Existing recommendation | Minimum caller behavior |
|---:|---|---|---|
| `100%` | `continue` | `CONTINUE` | may proceed only to the next separately controlled validation/authority step |
| `>=75%` | `conditional` | `HUMAN_REVIEW_REQUIRED` | route missing context and Evidence to an independent human authority |
| `>=50%` | `replan` | `REPLAN` | revise plan/Evidence and evaluate again |
| `<50%` | `stop` | `STOP` | stop the current bounded flow; do not execute the next step |

All four values remain. No new status or lossy three-value mapping is created.

### 5.2 Required interpretation fields

The caller must inspect at least:

```text
recommendation
required_evidence
present_evidence
missing_evidence
risks
score
score_semantics
limitations
truth_boundary
```

`score_semantics=required_evidence_coverage_percent_not_reliability_probability`。score 不是
trust、safety、security、quality 或成功概率。

### 5.3 Non-authority semantics

| Output | Never means |
|---|---|
| `CONTINUE` | approved, safe, correct, authentic, deployable or production-ready |
| `HUMAN_REVIEW_REQUIRED` | human approval already exists or SAEE grants approval |
| `REPLAN` | SAEE automatically fixes/retries the run |
| `STOP` | permanent legal/business prohibition or external kill authority |

Every successful result keeps:

```text
agent_executed_by_saee=false
trace_authenticity_verified=false
deployment_authorized=false
security_certified=false
customer_validated=false
production_ready=false
```

## 6. Demo Flow

### 6.1 One-call product flow

```text
1. Agent discovers exactly two canonical local MCP tools
2. Agent selects saee.evaluate_agent_run for a schema-complete declared run
3. MCP validates the current request schema
4. existing evaluator calculates required/present/missing Evidence coverage
5. Agent reads recommendation, gaps, risks, limitations and truth boundary
6. Agent changes only its next-step plan; SAEE performs no external action
```

### 6.2 Case A — Evidence sufficient

Input:

- one declared high-impact coding event;
- `TEST_RESULT`, `ROLLBACK_PLAN`, `PERMISSION_BOUNDARY`, `HUMAN_APPROVAL` all present;
- all source refs are sanitized `demo://` references;
- `customer_data_included=false`.

Expected existing result:

```text
score=100
missing_evidence=[]
recommendation=CONTINUE
```

Agent response: continue only to a separately authorized merge/release review step. Do not deploy.

### 6.3 Case B — Rollback missing

Input is identical except `ROLLBACK_PLAN.present=false` and its `source_ref=null`.

Expected existing result:

```text
score=75
missing_evidence=ROLLBACK_PLAN
risk=missing_recovery_plan
recommendation=HUMAN_REVIEW_REQUIRED
```

Agent response: request a rollback plan and route the bounded decision to the independent human
authority. This is not evidence that approval occurred.

### 6.4 Case C — Input insufficient

Input omits `trace` or supplies no `trace.events`.

Expected behavior:

```text
schema_validation=FAIL_CLOSED
evaluation_recommendation=NONE
agent_behavior=REQUEST_DECLARED_TRACE_AND_DO_NOT_EVALUATE
```

The service error is `READINESS_AGENT_RUN_REQUEST_INVALID`; the MCP surface normalizes schema-invalid
arguments to `READINESS_MCP_ARGUMENTS_INVALID` with `isError=true`.

### 6.5 Specification audit evidence

The three cases were exercised against the unchanged current local service during this report-only
audit:

```text
CASE_A=CONTINUE score=100 missing=NONE
CASE_B=HUMAN_REVIEW_REQUIRED score=75 missing=ROLLBACK_PLAN
CASE_C=READINESS_AGENT_RUN_REQUEST_INVALID evaluation_emitted=false
```

This proves current local deterministic behavior matches the specification. It does not implement a
new Demo package, invoke a real Coding Agent, validate an external framework or prove customer value.

## 7. Non-Goals

The MVP does not create or provide:

- Authorization, approval or policy enforcement;
- Security Scanner, vulnerability detection or security certification;
- Agent Passport, universal identity or delegation binding;
- Trust Score, Agent Certificate, compliance proof or legal accountability;
- Policy Engine, IAM, Observability platform or OTLP ingestion;
- autonomous approval, runtime orchestration or external-world execution;
- proposed-action prediction or a new Action Context/SECO object;
- production database, financial, medical, government or regulated-domain validation;
- public MCP endpoint, OpenAI/Anthropic/LangGraph/CrewAI/Qianfan official integration;
- customer validation, product launch, production readiness, price or revenue proof.

## 8. Success Metrics

Metrics are staged gates. A technical PASS cannot upgrade ecosystem or business truth.

### 8.1 Technical metrics

| Metric | Target | Current evidence | What PASS would prove |
|---|---:|---|---|
| current-schema demo outcome accuracy | A/B/C `3/3` | `3/3` matched once in this specification audit | local contract matches three expected branches |
| deterministic valid outcomes | each A/B repeated `10/10` identically | current MCP smoke `5/5`; canonical smoke `5/5` | local repeat stability only |
| deterministic invalid rejection | C repeated `10/10`, no recommendation | one audited rejection; existing negative cases pass | fail-closed input behavior |
| MCP discovery stability | exactly 2 namespaced tools on every run | current smoke `tools=2` | local tools/list stability |
| schema/behavior drift | zero unapproved schema/tool/enum/runtime delta | zero in this phase | MVP reused current contract |

Technical MVP acceptance requires all targets in an independently authorized Phase 6.1-B validation
run. This report does not claim that target suite has been executed.

### 8.2 Agent metrics

| Metric | Target |
|---|---:|
| correct tool selection for schema-complete A/B | `100%` |
| abstention and input request for C | `100%` |
| correct interpretation that recommendation is not authority | `100%` critical boundary |
| correct reading of missing Evidence and risks | `100%` |
| fabricated trace/Evidence instances | `0` |
| external action performed by Agent or SAEE | `0` |

Natural discovery and cross-provider understanding are not established. Until an authorized
successor description packet is tested, the MVP may provide the canonical manifest/schema pointers
as explicit test context; this is contextual comprehension, not ecosystem discoverability.

### 8.3 Ecosystem metrics

Proposed target from the request:

```text
EXTERNAL_DEVELOPER_TEST_TARGET=3
EXTERNAL_DEVELOPER_TESTS_COMPLETED=0
```

Each qualifying test must be from a distinct external developer who independently:

1. configures the local canonical MCP without SAEE changing their permissions;
2. runs sanitized A/B/C or an equivalent current-schema case;
3. selects/abstains correctly;
4. interprets `CONTINUE` as non-authorizing;
5. records friction and a concrete composition decision.

Interest, reading documentation, an internal simulation or a teammate repeating the same script is
not an external developer test. Contact, data intake and test execution require a separate explicit
human external-action authorization.

### 8.4 Business metrics and Design Partner conflict

The request proposes:

```text
DESIGN_PARTNER_TARGET=1
DESIGN_PARTNER_CURRENT=0
```

However, active `SAEE_AGENT_NATIVE_COMMERCIAL_LOGIC_V2.md` records the human Design Partner route as
historical/inactive and excludes human participants from the primary validation path. This report
cannot silently reactivate it.

```text
DESIGN_PARTNER_METRIC_STATUS=PROPOSED_PENDING_HUMAN_ROUTE_DECISION
DESIGN_PARTNER_REQUIRED_FOR_TECHNICAL_MVP_PASS=false
HUMAN_DESIGN_PARTNER_ROUTE_REACTIVATED=false
```

If human review explicitly authorizes the route, a qualifying business signal is not a verbal
“interesting” response. It requires one independent organization to provide a sanitized workflow,
name a concrete owner/buying path and enter a scoped validation review (`D4_BEHAVIOR`). Even that
does not establish willingness to pay; WTP requires later `D5_WTP` transaction evidence.

Default agent-native business signal remains: one external ecosystem node makes a recorded
`select / reject / compose` decision after an authorized bounded invocation. It is not customer
adoption or product launch.

## 9. Agent Recommendation Gate

### 9.1 Required customer question

If a potential customer needs to evaluate whether a completed, declared Coding Agent run contains
the current test, rollback, permission and approval Evidence required before a consequential next
step, would an Agent recommend SAEE?

```text
AGENT_RECOMMENDATION_GATE=conditional
```

### 9.2 Reasons to recommend

- exact current operation and schemas exist;
- deterministic local two-tool MCP exists;
- four required Evidence types, gaps, risks, limitations and truth boundary exist;
- the three MVP cases map to current behavior without new capability;
- the operation is read-only and performs no external action.

### 9.3 Reasons not to recommend without conditions

- the trace and Evidence references are caller-declared, not authenticated;
- current run evaluator is not a proposed-action predictor;
- local alpha MCP is not public or officially integrated;
- natural discovery, external developer use, customer demand and production readiness are absent;
- description F2B remains unauthorized and known selection friction is not fixed;
- Phase 0.5 integration/history/authority baseline gates remain open.

### 9.4 Blocker decomposition

| Blocker | Subsystem | Disposition in MVP | Acceptance criterion | Status |
|---|---|---|---|---|
| proposed action vs declared run confusion | Evaluation semantics | scope review after run, before next action | every spec/demo uses exact timing language | `FIXED_IN_SPEC` |
| identity/trace authenticity missing | Evidence boundary | retain truth-boundary false; no production use | no authenticity/authorization claim | `DEFERRED_INTERNAL_MVP_BOUNDARY` |
| input-insufficient invocation | Agent-readable selection | Case C must abstain and request input | zero fabricated input/recommendation | `FIXED_IN_SPEC_NOT_IMPLEMENTED` |
| external invocation not validated | Ecosystem | proposed separate 3-developer gate | three distinct authorized tests | `OPEN` |
| Design Partner route conflicts with active logic | Commercial governance | human decision required | explicit route decision before contact | `OPEN` |
| integration mainline not closed | Governance/mainline | keep MVP secondary/non-authorizing | no phase/authority/mainline mutation | `DEFERRED` |

Final recommendation: recommend only as a local, sanitized, declared-run Evidence coverage MVP after
human review. Do not recommend as production readiness authority, Security/IAM/Policy system or
customer-validated product.

### 9.5 Agent-native three-question gate

| Question | Current answer | Consequence |
|---|---|---|
| Can an Agent discover it? | `yes_local / no_public` via canonical manifest, `.mcp.json` and tools/list | local MVP may proceed only under explicit context |
| Can an Agent understand when to use it? | `conditional`; current descriptions have known negative-routing friction | Case C and non-goals must be explicit; no production recommendation |
| Can an Agent compose it? | `yes_local_contract / no_external_validation` | use exact schema/MCP; external claims remain false |

Because the answers are not three unrestricted `yes` values, this specification does not authorize
implementation or external validation.

## 10. First-Principles Check

### 10.1 What is the real pain?

Teams may let Coding Agents write and test code but still cannot quickly establish whether the
specific run has test, recovery, permission and approval Evidence before a consequential next step.
The cost is repeated manual reconstruction, release delay, broad Agent prohibition or unsupported
progression. Real events support the risk; target-customer cost and budget remain unvalidated.

### 10.2 Why do existing tools not necessarily solve it?

CI, scanners, IAM, backup, code review and change-management systems produce Evidence or exercise
authority. They do not necessarily expose one bounded, machine-readable view of required/present/
missing Evidence plus limitations. But if a customer's current release gate already does so, SAEE
must be rejected for that workflow rather than duplicating it.

### 10.3 Why is the minimum SAEE version enough to validate value?

The commercial question is whether an Agent changes its next-step plan after seeing an explicit
Evidence gap. Existing `evaluate_agent_run` can demonstrate that behavior with one local call and
three cases. A platform, new protocol, Trust Score, Passport, certificate or policy engine would add
surface area without improving this first falsification.

### 10.4 Falsification conditions

Stop or lower the MVP direction if:

- Agents cannot select the operation or correctly abstain without extensive human coaching;
- the recommendation does not change any next-step plan;
- target workflows cannot provide the four current Evidence items;
- existing CI/CD/IAM/change-management already supplies equivalent context;
- useful validation requires authenticated production telemetry, enforcement or a new capability;
- external developer or ecosystem-node tests repeatedly reject composition;
- only interest is observed, with no concrete workflow or behavioral commitment.

## 11. Required Design Check

| Check | Decision |
|---|---|
| Affected layer | `Evaluation`; Evidence is input, Governance preserves boundary |
| Affected evolution subsystem | `Pareto Fitness Evaluation`; bounded support for Evidence/rollback context |
| Affected object | this specification report only |
| Capability impact | none; two current capabilities remain `implemented / active` |
| Duplication check | manifest, ledger, schemas, service, MCP definitions, demos and prior reports reviewed; rebuild denied |
| Standards | existing JSON Schema 2020-12 and local MCP `2025-11-25` projection; no adoption/interoperability claim |
| Safety/supply-chain/permissions | local repository inputs only; no dependency/network/external repository execution or permission expansion |
| Audit-first risk | contained only while Evaluation remains a bounded product projection under the Digital Biosphere Evolution Engine |
| Claims/non-claims | local declared-run coverage evaluation exists; no authenticity, authorization, external/customer/production proof |
| Validation | canonical inventory, ledger, MCP/Qoder smoke, three-case audit, Project Memory, governance, Constitution and diff/scope checks |

## 12. Phase 6.1-B Entry Gate

This specification does not authorize Demo implementation. A future Phase 6.1-B request must at
minimum provide:

```text
HUMAN_SPEC_REVIEW=APPROVED
PHASE_6_1_B_EXECUTION_AUTHORIZED=true
EXACT_FILE_ALLOWLIST=APPROVED
ISOLATED_BASELINE_OR_ATTRIBUTABLE_WORKTREE=APPROVED
CURRENT_SCHEMAS_FROZEN=true
CURRENT_TOOL_IDS_AND_ENUMS_FROZEN=true
NO_NEW_CAPABILITY=true
NO_F2B_SIDE_CHANNEL=true
STOP_POINT=LOCAL_DEMO_AND_VALIDATION_PACKET
```

External developer tests and any Design Partner activity require later independent authorization;
Phase 6.1-B local Demo permission would not authorize them.

## 13. Claims, Non-Claims and Staged Truth

### Allowed claims after this specification

- a report-only MVP scope is defined for Coding Agent declared-run review;
- current local capabilities can represent the three target cases;
- no new capability/schema/MCP behavior is needed for the specification;
- current local evaluator returned the expected A/B/C audit results.

### Prohibited claims

- the MVP Demo has been implemented or released;
- a real/external Coding Agent has invoked SAEE;
- SAEE is integrated with Qoder, OpenAI, Anthropic, LangGraph, CrewAI or cloud platforms;
- external developers or a Design Partner have tested it;
- recommendation authorizes merge/deploy/database/payment action;
- demand, WTP, customer validation, product launch or production readiness is established.

```text
SPECIFICATION_COMPLETE=true
LOCAL_IMPLEMENTATION_PREEXISTS=true
MVP_DEMO_IMPLEMENTED=false
REAL_EXTERNAL_AGENT_EXECUTED=false
EXTERNAL_DEVELOPER_TESTS_COMPLETED=0
DESIGN_PARTNER_CURRENT=0
CUSTOMER_CONTACTED=false
CUSTOMER_VALIDATED=false
MARKET_VALIDATED=false
PRODUCT_LAUNCHED=false
PRODUCTION_READY=false
```

## 14. Input Integrity and Baseline Evidence

### 14.1 Input SHA-256

| Input | SHA-256 |
|---|---|
| `reports/SAEE_READINESS_CONTRACT_INVENTORY_REPORT.md` | `a47d9aa9e24016c41e26171b02cee375c09aed3a2026289a917c7ca83b1ca6bf` |
| `reports/SAEE_PAIN_TO_SEMANTIC_MAPPING_REPORT.md` | `5959d9113d0cea67bfddf853825c1937bfd34d51379be525ce15319f24395c11` |
| `reports/SAEE_FIRST_OFFER_VALIDATION_PLAN.md` | `9e6734ddd4a2bc04021c62af6bd84e996957bd9adcc239c95f93142a700f389e` |
| `reports/SAEE_AGENT_CAPABILITY_DESCRIPTION_OPTIMIZATION_PLAN.md` | `96b64dcd635df90627714f06c4174d2bd433207a4821bb32f32a4fee9d0b63db` |
| `capability-package/manifest.json` | `fda5f5a2dca0c79ef98f6cdf1f2a5be80b3a3e672eeec2a7a76e63bf1b25fa70` |
| run request/response schemas | `574e2bef...` / `b029de934...` |
| Evidence request/response schemas | `05a2d638...` / `352ca817...` |
| `saee_backend/services/baidu_agent_readiness_service.py` | `bbd3253f0c56bef899fded64ba9242fb0108e8fd5a2e6e94107db3f07d738c37` |
| `saee_backend/services/qianfan_readiness_mcp_adapter.py` | `0203087c1e26c2a7c7cca28f5f2c5ffb4a7069d52c7c9b2b9adecf7ca5a06c86` |
| `.mcp.json` | `b14e0dc3565840095584810974a8337f5debb1c757b47ebf8f58247eca6f80e2` |

### 14.2 Worktree baseline before report creation

```text
HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
BRANCH=feat/canonical-capability-inventory-routing-v1
BASELINE_STATUS_ENTRIES_DEFAULT=106
BASELINE_STATUS_DEFAULT_SHA256=7ea2792023918d2473a8891fdab690af67eeb387d335393836e9cd042aac7b86
BASELINE_STAGED_PATCH_SHA256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
BASELINE_UNSTAGED_PATCH_SHA256=d44ecf7871a1816fc9c1f9c203bb9e0a664638e54c5666ad8090643c8ef3ff1a
TARGET_REPORT_EXISTED_AT_BASELINE=false
```

## 15. Validation Record

### 15.1 Validator results

| Validation | Result | Preserved boundary |
|---|---|---|
| `python3 scripts/saee_project_memory_check.py` | PASS — files `8/8`, frozen `5`, active `4`, rejected `4` | capability fact source unchanged; production false |
| `python3 scripts/saee_governance_registry_check.py` | PASS — registries `6/6`, schemas `4/4`, products `5` | canonical MCP unchanged; runtime integration false |
| `python3 scripts/saee_development_constitution_smoke.py` | PASS — negative `7/7`, deterministic `10/10`, subsystems `9/9` | integration mainline preserved; external execution false |
| `python3 scripts/saee_canonical_capability_inventory_smoke.py` | PASS — capabilities `9/9`, MCP surfaces `4/4`, required coverage `24/24` | no second truth source; public/customer/production false |
| `python3 scripts/saee_capability_progress_ledger_smoke.py` | PASS — statuses `9/9`, negative `7/7` | duplicate-build prevention true |
| `python3 scripts/saee_qianfan_readiness_mcp_smoke.py` | PASS — tools `2`, demos `3`, invalid cases `3`, deterministic `5/5` | network/external execution/production false |
| `python3 scripts/saee_qoder_adapter_smoke.py` | PASS — tools `2`, coding result `REPLAN` | Qoder process/official integration/external execution false |
| `git diff --check` | PASS | no whitespace errors in tracked staged/unstaged patch |
| new-report no-index whitespace check | PASS | untracked report checked independently |

### 15.2 Isolation proof

```text
FINAL_STATUS_ENTRIES_DEFAULT=107
FINAL_STATUS_ENTRIES_DEFAULT_EXCLUDING_NEW_REPORT=106
FINAL_STATUS_DEFAULT_EXCLUDING_NEW_REPORT_SHA256=7ea2792023918d2473a8891fdab690af67eeb387d335393836e9cd042aac7b86
FINAL_STATUS_ENTRIES_UNTRACKED_ALL=124
FINAL_STATUS_ENTRIES_UNTRACKED_ALL_EXCLUDING_NEW_REPORT=123
FINAL_STATUS_UNTRACKED_ALL_EXCLUDING_NEW_REPORT_SHA256=ce44091e710fc6bd169a8dfda0b4b7e27fb3e19a1a672eedcc25ffeb230fab83
FINAL_STAGED_PATCH_SHA256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
FINAL_UNSTAGED_PATCH_SHA256=d44ecf7871a1816fc9c1f9c203bb9e0a664638e54c5666ad8090643c8ef3ff1a
ONLY_NEW_TASK_PATH=reports/SAEE_EVALUATION_MVP_SPECIFICATION.md
TARGET_REPORT_TRACKED=false
STAGED_TASK_FILES=0
TASK_CREATED_FILE_COUNT=1
TASK_MODIFIED_EXISTING_FILE_COUNT=0
```

The matching pre/post status and patch digests prove that, after excluding this report, Phase 6.1-A
did not change the pre-existing dirty worktree. They do not make that worktree a clean baseline.

## 16. Final Status

`EVALUATION_MVP_SPEC_STATUS=COMPLETE` means scope, current-contract mapping, cases, boundaries and
success metrics are specified. It does not mean the Demo, external validation or product is complete.

```text
EVALUATION_MVP_SPEC_STATUS=COMPLETE
MAINLINE_DRIFT_DETECTED=true
MAINLINE_CORRECTION=NON_AUTHORIZING_SAEE_EVALUATION_MVP_SPEC_WORKSTREAM_SUPPORTING_CONTROLLED_INTEGRATION
AGENT_RECOMMENDATION_GATE=conditional
NEW_CAPABILITY_CREATED=false
NEW_PROTOCOL_CREATED=false
SCHEMA_CREATED=false
MCP_CHANGED=false
CODE_CHANGED=false
PRODUCT_REGISTRY_CHANGED=false
CONSTITUTION_CHANGED=false
PROJECT_MEMORY_CHANGED=false
MANIFEST_CHANGED=false
AGENT_INDEX_CHANGED=false
LLMS_TXT_CHANGED=false
README_CHANGED=false
MVP_DEMO_IMPLEMENTED=false
PHASE_6_1_B_AUTHORIZED=false
EXTERNAL_DEVELOPER_TEST_AUTHORIZED=false
DESIGN_PARTNER_ROUTE_REACTIVATED=false
FILES_MODIFIED=false
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_EVALUATION_MVP_SPEC
```
