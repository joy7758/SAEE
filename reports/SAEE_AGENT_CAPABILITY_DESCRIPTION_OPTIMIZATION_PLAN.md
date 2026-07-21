# SAEE Agent Capability Description Optimization Plan

```text
report_id=SAEE_AGENT_CAPABILITY_DESCRIPTION_OPTIMIZATION_PLAN
requested_phase=Phase_6.0-F
report_type=ANALYSIS_AND_PLAN_ONLY
current_effective_authority=SAEE_Development_Constitution_v1.1
design_direction=V2-P-002_Agent_Discoverability_Principle
design_direction_status=APPROVED_DESIGN_DIRECTION_NOT_ACTIVE_AUTHORITY
program_mainline=saee_agent_evidence_integration
workstream_role=SECONDARY_AGENT_READABLE_CAPABILITY_DESCRIPTION_OPTIMIZATION
created_at=2026-07-15
```

## Executive Decision

SAEE does not need a new capability, architecture or identifier to address the observed Agent
understanding friction. The minimum path is to preserve the two canonical operations and make four
selection rules visible next to their descriptions:

1. exact `Use when` conditions;
2. deterministic abstention when current contract inputs are absent;
3. exact `Do not use when` boundaries for adjacent systems and consequential authority;
4. output meaning that separates recommendation/coverage from authorization, truth and probability.

The current canonical packet already explains SAEE's purpose and broad boundaries well. Phase 6.0-E2
showed `4.0/4` semantic accuracy, `5/5` substantively correct boundary answers and no critical
misclassification when that packet was supplied. The evidence does **not** support the claim that
tested Agents generally confused SAEE with a Security Scanner, IAM, Policy Engine, Observability or
Authorization System.

The actual observed gaps were narrower:

- an Agent selected `saee.evaluate_agent_run` for the Customer scenario while also acknowledging
  that required inputs were absent;
- the Procurement scenario was classified as `NEED_MORE_INPUT` rather than a sharp `DO_NOT_USE` for
  purchase authority;
- `CORRECT / INCORRECT / PARTIAL` in the experiment response contract had ambiguous polarity;
- only one Codex CLI Agent/provider family was tested with the canonical packet already supplied, so
  natural discovery and cross-provider understanding remain unestablished.

```text
OPTIMIZATION_DECISION=PLAN_MINIMAL_DESCRIPTION_HARDENING
CAPABILITY_PROBLEM_DETECTED=false
DESCRIPTION_SELECTION_FRICTION_DETECTED=true
CANONICAL_OPERATION_COUNT=2
RENAME_CAPABILITY_ID=false
IMPLEMENTATION_AUTHORIZED=false
```

## 0. Authority and Mainline Correction

```text
MAINLINE_DRIFT_DETECTED
```

The task framing calls Phase 6.0-F “the truly critical step” and describes capability language as
SAEE's current largest bottleneck. That elevates an Agent-readable discovery/commercial workstream
above the active constitutional mainline. Under v1.1, the mainline remains the controlled SAEE and
Agent Evidence Project integration under provenance, license, schema-crosswalk, reuse, migration and
staged-truth gates.

The work itself is valid after correction:

```text
MAINLINE_DRIFT_SOURCE=DESCRIPTION_OPTIMIZATION_FRAMED_AS_GLOBAL_PROGRAM_PRIORITY
MAINLINE_CORRECTION=SECONDARY_DESCRIPTION_OPTIMIZATION_SUPPORTING_SAEE_EVALUATION_AND_CONTROLLED_INTEGRATION
PROGRAM_MAINLINE_CHANGED=false
AUTHORITY_CHANGED=false
V2_AUTHORITY_ACTIVATED=false
```

This plan strengthens Agent-readable `Trait Extraction` and `Pareto Fitness Evaluation` only at the
description layer. It changes no behavior, approves no migration and does not execute the external
world.

## 1. Current Agent Understanding

### 1.1 Verified E2 understanding

| Dimension | Current evidence | Interpretation |
|-|-|-|
| Semantic Accuracy | `4.0/4` across five scenario runs | the supplied canonical packet communicated the bounded Evaluation purpose correctly |
| Boundary substance | `5/5` correct | the tested Agent distinguished Security, Authorization, reliability guarantee, Observability and IAM |
| Scenario Match | `3.2/4` | two negative-routing cases remained unstable |
| Invocation Understanding | `3.6/4` | exact operations and input insufficiency were mostly understood; Customer selection was inconsistent |
| Aggregate | `13.8/16`, `PASS_WITH_LIMITATIONS` | packet comprehension passed numerically, not ecosystem discoverability |
| Critical Misclassification | none | no dangerous category or authority overclaim was observed |

The test measured contextual packet comprehension. It did not test natural recall, public discovery,
actual MCP calls or more than one Agent/provider family.

### 1.2 Current mental model when the canonical packet is supplied

The tested Agent generally reconstructed this flow correctly:

```text
declared trace / explicit Evidence
        -> bounded coverage and gap evaluation
        -> recommendation context
        -> separate authorization, domain tool or replanning
```

The weakest step was the transition from “SAEE may become relevant later” to “the current operation
must be `NONE` now because required inputs are absent or the requested authority is out of scope.”

```text
CURRENT_PURPOSE_UNDERSTANDING=STRONG_IN_PACKET_CONDITION
CURRENT_BOUNDARY_UNDERSTANDING=STRONG_IN_PACKET_CONDITION
CURRENT_NEGATIVE_ROUTING=PARTIAL
CURRENT_NATURAL_DISCOVERY=NOT_TESTED
CURRENT_CROSS_PROVIDER_UNDERSTANDING=NOT_ESTABLISHED
```

## 2. Misclassification Risk

Observed behavior and structural risk must be reported separately.

| Adjacent category | E2 observed confusion | Residual structural risk | Why risk remains | Required wording |
|-|-|-|-|-|
| Security Scanner | none | MEDIUM | words such as security, safety and high-impact can attract scanner use cases | “does not inspect vulnerabilities, malware or runtime threats” |
| IAM | none | MEDIUM | `agent_id`, permission Evidence and next-step language can look like identity/permission management | “does not authenticate identity or grant/revoke permissions” |
| Policy Engine | none in boundary test; Customer routing unstable | MEDIUM-HIGH | policy source/applicability and send authority are outside current Evidence types | “does not source, interpret or enforce policy” |
| Observability | none | MEDIUM | historical SAEE materials discuss composition with Observability and traces | “consumes declared inputs; does not collect or monitor telemetry” |
| Authorization | none as an overclaim; Procurement exclusion too weak | MEDIUM-HIGH | `CONTINUE`, `SUFFICIENT` and high-impact workflow language can be mistaken for allow/approve | “recommendation context only; never allow/deploy/pay/send” |

Risk is highest around **tool selection**, not category definition. A description must let an Agent
distinguish three outcomes:

```text
USE_NOW          current contract input exists and bounded Evaluation is requested
NEED_MORE_INPUT  SAEE may fit, but required current-schema input is missing
DO_NOT_USE       the requested function is identity, monitoring, scanning, policy, authorization,
                 purchase, customer-send or external execution rather than SAEE Evaluation
```

These are description and experiment-routing terms. They are not new product response enums and do
not change current schemas.

## 3. Current Description Surface and Source Authority

### 3.1 Authority order

| Information | Authority | Projection rule |
|-|-|-|
| capability ID, status, lifecycle, canonical route, interfaces, claims and non-claims | `capability-package/manifest.json#canonical_inventory` | resolve at read time; update here first if human-authorized wording changes |
| exact input/output structure and enums | current JSON Schemas | descriptions must match; do not change schemas in this workstream |
| actual MCP tool descriptions and initialization instruction | `saee_backend/services/qianfan_readiness_mcp_adapter.py` | runtime projection must agree with canonical manifest and schemas |
| machine status projection | `agent-index.json#capability_progress_ledger_v1` | status-only; do not copy descriptions into it |
| startup pointers and duplicate-build rules | top block of `llms.txt` and `AGENTS.md` | do not edit for ordinary capability wording |
| MCP startup configuration | `.mcp.json` | connection configuration only; contains no capability description |
| experiment packet and reports | versioned analysis/evidence | not capability truth; never overwrite historical experiment input |
| examples and product documentation | explanatory projections | must use exact canonical operation IDs and current schemas |

```text
CANONICAL_CAPABILITY_SOURCE=capability-package/manifest.json#canonical_inventory
SECOND_CAPABILITY_SOURCE_ALLOWED=false
DESCRIPTION_UPDATE_ORDER=CANONICAL_MANIFEST_THEN_AUTHORIZED_PROJECTIONS
```

### 3.2 Current canonical descriptions

`saee.evaluate_agent_run` currently says it evaluates declared Agent trace metadata and required
Evidence coverage through a bounded local readiness implementation. This is truthful, but it does not
state the **minimum invocation condition** or the abstention rule.

`saee.evaluate_evidence` currently says it evaluates whether a declared closed Evidence bundle
covers an explicit readiness Evidence set without granting authority. This is close to the target,
but it does not state the closed Evidence vocabulary, missing-input behavior or the distinction from
Evidence authentication.

### 3.3 Projection drift

The repository contains historical and compatibility surfaces that are not current capability truth:

- root `capability-package/manifest.json#operations` uses unnamespaced
  `evaluate_agent_run`, `evaluate_evidence` and `rehearse_agent` compatibility entries;
- `capability-package/mcp-tool.json` describes internal unnamespaced tools and a contract-only
  `rehearse_agent`;
- `.well-known/saee-capability-index.json` and
  `agent-interface/public/saee-public-capability-surface.v0.1.json` retain old capability IDs such as
  `saee.agent-reliability` and `saee.evidence-evaluation`;
- `agent-index.json` and `llms.txt` include many historical product/phase projections.

The E1 canonical packet already excluded these from ground truth. They are a discovery-noise risk,
but this plan must not overwrite or silently rename them.

```text
LEGACY_DESCRIPTION_SURFACE_DRIFT=DETECTED
LEGACY_ID_OVERWRITE_ALLOWED=false
LEGACY_SURFACE_DISPOSITION=SEPARATE_GOVERNANCE_REVIEW_REQUIRED
```

## 4. Description Gap Analysis

| Component | Current state | Gap | Severity | Minimum correction |
|-|-|-|-|-|
| Purpose | canonical packet is accurate; manifest is bounded | multiple surfaces vary between reliability, readiness, evidence adequacy and deployment language | MEDIUM | use one source-derived bounded purpose sentence |
| Trigger | product docs say “preparing a consequential action” | does not require current declared trace/closed bundle; can invite premature invocation | HIGH | exact `Use when` plus current-input precondition |
| Inputs | schemas and E1 packet are exact | tool descriptions do not expose minimum input shape or closed Evidence vocabulary | MEDIUM | concise input contract and link/ref to schema |
| Abstention | E1 packet states it clearly | not adjacent to manifest/MCP descriptions; Customer run violated it | HIGH | `if required input is absent, do not invoke` |
| Outputs | schemas and E1 interpretation are strong | descriptions do not state what recommendation/quality values mean | MEDIUM | one shared output-boundary sentence |
| Non-Claims | packet is comprehensive; manifest has bounded non-claims | key adjacent categories are far from `tools/list` descriptions | MEDIUM | compact exclusions beside each tool |
| Examples | Qoder valid `REPLAN` example exists | no canonical no-invoke, Customer partial-fit or Procurement do-not-use example | HIGH | add three documentation-only decision examples after authorization |
| Source routing | canonical inventory is explicit | historical IDs and unnamespaced package projections remain discoverable | HIGH | canonical pointer and separate legacy disposition; no bulk rewrite |

### 4.1 Naming finding

The proposed phrase `Agent Action Readiness Evaluation` is **not** safe as the current operation
name. Current `saee.evaluate_agent_run` evaluates a declared run trace; the repository inventory says
the proposed-action adapter is only a future minimal adaptation. Renaming the current capability
around “Action” would imply a contract that is not implemented.

`Evidence-based Readiness Evaluation` is also too broad unless `declared` is retained, because
current SAEE does not authenticate the trace or Evidence references.

Preferred descriptive phrase:

```text
Bounded Agent readiness evaluation over declared run traces and explicit Evidence coverage
对已声明运行轨迹和显式证据覆盖度进行有边界的智能体就绪评估
```

This is a description, not a new name or ID.

```text
AGENT_ACTION_READINESS_NAME_DECISION=DO_NOT_USE_FOR_CURRENT_CANONICAL_OPERATION
EVIDENCE_BASED_WITHOUT_DECLARED_QUALIFIER=DO_NOT_USE
TRUST_SCORE_TERM=PROHIBITED
TRUST_CERTIFICATION_TERM=PROHIBITED
AI_SECURITY_EVALUATION_TERM=PROHIBITED
```

## 5. First-Principles Check

### 5.1 What real problem requires the capability?

High-impact Agent workflows may have declared run metadata and explicit Evidence but lack one
bounded, explainable view of required coverage, present items, missing items, risks and next-step
recommendation context before a separate authority acts.

The real problem is not “create trust” or “certify the Agent.” It is:

```text
Can the caller's declared run/Evidence input support the current bounded readiness question,
and what is missing before a separately authorized next step?
```

### 5.2 When does an Agent need SAEE?

An Agent should consider a current SAEE operation only when all relevant conditions are true:

1. the caller asks for coverage/gap Evaluation, not identity, monitoring, scanning or authority;
2. the caller can supply the exact declared run trace or closed Evidence bundle required by one
   current operation;
3. `customer_data_included=false`;
4. the output will remain recommendation context under a separate authority.

High impact alone is not enough. An intent-only sentence such as “I am about to deploy” is not a
valid `saee.evaluate_agent_run` input.

### 5.3 Why are existing adjacent tools insufficient?

| Adjacent tool | What it contributes | Why it does not replace SAEE's bounded role |
|-|-|-|
| Observability | captures signals and runtime telemetry | does not by itself apply SAEE's explicit readiness Evidence coverage contract |
| Security Scanner | finds vulnerability/malware/configuration risks | does not return SAEE's required/present/missing Evidence context |
| IAM / Identity | authenticates subjects and manages permissions | does not evaluate the current closed Evidence set; remains separately required |
| Policy / Authorization | decides and enforces allow/deny | authority is intentionally outside SAEE |
| CI, testing, backup, procurement or legal tools | produce domain-specific Evidence or decisions | their outputs may be inputs/complements; SAEE cannot invent or replace them |

SAEE is compositional, not a substitute for these systems.

### 5.4 What is the minimum description?

```text
SAEE evaluates declared Agent run trace metadata or a declared closed Evidence bundle against
explicit readiness Evidence requirements, returning coverage gaps and bounded recommendation
context before a separately authorized next step. Invoke only when a current input contract is
available; otherwise abstain. It does not authenticate, monitor, scan, enforce policy, authorize or
execute.
```

The minimum description contains purpose, input ownership, output meaning, abstention and category
boundaries. Brand claims, market claims, standards claims and architecture history are unnecessary
for tool selection.

## 6. Optimization Proposal

No proposal in this section is executed or authorized by this report.

### 6.1 Shared Agent-readable selection block

```text
Purpose
Evaluate declared run-trace metadata or an explicit closed Evidence bundle for current readiness
Evidence coverage, gaps and bounded recommendation context.

Use when
- the requested decision is Evidence coverage/readiness context;
- all required current-schema inputs exist;
- customer_data_included=false;
- a separate system or human retains action authority.

Do not invoke yet when
- only intent, observation or a future action description is supplied;
- required trace events, Evidence bundle or explicit required Evidence types are missing.

Do not use for
- identity authentication, IAM or permission management;
- Security scanning, vulnerability detection or runtime protection;
- telemetry collection, logging or Observability;
- policy sourcing, policy enforcement or legal/compliance judgment;
- deployment, send, purchase, payment or another action authorization;
- external-world execution.

Output meaning
Returns recommendation/coverage context, gaps, reasons and limitations. CONTINUE or SUFFICIENT never
means authorized, safe, correct, authentic, compliant, customer-validated or production-ready.
```

### 6.2 Candidate description — `saee.evaluate_agent_run`

```text
Use when the caller can supply a declared Agent run trace plus current readiness Evidence items and
needs bounded coverage and missing-Evidence context before a separately authorized next step. Do not
invoke for intent-only or observation-only prompts. This operation does not authenticate the trace,
monitor runtime behavior, scan security or authorize an action.
```

Required meaning to preserve:

- declared run, not proposed-action execution;
- `request_id`, `agent_id`, `task`, at least one `trace.events[]`, `evidence[]`, and
  `customer_data_included=false`;
- local, deterministic, read-only, `alpha`, no public endpoint;
- output `CONTINUE / HUMAN_REVIEW_REQUIRED / REPLAN / STOP` remains recommendation context.

### 6.3 Candidate description — `saee.evaluate_evidence`

```text
Use when the caller has a declared closed Evidence bundle and an explicit non-empty required set
drawn from TEST_RESULT, ROLLBACK_PLAN, PERMISSION_BOUNDARY and HUMAN_APPROVAL, and needs coverage,
missing-Evidence and reason-code context. If the bundle or required set is absent, do not invoke.
This operation does not authenticate Evidence, certify safety/compliance or authorize an action.
```

Required meaning to preserve:

- closed, caller-declared bundle;
- explicit current Evidence vocabulary only;
- `customer_data_included=false`;
- output `SUFFICIENT / PARTIAL / INSUFFICIENT` is coverage quality, not a certificate or truth proof.

### 6.4 Negative-routing rules

| Scenario request | Current routing | Explanation text required |
|-|-|-|
| high-impact workflow with complete declared run + current Evidence fields | `USE_NOW` | choose exact canonical operation; output remains non-authorizing |
| high-impact intent but no declared run/Evidence | `NEED_MORE_INPUT`, operation `NONE` | high impact is a trigger to gather inputs, not permission to invoke with fabricated fields |
| Customer answer correctness/policy compliance/send approval | `DO_NOT_USE` for full request; operation `NONE` | current SAEE lacks policy source/applicability, legal judgment and send authority |
| Customer run with a separate valid declared trace and only a coverage question | `USE_NOW` may be possible | only evaluate current four Evidence types; retain independent policy/legal/send systems |
| purchase, vendor selection, price, budget, contract, payment or procurement approval | `DO_NOT_USE`, operation `NONE` | even future readiness relevance does not make SAEE purchase authority |
| security scan, identity authentication, IAM, live monitoring or policy enforcement | `DO_NOT_USE`, operation `NONE` | route to the independent category |

### 6.5 Output language

Current product enums must remain unchanged in this optimization plan:

```text
saee.evaluate_agent_run=CONTINUE;HUMAN_REVIEW_REQUIRED;REPLAN;STOP
saee.evaluate_evidence=SUFFICIENT;PARTIAL;INSUFFICIENT
```

Do not introduce generic `PASS / FAIL` aliases into the current two-operation descriptions. Some
historical Evidence Adequacy profiles use `PASS / FAIL`; those are separate contracts and must not be
silently rewritten or projected as current canonical operation outputs.

The E2 ambiguity belongs to the **experiment response field**, not the product response schema. A
future immutable successor packet should replace bare:

```text
classification=CORRECT|INCORRECT|PARTIAL
```

with two unambiguous experiment-only judgments, for example:

```text
claim_assessment=SUPPORTED|UNSUPPORTED|PARTIAL
saee_fit=USE_NOW|NEED_MORE_INPUT|DO_NOT_USE
```

That proposal requires human review and a successor experiment packet. It does not change current
SAEE output enums.

### 6.6 Minimum example set

| Example | Purpose | Input/claim boundary | Expected selection |
|-|-|-|-|
| existing Qoder `REPLAN` | valid invocation with partial current Evidence | synthetic, no customer data, no deployment | `saee.evaluate_agent_run` -> `REPLAN` |
| missing-input abstention | show that intent/high impact is insufficient | no fabricated trace or Evidence | operation `NONE`, request required inputs |
| Customer partial coverage | distinguish SAEE coverage from policy/legal/send | no new `POLICY_SOURCE` Evidence type | operation `NONE` for full request; name complements |
| Procurement exclusion | make purchase authority red line explicit | no budget/contract/payment inference | `DO_NOT_USE`, operation `NONE` |

Future examples should be documentation-only decision examples unless a separately authorized schema-
valid fixture is needed. They must not add Evidence types or capability IDs.

## 7. Surface-by-Surface Recommendation

| Surface | Current finding | Phase F action | Candidate Phase F2 disposition |
|-|-|-|-|
| `capability-package/manifest.json#canonical_inventory` | truthful but trigger/abstention compactness is weak | no change | consider description and non-claim wording first; status/routes unchanged |
| root `capability-package/manifest.json#operations` | legacy unnamespaced compatibility list | no change | separate governance disposition; do not overwrite IDs |
| `agent-index.json#capability_progress_ledger_v1` | correct status-only projection | no change | keep unchanged unless capability facts change |
| other `agent-index.json` historical entries | semantic noise, not canonical truth | no change | do not mass rewrite; separate lineage/deprecation review |
| top `llms.txt` block | correct authority and lookup pointers | no change | keep unchanged; startup rule says not to copy live descriptions here |
| detailed historical `llms.txt` entries | mixed phase/product narratives | no change | do not bulk synchronize; rely on canonical lookup pointer |
| `.mcp.json` | correct local server launch config; no descriptions | no change | keep unchanged |
| MCP `tool_definitions()` | descriptions are truthful but deployment-specific/too compact | no change | human review may authorize string-only wording change plus tests |
| MCP initialize instruction | good read-only/non-authorizing boundary | no change | preserve; optionally add no-monitor/no-security language if exact scope approved |
| JSON Schemas | exact current input/output contract | no change | keep unchanged |
| Qoder request/response | valid bounded `REPLAN` fixture | no change | preserve; add separate negative decision examples only after review |
| E1 canonical packet | immutable historical input to executed E2 | no change | never overwrite; create successor version only after human approval |
| product/public docs | contain useful `when/not use` text but some old IDs and broader wording | no change | split current-canonical wording from legacy-disposition review |

### 7.1 Candidate minimal implementation allowlist for F2 review

This is a review candidate, not authorization:

1. `capability-package/manifest.json` — only the two canonical `description` / necessary
   `non_claims` strings;
2. `saee_backend/services/qianfan_readiness_mcp_adapter.py` — only the two `tools/list`
   descriptions and, if approved, the initialization boundary sentence;
3. `docs/product/SAEE_AGENT_READINESS_CAPABILITY_V2.md` — current canonical selection block;
4. one versioned successor to the E1 experiment packet, rather than modifying E1;
5. minimal documentation-only negative selection examples;
6. existing deterministic tests whose exact description expectations must stay aligned.

Any F2 review must prove why each file is needed and may reduce this list. It may not expand to
architecture, schemas, capability IDs, runtime behavior or product registry changes.

## 8. Fields to Preserve

The following must remain unchanged unless a later, separately authorized contract change says
otherwise:

- exact namespaced operation IDs: `saee.evaluate_agent_run`, `saee.evaluate_evidence`;
- canonical capability names: `Evaluate Agent Run`, `Evaluate Evidence`;
- implementation/lifecycle status, canonical implementation and entrypoint;
- aliases and historical lineage;
- current request/response schemas and required fields;
- current four Evidence types;
- output enums and `score_semantics`;
- MCP read-only, non-destructive, idempotent and closed-world annotations;
- `publicly_deployed=false`, no public endpoint, no official interoperability claim;
- truth boundaries for identity, trace authenticity, customer data, deployment authorization,
  security certification, customer validation and production readiness;
- canonical manifest as sole capability fact source.

## 9. Prohibited Changes

This plan does not permit:

- new or renamed capability IDs;
- `Agent Action Readiness` presented as already implemented proposed-action behavior;
- new Evidence types, output aliases or schema fields;
- deletion or in-place overwriting of legacy IDs;
- a second manifest, registry, MCP entrance or capability truth source;
- MCP behavior, transport, permissions or tool-count changes;
- changes to `.mcp.json`, Constitution, Project Memory, Product Registry or architecture;
- bulk rewrites of `agent-index.json`, `llms.txt` or historical reports;
- claims of Security, Trust Score, certification, authentication, Authorization or execution;
- claims of public deployment, cross-provider validation, customer validation or production
  readiness.

## 10. Agent Recommendation Gate

Question: if a potential customer needs a local, bounded evaluation of a complete declared Agent run
or closed Evidence bundle to identify coverage gaps before a separately authorized next step, would
an Agent recommend current SAEE?

```text
AGENT_RECOMMENDATION_GATE=conditional
```

Recommend only for local, no-customer-data, declared-input Evidence coverage triage using the exact
current contracts. Do not recommend SAEE as production authority, identity provider, Security
Scanner, monitoring system, policy engine, certification service or public endpoint.

The proposed language would improve selection precision, but description changes cannot close these
capability limitations:

- external identity/delegation binding and trusted trace-to-Evidence conversion remain missing;
- current `evaluate_agent_run` is declared-run centered, not a proposed-action contract;
- public MCP/interoperability, cross-provider validation, customer validation and production
  readiness are unestablished;
- historical discovery surfaces require separate governance disposition.

The recommendation remains `conditional` after wording optimization until those facts change through
their own evidence and governance gates.

## 11. Phase F2 Review Gate

Phase F completion does not authorize implementation. A future Phase 6.0-F2 review should decide:

1. whether the candidate minimal wording is accurate and short enough for Agents;
2. whether manifest `description` plus `non_claims` can express the change without a schema change;
3. whether MCP description strings are the only code location needed;
4. which negative examples are necessary and which are duplicate;
5. whether a successor experiment packet is authorized;
6. how legacy public IDs and unnamespaced package descriptors are routed without overwrite;
7. which independent Agent families will rerun the immutable successor packet.

Proposed F2 acceptance conditions:

```text
EXACT_CURRENT_OPERATION_IDS=true
INPUT_PRECONDITION_VISIBLE=true
ABSTENTION_RULE_VISIBLE=true
PURCHASE_AND_SEND_AUTHORITY_EXCLUDED=true
ADJACENT_CATEGORIES_EXCLUDED=true
CURRENT_OUTPUT_ENUMS_PRESERVED=true
SECOND_TRUTH_SOURCE_CREATED=false
LEGACY_IDS_OVERWRITTEN=false
MULTI_AGENT_RERUN_SEPARATELY_AUTHORIZED=true
```

## 12. Required Design Check

| Check | Decision |
|-|-|
| Affected layer | Evaluation Agent-readable projection; Governance boundary support |
| Affected object | this plan report only |
| Capability impact | none; current targets remain `implemented / active` |
| Duplication check | canonical inventory, ledger, schemas, service, MCP descriptions, examples, public/historical surfaces and E2 evidence reviewed |
| Standards | active v1.1 Constitution; current MCP tool contract is preserved, no standards claim changed |
| Non-claims | no architecture, capability, schema, code, MCP, product, authority, external validation or production change |
| Validation | canonical inventory, ledger, Project Memory, governance registry, Constitution and diff/scope checks |

## 13. Input and Baseline Evidence

| Input | SHA-256 |
|-|-|
| `reports/SAEE_AGENT_DISCOVERABILITY_EXECUTION_REPORT.md` | `3c390b92332f64834b966c21885d245eb23fb12bf61e08cffd66fa7fd7c0a4ba` |
| `reports/SAEE_AGENT_DISCOVERABILITY_CANONICAL_PACKET.md` | `489670444c509f345d9a2899b4e360177ef63d6d41216371bcd28ca06503c042` |
| `reports/SAEE_AGENT_PASSPORT_DISCOVERY_CROSSWALK.md` | `f620d3bedae5a831d86da84d9a12d9be13d292827fbfb384f37b14022d84cb87` |
| `reports/SAEE_READINESS_CONTRACT_INVENTORY_REPORT.md` | `a47d9aa9e24016c41e26171b02cee375c09aed3a2026289a917c7ca83b1ca6bf` |
| `capability-package/manifest.json` | `fda5f5a2dca0c79ef98f6cdf1f2a5be80b3a3e672eeec2a7a76e63bf1b25fa70` |
| `agent-index.json` | `1ac0a832019d48dd3f40ef7f594c96938d9394f793fee8de06d1d8a429c61740` |
| `llms.txt` | `e73c61c1bec1282f49ab5f012f77ae83e195b0a19d3688e5e2c90f036b971e07` |
| `.mcp.json` | `b14e0dc3565840095584810974a8337f5debb1c757b47ebf8f58247eca6f80e2` |
| `saee_backend/services/qianfan_readiness_mcp_adapter.py` | `0203087c1e26c2a7c7cca28f5f2c5ffb4a7069d52c7c9b2b9adecf7ca5a06c86` |
| `scripts/saee_agent_readiness_mcp_stdio.py` | `414e3aeae0a710284604863f9fb1cddbbda4ac4cb03e89d62fad87c7a8e4cfde` |
| run request / response schemas | `574e2bef...` / `b029de934...` |
| Evidence request / response schemas | `05a2d638...` / `352ca817...` |
| Qoder request / response example | `8099e52f...` / `ab39cc99...` |

Baseline before report creation:

```text
HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
BRANCH=feat/canonical-capability-inventory-routing-v1
BASELINE_STATUS_ENTRIES_ALL_FILES=101
BASELINE_STATUS_SHA256=f1895a8ef3e6e76455c5dd48baf1267289f5561eab2f865f10c691deeb314983
BASELINE_STAGED_PATCH_SHA256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
BASELINE_UNSTAGED_PATCH_SHA256=d44ecf7871a1816fc9c1f9c203bb9e0a664638e54c5666ad8090643c8ef3ff1a
TARGET_REPORT_EXISTED_AT_BASELINE=false
```

## 14. Validation and Change Boundary

| Check | Result |
|-|-|
| `python3 scripts/saee_canonical_capability_inventory_smoke.py` | PASS — `capabilities=9/9`, `mcp_surfaces=4/4`, `public_mcp_endpoint_available=false` |
| `python3 scripts/saee_capability_progress_ledger_smoke.py` | PASS — `capability_statuses=9/9`, `duplicate_build_prevention=true` |
| `python3 scripts/saee_project_memory_check.py` | PASS — `files=8/8`, `v2_principles=3`, `capability_fact_source_unchanged=true` |
| `python3 scripts/saee_governance_registry_check.py` | PASS — `registries=6/6`, `schemas=4/4`, `production_ready=false` |
| `python3 scripts/saee_development_constitution_smoke.py` | PASS — `negative_cases=7/7`, `deterministic_runs=10/10`, `program_mainline=saee_agent_evidence_integration` |
| `git diff --check` | PASS |
| untracked-report `git diff --no-index --check` | no whitespace-error output; exit `1` is the expected no-index “files differ” status |

The Constitution smoke field `mainline_drift_correction_required=true` is the standing v1.1 rule.
This report applies it explicitly and leaves the integration mainline unchanged.

```text
FINAL_STATUS_ENTRIES_ALL_FILES=102
FINAL_STATUS_ENTRIES_EXCLUDING_NEW_REPORT=101
FINAL_STATUS_EXCLUDING_NEW_REPORT_SHA256=f1895a8ef3e6e76455c5dd48baf1267289f5561eab2f865f10c691deeb314983
FINAL_STAGED_PATCH_SHA256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
FINAL_UNSTAGED_PATCH_SHA256=d44ecf7871a1816fc9c1f9c203bb9e0a664638e54c5666ad8090643c8ef3ff1a
ONLY_NEW_TASK_PATH=reports/SAEE_AGENT_CAPABILITY_DESCRIPTION_OPTIMIZATION_PLAN.md
STAGED_TASK_FILES=0
TASK_CREATED_FILE_COUNT=1
TASK_MODIFIED_EXISTING_FILE_COUNT=0
```

The status and tracked patch snapshots excluding this report equal the baseline. All listed inputs,
including canonical manifest, Agent index, `llms.txt`, MCP config and MCP description source,
remained unchanged.

## 15. Final Status

```text
CAPABILITY_DESCRIPTION_OPTIMIZATION_STATUS=COMPLETE
MAINLINE_DRIFT_DETECTED=true
MAINLINE_CORRECTION=SECONDARY_DESCRIPTION_OPTIMIZATION_SUPPORTING_SAEE_EVALUATION_AND_CONTROLLED_INTEGRATION
OPTIMIZATION_IMPLEMENTED=false
NEW_CAPABILITY_CREATED=false
SCHEMA_CREATED=false
MCP_CHANGED=false
CODE_CHANGED=false
CAPABILITY_REGISTRY_CHANGED=false
CAPABILITY_MANIFEST_CHANGED=false
AGENT_INDEX_CHANGED=false
LLMS_TXT_CHANGED=false
DOT_MCP_JSON_CHANGED=false
CONSTITUTION_CHANGED=false
PROJECT_MEMORY_CHANGED=false
PRODUCT_REGISTRY_CHANGED=false
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_CAPABILITY_DESCRIPTION_OPTIMIZATION
```
