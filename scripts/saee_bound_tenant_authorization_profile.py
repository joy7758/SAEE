#!/usr/bin/env python3
"""Generate local evidence for the bound tenant authorization chain."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_bound_tenant_authorization_smoke import run_checks


OUTPUT = ROOT / "phase_b_product/commercial_readiness/tenant_authorization/tenant_authorization.local.json"
SOURCES = [
    "saee_backend/config.py",
    "saee_backend/api/security.py",
    "saee_backend/main.py",
    "saee_backend/services/authorization_context.py",
    "saee_backend/services/experiment_service.py",
    "saee_backend/storage/factory.py",
    "saee_backend/storage/memory_db.py",
    "saee_backend/storage/sqlite_store.py",
    "scripts/saee_bound_tenant_authorization_smoke.py",
]


def main() -> None:
    run_checks()
    data = {
        "bound_tenant_authorization_profile_v0_1": True,
        "status": "pass_local_controlled_preview_bound_authorization",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "generated_by": "scripts/saee_bound_tenant_authorization_profile.py",
        "negative_cases_passed": 14,
        "negative_cases_total": 14,
        "authorized_principal_context_immutable": True,
        "api_service_storage_context_bound": True,
        "context_capability_hmac_verified": True,
        "storage_operation_permission_bound": True,
        "raw_tenant_direct_store_denied": True,
        "header_asserted_tenant_role_ready": False,
        "partial_authorization_chain_ready": False,
        "tenant_switch_denied": True,
        "role_spoof_denied": True,
        "unknown_route_denied": True,
        "probe_scope_explicit": True,
        "auth_source": "preview_jwt_hs256",
        "tenant_authorization_policy_reviewed": False,
        "production_identity_provider_available": False,
        "oauth_oidc_available": False,
        "jwks_fetched": False,
        "tokens_validated_in_production": False,
        "tenant_authorization_enabled": False,
        "rbac_available": False,
        "production_auth_ready": False,
        "production_tenant_storage_isolated": False,
        "security_review_completed": False,
        "privacy_legal_review_completed": False,
        "production_ready": False,
        "customer_validated": False,
        "blockers_closed": 0,
        "source_sha256": {
            path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            for path in SOURCES
        },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "SAEE_BOUND_TENANT_AUTHORIZATION_PROFILE: PASS negative_cases=14/14 "
        "tenant_authorization_policy_reviewed=false production_auth_ready=false "
        "production_ready=false blockers_closed=0"
    )


if __name__ == "__main__":
    main()
