# SAEE Architecture Capability Assessment Report

Assessment date: 2026-07-13

Repository: SAEE repository root (`.`)

Assessment mode: repository evidence only; no market uniqueness claim; no production or customer claim

Assessed commit: `00d8d0467` on `main`

Post-assessment ledger sync: follow-up governance work adds the startup snapshot
and duplicate-build rules to `AGENTS.md`, adds `capability_progress_ledger_v1`
to `agent-index.json`, synchronizes the top of `llms.txt`, and marks the two
historical OTEL next-PR instructions as superseded. A read-only ledger smoke is
wired into the mainline guard to detect future drift. The report preserves the
base-commit finding while treating that specific stale instruction as remediated
by the follow-up capability-governance change.

## Executive Summary

SAEE is not missing an OTEL-to-evidence path. It already contains an implemented, tested, deliberately bounded `synthetic_opentelemetry_style` candidate-evidence mapper:

- implementation: `saee_backend/services/otel_candidate_mapping.py:1-5,151-202,262-287`;
- schema: `agent-interface/schemas/otel-candidate-evidence-mapping.schema.json`;
- CLI: `scripts/saee_agent_cli.py` (`evaluate-trace-candidate`);
- examples and negative fixtures: `agent-interface/examples/otel-mapping/`, `agent-interface/fixtures/otel-mapping/`;
- test: `scripts/saee_otel_candidate_mapping_smoke.py:29-44,77-137`;
- agent-readable status: `agent-index.json:27692-27725`.

The mapper is not OpenTelemetry ingestion, not OTLP support, not SDK/Collector integration, not trace authenticity verification, and not a production Trace-to-Evidence Bridge. It accepts one closed synthetic event, extracts non-authoritative candidate fields, and invokes the existing Evidence Adequacy evaluator while forcing `accountability_claim_established=false`. The current smoke explicitly reports `opentelemetry_sdk_imported=false`, `trace_auto_accepted_as_evidence=0`, and `adequacy_fail_after_valid_mapping=3/3`.

The repository's strongest implemented asset is the combination of:

1. closed schemas and deterministic validators;
2. claim-specific evidence adequacy profiles;
3. field and semantic-relationship evaluation with stable reason codes;
4. digest/reference binding for controlled Agent-run records;
5. strict non-authority truth boundaries;
6. local CLI, MCP, HTTP, registry, examples, and smoke-test projections.

The largest immediate weakness is architectural multiplicity and stale routing truth. The same broad capability is projected through several evaluators, schemas, product labels, and at least four MCP surfaces. At assessed commit `00d8d0467`, two historical `agent-index.json` objects still recommended adding OpenTelemetry mappings that were already registered as implemented. This was a direct agent-readable repeat-development hazard; the current worktree now marks those instructions superseded and routes Agents through `capability_progress_ledger_v1`.

The highest-value next PR is therefore not another OTEL feature. It is a canonical capability inventory and deprecation/routing repair that establishes one authoritative operation graph, marks superseded `recommended_next_pr` fields as completed, and makes every adapter delegate to canonical domain services. After that, the highest-value new capability is a read-only OTLP/Collector ingestion and normalization boundary that still produces observations/candidates rather than self-authenticating evidence.

Repository status at assessment start:

- branch: `main`;
- HEAD: `00d8d0467 Record Alibaba Marketplace submission review state`;
- working tree: clean;
- recent direction: ecosystem/marketplace state recording, worktree consolidation, Qianfan/Qoder integration conversations and bounded validation packaging;
- no existing `reports/SAEE_CAPABILITY_ASSESSMENT_REPORT.md` was present.

## Current Architecture Map

This report treats Agent Readiness and Evidence Adequacy as an external product projection and immune/evidence subsystem of the Digital Biosphere Evolution Engine. It does not reframe SAEE as an audit SDK or generic Agent framework. The product identity preserves that boundary at `docs/product/SAEE_PRODUCT_IDENTITY_V1.md:35-49`.

### Layer 1: Identity Layer

| Status | Capability | Repository evidence | Assessment |
|---|---|---|---|
| Already Implemented | Controlled-preview principal/tenant/role binding | `saee_backend/services/authorization_context.py:1-7,25-34,62-128` | HMAC-bound local authorization context exists for preview routes. It is not bound to OTEL candidate evidence and is not production identity. |
| Already Implemented | Local preview JWT verification | `saee_backend/services/jwt_preview_auth.py:1-6,26-52,108-199` | Closed HS256 claims, tenant and roles are validated locally. The module explicitly excludes production OIDC/SSO/JWKS. |
| Partially Implemented | Agent identity references inside evidence | `saee_backend/services/otel_candidate_mapping.py:38-48,167-181`; `saee_backend/services/evidence_adequacy.py:46-49,64-75` | `agent.id` and `agent_id` are correlated and relationship-checked, but identity authenticity remains false. |
| Design Only | External Agent identity model | `docs/architecture/SAEE_EXTERNAL_AGENT_INTEGRATION_DESIGN.md:46-67`; `agent-interface/integration/saee-external-agent-integration-design.v0.1.json:14-20` | Caller-declared identity is explicitly not authentication, trust, or authority. |
| Missing | POP, ARO, Persona version binding | Repository keyword scan did not locate an implemented POP/ARO/Persona-version contract in the assessed capability path. `UNKNOWN` whether these names refer to an adjacent repository standard. |
| Missing | Delegation evidence binding | Delegation appears in synthetic MCP dry-integration records and runtime routing, but no signed delegation chain is bound to evidence, trace, caller identity, scope, and expiry. |

Important distinction: the `saee_v0_8/identity/` evolution identity kernel is organism/genome identity work, not enterprise Agent authentication. It must not be cited as evidence that external Agent identity binding is solved.

### Layer 2: Runtime Observation Layer

| Status | Capability | Repository evidence | Assessment |
|---|---|---|---|
| Already Implemented | Sanitized observed-trace bundle evaluation | `scripts/saee_mcp_stdio.py:18-33,56-89,181-206`; `saee_backend/observed_trace_adapter.py` | Inline allowlisted numerical trace bundles can be evaluated and returned with receipts. No capture or authenticity verification. |
| Already Implemented | Controlled Agent-run trace digest/reference binding | `saee_backend/services/agent_run_capability.py:35-60` | Recomputed SHA-256 binds `trace.events`, `trace_ref`, and evidence export. Tamper-negative tests exist at `scripts/saee_evaluate_agent_run_mcp_smoke.py:99-115`. |
| Partially Implemented | OTel-style normalization | `saee_backend/services/otel_candidate_mapping.py:29-48,122-148,151-202` | One closed synthetic event maps an allowlisted attribute set into candidate fields. This is not a trace tree/span normalization pipeline. |
| Partially Implemented | MCP tool-call observation | MCP transcripts and local tool-call evaluators exist, including `agent_recommendation/agent_first_validation/run_005/roundtrips/` and `saee_backend/services/mcp_invocation_evaluator.py`. They evaluate bounded invocations; they do not instrument arbitrary platform tool calls. |
| Design Only | Observability composition | `agent-interface/composition/saee-capability-composition-model.v0.1.json:5-16` | SAEE is correctly modeled as consuming observability context without replacing observability. External interoperability is false. |
| Missing | Real OpenTelemetry/OTLP ingestion | No OpenTelemetry SDK import, OTLP receiver, Collector component, exporter endpoint, or production trace source integration was found. |
| Missing | General Agent trace normalization | No normalization for span hierarchy, parent/child links, resource attributes, events, links, baggage, sampling, clock skew, or current GenAI semantic conventions. |

### Layer 3: Evidence Layer

| Status | Capability | Repository evidence | Assessment |
|---|---|---|---|
| Already Implemented | Claim-specific Evidence Adequacy evaluator | `saee_backend/services/evidence_adequacy.py:24-34,57-112,198-273,311-352` | Four profiles evaluate required fields and semantic relationships with deterministic PASS/FAIL and reason codes. |
| Already Implemented | Resource-resolution receipt integrity | `agent-interface/schemas/resource-resolution-receipt.schema.json:20-29,74-75,143-151`; `saee_backend/services/resource_resolution_receipt.py` | Receipt content and receipt digest contracts exist with strict non-execution boundaries. |
| Already Implemented | Evidence Case vertical slice | `saee_backend/services/saee_evidence_case.py:138-242,250-327` | Candidate/scenario observations, adequacy, estimated risk and bounded decision support are composed into a local synthetic Evidence Case. |
| Partially Implemented | Trace -> candidate evidence -> adequacy | `saee_backend/services/otel_candidate_mapping.py:205-287` | Implemented only as candidate projection from synthetic OTel-style fields. It intentionally refuses to establish evidence truth. |
| Partially Implemented | Integrity and provenance | SHA-256 digests and internal references are checked, but issuer trust, signature verification, timestamp authority, remote attestation, and source authenticity are not generally established. |
| Missing | Signed Evidence Object trust chain | No canonical issuer/signature/delegation verification chain binds real observation producer, agent identity, tool invocation, policy decision, human approval, and immutable evidence receipt. |
| Missing | Production evidence store/ledger | Local files/receipts exist; no production tenant-isolated append-only evidence ledger with retention, access, deletion and key management evidence is established. |

### Layer 4: Governance Evaluation Layer

| Status | Capability | Repository evidence | Assessment |
|---|---|---|---|
| Already Implemented | Evidence assessment | `saee_backend/services/agent_run_capability.py:60-95` | Produces `SUPPORTED` or `INSUFFICIENT_EVIDENCE`, missing requirements, relationships and reason codes. |
| Already Implemented | Bounded decision-support recommendations | `saee_backend/services/saee_evidence_case.py:128-135,207-242` | `DEPLOY_LIMITED`, `RETEST`, or `HOLD` is derived under declared synthetic thresholds, with `automatic_decision=false`. |
| Partially Implemented | Readiness recommendation | Qianfan-facing code produces `conditional`/`replan` and evidence coverage; tests at `scripts/saee_qianfan_readiness_mcp_smoke.py:58-120`. Scores are coverage, not safety/reliability probability. |
| Partially Implemented | Risk assessment | Synthetic estimates and failure/stability analysis exist; empirical risk probability, calibration and real-world generalization remain false. |
| Missing by design | Authorization/policy enforcement | `docs/architecture/SAEE_AGENT_CAPABILITY_ECOSYSTEM_INTEGRATION.md:1-24` and the composition matrix keep authorization and policy as separate authorities. SAEE must not silently fill this gap. |
| Missing | Production-grade human-review decision record | Human-review requirements are modeled, but authenticated approver identity, delegation, approval scope, expiry, revocation and evidence-linked decision receipts are not end-to-end implemented. |

### Layer 5: Integration Layer

| Status | Capability | Repository evidence | Assessment |
|---|---|---|---|
| Already Implemented | CLI | `scripts/saee_agent_cli.py`, including evidence and trace-candidate commands | Local closed-file operation is implemented. |
| Already Implemented | Local MCP implementations | `scripts/saee_mcp_stdio.py`; `saee_backend/services/local_mcp_server.py`; `saee_backend/services/capability_mcp_adapter.py`; `saee_backend/services/qianfan_readiness_mcp_adapter.py` | Multiple functioning local surfaces exist, which is both a capability and a consolidation risk. |
| Already Implemented | Local FastAPI shell | `saee_backend/main.py:1-40,61-82`; `saee_backend/api/experiment.py:28-64` | Local API routes, preview security and readiness endpoints exist. This is not a public production API. |
| Already Implemented | CI validation | `.github/workflows/mainline_guard.yml`; `.github/workflows/tests.yml` | Mainline guard and `make check` run in GitHub Actions. |
| Partially Implemented | HTTP capability adapter | `saee_backend/services/capability_http_adapter/` | Local transport exists; public deployment, authentication/tenancy evidence and external interoperability are not established. |
| Partially Implemented | Provider/platform adapters | Qianfan/Qoder/LangChain/CrewAI/Claude Code config/examples exist under `adapters/` and `agent-interface/qianfan/` | Mostly bounded local descriptors, demos or provider-specific facades, not verified production plugins. |
| Design Only | SDK | `phase_b_product/sdk_layer/saee_client_api.md:1-13,121-128`; `phase_b_product/sdk_layer/abstraction_interface.md:1-13` | Documentation-only abstraction; no released client library. |
| Design Only | External Agent integration | `docs/architecture/SAEE_EXTERNAL_AGENT_INTEGRATION_DESIGN.md:167-188,203-231` | Gate is `HOLD`; no external Agent, trusted identity, public MCP or production tenant system. |
| Missing | GitHub Action product integration | CI workflows test SAEE itself, but no `action.yml`/`action.yaml` consumer integration was found. |
| Missing | Public service and verified interoperability | `.well-known/saee-capability-index.json:18-21`; `agent-interface/public/saee-public-capability-surface.v0.1.json:49-69` | Public metadata is prepared; public API/service and external interoperability are false. |

## Implemented Capabilities

The following are supported by code plus tests, within the stated local/synthetic boundary:

1. Evidence Adequacy Profiles for `RESOURCE_AUTHENTICITY`, `AUTHORIZED_AGENT_ACTION`, `HUMAN_OVERSIGHT`, and `EXECUTION_BOUNDARY`.
2. Strict schema and unknown-field rejection, duplicate-key handling, timestamp/reference checks, and stable reason codes.
3. Semantic relationships including receipt validity, reference equality, scope coverage, authority-window checks, approval-before-action, and causal digest binding.
4. Synthetic OTel-style candidate extraction and routing into adequacy evaluation.
5. Sanitized observed-trace bundle comparison, stability/failure/survival/ranking outputs and receipts.
6. Rehearsal-run trace digest and evidence-export binding.
7. Local Agent readiness/evidence evaluation operations.
8. Local MCP transports, Capability Runtime routing, local HTTP/FastAPI surfaces and CLI.
9. Capability discovery, registry, public-surface schemas, `agent-index.json`, `llms.txt`, `.well-known` metadata and truth-consistency validators.
10. Local preview authentication/authorization controls and tenant-scoped API scaffolding.
11. Extensive offline smoke coverage and CI gates.

Validation run during this assessment:

| Validator | Result | Key boundary evidence |
|---|---|---|
| `scripts/saee_otel_candidate_mapping_smoke.py` | PASS | 3/3 positive, 3/3 negative, 7/7 adversarial, 15/15 deterministic; SDK imported false; trace auto-accepted 0 |
| `scripts/saee_evidence_adequacy_smoke.py` | PASS | 4/4 positive, 4/4 negative, 16/16 adversarial, 20/20 deterministic |
| `scripts/saee_evaluate_agent_run_mcp_smoke.py` | PASS | 3/3 valid, 6/6 invalid; trace binding preserved; standard transport/public endpoint false |
| `scripts/saee_capability_mcp_adapter_smoke.py` | PASS | 3/3 discovery, 3/3 runtime delegation, 12/12 invalid; external interoperability false |
| `scripts/saee_mcp_stdio_smoke.py` | PASS | 20/20 transcript, 100 mixed requests, file writes 0 |
| `scripts/saee_qianfan_readiness_mcp_smoke.py` | PASS | 2 tools, 3 demos; network/external execution/production false |
| `scripts/saee_public_capability_surface_smoke.py` | PASS | public metadata true; public deployment/API/service false |
| `scripts/saee_capability_truth_consistency_smoke.py` | PASS | 8/8 sources, 11/11 invalid; release/adoption/customer/production false |

One maintenance warning appeared: `scripts/saee_evidence_adequacy_smoke.py` imports deprecated `jsonschema.RefResolver`; a future `jsonschema` release may remove it. This is not a current capability failure but should enter dependency-maintenance backlog.

## Partial Capabilities

1. **OTel mapping:** real code, but synthetic single-event input only.
2. **Trace-to-evidence bridge:** real candidate projection and adequacy routing, but no automatic elevation to evidence and no real trace authenticity.
3. **Agent identity:** IDs are carried and compared; authentication is separate and not bound end-to-end to trace/evidence.
4. **Authorization context:** local preview principal/tenant/route binding exists; no production identity provider or evidence-linked authorization receipt.
5. **MCP tool-call evidence:** local transcripts and invocation evaluation exist; arbitrary runtime instrumentation and external tool provenance do not.
6. **Integrity:** SHA-256 bindings exist; general signatures, issuer trust and attestation do not.
7. **Readiness:** evidence coverage and bounded recommendation exist; safety, compliance and deployment authority do not.
8. **API/MCP/platform integration:** local facades exist; public service, standardized external interoperability and production tenancy do not.
9. **SDK:** conceptual documentation exists; no released library.
10. **Commercial packaging:** assessment packages and marketplace materials exist; customer validation and production readiness remain false.

## Missing Capabilities

The following are `NOT IMPLEMENTED` as production or real-external capabilities:

- OTLP receiver, OpenTelemetry SDK/Collector integration, or trace-source connector;
- normalized general span/trace graph ingestion;
- verified trace producer identity and authenticity;
- end-to-end Agent identity + persona/version + delegation binding;
- signed policy-decision and human-approval receipts;
- cryptographically verifiable multi-party evidence chain;
- production tenant-isolated evidence ledger;
- public MCP/API service;
- released SDK;
- consumer-facing GitHub Action;
- verified LangChain/CrewAI/Qianfan/etc. production interoperability;
- production policy enforcement or execution control;
- empirical safety/reliability probability;
- independent external validation and customer decision-value evidence.

## OTEL / Agent Evidence Status

### 1. OpenTelemetry trace ingestion

**NOT IMPLEMENTED.**

Evidence:

- `saee_backend/services/otel_candidate_mapping.py:1-5` explicitly says no OpenTelemetry SDK or network access.
- Input must have `trace_source=synthetic_opentelemetry_style` (`:21-23,122-148`).
- `docs/OTEL_CANDIDATE_EVIDENCE_MAPPING.md:5-9,85-91` states this is not SDK integration or compliance.
- Test rejects `trace_source=real_opentelemetry` at `scripts/saee_otel_candidate_mapping_smoke.py:127-129`.

### 2. Agent trace normalization

**PARTIALLY IMPLEMENTED.**

Implemented: closed allowlist mapping of `agent.id`, action/tool/resource/human/sandbox/status fields at `saee_backend/services/otel_candidate_mapping.py:38-48,167-181`.

Not implemented: OTLP decoding, span graph reconstruction, semantic-convention versioning, event/link/resource handling, platform-specific adapters and real source provenance.

### 3. Trace -> Evidence Object conversion

**PARTIALLY IMPLEMENTED AS CANDIDATE MAPPING; NOT IMPLEMENTED AS A TRUSTED CONVERSION.**

`map_otel_candidate()` creates candidate fields; `_candidate_package()` creates a bounded adequacy input; `evaluate_trace_candidate()` invokes the evaluator (`saee_backend/services/otel_candidate_mapping.py:151-202,205-287`). The same function forces `accountability_claim_established=false`. Therefore “bridge exists” is true only if named **OTel-style observation -> candidate evidence -> adequacy evaluation**.

### 4. Evidence -> Readiness Recommendation

**IMPLEMENTED LOCALLY, PARTIAL FOR ENTERPRISE USE.**

- `saee_backend/services/agent_run_capability.py:60-95` returns `SUPPORTED` or `INSUFFICIENT_EVIDENCE`.
- `saee_backend/services/saee_evidence_case.py:128-135,207-242` returns bounded `DEPLOY_LIMITED`/`RETEST`/`HOLD` decision support.
- Qianfan product projection returns `conditional`/`replan` and evidence coverage.

All outputs explicitly deny deployment authority, safety certification and production readiness.

### 5. MCP tool-call evidence

**PARTIALLY IMPLEMENTED.**

MCP servers, tool schemas, roundtrip transcripts and invocation evaluators are implemented. The repository can prove what its controlled local adapters received and returned under fixed tests. It cannot yet ingest or authenticate arbitrary MCP runtime calls from an enterprise Agent platform.

### 6. Identity binding

**PARTIAL LOCALLY; NOT IMPLEMENTED END-TO-END.**

Local preview JWT and HMAC-bound principal/tenant/route context exist. OTel candidate identity remains an observation, and `evidence_adequacy.py:106-112` keeps `identity_independently_verified=false`. No binding connects a production identity provider, the trace producer, the Agent version, evidence object and evaluation receipt.

### 7. Delegation binding

**NOT IMPLEMENTED.**

`runtime_delegation` in dry-integration results describes internal code routing, not authority delegation. No signed delegator/delegatee, scope, purpose, expiry, revocation, chain, trace reference and evidence receipt contract was found.

## Duplicate / Consolidation Risk

No byte-identical duplicate Python files were found by SHA-256 scan across `scripts/` and `saee_backend/`. The risk is architectural and semantic duplication, not simple copy-paste identity.

### Risk 1: Four overlapping MCP surfaces

1. `scripts/saee_mcp_stdio.py`: `describe_saee`, `compare_observed_traces`.
2. `saee_backend/services/local_mcp_server.py`: in-memory `evaluate_evidence_adequacy`, `evaluate_agent_run`.
3. `saee_backend/services/capability_mcp_adapter.py`: Capability Runtime projection of `evaluate_agent_run`, `evaluate_evidence`, `rehearse_agent`.
4. `saee_backend/services/qianfan_readiness_mcp_adapter.py`: provider-facing `saee.evaluate_agent_run`, `saee.evaluate_evidence` calling `baidu_agent_readiness_service` directly.

Each repeats some combination of protocol negotiation, JSON-RPC validation, limits, tool listing, response projection and boundary statements. Tool names and domain semantics differ across surfaces.

**Keep:**

- `capability_runtime` as the canonical internal invocation/router/receipt layer;
- canonical public operation IDs `saee.evaluate_agent_run` and `saee.evaluate_evidence` from `.well-known/saee-capability-index.json:5-12`;
- `evidence_adequacy.py` and `agent_run_capability.py` as canonical domain evaluators;
- observed-trace evaluation as a separate internal domain capability until it is explicitly promoted.

**Consolidate:**

- provider adapters should translate provider envelopes and delegate into Capability Runtime, not maintain independent readiness semantics;
- JSON-RPC protocol handling should be one reusable adapter with declared profiles/tool allowlists;
- old local prototype surfaces should receive lifecycle status (`canonical`, `provider_facade`, `internal_experimental`, `deprecated`) and replacement references.

### Risk 2: Two evidence/readiness semantics

`evidence_adequacy.py` evaluates claim-specific fields and relationships. `baidu_agent_readiness_service.py` evaluates required evidence-type coverage and returns product readiness labels. Both are useful, but today they can look like competing definitions of “evaluate evidence.” Provider-specific code should compose or project a canonical result, not become a second domain truth.

### Risk 3: Stale `recommended_next_pr` created repeat-development instructions

- At assessed commit `00d8d0467`, `evidence_adequacy_profile_v0_1` recommended `Add OpenTelemetry-to-SAEE Evidence Adequacy Mapping`.
- At the same commit, `external_resource_resolution_receipt_v0_1` recommended `Add OpenTelemetry-to-SAEE resource event mapping`.
- `otel_candidate_evidence_mapping_v0_1` already recorded the mapping as implemented and tested.

This was the concrete cause of the earlier mistaken command. The current worktree preserves both historical values as `superseded_recommended_next_pr`, changes their active recommendation to canonical inventory/routing work, and adds a startup-visible duplicate-build gate. The remaining risk is regression if future capability changes are not synchronized across the required ledger surfaces.

### Risk 4: Product/narrative surfaces have multiple eras

The FastAPI shell describes a black-box long-term competition evaluator (`saee_backend/main.py:17-20`), older buyer material emphasizes long-term stability (`agent_recommendation/BUYER_QUESTIONS_AND_ANSWERS.md:3-20`), while the frozen external product is Agent Readiness (`docs/product/SAEE_PRODUCT_IDENTITY_V1.md:3-22`). These can coexist only if marked as core capability, legacy product label, internal experimental surface, or current public product projection.

### Risk 5: Repository breadth obscures canonical code

The assessment counted approximately:

- 36,578 files excluding selected build/venv paths;
- 987 top-level Python scripts;
- 180 Python files under `saee_backend`;
- 569 files under `agent-interface`;
- 845 files under `docs`.

The problem is not that every file is redundant. The problem is that retrieval cost and stale-status probability are now high enough to affect development decisions. A smaller canonical graph is needed before more adapters are added.

## Competitive Position

This section compares categories by current code behavior. It does not claim current market superiority or uniqueness.

| Category | What that category primarily owns | What SAEE currently owns | Current difference |
|---|---|---|---|
| OpenTelemetry GenAI observability | Capture/export spans, logs, metrics and semantic telemetry | Candidate mapping plus evidence adequacy and bounded recommendations | SAEE adds claim/evidence relationship evaluation, but lacks real telemetry ingestion. It should consume observability, not replace it. |
| LangSmith-style trace platform | Trace capture, debugging, run exploration, eval workflow and dashboards | Offline deterministic evidence/reliability evaluation | SAEE is stronger on explicit non-authority boundaries and missing-evidence reason codes; far weaker on capture, UX, platform integration and operational maturity. |
| Agent security scanner | Code/config/runtime vulnerability and attack-surface detection | Evidence coverage and controlled reliability context | SAEE does not scan unknown code, detect vulnerabilities broadly, or certify security. Security scanners remain separate inputs/partners. |
| Policy engine | Evaluate/enforce allow/deny policy in runtime | Evaluate whether evidence supports a bounded accountability claim | SAEE is context, not authority. This separation is correctly modeled in `agent-interface/composition/saee-capability-interoperability-matrix.v0.1.json:4-15`. |
| Execution proof system | Cryptographic/attested proof that an action occurred under a trusted identity and environment | Digests, receipts, reference/relationship checks and truth boundaries | SAEE has useful proof-building primitives but lacks general issuer trust, signatures, remote attestation and real trace authenticity. It cannot currently claim execution proof. |

### What is genuinely differentiated today?

The most differentiated implemented combination is:

> deterministic, fail-closed evaluation of whether a closed evidence package satisfies claim-specific field and semantic-relationship requirements, with explicit missing requirements, stable reason codes, and machine-enforced non-authority boundaries.

This is a credible technical position and complements observability, authorization, policy and execution systems.

### Is it proven “irreplaceable”?

**UNKNOWN / NOT ESTABLISHED.**

The repository proves local implementation and internal consistency. It does not contain independent competitive evaluation, external customer substitution evidence, adoption data, or a verified survey establishing that no competing system can provide the same combination. SAEE should claim a distinctive composition, not market uniqueness.

## Commercial Readiness

Canonical internal commercial truth already reports `commercial_ready=false`, `pilot_ready=false`, `production_ready=false`, `enterprise_ready=false`, and `customer_validated=false` at `agent-interface/commercial/saee-commercial-readiness.v0.1.json:1-16`.

| Enterprise question | Result | Evidence-based answer |
|---|---|---|
| “我的 Agent 上线前是否安全？” | PARTIAL | SAEE can report evidence coverage, missing controls, controlled-run reliability context and bounded recommendations. It explicitly cannot establish safety or authorize deployment (`agent_run_capability.py:74-91`). |
| “发生事故后能否证明发生了什么？” | PARTIAL | SAEE can validate submitted trace/evidence structure, digests and internal references. It cannot prove trace authenticity, real occurrence, trusted identity or complete chain of custody. |
| “为什么允许 Agent 继续执行？” | PARTIAL | SAEE can provide reason codes, evidence adequacy and a non-authoritative decision context. The actual allow/deny must come from a separate authenticated authorization/policy authority. |
| “为什么要求人工审核？” | YES, within the bounded assessment scope | Missing requirements, failed relationships, limitations and explicit human-control boundaries explain why escalation/review is required. SAEE does not itself prove that the reviewer was authorized or that review occurred. |
| “能否接入现有 Agent 平台？” | PARTIAL | Local MCP, HTTP, CLI, schemas and adapter examples exist. There is no public service, released SDK, real OTLP ingestion, verified external interoperability or production tenancy. |

### Why would an enterprise buy SAEE today?

The only repository-supported buyable shape today is a bounded manual/offline assessment or design-partner review, not production platform software. The value proposition is:

- turn a specific Agent readiness/accountability question into a closed evidence contract;
- identify unsupported claims and missing evidence relationships;
- produce deterministic machine-readable assessment artifacts;
- preserve a clear boundary between observation, evidence, recommendation and authority.

This matches `agent-interface/commercial/saee-commercial-readiness.v0.1.json:24-29,69-84`. Any statement that SAEE is already a production safety platform, execution-proof authority, customer-validated product, or public MCP service would exceed repository evidence.

## Strategic Gaps

Ranking basis: commercial value x technical barrier x urgency. Scores are qualitative repository judgments, not market measurements.

### 1. Canonical capability graph and lifecycle/deprecation truth

- Impact: **Critical**
- Commercial value: High
- Technical barrier: Medium
- Urgency: Critical
- Evidence: the assessed base commit contained two conflicting OTEL next-PR pointers; the current worktree has locally remediated those pointers, while four MCP surfaces still overlap and the broader canonical graph remains incomplete.
- Why it matters: Agents and partners cannot safely plan integration when “design only,” “local prototype,” “public operation,” “provider facade,” and “deprecated” are not resolved through one canonical graph.

### 2. Real read-only OTLP ingestion and normalized observation envelope

- Impact: **High**
- Commercial value: High
- Technical barrier: High
- Urgency: High
- Evidence: existing mapper requires `synthetic_opentelemetry_style`; commercial readiness explicitly lists automatic OTEL ingestion as a later improvement (`agent-interface/commercial/saee-commercial-readiness.v0.1.json:86`).
- Why it matters: Without a standard input path, enterprise teams must manually reshape evidence, weakening adoption and repeatability.

### 3. Verifiable identity, delegation and provenance binding

- Impact: **High**
- Commercial value: High
- Technical barrier: High
- Urgency: High
- Evidence: external identity is declaration-only (`docs/architecture/SAEE_EXTERNAL_AGENT_INTEGRATION_DESIGN.md:46-67`); delegation binding is absent; trace authenticity is false.
- Why it matters: This blocks credible answers to “who acted,” “under whose authority,” and “can this record support incident reconstruction?”

### 4. One production-oriented integration surface with verified interoperability

- Impact: **High**
- Commercial value: High
- Technical barrier: Medium-High
- Urgency: Medium-High
- Evidence: `.well-known` and public surface declare no public API/service; SDK is documentation-only; external integration gate is `HOLD`.
- Why it matters: Multiple local demos do not equal a supportable platform integration. A single canonical MCP/HTTP surface, authentication/tenant boundary and conformance suite is required before GitHub Action or marketplace plugin expansion.

### 5. External calibration and decision-value evidence

- Impact: **High**
- Commercial value: Critical
- Technical barrier: Medium
- Urgency: Medium
- Evidence: customer/external/production validation flags remain false; risk scores are synthetic estimates and internal benchmarks.
- Why it matters: The repository shows that the machinery is internally consistent, not that it improves a real enterprise launch or incident decision. External activity still requires explicit authorization, privacy/data-use and support gates.

## Recommended Next PRs

### PR 1: Canonical Capability Inventory, Routing and Deprecation Map v1

- Goal: create one machine-readable capability graph mapping capability ID -> canonical domain service -> canonical schema -> supported transports -> lifecycle -> provider facades -> superseded artifacts -> validation command.
- Why now: it immediately prevents repeat development and makes the repository agent-readable at its current scale.
- Commercial blocker solved: partner/customer confusion about which operation is real, local, public, provider-specific or obsolete.
- Expected impact: very high reduction in duplicate PRs, schema drift and integration ambiguity.
- Required scope:
  - mark the stale OTEL `recommended_next_pr` entries completed/superseded (completed in the post-assessment ledger sync);
  - declare `evidence_adequacy.py`, `agent_run_capability.py` and Capability Runtime as canonical domain/routing services;
  - classify all MCP/HTTP/provider surfaces;
  - add a validator that rejects an active next-PR recommendation when its target capability is already implemented;
  - preserve historical objects without presenting them as current development direction.
- Evolution subsystem strengthened: Evolutionary Archive / Rollback Immune System.
- Recommendation gate: **recommend**. The need is discoverability and architecture integrity, not a new audit product.

### PR 2: Read-Only OTLP Observation Ingestion and Normalization v0.1

- Goal: accept a bounded offline OTLP JSON export or Collector-produced sanitized fixture, normalize it into a versioned SAEE Observation Envelope, and route only allowlisted observations into the existing candidate mapper/evaluator.
- Why now: only after PR 1 establishes the canonical path; this is the missing standard entrance, not a duplicate mapper.
- Commercial blocker solved: “Can SAEE consume the trace data we already have?”
- Expected impact: high increase in integration credibility and reduced manual transformation.
- Non-negotiable boundaries:
  - no network listener in the first PR;
  - no automatic evidence elevation;
  - explicit semantic-convention version and unsupported-field reporting;
  - provenance/source attestation fields remain unverified unless separately verified;
  - no raw prompts, secrets or uncontrolled customer data;
  - no OpenTelemetry conformance claim without conformance evidence.
- Evolution subsystem strengthened: Global Sensing -> Trait Extraction.
- Recommendation gate: **conditional** today. It becomes `recommend` only after canonical routing, input/privacy boundaries, and a non-duplication check are recorded.

### PR 3: Evidence Provenance, Identity and Delegation Binding v0.1

- Goal: define and implement a closed, verifiable receipt binding observation producer, Agent/version, delegator/delegatee, scope, policy decision, tool/action reference, evidence digest, evaluator version and result receipt.
- Why now: it addresses the highest-trust gap after standard ingestion exists.
- Commercial blocker solved: “Who acted, under whose authority, and what exactly does the record prove?”
- Expected impact: high for incident review, governance composition and enterprise trust; also reduces overclaim risk.
- Non-negotiable boundaries:
  - verification is not authorization;
  - signatures prove key possession/integrity only within a declared trust policy;
  - no remote execution or permission expansion;
  - revocation/expiry and partial-chain results must fail closed;
  - human approval remains a separately authenticated authority event.
- Evolution subsystem strengthened: Evolutionary Archive / Rollback Immune System and Pareto Fitness Evaluation inputs.
- Recommendation gate: **conditional**. First create the evolution proposal and trust-model threat analysis; do not jump directly to a broad identity platform.

### What should not be the next PR

- another synthetic OTEL field mapper;
- another independent MCP server with new tool names;
- a GitHub Action before the canonical operation and real input contract are stable;
- a marketplace/cloud plugin that wraps local synthetic behavior as production integration;
- an authorization or safety-certification claim;
- a generic audit-SDK reframing.

## Risk Assessment

| Risk | Severity | Evidence | Mitigation |
|---|---|---|---|
| Repeat development from stale agent-readable status | Critical at base commit; locally mitigated | Historical OTEL next-PR instructions conflicted with the implemented mapping | Complete PR 1 and validate active roadmap pointers against the implemented registry |
| Multiple MCP/evaluator semantics drift | High | Four overlapping MCP surfaces; provider service bypasses canonical runtime | Canonical domain services and adapter delegation rules |
| OTEL overclaim | High | Mapper name can be read as real integration; SDK/ingestion absent | Always say “synthetic OTel-style candidate mapping” until OTLP evidence exists |
| Evidence/proof overclaim | High | Digests exist but identity/authenticity/signature chain incomplete | Explicit evidence levels and verified/unverified provenance fields |
| Audit-first narrative drift | High | Evidence subsystem is commercially visible and extensive | Tie every PR to the evolution loop; preserve Product Identity core boundary |
| Local synthetic validation saturation | High | Many PASS results, external/customer/production flags false | Separate contract correctness from external utility/calibration |
| Agent discoverability degradation from repository scale | High | 987 scripts, 845 docs, large agent index | Canonical graph, lifecycle tags, generated indexes, archive separation |
| Dependency maintenance | Medium | `jsonschema.RefResolver` deprecation warning | Migrate smoke/schema resolution to `referencing.Registry` |
| Public/product status ambiguity | Medium-High | local public metadata, marketplace states and provider packages coexist | Keep prepared/submitted/reviewing/listed/deployed/adopted statuses separate |

## Final Judgment

If SAEE were placed into the enterprise Agent ecosystem today, its largest advantage would be its deterministic, agent-readable, fail-closed evidence-adequacy and bounded readiness context; its largest weakness would be the absence of a canonical, externally verified observation-to-identity/delegation/evidence integration path, compounded by overlapping adapters and stale next-step metadata.
