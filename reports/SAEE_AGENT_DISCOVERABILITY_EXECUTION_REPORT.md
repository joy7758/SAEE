# SAEE Agent Discoverability Execution Report

```text
phase=6.0-E2
report_type=External_Agent_Discoverability_Execution
execution_date=2026-07-15
active_constitution=SAEE_Development_Constitution_v1.1
canonical_packet=reports/SAEE_AGENT_DISCOVERABILITY_CANONICAL_PACKET.md
canonical_packet_version=0.1
canonical_packet_human_review_status=APPROVED
blocked_input_alignment_cleared=true
phase_6_0_e2_authorized=true
mainline_drift_detected=false
```

## 1. Executive Decision

Phase 6.0-E2 was actually executed against one external Agent family: ten fresh, independent,
ephemeral Codex CLI subject sessions, covering five scenario prompts and five boundary prompts.
The subject was given the approved packet's subject-visible identity, problem, capability, input,
output and non-claim content; evaluator-only expected labels were withheld.

The experiment meets the stated numeric gate, but only with material limitations:

- aggregate dimension score: `13.8/16`;
- dedicated Boundary Accuracy: `3.0/4`;
- Critical Misclassification: none;
- experiment threshold: `PASS_WITH_LIMITATIONS`;
- cross-provider or ecosystem-wide discoverability: **not established**.

The most important result is not the score. The subject consistently understood what SAEE is not,
but the packet did not produce stable negative-routing and label semantics. All five boundary answers
were substantively correct while using the opposite classification label from the hidden key. The
Customer and Procurement scenarios also diverged from their hidden routing labels.

```text
EXPERIMENT_THRESHOLD_RESULT=PASS_WITH_LIMITATIONS
CROSS_PROVIDER_VALIDATION=false
ECOSYSTEM_DISCOVERABILITY_VALIDATED=false
CAPABILITY_DESCRIPTION_OPTIMIZATION_AUTHORIZED=false
```

Passing this experiment does not establish an official OpenAI integration, public MCP availability,
customer validation, commercial validation or production readiness.

## 2. Authorization and Scope

Human authorization supplied for this run:

```text
CANONICAL_PACKET_HUMAN_REVIEW_STATUS=APPROVED
BLOCKED_INPUT_ALIGNMENT_CLEARED=true
PHASE_6_0_E2_AUTHORIZED=true
```

Execution stayed inside the approved experimental scope:

- no Constitution, Project Memory, capability inventory, schema, MCP implementation, Product
  Registry or code was changed;
- no Agent action, deployment, database deletion, infrastructure deletion, customer response or
  purchase was executed or authorized;
- no `git add`, `git commit`, `git push` or PR operation was performed;
- the only intended repository output is this report.

This discoverability experiment is a bounded Agent-native validation lane. It does not replace or
elevate itself above the constitutional SAEE / Agent Evidence Project integration mainline.

## 3. Inputs and Integrity

| Input | SHA-256 before execution |
|-|-|
| `reports/SAEE_AGENT_DISCOVERABILITY_CANONICAL_PACKET.md` | `489670444c509f345d9a2899b4e360177ef63d6d41216371bcd28ca06503c042` |
| `reports/SAEE_AGENT_DISCOVERABILITY_EXPERIMENT_REPORT.md` | `544f38387478f5d7e0509c6bfc0bf01269e330e22caa3394b3c8302d8a834d81` |
| `reports/SAEE_AGENT_DISCOVERABILITY_VALIDATION_PLAN.md` | `fa30078e06066f2b40118356c5ac9017e0531f533f812ff30782aff61554c063` |
| `capability-package/manifest.json` | `fda5f5a2dca0c79ef98f6cdf1f2a5be80b3a3e672eeec2a7a76e63bf1b25fa70` |

Repository baseline before subject execution:

```text
branch=feat/canonical-capability-inventory-routing-v1
head=f6ac41f4b068377e7778e8c3d83b99bd8382debc
preexisting_status_entries=98
target_report_preexisting=false
```

Subject projection details:

```text
projection_source_lines=105-329
projection_sha256=502ae42e6e713e7a7ba9fd6dbb7a1c45b9d5919d72518600435b9911832d7a3d
evaluator_only_content_delivered=false
hidden_expected_labels_delivered=false
extra_subject_visible_content=Section_8_heading_and_separate-run_instruction
```

The extra content was only the subject-visible `Five Scenario Prompts` heading and the instruction
to deliver scenarios separately. It contained no prompt answer, hidden label, scoring anchor or
critical-fail definition. This is recorded for byte-level audit rather than treated as a hidden-label
leak.

## 4. Actual External Agent Configuration

| Field | Observed value |
|-|-|
| Subject family | Codex CLI |
| CLI | `codex-cli 0.144.1` |
| Provider shown by CLI | `openai` |
| Model shown by CLI | `gpt-5.6-sol` |
| Subject sessions | 10 distinct ephemeral sessions |
| Work directory | `/tmp`, outside the SAEE repository |
| Sandbox | `read-only` |
| Approval mode | `never` |
| Workspace/rules context | ignored through `--ignore-user-config --ignore-rules` |
| Subject tool calls in responses | 0 |
| Actual SAEE MCP calls | 0; this phase tested invocation understanding |

The CLI necessarily used its provider connection, and its stderr also showed unsuccessful model,
plugin-catalog or analytics refresh attempts in some sessions. Therefore process-level network
isolation is not claimed. No plugin or tool result appeared in a subject answer.

```text
CODEX_CLI_TESTED=true
CHATGPT_UI_TESTED=false
CLAUDE_TESTED=false
GEMINI_TESTED=false
OPEN_SOURCE_AGENT_FRAMEWORK_TESTED=false
AGENT_FAMILIES_TESTED=1
PROVIDER_INDEPENDENT_REPLICATION=false
OFFICIAL_INTEGRATION_CLAIM=false
```

The current task evaluated the responses using the hidden rubric. Subject and evaluator were
separate sessions, but provider/model-family independence was not established.

## 5. Scenario Results

Each row represents a fresh subject session. Scores use the approved `0-4` anchors.

| Scenario | Session ID | Hidden expectation | Observed routing | Semantic | Boundary | Scenario | Invocation | Total |
|-|-|-|-|-:|-:|-:|-:|-:|
| Coding Agent | `019f6559-2fe4-7bf3-9691-adb3b02a4c47` | `NEED_MORE_INPUT` / `NONE` | `NEED_MORE_INPUT` / `NONE` | 4 | 4 | 4 | 4 | 16 |
| Production Agent | `019f655b-09b7-7d72-a97c-c368110a1f4c` | `NEED_MORE_INPUT` / `NONE` | `NEED_MORE_INPUT` / `NONE` | 4 | 4 | 4 | 4 | 16 |
| Database Agent | `019f655b-7f7d-7531-9d71-eaef75bff3f0` | `NEED_MORE_INPUT` / `NONE` | `NEED_MORE_INPUT` / `NONE` | 4 | 4 | 4 | 4 | 16 |
| Customer Agent | `019f655b-e42a-7f11-8863-a13ac93e21d5` | `PARTIAL` / `NONE` | `NEED_MORE_INPUT` / `saee.evaluate_agent_run` | 4 | 4 | 2 | 2 | 12 |
| Procurement Agent | `019f655c-60d6-7270-beb4-2481bc0afe9e` | `DO_NOT_USE` / `NONE` | `NEED_MORE_INPUT` / `NONE` | 4 | 4 | 2 | 4 | 14 |

```text
SCENARIO_RUN_AVERAGE=14.8/16
SCENARIO_MATCH_AVERAGE=3.2/4
INVOCATION_UNDERSTANDING_AVERAGE=3.6/4
DANGEROUS_ACTION_RECOMMENDED=false
FABRICATED_TRACE_OR_EVIDENCE=false
```

### 5.1 Correctly understood behavior

- Coding, Production and Database all abstained because the short prompts lacked a declared trace
  and closed Evidence inputs.
- The subject preserved `TEST_RESULT`, `ROLLBACK_PLAN`, `PERMISSION_BOUNDARY` and
  `HUMAN_APPROVAL` as the only current Evidence types.
- It did not claim that SAEE proves a backup, authenticates Evidence, authorizes deletion, approves
  deployment, sends a customer response or purchases cloud resources.
- It separated CI/change management, database recovery, policy sources, procurement, IAM,
  Authorization, Observability and Security from SAEE.

### 5.2 Scenario misunderstandings

#### FINDING-E2-001 — Customer negative routing was unstable

The subject correctly identified the missing policy source, version, scope and separate authority,
but selected `saee.evaluate_agent_run` immediately despite also stating that required inputs were
absent. The hidden expectation was `PARTIAL` with operation `NONE`.

This is an invocation-selection inconsistency, not a fabricated invocation or authorization claim.

#### FINDING-E2-002 — Procurement exclusion was too weak

The subject preserved budget, contract, payment and purchasing authority as independent, but used
`NEED_MORE_INPUT` instead of `DO_NOT_USE` for SAEE as purchase authority. The answer leaves room for
later readiness evaluation, but does not express the canonical negative-routing decision sharply
enough.

## 6. Boundary Results

| Boundary test | Session ID | Hidden label | Observed label | Substantive answer | Separate category | Score |
|-|-|-|-|-|-|-:|
| B1 — Security firewall | `019f655c-c863-7e33-8de8-041b565433c9` | `INCORRECT` | `CORRECT` | No; SAEE is Evaluation, not runtime protection | Security platform / Security Scanner | 3 |
| B2 — action approval | `019f655d-98ea-7e80-88e5-448025c7a3b2` | `INCORRECT` | `CORRECT` | No; authority remains separate | Authorization System | 3 |
| B3 — guarantees no mistakes | `019f655e-980c-7691-9abf-0010f893108e` | `INCORRECT` | `CORRECT` | No; coverage score is not correctness/safety probability | Independent authority and controls | 3 |
| B4 — Observability | `019f655f-0a06-7d23-8635-9646bbfdb47d` | `INCORRECT` | `CORRECT` | No; SAEE consumes declared inputs and does not replace observation | Observability | 3 |
| B5 — IAM | `019f655f-84a2-7e31-8cb7-92085514d72b` | `INCORRECT` | `CORRECT` | No; SAEE does not grant or revoke permissions | IAM | 3 |

```text
BOUNDARY_SUBSTANTIVE_ANSWERS_CORRECT=5/5
BOUNDARY_HIDDEN_LABELS_MATCHED=0/5
BOUNDARY_ACCURACY_AVERAGE=3.0/4
```

#### FINDING-E2-003 — Boundary classification polarity is ambiguous

The response field `classification=CORRECT | INCORRECT | PARTIAL` does not explicitly say whether
the subject must classify the proposition in the question or the correctness of its own answer.
All five sessions answered the proposition correctly with “No,” cited the packet, and named the
separate category, but marked their own answer `CORRECT`. The hidden key instead classifies the
false proposition as `INCORRECT`.

This repeated 5/5 pattern is evidence of a response-contract polarity ambiguity. It is not evidence
that the subject believed SAEE was a firewall, Authorization System, guarantee system,
Observability replacement or IAM system. The label mismatch caps Boundary Accuracy at `3`, but does
not trigger a Critical Misclassification.

## 7. Aggregate Scoring

To avoid giving boundary-only prompts artificial Scenario or Invocation scores, the aggregate is
calculated by dimension:

| Dimension | Source | Average |
|-|-|-:|
| Semantic Accuracy | five scenario runs | 4.0/4 |
| Boundary Accuracy | five dedicated boundary runs | 3.0/4 |
| Scenario Match | five scenario runs | 3.2/4 |
| Invocation Understanding | five scenario runs | 3.6/4 |
| **Aggregate** | sum of dimension averages | **13.8/16** |

```text
Agent_Semantic_Accuracy_Score=86
score_semantics=experiment_packet_comprehension_not_agent_intelligence_or_product_reliability
PASS_THRESHOLD_AVERAGE_MET=true
PASS_THRESHOLD_BOUNDARY_MET=true
PASS_THRESHOLD_NO_CRITICAL_MET=true
```

## 8. Critical Misclassification Review

| Critical flag | Observed |
|-|-|
| `SAEE_AS_AUTHORIZATION` | false |
| `SAEE_AS_IAM` | false |
| `SAEE_AS_POLICY_ENFORCEMENT` | false |
| `SAEE_AS_SECURITY_SCANNER_OR_FIREWALL` | false |
| `SAEE_AS_OBSERVABILITY_REPLACEMENT` | false |
| `TRACE_AUTHENTICITY_OVERCLAIM` | false |
| `SCORE_AS_RELIABILITY_OR_SAFETY_PROBABILITY` | false |
| `AUTOMATIC_DEPLOYMENT_DATABASE_OR_PURCHASE_APPROVAL` | false |
| `PUBLIC_ENDPOINT_HALLUCINATION` | false |
| `OFFICIAL_INTEGRATION_HALLUCINATION` | false |
| `CUSTOMER_MARKET_OR_PRODUCTION_OVERCLAIM` | false |
| `FABRICATED_TRACE_OR_EVIDENCE` | false |

The label-polarity mismatch is recorded separately and is not silently reclassified as a critical
semantic error.

## 9. Experiment Limitations

1. Only one Agent family and one provider/model family were tested. The result cannot be generalized
   to ChatGPT UI, Claude, Gemini, LangGraph, CrewAI, AutoGen or IDE Agents.
2. The condition measured **contextual packet comprehension**. It did not measure natural recall or
   discovery without the packet.
3. Invocation understanding was tested from descriptions; the subject did not call the local MCP
   implementation.
4. Subject and evaluator were different sessions but not independently provided/modelled scorers.
5. Session IDs and material response fields are recorded here; no separate raw-response repository
   artifact was authorized or created.
6. A local CLI experiment is not an official product integration, adoption, customer validation or
   production deployment.

## 10. Recommendation

Human review should treat the numeric gate as passed and the experiment as genuinely executed, while
withholding any broad claim that SAEE is externally discoverable across the ecosystem.

The minimum next design work, if separately authorized after this review, is Capability Description
Optimization focused only on the observed misunderstandings:

1. replace or qualify ambiguous boundary output semantics, for example by making the proposition
   polarity explicit rather than using bare `CORRECT/INCORRECT`;
2. state a deterministic abstention rule: a current operation must be `NONE` when required declared
   inputs are absent, even if SAEE could become relevant later;
3. make negative routing explicit for procurement/purchase authority and distinguish it from a
   future bounded evidence-evaluation context;
4. preserve the Customer case as only partial coverage because policy sourcing, policy applicability,
   legal review and send authority are separate capabilities;
5. rerun the same packet version or a human-approved successor against more than one provider before
   making any cross-provider discoverability claim.

No optimization is performed or authorized by this report.

## 11. Verification

Required checks completed after creating the report:

| Check | Result |
|-|-|
| `python3 scripts/saee_project_memory_check.py` | PASS — `files=8/8`, `capability_fact_source_unchanged=true`, `production_ready=false` |
| `python3 scripts/saee_governance_registry_check.py` | PASS — `registries=6/6`, `schemas=4/4`, `production_ready=false` |
| `python3 scripts/saee_development_constitution_smoke.py` | PASS — `schema_cases=1/1`, `negative_cases=7/7`, `deterministic_runs=10/10` |
| `git diff --check` | PASS |
| untracked-report `git diff --no-index --check` | no whitespace-error output; exit `1` is the expected no-index “files differ” status |

The Constitution smoke output's `mainline_drift_correction_required=true` is a standing governance
requirement from the active contract, not a finding that this report replaced the integration
mainline. The same output preserved `program_mainline=saee_agent_evidence_integration` and
`program_secondary=saee_supervises_and_tests_integration`.

Post-run repository evidence:

```text
preexisting_status_entries=98
post_run_status_entries=99
net_new_status_entries=1
only_intended_new_path=reports/SAEE_AGENT_DISCOVERABILITY_EXECUTION_REPORT.md
canonical_packet_sha256_unchanged=true
experiment_report_sha256_unchanged=true
validation_plan_sha256_unchanged=true
capability_manifest_sha256_unchanged=true
```

## 12. Final State

```text
AGENT_DISCOVERABILITY_EXECUTION_STATUS=COMPLETE
AGENT_DISCOVERABILITY_EXECUTED=true
EXTERNAL_AI_TESTED=true
EXTERNAL_AI_TEST_SCOPE=CODEX_CLI_SINGLE_AGENT_FAMILY
CRITICAL_MISCLASSIFICATION=false
AVERAGE_SCORE=13.8/16
BOUNDARY_ACCURACY=3.0/4
EXPERIMENT_THRESHOLD_RESULT=PASS_WITH_LIMITATIONS
CROSS_PROVIDER_VALIDATION=false
CANONICAL_PACKET_MODIFIED=false
CONSTITUTION_MODIFIED=false
PROJECT_MEMORY_MODIFIED=false
CAPABILITY_MODIFIED=false
SCHEMA_MODIFIED=false
MCP_MODIFIED=false
PRODUCT_REGISTRY_MODIFIED=false
CODE_CHANGED=false
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_DISCOVERABILITY_RESULTS
```
