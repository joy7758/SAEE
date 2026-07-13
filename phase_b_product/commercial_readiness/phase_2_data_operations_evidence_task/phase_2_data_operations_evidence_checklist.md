# SAEE Phase 2 Data and Operations Evidence Checklist

Use this checklist only after a human explicitly authorizes Phase 2
evidence collection. Codex must not deploy monitoring, contact vendors,
send alerts, activate on-call, run restore tests, modify production data
paths, or process customer data.

## production_monitoring

- [ ] `production_monitoring_plan_approved`
- [ ] `metrics_coverage_approved`
- [ ] `slo_dashboard_defined`
- [ ] `log_retention_reviewed`
- [ ] `monitoring_dry_run_recorded`

## external_alert_delivery

- [ ] `external_alert_channel_configured`
- [ ] `alert_routing_policy_approved`
- [ ] `alert_delivery_test_recorded`
- [ ] `alert_failure_handling_defined`
- [ ] `incident_escalation_path_defined`
- [ ] `alert_acknowledgement_process_defined`

## on_call_rotation

- [ ] `on_call_rotation_defined`
- [ ] `escalation_schedule_defined`
- [ ] `incident_commander_named`

## restore_tested

- [ ] `production_like_restore_test_plan_approved`
- [ ] `isolated_restore_environment_used`
- [ ] `restore_integrity_checks_passed`
- [ ] `rto_rpo_observed_and_recorded`
- [ ] `tenant_scope_validated_if_customer_data_exists`
- [ ] `restore_test_report_reviewed`

## production_restore_policy

- [ ] `production_restore_policy_approved`
- [ ] `backup_retention_policy_approved`
- [ ] `tenant_restore_boundary_approved`
- [ ] `credential_secret_exclusion_reviewed`
- [ ] `customer_notification_boundary_approved`
- [ ] `incident_response_handoff_approved`

## Required Review Before Blocker Closure

- [ ] Human approval confirms evidence is real and current.
- [ ] Evidence JSON is parseable by the readiness checker.
- [ ] No forbidden boundary flag is set to true.
- [ ] Commercial go/no-go is rerun with explicit evidence paths.
- [ ] Separate human launch approval remains required.
