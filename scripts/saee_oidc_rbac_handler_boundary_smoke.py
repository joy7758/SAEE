#!/usr/bin/env python3
"""Prove rejected signed requests stop before the synthetic handler boundary."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.oidc_jwks_verifier import (
    OfflineOidcVerificationError,
    verify_and_bind_offline_oidc_token,
)
from scripts.generate_rbac_policy_template import TEMPLATE_PATH, generate_template
from scripts.saee_oidc_jwks_verifier_smoke import (
    AUDIENCE,
    CAPABILITY_SECRET,
    ISSUER,
    JWKS,
    NOW,
    RECEIPT_SECRET,
    ROLE,
    TENANT,
    base_claims,
    changed_claim,
    sign_token,
)


def authorize(token: str, *, tenant: str = TENANT, role: str = ROLE, route: str = "POST /experiment/create"):
    return verify_and_bind_offline_oidc_token(
        token,
        local_jwks=JWKS,
        expected_issuer=ISSUER,
        expected_audience=AUDIENCE,
        now=NOW,
        requested_tenant_id=tenant,
        route_scope=route,
        requested_role=role,
        policy_path=str(TEMPLATE_PATH),
        capability_secret=CAPABILITY_SECRET,
        verification_receipt_secret=RECEIPT_SECRET,
    )


def main() -> None:
    generate_template()
    handler_calls: list[str] = []

    def handler(context: Any) -> None:
        handler_calls.append(context.tenant_id)

    handler(authorize(sign_token()))
    if handler_calls != [TENANT]:
        raise SystemExit("SAEE_OIDC_RBAC_HANDLER_BOUNDARY_SMOKE: FAIL: valid handler path")

    token = sign_token()
    expired = changed_claim(exp=NOW - 100)
    personal = base_claims()
    personal["email"] = "synthetic-at-example.invalid"
    cases = [
        (token[:-1] + ("A" if token[-1] != "A" else "B"), TENANT, ROLE, "POST /experiment/create"),
        (token, "tenant-agent-b", ROLE, "POST /experiment/create"),
        (token, TENANT, "owner", "POST /experiment/create"),
        (token, TENANT, ROLE, "POST /unknown"),
        (sign_token(expired), TENANT, ROLE, "POST /experiment/create"),
        (sign_token(personal), TENANT, ROLE, "POST /experiment/create"),
    ]
    before = len(handler_calls)
    for rejected_token, tenant, role, route in cases:
        try:
            context = authorize(rejected_token, tenant=tenant, role=role, route=route)
        except (OfflineOidcVerificationError, ValueError):
            continue
        handler(context)
        raise SystemExit("SAEE_OIDC_RBAC_HANDLER_BOUNDARY_SMOKE: FAIL: rejected request reached handler")
    if len(handler_calls) != before:
        raise SystemExit("SAEE_OIDC_RBAC_HANDLER_BOUNDARY_SMOKE: FAIL: handler count changed")
    print("SAEE_OIDC_RBAC_HANDLER_BOUNDARY_SMOKE: PASS")
    print("valid_handler_calls=1")
    print("rejected_before_handler=6")
    print("external_calls=0")
    print("production_blockers_closed=0")


if __name__ == "__main__":
    main()
