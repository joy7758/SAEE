# SAEE Goal Integrity HG-2 Evidence Root Creation Request

## Phase 8.0 — Human Review Request Preparation, Not Authorization

```text
request_id=SAEE-GI-P0-HG2-EVIDENCE-ROOT-CREATION-REQUEST-20260716-V1.0
request_date=2026-07-16
request_type=HUMAN_AUTHORIZATION_REQUEST_PREPARATION_ONLY
study_id=SAEE-GI-P0-20260716-001
program_mainline=saee_agent_evidence_integration
research_lane=goal_integrity_p0_secondary
governing_gate=G6_EVIDENCE_PRESERVATION
human_gate=HG-2
```

Bound sources：

```text
closure_plan_path=reports/SAEE_GOAL_INTEGRITY_PILOT_EXECUTION_CLOSURE_PLAN.md
closure_plan_sha256=36501278ba88d8ddd43571f189fc9f92d10c89bdbf9306351eed121831ca9417
evidence_root_plan_path=reports/SAEE_GOAL_INTEGRITY_EVIDENCE_ROOT_INITIALIZATION_PLAN.md
evidence_root_plan_sha256=701f4641d00208f484f102af50d3aa19cb4ca522d3b1a29d848b3b4928809cc4
final_human_gate_review_path=reports/SAEE_GOAL_INTEGRITY_FINAL_HUMAN_GATE_REVIEW.md
final_human_gate_review_sha256=4bb01cd05c21087b08ae61ac425a62e05ebddaab8b427497d6cb06d827860f87
final_authorization_template_path=reports/SAEE_GOAL_INTEGRITY_FINAL_HUMAN_AUTHORIZATION_RECORD.md
final_authorization_template_sha256=1b6b7505c6b1a134d1315f1dafe1d5ff6e0e6360319f3f6905aba8a45911da9a
```

## Executive Boundary

本文件只准备 HG-2 Evidence Root creation（证据根创建）的 Human authorization request。它定义未来可以授权的
exact path、目录、artifact、hash、provenance、逻辑 write-once 和 access boundary，但本轮不创建目录、文件或任何实验资产。

```text
HG2_REQUEST_CREATED=true
HG2_AUTHORIZATION_DECISION=NOT_RECORDED
HG2_EVIDENCE_ROOT_CREATION_AUTHORIZED=false
EVIDENCE_ROOT_CREATED=false
```

HG-2 只讨论证据容器。它不授权 HG-3 fixture，不授权 runtime、annotation、randomization、Agent session、model invocation
或 experiment execution。

# 0. Commander Command Check and Staged-Truth Correction

```text
COMMANDER_COMMAND_CHECK=PASS_WITH_STAGED_TRUTH_NOTE
GATE_MERGE_DETECTED=false
HG3_AUTHORIZATION_REQUEST_INCLUDED=false
MAINLINE_DRIFT_DETECTED=true
DUPLICATE_BUILD_RISK=true
DUPLICATE_BUILD_STATUS=CONTAINED_BY_BINDING_EXISTING_D6_2_PLAN
```

当前 Human message 明确把 HG-1 与 HG-2 分开，并指示本轮只准备 HG-2 request，范围正确。但仓库内尚无独立 HG-1
acceptance receipt；因此只能记录：

```text
HG1_HUMAN_ACCEPTANCE_DECLARED=true
HG1_ACCEPTANCE_RECEIPT_CREATED=false
HG1_ACCEPTANCE_RECEIPT_VERIFIED=false
G1_PREREGISTRATION_ACCEPTANCE_STATUS=HUMAN_DECLARED_RECEIPT_UNBOUND
```

HG-1 receipt 未绑定不阻止创建本 request 文档，但会阻止未来实际 Evidence Root 创建和 G6 closure。

D6.2 已经是 canonical Evidence Root initialization plan。本 request 不建立第二套 evidence model、Schema、Protocol 或
Capability，只引用其 exact hash 并把可授权范围投影为 Human-readable checklist。

现有 D6.2 receipt field vocabulary 中 `claims` 出现两次，属于非规范字段列表的编辑重复。本 request 将其解释为一个
`claims` 字段；不修改 D6.2，也不允许该重复进入 future canonical receipt：

```text
D6_2_DUPLICATE_CLAIMS_TOKEN_DETECTED=true
D6_2_DUPLICATE_CLAIMS_TOKEN_CLASS=NON_BLOCKING_EDITORIAL_DUPLICATE
FUTURE_RECEIPT_CLAIMS_FIELD_COUNT=1
SCHEMA_SEMANTICS_CHANGED=false
```

Goal Integrity P0 remains a bounded secondary research lane and does not replace the constitutional SAEE / Agent Evidence integration
mainline。

```text
MAINLINE_DRIFT_STATUS=CONTAINED_BY_HG2_REQUEST_ONLY
PROGRAM_MAINLINE_CHANGED=false
```

# 1. Evidence Root Purpose

The future Evidence Root would provide one external, bounded and traceable location for preserving P0 preparation, execution, failure and
review evidence from the first filesystem-changing attempt onward.

Its purpose is to preserve：

- exact authorization and actor lineage；
- source/preregistration bindings；
- failed, invalid, negative and successful attempts without replacement；
- byte-level artifact identity and receipt order；
- separation between experimental inputs, observations and Human annotations；
- enough evidence for independent verification of what was executed.

It is not the experiment itself and does not demonstrate Goal Integrity, State Integrity, Drift Detection or Recovery.

# 2. Proposed Root Boundary

The only candidate path that a future HG-2 approval may authorize is：

```text
SAEE_REPOSITORY=/Users/zhangbin/Documents/SAEE
EXPERIMENT_PARENT=/Users/zhangbin/Documents/SAEE-experiments/goal-integrity-p0
CANDIDATE_EVIDENCE_ROOT=/Users/zhangbin/Documents/SAEE-experiments/goal-integrity-p0/SAEE-GI-P0-20260716-001
```

Future creation must stop if the exact candidate path exists before the authorized creation attempt. It may not clean, merge, overwrite or
adopt a pre-existing path.

Required boundary：

```text
ROOT_EXTERNAL_TO_SAEE_REPOSITORY=true
ROOT_IS_GIT_WORKTREE=false
ROOT_CONTAINS_GIT_METADATA=false
SYMLINKS_ALLOWED=false
HARDLINKS_ALLOWED=false
DEVICE_SOCKET_FIFO_ALLOWED=false
AGENT_DIRECT_WRITE_TO_EVIDENCE_ROOT=false
SYNTHETIC_LOCAL_DATA_ONLY=true
```

The future root must not contain credentials, provider key values, tokens, customer/personal/payment data, production data, unrelated
repository content or unknown external code.

# 3. Proposed Directory Structure

The following structure is authorized-request vocabulary only and is not created in this phase：

```text
SAEE-GI-P0-20260716-001/
  evidence-root-manifest.json
  write-once-policy.md
  ledger/
    receipts/
    heads/
  authorization/
  source-bindings/
  case-inputs/
  fixtures/
  runtime/
  annotations/
  randomization/
  sessions/
  adjudication/
  final-analysis/
```

No additional top-level directory is allowed without a new HG-2 review and authorization lineage.

# 4. Allowed Future Contents and Artifact Categories

| Category | Allowed future contents | Explicit boundary |
|---|---|---|
| `authorization/` | grants, holds, denials, expiry, revocation and consumption records | records authority；does not grant itself |
| `source-bindings/` | D3.1–D6.x hashes, preregistration and gate receipts | references exact source bytes |
| `case-inputs/` | future frozen prompts, Goal/Transition packets, injections, answer keys and prelabels | HG-2 does not authorize their creation |
| `fixtures/` | future fixture manifests, copy verification, sentinel and failed creation evidence | references/captured evidence only under later HG-3 |
| `runtime/` | executable/model/framework/config/tool/sandbox/cost metadata and preflight evidence | no runtime creation or model call under HG-2 |
| `annotations/` | future role bindings, sealed prelabels, rubric, agreement and adjudication references | no annotation creation under HG-2 |
| `randomization/` | future seed, mapping and sealed execution-order receipts | no randomization under HG-2 |
| `sessions/` | future commands, events, traces, stdout/stderr, trees, tests, outputs and cost records | no session under HG-2 |
| `adjudication/` | future disagreement and blind-review records | Human/reviewer evidence only |
| `final-analysis/` | future frozen analysis, limitations, failures and conclusion | no automatic claim promotion |

An artifact has one canonical category. Other categories may reference its SHA-256 but must not create competing fact copies.

# 5. Artifact Naming and Attempt Rules

Future mutable actions use non-reusable monotonic attempt IDs：

```text
attempt-000001
attempt-000002
...
```

Each category attempt uses：

```text
<category>/attempt-NNNNNN/
  raw/
  canonical/
  artifact-manifest.json
  attempt-receipt.json
  boundary-observation.json
```

Allowed terminal states：

```text
ALLOCATED -> WRITING -> SEALED_COMPLETE
ALLOCATED -> WRITING -> INVALID_PRESERVED
ALLOCATED -> FAILED_BEFORE_WRITE
```

No failed or invalid attempt may be renamed, deleted, overwritten or promoted to complete. A correction requires a new attempt ID and, where
scope changes, new Human authorization.

Ledger head files are append-only names rather than a rewritten mutable head：

```text
ledger/heads/head-000001.json
ledger/heads/head-000002.json
```

# 6. Hashing and Canonicalization Requirements

Future evidence must use：

- `SHA-256` for file bytes, canonical manifests and canonical receipts；
- deterministic tree hashes binding normalized relative path, entry type, mode and content hash；
- recursive lexicographic JSON key order；
- stable semantic array order；
- UTF-8, LF line endings and final newline；
- no symlink following；
- three repeated hash calculations with `3/3` identical results before acceptance.

Receipt chain：

```text
first_parent_receipt_sha256=GENESIS
subsequent_parent_receipt_sha256=<EXACT_PREVIOUS_CANONICAL_RECEIPT_SHA256>
hash_algorithm=SHA-256
```

The root manifest remains static. It must not be rewritten to store the current chain head.

# 7. Provenance and Metadata Requirements

Each future attempt receipt must contain exactly one value for each applicable field：

```text
study_id
attempt_id
attempt_type
status
authorization_ref
actor_ref
started_at_utc
ended_at_utc
monotonic_sequence
parent_receipt_sha256
artifact_manifest_sha256
boundary_observation
failure_class
claims
non_claims
```

Each future root manifest must bind：

```text
study_id
root_absolute_path
created_by_ref
creation_authorization_ref
canonicalization_version
hash_algorithm
write_once_class
directory_allowlist
forbidden_entry_types
retention_policy
claims
non_claims
```

Wall-clock timestamps use RFC3339 UTC with optional `Asia/Shanghai` annotation, but are declared metadata rather than trusted time proof.
Ordering relies on monotonic sequence plus receipt chain.

Metadata field vocabulary is design-only. It does not create a Schema or executable Protocol.

# 8. Immutability and Failure-Preservation Requirements

The only permitted claim is：

```text
WRITE_ONCE_CLASS=LOCAL_LOGICAL_WRITE_ONCE_WITH_HASH_CHAIN
HARDWARE_WORM=false
TAMPER_PROOF_STORAGE=false
CRYPTOGRAPHIC_TIMESTAMP_AUTHORITY=false
```

Future implementation must：

- seal completed artifacts read-only to reduce accidental mutation；
- preserve partial bytes and command evidence after failure；
- create a new incident/attempt receipt if a sealed mismatch is found；
- never repair history in place；
- retain denials, expiry, non-use, timeout, invalid and negative results；
- verify the chain after initialization and every later attempt seal.

Suggested minimum local modes from D6.2：

```text
root_mode=0700
writable_attempt_directory_mode=0700
sealed_directory_mode=0550
sealed_file_mode=0440
```

These modes do not protect against the filesystem owner and must not be described as tamper-proof.

# 9. Access Boundary

| Role | Future allowed action | Forbidden action |
|---|---|---|
| Human Authority Owner | approve/hold/reject exact HG-2 scope | direct evidence history mutation |
| Evidence Custodian | create exact root after authorization, append/seal attempts | rewrite sealed history |
| Independent Validator | read and emit validation receipt | create experimental facts or alter history |
| Fixture Author | later authorized workspace creation | direct root write |
| Runtime Binder | later authorized static binding workspace | model invocation under HG-2 |
| P0 Executor | future bounded session execution after G8 | root creation or direct history write |
| Annotator/Reviewer | future assigned-view review | alter ground truth after output |
| Agent under test | read frozen task workspace only | access or write Evidence Root |

Current identities remain unbound：

```text
HUMAN_AUTHORITY_OWNER_ID=UNBOUND
EVIDENCE_CUSTODIAN_ID=UNBOUND
INDEPENDENT_VALIDATOR_ID=UNBOUND
```

HG-2 approval cannot be effective until all three identities and role-overlap disclosures are exact.

# 10. Proposed HG-2 Human Decision Fields

The future Human review must separately bind：

```text
HG2_AUTHORIZATION_ID=<REQUIRED:UNIQUE_ID>
APPROVE_HG2_EVIDENCE_ROOT_CREATION=<REQUIRED:true_OR_false>
HUMAN_AUTHORITY_OWNER_ID=<REQUIRED:STABLE_HUMAN_ID>
EVIDENCE_CUSTODIAN_ID=<REQUIRED:STABLE_ID>
INDEPENDENT_VALIDATOR_ID=<REQUIRED:STABLE_ID>
ROLE_OVERLAP_DISCLOSURE=<REQUIRED:EXACT_TEXT>
CANDIDATE_EVIDENCE_ROOT=/Users/zhangbin/Documents/SAEE-experiments/goal-integrity-p0/SAEE-GI-P0-20260716-001
ACCEPT_LOCAL_LOGICAL_WRITE_ONCE_BOUNDARY=<REQUIRED:true_OR_false>
ACCEPT_SYNTHETIC_LOCAL_DATA_ONLY=<REQUIRED:true_OR_false>
ACCEPT_NO_AUTOMATIC_DELETION=<REQUIRED:true_OR_false>
AUTHORIZATION_NOT_BEFORE=<REQUIRED:ISO_8601_TIMESTAMP_WITH_TIMEZONE>
AUTHORIZATION_EXPIRES_AT=<REQUIRED:ISO_8601_TIMESTAMP_WITH_TIMEZONE>
AUTHORIZATION_ONE_USE=true
```

The Human decision vocabulary is：

```text
APPROVE_HG2_ONE_USE
HOLD_HG2
REJECT_HG2
```

Silence, review acknowledgement, HG-1 acceptance or this request's completion is not `APPROVE_HG2_ONE_USE`。

# 11. Future HG-2 Allowed Scope

An effective future `APPROVE_HG2_ONE_USE` may authorize only：

1. verify the exact candidate root path is absent；
2. create the exact root and frozen directory allowlist；
3. write the root manifest and local logical write-once policy；
4. create bootstrap command/stdout/stderr and boundary evidence；
5. run permission, entry-type, hash determinism and chain verification；
6. preserve a failed or invalid initialization attempt；
7. create the G6 evidence-root binding receipt if every check passes.

It may not authorize fixture, case inputs, annotations, runtime, randomization, Agent session, model invocation, MCP invocation or experiment
execution.

# 12. Stop Conditions for Future Creation

Future creation must stop without continuing to HG-3 if：

- HG-1 acceptance receipt is absent or invalid；
- Human HG-2 decision is absent, incomplete, expired or already consumed；
- candidate path already exists；
- candidate path resolves inside SAEE repository or another Git worktree；
- symlink, hard link, device, socket or FIFO is observed；
- identities or role overlap remain unresolved；
- an unlisted directory or artifact is required；
- permission, manifest, hash `3/3`, receipt-chain or failure-preservation smoke fails；
- the operation would expose secrets or non-synthetic data；
- SAEE repository mutation or mainline displacement appears.

A failed creation attempt must be preserved and cannot be silently deleted and retried. A new attempt requires a new authorization lineage.

# 13. Non-Claims

This request does not claim：

- HG-2 was approved, signed, active, consumed or completed；
- G6 is closed；
- Evidence Root or any directory/artifact was created；
- HG-1 acceptance receipt exists or was verified；
- fixture, case input, runtime, annotation, randomization or session exists；
- any model, MCP, evaluator or experiment ran；
- local logical write-once storage is WORM, tamper-proof or compliance storage；
- Goal Integrity or State Integrity is implemented or validated；
- this request created a Capability, Schema, Protocol, MCP or product feature；
- Goal Integrity research replaced the constitutional integration mainline；
- customer validation, commercial validation, product launch or production readiness exists.

# 14. Current Status

```text
HG2_EVIDENCE_ROOT_CREATION_REQUEST_STATUS=COMPLETE
HG2_REQUEST_CREATED=true
HG2_AUTHORIZATION_DECISION=NOT_RECORDED
HG2_EVIDENCE_ROOT_CREATION_AUTHORIZED=false
HG3_AUTHORIZATION_REQUEST_INCLUDED=false
G1_PREREGISTRATION_ACCEPTANCE_STATUS=HUMAN_DECLARED_RECEIPT_UNBOUND
G6_EVIDENCE_PRESERVATION_STATUS=OPEN
EVIDENCE_ROOT_CREATED=false
FIXTURE_CREATED=false
RUNTIME_CREATED=false
ANNOTATION_CREATED=false
RANDOMIZATION_CREATED=false
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
MAINLINE_DRIFT_STATUS=CONTAINED_BY_HG2_REQUEST_ONLY
PROGRAM_MAINLINE_CHANGED=false
NEXT_ACTION=HUMAN_REVIEW_OF_HG2_EVIDENCE_ROOT_CREATION_REQUEST
```
