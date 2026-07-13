# SAEE Production Identity Provider Human Decision Runbook

Status: hold_human_identity_provider_decision_required.

This runbook gives the human-only path for turning reviewed production identity-provider facts into a local validator input. It does not select or contact an identity provider, fetch JWKS, validate production tokens, enable production auth, collect evidence, close blockers, launch product, or claim production readiness.

## Summary

- runbook_type: saee_production_identity_provider_human_decision_runbook
- runbook_scope: local_human_identity_provider_decision_procedure
- target_blocker_id: production_identity_provider
- runbook_ready: true
- completion_helper_available: true
- explicit_input_generation_supported: true
- approval_input_validator_available: true
- separate_evidence_builder_request_required: true
- human_decision_recorded: false
- human_filled_input_generated: false
- identity_provider_selected_by_codex: false
- identity_provider_contacted: false
- jwks_fetched: false
- production_auth_enabled: false
- production_ready: false
- blockers_closed_by_runbook: false

## Human Procedure

| Step | Title | Human Action | Expected Output | Command Or File | Boundary |
| --- | --- | --- | --- | --- | --- |
| PIDP-HUMAN-001 | Review existing decision packet | Open the production identity-provider decision packet and inspect the candidate provider slots. | Human understands which provider candidates can be reviewed. | `phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_decision_packet.md` | No provider contact or production configuration by Codex. |
| PIDP-HUMAN-002 | Collect human-reviewed source notes | Human owner reviews IdP admin documentation or internal security decision records and writes short source notes. | Source notes for selected provider, admin owner, issuer, audience, and JWKS rotation policy. | `phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_input_completion.csv` | No web/API fetching or vendor contact by Codex. |
| PIDP-HUMAN-003 | Provide required text fields | Human provides reviewer name, review date, selected provider name, and decision summary. | Required text fields available for local validator input generation. | `human_reviewer_name, review_date, selected_provider_name, decision_summary` | No customer validation or launch claim. |
| PIDP-HUMAN-004 | Generate local human-filled input | Run the completion helper with explicit human-provided fields and source notes. | production_identity_provider_decision_input.human_filled.local.json | `python3 scripts/saee_production_identity_provider_input_completion_helper.py --generate-input --human-reviewer-name '<human>' --review-date '<YYYY-MM-DD>' --selected-provider-name '<provider>' --decision-summary '<summary>' --selected-provider-slot idp_candidate_a --candidate-source-note '<source note>' --confirm-production-identity-provider-selected true --confirm-identity-provider-admin-owner-named true --confirm-oidc-issuer-verified true --confirm-oidc-audience-approved true --confirm-jwks-rotation-policy-reviewed true --source-note-production-identity-provider-selected '<source note>' --source-note-identity-provider-admin-owner-named '<source note>' --source-note-oidc-issuer-verified '<source note>' --source-note-oidc-audience-approved '<source note>' --source-note-jwks-rotation-policy-reviewed '<source note>'` | Generated local input is not evidence collection, auth enablement, or blocker closure. |
| PIDP-HUMAN-005 | Validate local human-filled input | Run the approval input validator against the generated local input. | Validator status pass, hold, or stop. | `python3 scripts/saee_production_identity_provider_approval_input_validator.py --input phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_decision_input.human_filled.local.json` | Validator pass does not itself close blockers. |
| PIDP-HUMAN-006 | Request separate evidence-builder approval | If validator status is pass, create a separate human-approved evidence-builder request. | Separate approved evidence request, or hold if validation is incomplete. | `phase_b_product/commercial_readiness/PHASE_1_IDENTITY_TENANT_EVIDENCE_BUILDER_V0_1.md` | No evidence builder execution from this runbook. |

## Boundary

- external_calls_made_by_codex: false
- external_model_api_called: false
- identity_provider_contacted_by_codex: false
- jwks_fetched_by_codex: false
- production_tokens_validated_by_codex: false
- production_auth_enabled: false
- evidence_collection_authorized: false
- execution_authorized: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
