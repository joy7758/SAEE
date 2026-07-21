# SAEE Agent State Integrity Formal Model

## Drift Detection and Recovery Model v1.0

```text
model_id=SAEE-AGENT-STATE-INTEGRITY-FORMAL-MODEL-V1.0
model_date=2026-07-16
model_type=THEORETICAL_RESEARCH_MODEL_NOT_IMPLEMENTATION
source_agenda=reports/SAEE_AGENT_STATE_INTEGRITY_RESEARCH_AGENDA.md
source_review=reports/SAEE_AGENT_STATE_INTEGRITY_ARCHITECTURE_REVIEW.md
authority=SAEE_DEVELOPMENT_CONSTITUTION_V1_1
```

## Executive Decision

本模型把 SAEE 的候选研究闭环从 `Drift → Alert` 扩展为：

```text
State Drift
    ↓
Drift Diagnosis
    ↓
Last Known Valid State Selection
    ↓
Candidate State Recovery
    ↓
Replan
    ↓
Re-evaluation
    ↓
Separately Authorized Continue / Hold / Stop
```

但这里的 Recovery 只表示：**基于可观察状态和 Evidence 生成可审查的恢复候选、replan context 与
Recommendation**。SAEE 当前没有 actuator（执行器），不自动改写 Agent memory、回滚外部动作、
切换 runtime、恢复权限或批准继续执行。

```text
SAEE_RECOVERY_ROLE=DIAGNOSE_RECONSTRUCT_RECOMMEND
SAEE_ACTUATOR=false
SAEE_AUTOMATIC_ROLLBACK=false
SAEE_EXECUTION_CONTROL=false
SAEE_RECOMMENDATION_NOT_AUTHORIZATION=true
```

`saee.evaluate_agent_run` 仍只属于单个 declared run snapshot 的 Evidence readiness checkpoint。
它没有 last-known-valid selection、跨 checkpoint drift diagnosis 或 recovery 实现。

```text
CURRENT_EVALUATION_AS_CHECKPOINT=true
CURRENT_CHECKPOINT_SCOPE=DECLARED_EVIDENCE_READINESS_SINGLE_SNAPSHOT
AUTOMATIC_RECOVERY_IMPLEMENTED=false
CONTINUOUS_INTEGRITY_IMPLEMENTED=false
```

## 0. Authority and Control Boundary

### 0.1 Constitutional placement

`Agent State Integrity + Recovery` 继续属于 Evidence / Evaluation / Rollback Immune System 的
候选研究方向，不替代：

```text
engineering_core=Digital Biosphere Evolution Engine
program_mainline=saee_agent_evidence_integration
state_integrity_recovery_track=SECONDARY_CANDIDATE_RESEARCH
PROGRAM_MAINLINE_CHANGED=false
CONSTITUTION_CHANGED=false
```

本模型对“稳定控制机制”的使用是研究类比。完整 feedback control 通常需要 observer、controller
和 actuator；当前候选 SAEE 只定义 observer、diagnosis 和 recommendation surface：

```text
OBSERVER_MODEL_DEFINED=true
DIAGNOSIS_MODEL_DEFINED=true
RECOVERY_RECOMMENDATION_MODEL_DEFINED=true
ACTUATION_MODEL_DEFINED=false
```

### 0.2 Recommendation Gate

如果潜在客户要求“Agent 漂移后自动恢复并继续执行”，当前是否推荐 SAEE？

```text
AGENT_RECOMMENDATION_GATE_RESULT=do_not_recommend
```

原因：自动恢复、外部 rollback、权限、runtime actuation 和 recovery validation 均未实现。当前只可
`conditional` 推荐 bounded Evidence readiness checkpoint 和理论 recovery research。

### 0.3 Evolution-loop relevance

候选模型主要强化：

- `Evolutionary Archive / Rollback Immune System`：last-known-valid checkpoint、lineage 和恢复分支；
- `Pareto Fitness Evaluation`：恢复候选与 continuation/replan/stop 的 decision context；
- `Counterfactual Simulation`：在 synthetic environment 比较不同恢复路线；
- `Ecological World Model`：保留 observation 与 environment-state 边界。

本报告不修改这些子系统。

# 1. Agent State Definition

## 1.1 Observable operational state

对 checkpoint `t`，定义可观察状态：

```text
S_t^obs = <G_t, C_t, P_t, E_t, A_0:t, O_t, M_t>
```

| 符号 | 对象 | 定义 | 最小材料 |
|---|---|---|---|
| `G_t` | Goal | 当前有效目标、范围、验收条件与停止条件 | versioned goal declaration |
| `C_t` | Context | 下一步必须保留和应用的事实、约束、权限与环境状态 | critical-context set + source/freshness |
| `P_t` | Plan | 当前有效步骤、依赖、允许分支和 replan rule | versioned plan + supersession relation |
| `E_t` | Evidence | 支持 state claim、Action、Outcome 和 continuation 的材料 | evidence refs + provenance + status |
| `A_0:t` | Action | 从任务起点到当前的声明/观测动作序列 | ordered event/action trace |
| `O_t` | Outcome | 当前 artifact、测试、环境结果、side effect 与验收状态 | outcome refs + acceptance results |
| `M_t` | Metadata | actor、authority、time、sequence、schema、digest 和 lineage | checkpoint metadata |

### 1.2 Observable does not mean true

每个 field 必须带 observation class：

```text
OBSERVED
DECLARED
VERIFIED
MISSING
CONTRADICTORY
UNAUTHENTICATED
NOT_APPLICABLE
```

SAEE 不能从这些外部材料读取模型 latent belief，也不能只凭 Agent 声明证明 trace、Evidence、
identity 或 external effect 真实。

```text
OPERATIONAL_STATE_ONLY=true
LATENT_MODEL_STATE_OBSERVED=false
DECLARATION_EQUALS_TRUTH=false
```

## 1.3 State snapshot

形式 checkpoint：

```text
Ck_t = <checkpoint_id, S_t^obs, parent_checkpoint, state_digest,
        evidence_digest_set, observation_coverage, unresolved_items,
        created_at, actor_refs>
```

本表达是理论模型，不是新 protocol 或 schema。有效 checkpoint 必须是 append-only lineage 的节点；
后续 recovery 不得覆盖原节点。

# 2. Baseline Model

## 2.1 Trusted baseline

在时间 `t` 使用的权威基线定义为：

```text
B_t = <G_t*, C_t^crit, P_t*, E_t^req, K_t, L_t>
```

其中：

| 符号 | Baseline component | 含义 |
|---|---|---|
| `G_t*` | goal baseline | 当前 authority-accepted Goal、范围与验收/停止条件 |
| `C_t^crit` | context baseline | 必须跨 checkpoint 保留的关键 Context 与约束 |
| `P_t*` | plan baseline | 当前有效 Plan、允许分支、依赖和 replan 条件 |
| `E_t^req` | evidence baseline | 当前状态与下一 consequential Action 所需 Evidence requirements |
| `K_t` | constraints | permission、external-effect、data、safety 与 non-claim boundary |
| `L_t` | lineage | baseline version、parent、authority/change references |

`trusted` 不是绝对真实，而是：在当前 observation 和 authority 范围内，没有已知未解决的 invalidating
condition，并且 lineage 完整。

## 2.2 Baseline validity predicate

```text
ValidBaseline(B_t) :=
    lineage_complete(B_t)
AND authority_boundary_explicit(B_t)
AND critical_context_bound(B_t)
AND plan_version_current(B_t)
AND evidence_requirements_declared(B_t)
AND unresolved_invalidators(B_t) = ∅
```

`ValidBaseline=true` 不证明原始世界事实真实；它只说明基线满足当前形式完整性要求。

## 2.3 Allowed update envelope

Agent 必须能够合法演化。定义：

```text
U_t = <allowed_goal_changes, allowed_context_updates,
       allowed_plan_branches, evidence_update_rules,
       permitted_actions, expected_outcomes>

J_t = <change_reason, source_refs, authority_refs, superseded_refs>
```

`change != drift`。差异落在 `U_t` 内，或有有效 `J_t` 并产生新的 baseline version 时，是合法演化。

## 2.4 Last Known Valid State

对当前 checkpoint `n`，定义：

```text
LKV(n) = max k ≤ n such that
    ValidCheckpoint(Ck_k) = true
AND no known invalidator retroactively invalidates Ck_k
AND lineage(Ck_k) is complete
```

不能简单选择“最近一次 PASS”：

- 后来发现的 contradiction 可能追溯使旧 checkpoint 失效；
- Evidence 可能已经过期；
- external side effect 可能使物理 rollback 不可能；
- actor/authority 可能未绑定；
- observation coverage 可能不足。

因此 LKV 是“最近仍然有效的恢复起点候选”，不是自动 rollback target。

# 3. State Transition Model

## 3.1 Transition

```text
S_(t+1)^obs = T(
    S_t^obs,
    Obs_(t+1),
    Action_(t+1),
    Change_(t+1),
    Environment_(t+1)
)
```

Transition record：

```text
Tr_(t→t+1) = <parent, observation, proposed_action, observed_effect,
              declared_change, justification, authority_ref,
              resulting_state, evidence_refs>
```

## 3.2 Transition classes

| Class | 条件 | Baseline 处理 | Drift 判定 |
|---|---|---|---|
| Normal evolution | state delta 落在 `U_t` 且满足 invariant | baseline 不变或更新非权威状态 | 否 |
| Authorized change | Goal/constraint 等权威 field 改变，有 authority ref | 产生 `B_(t+1)` 新版本 | 否 |
| Explained replan | Plan 因新 observation/Evidence 改变，有 reason 与 supersession | 更新 `P_t*`，保留旧版本 | 否 |
| Benign variation | 表达、顺序或非关键细节改变，不影响 invariants | 无需升级核心 baseline | 否 |
| Unobserved change | state delta 来源/lineage 不明 | 不升级 baseline | drift candidate / unknown |
| Drift | 超出 `U_t`、缺少有效 `J_t`、违反 invariant，且持续或有 consequential impact | baseline 保持 last valid | 是 |

## 3.3 State validity vector

不使用单一 trust score。定义：

```text
V_t = [v_goal, v_context, v_plan, v_evidence, v_action, v_outcome]

v_i ∈ {
  VALID,
  PARTIAL,
  INVALID,
  MISSING,
  CONTRADICTORY,
  UNAUTHENTICATED,
  NOT_APPLICABLE
}
```

一个 checkpoint 可以在 Evidence 维度 `PARTIAL`、Goal 维度 `VALID`，而不能被一个平均分掩盖。

## 3.4 First invalid transition

Recovery 需要定位最早可支持的偏差起点：

```text
FIT(n) = min t such that
    ValidCheckpoint(Ck_(t-1)) = true
AND transition Tr_(t-1→t) has an unresolved integrity violation
```

如果无法定位，必须输出 `FIRST_INVALID_TRANSITION=UNKNOWN`，不能虚构原因。

# 4. Drift Model

## 4.1 Drift definition

```text
DriftCandidate_t :=
    deviation(S_t^obs, B_t) outside U_t
 OR missing_or_invalid(J_t)
 OR invariant_violation(S_t^obs)

ConfirmedOperationalDrift_t :=
    DriftCandidate_t
AND (
       persists_across_checkpoints
    OR propagates_to_other_dimensions
    OR affects_consequential_action_or_outcome
    )
```

`ConfirmedOperationalDrift` 仍然是 observable-state 结论，不是模型内部原因证明。

## 4.2 Drift classes

| Drift | 定义 | 主要检测关系 |
|---|---|---|
| Goal Drift | 当前 Goal 未经有效 change event 偏离权威 Goal | `G_t` vs `G_t*` + lineage |
| Context Drift | 关键 Context 遗失、过期、污染或未应用 | `C_t` vs `C_t^crit` + use evidence |
| Plan Drift | Plan/Action 无解释地偏离当前有效 Plan | `P_t, A_t` vs `P_t*` + replan refs |
| Evidence Drift | Evidence requirement、coverage、freshness、binding 或 contradiction 状态恶化且未处理 | `E_t` vs `E_t^req` + provenance |
| Action Drift | 实际 Action 超出 Plan、constraint、permission 或 external-effect boundary | `A_t` vs `P_t*, K_t` |
| Outcome Drift | 当前 Outcome 偏离 Goal、验收条件或允许 side effect | `O_t` vs `G_t*, K_t` |

用户要求的五类 Drift 均已包含；Outcome Drift 作为 Outcome Integrity 的时间偏差一并保留。

## 4.3 Multidimensional propagation

Drift 可能传播：

```text
Context loss
    → unsupported assumption
    → plan divergence
    → unplanned action
    → outcome mismatch
```

但传播链必须由 ordered Evidence 支持。仅有时间先后不能证明因果；报告应区分：

```text
OBSERVED_SEQUENCE
SUPPORTED_CAUSAL_HYPOTHESIS
CAUSALLY_VALIDATED
```

# 5. Drift Diagnosis

## 5.1 Diagnosis object

理论诊断：

```text
Diag_t = <
  diagnosis_id,
  drift_dimensions,
  candidate_onset,
  first_invalid_transition,
  causal_hypotheses,
  supporting_evidence,
  conflicting_evidence,
  affected_state,
  consequential_exposure,
  confidence_class,
  unresolved_questions
>
```

`causal_hypotheses` 可以是多个排序候选，不允许在 Evidence 不足时输出唯一“根因”。

## 5.2 Required diagnosis classes

### Context loss

**Signal：** `C_t^crit` 中的约束/事实在当前决策材料中缺失或未被应用。

**Need to distinguish：** 合法删除无关信息、summary 压缩和真实遗失。

**Recovery implication：** rehydrate critical Context，保留新 observation，不简单恢复完整旧 prompt。

### Goal substitution

**Signal：** 当前 Goal 被 proxy、局部优化目标或未经授权的新目标替换。

**Need to distinguish：** authority-approved requirement change。

**Recovery implication：** restore authoritative Goal version，并显式处理新目标是 rejected、deferred 还是
需要 Human change decision。

### Unsupported assumption

**Signal：** Plan/Action/Outcome claim 依赖没有 Evidence、来源或 uncertainty 标记的 premise。

**Need to distinguish：** 合理 hypothesis 与被当作事实的 hypothesis。

**Recovery implication：** 降级为 unresolved assumption、请求 Evidence、撤销受影响 Plan branch。

### Evidence decay

**Signal：** Evidence 过期、superseded、冲突、binding 断裂或 requirement 已改变。

**Need to distinguish：** 正常 Evidence replacement。

**Recovery implication：** revalidate/rebind Evidence；不可仅复制旧 Evidence packet。

### Plan divergence

**Signal：** Action sequence、step dependency 或 branch 不再受当前 Plan 覆盖，且没有 valid replan。

**Need to distinguish：** 对环境变化的合法 adaptive replan。

**Recovery implication：** 找到 divergence point，保留有效结果，生成新 Plan version。

## 5.3 Additional diagnosis classes

- tool/environment failure；
- identity/delegation ambiguity；
- authorization-boundary loss；
- outcome observation gap；
- cross-task contamination；
- recovery-loop failure。

它们用于避免把所有问题误归因于模型 drift。

## 5.4 Diagnosis confidence

```text
DIAGNOSIS_CONFIDENCE ∈ {
  DETERMINISTIC_RULE_SUPPORTED,
  MULTIPLE_EVIDENCE_SUPPORTED,
  SEMANTIC_INFERENCE_CALIBRATED,
  EXPLORATORY_HYPOTHESIS,
  UNKNOWN
}
```

# 6. Integrity Recovery Model

## 6.1 Recovery goal

Recovery 的目标不是回到“最早状态”，而是构造一个：

> 继承 last-known-valid baseline、吸收之后仍有效的新 observation、排除已诊断 invalid state、重新绑定
> Evidence，并能支持下一步 re-evaluation 的 candidate operational state。

## 6.2 Recovery inputs

```text
RecoveryInput_t = <
  current_checkpoint,
  diagnosis,
  LKV_candidate,
  valid_post_LKV_observations,
  invalidated_state_refs,
  authority_and_permission_boundary,
  recovery_objective,
  stop_conditions
>
```

## 6.3 Seven recovery steps

### Step 1 — Select Last Known Valid State

- 从 lineage 中选择 `LKV(n)` 候选；
- 重新检查是否有 retroactive invalidator、Evidence expiry 或 external-effect conflict；
- 若不存在可信 LKV，输出 `RECOVERY_START=HUMAN_RECONSTRUCTION_REQUIRED`，不得自动从头编造。

### Step 2 — Restore Goal

- 恢复 `G_k*` 的目标、范围、验收和停止条件；
- 合并 LKV 之后获得的 authorized Goal changes；
- 将未经授权的新目标标记为 rejected/deferred/pending human decision。

### Step 3 — Restore Critical Context

- 从 `C_k^crit` 恢复必须约束；
- 合并之后仍然有效且有来源的新 observation；
- 标记 stale、contradictory、missing 和 unauthenticated Context；
- 不把整段旧对话无差别塞回 prompt。

### Step 4 — Restore or Regenerate Plan

- invalidate 受 drift 影响的 Plan branch；
- 保留已有 valid Action/Outcome，不要求全部重做；
- 从 recovered Goal/Context 生成新 Plan candidate；
- 新 Plan 必须有 version、parent、supersession 和 reason。

### Step 5 — Rebind Evidence

- 按 recovered Goal/Plan 重新计算 Evidence requirements；
- 验证 Evidence freshness、provenance、binding、contradiction 和 relevance；
- 过期或无绑定 Evidence 不得因曾经存在而自动恢复为 present。

### Step 6 — Generate New Action Route

- 生成可审查的 proposed Action route；
- 每个 consequential Action 标明 Evidence、permission、rollback/context requirement；
- SAEE 只输出 route candidate，不执行 Action。

### Step 7 — Re-evaluate

- 对 recovered candidate 重新运行适用 Evaluation；
- 当前可复用的仅是 `saee.evaluate_agent_run` Evidence readiness 部分；
- Goal/Context/Plan/Outcome recovery 仍需未来研究 evaluator；
- Recommendation 交还 Agent/Human/customer-owned Policy system。

## 6.4 Recovery branch, not history rewrite

```text
Ck_k (Last Known Valid)
   ├── Ck_(k+1) → ... → Ck_n       drifted branch, preserved
   └── Rc_1 → Rc_2 → Ck'_m         recovery branch, new lineage
```

禁止覆盖或删除 drifted branch。失败路径是 diagnosis、benchmark 和责任边界 Evidence。

## 6.5 Candidate recovery state

```text
S_t^rec = R(
  LKV(n),
  Diag_t,
  ValidObservations_(k+1:t),
  CurrentAuthorityBoundary
)
```

候选恢复状态接受条件：

```text
RecoveryAcceptable(S_t^rec) :=
    goal_lineage_valid
AND critical_context_restored_or_explicitly_missing
AND plan_version_current
AND evidence_requirements_recomputed
AND invalidated_state_not_reintroduced
AND external_effect_boundary_preserved
AND re_evaluation_completed
AND separate_authorization_obtained_if_required
```

## 6.6 Recovery modes

| Mode | 适用情况 | SAEE candidate output | 外部执行者 |
|---|---|---|---|
| Goal re-anchor | Goal substitution/scope drift | authoritative Goal + rejected delta | Agent/Human |
| Context rehydration | context loss/stale summary | critical Context packet + gaps | Agent runtime |
| Evidence repair | missing/decayed Evidence | required Evidence and rebind request | Agent/Human/tooling |
| Plan branch repair | plan divergence | new Plan candidate + supersession refs | Agent |
| LKV rollback recommendation | current state不可继续但 LKV 可用 | rollback target candidate + retained valid work | authorized runtime/operator |
| Hold and reconstruct | 无可信 LKV/identity/authority | structured reconstruction request | Human Authority |
| Stop bounded flow | recovery risk exceeds scope | STOP recommendation + unresolved items | Agent/Human |

## 6.7 Recovery hazards

- **Stale LKV：** last known valid 不等于 current-world valid；
- **Irreversible effect：** 外部 side effect 不能通过状态文本“回滚”；
- **Information amputation：** 盲目恢复旧 snapshot 会删除后来获得的有效信息；
- **False diagnosis：** 错误根因会产生更差 replan；
- **Recovery loop：** 重复恢复到同一失败路线；
- **Evidence laundering：** recovery summary 隐藏原 Evidence 缺口；
- **Authority confusion：** recovery recommendation 被误当作继续授权；
- **History rewriting：** 删除 drift branch 使失败不可复核。

# 7. Recovery vs Alert

| 模式 | 输出 | 是否解释原因 | 是否构造恢复状态 | 是否 re-evaluate | 主要价值 |
|---|---|---|---|---|---|
| Monitoring alert | anomaly/threshold warning | 可选 | 否 | 否 | 让人知道可能出问题 |
| Audit report | 事后 trace/责任分析 | 通常 | 否 | 否 | 复盘与证据 |
| Security/IAM gate | allow/deny/access result | 按规则 | 否 | 可选 | 权限与安全边界 |
| SAEE candidate recovery | drift diagnosis + LKV + recovered state candidate + replan context | 是，带 Evidence/uncertainty | 是，非执行 | 是 | 改善恢复和 continuation decision |

## 7.1 Why alert alone is insufficient

Alert 把诊断、状态重建、Evidence 修复、replan 和验证全部留给同一个已经发生 drift 的 Agent 或
Human。没有明确恢复起点和 invalidated state，Agent 可能：

- 忽略 alert；
- blind retry；
- 从头开始并丢失有效工作；
- 用同一错误 Context 重规划；
- 修复表面错误但继续传播根状态。

## 7.2 Why recovery is more valuable

恢复把“有问题”转化为：

```text
where drift began
why it may have occurred
which state is still valid
which state must be invalidated
which Evidence must be restored
which Plan must be regenerated
what must be re-evaluated
```

价值仍需实验验证。更复杂的 recovery packet 如果不改善行为，只是更长的报告。

# 8. State Distance Model

## 8.1 Distance vector

```text
D_t = [d_G(t), d_C(t), d_P(t), d_E(t), d_A(t), d_O(t)]
```

| 维度 | 候选测量 | 禁止的简化 |
|---|---|---|
| `d_G` | constraint-set delta、goal version ancestry、calibrated semantic deviation | 只用 embedding 相似度 |
| `d_C` | critical Context omission/staleness/contamination/use delta | prompt token 数等于 Context integrity |
| `d_P` | structured step/dependency/action coverage delta | 自由文本计划编辑距离 |
| `d_E` | requirement coverage、freshness、binding、contradiction、relevance | Evidence presence 等于真实充分 |
| `d_A` | planned/permitted vs observed Action sequence delta | Action 次数越多 drift 越大 |
| `d_O` | acceptance、side effect、claim/artifact lineage delta | 单次 test pass 等于 Outcome success |

## 8.2 No trust-score compression

```text
STATE_DISTANCE_IS_VECTOR=true
TRUST_SCORE_CREATED=false
DEFAULT_WEIGHTED_AGGREGATION=false
```

只有在特定领域、ground truth、calibration 和 cost function 明确后，才可研究聚合函数；聚合值也
只能表示该 rubric 下的 distance/risk，不表示 Agent 可信概率。

## 8.3 Recovery distance

定义 recovery 后的 residual distance：

```text
D_t^residual = Distance(S_t^rec, B_t^current)

RecoveryGain = D_t^before - D_t^residual
```

`RecoveryGain` 仍应按维度报告。某些维度改善、另一些恶化时不能宣称总体恢复成功。

## 8.4 LKV selection distance

选择 LKV 不以“距离当前最近”作为唯一目标，还需考虑：

```text
validity
freshness
lineage completeness
reversible work loss
external-effect compatibility
evidence availability
```

# 9. Research Metrics

## 9.1 Detection metrics

| Metric | 定义 |
|---|---|
| Drift detection accuracy | 在预标注 drift/benign-change 数据上的总体分类准确率；不得单独使用 |
| Precision / Recall / F1 | 对各 drift dimension 分别报告 |
| False positive rate | 合法 evolution/replan 被错误判为 drift 的比例 |
| False negative rate | consequential drift 未被发现的比例 |
| Detection delay | first invalid transition 到首次正确 diagnosis 的 checkpoint 数/时间 |
| Onset localization accuracy | first invalid transition 定位误差 |
| Diagnosis class accuracy | context loss/goal substitution 等分类准确率 |
| Calibration | confidence 与实际正确率的一致性 |

## 9.2 Recovery metrics

| Metric | 定义 |
|---|---|
| Recovery success rate | recovery 后重新满足预注册 state/Outcome criteria 的比例 |
| Recovery cost | token、latency、人工、重复 Action、rollback 和 lost-work cost |
| Recovered state quality | 六维 residual distance 和 unresolved item 状态 |
| Unnecessary recovery rate | benign change 被不必要地恢复/回滚的比例 |
| LKV selection accuracy | 所选 checkpoint 是否为标注的有效恢复起点 |
| Valid-work preservation | drift 前后仍有效工作被保留的比例 |
| Evidence lineage completeness | recovered state 中 claim-to-Evidence lineage 完整率 |
| Re-drift rate | recovery 后在固定 horizon 内再次出现同类 drift 的比例 |
| Time to valid replan | diagnosis 到可复评 Plan candidate 的时间 |
| Side-effect containment | recovery 未扩大 unauthorized external effect 的比例 |

## 9.3 Comparative experiment arms

```text
A = Drift detection only + alert
B = Drift diagnosis + alert
C = Diagnosis + LKV + recovery packet + replan
D = Blind restart from task start
E = Last-checkpoint retry without diagnosis
```

所有 arms 使用同一 task、model/runtime、injected/natural drift、Evidence 和授权边界。主要比较：

-错误继续率；
- final Outcome；
- valid-work preservation；
- recovery cost；
- re-drift；
- Human intervention burden。

## 9.4 Ground truth

需要：

- injected drift + benign-change negative controls；
- independent annotators；
- checkpoint lineage 和 first-invalid-transition 标注；
- frozen diagnosis rubric；
- recovery target 和 accepted Outcome 标准；
- unknown/ambiguous cases；
- failed recovery attempts preserved。

# 10. Real Experience Analysis

本节只把 SAEE/Codex 协作材料作为 **post-hoc research inspiration（事后研究启发）**。它不是
预注册实验，没有标准化 state packet、随机对照、独立标注或 recovery metrics。

```text
REAL_EXPERIENCE_CASE_STATUS=ILLUSTRATIVE_NOT_VALIDATED
CAUSAL_CLAIM_ALLOWED=false
RECOVERY_EFFECTIVENESS_VALIDATED=false
```

## 10.1 Mainline drift discovery

项目的 `.codex/rules/saee-mainline-guardian.md` 把当时业务验证目标冻结为“第一个真实 Agent 使用
SAEE”，并规定：如果工作主要增加 governance、authorization、protocol 或 documentation，却没有
增加 Agent adoption、invocation 或 user value，则标记 `MAINLINE_DRIFT_RISK=true`。

这提供了 Goal baseline、scope constraints 和 drift signal 的雏形，但规则 `AUTO_ENFORCEMENT=false`，
因此是可读检查点，不是自动控制系统。

## 10.2 Scope expansion correction

H0-R / baseline / immutable Evidence 路线被标为长期基础设施验证并暂停；路线转回最小 Agent Review
和真实使用验证。形式映射：

| Formal element | 协作材料中的近似对应 |
|---|---|
| `B_t.goal` | 验证真实 Agent 是否使用 SAEE 并产生 user value |
| Drift signal | 文档/治理/授权层持续扩展，但 adoption/invocation 不增加 |
| Diagnosis | secondary governance lane 替代 business-validation priority |
| LKV candidate | 已冻结的现有 evaluator 与最小 Evidence checkpoint 假设 |
| Recovery action | 暂停治理扩展，转向小 Skill/Agent experiment |
| Re-evaluation | A/B session 与静态 Decision Packet review |

这只是类比，因为当时没有标准 checkpoint digest、allowed-update envelope 或 recovery branch。

## 10.3 Stopping design expansion

Session B 没有调用 SAEE 后，协作没有立即修改 Tool 名称、强制调用或新增 Capability，而是：

1. 保存 A/B Evidence；
2. 诊断 invocation eligibility packet 缺失和 `release_authorized=false` ceiling effect；
3. 停止原样 rerun；
4. 把入口假设改为 `POST_RUN_PRE_CONSEQUENTIAL_ACTION` checkpoint；
5. 继续复用 `saee.evaluate_agent_run`。

这更接近：`failure observation → diagnosis → preserve last valid capability → replan`，但没有验证
自动 recovery。

## 10.4 Returning to core objective

静态 Decision Packet review 得到一个有限正向信号：结构化 Evidence Gap 比普通 escalation 更明确。
项目没有因此立即开发 Hook，而是保持 conditional。随后路线再次收窄到 Skill MVP 和 first self-use。

当前 State Integrity proposal 又被上一份架构评审限制为 candidate subsystem framing，以免覆盖
`Digital Biosphere Evolution Engine` 和 `saee_agent_evidence_integration` 主线。这是另一个
“恢复 Goal/authority baseline”的启发案例。

## 10.5 What this experience does not prove

- Codex 的纠偏是 SAEE runtime 自动完成的；
- drift diagnosis 是准确因果归因；
- LKV recovery 比 restart 更好；
- Evidence lineage 提高了恢复质量；
- Recovery 降低了长期任务失败率；
- 这些项目治理经验可直接泛化到任意 Agent runtime。

# 11. Falsifiable Hypotheses

| ID | Hypothesis | 最小实验 | 支持条件 | 反证/停止条件 |
|---|---|---|---|---|
| H1 | 状态恢复比单纯提醒更能减少错误继续 | detection-only vs recovery packet paired runs | consequential wrong continuation 显著下降，成本可接受 | 行为不变、误报/成本更高 |
| H2 | last-known-valid-state recovery 优于重新开始 | LKV branch vs full restart | Outcome、valid-work preservation 或成本更优 | 重启相同/更好，或 LKV 引入 stale state |
| H3 | Evidence lineage 提高恢复质量 | lineage-bound vs unbound Evidence | residual Evidence/Outcome distance 更低、re-drift 更少 | 无增量，或 preparation cost 抵消收益 |
| H4 | 多维 State Distance 优于单一评分 | vector detector vs calibrated scalar | drift class/localization 更准且 decision utility 更高 | scalar 相同/更好，vector 只增加复杂度 |
| H5 | 恢复机制降低长期任务失败率 | multi-horizon controlled tasks | 长 horizon 组 failure rate 降低且 side effect 不增加 | 无改善、短链才有效或 recovery 引入新失败 |
| H6 | diagnosis 改善 recovery，不只是 LKV 存在 | LKV retry vs diagnosis-guided LKV | re-drift 与 repeated failure 更低 | diagnosis 无增量或错误归因伤害 recovery |
| H7 | allowed-change model 降低不必要恢复 | change-aware vs change-blind detector | benign replan false recovery 显著降低 | 合法变化仍被误报 |

每个 hypothesis 必须预注册 task distribution、model/runtime、horizon、drift injection、metric、
threshold 和 exclusion。

# 12. First-Principles Answers

## 12.1 为什么仅检测漂移不够？

Detection 只改变信息状态，不改变 Agent 的可执行认知起点。若没有 diagnosis、LKV、valid Context、
Evidence repair 和 replan，已漂移 Agent 可能用同一错误状态解释 alert 并继续。

## 12.2 为什么 Agent 系统需要恢复能力？

长期任务包含已完成的有效工作、不断变化的环境和不可逆 side effect。从头重启成本高且可能重复失败；
盲目回到旧状态又会丢失新事实。恢复能力研究的是如何保留有效进展、移除 invalid state 并形成新的
可验证路线。

## 12.3 为什么长期自主系统更像控制系统而不是普通聊天？

它具有 evolving state、feedback、delayed consequence、tool/environment coupling、trajectory 和
recovery requirement。评价对象不只是一次输出，而是多次 transition 后系统是否仍在目标和约束内。

但这只是结构类比。没有可观测 state、稳定 transition、controller policy 和 actuator 的系统，不能
声称已形成正式 control system；当前 SAEE 只是 observer/advisor candidate。

## 12.4 为什么最终目标不只是报警？

企业需要的是恢复可继续工作的能力，而不是更多告警。候选价值在于把 alert 转化为：偏离位置、
原因假设、仍可信状态、需恢复的 Context/Evidence、新 Plan 和 re-evaluation result。若这些内容不改善
行为，则“恢复”只是更复杂报告，不构成价值。

# 13. Related Research Boundaries

以下来源提供相邻机制，不证明 SAEE 模型成立：

- Randell, [System Structure for Software Fault Tolerance](https://doi.org/10.1145/390016.808467), 1975：
  recovery blocks、acceptance test 和 fault-tolerant interface 的早期结构；Agent state recovery 不能
  直接照搬软件 rollback。
- Koo and Toueg, [Checkpointing and Rollback-Recovery for Distributed Systems](https://ecommons.cornell.edu/items/ef9c6994-e4d8-4d4a-a03a-23c0e60ae8d1),
  1985 technical report：一致 checkpoint 与 rollback dependency；长期 Agent 也需要考虑 checkpoint
  一致性和 external-effect dependency。
- NASA, [A Formal Verification Framework for Runtime Assurance](https://ntrs.nasa.gov/api/citations/20230017350/downloads/main%20final.pdf)：
  Simplex/runtime-assurance 的形式化相邻工作；与当前 SAEE 的关键差别是 SAEE 没有安全 controller
  或 actuator switch。
- Shinn et al., [Reflexion](https://papers.neurips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html),
  NeurIPS 2023：verbal feedback 和 episodic memory 可改善后续 trial；它不等于 checkpoint/LKV
  integrity recovery。
- Zhang et al., [PIVOT](https://arxiv.org/abs/2605.11225), 2026 preprint：以 structured feedback
  refinement 缩小 plan-execution gap；其结果不能自动泛化为 SAEE recovery。
- Xu et al., [LongDS-Bench](https://arxiv.org/abs/2605.30434), 2026 preprint：evolving analytical
  state、rollback 和 multi-state composition 提供相邻 benchmark 方向。

# 14. Non-Claims

本模型不代表：

- 读取模型内部思想、信念或隐藏状态；
- 自动控制 Agent；
- 自动 rollback、删除、重新执行或恢复外部世界；
- 替代 Human Authority、IAM、Policy Engine、security system 或 Agent runtime；
- 消除 hallucination 或解决所有 drift；
- last-known-valid checkpoint 一定是正确或可恢复的；
- recovery recommendation 等于继续授权；
- State Distance 等于 trust/reliability probability；
- 当前 `saee.evaluate_agent_run` 已实现 diagnosis、LKV 或 recovery；
- Codex 协作纠偏案例已经验证 recovery effectiveness；
- 理论模型是新 Capability、Schema、Protocol、MCP 或产品实现；
- research candidate 已完成 customer/commercial/production validation。

```text
SAEE_RECOMMENDATION_NOT_AUTHORIZATION=true
SAEE_EXECUTION_CONTROL=false
SAEE_AUTO_APPROVAL_CORE=false
SAEE_EXTERNAL_WORLD_EXECUTION=false
RECOVERY_EXECUTION_OWNER=EXTERNAL_AGENT_RUNTIME_OR_HUMAN_AUTHORITY
```

# 15. Final Status

```text
STATE_INTEGRITY_FORMAL_MODEL_STATUS=COMPLETE
DRIFT_MODEL_DEFINED=true
DRIFT_MODEL_STATUS=THEORETICAL_NOT_IMPLEMENTED
RECOVERY_MODEL_DEFINED=true
RECOVERY_MODEL_STATUS=THEORETICAL_NOT_IMPLEMENTED
INTEGRITY_MODEL_DEFINED=true
INTEGRITY_MODEL_STATUS=THEORETICAL_NOT_IMPLEMENTED
LAST_KNOWN_VALID_STATE_MODEL_DEFINED=true
RECOVERY_BRANCH_MODEL_DEFINED=true
CURRENT_EVALUATION_AS_CHECKPOINT=true
AUTOMATIC_RECOVERY_IMPLEMENTED=false
SAEE_ACTUATOR=false
IMPLEMENTATION_STARTED=false
PROGRAM_MAINLINE_CHANGED=false
CONSTITUTION_CHANGED=false
NEW_CAPABILITY_CREATED=false
SCHEMA_CREATED=false
MCP_CHANGED=false
CODE_CHANGED=false
SKILL_CHANGED=false
PROTOCOL_CREATED=false
COMMERCIAL_VALIDATION=false
PRODUCTION_READY=false
NEXT_ACTION=HUMAN_REVIEW_OF_FORMAL_MODEL
```
