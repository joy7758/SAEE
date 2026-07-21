# SAEE Check Idempotency Preflight Recommendation

```yaml
recommendation_gate:
  feature_or_direction: clean_idempotent_validation_checks
  target_customer_need: integrate_saee_code_and_capability_fact_validation_into_enterprise_development_and_audit_workflows
  answer: conditional
  reasons_to_recommend:
    - SAEE already exposes substantial offline validators and agent-readable evidence surfaces.
    - The defect is isolated to build and validation reliability rather than a missing product capability.
  reasons_not_to_recommend:
    - make_check_modifies_tracked_files
    - mainline_guard_depends_on_ignored_local_provider_evidence
    - clean_checkout_results_are_not_reproducible
    - a_green_result_from_the_owner_worktree_is_not_portable_evidence
  decomposition:
    - blocker: validation_mutates_the_evidence_scene
      subsystem: evolutionary_archive_and_rollback_immune_system
      fix_task: isolate_generation_and_make_normal_checks_read_only
      acceptance_criteria: two_clean_runs_exit_zero_and_leave_zero_tracked_changes
      status: open
    - blocker: generate_and_check_responsibilities_are_mixed
      subsystem: evolutionary_archive_and_rollback_immune_system
      fix_task: expose_explicit_generate_and_check_generated_contracts
      acceptance_criteria: generation_is_explicit_and_comparison_occurs_outside_tracked_paths
      status: open
    - blocker: normal_checks_require_ignored_qianfan_runtime_evidence
      subsystem: evolutionary_archive_and_rollback_immune_system
      fix_task: separate_normal_and_strict_provider_evidence_validation
      acceptance_criteria: normal_check_reports_not_required_while_strict_check_reports_not_available_and_fails
      status: open
    - blocker: canonical_remote_identity_is_unresolved
      subsystem: evolutionary_archive_and_rollback_immune_system
      fix_task: owner_selects_and_creates_the_canonical_remote
      acceptance_criteria: canonical_origin_and_public_projection_roles_are_explicit
      status: deferred
  final_decision: proceed_only_with_the_bounded_build_reliability_repair_on_an_independent_branch
  evidence:
    docs:
      - /Users/zhangbin/Documents/SAEE-backups/audits/SAEE_MERGE_BLOCKER_ROOT_CAUSE_AUDIT.md
    tests:
      - clean_worktree_make_check_root_cause_reproduction
    examples: []
```

## Customer question

> We are considering SAEE, but `make check` modifies tracked files and mainline validation depends on an ignored Provider runtime file on a developer machine. Would you recommend integrating it into enterprise development and audit workflows?

## Recommendation before development

`conditional` — do not integrate the current check as an enterprise gate yet.

The core reasons are:

- a validator must not alter the evidence it is validating;
- the same clean commit must produce the same result on another machine;
- ignored external Provider evidence cannot be an undeclared prerequisite of an offline mainline check;
- a pass observed only in an owner worktree is not portable validation evidence.

## Reliability versus product capability

Build reliability problems:

- generation is invoked from validator-shaped smoke tests;
- generated timestamps and live host-process state are nondeterministic;
- the normal mainline gate assumes ignored Qianfan evidence exists;
- repeated clean-checkout execution is not currently stable.

Product capability problems:

- none of the above proves that SAEE's evolution-engine capabilities are missing or incorrect;
- this repair does not validate Agent execution truth, production safety, regulatory compliance, customer adoption, or commercial readiness;
- canonical remote identity remains an owner decision outside this repair.

## Design check

- Evolution subsystem strengthened: `Evolutionary Archive / Rollback Immune System`.
- Improvement: reproducible selection evidence, archive integrity, and rollback confidence.
- Safety and supply-chain boundary: preserved; no network Provider call, dependency installation, permission expansion, or external publication is required.
- Audit-first reframing risk: `no`; this is repository validation reliability for the Digital Biosphere Evolution Engine, not a new audit product surface.

## Bounded development decision

Development may continue only as an independent build-reliability repair. The repair can remove the dirty-worktree and hidden-input blockers. It cannot resolve repository provenance, create a canonical remote, prove production safety, or authorize publication.
