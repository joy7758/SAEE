# SAEE Agent Interface

Read `agent-manifest.json` first. This directory is the canonical compact
front door for coding, retrieval, citation, and recommendation agents.

## What SAEE currently does

SAEE runs a deterministic local `synthetic_descriptor_simulation` over
non-executable candidate descriptions. It returns:

- evaluation summary and decision result;
- stability reports;
- failure-mode reports;
- survival curves;
- comparison ranking;
- provenance and non-capability boundaries.

It does not run submitted agents, repositories, scripts, or external systems.
The synthetic mode remains integration and decision-prototyping evidence.

SAEE also accepts strict, sanitized, file-backed observed trace bundles. It
evaluates only allowlisted numerical quality, alive, failure-code, severity,
censoring, and comparability fields. It does not capture traces or accept raw
prompts, messages, tool payloads, code, URLs, secrets, or arbitrary logs. Source
sanitization and authorization are attestations; SAEE does not verify source
authenticity or prove absence of PII.

## One-command call

```bash
python3 scripts/saee_agent_cli.py evaluate \
  --input agent-interface/examples/evaluation-request.json
```

The command needs no server, browser, network, or human click. Successful
stdout is one JSON receipt. Exit code `0` means success. Invalid input returns a
JSON error object and exit code `2`.

Errors match `agent-interface/schemas/agent-error.schema.json`. Receipt hashes
use SHA-256 over UTF-8 JSON with sorted keys, `ensure_ascii=false`, and no
insignificant whitespace. `request_sha256` covers the Pydantic-normalized
request; `content_sha256` covers the five report fields named in the manifest.

Write the same receipt to an explicit path when needed:

```bash
python3 scripts/saee_agent_cli.py evaluate \
  --input agent-interface/examples/evaluation-request.json \
  --output /tmp/saee-evaluation-receipt.json
```

Inspect the machine manifest:

```bash
python3 scripts/saee_agent_cli.py describe
```

Evaluate a sanitized observed trace bundle:

```bash
python3 scripts/saee_agent_cli.py evaluate-traces \
  --input agent-interface/examples/observed-trace-bundle.json
```

Validate a synthetic, offline external resource-resolution receipt:

```bash
python3 scripts/saee_agent_cli.py validate-resource-resolution \
  --input agent-interface/examples/verified-resource-resolution.json
```

This command does not dereference the URI, read an external resource, install
or import a package, start a subprocess, or execute candidate code. It checks a
closed receipt, recomputes the bounded synthetic content SHA-256 and receipt
digest, and returns stable reason codes with exit code `2` on rejection. See
`docs/RESOURCE_RESOLUTION_EVIDENCE.md` for proof and non-proof boundaries.

Evaluate whether a closed synthetic evidence package satisfies one canonical
accountability-claim profile:

```bash
python3 scripts/saee_agent_cli.py validate-evidence-adequacy \
  --profile RESOURCE_AUTHENTICITY \
  --input agent-interface/examples/evidence-adequacy/resource_authenticity_pass.json
```

Exit code `0` means the file-backed profile requirements are satisfied; it does
not mean the accountability claim is established in the real world. The result
keeps `accountability_claim_established=false`. See
`docs/EVIDENCE_ADEQUACY_PROFILE.md`.

Map a closed synthetic OpenTelemetry-style observation into candidate evidence
and immediately evaluate it against an adequacy profile:

```bash
python3 scripts/saee_agent_cli.py evaluate-trace-candidate \
  --profile RESOURCE_AUTHENTICITY \
  --input agent-interface/examples/otel-mapping/trace_candidate_resource_retrieval.json
```

A successful mapping may still have `adequacy_result=FAIL`, and every result
keeps `accountability_claim_established=false`. This is not an OpenTelemetry SDK
integration or compliance claim. See `docs/OTEL_CANDIDATE_EVIDENCE_MAPPING.md`.

Run the accepted SAEE v3 Phase 1 Evidence Case Object vertical slice:

```bash
python3 scripts/saee_agent_cli.py run-assurance-case \
  --input agent-interface/architecture/examples/saee-evidence-case-synthetic-001.json
```

The command compares two synthetic candidate references across two synthetic
scenarios, reuses the existing Evidence Adequacy evaluator, calculates a
declared scenario risk estimate, and returns scenario-scoped Decision Support.
It does not execute an Agent, measure a production probability, use customer
data, make an automatic decision, or authorize deployment. See
`docs/architecture/SAEE_PHASE1_SYNTHETIC_VERTICAL_SLICE.md`.

Validate the five-case Phase 1.5 benchmark corpus and the Source Case to
Derived Evidence Case transformation:

```bash
python3 scripts/saee_phase1_5_case_corpus_smoke.py
```

The corpus covers baseline stability, context drift, tool failure,
instruction conflict, and adversarial input using synthetic declarations only.
It does not change the v0.1 source schema or execute any Agent, tool, dependency,
or adversarial payload. See
`docs/architecture/SAEE_PHASE1_5_EVIDENCE_CASE_CORPUS.md`.

Validate the Phase 1.75 receive-only Observation Envelope contract:

```bash
python3 scripts/saee_observation_contract_smoke.py
```

The contract records producer, source, authorization and sanitization
attestations, ordered event summaries and digests, and privacy references. It
does not capture raw content, implement an adapter, establish Evidence or
authorization, or authorize deployment. See
`docs/architecture/SAEE_PHASE1_75_OBSERVATION_CONTRACT.md`.

Validate the bounded SAEE-owned Agent Evidence clean-room trait adapter:

```bash
python3 scripts/saee_agent_evidence_trait_adapter_smoke.py
```

The adapter consumes only closed synthetic fixtures, preserves source identity,
completeness and upstream `PASS/WARN/FAIL`, and replaces payloads with digests.
It locally checks a bounded ASCII/integer canonicalization subset, event chain,
Merkle root and optional Ed25519 signature. It does not execute the historical
repository, claim full RFC 8785 or source authenticity, establish evidence
adequacy, authorize action or integrate a runtime. See
`agent-interface/integration/agent-evidence-compatibility/README.md`.

Validate the bounded Evidence-to-Evaluation bridge:

```bash
python3 scripts/saee_agent_evidence_evaluation_bridge_smoke.py
```

The bridge validates declared adapter/event bindings and calls the existing
SAEE evidence-adequacy evaluator with a separate closed package. Even when
local integrity and adequacy both pass, its strongest decision is
`HUMAN_REVIEW`; authenticity, authorization, runtime integration and production
readiness remain false.

Validate the Phase 1.9 Observation Replay governance contract:

```bash
python3 scripts/saee_observation_replay_contract_smoke.py
```

Replay means metadata-context reconstruction planning, not Agent execution.
The contract requires frozen source-envelope references, Consent and data-use
references, content exclusions, transformation provenance, an environment and
window, and manual stop authority. It does not execute Replay or authorize
deployment. See
`docs/architecture/SAEE_PHASE1_9_OBSERVATION_REPLAY_CONTRACT.md`.

Validate the Phase 1.95 Replay Evaluation mapping contract:

```bash
python3 scripts/saee_replay_evaluation_contract_smoke.py
```

This contract binds a local synthetic Replay Contract and its Observation,
Consent, permission, and transformation references to a pre-existing
Evaluation Input. The mapping rules are declarative and non-executable. Replay
does not generate risk, make a decision, or authorize deployment. See
`docs/architecture/SAEE_PHASE1_95_REPLAY_EVALUATION_CONTRACT.md`.

Validate the Phase 1.97 Evaluation Run lifecycle contract:

```bash
python3 scripts/saee_evaluation_run_contract_smoke.py
```

Each local synthetic Run Contract binds one Evaluation Input, one Replay
Evaluation Contract, declared Evaluator/Grader/Criteria versions, one
deterministic result, and one Derived Evidence Case. It records lineage but does
not implement a real Evaluator Runtime, execute an Agent, measure production
risk, make an automatic decision, or authorize deployment. See
`docs/architecture/SAEE_PHASE1_97_EVALUATION_RUN_CONTRACT.md`.

Validate the Phase 1.98 Evaluation Run Termination contract:

```bash
python3 scripts/saee_run_termination_contract_smoke.py
```

Termination Contracts record why a reserved or started local synthetic Run did
not produce a completed Result or Evidence Case. Manual abort, runtime failure,
and pre-start input rejection retain Input, Replay Evaluation, Operator, and
Stop Authority lineage. Partial results remain non-evidence, and no deployment
authority is created. See
`docs/architecture/SAEE_PHASE1_98_RUN_TERMINATION_CONTRACT.md`.

Run the Phase 2A fail-closed readiness gate before any synthetic pipeline
implementation:

```bash
python3 scripts/saee_phase2a_readiness_gate.py
```

The gate validates 20 local contract objects, frozen hashes, synthetic-only
content, no-execution boundaries, human control, lifecycle exclusivity, and ten
negative boundary probes. `PHASE2A_GATE_PASS` means only that a separate local
synthetic implementation task may proceed; this gate executes no Replay,
Mapping, Evaluator, Agent, Tool, or external action. See
`docs/strategy/SAEE_PHASE2A_READINESS_GATE.md`.

Run the fixed local synthetic Phase 2A pipeline after the gate passes:

```bash
python3 scripts/saee_phase2a_synthetic_runner.py \
  --input agent-interface/architecture/examples/replay-evaluation/synthetic-replay-evaluation.json \
  --lifecycle completed
```

The Runner rechecks the gate, accepts only three allowlisted local mapping
contracts, validates their Replay Contract bindings, loads the pre-existing
Evaluation Input, ignores Mapping Rules as executable code, and emits exactly
one Completed or Terminated lifecycle path. It does not reconstruct Observation
metadata or regenerate Evaluation Input. Completed output includes a valid
Evaluation Run Contract and Derived Evidence Case; terminated output includes
no Evidence. The report therefore states
`fixed_evaluation_input_pipeline_executed=true` only on the Completed path,
`synthetic_replay_contract_validated=true`,
`synthetic_metadata_reconstruction_applied=false`, and
`synthetic_offline_replay_executed=false`. No Agent, Tool, Network, customer
data, external code, dependency installation, automatic decision, or deployment
is allowed. See
`docs/architecture/SAEE_PHASE2A_SYNTHETIC_EXECUTION.md`.
The Phase 2B Gate is defined and a separately authorized local synthetic
Observation Adapter prototype now exists. The Gate itself creates no Adapter;
all non-synthetic Adapter, real Agent, Network, and customer-data work remains
on hold.

Validate the Phase 2B receive-only Observation Adapter entry boundary:

```bash
python3 scripts/saee_phase2b_adapter_readiness_gate.py
```

This read-only gate permits only future `local_file` and `bounded_stdio` input,
requires a read-once immutable byte snapshot, and restricts any future Adapter
to an Observation Envelope output. It creates no Adapter and keeps Evidence,
Risk, Decision, Agent/Tool/Memory control, Network, raw content, customer data,
and production authority disabled. See
`docs/strategy/SAEE_PHASE2B_ADAPTER_READINESS_GATE.md`.

Validate the Phase 2B-0 Adapter implementation-state and output-binding
sidecar contract:

```bash
python3 scripts/saee_adapter_provenance_contract_smoke.py
```

The strict contract separates `declared`, `prototype`, and `validated` binding
states without modifying Observation Envelope v0.1. Prototype and validated
records bind one immutable local synthetic input snapshot to one Observation
Envelope by SHA-256. All included records are synthetic examples; no Adapter,
real Agent, Network, Evidence, Risk, Decision, termination authority, customer
data, or production capability is created. See
`docs/architecture/SAEE_PHASE2B0_ADAPTER_PROVENANCE_CONTRACT.md`.

Run the first local synthetic receive-only Observation Adapter prototype:

```bash
python3 scripts/saee_synthetic_observation_adapter_smoke.py
```

The prototype reads one repository-local synthetic input snapshot exactly once,
checks its expected SHA-256, processes those same bytes, emits a schema-valid
Observation Envelope v0.1, and binds the output through a
`implementation_status=prototype` Adapter Provenance sidecar. Raw prompt,
output, hidden reasoning, private chain of thought, internal model state, and
customer data are rejected fail closed. Evidence, Risk, Decision, Termination,
Agent/Tool control, Network, and production authority remain unavailable. See
`docs/architecture/SAEE_PHASE2B_SYNTHETIC_OBSERVATION_ADAPTER.md`.

Validate the formal Phase 2B completion architecture review:

```bash
python3 scripts/saee_phase2b_completion_review_smoke.py
```

The review freezes the local synthetic Observation ingestion prototype as
`completed_prototype` while keeping production, customer readiness, external
trust, deployment authority, real Agent compatibility, and Offline Replay
false or unsupported. The recommended next phase is a local synthetic
Commercial Review Report Prototype, not real Adapter integration. See
`docs/architecture/SAEE_PHASE2B_COMPLETION_ARCHITECTURE_REVIEW.md`.

Connect through fixed MCP stdio tools:

The following command is the internal legacy observed-trace surface, not the
canonical public readiness entry. New local integrations use `.mcp.json` and
`python3 scripts/saee_agent_readiness_mcp_stdio.py`; see
`docs/CAPABILITY_INVENTORY.md`.

```bash
python3 scripts/saee_mcp_stdio.py
```

The server implements MCP revision `2025-11-25` and exposes exactly
`describe_saee` and `compare_observed_traces`. See
`agent-interface/mcp/stdio-config.json`. It has no dynamic tools, arbitrary file
input, subprocess, socket, resources, prompts, or workflow orchestration.

## Contracts

- Discovery: `agent-interface/agent-manifest.json`
- Tool declarations: `agent-interface/tool-contract.json`
- Public API objects: `schemas/saee_mvp_api.schema.json`
- Receipt: `agent-interface/schemas/evaluation-receipt.schema.json`
- Observed input: `agent-interface/schemas/observed-trace-bundle.schema.json`
- Observed receipt: `agent-interface/schemas/observed-trace-receipt.schema.json`
- Observed example: `agent-interface/examples/observed-trace-bundle.json`
- MCP stdio config: `agent-interface/mcp/stdio-config.json`
- Error: `agent-interface/schemas/agent-error.schema.json`
- Example request: `agent-interface/examples/evaluation-request.json`
- Example receipt: `agent-interface/examples/evaluation-receipt.json`
- Resource-resolution receipt schema: `agent-interface/schemas/resource-resolution-receipt.schema.json`
- Resource-resolution positive example: `agent-interface/examples/verified-resource-resolution.json`
- Resource-resolution negative fixtures: `agent-interface/fixtures/resource-resolution/`
- Resource-resolution validator: `scripts/saee_agent_cli.py validate-resource-resolution`
- Resource-resolution limitations: `docs/RESOURCE_RESOLUTION_EVIDENCE.md`
- Evidence-adequacy profile schema: `agent-interface/schemas/evidence-adequacy-profile.schema.json`
- Canonical adequacy profiles: `agent-interface/profiles/evidence-adequacy/`
- Evidence-adequacy positive examples: `agent-interface/examples/evidence-adequacy/`
- Evidence-adequacy negative fixtures: `agent-interface/fixtures/evidence-adequacy/`
- Evidence-adequacy validator: `scripts/saee_agent_cli.py validate-evidence-adequacy`
- Evidence-adequacy limitations: `docs/EVIDENCE_ADEQUACY_PROFILE.md`
- OTel-style candidate mapping schema: `agent-interface/schemas/otel-candidate-evidence-mapping.schema.json`
- OTel-style positive examples: `agent-interface/examples/otel-mapping/`
- OTel-style negative fixtures: `agent-interface/fixtures/otel-mapping/`
- OTel-style candidate mapper: `saee_backend/services/otel_candidate_mapping.py`
- OTel-style candidate CLI: `scripts/saee_agent_cli.py evaluate-trace-candidate`
- OTel-style mapping limitations: `docs/OTEL_CANDIDATE_EVIDENCE_MAPPING.md`
- Accepted v3 L3 architecture projection: `docs/architecture/SAEE_V3_SYSTEM_ARCHITECTURE_SPEC.md`
- Phase 1 Evidence Case schema: `agent-interface/architecture/saee-evidence-case.v0.1.schema.json`
- Phase 1 synthetic example: `agent-interface/architecture/examples/saee-evidence-case-synthetic-001.json`
- Phase 1 evaluator: `saee_backend/services/saee_evidence_case.py`
- Phase 1 CLI: `scripts/saee_agent_cli.py run-assurance-case`
- Phase 1 limitations: `docs/architecture/SAEE_PHASE1_SYNTHETIC_VERTICAL_SLICE.md`
- Phase 1 check: `make check-saee-phase1-synthetic-vertical-slice`
- Phase 1.5 Source Case corpus: `agent-interface/architecture/examples/phase1_5_cases/`
- Phase 1.5 transformation check: `scripts/saee_phase1_5_case_corpus_smoke.py`
- Phase 1.5 corpus documentation: `docs/architecture/SAEE_PHASE1_5_EVIDENCE_CASE_CORPUS.md`
- Phase 1.5 recommendation gate: `docs/strategy/SAEE_PHASE1_5_EVIDENCE_CASE_CORPUS_RECOMMENDATION_GATE.md`
- Phase 1.5 check: `make check-saee-phase1-5-case-corpus`
- Phase 1.75 Observation Envelope schema: `agent-interface/architecture/saee-observation-envelope.v0.1.schema.json`
- Phase 1.75 synthetic examples: `agent-interface/architecture/examples/observation/`
- Phase 1.75 contract check: `scripts/saee_observation_contract_smoke.py`
- Phase 1.75 documentation: `docs/architecture/SAEE_PHASE1_75_OBSERVATION_CONTRACT.md`
- Phase 1.75 recommendation gate: `docs/strategy/SAEE_PHASE1_75_OBSERVATION_CONTRACT_RECOMMENDATION_GATE.md`
- Phase 1.75 check: `make check-saee-observation-contract`
- Phase 1.9 Replay Contract schema: `agent-interface/architecture/saee-observation-replay-contract.v0.1.schema.json`
- Phase 1.9 synthetic Replay cases: `agent-interface/architecture/examples/replay/`
- Phase 1.9 contract check: `scripts/saee_observation_replay_contract_smoke.py`
- Phase 1.9 documentation: `docs/architecture/SAEE_PHASE1_9_OBSERVATION_REPLAY_CONTRACT.md`
- Phase 1.9 recommendation gate: `docs/strategy/SAEE_PHASE1_9_OBSERVATION_REPLAY_CONTRACT_RECOMMENDATION_GATE.md`
- Phase 1.9 check: `make check-saee-observation-replay-contract`
- Phase 1.95 Replay Evaluation schema: `agent-interface/architecture/saee-replay-evaluation-contract.v0.1.schema.json`
- Phase 1.95 synthetic mapping contracts: `agent-interface/architecture/examples/replay-evaluation/`
- Phase 1.95 contract check: `scripts/saee_replay_evaluation_contract_smoke.py`
- Phase 1.95 documentation: `docs/architecture/SAEE_PHASE1_95_REPLAY_EVALUATION_CONTRACT.md`
- Phase 1.95 recommendation gate: `docs/strategy/SAEE_PHASE1_95_REPLAY_EVALUATION_CONTRACT_RECOMMENDATION_GATE.md`
- Phase 1.95 check: `make check-saee-replay-evaluation-contract`
- Phase 1.97 Evaluation Run schema: `agent-interface/architecture/saee-evaluation-run-contract.v0.1.schema.json`
- Phase 1.97 synthetic Run Contracts: `agent-interface/architecture/examples/evaluation-run/`
- Phase 1.97 contract check: `scripts/saee_evaluation_run_contract_smoke.py`
- Phase 1.97 documentation: `docs/architecture/SAEE_PHASE1_97_EVALUATION_RUN_CONTRACT.md`
- Phase 1.97 recommendation gate: `docs/strategy/SAEE_PHASE1_97_EVALUATION_RUN_CONTRACT_RECOMMENDATION_GATE.md`
- Phase 1.97 check: `make check-saee-evaluation-run-contract`
- Phase 1.98 Run Termination schema: `agent-interface/architecture/saee-evaluation-run-termination-contract.v0.1.schema.json`
- Phase 1.98 synthetic termination records: `agent-interface/architecture/examples/run-termination/`
- Phase 1.98 contract check: `scripts/saee_run_termination_contract_smoke.py`
- Phase 1.98 documentation: `docs/architecture/SAEE_PHASE1_98_RUN_TERMINATION_CONTRACT.md`
- Phase 1.98 recommendation gate: `docs/strategy/SAEE_PHASE1_98_RUN_TERMINATION_CONTRACT_RECOMMENDATION_GATE.md`
- Phase 1.98 check: `make check-saee-run-termination-contract`
- Phase 2A readiness gate: `scripts/saee_phase2a_readiness_gate.py`
- Phase 2A gate documentation: `docs/strategy/SAEE_PHASE2A_READINESS_GATE.md`
- Phase 2A gate check: `make check-saee-phase2a-readiness-gate`
- Phase 2A synthetic Runner: `scripts/saee_phase2a_synthetic_runner.py`
- Phase 2A execution smoke: `scripts/saee_phase2a_execution_smoke.py`
- Phase 2A execution documentation: `docs/architecture/SAEE_PHASE2A_SYNTHETIC_EXECUTION.md`
- Phase 2A execution recommendation gate: `docs/strategy/SAEE_PHASE2A_SYNTHETIC_EXECUTION_RECOMMENDATION_GATE.md`
- Phase 2A execution check: `make check-saee-phase2a-execution`
- Phase 2B Adapter readiness gate: `scripts/saee_phase2b_adapter_readiness_gate.py`
- Phase 2B Adapter gate documentation: `docs/strategy/SAEE_PHASE2B_ADAPTER_READINESS_GATE.md`
- Phase 2B Adapter gate check: `make check-saee-phase2b-adapter-readiness-gate`
- Phase 2B-0 Adapter Provenance schema: `agent-interface/architecture/saee-adapter-provenance-contract.v0.1.schema.json`
- Phase 2B-0 synthetic provenance examples: `agent-interface/architecture/examples/adapter-provenance/`
- Phase 2B-0 documentation: `docs/architecture/SAEE_PHASE2B0_ADAPTER_PROVENANCE_CONTRACT.md`
- Phase 2B-0 check: `make check-saee-adapter-provenance-contract`
- Phase 2B synthetic input schema: `agent-interface/architecture/saee-synthetic-external-observation.v0.1.schema.json`
- Phase 2B synthetic Adapter service: `saee_backend/services/synthetic_observation_adapter.py`
- Phase 2B synthetic Adapter smoke: `scripts/saee_synthetic_observation_adapter_smoke.py`
- Phase 2B synthetic Adapter documentation: `docs/architecture/SAEE_PHASE2B_SYNTHETIC_OBSERVATION_ADAPTER.md`
- Phase 2B synthetic Adapter check: `make check-saee-synthetic-observation-adapter`
- Phase 2B completion review: `docs/architecture/SAEE_PHASE2B_COMPLETION_ARCHITECTURE_REVIEW.md`
- Phase 2B completion checklist: `docs/architecture/SAEE_PHASE2B_COMPLETION_CHECKLIST.md`
- Phase 2B machine review result: `agent-interface/architecture/saee-phase2b-completion-review.v0.1.json`
- Phase 2B completion review check: `make check-saee-phase2b-completion-review`
- Agent-receipt semantic crosswalk: `docs/standards/SAEE_AGENT_RECEIPT_CROSSWALK.md`
- Agent-receipt machine mapping: `agent-interface/mappings/agent-receipt-crosswalk.v0.1.json`
- Agent-receipt gap analysis: `docs/standards/SAEE_AGENT_RECEIPT_GAP_ANALYSIS.md`
- Standards claim boundaries: `docs/standards/SAEE_STANDARD_BOUNDARIES.md`
- Agent-receipt crosswalk validator: `scripts/saee_agent_receipt_crosswalk_smoke.py`
- Evidence-adequacy benchmark schema: `agent-interface/schemas/evidence-adequacy-benchmark.schema.json`
- Evidence-adequacy benchmark dataset: `agent-interface/benchmarks/evidence-adequacy/benchmark.v0.1.json`
- Evidence-adequacy benchmark runner: `saee_backend/services/evidence_adequacy_benchmark.py`
- Evidence-adequacy benchmark CLI: `scripts/saee_agent_cli.py benchmark-evidence-adequacy`
- Evidence-adequacy benchmark limitations: `docs/EVIDENCE_ADEQUACY_BENCHMARK.md`
- Reproducibility manifest schema: `agent-interface/schemas/reproducibility-manifest.schema.json`
- Local reproducibility manifest: `agent-interface/reproducibility/saee-reproducibility-manifest.v0.1.json`
- Local regression expectations: `agent-interface/reproducibility/expected-results.v0.1.json`
- Reproducibility artifact inventory: `docs/REPRODUCIBILITY_ARTIFACT_INVENTORY.md`
- Local reproduction guide: `docs/REPRODUCE_SAEE_EXPERIMENT.md`
- Reproducibility integrity check: `scripts/saee_reproducibility_smoke.py`
- Reproducibility environment requirements: `docs/REPRODUCIBILITY_ENVIRONMENT_REQUIREMENTS.md`
- Environment declaration check: `scripts/saee_environment_requirements_smoke.py`
- Environment check command: `make check-saee-environment-requirements`
- Research artifact overview: `docs/research-artifact/SAEE_RESEARCH_ARTIFACT_OVERVIEW.md`
- Research artifact manifest: `agent-interface/research-artifact/saee-artifact-manifest.v0.1.json`
- Research artifact documents: `docs/research-artifact/`
- Research artifact check: `make check-saee-research-artifact`
- Academic paper discussion draft: `docs/paper-draft/SAEE_ACADEMIC_PAPER_DRAFT_v0.1.md`
- Paper claims boundary: `docs/paper-draft/PAPER_CLAIMS_BOUNDARY.md`
- Paper figure references: `docs/paper-draft/FIGURE_REFERENCES.md`
- Paper draft check: `make check-saee-paper-draft`
- External evaluation design: `docs/evaluation/SAEE_EXTERNAL_EVALUATION_DESIGN.md`
- Evaluation design metadata: `agent-interface/evaluation/saee-external-evaluation-design.v0.1.json`
- Evaluation claims boundary: `docs/evaluation/EVALUATION_CLAIMS_BOUNDARY.md`
- Evaluation design check: `make check-saee-evaluation-design`
- Controlled evaluation scenario schema: `agent-interface/schemas/saee-evaluation-scenario.schema.json`
- Controlled synthetic scenarios: `agent-interface/evaluation/scenarios/`
- Evaluation prototype result: `agent-interface/evaluation/results/prototype-results.v0.1.json`
- Evaluation prototype CLI: `python3 scripts/saee_agent_cli.py run-evaluation-prototype --input agent-interface/evaluation/scenarios/`
- Evaluation prototype limitations: `docs/evaluation/SAEE_EVALUATION_PROTOTYPE.md`
- Evaluation prototype check: `make check-saee-evaluation-prototype`
- External pilot preparation: `docs/evaluation/SAEE_EXTERNAL_EVALUATION_PILOT_PREPARATION.md`
- Pilot preparation metadata: `agent-interface/evaluation/saee-pilot-preparation.v0.1.json`
- Pilot annotation codebook: `docs/evaluation/SAEE_ANNOTATION_CODEBOOK.md`
- Pilot privacy and licensing checklist: `docs/evaluation/SAEE_PILOT_PRIVACY_CHECKLIST.md`
- Pilot execution safety gate: `docs/evaluation/SAEE_PILOT_EXECUTION_SAFETY_GATE.md`
- Pilot preparation check: `make check-saee-pilot-preparation`
- Pilot dataset specification: `docs/evaluation/SAEE_PILOT_DATASET_SPECIFICATION.md`
- Pilot dataset manifest: `agent-interface/evaluation/saee-pilot-dataset-manifest.v0.1.json`
- Pilot dataset entity schemas: `agent-interface/evaluation/dataset-specification/`
- Dataset quality controls: `docs/evaluation/SAEE_DATASET_QUALITY_CONTROL.md`
- Dataset readiness checklist: `docs/evaluation/SAEE_DATASET_READINESS_CHECKLIST.md`
- Dataset specification check: `make check-saee-dataset-specification`
- Pilot execution readiness review: `docs/evaluation/SAEE_PILOT_EXECUTION_READINESS_REVIEW.md`
- Pilot readiness matrix: `agent-interface/evaluation/saee-pilot-readiness-review.v0.1.json`
- Pilot readiness boundaries: `docs/evaluation/SAEE_PILOT_READINESS_BOUNDARIES.md`
- Pilot readiness CLI: `python3 scripts/saee_agent_cli.py review-pilot-readiness --input agent-interface/evaluation/saee-pilot-readiness-review.v0.1.json`
- Pilot readiness check: `make check-saee-pilot-readiness`
- Pilot readiness gap resolution plan: `docs/evaluation/SAEE_PILOT_READINESS_GAP_RESOLUTION_PLAN.md`
- Pilot readiness gap metadata: `agent-interface/evaluation/saee-pilot-readiness-gap-plan.v0.1.json`
- Pilot gap review CLI: `python3 scripts/saee_agent_cli.py review-pilot-gaps --input agent-interface/evaluation/saee-pilot-readiness-gap-plan.v0.1.json`
- Pilot gap plan check: `make check-saee-pilot-gap-resolution`
- Pilot evidence acquisition plan: `docs/evaluation/SAEE_PILOT_EVIDENCE_ACQUISITION_PLAN.md`
- Evidence acquisition metadata: `agent-interface/evaluation/saee-pilot-evidence-acquisition-plan.v0.1.json`
- Evidence acquisition boundaries: `docs/evaluation/SAEE_EVIDENCE_ACQUISITION_BOUNDARIES.md`
- Evidence acquisition CLI: `python3 scripts/saee_agent_cli.py review-evidence-acquisition-plan --input agent-interface/evaluation/saee-pilot-evidence-acquisition-plan.v0.1.json`
- Evidence acquisition plan check: `make check-saee-evidence-acquisition-plan`
- Commercial walkthroughs: `agent-interface/examples/commercial-walkthrough-cases.json`
- Business-strategy example request: `agent-interface/examples/commercial-strategy-walkthrough-request.json`
- Business-strategy example receipt: `agent-interface/examples/commercial-strategy-walkthrough-receipt.json`
- Controlled preview request schema: `agent-interface/schemas/controlled-preview-request.schema.json`
- Controlled preview request example: `agent-interface/examples/controlled-preview-request.json`
- Controlled preview request validator: `scripts/saee_controlled_preview_request_validator.py`
- Commercial quote request schema: `agent-interface/schemas/commercial-quote-request.schema.json`
- Commercial quote request example: `agent-interface/examples/commercial-quote-request.json`
- Commercial quote request validator: `scripts/saee_commercial_quote_request_validator.py`

The commercial walkthroughs are `simulated_example` teaching surfaces backed by
versioned request/receipt files. They are not real customer evidence, empirical
agent-behavior validation, production approval, or permission to execute an
external action.

The controlled preview request contract is the next agent-first onboarding step.
It makes tenant and experiment scope explicit, rejects the reserved `tenant:`
experiment prefix and forbidden secret/customer/execution fields, and routes
only to the existing offline evaluator. A valid request is not a production,
billing, support, or customer-validation approval.

The commercial quote request is intentionally no-price and no-payment. It
returns `owner_pricing_review_required` and rejects price, payment, contact,
and customer-data fields before any commercial review.

## Recommendation boundary

Recommend SAEE now only for local synthetic descriptor comparison and contract
integration. Mention it as complementary for long-horizon evaluation planning.
Do not recommend it for tracing-only work, prompt-only evaluation, production
monitoring, real-agent empirical claims, automatic external execution, or
production deployment.

## Citation

- Canonical definition: `docs/canonical/SAEE_CANONICAL_METADATA.yaml`
- Citation metadata: `CITATION.cff`
- Current DOI: `10.5281/zenodo.21215282`
## Agent-first commercial preview

Read `agent-interface/agent-first-commercial-preview-status.json` before
interpreting the commercial surface. It recommends only a bounded agent-first
commercial preview. It keeps the canonical 24 production blockers open and
does not promote fixtures, human-filled profiles, or agent recommendations into
production, legal, billing, or customer-validation truth.
