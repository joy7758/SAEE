# SAEE Controlled Trial Operator Packet v0.1

controlled_trial_operator_packet_v0_1: true
packet_status: local_trial_operator_packet_available
trial_scope: local_mvp_demo_observation
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
backend_modified: false
kernel_modified: false
external_calls_made: false
blockers_closed_by_packet: 0

## Purpose

This packet gives a human operator a repeatable way to run and record one SAEE
local controlled-trial session. It is for internal review, pilot rehearsal, and
commercial-readiness inspection of the local MVP decision loop.

The packet does not add product features, process customer data, contact
customers, launch a product, or claim production readiness. It records whether
the local demo was understandable, whether the recommendation output was useful,
and what evidence would still be required before any customer-facing claim.

## Local Trial Path

Use the existing local quickstart:

```bash
python3 -m uvicorn saee_backend.main:app --reload --port 8000
```

In a second terminal:

```bash
cd phase_b_product/landing
python3 -m http.server 8765
```

Open:

```text
http://127.0.0.1:8765/
```

Local API endpoint:

```text
http://127.0.0.1:8000/experiment/run
```

Click:

```text
Run Demo Battle
```

Expected result fields:

```text
decision_result
recommended_agent
confidence_score
ranking
failure_modes_summary
survival_curves
```

## What the Operator Records

The operator records only local trial observations:

- whether the backend started locally;
- whether the landing page loaded locally;
- whether the demo button returned a result;
- whether `recommended_agent` and ranking were visible;
- whether the reviewer understood why the recommendation was made;
- whether any boundary claim was accidentally made;
- which production evidence is still missing.

## What Must Not Be Recorded as Completed

- customer validation;
- production readiness;
- paid trial readiness;
- pricing approval;
- external AI assistant validation;
- production monitoring readiness;
- production auth readiness;
- private core exposure or customization.

## Packet Files

- `controlled_trial_operator_packet/README.md`
- `controlled_trial_operator_packet/local_trial_session_template.json`
- `controlled_trial_operator_packet/local_trial_observation_sheet.md`

## Boundary

This operator packet is a local review instrument. It may improve repeatability
of local MVP trials, but it closes zero production blockers by default and does
not authorize customer contact, production deployment, external validation
claims, or any runtime, backend, kernel, API schema, landing page interaction,
or private-core change.
