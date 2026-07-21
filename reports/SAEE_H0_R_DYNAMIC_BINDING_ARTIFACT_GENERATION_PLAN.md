# SAEE H0-R Dynamic Binding Artifact Generation Plan

```text
report_id=SAEE_H0_R_DYNAMIC_BINDING_ARTIFACT_GENERATION_PLAN
phase=Phase_6.1-B1-H0-R-F1
report_type=DYNAMIC_BINDING_ARTIFACT_GENERATION_PLAN_ONLY
authorization_id=SAEE-H0-R-20260715-001
current_effective_authority=SAEE_Development_Constitution_v1.1
program_mainline=controlled_SAEE_Agent_Evidence_integration
report_date=2026-07-16
```

## Executive Decision

人工决定已经允许 H0-R 流程进入最终动态绑定规划阶段：

```text
H0_R_FINAL_BINDING_DECISION=APPROVED
H0-R-001=APPROVED
H0-R-002=APPROVED
H0-R-003=APPROVED
H0-R-004=APPROVED
H0-R-005=APPROVED
APPROVAL_SCOPE=ENTER_DYNAMIC_BINDING_ARTIFACT_GENERATION_PLANNING_ONLY
APPROVAL_IS_H0_R_GRANT=false
```

本报告把已批准的 DB-001～DB-006 设计转换为一次可执行、可停止、可重算但不可静默
覆盖的材料生成计划。它不生成任何动态材料，也不授予 baseline reconstruction 执行权。

冻结的生成顺序为：

```text
G0  Read-only preflight + attempt lock
 ↓
G1  DB-001 Path/Hunk Manifest
 ↓
G2  DB-002 Forbidden-Scope Manifest
 ↓
G3  Validator Contract + R3 Accepted-Input Manifest
 ↓
G4  DB-004 Role Binding
 ↓
G5  DB-005 Location Binding + collision proof
 ↓
G6  DB-003 Preimage P
 ↓
G7  DB-006 Human Expiry/One-use + detached signature
 ↓
G8  Atomic H0-R Grant Evaluation
 ↓
G9  only after atomic PASS: R1-R4 execution may be separately entered
```

当前状态：

```text
H0_R_DYNAMIC_ARTIFACT_GENERATION_PLAN_STATUS=COMPLETE
DYNAMIC_BINDING_ARTIFACT_GENERATION_STARTED=false
DYNAMIC_BINDING_ARTIFACTS_COMPLETE=false
H0_R_GRANTED=false
BASELINE_RECONSTRUCTION_EXECUTION_AUTHORIZED=false
```

## 0. Mainline、Authority 与本阶段边界

```text
MAINLINE_DRIFT_DETECTED
```

H0-R 是支持一次 bounded baseline reconstruction 的治理副线，不是 SAEE 的产品主线，也
不是新的 authorization service。当前宪法主线仍是受控整合 SAEE 与 Agent Evidence Project。

```text
MAINLINE_CORRECTION=STOP_DESIGN_EXPANSION_AFTER_F1_AND_MOVE_TO_EXACT_ARTIFACT_GENERATION_OR_DENIAL
PROGRAM_MAINLINE_CHANGED=false
CURRENT_AUTHORITY_CHANGED=false
PRODUCT_IDENTITY_CHANGED=false
H0_R_DESIGN_EXTENSION_AFTER_F1_RECOMMENDED=false
```

持续冻结：

```text
SAEE_RECOMMENDATION_NOT_AUTHORIZATION=true
SAEE_EXECUTION_CONTROL=false
SAEE_AUTO_APPROVAL_CORE=false
P_IS_EVIDENCE_NOT_PERMISSION=true
VALIDATION_PASS_IS_NOT_AUTHORIZATION=true
HUMAN_GRANT_BEFORE_RECONSTRUCTION_MUTATION=true
```

这里的 `reconstruction mutation` 指 repository、Git ref、candidate worktree、R1-R4 或 Demo
变化。未来经人工明确允许的 detached evidence artifact generation 只可写入绑定的 evidence
root；它仍不构成 H0-R grant。

## 1. Generation Attempt Model

### 1.1 单次 attempt

未来材料生成必须使用一个不可复用的 attempt identity：

```text
authorization_id=SAEE-H0-R-20260715-001
attempt_id=<HUMAN_REVIEWED_UNIQUE_ATTEMPT_ID>
attempt_state=PREPARED|GENERATING|FROZEN|INVALID
artifact_replacement_policy=NEW_ATTEMPT_REQUIRED
partial_grant_allowed=false
```

同一 attempt 内禁止覆盖已经 freeze 的 artifact。任何 digest、role、location 或 preimage
变化都必须：保留旧 attempt、标记 `INVALID`、创建新 attempt，并重新经过依赖它的后续步骤。

### 1.2 Detached evidence root

候选根目录保持：

```text
detached_evidence_root=/Users/zhangbin/Documents/SAEE-baseline-evidence/phase-6.1-b1/SAEE-H0-R-20260715-001
```

实际生成前必须由人工单独允许创建该 root。创建时使用 owner-only 权限、拒绝 symlink、
拒绝已有非空目录，并写入一个 attempt 子目录。不得在 shared worktree 或未来 candidate
worktree 内存放 DB artifacts。

推荐布局：

```text
<detached_evidence_root>/<attempt_id>/
  path-hunk-manifest.json
  forbidden-scope-manifest.json
  validator-contract.json
  r3-input-manifest.json
  role-binding.json
  location-binding.json
  P.json
  human-grant-attestation.json        # only after human signature
  grant-evaluation-receipt.json       # only after atomic evaluation
```

本报告不创建或预留上述目录。

### 1.3 Canonical artifact rules

所有 JSON artifact 必须：

```text
encoding=UTF-8
key_order=LEXICOGRAPHIC_OR_FROZEN_CONTRACT_ORDER
array_order=EXPLICITLY_DEFINED_PER_ARTIFACT
newline=LF
final_newline=ONE
hash=SHA-256_LOWERCASE_HEX_OVER_EXACT_BYTES
write_mode=TEMP_FILE_FSYNC_ATOMIC_RENAME
file_mode=OWNER_READ_WRITE_ONLY_UNTIL_FREEZE
secrets_allowed=false
unknown_fields_allowed=false
unresolved_placeholders_allowed=false
```

同一输入必须独立序列化三次并得到相同 bytes/digest。`mtime`、shell PID、临时路径和
非稳定环境变量不得进入规范内容。

## 2. End-to-End Generation Gates

| Gate | Input | Output | May continue when | Hard stop |
|-|-|-|-|-|
| G0 | approved F1 plan + live read-only state | transient preflight record | all protected facts unchanged | any collision/drift |
| G1 | anchor + exact accepted scope | DB-001 | deterministic + human scope review | unlisted/ambiguous hunk |
| G2 | DB-001 + frozen deny rules | DB-002 | allow/deny closure proven | gap/overlap |
| G3 | DB-001/002 + accepted inputs | validator/R3 manifests | contracts non-circular | self-reference/unaccepted input |
| G4 | actual identities | role binding | separation proven | generic/missing/same identity |
| G5 | live refs/filesystem | location binding | required absence/ownership proven | collision/symlink/reuse |
| G6 | all frozen prior artifacts + live state | P | exact recomputation PASS | preimage drift/unresolved value |
| G7 | P + human decision | expiry/signature attestation | explicit valid human grant | no signature/denial/expiry error |
| G8 | all digests + live recheck | grant receipt | atomic predicate PASS | any false predicate |

No gate output automatically invokes the next gate。每次 continuation 都必须明确记录输入 digest、
producer identity、validator identity、time 与 next-step decision。

## 3. G0 — Read-only Preflight and Attempt Lock

### 3.1 Required checks

实际生成动作开始前，重新读取：

```text
source_anchor_commit=f6ac41f4b068377e7778e8c3d83b99bd8382debc
source_anchor_tree=def1f5fb06b8087a5c0fabd929be253f25faed67
authorization_record_instance=reports/SAEE_H0_R_AUTHORIZATION_RECORD_INSTANCE.md
final_binding_execution_plan=reports/SAEE_H0_R_FINAL_BINDING_EXECUTION_PLAN.md
dynamic_binding_preparation=reports/SAEE_H0_R_DYNAMIC_BINDING_PREPARATION.md
this_F1_plan=reports/SAEE_H0_R_DYNAMIC_BINDING_ARTIFACT_GENERATION_PLAN.md
```

核对：

- record instance 和三个 approved plan 的 exact SHA-256；
- HEAD/tree/branch、default/all status、staged/unstaged patch；
- refs、worktree、stash inventory；
- capability、schema、MCP、runtime、evaluation、product、authority 与 Project Memory protected truth；
- reconstruction branch、两个 worktree、R4 path、六个 Demo path 的 absence；
- evidence root 是否满足“absent，或属于本 authorization 的空且未使用 root”规则。

### 3.2 Attempt lock

只在后续人工批准 artifact generation 后，才可创建 evidence root/attempt directory。创建采用
exclusive semantics；如果目录已存在且无法证明是同一 authorization 的空 preparation root，
立即停止，不得清空、复用或更改权限来规避 collision。

```text
G0_OUTPUT=TRANSIENT_PREFLIGHT_OBSERVATION_PLUS_FUTURE_EXCLUSIVE_ATTEMPT_DIRECTORY
G0_IS_AUTHORIZATION=false
G0_CREATES_GIT_STATE=false
```

## 4. G1 / DB-001 — Path/Hunk Manifest Generation

### 4.1 Inputs

DB-001 从权威对象和人工接受的 scope 生成，不从报告叙述推断 implementation truth：

```text
Git object database at source anchor
approved A3 R1/R2/R3 exact paths and hunks
human-accepted report inventory after F1 review
R4 frozen generator contract mode
active v1.1 authority boundaries
```

F1 human review must first freeze最终 R3 accepted report list。未被明确接受的报告不得因为
存在于 worktree 而自动进入 R3。

### 4.2 Exact entry contract

每个未来 R1-R4 repository change 记录：

```json
{
  "commit_group": "R1|R2|R3|R4",
  "path": "exact/repository/path",
  "change_type": "ADD_EXACT|MODIFY_EXACT_HUNKS|GENERATE_EXACT_FROM_FROZEN_CONTRACT",
  "anchor_blob_sha256": "ABSENT_OR_64_HEX",
  "approved_input_sha256": "64_HEX_OR_NOT_APPLICABLE",
  "selected_hunk_sha256": [],
  "excluded_hunk_ids": [],
  "truth_role": "AUTHORITY|GOVERNANCE|ACCEPTED_INPUT|CANDIDATE_MANIFEST",
  "validator_contract_id": "exact-id",
  "rollback_rule": "STOP_ON_MISMATCH"
}
```

Entries 按 `commit_group,path` 排序；每个 path 只能出现一次。`MODIFY_EXACT_HUNKS` 必须同时
绑定 anchor blob、selected hunks 与 explicitly excluded hunks，不能退化为 file-level 许可。

R4 固定：

```text
path=reports/SAEE_DEMO_BASELINE_CANDIDATE_INPUT_MANIFEST.json
change_type=GENERATE_EXACT_FROM_FROZEN_CONTRACT
generator_contract_id=SAEE_DEMO_BASELINE_CANDIDATE_INPUT_MANIFEST_V1
preknown_final_file_sha256_required=false
final_sha256_recorded_in=DETACHED_Q_B
```

### 4.3 Validation and freeze

```text
exact_R1_R4_path_coverage=true
duplicate_path_count=0
unlisted_hunk_count=0
ADD_EXACT_byte_hashes_match=true
MODIFY_EXACT_HUNKS_apply_to_anchor=true
R4_contract_mode_matches_approved_E_decision=true
deterministic_runs=3/3
independent_scope_review=PASS
```

输出及 digest：

```text
DB_001_PATH=<attempt_root>/path-hunk-manifest.json
path_hunk_manifest_sha256=<CALCULATED_FROM_FINAL_BYTES>
DB_001_STATUS=FROZEN_NOT_AUTHORIZED
```

任何 mismatch 都终止当前 attempt；禁止静默重新哈希后继续。

## 5. G2 / DB-002 — Forbidden-Scope Manifest Generation

### 5.1 Derivation

DB-002 必须是 DB-001 allowlist 的 default-deny complement，并绑定 DB-001 digest。它至少保护：

```text
capability-package/**
agent-index capability facts except an explicitly approved authority-only hunk
schemas/** except the one exact-byte v1.1 authority schema carry-forward
.mcp.json and all MCP tool IDs/schemas/routes/wrappers
saee_backend/** and runtime behavior
evaluation behavior and reason codes
governance registries and product truth outside exact R2 hunks
Constitution semantic content and authority switch
all unlisted paths/hunks
all Demo implementation paths
push/PR/release/external action
```

唯一 schema exception 只能是：

```text
path=schemas/saee-development-constitution.schema.v1.1.json
change_type=ADD_EXACT
sha256=dc2d259a0936d0dc0d74b6279c840cfd62e524c9a7e88db56247995ab0b31d86
semantic_change=false
```

### 5.2 Closure proof

```text
default_policy=DENY
bound_path_hunk_manifest_sha256=<DB_001_DIGEST>
allow_deny_unexplained_overlap_count=0
protected_surface_gap_count=0
six_Demo_paths=REQUIRED_ABSENCE
capability_truth_source=capability-package/manifest.json#canonical_inventory
external_action_allowed=false
```

独立 validator 必须从完整 repository path universe 与 protected logical surface 两个维度证明
closure；仅对比两个文本列表不够。

### 5.3 Output

```text
DB_002_PATH=<attempt_root>/forbidden-scope-manifest.json
forbidden_scope_manifest_sha256=<CALCULATED_FROM_FINAL_BYTES>
DB_002_STATUS=FROZEN_NOT_AUTHORIZED
```

## 6. G3a — Validator Contract Generation

Validator contract 只定义验证行为，不实现或修改 runtime。它必须冻结：

1. exact command、working directory、environment assumptions 与 expected exit code；
2. before/after HEAD/tree/status/staged/unstaged/worktree/stash digest checks；
3. DB-001/002 closure validator；
4. authority schema exact-byte validator；
5. Project Memory、Governance、Constitution、canonical inventory、ledger 与 MCP smoke；
6. R4 generator contract 与 Q-B output fields；
7. two-run idempotency；
8. failure codes、fail-closed behavior、no in-place repair；
9. atomic grant evaluator 的 read-only predicate；
10. validator不得创建 branch/worktree、修改 repository 或自授予权限。

至少冻结这些现有命令：

```text
python3 scripts/saee_project_memory_check.py
python3 scripts/saee_governance_registry_check.py
python3 scripts/saee_development_constitution_smoke.py
python3 scripts/saee_canonical_capability_inventory_smoke.py
python3 scripts/saee_capability_progress_ledger_smoke.py
python3 scripts/saee_qianfan_readiness_mcp_smoke.py
python3 scripts/saee_qoder_adapter_smoke.py
python3 scripts/saee_public_capability_surface_smoke.py
git diff --check
```

生成 contract 时必须记录每个 referenced validator file 的 byte digest，避免签署后 validator
本身漂移。

```text
VALIDATOR_CONTRACT_PATH=<attempt_root>/validator-contract.json
validator_contract_sha256=<CALCULATED_FROM_FINAL_BYTES>
VALIDATOR_CONTRACT_STATUS=FROZEN_NOT_AUTHORIZED
```

## 7. G3b — R3 Accepted-Input Manifest Generation

### 7.1 Inclusion rule

R3 manifest 枚举未来 R3 commit 可以 carry-forward 的 human-accepted reports/records 及 exact
hash。每个 entry 必须包含：path、sha256、acceptance decision source、truth role、target commit
group、non-authority disclaimer。

```text
reports_are_capability_truth=false
reports_are_runtime_truth=false
reports_are_historical_and_governance_provenance=true
unreviewed_reports_auto_included=false
```

至少必须考虑但仍需 human review 后才能列入：

```text
reports/SAEE_H0_R_AUTHORIZATION_RECORD_INSTANCE.md
reports/SAEE_H0_R_FINAL_BINDING_CHECKLIST.md
reports/SAEE_H0_R_DYNAMIC_BINDING_PREPARATION.md
reports/SAEE_H0_R_FINAL_BINDING_EXECUTION_PLAN.md
reports/SAEE_H0_R_DYNAMIC_BINDING_ARTIFACT_GENERATION_PLAN.md
```

### 7.2 Non-circular exclusion

不得把未来 detached artifacts 当作 repository R3 inputs：

```text
human-grant-attestation.json=EXCLUDED_FROM_R3_REPOSITORY_INPUT
grant-evaluation-receipt.json=EXCLUDED_FROM_R3_REPOSITORY_INPUT
future_Q-B.json=EXCLUDED_FROM_R3_REPOSITORY_INPUT
P.json=DETACHED_EVIDENCE_NOT_R3_REPOSITORY_INPUT
```

R4 在生成时只按 digest 引用这些 detached evidence。

```text
R3_INPUT_MANIFEST_PATH=<attempt_root>/r3-input-manifest.json
R3_accepted_input_manifest_sha256=<CALCULATED_FROM_FINAL_BYTES>
R3_INPUT_MANIFEST_STATUS=FROZEN_NOT_AUTHORIZED
```

## 8. G4 / DB-004 — Role Binding Generation

### 8.1 Identity acquisition

Role binding 必须从真实 orchestrator/session/thread metadata 与人工声明取得，禁止填模型名、
`Codex`、`Agent A/B`、shell PID 或推测身份：

```text
executor_identity=<ACTUAL_STABLE_AGENT_SESSION_OR_THREAD_ID>
independent_validator_identity=<DIFFERENT_ACTUAL_STABLE_AGENT_SESSION_OR_THREAD_ID>
rollback_owner_identity=<EXPLICIT_HUMAN_IDENTITY>
human_authority_owner_identity=<EXPLICIT_HUMAN_IDENTITY>
identity_source=<ORCHESTRATOR_METADATA_OR_HUMAN_ATTESTATION>
```

若当前接口无法暴露稳定 session/thread identity，则必须停止并由人工提供可审计 identity；不得
用当前聊天标题或模型标签替代。

### 8.2 Separation and scopes

```text
Executor != Independent_Validator
Executor != Human_Authority_Owner
Independent_Validator != Human_Authority_Owner
Rollback_Owner may_equal Human_Authority_Owner
executor_scope=R1_R4_ONLY
validator_scope=READ_ONLY_V_B_AND_Q_B
rollback_scope=STOP_QUARANTINE_PRESERVE_EVIDENCE
```

Role binding 还必须记录每个角色的 stop point、可访问 location、禁止动作、绑定时间与有效
attempt。任何 role replacement 会使 DB-004 及其后的 DB-005/P/signature 失效。

```text
DB_004_PATH=<attempt_root>/role-binding.json
role_assignment_sha256=<CALCULATED_FROM_FINAL_BYTES>
DB_004_STATUS=FROZEN_IDENTITIES_BOUND_NOT_AUTHORIZED
```

## 9. G5 / DB-005 — Location Binding Generation

### 9.1 Candidate bindings

```text
reconstruction_branch=codex/phase-6.1-b1-baseline-reconstruction
reconstruction_worktree=/Users/zhangbin/Documents/SAEE-worktrees/phase-6.1-b1-baseline-reconstruction
validation_worktree=/Users/zhangbin/Documents/SAEE-worktrees/phase-6.1-b1-baseline-validation
detached_evidence_root=/Users/zhangbin/Documents/SAEE-baseline-evidence/phase-6.1-b1/SAEE-H0-R-20260715-001
shared_worktree=/Users/zhangbin/Documents/SAEE
shared_worktree_access=READ_ONLY_HASH_VERIFICATION_ONLY
```

### 9.2 Collision proof

Location generator 只读运行：

- `git show-ref` 验证 reconstruction branch 不存在；
- `git worktree list --porcelain` 验证两个 candidate worktree 未注册；
- `lstat` 验证两个 candidate path 不存在且父目录 ownership 可接受；
- 验证 reconstruction/validation/shared 三个位置互不相同、不嵌套；
- 验证没有 symlink、mount alias 或 case-fold collision；
- 验证 evidence root/attempt 仅含 G1～G4 的 exact artifacts，没有 Git ref/worktree/P/signature；
- 验证 R4 path 与六个 Demo path 仍不存在。

DB-005 必须区分：

```text
artifact_root_expected_exists_at_G5=true
artifact_root_is_execution_worktree=false
reconstruction_branch_expected_exists=false
reconstruction_worktree_expected_exists=false
validation_worktree_expected_exists=false
```

Evidence root 的存在来自经人工批准的 detached artifact generation，不得被误报为
`WORKTREE_CREATED=true` 或 reconstruction execution。

```text
DB_005_PATH=<attempt_root>/location-binding.json
location_binding_sha256=<CALCULATED_FROM_FINAL_BYTES>
DB_005_STATUS=FROZEN_COLLISION_FREE_NOT_AUTHORIZED
```

## 10. G6 / DB-003 — Preimage P Generation

### 10.1 Timing

P 是 human signature 前最后生成的 evidence artifact。只有 DB-001、DB-002、validator
contract、R3 manifest、DB-004、DB-005 全部 frozen 后才能生成：

```text
P_AFTER_ALL_HASHED_BINDINGS=true
P_BEFORE_HUMAN_SIGNATURE=true
P_BEFORE_BRANCH_OR_WORKTREE=true
P_BEFORE_R1_R4=true
```

### 10.2 Required preimage facts

P 必须记录并绑定：

- authorization/attempt ID、producer identity、timestamp；
- source anchor commit/tree；
- current HEAD/tree/branch；
- status default/all entries及 digest；
- staged/unstaged patch digest；
- refs、worktree、stash inventory；
- `capability-package/manifest.json` 与 ledger projection digest；
- schema、MCP、runtime、evaluation、product protected-tree digests；
- v1.1 authority family、Governance、Project Memory、validator file digests；
- DB-001/002、validator/R3、DB-004/005 exact digests；
- authority schema exact carry-forward bytes；
- reconstruction branch/worktree、R4、six Demo paths absence；
- Recommendation-Execution separation constants。

### 10.3 P self-reference exclusion

P 不能 hash 包含自身的 whole evidence-root tree。它只能 hash G1～G5 的 explicit allowlisted
artifact inventory，并声明 future exclusions：

```text
P_HASHES_WHOLE_EVIDENCE_ROOT=false
P_HASHED_ARTIFACT_SET=DB_001;DB_002;VALIDATOR_CONTRACT;R3_MANIFEST;DB_004;DB_005
P_EXCLUDES_SELF=true
P_EXCLUDES_FUTURE_HUMAN_ATTESTATION=true
P_EXCLUDES_FUTURE_GRANT_RECEIPT=true
P_EXCLUDES_FUTURE_Q_B=true
```

生成流程：先在同一 filesystem 创建 canonical temp bytes，三次重算一致后 atomic rename 为
`P.json`；随后计算 P exact-byte digest。任何在 P 后变化的 hashed input 都使 P 失效。

### 10.4 Output

```text
DB_003_PATH=<attempt_root>/P.json
preimage_P_sha256=<CALCULATED_FROM_FINAL_BYTES>
P_IS_AUTHORITY=false
P_CAN_GRANT_H0_R=false
DB_003_STATUS=FROZEN_AWAITING_HUMAN_SIGNATURE
```

## 11. G7 / DB-006 — Expiry、One-use and Human Signature

### 11.1 Human-only binding

Agent 可以呈现字段和验证格式，但不得选择授权窗口、冒充签署人或把 earlier process
approval 复制为 grant。Human Authority Owner 在看到 P digest 后提供：

```text
human_authority_owner_identity=<EXPLICIT_HUMAN_IDENTITY>
authorization_decision=GRANTED|DENIED
baseline_reconstruction_execution_decision=AUTHORIZED|NOT_AUTHORIZED
authorized_at=<ISO_8601_WITH_TIMEZONE>
expires_at=<ISO_8601_WITH_TIMEZONE>
authorization_use=ONE_USE
authorization_consumed=false
authorization_revoked=false
R4_dynamic_content_mode_decision=APPROVED|DENIED
all_bound_digests=<EXACT_COMPLETE_SET>
```

`authorized_at` 必须是实际签署事件时间，`expires_at` 必须由 Human Authority Owner 明确给出，
不能由 Agent 从推荐期限推断。过期窗口不得无限期或无 timezone。

### 11.2 Detached attestation

签署结果写入 detached `human-grant-attestation.json`，引用 inactive record instance、DB-001～
DB-006 supporting digests 与 P。不得在 P 后编辑 repository record instance 或 P-hashed file。

Attestation 必须再次声明：

```text
SAEE_RECOMMENDATION_NOT_AUTHORIZATION=true
SAEE_EXECUTION_CONTROL=false
SAEE_AUTO_APPROVAL_CORE=false
H0_R_AUTHORIZES_DEMO=false
H0_R_AUTHORIZES_PUSH=false
H0_R_AUTHORIZES_EXTERNAL_ACTION=false
```

```text
DB_006_PATH=<attempt_root>/human-grant-attestation.json
human_grant_attestation_sha256=<CALCULATED_AFTER_HUMAN_SIGNATURE>
DB_006_STATUS=HUMAN_GRANTED_OR_DENIED_NOT_YET_ATOMICALLY_EVALUATED
```

无签署、denial、identity 不完整或 expiry 无效均立即停止；不会产生有效 grant。

## 12. G8 — Atomic H0-R Grant Evaluation

### 12.1 Live recheck

Evaluator 在读取 human attestation 后立即重新计算 P-sensitive live state：HEAD/tree/status、
patch、refs、worktrees、stash、protected truth、candidate absence、Demo absence 与 current time。
任何差异都使 signed tuple 无效；不得修改 P 或签名来适配变化。

### 12.2 Atomic predicate

只有全部为 true 才能产生有效 PASS receipt：

```text
record_instance_digest_matches
AND F1_plan_human_reviewed
AND DB_001_digest_and_scope_match
AND DB_002_digest_and_closure_match
AND validator_contract_digest_matches
AND R3_manifest_digest_and_acceptance_match
AND role_identities_are_actual_and_separated
AND locations_match_and_are_collision_free
AND P_is_complete_and_matches_live_state
AND human_signature_is_authentic_and_explicitly_grants
AND expiry_is_current
AND authorization_is_one_use_not_consumed_not_revoked
AND R4_frozen_contract_mode_is_human_approved
AND authority_schema_exact_bytes_match
AND Recommendation_Execution_Separation_is_preserved
AND candidate_and_Demo_paths_remain_absent
AND push_PR_release_external_authority_is_false
```

No partial PASS。Evaluator 输出 detached receipt：

```text
GRANT_RECEIPT_PATH=<attempt_root>/grant-evaluation-receipt.json
grant_evaluation_result=PASS|FAIL
effective_authorization_state=GRANTED|NOT_GRANTED
effective_reconstruction_state=AUTHORIZED|NOT_AUTHORIZED
record_instance_sha256=<digest>
P_sha256=<digest>
human_grant_attestation_sha256=<digest>
evaluated_at=<timestamp>
evaluator_identity=<actual_identity>
failure_reasons=[]
```

Receipt 只证明 human grant 与动态事实满足 predicate；它不创造人类权威。

### 12.3 Current state

```text
ATOMIC_GRANT_EVALUATION_RUN=false
GRANT_EVALUATION_RECEIPT_CREATED=false
H0_R_GRANTED=false
BASELINE_RECONSTRUCTION_EXECUTION_AUTHORIZED=false
```

## 13. Failure、Invalidation and Regeneration

| Failure | Immediate result | Regeneration boundary |
|-|-|-|
| DB-001 path/hunk mismatch | invalidate attempt; no DB-002 | new DB-001 after human scope review |
| DB-002 closure gap/overlap | no contracts/roles | fix design through human review; new attempt |
| validator/R3 self-reference | stop G3 | regenerate G3 and all downstream |
| generic or equal role identity | no location/P | bind real distinct identities; regenerate DB-004 onward |
| branch/worktree/path collision | no P | human selects new location; regenerate DB-005 onward |
| P serialization or live-state mismatch | no signature | new P after investigation |
| any P-hashed input changes after P | signed tuple invalid | regenerate affected artifact, P, human signature |
| expiry invalid/expired/revoked/consumed | no execution | new human attestation and atomic evaluation |
| grant evaluator FAIL | preserve receipt; no mutation | human-reviewed new attempt |

冻结：

```text
SILENT_REHASH_ALLOWED=false
IN_PLACE_SIGNED_ARTIFACT_REPAIR_ALLOWED=false
AUTOMATIC_SCOPE_EXPANSION_ALLOWED=false
SHARED_DIRTY_WORKTREE_CLEAN_RESET_STASH_ALLOWED=false
FAILED_EVIDENCE_DELETION_ALLOWED=false
```

## 14. Human Signature Point and Stop Points

### Signature point

人工签署只能发生在：

```text
DB_001_FROZEN
AND DB_002_FROZEN
AND VALIDATOR_CONTRACT_FROZEN
AND R3_MANIFEST_FROZEN
AND DB_004_IDENTITIES_BOUND
AND DB_005_LOCATIONS_BOUND
AND DB_003_P_FROZEN
AND NO_RECONSTRUCTION_MUTATION_STARTED
```

### Stop matrix

| Stop | Evidence state | Maximum next action |
|-|-|-|
| S-F1 | this plan human-reviewed | explicitly authorize detached artifact generation |
| S-DB2 | DB-001/002 frozen | generate supporting contracts only |
| S-G3 | validator/R3 frozen | bind actual roles |
| S-G5 | roles/locations frozen | generate P |
| S-P | P frozen | human grant/deny |
| S-SIGN | detached signature exists | atomic evaluator only |
| S-FAIL | atomic FAIL | preserve evidence; no mutation |
| S-PASS | atomic PASS receipt | immediate TOCTOU recheck, then separately enter R1-R4 |
| S-R4 | Candidate B/Q-B | stop H0-R; H1 required |

## 15. Transition Boundary to R1-R4

DB artifact generation、human signature 或 validator PASS 均不允许 R1-R4。只有 fresh detached
receipt 同时满足以下三个值，才可在 expiry/one-use 范围内进入 reconstruction：

```text
grant_evaluation_result=PASS
effective_authorization_state=GRANTED
effective_reconstruction_state=AUTHORIZED
```

进入前仍需一次 read-only TOCTOU recheck。随后允许的最大范围仅是 exact branch/worktrees 与
R1 Authority、R2 Governance、R3 Accepted Inputs、R4 Candidate Manifest，直到 Candidate B +
detached Q-B 为止。

仍禁止：

```text
Demo implementation
new capability
schema semantic change
MCP/runtime/evaluation/product change
authority switch
push/PR/release
external integration or external action
```

## 16. Artifact Readiness Matrix

| Artifact/binding | Design | Generated now | Identity/digest bound | Human grant effect |
|-|-|-|-|-|
| DB-001 Path/Hunk | COMPLETE | NO | NO | NONE |
| DB-002 Forbidden Scope | COMPLETE | NO | NO | NONE |
| Validator Contract | COMPLETE | NO | NO | NONE |
| R3 Input Manifest | COMPLETE | NO | NO | NONE |
| DB-004 Roles | COMPLETE | NO | NO | NONE |
| DB-005 Locations | COMPLETE | NO | NO | NONE |
| DB-003 P | COMPLETE | NO | NO | NONE |
| DB-006 Expiry/signature | COMPLETE | NO | NO | NONE |
| Atomic receipt | COMPLETE | NO | NO | NONE |

```text
DYNAMIC_BINDING_GENERATION_SEQUENCE_COMPLETE=true
DYNAMIC_BINDING_ARTIFACTS_COMPLETE=false
HUMAN_FINAL_BINDING_COMPLETE=false
H0_R_FINAL_BINDINGS_COMPLETE=false
```

## 17. First-Principles Check

### Why generate evidence before grant?

Human authority must bind a concrete object，not a promise to decide details later。Without exact
digests、identities、locations and P，the approved subject is incomplete，so execution scope can drift
after signature。

### Why is P last before signature?

P must observe every fact that the human signs，yet must precede the signature that references it。If
any hashed fact changes after P，the grant tuple no longer describes execution prestate。

### Why are role and location facts mandatory?

The same bytes executed by an unbound actor or in a colliding worktree are a different risk event。
Artifact correctness cannot substitute for actor separation or filesystem/Git isolation。

### Why does PASS not authorize?

A validator can establish consistency only。Authority remains an explicit human decision，and SAEE's
long-term role remains Recommendation / Decision Context rather than execution control。

## 18. Plan Pre-image and Input Integrity

Target report creation pre-image：

```text
branch=feat/canonical-capability-inventory-routing-v1
head=f6ac41f4b068377e7778e8c3d83b99bd8382debc
head_tree=def1f5fb06b8087a5c0fabd929be253f25faed67
status_default_entry_count=120
status_all_untracked_entry_count=137
status_default_sha256=26178d17d9fd8d8012e01183d31672f82d9af7afd30e8a160607c58189b6da54
status_all_untracked_sha256=7901cfc15a270a8d959cb233c4e1cb37bb84e2824bfb024de1543720cd1f6c7b
staged_patch_sha256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
unstaged_patch_sha256=d44ecf7871a1816fc9c1f9c203bb9e0a664638e54c5666ad8090643c8ef3ff1a
registered_worktree_count=4
stash_count=0
target_report_preexisting=false
```

Exact inputs：

```text
reports/SAEE_H0_R_FINAL_BINDING_EXECUTION_PLAN.md=93b6ec791e1903e5cfe4d6e50995ddf562f4ade1f03adb3fcdf9f5521cfa12ab
reports/SAEE_H0_R_DYNAMIC_BINDING_PREPARATION.md=a6c251c7af4629805d836902673fbff3f05274242968908ab115bf31899a0616
reports/SAEE_H0_R_AUTHORIZATION_RECORD_INSTANCE.md=dfc77433c4c0884c2f782e282917bb697601253ef25a9822e82786eb5a140f57
```

## 19. Final Status

```text
H0_R_DYNAMIC_ARTIFACT_GENERATION_PLAN_STATUS=COMPLETE
H0_R_FINAL_BINDING_DECISION=APPROVED
H0_R_FINAL_BINDING_DECISION_SCOPE=ENTER_DYNAMIC_BINDING_PLANNING_ONLY
DYNAMIC_BINDING_ARTIFACT_GENERATION_STARTED=false
DYNAMIC_BINDING_ARTIFACTS_COMPLETE=false
HUMAN_FINAL_BINDING_COMPLETE=false
H0_R_HUMAN_SIGNATURE_RECORDED=false
ATOMIC_GRANT_EVALUATION_RUN=false
H0_R_GRANTED=false
BASELINE_RECONSTRUCTION_EXECUTION_AUTHORIZED=false
SAEE_RECOMMENDATION_NOT_AUTHORIZATION=true
SAEE_EXECUTION_CONTROL=false
SAEE_AUTO_APPROVAL_CORE=false
PATH_HUNK_MANIFEST_CREATED=false
FORBIDDEN_SCOPE_MANIFEST_CREATED=false
VALIDATOR_CONTRACT_CREATED=false
R3_ACCEPTED_INPUT_MANIFEST_CREATED=false
ROLE_BINDING_CREATED=false
LOCATION_BINDING_CREATED=false
PREIMAGE_P_CREATED=false
EXPIRY_BINDING_COMPLETE=false
GRANT_EVALUATION_RECEIPT_CREATED=false
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
PRODUCT_REGISTRY_CHANGED=false
CONSTITUTION_CHANGED=false
PROJECT_MEMORY_CHANGED=false
CODE_CHANGED=false
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_DYNAMIC_ARTIFACT_GENERATION_PLAN
```

## 20. Current-Phase Validation Record

本节只验证计划报告生成安全性，不验证 DB artifacts、human signature 或 H0-R grant。

```text
PROJECT_MEMORY_CHECK=PASS
GOVERNANCE_REGISTRY_CHECK=PASS
DEVELOPMENT_CONSTITUTION_SMOKE=PASS
CANONICAL_CAPABILITY_INVENTORY_SMOKE=PASS
CAPABILITY_PROGRESS_LEDGER_SMOKE=PASS
QIANFAN_READINESS_MCP_SMOKE=PASS
QODER_ADAPTER_SMOKE=PASS
PUBLIC_CAPABILITY_SURFACE_SMOKE=PASS
GIT_DIFF_CHECK=PASS
REPORT_DIFF_CHECK=PASS
ONLY_TARGET_REPORT_ADDED=PASS

PREEXISTING_STATUS_DEFAULT_COUNT=120
PREEXISTING_STATUS_ALL_UNTRACKED_COUNT=137
PREEXISTING_STATUS_DEFAULT_SHA256=26178d17d9fd8d8012e01183d31672f82d9af7afd30e8a160607c58189b6da54
PREEXISTING_STATUS_ALL_UNTRACKED_SHA256=7901cfc15a270a8d959cb233c4e1cb37bb84e2824bfb024de1543720cd1f6c7b
STAGED_PATCH_SHA256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
UNSTAGED_PATCH_SHA256=d44ecf7871a1816fc9c1f9c203bb9e0a664638e54c5666ad8090643c8ef3ff1a
BRANCH=feat/canonical-capability-inventory-routing-v1
HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
HEAD_TREE=def1f5fb06b8087a5c0fabd929be253f25faed67
REGISTERED_WORKTREE_COUNT=4
STASH_COUNT=0
CANDIDATE_BRANCH_CREATED=false
RECONSTRUCTION_WORKTREE_CREATED=false
VALIDATION_WORKTREE_CREATED=false
DYNAMIC_BINDING_EVIDENCE_ROOT_CREATED=false
PREIMAGE_P_CREATED=false
R4_CANDIDATE_MANIFEST_CREATED=false
```
