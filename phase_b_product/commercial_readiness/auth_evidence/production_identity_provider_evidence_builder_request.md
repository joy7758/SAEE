# SAEE Production Identity Provider Evidence Builder Request Template

Status: hold_human_evidence_builder_request_required.

This local template records the separate human approval request needed before running the Phase 1 identity/tenant evidence builder for the `production_identity_provider` blocker. It does not execute the builder, contact an identity provider, fetch JWKS, validate production tokens, enable production auth, close blockers, launch product, or claim production readiness.

## Summary

- request_template_type: saee_production_identity_provider_evidence_builder_request_template
- request_scope: separate_human_approval_for_phase1_identity_tenant_evidence_builder
- target_blocker_id: production_identity_provider
- target_builder: `scripts/saee_phase1_identity_tenant_evidence_builder.py`
- request_template_ready: true
- request_approved: false
- approval_input_validator_passed: false
- human_filled_input_available: false
- evidence_builder_execution_authorized: false
- evidence_builder_executed: false
- phase1_builder_output_created_by_request: false
- blockers_closed_by_request_template: 0
- production_ready: false

## Completion Items

| Item | Field | Type | Required | Current | Complete | Human Instruction |
| --- | --- | --- | --- | --- | --- | --- |
| PIDP-EBR-001 | `human_requester_name` | text | nonempty |  | false | Name of the human owner requesting builder approval. |
| PIDP-EBR-002 | `request_date` | text | nonempty |  | false | Request date in YYYY-MM-DD format. |
| PIDP-EBR-003 | `approval_reference` | text | nonempty |  | false | Reference to the passing approval-input validation record. |
| PIDP-EBR-004 | `validated_input_path` | text | nonempty |  | false | Path to the human-filled input that passed validation. |
| PIDP-EBR-005 | `human_acknowledgements.approval_input_validator_passed` | boolean | true | false | false | Human must set this acknowledgement to true before builder execution can be separately requested. |
| PIDP-EBR-006 | `human_acknowledgements.runbook_reviewed` | boolean | true | false | false | Human must set this acknowledgement to true before builder execution can be separately requested. |
| PIDP-EBR-007 | `human_acknowledgements.human_filled_input_available` | boolean | true | false | false | Human must set this acknowledgement to true before builder execution can be separately requested. |
| PIDP-EBR-008 | `human_acknowledgements.validated_input_path_confirmed` | boolean | true | false | false | Human must set this acknowledgement to true before builder execution can be separately requested. |
| PIDP-EBR-009 | `human_acknowledgements.phase1_builder_input_path_confirmed` | boolean | true | false | false | Human must set this acknowledgement to true before builder execution can be separately requested. |
| PIDP-EBR-010 | `human_acknowledgements.target_builder_confirmed` | boolean | true | false | false | Human must set this acknowledgement to true before builder execution can be separately requested. |
| PIDP-EBR-011 | `human_acknowledgements.no_external_calls_by_codex` | boolean | true | false | false | Human must set this acknowledgement to true before builder execution can be separately requested. |
| PIDP-EBR-012 | `human_acknowledgements.no_identity_provider_contact_by_codex` | boolean | true | false | false | Human must set this acknowledgement to true before builder execution can be separately requested. |
| PIDP-EBR-013 | `human_acknowledgements.no_jwks_fetch_by_codex` | boolean | true | false | false | Human must set this acknowledgement to true before builder execution can be separately requested. |
| PIDP-EBR-014 | `human_acknowledgements.no_production_auth_enablement` | boolean | true | false | false | Human must set this acknowledgement to true before builder execution can be separately requested. |
| PIDP-EBR-015 | `human_acknowledgements.no_blocker_closure_by_request` | boolean | true | false | false | Human must set this acknowledgement to true before builder execution can be separately requested. |

## Boundary

- external_calls_made_by_codex: false
- external_model_api_called: false
- identity_provider_contacted_by_codex: false
- jwks_fetched_by_codex: false
- production_tokens_validated_by_codex: false
- production_auth_enabled: false
- evidence_collection_authorized: false
- execution_authorized: false
- development_permission_granted: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
