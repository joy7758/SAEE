# SAEE H0-R Final Binding Checklist

```text
checklist_id=SAEE_H0_R_FINAL_BINDING_CHECKLIST
phase=Phase_6.1-B1-H0-R-C
checklist_type=PRE_GRANT_DYNAMIC_BINDING_CHECKLIST_ONLY
authorization_id=SAEE-H0-R-20260715-001
current_effective_authority=SAEE_Development_Constitution_v1.1
program_mainline=controlled_SAEE_Agent_Evidence_integration
checklist_date=2026-07-15
```

## Executive Decision

本清单定义 `SAEE-H0-R-20260715-001` 在未来获得 Human H0-R grant 前必须具备的全部动态
bindings。它不执行授权，不创建 manifest、Preimage P、branch、worktree、R1-R4、Candidate B
或 Demo。

Current binding summary：

```text
AUTHORIZATION_RECORD_INSTANCE=CREATED_INACTIVE
SOURCE_ANCHOR=BOUND_AS_ANCESTRY_ONLY
RECOMMENDATION_EXECUTION_BOUNDARY=HUMAN_CONFIRMED
HUMAN_SIGNATURE=UNRESOLVED
MANIFEST_DIGESTS=UNRESOLVED
PREIMAGE_P=UNRESOLVED
ROLE_SESSIONS=UNRESOLVED
FINAL_LOCATIONS=UNRESOLVED
EXPIRY_AND_ONE_USE_WINDOW=UNRESOLVED
```

Therefore：

```text
H0_R_FINAL_BINDING_CHECKLIST_STATUS=COMPLETE
H0_R_FINAL_BINDINGS_COMPLETE=false
H0_R_GRANTED=false
BASELINE_RECONSTRUCTION_EXECUTION_AUTHORIZED=false
```

本清单完成不等于 bindings 完成。任一 required item 缺失、过期、不一致或未经人工确认时，
effective H0-R state 必须保持 false。

## 0. Mainline and Recommendation Boundary

```text
MAINLINE_DRIFT_DETECTED
```

Final binding 的目的只是允许一次 bounded baseline reconstruction，不得演化为新的治理产品或
改变 controlled SAEE–Agent Evidence integration mainline。

```text
MAINLINE_CORRECTION=COMPLETE_ONLY_DYNAMIC_H0_R_BINDINGS_THEN_STOP_FOR_HUMAN_GRANT
PROGRAM_MAINLINE_CHANGED=false
CURRENT_AUTHORITY_CHANGED=false
PRODUCT_IDENTITY_CHANGED=false
```

Human-confirmed frozen boundary：

```text
SAEE_RECOMMENDATION_NOT_AUTHORIZATION=true
SAEE_EXECUTION_CONTROL=false
SAEE_AUTO_APPROVAL_CORE=false
```

SAEE Recommendation、Decision Context、validator PASS、report COMPLETE 和 checklist COMPLETE 均
不能满足 human signature 或自动激活 H0-R。

## 1. Static Record Bindings

These bindings are already recorded but must be reverified at grant time：

```text
authorization_id=SAEE-H0-R-20260715-001
record_instance=reports/SAEE_H0_R_AUTHORIZATION_RECORD_INSTANCE.md
record_instance_sha256=dfc77433c4c0884c2f782e282917bb697601253ef25a9822e82786eb5a140f57
record_instance_status=COMPLETE_INACTIVE
source_anchor_commit=f6ac41f4b068377e7778e8c3d83b99bd8382debc
source_anchor_tree=def1f5fb06b8087a5c0fabd929be253f25faed67
source_anchor_role=ANCESTRY_ANCHOR_ONLY_NOT_BASELINE
authorization_type=BASELINE_RECONSTRUCTION_ONLY
```

Grant-time verification：

```text
[ ] record instance SHA-256 matches
[ ] authorization ID remains unique
[ ] source anchor commit exists
[ ] source anchor tree matches commit
[ ] source anchor remains ancestry only
[ ] record has not already been granted, denied, expired or consumed
```

Current status：

```text
STATIC_RECORD_BINDING_STATUS=RECORDED_REVERIFY_BEFORE_GRANT
```

## 2. Human Signature Requirement

### 2.1 Required fields

The human signature is an explicit, auditable instruction，not a cryptographic-signature-system
requirement。It must bind：

```text
human_authority_owner_identity=<REQUIRED:HUMAN_NAME_OR_STABLE_IDENTIFIER>
human_authority_owner_role=REPOSITORY_AUTHORITY_OWNER
human_authority_owner_confirmation=CONFIRMED
human_authority_owner_attestation=<REQUIRED:EXPLICIT_GRANT_TEXT>
human_authority_owner_signed_at=<REQUIRED:ISO_8601_TIMEZONE_QUALIFIED_TIMESTAMP>
authorization_decision=<REQUIRED:GRANTED_OR_DENIED>
baseline_reconstruction_execution_decision=<REQUIRED:AUTHORIZED_OR_NOT_AUTHORIZED>
human_authority_owner_is_ai_agent=false
```

Required grant attestation must explicitly name：

- `authorization_id=SAEE-H0-R-20260715-001`；
- exact manifest、P、role and location digests/bindings；
- one-use expiry；
- R1-R4 and V-B stop point；
- no Demo、push、external action or authority switch。

### 2.2 Insufficient human actions

The following do not satisfy final signature：

```text
template_review_pass
record_instance_creation_approval
record_instance_review_pass
checklist_review_pass
approval_without_digests_or_expiry
general_continue_instruction
AI_generated_signature_text
```

### 2.3 Current check

```text
[ ] human identity bound
[ ] explicit attestation recorded
[ ] signed timestamp recorded
[ ] grant/deny decision recorded
[ ] execution authorize/not-authorize decision recorded
[ ] attestation references all final bindings
```

```text
HUMAN_SIGNATURE_BINDING_STATUS=INCOMPLETE
H0_R_HUMAN_SIGNATURE_RECORDED=false
```

## 3. Manifest Digest Binding

### 3.1 Path/hunk manifest

Required：

```text
path_hunk_manifest_path=<REQUIRED:ABSOLUTE_OR_REPOSITORY_RELATIVE_DETACHED_PATH>
path_hunk_manifest_sha256=<REQUIRED:64_LOWERCASE_HEX>
path_hunk_manifest_format=CANONICAL_SORTED_UTF8_FINAL_NEWLINE
path_hunk_manifest_human_reviewed=true
```

It must enumerate every R1-R4 `ADD_EXACT` or `MODIFY_EXACT_HUNKS` entry with source、anchor blob、
approved input hash、selected hunk hashes、truth role、validator and rollback rule。

```text
[ ] path exists outside execution worktree or in an immutable pre-execution packet
[ ] serialization is canonical and reproducible
[ ] SHA-256 recomputes exactly
[ ] every path belongs to R1/R2/R3/R4
[ ] every MODIFY entry has selected hunk hashes
[ ] every excluded hunk is explicit
[ ] no directory glob or unlisted path is authorized
```

### 3.2 Forbidden-scope manifest

Required：

```text
forbidden_scope_manifest_path=<REQUIRED:DETACHED_PATH>
forbidden_scope_manifest_sha256=<REQUIRED:64_LOWERCASE_HEX>
forbidden_scope_manifest_human_reviewed=true
```

It must freeze：Capability、all schema semantics except the one exact authority-schema carry-forward、
MCP、Runtime、Evaluation、Product Registry、Protocol、Constitution semantics、authority switch、Demo
paths、push、external action and every unlisted path/hunk。

```text
[ ] capability-package is forbidden
[ ] agent-index capability projection is forbidden
[ ] capability/runtime schemas are forbidden
[ ] authority schema exception is one exact path/hash only
[ ] MCP/runtime/evaluation/product truth is forbidden
[ ] six Demo paths require absence
[ ] push/PR/release/external actions are forbidden
[ ] default rule for unlisted scope is DENY
```

### 3.3 Validator contract and R3 input manifest

Additional dynamic digests required by the record instance：

```text
validator_contract_path=<REQUIRED:DETACHED_PATH>
validator_contract_sha256=<REQUIRED:64_LOWERCASE_HEX>
R3_accepted_input_manifest_path=<REQUIRED:DETACHED_PATH>
R3_accepted_input_manifest_sha256=<REQUIRED:64_LOWERCASE_HEX>
```

The validator contract must define command order、two-run idempotency、before/after Git status digests、
delta proof and failure behavior。R3 manifest must include only human-accepted reports and the signed
H0-R record instance with exact hashes。

### 3.4 Current check

```text
[ ] path_hunk_manifest_sha256 resolved
[ ] forbidden_scope_manifest_sha256 resolved
[ ] validator_contract_sha256 resolved
[ ] R3_accepted_input_manifest_sha256 resolved
[ ] all four digests human-reviewed and mutually consistent
```

```text
MANIFEST_DIGEST_BINDING_STATUS=INCOMPLETE
PATH_HUNK_MANIFEST_CREATED=false
FORBIDDEN_SCOPE_MANIFEST_CREATED=false
VALIDATOR_CONTRACT_CREATED=false
R3_ACCEPTED_INPUT_MANIFEST_CREATED=false
```

## 4. Preimage P Binding

### 4.1 Required identity

```text
preimage_P_path=/Users/zhangbin/Documents/SAEE-baseline-evidence/phase-6.1-b1/SAEE-H0-R-20260715-001/P.json
preimage_P_sha256=<REQUIRED:64_LOWERCASE_HEX>
preimage_P_created_at=<REQUIRED:ISO_8601_TIMEZONE_QUALIFIED_TIMESTAMP>
preimage_P_created_by=<REQUIRED:READ_ONLY_PREPARER_IDENTITY>
preimage_P_storage=DETACHED_READ_ONLY
preimage_P_contains_secrets=false
preimage_P_human_reviewed=true
```

### 4.2 Required coverage

P must freeze：

```text
source_anchor_commit_and_tree
shared_worktree_status_default_and_all_digests
shared_worktree_staged_and_unstaged_patch_digests
capability_manifest_and_agent_index_projection
schema_tree
MCP_registry_wrapper_adapter_and_tool_metadata
runtime_and_evaluation_files_plus_deterministic_behavior_receipts
product_truth
Constitution_and_Project_Memory
validator_files
path_hunk_manifest_digest
forbidden_scope_manifest_digest
validator_contract_digest
R3_input_manifest_digest
role_binding_digest
location_binding_digest
six_Demo_path_absence
```

### 4.3 Immutability and drift rules

```text
[ ] P created before branch/worktree creation
[ ] P digest recomputes exactly
[ ] P references the same authorization ID
[ ] P contains no unresolved dynamic field
[ ] current shared-worktree exclusion snapshot matches P
[ ] any P change requires a new authorization record or new version
```

Current：

```text
PREIMAGE_P_BINDING_STATUS=INCOMPLETE
PREIMAGE_P_CREATED=false
PREIMAGE_P_SHA256=UNRESOLVED
```

## 5. Role Binding

### 5.1 Executor

```text
executor_role=BASELINE_RECONSTRUCTION_EXECUTOR
executor_identity=<REQUIRED:STABLE_AGENT_SESSION_OR_THREAD_ID>
executor_authorized_worktree=<REQUIRED:EXACT_RECONSTRUCTION_WORKTREE>
executor_scope=R1_R2_R3_R4_ONLY
executor_may_validate_own_B=false
executor_may_expand_scope=false
```

### 5.2 Independent Validator

```text
independent_validator_role=BASELINE_INDEPENDENT_VALIDATOR
independent_validator_identity=<REQUIRED:DIFFERENT_STABLE_AGENT_SESSION_OR_THREAD_ID>
independent_validator_worktree=<REQUIRED:EXACT_VALIDATION_WORKTREE>
independent_validator_scope=READ_ONLY_V_B_AND_DETACHED_Q_B
independent_validator_may_fix_B=false
independent_validator_may_grant_H1=false
```

### 5.3 Rollback Owner

```text
rollback_owner_role=HUMAN_ROLLBACK_OWNER
rollback_owner_identity=<REQUIRED:HUMAN_NAME_OR_STABLE_IDENTIFIER>
rollback_owner_confirmation=CONFIRMED
rollback_owner_may_equal_human_authority_owner=true
rollback_owner_may_rewrite_history=false
```

### 5.4 Separation checks

```text
[ ] Executor identity resolved
[ ] Independent Validator identity resolved
[ ] Executor and Validator are different sessions/threads
[ ] Executor and Human Authority Owner are different
[ ] Validator and Human Authority Owner are different
[ ] Rollback Owner explicitly accepts the role
[ ] role_assignment_sha256 computed and bound into P/H0-R
```

Current：

```text
ROLE_BINDING_STATUS=INCOMPLETE
EXECUTOR_IDENTITY=UNRESOLVED
INDEPENDENT_VALIDATOR_IDENTITY=UNRESOLVED
ROLLBACK_OWNER_IDENTITY=UNRESOLVED
ROLE_ASSIGNMENT_SHA256=UNRESOLVED
```

## 6. Location Binding

### 6.1 Candidate locations

```text
reconstruction_branch=codex/phase-6.1-b1-baseline-reconstruction
reconstruction_worktree=/Users/zhangbin/Documents/SAEE-worktrees/phase-6.1-b1-baseline-reconstruction
validation_worktree=/Users/zhangbin/Documents/SAEE-worktrees/phase-6.1-b1-baseline-validation
detached_evidence_root=/Users/zhangbin/Documents/SAEE-baseline-evidence/phase-6.1-b1/SAEE-H0-R-20260715-001
shared_worktree=/Users/zhangbin/Documents/SAEE
shared_worktree_access=READ_ONLY_HASH_VERIFICATION_ONLY
```

### 6.2 Grant-time collision and ownership checks

```text
[ ] reconstruction branch does not exist
[ ] reconstruction worktree path does not exist
[ ] validation worktree path does not exist
[ ] detached evidence root does not exist before approved preparation
[ ] R4 path does not exist
[ ] no existing registered worktree is reused
[ ] reconstruction and validation paths differ
[ ] both Agents have only required filesystem permissions
[ ] shared worktree exclusion snapshot is unchanged
[ ] location_binding_sha256 computed and bound into P/H0-R
```

### 6.3 Human location approval

```text
location_binding_human_approved=<REQUIRED:true_OR_false>
location_binding_approved_at=<REQUIRED:ISO_8601_TIMESTAMP>
location_binding_sha256=<REQUIRED:64_LOWERCASE_HEX>
```

Current：

```text
LOCATION_BINDING_STATUS=INCOMPLETE
CANDIDATE_LOCATIONS_EXIST=false
LOCATION_BINDING_SHA256=UNRESOLVED
```

## 7. Expiry and One-use Authorization

### 7.1 Required temporal fields

```text
authorized_at=<REQUIRED:ISO_8601_TIMEZONE_QUALIFIED_TIMESTAMP>
expires_at=<REQUIRED:ISO_8601_TIMEZONE_QUALIFIED_TIMESTAMP>
authorization_use=ONE_USE
authorization_consumed=false
authorization_revoked=false
```

### 7.2 Temporal rules

```text
[ ] authorized_at is human-signature time
[ ] expires_at is later than authorized_at
[ ] expiry window is explicit and bounded
[ ] authorization is not reused after R4 or invalidation
[ ] any binding drift consumes/invalidates the authorization
[ ] failed V-B requires new authorization for correction
```

Recommended maximum semantics：one execution batch ending when R4 creates Candidate B and V-B emits
Q-B，or earlier on stop/invalidation。H0-R never persists as standing authority。

Current：

```text
EXPIRY_BINDING_STATUS=INCOMPLETE
AUTHORIZED_AT=UNRESOLVED
EXPIRES_AT=UNRESOLVED
AUTHORIZATION_CONSUMED=false
```

## 8. Authority Schema and Static Boundary Recheck

Before grant，recheck the one schema carry-forward exception：

```text
authority_schema_path=schemas/saee-development-constitution.schema.v1.1.json
authority_schema_change_type=ADD_EXACT
authority_schema_approved_input_sha256=dc2d259a0936d0dc0d74b6279c840cfd62e524c9a7e88db56247995ab0b31d86
authority_schema_semantic_change=false
other_schema_path_allowed=false
```

```text
[ ] approved input bytes still match SHA-256
[ ] source anchor still lacks the path
[ ] human signature explicitly approves exact carry-forward
[ ] no other schema path appears in allowlist
[ ] capability/runtime schema trees remain frozen
```

Current reservation is not active permission。

## 9. Final H0-R Grant Gate

### 9.1 Atomic predicates

The future grant gate is atomic：

```text
record_instance_matches
AND authorization_id_unique
AND source_anchor_matches
AND human_signature_complete
AND human_grant_decision_explicit
AND path_hunk_manifest_digest_matches
AND forbidden_scope_manifest_digest_matches
AND validator_contract_digest_matches
AND R3_input_manifest_digest_matches
AND authority_schema_exact_byte_exception_matches
AND preimage_P_digest_matches
AND role_separation_holds
AND locations_final_and_collision_free
AND expiry_valid
AND authorization_not_consumed_or_revoked
AND recommendation_execution_boundary_preserved
AND six_Demo_paths_absent
AND push_external_authority_false
```

No predicate may be inferred from another。In particular：

```text
SAEE_RECOMMENDATION_NOT_AUTHORIZATION=true
SAEE_VALIDATOR_PASS_IS_NOT_HUMAN_SIGNATURE=true
CHECKLIST_COMPLETE_IS_NOT_GRANT=true
RECORD_INSTANCE_COMPLETE_IS_NOT_GRANT=true
```

### 9.2 Fail-closed result

If any required item is missing or false：

```text
H0_R_GRANTED=false
BASELINE_RECONSTRUCTION_EXECUTION_AUTHORIZED=false
BRANCH_CREATION_AUTHORIZED=false
WORKTREE_CREATION_AUTHORIZED=false
R1_R4_COMMIT_AUTHORIZED=false
```

Current evaluation：

```text
FINAL_H0_R_GRANT_GATE_STATUS=FAIL_REQUIRED_DYNAMIC_BINDINGS_MISSING
H0_R_FINAL_BINDINGS_COMPLETE=false
H0_R_GRANTED=false
BASELINE_RECONSTRUCTION_EXECUTION_AUTHORIZED=false
```

### 9.3 Maximum granted scope

Even a future complete grant may authorize only：

```text
R1_AUTHORITY_CLOSURE
R2_GOVERNANCE_CLOSURE
R3_ACCEPTED_INPUT_CLOSURE
R4_CANDIDATE_MANIFEST
CANDIDATE_B_CREATION
V_B_INDEPENDENT_VALIDATION
DETACHED_Q_B_CREATION
```

It must stop before H1/Demo：

```text
H0_R_STOP_POINT=CANDIDATE_B_AND_DETACHED_Q_B
H0_R_AUTHORIZES_DEMO=false
H0_R_AUTHORIZES_PUSH=false
H0_R_AUTHORIZES_EXTERNAL_ACTION=false
H1_REQUIRED_BEFORE_DEMO=true
```

## 10. Rollback and Invalidation Checklist

```text
[ ] rollback owner bound
[ ] rollback anchor commit/tree verified
[ ] stop triggers frozen in denylist
[ ] failed worktree/branch quarantine procedure defined
[ ] shared worktree remains untouched
[ ] failed Candidate B retained as forensic evidence only
[ ] no amend/rebase/reset history
[ ] new authorization required after failure or drift
```

Automatic invalidation triggers：manifest/P/hash drift、unexpected path/hunk、validator mutation、role
or location mismatch、Demo path appearance、expiry、consumption、scope expansion or any frozen truth
change。

```text
ROLLBACK_BINDING_STATUS=INCOMPLETE_PENDING_OWNER_AND_DIGESTS
ROLLBACK_EXECUTED=false
```

## 11. Final Human Review Form

Human review of this checklist should record only whether the checklist is sufficient，not grant
execution：

```text
FINAL_BINDING_CHECKLIST_HUMAN_REVIEW=<PASS|REVISION_REQUIRED>
HUMAN_SIGNATURE_FIELDS_SUFFICIENT=<true|false>
MANIFEST_BINDING_FIELDS_SUFFICIENT=<true|false>
PREIMAGE_BINDING_FIELDS_SUFFICIENT=<true|false>
ROLE_BINDING_FIELDS_SUFFICIENT=<true|false>
LOCATION_BINDING_FIELDS_SUFFICIENT=<true|false>
EXPIRY_FIELDS_SUFFICIENT=<true|false>
FINAL_GRANT_GATE_SUFFICIENT=<true|false>
```

Even all `true` values leave effective grant false until the dynamic values are actually created、
verified and signed in the authorization record instance。

## 12. Checklist Pre-image and Input Integrity

Target checklist creation pre-image：

```text
branch=feat/canonical-capability-inventory-routing-v1
head=f6ac41f4b068377e7778e8c3d83b99bd8382debc
head_tree=def1f5fb06b8087a5c0fabd929be253f25faed67
status_default_entry_count=117
status_all_untracked_entry_count=134
status_default_sha256=1a970167a3f44cd63aa55fc4a1a97c03d780625b6d3244d1e3746e20b5176687
status_all_untracked_sha256=6f83c52d57135f5f61c3f4cf94abc7091a0a9f69d5ba30d99b39d8b2e44b35b1
staged_patch_sha256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
unstaged_patch_sha256=d44ecf7871a1816fc9c1f9c203bb9e0a664638e54c5666ad8090643c8ef3ff1a
registered_worktree_count=4
stash_count=0
target_checklist_preexisting=false
```

Inputs：

```text
reports/SAEE_H0_R_AUTHORIZATION_RECORD_INSTANCE.md=dfc77433c4c0884c2f782e282917bb697601253ef25a9822e82786eb5a140f57
reports/SAEE_BASELINE_RECONSTRUCTION_H0_BLOCKER_RESOLUTION_PLAN.md=34a816a7cfff70c632fe4f4cbe3591e54fc5f89804bbbaf2e94966cb413f2b0a
```

## 13. Final Status

```text
H0_R_FINAL_BINDING_CHECKLIST_STATUS=COMPLETE
H0_R_FINAL_BINDINGS_COMPLETE=false
H0_R_HUMAN_SIGNATURE_RECORDED=false
PATH_HUNK_MANIFEST_CREATED=false
FORBIDDEN_SCOPE_MANIFEST_CREATED=false
VALIDATOR_CONTRACT_CREATED=false
R3_ACCEPTED_INPUT_MANIFEST_CREATED=false
PREIMAGE_P_CREATED=false
ROLE_BINDINGS_COMPLETE=false
LOCATION_BINDINGS_COMPLETE=false
EXPIRY_BINDING_COMPLETE=false
H0_R_GRANTED=false
BASELINE_RECONSTRUCTION_EXECUTION_AUTHORIZED=false
SAEE_RECOMMENDATION_NOT_AUTHORIZATION=true
SAEE_EXECUTION_CONTROL=false
SAEE_AUTO_APPROVAL_CORE=false
BASELINE_CREATED=false
WORKTREE_CREATED=false
BRANCH_CREATED=false
COMMITS_CREATED=false
DEMO_IMPLEMENTED=false
NEW_CAPABILITY_CREATED=false
SCHEMA_CONTENT_MODIFIED=false
MCP_CHANGED=false
RUNTIME_CHANGED=false
EVALUATION_CHANGED=false
CODE_CHANGED=false
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_H0_R_FINAL_BINDING_CHECKLIST
```

## 14. Current-Phase Validation Record

This section validates only checklist creation safety，not dynamic binding completeness。

```text
PROJECT_MEMORY_CHECK=PASS
GOVERNANCE_REGISTRY_CHECK=PASS
DEVELOPMENT_CONSTITUTION_SMOKE=PASS
CANONICAL_CAPABILITY_INVENTORY_SMOKE=PASS_9_OF_9
CAPABILITY_PROGRESS_LEDGER_SMOKE=PASS_9_OF_9
QIANFAN_READINESS_MCP_SMOKE=PASS_TOOLS_2_DEMOS_3
QODER_ADAPTER_SMOKE=PASS_TOOLS_2
GIT_DIFF_CHECK=PASS
REPORT_DIFF_CHECK=PASS_NO_WHITESPACE_ERRORS
POST_CHECKLIST_STATUS_DEFAULT_ENTRY_COUNT=118
POST_CHECKLIST_STATUS_ALL_UNTRACKED_ENTRY_COUNT=135
EXCLUDING_TARGET_STATUS_DEFAULT_ENTRY_COUNT=117
EXCLUDING_TARGET_STATUS_ALL_UNTRACKED_ENTRY_COUNT=134
EXCLUDING_TARGET_STATUS_DEFAULT_SHA256=1a970167a3f44cd63aa55fc4a1a97c03d780625b6d3244d1e3746e20b5176687
EXCLUDING_TARGET_STATUS_ALL_UNTRACKED_SHA256=6f83c52d57135f5f61c3f4cf94abc7091a0a9f69d5ba30d99b39d8b2e44b35b1
POST_CHECKLIST_STAGED_PATCH_SHA256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
POST_CHECKLIST_UNSTAGED_PATCH_SHA256=d44ecf7871a1816fc9c1f9c203bb9e0a664638e54c5666ad8090643c8ef3ff1a
HEAD_UNCHANGED=true
REGISTERED_WORKTREE_COUNT_UNCHANGED=4
STASH_COUNT_UNCHANGED=0
CANDIDATE_BRANCH_EXISTS=false
RECONSTRUCTION_WORKTREE_EXISTS=false
VALIDATION_WORKTREE_EXISTS=false
DETACHED_EVIDENCE_ROOT_EXISTS=false
PREIMAGE_P_EXISTS=false
SIX_DEMO_PATHS_ABSENT=true
ONLY_TARGET_CHECKLIST_ADDED=true
```
