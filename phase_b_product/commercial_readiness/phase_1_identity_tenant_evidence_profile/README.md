# SAEE Phase 1 Identity/Tenant Evidence Profile

Status: local profile available; default output is hold.

This directory contains the local profile that connects Phase 1 evidence-builder
outputs to the existing commercial go/no-go aggregation.

Primary files:

```text
phase_1_identity_tenant_evidence_profile.env.example
phase_1_identity_tenant_evidence_profile.local.json
phase_1_identity_tenant_evidence_profile.md
```

Generate them with:

```bash
python3 scripts/saee_phase1_identity_tenant_evidence_profile.py
```

Boundary:

```yaml
phase_1_identity_tenant_evidence_profile_v0_1: true
profile_scope: local_phase_1_builder_outputs_to_go_no_go_profile
default_profile_status: hold
phase_1_blockers_closed_by_profile: 0
development_permission_granted_for_local_scope: true
rbac_role_permission_consistency_enforced: true
production_deployment_authorized: false
production_launch_status: hold
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
external_calls_made: false
```
