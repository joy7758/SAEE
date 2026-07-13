# SAEE Customer Validation Evidence Builder v0.1

customer_validation_evidence_builder_v0_1: true
builder_scope: human_filled_local_pilot_result_to_customer_validation_evidence
input_template: phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence_input.template.json
default_input: phase_b_product/validation/PILOT_RESULT_TEMPLATE.json
default_output: phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence.from_pilot.local.json
production_customer_validation_ready_default: false
customer_validated: false
production_ready: false
product_launched: false
customer_contacted_by_codex: false
external_calls_made: false
private_core_exposed: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false

## Purpose

This builder converts a local, human-filled pilot result JSON into the
`production_customer_validation_evidence` shape used by the SAEE commercial
go/no-go layer.

It exists to make the customer-validation path executable after a human has
run an approved pilot session and filled the local result file. It does not run
the pilot, contact customers, infer missing answers, publish testimonials,
claim customer validation, validate revenue, or mark SAEE production-ready.

## Commands

Create the human-fillable evidence input template:

```bash
python3 scripts/saee_customer_validation_evidence_builder.py --write-template --json
```

Build evidence from the current empty pilot template:

```bash
python3 scripts/saee_customer_validation_evidence_builder.py --json
```

Build evidence from a human-filled pilot result:

```bash
python3 scripts/saee_customer_validation_evidence_builder.py \
  --input /path/to/human-filled-pilot-result.json \
  --output /path/to/customer-validation-evidence.json \
  --json
```

Validate the generated evidence with:

```bash
SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH=/path/to/customer-validation-evidence.json \
python3 scripts/saee_production_customer_validation_evidence_readiness.py
```

## Required Human Input

The input must contain at least one completed pilot session and an
`evidence_review` object. The builder sets evidence fields to `true` only when
the corresponding human review flag is explicitly true and the local session
data passes basic safety checks.

The builder does not infer missing pilot evidence from narrative notes.

## Boundary

```yaml
codex_contacted_customer: false
codex_executed_pilot: false
codex_inferred_missing_results: false
codex_collected_customer_data: false
customer_contacted_by_codex: false
automated_customer_contact: false
external_calls_made: false
external_model_api_called: false
external_ai_assistant_tested: false
customer_validated: false
production_ready: false
product_launched: false
public_sdk_released: false
private_core_exposed: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
```

## Go / No-Go Effect

The default empty input produces `hold` evidence. Complete, boundary-safe,
human-filled evidence may make the production customer-validation evidence
readiness checker return `pass`, which can satisfy the `pilot_results` and
`customer_validated` evidence blockers inside commercial go/no-go review.

That still does not publish a customer-validation claim, launch the product, or
make SAEE production-ready. A separate human decision remains required for any
public claim.
