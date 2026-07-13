#!/usr/bin/env python3
"""Verify the exact local-only Phase 1 execution authorization boundary."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTHORIZATION = ROOT / "phase_b_product/commercial_readiness/phase_1_local_execution_authorization/authorization.local.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_PHASE1_LOCAL_EXECUTION_AUTHORIZATION_SMOKE: FAIL " + message)


def main() -> None:
    data = json.loads(AUTHORIZATION.read_text(encoding="utf-8"))
    require(data["target_phase"] == "phase_1_identity_and_tenant_boundary", "phase")
    require(len(data["target_blocker_ids"]) == 4, "blocker count")
    require(all(data["authorized_local_actions"].values()), "all local actions authorized")
    require(data["development_permission_granted_for_local_scope"] is True, "local development permission")
    require(data["sanitized_local_evidence_collection_authorized"] is True, "sanitized evidence permission")
    for key in (
        "customer_contact_authorized", "identity_provider_contact_authorized",
        "vendor_contract_authorized", "legal_signature_authorized",
        "public_pricing_authorized", "payment_enablement_authorized",
        "production_deployment_authorized", "production_data_migration_authorized",
        "blocker_closure_authorized", "external_calls_authorized",
        "production_ready", "customer_validated", "product_launched",
    ):
        require(data[key] is False, key)
    require(data["blockers_closed"] == 0, "blocker closure boundary")
    print("SAEE_PHASE1_LOCAL_EXECUTION_AUTHORIZATION_SMOKE: PASS local_code=true local_contracts=true local_tests=true sanitized_evidence=true zh_cn_site=true external_calls=false production_deployment=false blockers_closed=0")


if __name__ == "__main__":
    main()
