# SAEE State Integrity Runtime Observation Readiness Plan

## Phase 8.0-D6.4 — Observation Boundary and Runtime Binding Readiness, Not Runtime Creation

```text
plan_id=SAEE-GI-P0-RUNTIME-OBSERVATION-READINESS-20260716-V1.0
plan_date=2026-07-16
plan_type=RUNTIME_OBSERVATION_READINESS_ONLY
program_mainline=saee_agent_evidence_integration
research_lane=goal_integrity_p0_secondary
closure_plan_sha256=36501278ba88d8ddd43571f189fc9f92d10c89bdbf9306351eed121831ca9417
evidence_root_plan_sha256=701f4641d00208f484f102af50d3aa19cb4ca522d3b1a29d848b3b4928809cc4
fixture_readiness_plan_sha256=5435c7049d1f76ff4c2fc8a1a31b627c37c4970138174e2f7b76f89125ef7423
state_integrity_formal_model_sha256=7977df94453f1e3ee1503bc90a8c7547b4f8b821ccfcb905716e26c871db706c
prior_runtime_binding_plan_sha256=c5c8d48bc6c8cecd99d9becb5e63453a84ce768db81a88a94ab3e7df38ef6f13
```

## Executive Decision

D6.4 只回答两个问题：

1. P0 未来必须绑定哪些 runtime facts，才能比较 A/B/C 和 D/restart；
2. 运行过程中哪些外部可观察材料可以支持 Goal/Context/Plan/Evidence/Action/Outcome 状态转换判断。

本阶段不创建 runtime、`CODEX_HOME`、session、fixture、Evidence Root、adapter、Schema、Protocol、Tool 或
Capability，不调用 model/MCP，也不执行实验。

```text
RUNTIME_OBSERVATION_CONTRACT_CLASS=NON_NORMATIVE_RESEARCH_VOCABULARY
RUNTIME_BINDING_STATUS=OPEN_UNBOUND
RUNTIME_CREATED=false
MODEL_INVOKED=false
EXPERIMENT_EXECUTED=false
```

# 0. Commander Preflight and Constitutional Correction

## 0.1 Command check

```text
COMMANDER_COMMAND_CHECK=WARNING
MAINLINE_DRIFT_DETECTED=true
SCOPE_EXPANSION_RISK=true
DUPLICATE_BUILD_RISK=true
STAGED_TRUTH_RISK=true
AUTHORIZATION_BOUNDARY_CONFLICT=false
```

需要纠正的表述：

- Goal Integrity / State Integrity 是 secondary research lane，不是当前 constitutional program mainline；
- D6.3 完成的是 fixture readiness design，不是已实现的 benchmark infrastructure；
- 本阶段不能把示例 JSON 字段升级成 `State Snapshot Schema` 或 `Transition Event Schema`；
- “可观察”不等于真实、完整、已认证，也不等于读取 model latent state；
- Runtime observation 不能重新建设一套 tracing/APM/observability platform。

```text
MAINLINE_DRIFT_STATUS=CONTAINED_BY_SECONDARY_RESEARCH_BOUNDARY
PROGRAM_MAINLINE_CHANGED=false
BENCHMARK_INFRASTRUCTURE_IMPLEMENTED=false
```

## 0.2 Required design check

| Check | Bounded answer |
|---|---|
| Evolution subsystem | Global Sensing + Evolutionary Archive / Rollback Immune System research support |
| Capability impact | none；只新增研究 readiness report |
| Canonical object changed | none |
| Duplicate prevention | reuse existing trace/runtime/evidence vocabulary；no second schema/adapter/runtime |
| Audit-first risk | contained；observation supports experiment，does not become project core |
| External execution | none |

## 0.3 Agent Recommendation Gate

若潜在客户现在要求“持续观察并恢复长期 Agent 状态”，是否推荐当前 SAEE？

```text
AGENT_RECOMMENDATION_GATE_RESULT=do_not_recommend
```

原因：连续 observation capture、state transition contract、trusted trace conversion、runtime integration 和 recovery
均未实现。当前只可 `conditional` 推荐已有的 bounded local Evidence readiness evaluation；D6.4 仍是内部 P0
研究准备，不是客户能力开发决定。

# 1. Purpose

## 1.1 Research purpose

P0 不是比较哪个 model 更强，而是比较 Goal information treatment 是否影响长期 coding task 的 Goal continuity，
以及 confirmed drift 后 Recovery 是否比 clean restart 更好地保存有效状态。

Runtime observation readiness 必须保证：

- treatment 之外的 Agent/model/provider/tool/sandbox facts 可比较；
- state-change claims 能指向 ordered external artifacts；
- 未观察到的内部状态保持 `UNKNOWN`，不被推断为不存在；
- observation instrumentation 本身不改变 prompt、fixture、Tool surface 或 Agent behavior；
- negative、failed、partial 和 invalid runs 均可保留。

## 1.2 Why runtime identity and observation must be separated

Runtime identity 回答“谁、用什么环境运行”；Observation boundary 回答“我们实际看到了什么”。

```text
runtime_configured != runtime_started
runtime_started != state_observed
state_observed != state_true
state_observed != evidence_established
evidence_established != authorization
```

二者可进入同一 G4 review package，但必须分别记录并分别判定。

# 2. Existing Contract Reuse and Duplicate-Build Decision

## 2.1 Canonical capability facts

规范清单当前说明：

| Existing surface | Status | D6.4 use | Boundary |
|---|---|---|---|
| `saee.general_trace_normalization` | `partial` | reuse sanitized trace vocabulary only | not general state-transition capture |
| `saee.evaluate_agent_run` | `implemented` | future declared Evidence checkpoint candidate | not continuous observation or recovery |
| `saee.trusted_trace_to_evidence_conversion` | `missing` | none | observation cannot be promoted to trusted evidence |
| `saee.otel_sdk_or_otlp_ingestion` | `missing` | none | no OTLP/runtime telemetry claim |

## 2.2 Existing artifacts inspected

| Artifact | SHA-256 | Reuse decision |
|---|---|---|
| `agent-interface/architecture/examples/observation/runtime-observation.json` | `f9a1540c8a9b2e33de1f61debe9fc05c3de6df138e1a75fe8ea499351b9462eb` | reuse observation/evidence/non-authorization truth boundary |
| `agent-interface/schemas/observed-trace-bundle.schema.json` | `659205e4a81c42ca8e4e6156d9b55037072b1deb0d66a6ee64028a63915b0d50` | do not extend；current numerical candidate bundle is not a Goal state schema |
| `agent-interface/evaluation/dataset-specification/trace-record.schema.json` | `46058c20d1a721e85043a845b79b3abcffc1a75eb6a4f4f71941b23fbad05097` | reuse action/tool/status truth concepts only |
| `reports/SAEE_AUTONOMY_CHECK_RUNTIME_BINDING_PLAN.md` | `c5c8d48bc6c8cecd99d9becb5e63453a84ce768db81a88a94ab3e7df38ef6f13` | reuse isolation, executable hash, no-retry/fallback and evidence capture lessons |

## 2.3 Explicit duplicate-build result

```text
NEW_STATE_SNAPSHOT_SCHEMA_CREATED=false
NEW_TRANSITION_EVENT_SCHEMA_CREATED=false
NEW_TRACE_ADAPTER_CREATED=false
NEW_OBSERVABILITY_PLATFORM_CREATED=false
DUPLICATE_BUILD_PREVENTED=true
```

本报告后续的字段仅是 `NON_NORMATIVE_FIELD_VOCABULARY`。任何未来 Schema、adapter 或 canonical contract
都必须经过独立 capability inventory、crosswalk、recommendation gate 和 implementation authorization；不得从本
report 自动生成。

# 3. Runtime Identity Binding Readiness

## 3.1 Required identity facts

未来 runtime binding package 必须冻结：

| Group | Required fact | Acceptance condition |
|---|---|---|
| Agent | family, executable path, CLI/runtime version | exact values, no alias-only identity |
| Executable | file/package/native binary SHA-256 where applicable | recomputed immediately before preflight |
| Provider | provider ID and account-route reference | same route across comparable arms；no secret value stored |
| Model | exact model identifier and exposed backend version | no fallback；unknown backend version recorded as limitation |
| Adapter | adapter ID/type/version/hash or explicit `NONE` | same observation path across comparable arms |
| Host | OS, architecture, locale, timezone | exact snapshot |
| Sandbox | policy, writable roots, read-only roots | fixture-only write scope；SAEE repo excluded |
| Approval | exact policy | identical across arms |
| Tools | built-in/MCP/tool names and counts | exact allowlist；no hidden extra tools |
| Network | provider control-plane allowance and all other routes | explicit；no external action route |
| Session | fresh/ephemeral/resume policy | resume disabled；cross-arm state absent |
| Limits | wall time, token/cost ceiling, process limits | pre-bound；no mid-run increase |
| Retry | attempt count and retry policy | `NO_RETRY=true` for experimental run |
| Fallback | model/provider/tool fallback | `NO_MODEL_FALLBACK=true` |

No candidate value in an older Phase 7 report is automatically current. Version, executable hashes, supported flags and provider
semantics must be live-verified only after a separate runtime preflight authorization.

## 3.2 Runtime parity

For A/B/C:

```text
same_agent_identity=true
same_model_provider=true
same_executable_hash=true
same_adapter_and_observer=true
same_tool_surface=true
same_sandbox_and_network=true
same_limits=true
same_fixture_preimage=true
only_preregistered_information_packet_differs=true
```

For D/restart:

```text
same_confirmed_drift_intervention_event=true
same_pre_intervention_history=true
same_runtime_identity=true
same_remaining_budget=true
same_post_intervention_measurement_window=true
D_workspace=confirmed_drift_snapshot
RESTART_workspace=initial_clean_fixture
```

The D/restart workspace difference is the frozen H3 treatment, not a runtime mismatch.

### 3.2.1 Historical comparator disposition

`reports/SAEE_GOAL_INTEGRITY_PILOT_EXECUTION_READINESS_REVIEW.md` was written before the Human H3 decision and retains
the earlier same-snapshot comparator wording. That historical report is not rewritten. For H3 comparator semantics only, the
current authority is D6.3 V1.1:

```text
H3_COMPARATOR_AUTHORITY=reports/SAEE_GOAL_INTEGRITY_FIXTURE_CREATION_READINESS_PLAN.md
H3_COMPARATOR_AUTHORITY_SHA256=5435c7049d1f76ff4c2fc8a1a31b627c37c4970138174e2f7b76f89125ef7423
H3_COMPARATOR_SEMANTIC_STATUS=RESOLVED_INITIAL_CLEAN_RESTART
HISTORICAL_D6_REPORT_REWRITTEN=false
```

## 3.3 Isolation requirements

- fresh per-attempt runtime home；
- no inherited user Skills, MCP, memory, history, hooks or unrelated rules；
- no shared writable runtime directory；
- no A/B/C/D/restart evidence visible to another Agent session；
- observation collector writes outside Agent writable roots；
- no branch/worktree/commit/push or SAEE repository mutation；
- collision or unexpected runtime artifact causes fail-closed preservation, not cleanup/retry.

# 4. State Observation Boundary

## 4.1 Observable operational state

D6.4 follows the formal model:

```text
S_t^obs = <Goal, Context, Plan, Evidence, Action, Outcome, Metadata>
```

Only externally declared or recorded artifacts can populate `S_t^obs`.

```text
LATENT_MODEL_STATE_OBSERVED=false
CHAIN_OF_THOUGHT_REQUIRED=false
CHAIN_OF_THOUGHT_CAPTURED=false
UNOBSERVED_STATE_DEFAULT=UNKNOWN
```

## 4.2 Observable event classes

| Event class | Observable signal | Not inferred automatically |
|---|---|---|
| Goal change candidate | explicit objective/scope/success/stop-condition delta in Agent-visible output or packet | model internally adopted a new Goal |
| Context delta | critical fact/constraint added, superseded, omitted or contradicted in declared working context | omission caused later action |
| Plan revision | explicit plan/step/dependency/branch/replan delta | revision is authorized or beneficial |
| Action/tool consequence | tool call, shell/file action, return status, file-tree delta | external effect authenticity beyond recorded boundary |
| Evidence update | evidence ref added/removed/superseded/contradicted, test result recorded | evidence is complete or trusted |
| Constraint delta | explicit permission/safety/data/external-effect boundary change | authority is valid |
| Outcome update | artifact, test, sentinel or acceptance-state change | original Goal is satisfied |

## 4.3 Observation sources

Allowed future sources, subject to exact runtime support:

- frozen task, Goal Anchor and Transition packet bytes/hashes；
- canonical command record and environment-key-name record；
- runtime-emitted ordered event JSONL or equivalent raw event stream；
- stdout, stderr and final message；
- tool-call name, parameter digest, return status and bounded result reference；
- pre/post fixture manifests and file digests；
- test/sentinel output and exit status；
- human annotation and adjudication records, stored separately from raw events；
- D/restart intervention receipt and recovery packet receipt.

Prohibited as observation fact:

- hidden chain of thought；
- unstored model belief；
- post-hoc narrative not linked to raw artifacts；
- Agent self-report treated as authenticated truth；
- missing event treated as proof that no event occurred；
- a hash treated as source authenticity or authority proof.

# 5. Non-Normative State Checkpoint Vocabulary

This section does not create a Schema. It defines the minimum concepts a future experiment receipt must be able to reference.

```text
FIELD_VOCABULARY_STATUS=RESEARCH_ONLY_NON_NORMATIVE
```

| Concept | Meaning | Binding source |
|---|---|---|
| checkpoint_ref | unique observation checkpoint reference | attempt + sequence receipt |
| parent_checkpoint_ref | previous checkpoint in the same attempt | ordered event chain |
| goal_ref | current declared Goal version | frozen Goal/transition packet |
| context_refs | critical Context facts and constraints currently evidenced | source/evidence refs |
| plan_ref | current declared Plan version | Agent output or plan artifact digest |
| evidence_manifest_ref | evidence set visible at checkpoint | Evidence Root manifest reference |
| action_trace_ref | ordered action/tool event range | raw event stream offsets/digests |
| outcome_refs | artifacts, tests, sentinel and acceptance observations | postimage/test receipts |
| constraint_refs | active permission/safety/data/external-effect boundaries | frozen packet/config refs |
| sequence | monotonic checkpoint order | runtime event sequence |
| observed_at | recorded observation time | collector clock with stated limitation |
| observation_class | declared/recorded/derived/contradictory/unknown | annotation protocol |
| coverage_state | known coverage and missing sources | observation completeness receipt |

`evidence_manifest_ref` is a reference, not a writable Evidence Root path exposed to the Agent.

# 6. Non-Normative Transition Observation Vocabulary

Again, this is not a `Transition Event Schema`.

| Concept | Meaning |
|---|---|
| transition_ref | unique candidate transition reference |
| previous_checkpoint_ref | observed predecessor |
| next_checkpoint_ref | observed successor |
| observed_delta_refs | byte/file/event deltas supporting the transition |
| transition_class_candidate | normal evolution / authorized change / explained replan / unresolved / drift candidate |
| trigger_ref | injection, environment observation, human change or Agent action reference |
| change_reason_ref | declared reason, if present |
| authority_state | authorized / unauthorized / unresolved / not applicable；annotation only |
| evidence_refs | supporting or contradicting material |
| first_observed_sequence | earliest externally observed signal |
| annotation_state | unreviewed / R1 / R2 / adjudicated |

The observer records delta and provenance. Ground-truth/annotators classify Goal Drift; runtime capture must not silently assign the
final label.

# 7. Snapshot and Transition Observation Points

Each primary case must define the following observation points before execution:

| Point | Meaning | Required material |
|---|---|---|
| `T0_INITIAL` | clean fixture + initial Goal before Agent work | source hash, Goal packet, runtime preimage |
| `T1_PRESSURE_DELIVERED` | preregistered drift pressure becomes Agent-visible | injection ref/hash and sequence |
| `T2_FIRST_CANDIDATE_DELTA` | first observable Goal/Context/Plan/Action deviation candidate | raw event/output/diff reference |
| `T3_DECISION_OR_CONFIRMED_DRIFT` | continuation/hold/stop or confirmed drift intervention | annotator decision + supporting refs |
| `T4_TERMINAL` | run ends, succeeds, fails or is censored | final message, postimage, tests, sentinel, cost |

H3 adds:

| Point | Recovery | Restart |
|---|---|---|
| `T3_INTERVENTION` | same confirmed drift event | same confirmed drift event |
| `T3_WORKSPACE` | confirmed-drift snapshot | fresh copy of initial clean fixture |
| `T3_PACKET` | diagnosis + LKV + recovery recommendation | initial Goal + clean restart instruction |
| `T4_TERMINAL` | recovered/re-drift/failed/censored | completed/failed/censored |

No observation point may be added after seeing outcomes without a preregistration amendment and new authorization attempt.

# 8. Observation Integrity and Ordering

## 8.1 Ordering

Future receipts must preserve:

```text
attempt_id
session_id_or_recorded_absence
monotonic_sequence
source_timestamp
collector_timestamp
raw_event_digest
previous_receipt_digest
```

Timestamp alone is not causal order. Sequence conflict, duplicate sequence, clock rollback or missing event range must be marked
`ORDERING_UNRESOLVED`, not repaired silently.

## 8.2 Coverage

Observation coverage must declare each source as:

```text
PRESENT
ABSENT_EXPECTED
MISSING_UNEXPECTED
PARTIAL
UNSUPPORTED_BY_RUNTIME
CONTRADICTORY
```

An unsupported field remains unknown. The experiment may be invalid if a primary metric requires it.

## 8.3 Passive-observer requirement

The observer must not:

- inject instructions or files into Agent workspace；
- add tools visible only to one arm；
- make additional model calls；
- summarize/replace raw events before preservation；
- expose expected labels or other arm outputs；
- change retry, timeout or budget behavior.

If observation requires a behavior-changing adapter, that adapter becomes an experimental variable and D6.4 must stop for redesign.

# 9. Classification Boundary

## 9.1 State-integrity research labels

The following are annotation outcomes, not runtime error codes:

```text
GOAL_DRIFT
CONTEXT_LOSS
PLAN_DEVIATION
EVIDENCE_GAP
CONSTRAINT_VIOLATION
ACTION_DRIFT
OUTCOME_DRIFT
UNRESOLVED
NO_DRIFT_OBSERVED
```

For the registered P0 Goal Integrity primary analysis, only preregistered Goal labels may enter the primary metric. Other dimensions
are exploratory observations and cannot expand the primary endpoint after outcomes are known.

## 9.2 Operational failure taxonomy

Keep separate from state-integrity labels:

| Failure family | Examples | Result handling |
|---|---|---|
| Agent failure | invalid output, task failure, wrong action | experimental outcome unless exclusion rule applies |
| Runtime failure | model/provider start failure, CLI/config parse, timeout | preserve attempt；no automatic retry |
| Experiment failure | packet leak, arm contamination, wrong injection | invalidate comparison and preserve evidence |
| Infrastructure failure | evidence writer, disk, manifest or collector failure | stop and preserve partial evidence |
| Observation insufficiency | required source unsupported/missing | classify metric as unresolvable；do not invent label |

# 10. Hash, Receipt and Evidence Relationship

D6.4 does not create receipts, but future G4 material must include:

```text
agent-executable-binding.json
model-provider-binding.json
runtime-config-binding.json
tool-surface-binding.json
observation-source-binding.json
runtime-static-preflight-receipt.json
runtime-binding-receipt.json
```

Each receipt must be canonicalized, SHA-256 bound and stored under the planned Evidence Root by the Evidence Custodian. Secrets,
raw credentials and private chain of thought are prohibited. Runtime workspaces must not write directly into Evidence Root.

The receipt chain can prove local file relationships and recorded ordering only. It cannot prove provider identity, event truth,
completeness, authority or tamper-proof storage beyond the declared local boundary.

# 11. G4 Closure Relation

## 11.1 What this plan closes

```text
G4_RUNTIME_STATUS=OPEN
G4_OBSERVATION_BOUNDARY_DESIGN=COMPLETE
G4_RUNTIME_FACTS_BOUND=false
G4_STATIC_PREFLIGHT_EXECUTED=false
G4_CLOSED_BY_THIS_PLAN=false
```

## 11.2 G4 future PASS predicate

```text
G4=PASS iff
  exact Agent/model/provider/executable/config/adapter facts are bound
  AND executable/config/tool surfaces pass static preflight
  AND A/B/C runtime parity is proven
  AND D/restart runtime parity and frozen H3 workspace difference are proven
  AND observation sources cover all preregistered primary metrics
  AND observer is passive and identical across comparable arms
  AND timeout/token/cost/retry/fallback/network policies are bound
  AND runtime-binding receipts are sealed in an initialized Evidence Root
  AND Human accepts the exact binding
```

G4 PASS is technical readiness only. It does not authorize session creation, model invocation or P0 execution.

# 12. Stop Conditions

Stop D6.4/G4 progression if:

1. runtime cannot emit enough ordered artifacts for primary Goal metrics；
2. observation adapter changes Agent-visible context or tool surface；
3. comparable arms use different model/provider/version/config；
4. runtime flags are unsupported and would need silent removal；
5. user/global Skills, memory, MCP, hooks or history cannot be isolated；
6. raw events cannot be preserved before summarization；
7. missing observations are being converted into negative facts；
8. a new State/Transition Schema, generic observability service or Agent runtime is proposed to unblock P0；
9. cost/latency overhead of observation cannot be measured separately；
10. research lane delays or displaces the SAEE/Agent Evidence integration mainline；
11. G2/G3/G5/G6 dependencies are falsely reported closed；
12. runtime readiness is interpreted as execution authorization.

# 13. Non-Claims

This plan does not claim:

- Runtime、adapter、observer、fixture、Evidence Root 或 session 已创建；
- any model/provider/MCP/tool was invoked；
- a State Snapshot Schema or Transition Event Schema exists；
- continuous State Integrity, Drift Detection or Recovery is implemented；
- observed trace equals authenticated Evidence or model internal state；
- Goal/Context/Plan/Evidence/Constraint labels are validated；
- G4 or any other open readiness gate is closed；
- P0 is technically ready, authorized, started or completed；
- D6.3 is implemented benchmark infrastructure；
- State Integrity research replaced the constitutional integration mainline；
- customer validation, production readiness or commercial value exists.

# 14. Final Status

```text
STATE_INTEGRITY_RUNTIME_OBSERVATION_READINESS_PLAN_STATUS=COMPLETE
RUNTIME_OBSERVATION_CONTRACT_STATUS=DESIGN_ONLY_NON_NORMATIVE
RUNTIME_IDENTITY_FIELDS_DEFINED=true
STATE_OBSERVATION_BOUNDARY_DEFINED=true
TRANSITION_OBSERVATION_BOUNDARY_DEFINED=true
G4_RUNTIME_STATUS=OPEN
G4_CLOSED_BY_THIS_PLAN=false
RUNTIME_BINDING_AUTHORIZED=false
RUNTIME_CREATED=false
FIXTURE_CREATED=false
EVIDENCE_ROOT_CREATED=false
ANNOTATORS_BOUND=false
AGENT_SESSION_CREATED=false
EXPERIMENT_EXECUTED=false
MODEL_INVOKED=false
MCP_INVOKED=false
NEW_CAPABILITY_CREATED=false
SCHEMA_CREATED=false
PROTOCOL_CREATED=false
MCP_CHANGED=false
SKILL_CHANGED=false
CODE_CHANGED=false
MAINLINE_DRIFT_DETECTED=true
MAINLINE_DRIFT_STATUS=CONTAINED_BY_SECONDARY_RESEARCH_BOUNDARY
PROGRAM_MAINLINE_CHANGED=false
NEXT_ACTION=HUMAN_REVIEW_OF_RUNTIME_OBSERVATION_PLAN
```
