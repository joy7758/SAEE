# SAEE Auth Readiness v0.1

Status: local/pre-commercial authentication readiness, not production identity.

## Purpose

SAEE Auth Readiness v0.1 makes the authentication boundary machine-readable for
the MVP API shell. It separates:

- local demo mode with no auth requirement;
- controlled-preview API key auth using `X-SAEE-API-Key`;
- missing production identity infrastructure.

This does not implement OAuth, OIDC, SSO, RBAC, account provisioning, session
management, or production authorization.

## Current Auth Modes

```text
local_none: default local demo mode
api_key_required_unconfigured: API key guard enabled without SAEE_API_KEY
api_key_preview: controlled-preview API key guard configured
```

## Environment Variables

```text
SAEE_REQUIRE_API_KEY=false
SAEE_API_KEY=
```

When `SAEE_REQUIRE_API_KEY=true`, experiment routes require:

```text
X-SAEE-API-Key: <SAEE_API_KEY>
```

## Readiness Fields

`GET /ready` reports:

```text
auth_boundary_available: true
auth_mode: local_none
preview_auth_available: false
production_identity_provider_available: false
oauth_oidc_available: false
sso_available: false
rbac_available: false
production_auth_ready: false
```

## Command

```bash
python3 scripts/saee_auth_readiness.py
```

The command reads local configuration and prints a deterministic JSON report.
It does not call external identity providers, start the server, contact
customers, modify API schema, or inspect private core.

## Status Rules

```text
local default configuration -> hold
non-local configuration without API key auth -> hold
non-local configuration with API key auth -> pass for controlled preview only
production identity provider availability -> false
production auth readiness -> false
```

`pass` means only that controlled-preview API key auth is configured. It does
not mean production authentication or formal commercial readiness.

## Required Design Check

1. Which evolution subsystem does this strengthen?

   It strengthens Sandbox Development and the Rollback Immune System by
   preventing local demo access from being confused with controlled preview or
   production identity readiness.

2. Does it improve sensing, branching, variation, selection, archive, or rollback?

   It improves deployment-boundary sensing and rollback readiness. It does not
   modify sensing, branching, mutation, selection, scoring, fitness, lineage,
   runtime, kernel, or private core.

3. Does it preserve safety, license, supply-chain, and permission boundaries?

   Yes. It reads local configuration only, adds no dependency, makes no
   external call, changes no public schema, and exposes no private internals.

4. Could this change push the project back into audit-first framing?

   No. Authentication readiness is a commercial boundary for controlled preview
   access. Audit remains an immune/evidence subsystem.

## Current State

```text
auth_readiness_v0_1: true
auth_boundary_available: true
local_default_status: hold
controlled_preview_auth_possible: true
preview_auth_available: true
production_identity_provider_available: false
oauth_oidc_available: false
sso_available: false
rbac_available: false
production_auth_ready: false
api_schema_modified: false
runtime_modified: false
kernel_modified: false
private_core_exposed: false
production_ready: false
customer_validated: false
product_launched: false
public_sdk_released: false
external_calls_made: false
```

## Remaining Gaps

Formal commercial use still needs external identity provider selection, OIDC or
SSO integration, role and permission model, account provisioning, session and
token lifecycle rules, admin recovery procedures, audit ownership, incident
response, and customer validation.
