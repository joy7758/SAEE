# SAEE Production Monitoring Approval Input Prompt

production_monitoring_approval_input_prompt_v0_1: true
status: hold_human_production_monitoring_input_required
target_blocker_id: production_monitoring
required_metadata_field_count: 5
completed_metadata_field_count: 0
required_monitoring_evidence_item_count: 5
completed_monitoring_evidence_item_count: 0
builder_ready: false
production_monitoring_available: false
production_monitoring_approved: false
production_monitoring_deployed: false
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false

## Purpose

This prompt gives a human reviewer the shortest safe path for filling the
`production_monitoring` approval input before validator use.

## Metadata Fields To Fill

- `human_reviewer_name`
- `review_date`
- `monitoring_owner`
- `operations_reviewer_name`
- `decision_summary`

## Monitoring Evidence Keys To Review

| Evidence Key | Review Flag | Source Note | Evidence Slot | Owner Named | Reviewed By Human | Codex May Fill |
| --- | --- | --- | --- | --- | --- | --- |
| `log_retention_reviewed` | set true only after human approval | required | required | required | required | false |
| `metrics_coverage_approved` | set true only after human approval | required | required | required | required | false |
| `monitoring_dry_run_recorded` | set true only after human approval | required | required | required | required | false |
| `production_monitoring_plan_approved` | set true only after human approval | required | required | required | required | false |
| `slo_dashboard_defined` | set true only after human approval | required | required | required | required | false |

## Copy Template

```bash
cp phase_b_product/commercial_readiness/operations_evidence/production_monitoring_evidence_input.template.json phase_b_product/commercial_readiness/operations_evidence/production_monitoring_evidence_input.human_filled.local.json
```

## Validate Human-Filled Input

```bash
python3 scripts/saee_production_monitoring_approval_input_validator.py --input phase_b_product/commercial_readiness/operations_evidence/production_monitoring_evidence_input.human_filled.local.json
```

## Stop Point

After validation, stop. Evidence-builder execution, monitoring deployment,
dashboard configuration, metrics export, log-retention change, blocker closure,
launch, and production-readiness claims require separate approvals.

## Boundary

This prompt does not approve monitoring, fill evidence, deploy monitoring,
configure dashboards, enable metrics export, change log retention, touch live
operations paths, contact customers or vendors, execute the evidence builder,
close blockers, launch product, modify runtime/backend/kernel/API schema,
expose private core, or claim production readiness.
