#!/usr/bin/env python3
"""Generate a local SAEE production RBAC policy template.

The generated policy is a review template for future production-auth work. It
does not enforce RBAC, validate tokens, contact identity providers, modify API
schema, or claim production authentication readiness.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.identity_provider_readiness import (
    REQUIRED_RBAC_PERMISSIONS,
    REQUIRED_RBAC_ROLES,
    REQUIRED_ROUTE_SCOPES,
)


TEMPLATE_DIR = ROOT / "phase_b_product/commercial_readiness/rbac_policy_templates"
TEMPLATE_PATH = TEMPLATE_DIR / "production_rbac_policy.template.json"


ROLE_DEFINITIONS = {
    "owner": {
        "description": "Account owner role for future human-approved production auth.",
        "permissions": sorted(REQUIRED_RBAC_PERMISSIONS),
    },
    "admin": {
        "description": "Administrative role without ownership transfer authority.",
        "permissions": [
            "audit:read",
            "experiment:create",
            "experiment:read",
            "experiment:run",
            "operations:read",
            "readiness:read",
            "support:read",
            "support:triage",
        ],
    },
    "evaluator_operator": {
        "description": "Operator role for creating and running evaluation jobs.",
        "permissions": [
            "experiment:create",
            "experiment:read",
            "experiment:run",
            "readiness:read",
        ],
    },
    "viewer": {
        "description": "Read-only role for evaluation result inspection.",
        "permissions": [
            "experiment:read",
            "readiness:read",
        ],
    },
    "support_operator": {
        "description": "Support role for future triage without private core access.",
        "permissions": [
            "audit:read",
            "experiment:read",
            "operations:read",
            "readiness:read",
            "support:read",
            "support:triage",
        ],
    },
}


ROUTE_PERMISSIONS = {
    "GET /commercial/status": ("readiness:read", ["owner", "admin", "support_operator"]),
    "GET /health": ("readiness:read", ["owner", "admin", "evaluator_operator", "viewer", "support_operator"]),
    "GET /ready": ("readiness:read", ["owner", "admin", "evaluator_operator", "viewer", "support_operator"]),
    "GET /experiment": ("experiment:read", ["owner", "admin", "evaluator_operator", "viewer", "support_operator"]),
    "POST /experiment/create": ("experiment:create", ["owner", "admin", "evaluator_operator"]),
    "POST /experiment/run": ("experiment:run", ["owner", "admin", "evaluator_operator"]),
    "GET /experiment/{experiment_id}/stability": ("experiment:read", ["owner", "admin", "evaluator_operator", "viewer", "support_operator"]),
    "GET /experiment/{experiment_id}/failures": ("experiment:read", ["owner", "admin", "evaluator_operator", "viewer", "support_operator"]),
    "GET /experiment/{experiment_id}/ranking": ("experiment:read", ["owner", "admin", "evaluator_operator", "viewer", "support_operator"]),
    "GET /experiment/{experiment_id}/survival": ("experiment:read", ["owner", "admin", "evaluator_operator", "viewer", "support_operator"]),
    "GET /operations/telemetry": ("operations:read", ["owner", "admin", "support_operator"]),
    "GET /operations/alerts": ("operations:read", ["owner", "admin", "support_operator"]),
    "GET /readiness/billing-pricing": ("readiness:read", ["owner", "admin", "support_operator"]),
    "GET /readiness/data-operations": ("readiness:read", ["owner", "admin", "support_operator"]),
    "GET /readiness/legal": ("readiness:read", ["owner", "admin", "support_operator"]),
    "GET /readiness/operations": ("readiness:read", ["owner", "admin", "support_operator"]),
    "GET /readiness/privacy-security": ("readiness:read", ["owner", "admin", "support_operator"]),
    "GET /readiness/support": ("readiness:read", ["owner", "admin", "support_operator"]),
    "GET /readiness/vulnerability": ("readiness:read", ["owner", "admin", "support_operator"]),
}


def _policy_payload() -> dict[str, object]:
    return {
        "policy_type": "saee_production_rbac_policy_template",
        "policy_version": "v0.1",
        "policy_status": "template_only_not_enforced",
        "rbac_policy_template_v0_1": True,
        "required_roles": sorted(REQUIRED_RBAC_ROLES),
        "required_permissions": sorted(REQUIRED_RBAC_PERMISSIONS),
        "required_route_scopes": sorted(REQUIRED_ROUTE_SCOPES),
        "roles": [
            {
                "role": role,
                "description": ROLE_DEFINITIONS[role]["description"],
                "permissions": ROLE_DEFINITIONS[role]["permissions"],
            }
            for role in sorted(REQUIRED_RBAC_ROLES)
        ],
        "route_scopes": [
            {
                "route": route,
                "required_permission": ROUTE_PERMISSIONS[route][0],
                "allowed_roles": ROUTE_PERMISSIONS[route][1],
            }
            for route in sorted(REQUIRED_ROUTE_SCOPES)
        ],
        "production_identity_provider_available": False,
        "oauth_oidc_available": False,
        "rbac_available": False,
        "rbac_enforced": False,
        "production_auth_ready": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "public_sdk_released": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_identity_provider_contacted": False,
        "jwks_fetched": False,
        "tokens_validated": False,
        "notes": (
            "Template for future human-approved production auth implementation "
            "review. It is not an enforced RBAC policy."
        ),
    }


def _readme_text() -> str:
    roles = ", ".join(sorted(REQUIRED_RBAC_ROLES))
    permissions = ", ".join(sorted(REQUIRED_RBAC_PERMISSIONS))
    return f"""# SAEE RBAC Policy Templates v0.1

Status: template only; RBAC is not enforced.

This directory contains a local machine-readable RBAC policy template for future
production-auth implementation review. It supports the identity-provider
configuration readiness check but does not enable OAuth/OIDC, SSO, token
validation, route authorization, or production authentication.

Template:

- `production_rbac_policy.template.json`

Required roles:

{roles}

Required permissions:

{permissions}

Boundary:

- No runtime modified.
- No backend route behavior modified.
- No kernel modified.
- No API schema modified.
- No identity provider contacted.
- No JWKS fetched.
- No token validated.
- No RBAC enforcement enabled.
- No production authentication readiness claimed.
- No private core exposed.
"""


def generate_template() -> None:
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    TEMPLATE_PATH.write_text(
        json.dumps(_policy_payload(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (TEMPLATE_DIR / "README.md").write_text(_readme_text(), encoding="utf-8")


def main() -> None:
    generate_template()
    print(
        "SAEE_RBAC_POLICY_TEMPLATE_GENERATED: "
        f"path={TEMPLATE_PATH.relative_to(ROOT)} roles={len(REQUIRED_RBAC_ROLES)} "
        f"permissions={len(REQUIRED_RBAC_PERMISSIONS)} "
        f"route_scopes={len(REQUIRED_ROUTE_SCOPES)}"
    )


if __name__ == "__main__":
    main()
