#!/usr/bin/env python3
"""Validate the local bound tenant authorization profile."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_bound_tenant_authorization_profile import OUTPUT, SOURCES, main as run



def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_BOUND_TENANT_AUTHORIZATION_PROFILE_SMOKE: FAIL: " + message)


def main() -> None:
    run()
    data = json.loads(OUTPUT.read_text(encoding="utf-8"))
    require(data["status"] == "pass_local_controlled_preview_bound_authorization", "status")
    require(data["negative_cases_passed"] == data["negative_cases_total"] == 14, "cases")
    for key in (
        "authorized_principal_context_immutable",
        "api_service_storage_context_bound",
        "context_capability_hmac_verified",
        "storage_operation_permission_bound",
        "raw_tenant_direct_store_denied",
        "tenant_switch_denied",
        "role_spoof_denied",
        "unknown_route_denied",
        "probe_scope_explicit",
    ):
        require(data[key] is True, key)
    for key in (
        "header_asserted_tenant_role_ready",
        "partial_authorization_chain_ready",
        "tenant_authorization_policy_reviewed",
        "production_identity_provider_available",
        "oauth_oidc_available",
        "jwks_fetched",
        "tokens_validated_in_production",
        "tenant_authorization_enabled",
        "rbac_available",
        "production_auth_ready",
        "production_tenant_storage_isolated",
        "security_review_completed",
        "privacy_legal_review_completed",
        "production_ready",
        "customer_validated",
    ):
        require(data[key] is False, key)
    require(data["blockers_closed"] == 0, "blockers")
    for path in SOURCES:
        require(
            data["source_sha256"][path]
            == hashlib.sha256((ROOT / path).read_bytes()).hexdigest(),
            "source hash " + path,
        )
    print(
        "SAEE_BOUND_TENANT_AUTHORIZATION_PROFILE_SMOKE: PASS negative_cases=14/14 "
        "tenant_authorization_policy_reviewed=false production_ready=false blockers_closed=0"
    )


if __name__ == "__main__":
    main()
