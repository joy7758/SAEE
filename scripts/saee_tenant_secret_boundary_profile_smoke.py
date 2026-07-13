#!/usr/bin/env python3
"""Validate the generated tenant secret boundary profile."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_tenant_secret_boundary_profile import OUTPUT_PATH, SOURCE_PATHS, main as run


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_TENANT_SECRET_BOUNDARY_PROFILE_SMOKE: FAIL: " + message)


def main() -> None:
    run()
    data = json.loads(OUTPUT_PATH.read_text())
    require(data["status"] == "pass_local_controlled_preview_secret_boundary", "status")
    require(data["negative_cases_passed"] == data["negative_cases_total"] == 24, "cases")
    for key in (
        "audit_closed_schema",
        "request_secret_input_rejected",
        "runner_revalidation",
        "persistence_closed_schema",
        "memory_copy_isolation",
        "sqlite_tenant_key_pseudonymous",
        "legacy_raw_tenant_key_fail_closed",
        "audit_route_template_only",
        "raw_tenant_cross_field_denied",
        "nested_type_fail_closed",
    ):
        require(data[key] is True, key)
    for key in (
        "automatic_legacy_migration_performed",
        "request_body_recorded",
        "credentials_recorded",
        "tenant_id_raw_recorded",
        "tenant_secret_boundary_reviewed",
        "production_secrets_management_available",
        "encryption_at_rest_proven",
        "kms_hsm_available",
        "tenant_authorization_enabled",
        "production_tenant_storage_isolated",
        "security_review_completed",
        "privacy_legal_review_completed",
        "customer_validated",
        "production_ready",
        "product_launched",
    ):
        require(data[key] is False, key)
    require(data["blockers_closed"] == 0 and data["secret_echo_count"] == 0, "zero boundary")
    for path in SOURCE_PATHS:
        actual = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        require(data["source_sha256"][path] == actual, "source hash " + path)
    print(
        "SAEE_TENANT_SECRET_BOUNDARY_PROFILE_SMOKE: PASS "
        "negative_cases=24/24 secret_echo_count=0 "
        "tenant_secret_boundary_reviewed=false production_ready=false blockers_closed=0"
    )


if __name__ == "__main__":
    main()
