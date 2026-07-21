# SAEE Minimal Observation Recovery Plan

## Recover from Goal Drift Without Creating Another Governance Layer

```text
plan_id=SAEE-MINIMAL-OBSERVATION-RECOVERY-20260716-V1.0
plan_date=2026-07-16
plan_type=RECOVERY_PLAN_ONLY
source_self_audit=reports/SAEE_SELF_GOAL_INTEGRITY_AUDIT.md
source_self_audit_sha256=9c9b3fff1c884cf06d67763d602b1199338a82d9958340543cb8ec29bb2fbe9e
program_mainline=saee_agent_evidence_integration
research_lane=goal_integrity_p0_secondary_paused
```

## Executive Decision

The internal trajectory is preserved as the first real-world **Goal Drift observation candidate**, not as SAEE's first validated Goal
Integrity case. Recovery returns to the D6 last-known-valid state, pauses the full benchmark and all later governance work, and asks only
whether this one historical case can be examined truthfully with existing SAEE Evaluation semantics.

```text
SAEE_GOAL_INTEGRITY_PILOT_STATUS=PAUSED_AFTER_SELF_AUDIT
RESEARCH_FINDING=REAL_WORLD_GOAL_DRIFT_OBSERVATION_CANDIDATE_IDENTIFIED
FIRST_REAL_VALIDATION_CASE=false
P0_BENCHMARK=NOT_EXECUTED
MINIMAL_OBSERVATION_EXECUTED=false
```

# 0. Commander Check and Required Claim Correction

```text
COMMANDER_COMMAND_CHECK=PASS_WITH_CLAIM_CORRECTION
VALIDATION_CLAIM_INFLATION_DETECTED=true
CURRENT_EVALUATOR_SCOPE_MISMATCH_DETECTED=true
GOVERNANCE_RECURSION_RISK=true
MAINLINE_DRIFT_DETECTED=true
```

The case is real because the collaboration trajectory actually occurred. It is not yet a validation case because：

- it was identified and labeled after the trajectory was observed；
- the self-audit was not independent or blinded；
- `saee.evaluate_agent_run` was not invoked；
- the current evaluator does not implement longitudinal Goal Drift classification.

The existing Capability contract states：

```text
capability=saee.evaluate_agent_run
input=VALIDATED_SAEE_REHEARSAL_RUN
assessment=SUPPORTED_OR_INSUFFICIENT_EVIDENCE
purpose=FIXED_EVIDENCE_ADEQUACY
arbitrary_external_trace_supported=false
goal_drift_classifier_implemented=false
```

Therefore a future `HUMAN_REVIEW_REQUIRED` output could support Evidence readiness review, but it cannot by itself prove that SAEE detected
scope expansion or Goal substitution.

```text
MAINLINE_DRIFT_STATUS=CONTAINED_BY_PAUSING_SECONDARY_RESEARCH_LANE
PROGRAM_MAINLINE_CHANGED=false
```

# 1. Original Goal

```text
ORIGINAL_GOAL=VALIDATE_EVIDENCE_BASED_AGENT_EVALUATION_WITH_A_MINIMAL_OBSERVATION
ORIGINAL_SCOPE=ONE_BOUNDED_OBSERVATION_BEFORE_ANY_NEW_SYSTEM
ORIGINAL_NON_GOAL=BUILD_GOAL_GOVERNANCE_OR_STATE_INTEGRITY_INFRASTRUCTURE
```

The desired evidence is modest：whether existing SAEE Evaluation contributes useful, bounded decision context for an observed Agent run.
It is not proof that SAEE solves long-horizon drift.

# 2. Drift Onset and Last Known Valid State

```text
LAST_KNOWN_VALID_STATE=PHASE_8_0_D6_EXECUTION_READINESS_REVIEW
LKV_ARTIFACT=reports/SAEE_GOAL_INTEGRITY_PILOT_EXECUTION_READINESS_REVIEW.md
LKV_ARTIFACT_SHA256=af1e2450adea340b4435e960a3066e458736ab8f4f8b240f01dc4a4d861c371a
DRIFT_ONSET=PHASE_8_0_D6_1_CLOSURE_PLAN
DRIFT_THRESHOLD_CROSSED=PHASE_8_0_D6_2_EVIDENCE_ROOT_INITIALIZATION_PLAN
```

D6 is the recovery anchor because it accurately reported `NOT_READY` without pretending the experiment had run. Recovery does not mean
executing the nine-gate closure project. It means restoring the original decision：is one truthful observation possible and useful?

# 3. Minimal Recovery Scope

The recovered scope contains one historical case and one applicability question：

```text
case_id=SAEE-SELF-DRIFT-CASE-0
case_source=EXISTING_CONVERSATION_AND_REPOSITORY_REPORT_LINEAGE
new_fixture_required=false
new_runtime_required=false
new_schema_required=false
new_capability_required=false
new_mcp_required=false
```

## 3.1 Case-0 facts

```text
original_goal=execute_minimal_SAEE_Evaluation_validation
observed_sequence=D6 -> D6.1 -> D6.2 -> D6.3/D6.4/D6.5 -> Final Gate -> Authorization Record -> HG-2 Request
observed_outcome=governance_artifacts_created_while_primary_observation_remained_unexecuted
human_diagnosis=locally_rational_expansion_became_operational_goal_substitution
```

## 3.2 Only allowed research question

> Can the existing SAEE Evaluation contract consume a truthful representation of Case-0, without inventing a rehearsal run or changing
> evaluator semantics, and provide incremental Evidence-readiness context useful to Human review?

This question is narrower than “Can SAEE detect Goal Drift?”

## 3.3 Applicability stop rule

Current contract inspection indicates the historical collaboration trace is not a validated SAEE rehearsal run and the output contract is not
a Goal Drift classifier：

```text
CURRENT_CONTRACT_APPLICABILITY_FOR_GOAL_DRIFT_CLASSIFICATION=NOT_APPLICABLE
CURRENT_CONTRACT_APPLICABILITY_FOR_DECLARED_EVIDENCE_READINESS=UNRESOLVED_REQUIRES_TRUTHFUL_INPUT_REVIEW
```

If truthful input requires a new Schema, adapter, Capability, reinterpretation of `rehearsal_run`, or fabricated trace/evidence binding,
Case-0 stops as `CURRENT_EVALUATOR_NOT_APPLICABLE`. Recovery does not authorize building the missing layer.

# 4. What Leaves the Active Path

“Discard” means remove from the active execution path, not delete history：

- pause the 28-run Goal Integrity P0 benchmark；
- do not continue D6.1 closure, G0–G8 or HG-2 authorization chains；
- do not create Evidence Root, fixture, runtime, annotations or randomization for this recovery；
- do not add Goal Object, Goal Transition, Authority or Recovery implementation；
- do not create a self-governance product or State Integrity Engine；
- discard the claim that Case-0 is already a validated SAEE case；
- discard any plan to treat manual `HUMAN_REVIEW_REQUIRED` mapping as actual tool output.

```text
FULL_P0_ACTIVE=false
HG2_ACTIVE=false
NEW_GOVERNANCE_DOCUMENT_CHAIN_ALLOWED=false
```

# 5. What Is Preserved

Preserve without rewriting：

- D5 preregistration as the unexecuted full-study design；
- D6 readiness review as the LKV；
- D6.1 onward as the observed drift trajectory；
- `SAEE_SELF_GOAL_INTEGRITY_AUDIT.md` as a post-hoc internal diagnosis；
- all hashes, false statuses, warnings and negative states；
- the constitutional distinction between mainline and secondary research.

```text
HISTORY_DELETED=false
HISTORICAL_REPORTS_REWRITTEN=false
P0_RESULT=NO_RESULT_NOT_EXECUTED
```

# 6. Future Minimal Observation, If Separately Chosen

This plan does not execute the observation. A later Human decision may allow at most one local, offline, no-retry applicability observation：

1. freeze one read-only Case-0 fact packet derived only from existing artifacts；
2. verify whether it satisfies the current `rehearsal_run` input contract without fabrication；
3. if not, record `CURRENT_EVALUATOR_NOT_APPLICABLE` and stop；
4. if yes, invoke existing `saee.evaluate_agent_run` once without code, Schema, MCP or evaluator change；
5. preserve the exact request/response；
6. ask whether its Evidence gaps improve Human review；
7. stop after the single observation.

Allowed outcomes：

```text
CURRENT_EVALUATOR_NOT_APPLICABLE
NO_INCREMENTAL_DECISION_VALUE
PARTIAL_EVIDENCE_READINESS_VALUE
```

`GOAL_DRIFT_DETECTED_BY_SAEE` is not an allowed outcome because the current contract does not support that claim.

# 7. Stop Conditions

Stop recovery immediately if：

- a new governance gate or authorization-record family is proposed；
- Case-0 requires a new Capability, Schema, Protocol, MCP or evaluator rule；
- conversation history is rewritten into a synthetic “validated rehearsal run” without contractual basis；
- the Human post-hoc label is presented as ground truth validated by SAEE；
- more than one case, one invocation or one attempt is proposed；
- the workstream again displaces the constitutional integration mainline；
- a product, customer, production or enterprise claim is inferred.

# 8. Recovery Decision

```text
RECOVERY_RECOMMENDATION=CONDITIONAL_MINIMAL_OBSERVATION
CONDITION=TRUTHFUL_REUSE_OF_EXISTING_EVALUATOR_CONTRACT_WITHOUT_SEMANTIC_STRETCH
DEFAULT_IF_CONDITION_FAILS=STOP_SECONDARY_LANE
```

This preserves the value of the real trajectory while preventing it from becoming an excuse to build the missing State Engine.

# 9. Non-Claims

This plan does not claim：

- Case-0 has been evaluated by SAEE；
- SAEE detected Goal Drift；
- the Human post-hoc classification is independent ground truth；
- `saee.evaluate_agent_run` accepts arbitrary conversation traces；
- a fixture, runtime, Evidence Root, annotation or experiment exists；
- the full P0 is invalid, executed or completed；
- Goal Integrity is a current product Capability；
- a new product, architecture, Schema, Protocol, MCP or evaluator is needed or authorized；
- Goal Integrity replaced the SAEE / Agent Evidence integration mainline；
- customer validation, commercial validation or production readiness exists.

# 10. Final Status

```text
MINIMAL_OBSERVATION_RECOVERY_PLAN_STATUS=COMPLETE
SAEE_GOAL_INTEGRITY_PILOT_STATUS=PAUSED_AFTER_SELF_AUDIT
RESEARCH_FINDING=REAL_WORLD_GOAL_DRIFT_OBSERVATION_CANDIDATE_IDENTIFIED
FIRST_REAL_VALIDATION_CASE=false
LAST_KNOWN_VALID_STATE=PHASE_8_0_D6_EXECUTION_READINESS_REVIEW
P0_BENCHMARK=NOT_EXECUTED
FULL_P0_ACTIVE=false
MINIMAL_OBSERVATION_AUTHORIZED=false
MINIMAL_OBSERVATION_EXECUTED=false
SAEE_EVALUATOR_CALLED=false
SAEE_MCP_INVOKED=false
NEW_EXTERNAL_MODEL_INVOCATION=false
EVIDENCE_ROOT_CREATED=false
FIXTURE_CREATED=false
RUNTIME_CREATED=false
ANNOTATION_CREATED=false
EXPERIMENT_EXECUTED=false
NEW_CAPABILITY_CREATED=false
SCHEMA_CREATED=false
PROTOCOL_CREATED=false
MCP_CHANGED=false
SKILL_CHANGED=false
CODE_CHANGED=false
MAINLINE_DRIFT_DETECTED=true
MAINLINE_DRIFT_STATUS=CONTAINED_BY_PAUSING_SECONDARY_RESEARCH_LANE
PROGRAM_MAINLINE_CHANGED=false
NEXT_ACTION=HUMAN_REVIEW_OF_MINIMAL_OBSERVATION_RECOVERY_PLAN
```
