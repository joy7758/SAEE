# SAEE Controlled Trial Local E2E Proof v0.1

controlled_trial_local_e2e_proof_v0_1: true
proof_status: local_e2e_pass_required
proof_scope: controlled_trial_demo_payload
trial_status: local_demo_available
production_ready: false
customer_validated: false
customer_contacted: false
customer_data_allowed: false
paid_trial_enabled: false
payment_provider_configured: false
product_launched: false
public_sdk_released: false
external_ai_assistant_tested: false
external_validation_claim: false
private_core_exposed: false
api_schema_modified: false
runtime_modified: false
kernel_modified: false
external_calls_made: false

## Purpose

This file records the local end-to-end proof surface for the SAEE controlled
trial demo path. It verifies that the public controlled-trial demo payload can
be evaluated through the public request models and experiment service, producing
a deterministic deployment recommendation without using external services.

This is a local trial proof only. It is not production readiness, customer
validation, paid trial enablement, or external AI assistant validation.

## What Is Proved

- The controlled-trial demo payload is accepted by the public request model.
- Request limits accept the demo payload under local default limits.
- The public experiment service returns `status = completed`.
- The result includes `decision_result`, `recommended_agent`, ranking,
  failure-mode summary, and survival curves.
- The local demo recommendation is produced without exposing private core logic.

## Current Local Expected Result

```yaml
experiment_id: controlled-trial-local-e2e
expected_status: completed
expected_recommended_agent: agent-b
expected_agents: 3
expected_repeat_runs_per_agent: 5
expected_stored_runs: 15
expected_outputs:
  - decision_result
  - recommended_agent
  - confidence_score
  - ranking
  - failure_modes_summary
  - survival_curves
```

## Verification Command

Run:

```bash
python3 scripts/saee_controlled_trial_local_e2e_smoke.py
```

Expected output:

```text
SAEE_CONTROLLED_TRIAL_LOCAL_E2E_SMOKE: PASS
```

## Boundary

This proof does not start a public server, open a browser, contact customers,
collect customer data, call external AI assistants, configure payment, publish a
product, release an SDK, modify runtime logic, modify API schema, or expose the
private core.

The proof only demonstrates that the local controlled trial path is runnable and
that the demo output surface is available for human review.
