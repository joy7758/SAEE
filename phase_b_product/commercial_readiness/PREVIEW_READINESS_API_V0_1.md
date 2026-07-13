# SAEE Preview Readiness API v0.1

Status: local/pre-commercial read-only readiness API, not production support or production security operations.

Preview Readiness API v0.1 exposes existing support and vulnerability-readiness
reports through the public API shell so a human operator can verify controlled
preview configuration before inviting a reviewer. It is a read-only
agent-readable surface. It does not create support, security operations,
ticketing, customer support, SLA, production monitoring, vulnerability
management, customer validation, product launch, or production readiness.

## Routes

```text
GET /readiness/support
GET /readiness/vulnerability
```

Both routes reuse the API-key guard and tenant request-envelope guard when
those preview controls are configured.

## What The Routes Return

`GET /readiness/support` returns the same support-readiness report used by:

```bash
python3 scripts/saee_support_readiness.py
```

It reports whether a controlled-preview support contact is configured as a
boolean. It does not return the contact value.

`GET /readiness/vulnerability` returns the same vulnerability-intake readiness
report used by:

```bash
python3 scripts/saee_vulnerability_management_readiness.py
```

It reports whether a controlled-preview security contact is configured as a
boolean. It does not return the contact value.

## Current State

```text
preview_readiness_api_v0_1: true
preview_readiness_api_available: true
read_only_preview_readiness_api: true
preview_readiness_routes_available: true
route_scope: public_shell_preview_readiness_read_only
support_route: /readiness/support
vulnerability_route: /readiness/vulnerability
support_contact_value_exposed: false
security_contact_value_exposed: false
request_body_inspected: false
response_body_inspected: false
credentials_inspected: false
private_core_inspected: false
customer_support_available: false
production_support_available: false
sla_available: false
on_call_rotation_available: false
vulnerability_management_available: false
production_vulnerability_management_ready: false
formal_security_review_completed: false
production_security_ready: false
production_ready: false
customer_validated: false
product_launched: false
public_sdk_released: false
private_core_exposed: false
api_schema_modified: false
runtime_modified: false
kernel_modified: false
external_calls_made: false
external_model_api_called: false
customer_contacted: false
```

## Controlled Preview Use

Use these routes after configuring the controlled-preview environment:

```text
SAEE_ENV=preview
SAEE_REQUIRE_API_KEY=true
SAEE_API_KEY=<local-preview-secret>
SAEE_REQUIRE_TENANT_ID=true
SAEE_ALLOWED_TENANT_IDS=<approved-preview-tenant-id>
SAEE_SUPPORT_CONTACT=<approved-preview-support-mailbox-or-ticket-queue>
SAEE_SECURITY_CONTACT=<approved-preview-security-mailbox-or-ticket-queue>
```

Expected useful checks:

- `support_contact_configured` should be `true` before a controlled preview.
- `security_contact_configured` should be `true` before a controlled preview.
- `customer_support_available` must remain `false`.
- `production_support_available` must remain `false`.
- `sla_available` must remain `false`.
- `vulnerability_management_available` must remain `false`.
- `production_vulnerability_management_ready` must remain `false`.
- `private_core_exposed` must remain `false`.

## What This Does Not Provide

- production identity, OAuth/OIDC, SSO, or RBAC;
- production customer support;
- staffed ticket queue;
- contractual SLA;
- on-call rotation;
- production security operations;
- vulnerability scanning;
- penetration testing;
- remediation SLA;
- coordinated disclosure program;
- customer notification workflow;
- customer validation;
- production readiness.

## Commercial Readiness Role

This API closes a controlled-preview usability gap: after an operator replaces
the placeholder contact values outside the repository, a reviewer can verify
from the running API that support and security intake are configured as booleans
without exposing the contact values themselves.

It does not close the production launch blockers for customer support, SLA,
on-call, vulnerability management, formal security review, or customer
validation.
