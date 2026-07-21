# SAEE Goal Integrity Evidence Root Initialization Plan

## Phase 8.0-D6.2 — Local Evidence Space Before Fixture Creation

```text
plan_id=SAEE-GI-P0-EVIDENCE-ROOT-PLAN-20260716-V1.0
plan_date=2026-07-16
plan_type=INITIALIZATION_PLAN_ONLY
readiness_review_sha256=af1e2450adea340b4435e960a3066e458736ab8f4f8b240f01dc4a4d861c371a
closure_plan_sha256=36501278ba88d8ddd43571f189fc9f92d10c89bdbf9306351eed121831ca9417
```

## Executive Decision

D6 和 D6.1 已经定义 Evidence Root 必须位于 SAEE repository 外、保存 failed attempts、使用 write-once lineage，
并在 fixture 创建前关闭 `G6 Evidence preservation`。本文件不重复 readiness theory，只冻结初始化所需的：

```text
candidate_path
directory_names
receipt_and_hash_rules
access_roles
permission_expectations
retention_boundary
G6_acceptance_criteria
```

本计划没有创建任何目录或 evidence。候选路径当前只经过只读 absent check：

```text
CANDIDATE_EVIDENCE_ROOT=/Users/zhangbin/Documents/SAEE-experiments/goal-integrity-p0/SAEE-GI-P0-20260716-001
CANDIDATE_EVIDENCE_ROOT_STATE_AT_PLAN_TIME=ABSENT
EVIDENCE_ROOT_CREATION_AUTHORIZED=false
EVIDENCE_ROOT_CREATED=false
```

## Commander Preflight Decision

```text
COMMANDER_COMMAND_CHECK=WARNING
MAINLINE_DRIFT_DETECTED=true
DUPLICATE_BUILD_RISK=true
DUPLICATE_BUILD_PREVENTED=true
STAGED_TRUTH_RISK=true
MAINLINE_DRIFT_STATUS=CONTAINED_BY_LOCAL_EVIDENCE_ROOT_PLAN
PROGRAM_MAINLINE_CHANGED=false
```

该 Evidence Root 是一个 bounded local research artifact store，不是新的 SAEE product、Capability 或 audit stack。

# 1. Purpose

Evidence Root 必须早于 fixture，原因不是追求更多治理，而是保证第一项可变实验事实就进入可追溯 lineage：

```text
Human root authorization
  ↓
Root initialization attempt
  ↓
Fixture creation attempt
  ↓
Runtime binding attempt
  ↓
Annotation binding
  ↓
Session attempts
  ↓
Adjudication and final analysis
```

如果先创建 fixture、之后才建立 Evidence Root，则无法可信记录：

- fixture 创建前状态；
- 第一次创建失败；
- 被替换或修正的 bytes；
- copy/hash 不一致；
- 创建者、授权和 stop point；
- 为什么一个 attempt 被判 invalid。

Evidence Root 的目标是保留 P0 的状态演化与失败证据，而不是让实验更容易得到正结果。

# 2. Root Boundary

## 2.1 Frozen candidate paths

```text
SAEE_REPOSITORY=/Users/zhangbin/Documents/SAEE
EXPERIMENT_PARENT=/Users/zhangbin/Documents/SAEE-experiments/goal-integrity-p0
STUDY_ID=SAEE-GI-P0-20260716-001
CANDIDATE_EVIDENCE_ROOT=/Users/zhangbin/Documents/SAEE-experiments/goal-integrity-p0/SAEE-GI-P0-20260716-001
```

未来 human authorization 必须引用 exact absolute path。若该 path 在授权前已存在，初始化立即停止；不得清理、
覆盖、合并或推测它是安全空目录。

## 2.2 Repository isolation

必须满足：

- candidate root 不是 SAEE repository 的 descendant；
- candidate root 不是 Git worktree；
- candidate root 不包含 `.git`；
- 不创建指向 SAEE repository、home secrets 或其他 project 的 symlink；
- 不使用 hard link、device、socket 或 FIFO；
- fixture/session workspace 与 evidence root 分离；
- Agent runtime 不把 evidence root 配置为 writable workspace；
- SAEE dirty worktree 不作为 evidence source；
- root 初始化不得修改 SAEE tracked/untracked files。

```text
ROOT_IS_EXTERNAL_TO_SAEE_REPOSITORY=true
ROOT_IS_GIT_WORKTREE=false
SYMLINKS_ALLOWED=false
HARDLINKS_ALLOWED=false
AGENT_DIRECT_WRITE_TO_EVIDENCE_ROOT=false
```

## 2.3 Data boundary

P0 Evidence Root 只允许 synthetic/local research data。禁止：

- customer/personal/payment data；
- production credentials；
- provider API keys；
- GitHub tokens；
- unrelated repository content；
- unknown external code；
- secrets copied from environment。

runtime binding 可以记录 key **presence state** 或 secret reference name，但不能保存 secret value。

# 3. Write-once Rules

## 3.1 Write-once class

```text
WRITE_ONCE_CLASS=LOCAL_LOGICAL_WRITE_ONCE_WITH_HASH_CHAIN
HARDWARE_WORM=false
TAMPER_PROOF_STORAGE=false
CRYPTOGRAPHIC_TIMESTAMP_AUTHORITY=false
```

在普通本地 filesystem 和同一 OS owner 下，permissions 不能阻止 owner 重新 chmod 或篡改。因此本计划只声称：

- 不覆盖既有 attempt；
- sealed artifacts 使用 read-only modes；
- receipts 形成 SHA-256 chain；
- independent validator 可发现多数非授权变化；
- 无法提供硬件 WORM、remote notarization 或 adversarial tamper resistance。

## 3.2 Attempt lifecycle

每次 future action 必须先分配不可复用的 attempt ID：

```text
attempt-000001
attempt-000002
...
```

状态只能沿以下方向：

```text
ALLOCATED
  -> WRITING
  -> SEALED_COMPLETE

or

ALLOCATED
  -> WRITING
  -> INVALID_PRESERVED

or

ALLOCATED
  -> FAILED_BEFORE_WRITE
```

禁止从 `INVALID_PRESERVED` 改回 complete；修复只能使用新 attempt ID。

## 3.3 No history mutation

禁止：

- overwrite、truncate、delete 或 rename 已 sealed artifact；
- 重用 attempt ID；
- 把 failed directory 替换为成功目录；
- 根据实验结果修改 prompt、Goal、label 或 receipt；
- 删除 timeout、invalid output、negative result 或 authorization denial；
- 移动 failed evidence 到不在 manifest 中的位置。

若发现 sealed artifact 不一致：

1. 停止后续写入；
2. 创建新的 incident attempt；
3. 记录 affected hashes；
4. 标记 chain verification fail；
5. 请求 human review；
6. 不原位修复历史。

## 3.4 Receipt chain

每个 sealed attempt receipt 至少包含：

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

第一条 receipt 使用：

```text
parent_receipt_sha256=GENESIS
```

后续 receipt 引用前一条 canonical receipt SHA-256。不得覆盖一个 mutable `head.json`；每次 chain head 创建新文件：

```text
ledger/heads/head-000001.json
ledger/heads/head-000002.json
```

## 3.5 Canonical serialization

JSON receipts 和 manifests 必须：

- UTF-8；
- recursive lexicographic key ordering；
- stable array order where semantically ordered；
- LF line endings；
- final newline；
- no insignificant rewrite after sealing；
- SHA-256 repeated calculation `3/3` identical before acceptance。

# 4. Directory Model

以下只是 future structure，不在本轮创建：

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

## 4.1 Root manifest

`evidence-root-manifest.json` 未来只记录初始化时不变事实：

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

它不保存会不断变化的 current chain head；否则每次 append 都需要重写 manifest。

## 4.2 Attempt layout

每个 category 下使用：

```text
<category>/attempt-000001/
  raw/
  canonical/
  artifact-manifest.json
  attempt-receipt.json
  boundary-observation.json
```

即使 attempt 在 `raw/` 写入中失败，目录和已写 bytes 仍保留，并尽可能写入 `INVALID_PRESERVED` receipt。

## 4.3 Category boundary

| Directory | Allowed evidence |
|---|---|
| `authorization/` | human grants、denials、expiry/consumption records |
| `source-bindings/` | D3.1–D6.2 hashes、status receipts |
| `case-inputs/` | prompts、Goal/Transition packets、ground-truth prelabels |
| `fixtures/` | creation attempts、manifests、copy verification、sentinel |
| `runtime/` | executable/model/config/tool/sandbox/cost bindings and preflight |
| `annotations/` | role binding、R1/R2 records、rubric、agreement |
| `randomization/` | seed、sealed mapping、order receipt |
| `sessions/` | commands、events、stdout/stderr、pre/post trees、tests、cost |
| `adjudication/` | disagreements、blind decisions、adjudication records |
| `final-analysis/` | frozen analysis、limitations、negative results、human conclusion |

一个 artifact 只存在于一个 canonical category；其他位置用 hash reference，不复制成多个事实源。

# 5. Integrity Requirements

## 5.1 Hash requirements

- content hash：file bytes 的 SHA-256；
- manifest hash：canonical manifest bytes 的 SHA-256；
- deterministic tree hash：按 normalized relative path 递归字典序，绑定 entry type、mode 和 content hash；
- receipt hash：canonical receipt bytes 的 SHA-256；
- chain verification：每个 `parent_receipt_sha256` 指向前一 receipt；
- no symlink following；
- no absolute path stored as tree entry key；root absolute path 只存于 root manifest。

## 5.2 Timestamp requirements

```text
timestamp_format=RFC3339_UTC
local_timezone_annotation=Asia/Shanghai
monotonic_sequence_required=true
```

wall-clock timestamp 仅是 declared metadata，不是 trusted time proof。排序首先依赖 monotonic sequence 和 receipt chain，
不能因系统时钟回拨重写历史。

## 5.3 Permission expectations

future initialization 的最低期望：

```text
root_mode=0700
writable_attempt_directory_mode=0700
sealed_directory_mode=0550
sealed_file_mode=0440
```

这些 modes 只防止意外写入和未授权 group/other access，不构成对 root owner 的强制不可变保障。

## 5.4 Chain verification schedule

必须在以下时点复验：

1. root initialization 完成；
2. 每个 attempt seal 后；
3. fixture/runtime/annotation gate closure 前；
4. 每个 Agent session 前后；
5. final analysis 前；
6. human conclusion 前。

任一 verification fail：后续 gate fail-closed。

## 5.5 Concurrency

- 同一时刻只允许一个 Evidence Custodian writer；
- Agent session 不直接写 root；
- reviewer 只读；
- parallel fixture/runtime/session attempts 禁止，除非未来新授权重写该规则；
- writer lock 只是本地过程控制，不是 distributed lock claim。

# 6. Failure Preservation

## 6.1 Root initialization failure

若初始化在 candidate path 创建后失败：

- 保留 partial root；
- 不删除、不重新使用同一路径；
- 尽可能写入 `INVALID_PRESERVED` bootstrap receipt；
- 若 receipt 无法写入，保留 command stdout/stderr 和 partial path observation；
- 新尝试必须使用新的 study/root attempt suffix，并获新授权。

若在任何 filesystem write 前失败，则只记录外层授权任务的 failure evidence，不声称 root 已创建。

## 6.2 Fixture failure

保存：

- authorization；
- preimage/root chain head；
- attempted file list；
- partial bytes；
- command/stdout/stderr；
- manifest/hash mismatch；
- required absence or sentinel failure；
- `FIXTURE_CREATED=false` receipt。

不得删除失败 fixture 后在同一 attempt 重建。

## 6.3 Runtime failure

保存：

- executable/version/hash；
- runtime config；
- model/provider declared binding；
- sandbox/tool/network projection；
- parse/preflight output；
- timeout/provider/startup failure；
- `MODEL_INVOKED` 和 `SESSION_CREATED` 的准确状态。

runtime failure 不计为 Agent behavior failure。

## 6.4 Authorization denial, expiry or non-use

如果 Human 拒绝、授权过期或 one-use grant 未使用：

- 保存 decision/expiry/non-use receipt；
- 不创建 session；
- 不把 denial 当作 research failure；
- 不自动请求更宽权限。

## 6.5 Negative and invalid session results

所有 negative、drift、timeout、invalid、boundary breach、unclassifiable outputs 保留；不得只保存成功 arm。

# 7. Access Boundary

## 7.1 Roles

| Role | Create | Append new attempt | Read | Seal/verify | Modify sealed history |
|---|---:|---:|---:|---:|---:|
| Human Authority Owner | authorize only | no | yes | accept receipts | no |
| Evidence Custodian | root initialization after authorization | yes | yes | seal | no |
| Independent Validator | no | validation receipt only | yes | verify | no |
| Fixture Author | through authorized attempt workspace | no direct root write | limited | no | no |
| Runtime Binder | through authorized attempt workspace | no direct root write | limited | no | no |
| P0 Executor | no root creation | session stream via custodian | limited | no | no |
| Annotator/Reviewer | annotation receipt via custodian | no direct history rewrite | assigned views | sign decision | no |
| Agent under test | no | no | only frozen task workspace | no | no |

## 7.2 Identity state

```text
HUMAN_AUTHORITY_OWNER_ID=UNBOUND_FOR_P0
EVIDENCE_CUSTODIAN_ID=UNBOUND
INDEPENDENT_VALIDATOR_ID=UNBOUND
```

角色定义不等于身份绑定。G6 关闭前必须完成人工 role confirmation。

## 7.3 Secret and permission boundary

- Evidence Custodian 不记录 provider secret values；
- Agent under test 不获得 root write path；
- root creation 不扩大 Codex、Agent 或 MCP permissions；
- root 不用于执行 code；
- evidence files 只作为 data 阅读；
- unknown external artifacts 不进入 root。

# 8. Retention and Disposal

```text
RETENTION_POLICY=NO_AUTOMATIC_DELETION_UNTIL_EXPLICIT_POST_STUDY_HUMAN_DISPOSITION
AUTO_CLEANUP=false
FAILED_ATTEMPT_RETENTION=true
NEGATIVE_RESULT_RETENTION=true
```

P0 期间和 human conclusion 前禁止删除。任何未来 disposition 必须另行设计并授权；该 future action 需要先生成
root-level final chain receipt 和 disposal scope，但本阶段不定义或执行删除流程。

由于仅允许 synthetic data，本计划不声称满足企业 records retention、legal hold、privacy deletion 或 regulated
storage requirements。

# 9. G6 Gate Closure Relation

## 9.1 G6 closure predicate

```text
G6_EVIDENCE_PRESERVATION_PASS :=
    human_root_creation_authorization_received=true
AND candidate_path_precondition=ABSENT
AND evidence_custodian_bound=true
AND independent_validator_bound=true
AND root_created_at_exact_authorized_path=true
AND root_outside_saee_repository=true
AND directory_allowlist_exact=true
AND symlink_hardlink_forbidden_check=PASS
AND root_manifest_hash_verified=true
AND write_once_policy_hash_verified=true
AND permission_check=PASS
AND bootstrap_attempt_preservation_smoke=PASS
AND receipt_chain_verification=PASS
AND hash_determinism=3/3
AND saee_repository_unchanged=true
AND blocking_issues=[]
```

## 9.2 G6 acceptance artifacts

未来至少需要：

```text
human-evidence-root-authorization.json
evidence-root-manifest.json
write-once-policy.md
bootstrap-command-record.json
bootstrap-stdout.log
bootstrap-stderr.log
bootstrap-attempt-receipt.json
permission-verification.json
chain-verification.json
boundary-observation.json
evidence-root-binding-receipt.json
```

这些是 future artifact names，不是新 Schema。

## 9.3 What G6 closure does not close

即使 G6 未来 PASS，仍保持：

```text
G2_CASE_INPUTS=OPEN
G3_FIXTURE=OPEN
G4_RUNTIME=OPEN
G5_ANNOTATION=OPEN
G7_RANDOMIZATION=OPEN
G8_EXECUTION_AUTHORIZATION=OPEN
P0_TECHNICALLY_READY=false
P0_EXECUTION_AUTHORIZED=false
```

Evidence Root 创建只提供证据空间，不授权任何实验资产或 Agent session。

# 10. Risk Register

| Risk | Boundary |
|---|---|
| Local owner can rewrite modes/history | 明确 `LOCAL_LOGICAL_WRITE_ONCE`，不声称 tamper-proof；依靠 hash chain + independent verification |
| Clock manipulation | timestamp 仅 metadata；monotonic sequence 和 chain 为主要顺序 |
| Symlink/path escape | exact absolute path、no symlink/hardlink、entry-type verification |
| Concurrent writer | single custodian writer；no parallel attempts |
| Agent modifies evidence | root 不进入 Agent writable roots；custodian capture streams |
| Bootstrap failure lost | partial path preserved；outer command evidence retained |
| Manifest becomes mutable head | root manifest 静态；每个 head 新建文件 |
| Secret leakage | synthetic-only；secret value prohibited；references only |
| Duplicate audit stack | root 仅服务 P0，未注册 Capability/Product，不修改 MCP |
| Mainline displacement | time/scope bounded；G6 plan 不取代 integration mainline |
| Staged-truth inflation | plan/created/verified/gate-pass/authorized 状态分离 |

# 11. Non-Claims

本计划不代表：

- Evidence Root 已创建、验证或关闭 G6；
- 本地 filesystem 是 WORM、tamper-proof、secure enclave 或 trusted timestamp service；
- SAEE 已实现生产审计、合规存储、SIEM、IAM 或自动治理；
- fixture、runtime、annotation、randomization 或 Agent session 已创建；
- P0 已 ready、authorized 或 executed；
- Goal Integrity 假设已有任何结果；
- 新 Capability、Schema、Protocol、MCP、Skill 或 code 已实现；
- State Integrity research 已取代 SAEE / Agent Evidence integration mainline。

# 12. Final Status

```text
EVIDENCE_ROOT_INITIALIZATION_PLAN_STATUS=COMPLETE
CANDIDATE_EVIDENCE_ROOT=/Users/zhangbin/Documents/SAEE-experiments/goal-integrity-p0/SAEE-GI-P0-20260716-001
CANDIDATE_EVIDENCE_ROOT_STATE_AT_PLAN_TIME=ABSENT
WRITE_ONCE_CLASS=LOCAL_LOGICAL_WRITE_ONCE_WITH_HASH_CHAIN
EVIDENCE_ROOT_CREATION_AUTHORIZED=false
EVIDENCE_ROOT_CREATED=false
G6_EVIDENCE_PRESERVATION_STATUS=OPEN
FIXTURE_CREATED=false
RUNTIME_CREATED=false
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
MAINLINE_DRIFT_STATUS=CONTAINED_BY_LOCAL_EVIDENCE_ROOT_PLAN
PROGRAM_MAINLINE_CHANGED=false
NEXT_ACTION=HUMAN_REVIEW_OF_EVIDENCE_ROOT_PLAN
```
