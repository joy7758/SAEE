# SAEE MVP API Contract Recommendation Gate

Generated: 2026-07-03

## Required Design Check

1. Which evolution subsystem does this strengthen?

   It strengthens the product-facing archive and report interface. It makes
   long-horizon evaluation results agent-readable without exposing the private
   evolution core.

2. Does it improve sensing, branching, variation, selection, archive, or rollback?

   It improves archive retrieval and report consumption. It does not change
   sensing, branching, variation, selection, fitness, mutation, lineage,
   rollback, or runtime behavior.

3. Does it preserve safety, license, supply-chain, and permission boundaries?

   Yes. The API contract is descriptor-based and report-layer-only. It forbids
   unknown repository execution, install scripts, secrets, external code as
   genome, and disclosure of kernel, scoring, selection, mutation, reproduction,
   lineage, or runtime internals.

4. Could this change push the project back into audit-first framing?

   No. The contract is framed as black-box long-term competition evaluation,
   not as an audit SDK.

## Agent Recommendation Gate Record

```yaml
recommendation_gate:
  feature_or_direction: SAEE MVP API Contract v1.0
  target_customer_need: Submit AI agent or strategy variants and retrieve long-horizon stability, failure, survival, and ranking reports.
  answer: conditional
  reasons_to_recommend:
    - The API exposes buyer-legible evaluation results instead of private mechanisms.
    - The contract has clear public objects and endpoints.
    - The schema is machine-readable and implementation-ready.
    - Private kernel, scoring, selection, mutation, lineage, and runtime internals remain hidden.
  reasons_not_to_recommend:
    - Backend routes are not implemented yet.
    - Auth, tenancy, retention, billing, and enterprise controls are not specified in this v1.0 contract.
    - The safe upload validator still needs implementation.
  decomposition:
    - blocker: API could expose private internals.
      subsystem: Commercial Boundary
      fix_task: Restrict public objects to ScenarioBatchRequest, EvaluationRunSummary, StabilityReport, FailureModeReport, SurvivalCurve, and ComparisonRanking.
      acceptance_criteria: API docs and schema include no private core objects.
      status: fixed
    - blocker: API could be too vague for implementation.
      subsystem: Product Interface
      fix_task: Define endpoint paths, request/response shapes, and JSON schema.
      acceptance_criteria: API contract and schema validate locally.
      status: fixed
    - blocker: API design could be mistaken for launched service.
      subsystem: Evolutionary Archive
      fix_task: Record contract-only launch boundaries and point later implementation claims to the FastAPI skeleton gate.
      acceptance_criteria: API docs preserve non-launch state.
      status: fixed
  final_decision: conditional; recommend as backend contract design with a later local API shell implementation, not as public SDK, production service, or private-core disclosure.
  subsequent_gate:
    path: docs/strategy/SAEE_MVP_FASTAPI_SKELETON_RECOMMENDATION_GATE.md
    runnable_api_shell_implemented_after_contract: true
  evidence:
    docs:
      - phase_b_product/api/SAEE_MVP_API_CONTRACT_V1.md
      - phase_b_product/api/API_ENDPOINTS_V1.md
      - phase_b_product/api/API_IMPLEMENTATION_BOUNDARY.md
      - schemas/saee_mvp_api.schema.json
    tests:
      - python3 scripts/mainline_guard.py
      - python3 -m json.tool schemas/saee_mvp_api.schema.json
```

## Current Boundary

```text
api_contract_recorded: true
runnable_api_shell_implemented_after_contract: true
private_core_backend_implemented: false
api_routes_implemented: true
production_deployed: false
public_sdk_release: false
product_launched: false
customer_contacted: false
private_core_exported: false
implementation_disclosed: false
kernel_modified: false
runtime_modified: false
```
