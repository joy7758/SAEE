# SAEE Goal Integrity Final Human Authorization Record

## Phase 8.0 — Inactive P0 Authorization Record Template, Not an Execution Grant

```text
document_id=SAEE-GI-P0-FINAL-HUMAN-AUTHORIZATION-RECORD-20260716-V1.0
document_date=2026-07-16
document_type=INACTIVE_AUTHORIZATION_RECORD_TEMPLATE_ONLY
record_scope=GOAL_INTEGRITY_P0_SECONDARY_RESEARCH_LANE
program_mainline=saee_agent_evidence_integration
research_lane=goal_integrity_p0_secondary
authorization_gate=G8
authorization_decision=NOT_RECORDED
authorization_status=OPEN_NOT_GRANTED
```

Bound design sources：

```text
final_human_gate_review_path=reports/SAEE_GOAL_INTEGRITY_FINAL_HUMAN_GATE_REVIEW.md
final_human_gate_review_sha256=4bb01cd05c21087b08ae61ac425a62e05ebddaab8b427497d6cb06d827860f87
closure_plan_path=reports/SAEE_GOAL_INTEGRITY_PILOT_EXECUTION_CLOSURE_PLAN.md
closure_plan_sha256=36501278ba88d8ddd43571f189fc9f92d10c89bdbf9306351eed121831ca9417
preregistration_path=reports/SAEE_GOAL_INTEGRITY_PILOT_PREREGISTRATION.md
preregistration_sha256=db3deadd762897027ed85cf4217e67e68dc1071764ece74f7a3ffe7d828f2493
d6_3_fixture_readiness_plan_sha256=5435c7049d1f76ff4c2fc8a1a31b627c37c4970138174e2f7b76f89125ef7423
d6_4_runtime_observation_plan_sha256=d040e62adc69171fe65b0ea82842fe57055ae5ccbd41b91f4e2dd5230c31d3d2
d6_5_annotation_readiness_plan_sha256=9dc3c3ae8a53cdc2292ad2392a79bbcaf722e86717856fe5b3641a723ff310c7
reused_generic_authorization_template_path=reports/SAEE_H0_R_AUTHORIZATION_RECORD_TEMPLATE.md
reused_generic_authorization_template_sha256=17e5e76e05b79c902e6d6c6e4b5e18ea3b54662f55fc637dc0e04e40cd96d708
```

## Executive Boundary

本文件只定义未来 Goal Integrity P0 one-use Human authorization record（一次性人工授权记录）
需要绑定的字段、允许范围、禁止事项、消费规则和停止条件。它不是已签署授权，不创建授权实例，也不允许开始实验。

```text
AUTHORIZATION_RECORD_CLASS=NON_NORMATIVE_P0_TEMPLATE_ONLY
AUTHORIZATION_TEMPLATE_CREATED=true
AUTHORIZATION_GRANT_RECORD_CREATED=false
HUMAN_AUTHORIZATION_DECISION=NOT_RECORDED
P0_EXECUTION_AUTHORIZED=false
```

设计通过、模板完成、技术准备完成、Human grant 生效、首次 session 尝试、实验完成和结果成立是不同状态，
不得相互替代。

# 0. Commander Command Check and Truth Corrections

```text
COMMANDER_COMMAND_CHECK=WARNING_WITH_CORRECTIONS
GATE_NUMBERING_CONFLICT_DETECTED=true
AUTHORIZATION_SCOPE_COLLAPSE_RISK=true
CONSUMPTION_RULE_CONFLICT_DETECTED=true
DUPLICATE_BUILD_RISK=true
MAINLINE_DRIFT_DETECTED=true
```

## 0.1 Gate numbering correction

本研究采用 `G0`–`G8` 九道 gate。最终 execution authorization 是 `G8`，不是 `G7`：

```text
G0=SOURCE_INTEGRITY
G1=PREREGISTRATION_ACCEPTANCE
G2=EXECUTABLE_CASE_INPUTS
G3=FIXTURE_VALIDITY
G4=RUNTIME_OBSERVATION
G5=ANNOTATION_INTEGRITY
G6=EVIDENCE_REPRODUCIBILITY
G7=RANDOMIZATION
G8=ONE_USE_HUMAN_EXECUTION_AUTHORIZATION
```

## 0.2 Authorization-scope correction

G8 不能把 Evidence Root、case inputs、fixture、annotations、runtime 或 randomization 的创建授权合并为一次
“最终授权”。这些资产分别属于 G2–G7 的独立准备、授权、执行和验收链。只有 G0–G7 已全部 `PASS`，G8 才可能
允许创建首个 subject Agent session 并调用已冻结的模型。

## 0.3 Consumption correction

one-use authorization 不是在 P0 完成后才消费。它在**首次 subject Agent session creation command 被尝试时**立即消费；
即使 session 启动失败，也不允许自动 retry、resume 或复用同一 authorization。

## 0.4 Duplicate-build correction

仓库已有通用 Human authorization template。本文件复用其模板/实例分离、Human attestation、exact binding、one-use、
fail-closed 和不可覆盖历史原则，只作为 Goal Integrity P0 的专用投影：

```text
GENERIC_AUTHORIZATION_PROTOCOL_CREATED=false
AUTHORIZATION_SCHEMA_CREATED=false
SPECIALIZED_P0_PROJECTION_ONLY=true
DUPLICATE_BUILD_STATUS=CONTAINED_BY_REUSING_EXISTING_AUTHORIZATION_PRINCIPLES
```

本文中的“field vocabulary”仅用于设计未来记录的字段，不是 JSON Schema、协议或 Capability。

## 0.5 Constitutional mainline correction

Goal Integrity P0 是 secondary research lane，不得替代 SAEE 与 Agent Evidence 受控集成主线；研究报告也不能批准自身执行。

```text
MAINLINE_DRIFT_STATUS=CONTAINED_BY_INACTIVE_AUTHORIZATION_TEMPLATE
PROGRAM_MAINLINE_CHANGED=false
SELF_ASSESSMENT_AUTHORIZES_CHANGE=false
```

# 1. Template, Instance and Grant Separation

| Surface | Meaning | Current state |
|---|---|---|
| 本文件 | 非规范、失活的 P0 authorization template | `CREATED` |
| Future record instance | 用 exact facts 填写、存入外部 Evidence Root 的不可覆盖记录 | `NOT_CREATED` |
| Human decision | Human Authority Owner 的显式 `APPROVE_ONE_USE`、`HOLD` 或 `REJECT` | `NOT_RECORDED` |
| Effective grant | G0–G7 PASS 后，经独立 final preflight 验证并在有效期内签发的 one-use grant | `NOT_GRANTED` |
| Consumed authorization | 首次 subject session creation attempt 已发生 | `false` |

模板内容被人工审阅或接受，不代表 grant。包含 `<REQUIRED:...>`、`UNBOUND`、wildcard、空值、冲突值或未验证 hash 的
instance 永远不能激活。

Future active instance 应使用新的唯一文件和 lineage，不得覆盖本模板，也不得覆盖任何 denied、expired、revoked、consumed
或 failed-attempt 记录。

# 2. Current Fail-Closed Gate Snapshot

| Gate | Current state | Current blocking fact |
|---|---|---|
| `G0` | `PASS_REVALIDATION_REQUIRED_AT_FINAL_PREFLIGHT` | 后续全部 receipt 仍需进入 final preimage |
| `G1` | `OPEN` | Human preregistration acceptance receipt absent |
| `G2` | `OPEN` | frozen executable case artifacts absent |
| `G3` | `OPEN` | fixture absent |
| `G4` | `OPEN` | runtime unbound and uncreated |
| `G5` | `OPEN` | annotators, prelabels and adjudication absent |
| `G6` | `OPEN` | external Evidence Root absent |
| `G7` | `OPEN` | sealed randomization receipt absent |
| `G8` | `OPEN_NOT_GRANTED` | G0–G7 are not all PASS and Human grant is absent |

```text
READINESS_GATES_TOTAL=9
READINESS_GATES_PASS=1
READINESS_GATES_OPEN=8
FINAL_HUMAN_GATE_READY=false
P0_TECHNICALLY_READY=false
P0_EXECUTION_READY=false
P0_EXECUTION_AUTHORIZED=false
```

# 3. Prerequisite Authorization Separation

| Preparation object | Governing gate | Separate Human decision required | May G8 create it? |
|---|---|---|---|
| External Evidence Root | `G6` | yes | no |
| Executable case inputs | `G2` | yes | no |
| Fixture source and arm copies | `G3` | yes | no |
| Annotation/prelabel artifacts | `G5` | yes | no |
| Runtime/CODEX_HOME/config binding | `G4` | yes | no |
| Randomization and sealed mapping | `G7` | yes | no |
| Subject Agent sessions | `G8` | yes, one-use | yes, only after G0–G7 PASS |

Each earlier grant must have its own scope, evidence, consumption and failure lineage. Completion of this template grants none of them.

# 4. Non-Normative Authorization Record Field Vocabulary

Only after an independent final preflight proves G0–G7 `PASS` may a future record instance bind every field below with exact values：

```text
authorization_id=<REQUIRED:UNIQUE_ID>
authorization_record_version=<REQUIRED:POSITIVE_INTEGER>
study_id=<REQUIRED:EXACT_STUDY_ID>
authorization_type=GOAL_INTEGRITY_P0_EXECUTION_ONE_USE
authorization_decision=<REQUIRED:APPROVE_ONE_USE_OR_HOLD_OR_REJECT>
authorization_status=<REQUIRED:ACTIVE_ONE_USE_OR_HELD_OR_REJECTED>

human_authority_owner_id=<REQUIRED:STABLE_HUMAN_ID>
human_authority_owner_role=<REQUIRED:ROLE>
human_authority_owner_attestation=<REQUIRED:EXPLICIT_SENTENCE>
human_authority_owner_confirmed_at=<REQUIRED:ISO_8601_TIMESTAMP_WITH_TIMEZONE>
human_authority_owner_is_ai_agent=false

executor_id=<REQUIRED:STABLE_ID>
independent_observer_id=<REQUIRED:STABLE_ID>
stop_owner_id=<REQUIRED:STABLE_ID>
cleanup_owner_id=<REQUIRED:STABLE_ID>

all_gates_receipt_sha256=<REQUIRED:64_HEX_DIGEST>
final_preimage_sha256=<REQUIRED:64_HEX_DIGEST>
session_order_receipt_sha256=<REQUIRED:64_HEX_DIGEST>

allowed_case_ids=<REQUIRED:EXACT_NONEMPTY_LIST>
allowed_arm_ids=<REQUIRED:EXACT_NONEMPTY_LIST>
allowed_session_count=<REQUIRED:POSITIVE_INTEGER>

agent_family=<REQUIRED:EXACT_VALUE>
executable_version_and_sha256=<REQUIRED:EXACT_VERSION_AND_64_HEX_DIGEST>
model_provider=<REQUIRED:EXACT_PROVIDER>
model_id=<REQUIRED:EXACT_MODEL_ID>

synthetic_context_transmission_accepted=<REQUIRED:true_OR_false>
workspace_write_residual_risk_accepted=<REQUIRED:true_OR_false>
provider_network_exception_accepted=<REQUIRED:true_OR_false>

max_session_wall_time_seconds=<REQUIRED:POSITIVE_INTEGER>
max_total_wall_time_seconds=<REQUIRED:POSITIVE_INTEGER>
max_total_tokens=<REQUIRED:POSITIVE_INTEGER>
max_total_provider_cost=<REQUIRED:NONNEGATIVE_AMOUNT_AND_CURRENCY>

retry_allowed=false
model_fallback_allowed=false
parallel_sessions_allowed=false
external_action_allowed=false
saee_repository_mutation_allowed=false

authorization_not_before=<REQUIRED:ISO_8601_TIMESTAMP_WITH_TIMEZONE>
authorization_expires_at=<REQUIRED:ISO_8601_TIMESTAMP_WITH_TIMEZONE>
authorization_one_use=true
authorization_consumed=false
supersedes_authorization_id=NONE_OR_EXACT_ID
```

This vocabulary does not create an executable Schema. Natural-language scope alone is insufficient；the active record must bind exact
receipts, hashes, identities, paths and ceilings.

# 5. Human Identity and Attestation Boundary

A future `APPROVE_ONE_USE` decision requires a direct Human Authority Owner attestation. An AI Agent may prepare, validate or explain the
record but may not：

- set `human_authority_owner_is_ai_agent=false` on a Human's behalf；
- invent or infer the Human identity、timestamp、acceptance or signature；
- convert review acknowledgement into execution approval；
- activate a record with unresolved fields；
- approve its own runtime, outputs or scope changes.

Recommended future grant attestation：

```text
I authorize only the exact one-use Goal Integrity P0 Agent execution bound by this record and its final preimage. I do not authorize prerequisite asset creation, retries, fallbacks, SAEE repository mutation, external action, automatic publication, or claim expansion.
```

Current values：

```text
HUMAN_AUTHORITY_OWNER_ID=UNBOUND
HUMAN_AUTHORITY_OWNER_ATTESTATION=UNBOUND
HUMAN_AUTHORITY_OWNER_CONFIRMED_AT=UNBOUND
```

# 6. Activation Predicate

A future record becomes `ACTIVE_ONE_USE` only if all conditions are simultaneously true：

```text
G0=PASS
G1=PASS
G2=PASS
G3=PASS
G4=PASS
G5=PASS
G6=PASS
G7=PASS
all_gates_receipt_verified=true
blocking_issues_empty=true
final_preimage_verified=true
all_required_fields_exact=true
wildcards_present=false
unbound_fields_present=false
authorization_not_yet_valid=false
authorization_expired=false
authorization_consumed=false
human_attestation_valid=true
```

If any predicate is false or unknown，G8 remains `OPEN_NOT_GRANTED`。

# 7. Allowed Scope of a Future Effective G8 Grant

If and only if Section 6 passes, a future grant may allow：

1. create exactly the pre-authorized fresh subject Agent sessions in the sealed order；
2. invoke exactly the bound model/provider through the frozen runtime；
3. transmit only the frozen synthetic case materials accepted by the Human owner；
4. write only inside already-created isolated arm workspaces and already-created evidence/runtime capture paths；
5. run only the frozen local tests and sentinels；
6. perform passive observation and append-only evidence capture；
7. execute only the exact approved cases, arms, session count and measurement window；
8. stop at the first bound limit, stop instruction or boundary violation.

G8 does not authorize creation or repair of any prerequisite asset. If a G2–G7 artifact is absent or invalid, execution stops and the
corresponding earlier gate must follow a new evidence-preserving authorization lineage.

# 8. Explicitly Forbidden Actions

Even a future effective G8 grant cannot authorize：

- creating or repairing Evidence Root, case inputs, fixture, annotations, runtime binding or randomization under G8；
- changing H1/H2/H3、H3 comparator、ground truth、labels、metrics、stop conditions or success thresholds after pre-registration；
- adding an experimental arm, case, field or score after execution starts；
- changing prompt、Goal packet、transition packet、drift injection or expected label after outcomes are observed；
- creating or modifying a Capability、Schema、Protocol、MCP、Skill、evaluator、runtime implementation or product registry；
- modifying the SAEE repository or using its dirty worktree as a subject workspace；
- creating branch/worktree or performing `git add`, commit, push, PR, merge, release or deployment；
- using real customer、payment、personal、production or confidential business data；
- external business, GitHub, database, deployment or production actions；
- permission expansion、unbound network access or non-approved Tool/MCP access；
- parallel sessions、automatic retry、resume、model fallback or provider fallback；
- deleting, replacing or rewriting failed/negative attempt evidence；
- automatic publication or claim expansion；
- treating SAEE evaluation, recommendation or research output as Human authorization.

# 9. Decision Vocabulary and State Transitions

| Decision/status | Meaning | Execution effect |
|---|---|---|
| `NOT_READY` | G0–G7 or required bindings incomplete | no grant；no session |
| `APPROVE_ONE_USE` | all predicates pass and Human explicitly grants exact scope | G8 may become `ACTIVE_ONE_USE` |
| `HOLD` | unresolved prerequisite, risk or identity | G8 remains open |
| `REJECT` | Human does not accept P0 scope, cost or risk | no grant；study stops or is redesigned under new lineage |
| `CONSUMED` | first subject session creation command was attempted | no retry or reuse |
| `EXPIRED` | current time is outside bound validity window | no execution |
| `REVOKED` | Human revokes before consumption or a bound fact changes | no execution；new lineage required |

Allowed transition outline：

```text
NOT_READY -> HOLD
NOT_READY -> APPROVE_ONE_USE  [only after activation predicate passes]
APPROVE_ONE_USE -> ACTIVE_ONE_USE
ACTIVE_ONE_USE -> CONSUMED    [first session creation attempt]
ACTIVE_ONE_USE -> EXPIRED
ACTIVE_ONE_USE -> REVOKED
HOLD|REJECT|CONSUMED|EXPIRED|REVOKED -> no automatic reactivation
```

Silence, design approval, document acceptance, `READY`, prior Phase 7 authorization or an Agent recommendation is not
`APPROVE_ONE_USE`。

# 10. One-Use Consumption, Expiry and Reauthorization

## 10.1 Consumption event

```text
authorization_consumed_when=FIRST_SUBJECT_AGENT_SESSION_CREATION_COMMAND_ATTEMPTED
startup_failure_consumes_authorization=true
runtime_failure_after_attempt_consumes_authorization=true
retry_allowed=false
resume_allowed=false
authorization_reuse_allowed=false
```

The executor must write the consumption event before or atomically with the first session attempt. A successful model response is not
required for consumption.

## 10.2 Expiry and revocation

The authorization is invalid before `authorization_not_before` and after `authorization_expires_at`. Human revocation before consumption,
or any mismatch in model、runtime、fixture、annotation、case、randomization、cost、path、identity or receipt, makes the authorization
non-executable.

## 10.3 Reauthorization

Any new attempt requires：

- preservation of the complete prior authorization and failure evidence；
- a new unique `authorization_id`；
- a new final preimage and all-gates receipt if any binding changed；
- independent final preflight；
- a new explicit Human decision.

# 11. Stop and Rollback Conditions

“Rollback” here means stop the study attempt, preserve the observed state, mark the authorization and attempt accurately, and return to the
correct earlier gate. It does not mean delete history, revert external systems or claim that Agent side effects were automatically undone.

## 11.1 Stop before session attempt

Stop without consuming the authorization if：

- G0–G7 no longer match their bound receipts；
- final preimage or all-gates hash fails；
- authorization is absent、not-yet-valid、expired、revoked or already consumed；
- any required value is unresolved, wildcarded or contradictory；
- Human stop instruction is received before the attempt；
- mainline drift or an external-action route appears.

## 11.2 Stop after consumption

Stop immediately and preserve evidence if：

- wrong Agent/model/provider/executable/config/tool surface is observed；
- fixture contamination, expected-label leakage or arm crossover occurs；
- Evidence Root cannot preserve the attempt；
- cost、token、time or session ceiling is reached；
- unauthorized network, Tool/MCP, external action or SAEE repository mutation occurs；
- retry, fallback, parallel session or permission expansion is attempted；
- Human stop instruction is received.

## 11.3 Return gate

| Failure | Required return |
|---|---|
| Evidence preservation failure | `G6` |
| Case/prompt/injection defect | `G2` and new preregistered lineage if semantics change |
| Fixture defect | `G3` |
| Runtime/observation defect | `G4` |
| Ground-truth/annotation defect | `G5`；semantic change requires preregistration amendment |
| Randomization defect | `G7` |
| Scope/cost/risk rejection | `G8=REJECT`；no execution |
| First session startup/runtime failure | authorization `CONSUMED`；new authorization lineage required |

Changing comparator, labels, hypotheses, metrics or study semantics is not a repair inside the current authorization. It closes the current
lineage and requires a versioned preregistration amendment and renewed gate review.

# 12. Evidence Binding and History Preservation

The future active Human record must be stored in the external Evidence Root, outside every subject Agent writable root. It must be hashed and
linked to：

- verified G0–G7 receipts；
- empty blocking-issues record；
- final preimage；
- exact runtime and session order；
- Human identity, decision and attestation；
- activation、consumption、expiry or revocation event；
- stop/failure receipt when applicable.

The current Evidence Root does not exist. Therefore no effective external grant record can exist now.

```text
EVIDENCE_ROOT_CREATED=false
ACTIVE_AUTHORIZATION_RECORD_STORED=false
AUTHORIZATION_RECORD_SHA256=UNBOUND
```

# 13. Non-Claims

This template does not claim：

- Human granted or denied P0 execution；
- G1–G7 are closed；
- technical readiness or execution readiness exists；
- Evidence Root, case inputs, fixture, annotations, runtime or randomization exists；
- any Agent session, model, Tool/MCP or experiment ran；
- Goal Integrity, Drift Detection, Recovery or State Integrity is implemented or validated；
- SAEE can control an Agent or grant authority；
- this field vocabulary is a Schema, Protocol, Capability or reusable production governance standard；
- Goal Integrity research replaced the constitutional integration mainline；
- customer validation, commercial validation, product launch or production readiness exists.

# 14. Current Record State

```text
GOAL_INTEGRITY_FINAL_HUMAN_AUTHORIZATION_RECORD_PREPARATION_STATUS=COMPLETE
AUTHORIZATION_RECORD_CLASS=NON_NORMATIVE_P0_TEMPLATE_ONLY
AUTHORIZATION_TEMPLATE_CREATED=true
AUTHORIZATION_GRANT_RECORD_CREATED=false
HUMAN_AUTHORIZATION_DECISION=NOT_RECORDED
HUMAN_AUTHORITY_OWNER_ID=UNBOUND
FINAL_HUMAN_GATE_READY=false
G8_EXECUTION_AUTHORIZATION_STATUS=OPEN_NOT_GRANTED
P0_TECHNICALLY_READY=false
P0_EXECUTION_READY=false
P0_EXECUTION_AUTHORIZED=false
AUTHORIZATION_ONE_USE_REQUIRED=true
AUTHORIZATION_ONE_USE_BOUND=false
AUTHORIZATION_CONSUMED=false
EVIDENCE_ROOT_CREATED=false
FIXTURE_CREATED=false
ANNOTATION_CREATED=false
RUNTIME_CREATED=false
AGENT_SESSION_CREATED=false
MODEL_INVOKED=false
MCP_INVOKED=false
EXPERIMENT_EXECUTED=false
NEW_CAPABILITY_CREATED=false
SCHEMA_CREATED=false
PROTOCOL_CREATED=false
MCP_CHANGED=false
SKILL_CHANGED=false
CODE_CHANGED=false
MAINLINE_DRIFT_DETECTED=true
MAINLINE_DRIFT_STATUS=CONTAINED_BY_INACTIVE_AUTHORIZATION_TEMPLATE
PROGRAM_MAINLINE_CHANGED=false
NEXT_ACTION=HUMAN_REVIEW_OF_AUTHORIZATION_RECORD_TEMPLATE
```
