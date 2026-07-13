# SAEE Production Monitoring Approval Input Prompt Recommendation Gate

answer: recommend
recommend_for_human_production_monitoring_input_prompt: true
recommend_for_monitoring_approval_by_codex: false
recommend_for_evidence_builder_execution: false
recommend_for_monitoring_deployment: false
recommend_for_blocker_closure: false
recommend_for_production: false

## Reason

The prompt is recommendable as a local human-input guide for the
`production_monitoring` approval template. It makes the required metadata and
monitoring evidence keys explicit without approving or deploying monitoring.

## Boundary

- target_blocker_id: production_monitoring
- builder_ready: false
- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_prompt: 0
- production_monitoring_available: false
- production_monitoring_approved: false
- production_monitoring_deployed: false
- dashboard_configured_by_codex: false
- metrics_export_enabled_by_codex: false
- log_retention_changed_by_codex: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
