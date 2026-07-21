# SAEE Check Idempotency Postflight Recommendation

```yaml
recommendation_gate:
  feature_or_direction: clean_idempotent_validation_checks
  target_customer_need: integrate_saee_code_and_capability_fact_validation_into_enterprise_development_and_audit_workflows
  answer: recommend
  reasons_to_recommend:
    - normal_validation_runs_in_a_disposable_tracked_only_local_clone
    - repeated_make_check_and_mainline_guard_runs_are_read_only_and_identical
    - ignored_provider_runtime_evidence_is_not_a_hidden_normal_check_input
    - strict_provider_evidence_validation_remains_fail_closed
    - substantive_generated_artifact_drift_is_detected_by_path
  reasons_not_to_recommend:
    - recommendation_is_limited_to_repository_code_and_capability_fact_validation
    - canonical_remote_identity_remains_unresolved
    - build_idempotency_does_not_prove_agent_execution_truth_or_production_safety
  decomposition:
    - blocker: validation_mutates_the_evidence_scene
      subsystem: evolutionary_archive_and_rollback_immune_system
      fix_task: isolate_generation_and_make_normal_checks_read_only
      acceptance_criteria: two_clean_runs_exit_zero_and_leave_zero_tracked_changes
      status: fixed
    - blocker: generate_and_check_responsibilities_are_mixed
      subsystem: evolutionary_archive_and_rollback_immune_system
      fix_task: expose_explicit_generate_and_check_generated_contracts
      acceptance_criteria: generation_is_explicit_and_substantive_drift_is_checked_outside_tracked_paths
      status: fixed
    - blocker: normal_checks_require_ignored_qianfan_runtime_evidence
      subsystem: evolutionary_archive_and_rollback_immune_system
      fix_task: separate_normal_and_strict_provider_evidence_validation
      acceptance_criteria: normal_absence_is_not_required_and_strict_absence_is_not_available_and_nonzero
      status: fixed
    - blocker: canonical_remote_identity_is_unresolved
      subsystem: evolutionary_archive_and_rollback_immune_system
      fix_task: owner_selects_and_creates_the_canonical_remote
      acceptance_criteria: canonical_origin_and_public_projection_roles_are_explicit
      status: deferred
  final_decision: recommend_for_bounded_repository_code_and_capability_fact_validation_only
  evidence:
    docs:
      - agent-interface/validation/saee-check-idempotency-contract.v1.json
      - docs/architecture/SAEE_CHECK_IDEMPOTENCY_CONTRACT.md
      - reports/CHECK_IDEMPOTENCY_FIX_REPORT.md
    tests:
      - python3 scripts/saee_check_idempotency_smoke.py
      - make check twice
      - python3 scripts/mainline_guard.py twice
      - make check-generated positive and negative cases
      - strict Provider evidence missing invalid and verified cases
    examples: []
```

## Recommendation after development

`recommend` for a bounded scope: SAEE repository code validation, checked-in
capability-fact consistency, and local generated-artifact drift detection.

The recommendation does not extend to:

- proof that a real Agent executed as claimed;
- production security or operational safety;
- authorization, regulatory compliance, certification, or legal conclusions;
- customer validation, adoption, marketplace publication, or production readiness;
- canonical remote selection or publication authority.

Compared with preflight, the repair removes the dirty-worktree gate, separates
explicit generation from normal checking, makes repeated output stable, and
turns external Provider evidence availability into an explicit machine-readable
contract. Product-level validation and repository provenance remain separate
workstreams.
