# SAEE Owner Assignment Completion Guide

Status: local human input guide, hold.

Use this guide to fill the owner assignment completion sheet for the five
selected commercial evidence sprint blockers.

## Files

- CSV sheet: `owner_assignment_input_completion.csv`
- Source JSON template: `owner_assignment_input.template.json`
- Status JSON: `owner_assignment_completion_status.local.json`
- Existing validator output: `owner_assignment_input_validation.local.json`

## Required Human Fields

For each blocker row, fill:

- `assigned_human_owner`
- `target_review_date`
- `owner_acknowledged_scope` as `true`
- `human_approval_reference`

Optional fields:

- `owner_contact_reference`
- `evidence_collection_request_reference`
- `notes`

## Convert CSV to Validator Input

After a human fills the CSV, run:

```bash
python3 scripts/saee_commercial_evidence_sprint_owner_assignment_completion_helper.py \
  --import-csv phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_input_completion.csv \
  --output-input-json phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_input.human_filled.local.json
```

Then validate:

```bash
python3 scripts/saee_commercial_evidence_sprint_owner_assignment_input_validator.py \
  --input phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_input.human_filled.local.json
```

## Generate One Human-Assigned Blocker Input Without Editing CSV

For a single selected blocker, a human can provide owner-assignment fields
directly:

```bash
python3 scripts/saee_commercial_evidence_sprint_owner_assignment_completion_helper.py \
  --single-blocker-id support_contact \
  --assigned-human-owner "Human Owner Name" \
  --target-review-date "2026-07-12" \
  --owner-acknowledged-scope true \
  --human-approval-reference "approval-record-id" \
  --output-input-json phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_input.human_filled.local.json
```

To fill multiple blockers incrementally, pass the previous output back with
`--base-input-json` and a new `--single-blocker-id`.

This mode records only human-provided owner-assignment input. It does not
contact owners, collect evidence, authorize execution, or close blockers.

## Boundary

This completion helper does not assign owners by itself, contact owners, collect
evidence, execute tasks, close blockers, launch product, contact customers,
expose private core, or claim production readiness. A passing validator result
only means a separate human-approved evidence collection request can be created.
