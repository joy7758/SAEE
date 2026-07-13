# SAEE Phase 2 Data/Operations Priority Collection Checklist

Use this only after a human owner decides to collect Phase 2 evidence.

- [ ] P2-ECP-001 `production_monitoring` / `log_retention_reviewed` -> fill `evidence_review` and `source_notes_by_key` in the priority template
- [ ] P2-ECP-002 `production_monitoring` / `metrics_coverage_approved` -> fill `evidence_review` and `source_notes_by_key` in the priority template
- [ ] P2-ECP-003 `production_monitoring` / `production_monitoring_plan_approved` -> fill `evidence_review` and `source_notes_by_key` in the priority template
- [ ] P2-ECP-004 `production_monitoring` / `slo_dashboard_defined` -> fill `evidence_review` and `source_notes_by_key` in the priority template
- [ ] P2-ECP-005 `production_monitoring` / `monitoring_dry_run_recorded` -> fill `evidence_review` and `source_notes_by_key` in the priority template
- [ ] P2-ECP-006 `external_alert_delivery` / `alert_acknowledgement_process_defined` -> fill `evidence_review` and `source_notes_by_key` in the priority template
- [ ] P2-ECP-007 `external_alert_delivery` / `alert_delivery_test_recorded` -> fill `evidence_review` and `source_notes_by_key` in the priority template
- [ ] P2-ECP-008 `external_alert_delivery` / `alert_failure_handling_defined` -> fill `evidence_review` and `source_notes_by_key` in the priority template
- [ ] P2-ECP-009 `external_alert_delivery` / `alert_routing_policy_approved` -> fill `evidence_review` and `source_notes_by_key` in the priority template
- [ ] P2-ECP-010 `external_alert_delivery` / `external_alert_channel_configured` -> fill `evidence_review` and `source_notes_by_key` in the priority template
- [ ] P2-ECP-011 `external_alert_delivery` / `incident_escalation_path_defined` -> fill `evidence_review` and `source_notes_by_key` in the priority template
- [ ] P2-ECP-012 `on_call_rotation` / `escalation_schedule_defined` -> fill `evidence_review` and `source_notes_by_key` in the priority template
- [ ] P2-ECP-013 `on_call_rotation` / `incident_commander_named` -> fill `evidence_review` and `source_notes_by_key` in the priority template
- [ ] P2-ECP-014 `on_call_rotation` / `on_call_rotation_defined` -> fill `evidence_review` and `source_notes_by_key` in the priority template
- [ ] P2-ECP-015 `restore_tested` / `isolated_restore_environment_used` -> fill `evidence_review` and `source_notes_by_key` in the priority template
- [ ] P2-ECP-016 `restore_tested` / `production_like_restore_test_plan_approved` -> fill `evidence_review` and `source_notes_by_key` in the priority template
- [ ] P2-ECP-017 `restore_tested` / `restore_integrity_checks_passed` -> fill `evidence_review` and `source_notes_by_key` in the priority template
- [ ] P2-ECP-018 `restore_tested` / `restore_test_report_reviewed` -> fill `evidence_review` and `source_notes_by_key` in the priority template
- [ ] P2-ECP-019 `restore_tested` / `rto_rpo_observed_and_recorded` -> fill `evidence_review` and `source_notes_by_key` in the priority template
- [ ] P2-ECP-020 `restore_tested` / `tenant_scope_validated_if_customer_data_exists` -> fill `evidence_review` and `source_notes_by_key` in the priority template
- [ ] P2-ECP-021 `production_restore_policy` / `backup_retention_policy_approved` -> fill `evidence_review` and `source_notes_by_key` in the priority template
- [ ] P2-ECP-022 `production_restore_policy` / `customer_notification_boundary_approved` -> fill `evidence_review` and `source_notes_by_key` in the priority template
- [ ] P2-ECP-023 `production_restore_policy` / `incident_response_handoff_approved` -> fill `evidence_review` and `source_notes_by_key` in the priority template
- [ ] P2-ECP-024 `production_restore_policy` / `production_restore_policy_approved` -> fill `evidence_review` and `source_notes_by_key` in the priority template
- [ ] P2-ECP-025 `production_restore_policy` / `tenant_restore_boundary_approved` -> fill `evidence_review` and `source_notes_by_key` in the priority template
- [ ] P2-ECP-026 `production_restore_policy` / `credential_secret_exclusion_reviewed` -> fill `evidence_review` and `source_notes_by_key` in the priority template

## Boundary

- Do not deploy monitoring from this packet.
- Do not contact monitoring or alert vendors from this packet.
- Do not send external alerts from this packet.
- Do not activate on-call from this packet.
- Do not run restore tests from this packet.
- Do not modify production data paths from this packet.
- Do not close blockers from this packet.
