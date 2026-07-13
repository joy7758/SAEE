# SAEE Request Limits Recommendation Gate

Generated: 2026-07-03

## Required Design Check

1. Which evolution subsystem does this strengthen?

   It strengthens Sandbox Development and Evolutionary Archive access safety by
   bounding public-shell evaluation requests before they enter the MVP service.

2. Does it improve sensing, branching, variation, selection, archive, or rollback?

   It improves deployment safety around archive/report generation. It does not
   modify sensing, branching, variation, selection, fitness, mutation, lineage,
   rollback, runtime, or private core.

3. Does it preserve safety, license, supply-chain, and permission boundaries?

   Yes. It uses local request validation only, adds no dependencies, performs
   no external calls, and keeps private internals disconnected.

4. Could this change push the project back into audit-first framing?

   No. It is resource protection for SAEE's stability-evaluation API shell.

## Agent Recommendation Gate Record

```yaml
recommendation_gate:
  feature_or_direction: SAEE Request Limits v0.1
  target_customer_need: Try SAEE in a controlled local or preview setting where oversized evaluation requests cannot exhaust the MVP service.
  answer: conditional
  reasons_to_recommend:
    - Bounded request controls are necessary before shared preview usage.
    - Limits are configurable by deployment environment without changing endpoint shape.
    - Oversized requests are rejected before reaching the evaluation service.
  reasons_not_to_recommend:
    - This is not tenant-aware billing, metering, or production rate limiting.
    - It does not provide persistent usage records or abuse detection.
    - It does not make SAEE production-ready.
  decomposition:
    - blocker: Public shell accepted schema-maximum requests with no deployment-specific cap.
      subsystem: Product Boundary
      fix_task: Add configurable request limits for agents, repeat runs, time horizon, and payload size.
      acceptance_criteria: Environment variables control the limits and local defaults preserve existing schema maxima.
      status: fixed
    - blocker: Oversized requests could enter the evaluation service.
      subsystem: Sandbox Development
      fix_task: Validate `ScenarioBatchRequest` before `ExperimentService.run_experiment`.
      acceptance_criteria: Exceeded limits return HTTP 413 and do not enter the service.
      status: fixed
    - blocker: Commercial usage still needs quotas and metering.
      subsystem: Commercial Boundary
      fix_task: Record remaining quota, metering, tenant, and monitoring gaps.
      acceptance_criteria: Request-limits documentation preserves non-production status and lists remaining gaps.
      status: deferred
  final_decision: conditional; proceed as local/pre-commercial resource guard only, not as production quota readiness.
  evidence:
    docs:
      - phase_b_product/commercial_readiness/REQUEST_LIMITS_V0_1.md
      - saee_backend/README.md
    code:
      - saee_backend/config.py
      - saee_backend/services/request_limits.py
      - saee_backend/api/experiment.py
    tests:
      - python3 scripts/saee_request_limits_smoke.py
```

## Action Boundary

```text
recommend_public_launch_now: false
request_limits_available: true
production_quota_system_available: false
production_ready: false
customer_validated: false
product_launched: false
public_sdk_released: false
private_core_exposed: false
runtime_modified: false
kernel_modified: false
api_schema_modified: false
```

