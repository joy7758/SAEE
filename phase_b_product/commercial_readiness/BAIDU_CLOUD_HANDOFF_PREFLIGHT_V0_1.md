# SAEE Baidu Cloud Handoff Preflight v0.1

baidu_cloud_handoff_preflight_v0_1: true
status: ready_for_human_cloud_clear_confirmation
cloud_target_id: i-8xOwPKN3
handoff_scope: docs_and_readiness_manifest_only_no_runtime_upload
cloud_clear_required_before_sync: true
destructive_cloud_operation_requires_separate_confirmation: true
cloud_clear_performed: false
cloud_sync_performed: false
cloud_upload_authorized: false
cloud_delete_authorized: false
safe_upload_candidate_count: 38
candidate_count: 38
missing_candidate_count: 0
blockers_closed_by_preflight: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This local preflight records a safe, agent-readable handoff plan for a possible
future Baidu Cloud sync target. It does not clear cloud storage, upload files,
call cloud APIs, open a browser, package runtime code, expose private core, or
claim production readiness.

## Upload Scope

The default upload scope is documentation and readiness evidence only. It
excludes runtime, backend, kernel, API schema, private core, and landing-page
interaction files.

## Candidate Manifest

| Path | Exists | Safe to upload | Size bytes |
| --- | --- | --- | ---: |
| README.md | True | True | 307780 |
| PROJECT_STATUS.md | True | True | 234748 |
| ROADMAP.md | True | True | 230127 |
| CHANGELOG.md | True | True | 317013 |
| agent-readable.md | True | True | 373963 |
| llms.txt | True | True | 251231 |
| agent-index.json | True | True | 973390 |
| agent_recommendation/PRODUCT_FACTS.md | True | True | 3385 |
| agent_recommendation/PRODUCT_FACTS.json | True | True | 2108 |
| agent_recommendation/WHEN_TO_RECOMMEND_SAEE.md | True | True | 3746 |
| agent_recommendation/WHEN_NOT_TO_RECOMMEND_SAEE.md | True | True | 3057 |
| agent_recommendation/RECOMMENDATION_DECISION_TREE.md | True | True | 2641 |
| agent_recommendation/BUYER_QUESTIONS_AND_ANSWERS.md | True | True | 3834 |
| agent_recommendation/VALIDATION_RESULTS.md | True | True | 2849 |
| agent_recommendation/internal_self_play/SELF_PLAY_RESULTS.md | True | True | 1667 |
| phase_b_product/landing/for-ai-assistants.html | True | True | 13012 |
| phase_b_product/commercial_readiness/commercial_readiness_status.md | True | True | 5141 |
| phase_b_product/commercial_readiness/commercial_readiness_status.local.json | True | True | 8900 |
| phase_b_product/commercial_readiness/commercial_readiness_status.csv | True | True | 329 |
| phase_b_product/commercial_readiness/commercial_next_action_summary/commercial_next_action_summary.md | True | True | 5066 |
| phase_b_product/commercial_readiness/commercial_next_action_summary/commercial_next_action_summary.local.json | True | True | 11874 |
| phase_b_product/commercial_readiness/CONTROLLED_TRIAL_QUICKSTART_V0_1.md | True | True | 3321 |
| phase_b_product/commercial_readiness/LOCAL_TRIAL_SESSION_MANAGER_V0_1.md | True | True | 4309 |
| phase_b_product/commercial_readiness/LOCAL_TRIAL_MAKE_TARGETS_V0_1.md | True | True | 3397 |
| phase_b_product/validation/LOCAL_TRIAL_PREFLIGHT_SNAPSHOT_V0_1.md | True | True | 1856 |
| phase_b_product/validation/local_trial_preflight_snapshot.local.json | True | True | 1876 |
| phase_b_product/validation/LOCAL_TRIAL_COLD_START_PREFLIGHT_V0_1.md | True | True | 1762 |
| phase_b_product/validation/local_trial_cold_start_preflight.local.json | True | True | 2090 |
| phase_b_product/validation/local_trial_cold_start_preflight.md | True | True | 2065 |
| phase_b_product/validation/LOCAL_TRIAL_HTTP_E2E_V0_1.md | True | True | 1169 |
| phase_b_product/validation/local_trial_http_e2e/local_trial_http_e2e.local.json | True | True | 1803 |
| phase_b_product/validation/local_trial_http_e2e/local_trial_http_e2e.md | True | True | 1770 |
| phase_b_product/validation/LOCAL_TRIAL_LIFECYCLE_PROOF_V0_1.md | True | True | 1244 |
| phase_b_product/validation/local_trial_lifecycle_proof/local_trial_lifecycle_proof.local.json | True | True | 4124 |
| phase_b_product/validation/local_trial_lifecycle_proof/local_trial_lifecycle_proof.md | True | True | 2354 |
| phase_b_product/validation/LOCAL_TRIAL_HANDOFF_PACKET_V0_1.md | True | True | 1258 |
| phase_b_product/validation/local_trial_handoff_packet.local.json | True | True | 2703 |
| phase_b_product/validation/local_trial_handoff_packet.md | True | True | 2331 |

## Boundary

- No cloud clear was performed.
- No cloud sync was performed.
- No cloud upload is authorized by this file.
- No cloud delete is authorized by this file.
- No backend, runtime, kernel, API schema, landing interaction, or private core
  file is included in the safe manifest.
- Production readiness, customer validation, product launch, and blocker
  closure remain false.
