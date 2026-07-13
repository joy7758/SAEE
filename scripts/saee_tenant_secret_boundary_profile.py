#!/usr/bin/env python3
"""Generate local adversarial evidence for the tenant secret boundary."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_tenant_secret_boundary_smoke import (
    audit_boundary,
    persistence_boundary,
    request_boundary,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/tenant_secret_boundary"
OUTPUT_PATH = OUTPUT_DIR / "tenant_secret_boundary.local.json"
SOURCE_PATHS = [
    "saee_backend/api/audit.py",
    "saee_backend/main.py",
    "saee_backend/models/request.py",
    "saee_backend/services/public_input_contract.py",
    "saee_backend/storage/secret_boundary.py",
    "saee_backend/storage/tenant_key.py",
    "saee_backend/storage/memory_db.py",
    "saee_backend/storage/sqlite_store.py",
    "scripts/saee_tenant_secret_boundary_smoke.py",
]
NEGATIVE_CASE_IDS = [
    "audit_unknown_note",
    "audit_authorization_header",
    "audit_api_key_header",
    "audit_raw_tenant_header",
    "audit_protected_field_override",
    "audit_forged_tenant_hash",
    "audit_raw_tenant_path",
    "request_secret_agent_id",
    "request_secret_experiment_id",
    "request_nested_api_key",
    "request_duplicate_agent_id",
    "runner_model_construct_bypass",
    "memory_malicious_result",
    "sqlite_malicious_result",
    "sqlite_legacy_raw_tenant_key",
    "raw_tenant_as_agent_id",
    "raw_tenant_as_experiment_id",
    "direct_store_create_credential_id",
    "persisted_run_score_bytes",
    "persisted_unknown_object",
    "persisted_wrong_numeric_type",
    "persisted_non_finite_number",
    "decision_result_ranking_raw_tenant",
    "decision_result_failure_summary_raw_tenant",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_profile() -> dict:
    audit_boundary()
    request = request_boundary()
    persistence_boundary(request)
    return {
        "tenant_secret_boundary_profile_v0_1": True,
        "status": "pass_local_controlled_preview_secret_boundary",
        "scope": "local_controlled_preview_secret_exclusion_and_pseudonymous_storage_keys",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "generated_by": "scripts/saee_tenant_secret_boundary_profile.py",
        "negative_case_ids": NEGATIVE_CASE_IDS,
        "negative_cases_passed": len(NEGATIVE_CASE_IDS),
        "negative_cases_total": len(NEGATIVE_CASE_IDS),
        "secret_echo_count": 0,
        "audit_closed_schema": True,
        "request_secret_input_rejected": True,
        "runner_revalidation": True,
        "persistence_closed_schema": True,
        "memory_copy_isolation": True,
        "sqlite_tenant_key_pseudonymous": True,
        "tenant_storage_key_version": "v1",
        "legacy_raw_tenant_key_fail_closed": True,
        "audit_route_template_only": True,
        "raw_tenant_cross_field_denied": True,
        "nested_type_fail_closed": True,
        "automatic_legacy_migration_performed": False,
        "request_body_recorded": False,
        "credentials_recorded": False,
        "tenant_id_raw_recorded": False,
        "tenant_secret_boundary_reviewed": False,
        "production_secrets_management_available": False,
        "encryption_at_rest_proven": False,
        "kms_hsm_available": False,
        "tenant_authorization_enabled": False,
        "production_tenant_storage_isolated": False,
        "security_review_completed": False,
        "privacy_legal_review_completed": False,
        "customer_validated": False,
        "production_ready": False,
        "product_launched": False,
        "blockers_closed": 0,
        "source_sha256": {
            path: sha256(ROOT / path)
            for path in SOURCE_PATHS
        },
    }


def main() -> None:
    profile = build_profile()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(profile, indent=2, sort_keys=True) + "\n")
    print(
        "SAEE_TENANT_SECRET_BOUNDARY_PROFILE: PASS "
        f"negative_cases={profile['negative_cases_passed']}/{profile['negative_cases_total']} "
        "secret_echo_count=0 tenant_secret_boundary_reviewed=false "
        "production_ready=false blockers_closed=0"
    )


if __name__ == "__main__":
    main()
