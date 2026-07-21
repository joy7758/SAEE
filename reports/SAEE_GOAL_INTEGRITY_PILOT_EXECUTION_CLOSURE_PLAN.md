# SAEE Goal Integrity Pilot Execution Closure Plan

## Phase 8.0-D6.1 — From NOT_READY to a Separately Authorized P0

```text
plan_id=SAEE-GOAL-INTEGRITY-P0-CLOSURE-20260716-V1.0
plan_date=2026-07-16
plan_type=GATE_CLOSURE_LEDGER_NOT_EXECUTION
preregistration_sha256=db3deadd762897027ed85cf4217e67e68dc1071764ece74f7a3ffe7d828f2493
readiness_review_sha256=af1e2450adea340b4435e960a3066e458736ab8f4f8b240f01dc4a4d861c371a
```

## Executive Decision

D6 已经定义 readiness requirements、gate matrix、failure taxonomy 和 closure sequence。为避免再造同义报告，
本文件只补充 D6 尚未绑定的四类操作信息：

```text
owner_role
required_input
acceptance_criteria
closure_receipt
```

D6 当前事实是：

```text
READINESS_GATES_TOTAL=9
READINESS_GATES_PASS=1
READINESS_GATES_OPEN=8
READINESS_VERDICT=NOT_READY
P0_EXECUTION_READY=false
P0_EXECUTION_AUTHORIZED=false
```

不是 9 个 gate 全部未通过；`G0 Source integrity` 已通过，但 source hash 变化会使其重新打开。

## Commander Preflight Decision

```text
COMMANDER_COMMAND_CHECK=WARNING
MAINLINE_DRIFT_DETECTED=true
DUPLICATE_BUILD_RISK=true
DUPLICATE_BUILD_PREVENTED=true
STAGED_TRUTH_RISK=true
MAINLINE_DRIFT_STATUS=CONTAINED_BY_THIN_CLOSURE_LEDGER
PROGRAM_MAINLINE_CHANGED=false
```

本 plan 不关闭任何 gate，不分配真实 identity，不创建 artifact，也不授予执行。

# 1. Current Readiness Gap Ledger

## 1.1 Gate summary

| Gate | Current state | Missing item | Owner role | Closure acceptance | Required receipt |
|---|---|---|---|---|---|
| `G0` Source integrity | `PASS` | none currently | Evidence Custodian | D3.1/D3.4/D4/D5/D6 expected hashes all复算一致 | `source-integrity-receipt.json` |
| `G1` Preregistration acceptance | `OPEN` | human acceptance of exact D5/D6 | Human Authority Owner | exact hashes、local-only boundary、D5 amendment 和 D6 `NOT_READY` 被明确接受 | `human-preregistration-acceptance.json` |
| `G2` Executable case inputs | `OPEN` | prompts、packets、injections、oracles、case hashes | Fixture Author + Ground-truth Custodian | 7 primary cases + `P-C01` 全部 byte-frozen；无 label leakage；manifest/hash 可复算 | `case-input-binding-receipt.json` |
| `G3` Fixture | `OPEN` | isolated fixture、arm copies、tests、sentinel、tree hashes | Fixture Author + Independent Validator | source/A/B/C preimages 等价；required absences 成立；sentinel local-only；copy verification pass | `fixture-creation-receipt.json` |
| `G4` Runtime | `OPEN` | Agent/model/provider/version/sandbox/tools/time/cost binding | Runtime Binder + Independent Validator | exact executable hash、model/provider、tool count、sandbox、network、ceilings、no-retry/fallback 全部绑定并 preflight pass | `runtime-binding-receipt.json` |
| `G5` Annotation | `OPEN` | R1/R2/adjudicator/blind reviewer/custodian identities and sealed rubric | Human Authority Owner + Annotation Lead | 两名独立 annotator 完成 pre-output labels；disagreement adjudicated；blind mapping sealed | `annotation-binding-receipt.json` |
| `G6` Evidence preservation | `OPEN` | external root、write-once attempts、canonical receipts、hash checks | Evidence Custodian + Independent Validator | root 在 SAEE repo 外；权限/路径冻结；failed attempts preserved；write-once smoke pass | `evidence-root-binding-receipt.json` |
| `G7` Randomization | `OPEN` | order mapping generated from frozen seed | Evidence Custodian | seed=`20260716`；case/arm order deterministic；mapping sealed before sessions | `randomization-receipt.json` |
| `G8` Execution authorization | `OPEN` | one-use human P0 grant | Human Authority Owner | G0–G7 all PASS、final preflight hash bound、scope/cost/session count explicit、one-use grant signed | `p0-execution-authorization.json` |

## 1.2 Owner-binding boundary

上表只定义 roles，不绑定人或 Agent identity：

```text
HUMAN_AUTHORITY_OWNER_ID=UNBOUND_FOR_P0
FIXTURE_AUTHOR_ID=UNBOUND
RUNTIME_BINDER_ID=UNBOUND
INDEPENDENT_VALIDATOR_ID=UNBOUND
ANNOTATOR_R1_ID=UNBOUND
ANNOTATOR_R2_ID=UNBOUND
ADJUDICATOR_ID=UNBOUND
BLIND_REVIEWER_ID=UNBOUND
EVIDENCE_CUSTODIAN_ID=UNBOUND
P0_EXECUTOR_ID=UNBOUND
```

角色重叠必须在 G5 前显式申报。`P0 Executor` 不得兼任 blind reviewer；case author 不得单独决定 ground truth。

# 2. Closure Sequence

## 2.1 Required order

关闭顺序不是简单按 gate 编号排列。Evidence root 必须在创建 fixture 前 bootstrap，才能保留 fixture creation 的失败
attempt：

```text
C0  Revalidate G0 source hashes
 ↓
C1  Human accepts exact D5 + D6 hashes                    -> closes G1
 ↓
C2  Authorize and bootstrap external write-once root      -> closes G6
 ↓
C3  Authorize and create executable case inputs           -> closes G2
 ↓
C4  Authorize and create fixture/copies/sentinel          -> closes G3
 ↓
C5  Bind R1/R2/adjudicator/blind reviewer/custodian       -> closes G5
 ↓
C6  Bind runtime/model/sandbox/tools/time/cost             -> closes G4
 ↓
C7  Generate and seal deterministic randomization mapping -> closes G7
 ↓
C8  Independent final static preflight                    -> technical readiness review
 ↓
C9  Human one-use P0 execution authorization              -> closes G8
 ↓
C10 First Agent session may be created
```

## 2.2 No automatic promotion

```text
GATE_CLOSURE_DOES_NOT_AUTHORIZE_NEXT_GATE=true
TECHNICAL_READINESS_DOES_NOT_AUTHORIZE_EXECUTION=true
HUMAN_REVIEW_DOES_NOT_EQUAL_HUMAN_EXECUTION_GRANT=true
ARTIFACT_CREATED_DOES_NOT_EQUAL_ARTIFACT_ACCEPTED=true
```

任一步失败必须停止并保留 attempt；不得在同一 attempt 自动修复、重试或继续后续 gate。

# 3. Human Gates

## HG-1 — Preregistration acceptance

Human 必须明确接受：

- D5 SHA-256；
- D6 SHA-256；
- P0 仅允许 `DIRECTIONAL_SUPPORT | NOT_SUPPORTED | INCONCLUSIVE`；
- 28-run maximum 是 ceiling，不是执行要求；
- `P-C01` 是 false-positive control；
- no new arm、no mid-study metric、no retry/fallback；
- local artifact 不是 public preregistration。

HG-1 不授权创建 fixture、runtime 或 session。

## HG-2 — Evidence-root creation authorization

必须明确允许：

- repository 外路径；
- 目录和 write-once attempt structure 创建；
- creation receipt/hash 写入；
- read/write ownership；
- cleanup boundary。

HG-2 不授权 fixture 或 Agent session。

## HG-3 — Case and fixture creation authorization

必须引用 D5/D6/closure hashes，冻结：

- 允许创建的 paths/files；
- 7 primary cases + `P-C01`；
- source/A/B/C copy strategy；
- injection、test、sentinel 和 required absences；
- no SAEE repository mutation。

HG-3 不授权模型调用。

## HG-4 — Role and annotation acceptance

必须确认：

- R1/R2 独立性；
- adjudicator boundary；
- blind reviewer 不看 mapping/ground truth；
- Evidence Custodian；
- role-overlap disclosure；
- disagreement stop rule。

## HG-5 — Runtime-binding acceptance

必须接受 exact Agent/model/provider/version/sandbox/tool/network/time/token/cost facts。Runtime binding 只允许静态
preflight；模型调用需要 HG-6。

## HG-6 — Final one-use execution authorization

只有 G0–G7 已由 independent final preflight 判 PASS 后，Human 才能签发：

```text
authorization_id
study_id
allowed_cases
allowed_arms
session_order_receipt_hash
model/provider
max_sessions
max_wall_time
max_tokens
max_provider_cost
no_retry
no_fallback
no_external_action
expiry
one_use
```

HG-6 是唯一允许创建第一个 P0 Agent session 的 gate。

# 4. Future Artifact Requirements

本节定义要求，不创建文件。

## 4.1 Evidence root package

```text
evidence-root-manifest.json
write-once-policy.md
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

验收：external path、owner、mode、canonical serialization、hash algorithm、attempt lineage 和 cleanup rule 全部冻结。

## 4.2 Case-input package

每个 case：

```text
task-prompt.txt
goal-baseline.txt
allowed-evolution.txt
arm-a-packet.txt
arm-b-packet.txt
arm-c-packet.txt
injection-record.json
ground-truth-record.json
recovery-target.json
case-manifest.json
```

验收：bytes/hash 固定；A/B/C 只存在 preregistered information difference；无 expected label leakage。

## 4.3 Fixture package

```text
fixture-source/
arm-a/
arm-b/
arm-c/
recovery-snapshots/
tests/
sentinel/
fixture-source-manifest.json
fixture-copy-verification.json
fixture-creation-receipt.json
```

验收：relative paths、bytes、modes、required absences、tree hashes 和 local-only sentinel 全部匹配。

## 4.4 Runtime-binding package

```text
agent-executable-binding.json
model-provider-binding.json
runtime-config.json
tool-surface-receipt.json
sandbox-network-boundary.json
cost-time-ceiling.json
runtime-preflight-receipt.json
```

验收：A/B/C runtime 等价；D/restart matched；no retry/fallback；preflight 不调用模型。

## 4.5 Annotation package

```text
role-binding.json
label-rubric.md
annotator-r1-prelabels.json
annotator-r2-prelabels.json
disagreement-record.json
adjudication-record.json
blind-review-template.md
sealed-view-mapping.json
annotation-binding-receipt.json
```

验收：pre-output labels、independence、agreement、disagreement、adjudication 和 blinding 可证明。

## 4.6 Final-preflight package

```text
all-gates-receipt.json
final-preimage.json
boundary-observation.json
blocking-issues.json
execution-authorization-template.json
```

验收：G0–G7 PASS，`blocking-issues=[]`，但 `P0_EXECUTION_AUTHORIZED=false` 直到 HG-6 完成。

# 5. Acceptance Criteria by Gate

## G0 — Source integrity

```text
PASS iff all expected source hashes match
FAIL action = stop; create new preregistration lineage if source changed
```

## G1 — Human acceptance

```text
PASS iff receipt names exact D5/D6 hashes and accepts claims/non-claims
FAIL action = no artifact creation
```

## G2 — Case inputs

```text
PASS iff all 8 registered trajectories are byte-frozen, hashed, leakage-reviewed and independently checked
FAIL action = preserve attempt; do not create Agent session
```

这里的 8 是 `7 primary + P-C01 control`，不是 8 primary cases。

## G3 — Fixture

```text
PASS iff source/A/B/C preimages are equivalent except arm packets,
tests/sentinel are local-only, and hashes/modes/absences all verify
```

## G4 — Runtime

```text
PASS iff exact Agent/model/provider/version/config/sandbox/tools/network/ceilings bind,
all arms share runtime facts, and static preflight passes without model invocation
```

## G5 — Annotation

```text
PASS iff R1/R2 independently prelabel every case,
material disagreement is adjudicated before outputs,
and blind mapping remains sealed
```

## G6 — Evidence preservation

```text
PASS iff external root exists, write-once attempt behavior is smoke-tested,
failed attempts are preservable, and receipts/hashes are deterministic
```

## G7 — Randomization

```text
PASS iff seed 20260716 deterministically produces a complete case/arm order,
mapping is hashed and sealed, and no session has started
```

## G8 — Execution authorization

```text
PASS iff a one-use, scoped, cost/time-limited human grant references
the final all-gates receipt and has not expired or been consumed
```

# 6. Risk Register

| Risk | Early signal | Prevention | Stop/closure action |
|---|---|---|---|
| Hidden-variable contamination | arms differ in model/tools/fixture/order | manifests + preflight equivalence | invalidate attempt; no automatic repair |
| Context-length confound | benefit only tracks packet size/verbosity | record token lengths and behavior, preserve P0 limitation | `INCONCLUSIVE`; do not add E mid-study |
| Label leakage | packet contains expected class or answer-shaped wording | independent packet review | rebuild as new version before execution |
| Duplicate build | request for Goal Plugin/Schema/IAM before P0 | canonical inventory + recommendation gate | reject/defer implementation |
| Mainline drift | research delays SAEE/Agent Evidence integration | scope/time ceiling and status review | pause P0 lane |
| Staged-truth inflation | artifact complete reported as ready/authorized | separate status constants | correct status before continuation |
| Role conflict | author judges own cases or sees mapping | pre-bound roles and disclosure | rebind roles; new review attempt |
| Evidence overwrite | retry replaces failure | write-once attempt directories | preserve invalid attempt; new authorization |
| Runtime drift | model/provider/version changes across arms | exact hash/config binding | invalidate affected comparison |
| Fixture mutation | tree hash changes or concurrent write | read-only source + pre/post hash | stop and preserve contamination evidence |
| Cost creep | ceiling raised after poor results | pre-bound hard ceilings | stop on ceiling; no mid-run increase |
| Negative-result suppression | failed/invalid cases excluded | frozen exclusion rules | include raw evidence and reason |
| Authorization creep | readiness interpreted as permission | HG-6 one-use gate | no session until exact grant |

```text
RISK_REGISTER_STATUS=DEFINED_NOT_EXECUTED
ACTIVE_RISK_CLOSURES=0
```

# 7. Final Technical Readiness and Execution Gate

## 7.1 Technical readiness predicate

```text
P0_TECHNICALLY_READY :=
    G0=PASS
AND G1=PASS
AND G2=PASS
AND G3=PASS
AND G4=PASS
AND G5=PASS
AND G6=PASS
AND G7=PASS
AND blocking_issues=[]
AND all_receipt_hashes_match=true
```

当且仅当该 predicate 成立，才可输出：

```text
P0_EXECUTION_READY=true
P0_EXECUTION_AUTHORIZED=false
NEXT_ACTION=HUMAN_REVIEW_OF_FINAL_P0_EXECUTION_AUTHORIZATION
```

## 7.2 Execution permission predicate

```text
P0_EXECUTION_ALLOWED :=
    P0_TECHNICALLY_READY=true
AND G8=PASS
AND authorization_one_use=true
AND authorization_expired=false
AND authorization_consumed=false
```

只有 `P0_EXECUTION_ALLOWED=true` 才能创建第一个 Agent session。

## 7.3 Current evaluation

```text
G0=PASS
G1=OPEN
G2=OPEN
G3=OPEN
G4=OPEN
G5=OPEN
G6=OPEN
G7=OPEN
G8=OPEN
P0_TECHNICALLY_READY=false
P0_EXECUTION_ALLOWED=false
```

# 8. Claims and Non-Claims

## Claims

- 已把 8 个 open readiness gates 转换成 role/input/acceptance/receipt ledger；
- 已定义不自动升级的 closure sequence；
- 已区分 technical readiness 与 one-use execution permission；
- 已定义 future artifact requirements 和 risk register；
- D6 `NOT_READY` 结论保持不变。

## Non-Claims

- 任何 gate 已因本 plan 新关闭；
- Human 已接受 D5/D6；
- owner identities 已绑定；
- evidence root、case inputs、fixture、runtime 或 annotation package 已创建；
- P0 已 ready、authorized、started 或 completed；
- Goal Integrity 假设已有结果；
- SAEE repository mainline、Capability、Schema、MCP、Skill 或代码已改变。

# 9. Final Status

```text
GOAL_INTEGRITY_EXECUTION_CLOSURE_PLAN_STATUS=COMPLETE
READINESS_GATES_TOTAL=9
READINESS_GATES_PASS=1
READINESS_GATES_OPEN=8
GATES_CLOSED_BY_THIS_PLAN=0
P0_TECHNICALLY_READY=false
P0_EXECUTION_READY=false
P0_EXECUTION_AUTHORIZED=false
FIXTURE_CREATED=false
RUNTIME_CREATED=false
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
MAINLINE_DRIFT_STATUS=CONTAINED_BY_THIN_CLOSURE_LEDGER
PROGRAM_MAINLINE_CHANGED=false
NEXT_ACTION=HUMAN_REVIEW_OF_CLOSURE_PLAN
```
