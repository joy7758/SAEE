# SAEE Commercial Boundary Hardening v0.1

Status: local commercial-readiness hardening, not production readiness.

## Purpose

This layer adds deployment-facing boundary controls to the local SAEE MVP API
shell without changing the private core, evaluation logic, public schema, or
landing page interaction.

## What Changed

- CORS origins are now read from `SAEE_ALLOWED_ORIGINS`.
- Local demo origins remain the default.
- Experiment endpoints can require `X-SAEE-API-Key` when
  `SAEE_REQUIRE_API_KEY=true`.
- Auth readiness is now reported as local demo, controlled preview API key
  auth, or missing production identity infrastructure.
- Identity-provider configuration readiness reports whether future production
  OIDC/RBAC inputs are present without enabling production auth.
- Controlled-preview RBAC route enforcement can require `X-SAEE-Role` when
  `SAEE_REQUIRE_RBAC_ROLE=true` and a local policy path is configured.
- Experiment endpoints can require `X-SAEE-Tenant-ID` when
  `SAEE_REQUIRE_TENANT_ID=true`.
- `/ready` reports configuration readiness and explicit non-claims.

## Environment Variables

```text
SAEE_ENV=local
SAEE_ALLOWED_ORIGINS=http://127.0.0.1:8765,http://localhost:8765
SAEE_REQUIRE_API_KEY=false
SAEE_API_KEY=
SAEE_MAX_AGENTS=100
SAEE_MAX_REPEAT_RUNS=10000
SAEE_MAX_TIME_HORIZON=100000
SAEE_MAX_PAYLOAD_BYTES=1048576
SAEE_STORAGE_BACKEND=memory
SAEE_STORAGE_PATH=.saee_data/saee_mvp.sqlite3
SAEE_REQUEST_AUDIT_ENABLED=false
SAEE_REQUEST_AUDIT_PATH=.saee_data/request_audit.jsonl
SAEE_RETENTION_DAYS=0
SAEE_RETENTION_DRY_RUN=true
SAEE_BACKUP_DIR=.saee_backups
SAEE_RESTORE_DRILL_DIR=.saee_restore_drills
SAEE_REQUIRE_TENANT_ID=false
SAEE_ALLOWED_TENANT_IDS=
SAEE_PRODUCTION_OIDC_ISSUER=
SAEE_PRODUCTION_OIDC_AUDIENCE=
SAEE_PRODUCTION_OIDC_JWKS_URL=
SAEE_PRODUCTION_RBAC_POLICY_PATH=
SAEE_REQUIRE_RBAC_ROLE=false
SAEE_RBAC_POLICY_PATH=
```

## Readiness Output

`GET /ready` returns public-shell deployment state:

```json
{
  "status": "ready",
  "environment": "local",
  "api_key_required": false,
  "api_key_configured": false,
  "auth_boundary_available": true,
  "auth_mode": "local_none",
  "preview_auth_available": false,
  "identity_provider_config_readiness_v0_1": true,
  "production_oidc_configuration_present": false,
  "production_rbac_policy_path_configured": false,
  "rbac_preview_enforcement_available": true,
  "rbac_role_required": false,
  "rbac_policy_path_configured": false,
  "preview_rbac_available": false,
  "external_identity_provider_contacted": false,
  "production_identity_provider_available": false,
  "oauth_oidc_available": false,
  "sso_available": false,
  "rbac_available": false,
  "production_auth_ready": false,
  "max_agents": 100,
  "max_repeat_runs": 10000,
  "max_time_horizon": 100000,
  "max_payload_bytes": 1048576,
  "storage_backend": "memory",
  "storage_path_configured": true,
  "durable_persistence": false,
  "request_audit_enabled": false,
  "request_audit_path_configured": true,
  "request_audit_log_available": false,
  "local_operations_telemetry_available": true,
  "operations_telemetry_source": "request_audit_jsonl",
  "operations_telemetry_external_export_available": false,
  "local_alert_policy_available": true,
  "external_alert_delivery_available": false,
  "operations_readiness_available": true,
  "operations_readiness_status": "hold",
  "production_monitoring_available": false,
  "alerting_available": false,
  "incident_response_runbook_available": true,
  "support_readiness_v0_1": true,
  "support_runbook_available": true,
  "support_contact_configured": false,
  "customer_support_available": false,
  "production_support_available": false,
  "on_call_rotation_available": false,
  "sla_available": false,
  "support_process_available": false,
  "production_operations_ready": false,
  "commercial_preflight_available": true,
  "commercial_preflight_required_for_public_use": true,
  "data_retention_available": true,
  "retention_policy_configured": false,
  "retention_days": 0,
  "retention_dry_run": true,
  "data_backup_available": true,
  "backup_dir_configured": true,
  "backup_default_automatic": false,
  "restore_drill_available": true,
  "restore_drill_dir_configured": true,
  "restore_drill_default_automatic": false,
  "production_restore_policy_available": false,
  "restore_tested": false,
  "tenant_boundary_available": true,
  "tenant_id_required": false,
  "tenant_allowlist_configured": false,
  "preview_storage_scoped_by_tenant": false,
  "tenant_storage_isolated": false,
  "tenant_billing_isolated": false,
  "multi_tenant_production_ready": false,
  "production_ready": false,
  "customer_validated": false,
  "public_sdk_released": false,
  "product_launched": false,
  "private_core_connected": false,
  "private_core_exposed": false
}
```

## Required Design Check

1. Which evolution subsystem does this strengthen?

   It strengthens the public-shell deployment boundary around Sandbox
   Development and Evolutionary Archive access. It does not modify the
   evolution loop itself.

2. Does it improve sensing, branching, variation, selection, archive, or rollback?

   It improves archive/report access safety and deployment configuration. It
   does not change sensing, branching, mutation, selection, scoring, lineage,
   rollback, or runtime behavior.

3. Does it preserve safety, license, supply-chain, and permission boundaries?

   Yes. It adds local configuration and optional request guarding using standard
   FastAPI behavior. It does not install dependencies, fetch code, contact
   customers, call external services, or expose private internals.

4. Could this change push the project back into audit-first framing?

   No. It keeps SAEE framed as long-term AI agent / policy stability
   evaluation. The change is deployment boundary hardening, not an audit SDK.

## Current Commercial Readiness

```text
local_mvp_runnable: true
commercial_boundary_hardening_v0_1: true
optional_api_key_guard: true
configurable_cors_origins: true
readiness_endpoint: true
auth_readiness_v0_1: true
controlled_preview_auth_possible: true
identity_provider_config_readiness_v0_1: true
production_oidc_configuration_present_default: false
production_rbac_policy_path_configured_default: false
rbac_preview_enforcement_v0_1: true
controlled_preview_rbac_guard_available: true
rbac_preview_default_required: false
preview_rbac_available_when_configured: true
rbac_enforced_in_controlled_preview: true
rbac_enforced_in_production: false
external_identity_provider_contacted: false
production_identity_provider_available: false
oauth_oidc_available: false
sso_available: false
rbac_available: false
production_auth_ready: false
request_limits_v0_1: true
persistence_v0_1: true
storage_backend_configurable: true
sqlite_persistence_option: true
request_audit_v0_1: true
request_audit_default_enabled: false
operations_telemetry_v0_1: true
local_operations_telemetry_available: true
operations_telemetry_external_export_available: false
operations_readiness_v0_1: true
operations_readiness_status: hold
operations_alert_policy_v0_1: true
local_alert_policy_available: true
external_alert_delivery_available: false
production_monitoring_available: false
alerting_available: false
incident_response_runbook_available: true
support_readiness_v0_1: true
support_runbook_available: true
support_contact_configured: false
customer_support_available: false
production_support_available: false
on_call_rotation_available: false
sla_available: false
support_process_available: false
production_operations_ready: false
commercial_preflight_v0_1: true
commercial_preflight_default_local_status: hold
controlled_preview_possible: true
data_retention_v0_1: true
retention_default_dry_run: true
retention_policy_configured: false
data_backup_v0_1: true
backup_default_automatic: false
data_restore_drill_v0_1: true
restore_drill_default_automatic: false
production_restore_policy_available: false
restore_tested: false
tenant_boundary_v0_1: true
tenant_boundary_default_required: false
preview_storage_scoped_by_tenant: true
tenant_storage_isolated: false
tenant_billing_isolated: false
tenant_authorization_policy_available: false
multi_tenant_production_ready: false
production_backup_policy_available: false
production_database_ready: false
production_monitoring_available: false
production_ready: false
customer_validated: false
product_launched: false
public_sdk_released: false
private_core_connected: false
private_core_exposed: false
```

## Remaining Gaps Before Formal Commercial Use

- durable persistence and tenant-isolated storage;
- request audit retention, access control, and production monitoring integration;
- tenant-scoped audit ownership, tenant-aware retention policy, deletion approval, production backup, and restore testing;
- production authentication and authorization policy, including external identity provider, OIDC/SSO, RBAC, account lifecycle, and admin recovery;
- deployment packaging and operational runbook;
- privacy, terms, data-retention, and incident-response documents;
- monitored production environment;
- customer validation with real buyer workflows;
- support, billing, onboarding, and SLA boundaries.
