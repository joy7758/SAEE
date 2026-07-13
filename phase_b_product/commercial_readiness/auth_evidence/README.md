# SAEE Auth Evidence

Status: local public-shell auth review evidence, not production auth readiness.

This directory contains a generated local evidence JSON file for future
identity-provider, OAuth/OIDC, and RBAC production-auth review. It records only
what the local runner can prove from existing public-shell readiness materials.

It does not select or contact an identity provider, fetch JWKS, validate
production tokens, approve OAuth/OIDC flow, approve production RBAC, enforce
RBAC, enable production authentication, contact customers, modify runtime
behavior, modify backend behavior, modify API schema, or expose private core.

Primary file:

```text
auth_evidence.local.json
production_auth_evidence_path.local.json
production_auth_evidence_path_report.md
production_identity_provider_decision_packet.local.json
production_identity_provider_decision_packet.md
production_identity_provider_decision_input.template.json
production_identity_provider_decision_packet_boundary_audit.md
production_identity_provider_approval_input_validation.local.json
production_identity_provider_approval_input_validation.md
rbac_approval_input_validation.local.json
rbac_approval_input_validation.md
```

Generate it with:

```bash
python3 scripts/saee_auth_evidence_runner.py
python3 scripts/saee_production_auth_evidence_path.py
python3 scripts/saee_production_identity_provider_decision_packet.py
python3 scripts/saee_production_identity_provider_approval_input_validator.py
python3 scripts/saee_oauth_oidc_approval_input_validator.py
python3 scripts/saee_rbac_approval_input_validator.py
```

Boundary:

```yaml
evidence_scope: local_public_shell_auth_review_packet
production_auth_evidence_path_available: true
production_auth_evidence_path_status: local_fixture_only_path_proof
production_auth_evidence_path_type: local_fixture_only_production_auth_evidence_path
production_auth_evidence_path_fixture_only: true
production_auth_evidence_path_real_identity_provider_selected: false
production_auth_evidence_path_real_oauth_oidc_flow_approved: false
production_auth_evidence_path_real_rbac_policy_approved: false
production_auth_evidence_path_real_production_tokens_validated: false
production_auth_evidence_path_blocker_path_proven: true
production_auth_evidence_path_auth_identity_provider_path_available: true
production_auth_evidence_path_auth_oauth_oidc_path_available: true
production_auth_evidence_path_auth_rbac_path_available: true
production_auth_evidence_path_auth_ready_path_available: true
production_auth_evidence_path_target_blockers_satisfied_count: 3
production_auth_evidence_path_production_blocker_count: 21
production_auth_evidence_path_closes_blockers: false
preview_api_key_auth_available: true
rbac_policy_template_available: true
role_matrix_reviewed: true
tenant_role_boundary_reviewed: true
production_identity_provider_selected: false
oauth_oidc_flow_approved: false
token_validation_test_recorded: false
rbac_policy_approved: false
production_identity_provider_available: false
oauth_oidc_available: false
rbac_available: false
production_auth_ready: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
identity_provider_contacted: false
jwks_fetched: false
tokens_validated_in_production: false
production_auth_enabled: false
rbac_enforced_in_production: false
```

The production identity-provider decision packet is a focused human-review
surface for the `production_identity_provider` blocker. It maps the identity
provider fields that would later be required by Phase 1 identity/tenant
evidence, but it does not select or contact an identity provider, fetch JWKS,
validate production tokens, enable production authentication, close blockers,
or claim production readiness.

The production-auth evidence path is a fixture-only path proof. It proves that
complete production identity-provider, OAuth/OIDC, and RBAC evidence can flow
through the existing production-auth evidence readiness and commercial go/no-go
checks. It does not select or contact an identity provider, fetch JWKS,
validate production tokens, enable production authentication, enforce
production RBAC, close blockers by itself, launch product, contact customers,
or claim production readiness.

The production identity-provider approval input validator checks human-filled
identity-provider decision input before evidence-builder use. It writes
`production_identity_provider_approval_input_validation.local.json` and
`production_identity_provider_approval_input_validation.md`, remains `hold` by
default, and closes zero blockers.

```yaml
production_identity_provider_approval_input_validator_status: hold
production_identity_provider_approval_input_validator_builder_ready: false
production_identity_provider_approval_input_validator_closes_blockers: 0
```

The OAuth/OIDC approval input validator checks the five OAuth/OIDC evidence
fields in the Phase 1 identity/tenant evidence template. It writes
`phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/oauth_oidc_approval_input_validation.local.json`,
remains `hold` by default, and does not validate production tokens or enable
production auth.

```yaml
oauth_oidc_approval_input_validator_status: hold
oauth_oidc_approval_input_validator_builder_ready: false
oauth_oidc_approval_input_validator_closes_blockers: 0
```

The RBAC approval input validator checks the five RBAC evidence fields in the
Phase 1 identity/tenant evidence template. It writes
`phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/rbac_approval_input_validation.local.json`,
remains `hold` by default, and does not enforce production RBAC or enable
production auth.

```yaml
rbac_approval_input_validator_status: hold
rbac_approval_input_validator_builder_ready: false
rbac_approval_input_validator_closes_blockers: 0
```
