# SAEE Evidence Request Approval Completion Guide

Status: local human input guide, hold.

Use this guide to fill the ERD approval completion sheet for the five selected
commercial evidence request drafts.

## Files

- CSV sheet: `evidence_request_approval_input_completion.csv`
- Source JSON template: `evidence_request_approval_input.template.json`
- Status JSON: `evidence_request_approval_completion_status.local.json`
- Existing validator output: `evidence_request_approval_input_validation.local.json`

## Required Human Fields For One Approved ERD

Choose at most one ERD row. For that row, fill:

- `assigned_human_owner`
- `human_approval_reference`
- `approval_decision`
- `approval_scope`
- `evidence_collection_request_reference` or `execution_request_reference`
- `owner_acknowledged_scope` as `true`
- `boundary_acknowledged` as `true`

Allowed decisions:

- `hold`
- `approved_for_separate_evidence_collection_request`
- `approved_for_separate_execution_request`

Allowed scopes:

- `evidence_collection_only`
- `implementation_and_evidence_collection_review`

## Convert CSV to Validator Input

After a human fills the CSV, run:

```bash
python3 scripts/saee_commercial_evidence_request_approval_completion_helper.py \
  --import-csv phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_input_completion.csv \
  --output-input-json phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_input.human_filled.local.json
```

Then validate:

```bash
python3 scripts/saee_commercial_evidence_request_approval_input_validator.py \
  --input phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_input.human_filled.local.json
```

## Generate One Human-Approved ERD Input Without Editing CSV

If a human has already chosen one ERD and can provide all required approval
fields, the helper can generate the validator input directly:

```bash
python3 scripts/saee_commercial_evidence_request_approval_completion_helper.py \
  --single-request-id ERD-001 \
  --assigned-human-owner "Human Owner Name" \
  --human-approval-reference "approval-record-id" \
  --approval-decision approved_for_separate_evidence_collection_request \
  --approval-scope evidence_collection_only \
  --evidence-collection-request-reference "separate-evidence-request-id" \
  --output-input-json phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_input.human_filled.local.json
```

This mode still does not approve anything by itself. It only records explicit
human-provided approval fields in a validator input file.

## Boundary

This completion helper does not approve requests by itself, collect evidence,
execute tasks, contact owners, contact customers, contact vendors, close
blockers, launch product, expose private core, or claim production readiness. A
passing validator result only means a separate human-approved evidence
collection or execution request can be created.
