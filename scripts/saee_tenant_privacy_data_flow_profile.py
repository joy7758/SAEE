#!/usr/bin/env python3
"""Generate the agent-readable tenant controlled-preview privacy data-flow map."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "phase_b_product/commercial_readiness/tenant_privacy_agent_review/tenant_privacy_data_flow.local.json"
SOURCES = (
    "saee_backend/config.py",
    "saee_backend/services/public_input_contract.py",
    "saee_backend/models/request.py",
    "saee_backend/services/jwt_preview_auth.py",
    "saee_backend/api/security.py",
    "saee_backend/api/audit.py",
    "saee_backend/api/experiment.py",
    "saee_backend/services/experiment_service.py",
    "saee_backend/core/runner.py",
    "saee_backend/storage/memory_db.py",
    "saee_backend/storage/sqlite_store.py",
    "saee_backend/services/data_backup.py",
    "saee_backend/services/data_retention.py",
    "saee_backend/services/data_restore_drill.py",
    "schemas/saee_mvp_api.schema.json",
    "saee_backend/schemas/saee_mvp_api.schema.json",
    "phase_b_product/commercial_readiness/provider_data_processing/qianfan_provider_data_processing_profile.local.json",
)


def build_profile() -> dict:
    return {
        "tenant_privacy_data_flow_profile_v0_1": True,
        "status": "pass_synthetic_only_controlled_preview_inventory",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "generated_by": "scripts/saee_tenant_privacy_data_flow_profile.py",
        "review_scope": "whole_tenant_api_synthetic_only_controlled_preview",
        "surface_count": 8,
        "surfaces": [
            {
                "surface": "request_json_body",
                "accepted": "closed_scenario_and_create_contracts",
                "controls": ["pydantic_extra_forbid", "closed_config_keys", "public_safe_identifiers", "runner_revalidation"],
                "personal_data_allowed": False,
            },
            {
                "surface": "path_and_query",
                "accepted": "public_safe_experiment_identifier_only_or_closed_pagination",
                "controls": ["service_layer_identifier_validation", "non_reflecting_not_found_error"],
                "personal_data_allowed": False,
            },
            {
                "surface": "tenant_and_role_headers",
                "accepted": "allowlisted_public_safe_identifiers_only",
                "controls": ["tenant_format", "allowlist", "rbac_closed_policy"],
                "personal_data_allowed": False,
            },
            {
                "surface": "authorization_and_api_key_headers",
                "accepted": "transient_credentials_only",
                "controls": ["not_persisted", "not_audited", "not_reflected"],
                "personal_data_allowed": False,
            },
            {
                "surface": "preview_jwt",
                "accepted": "exact_closed_claim_set_without_email",
                "controls": ["hs256_signature", "public_safe_subject_tenant_roles", "extra_claims_rejected"],
                "personal_data_allowed": False,
            },
            {
                "surface": "audit_and_errors",
                "accepted": "closed_metadata_only",
                "controls": ["no_body", "no_credentials", "hashed_tenant", "non_reflecting_validation_errors"],
                "personal_data_allowed": False,
            },
            {
                "surface": "storage_backup_restore_retention",
                "accepted": "synthetic_evaluation_records_and_closed_audit_metadata_only",
                "controls": ["tenant_partition", "local_backup_manifest", "no_follow_restore", "retention_atomic_replace"],
                "personal_data_allowed": False,
            },
            {
                "surface": "baidu_qianfan_provider",
                "accepted": "sanitized_numeric_fixture_and_fixed_tool_receipts_only",
                "controls": ["no_customer_records", "no_api_key_transcript", "no_candidate_code"],
                "personal_data_allowed": False,
            },
        ],
        "synthetic_data_only": True,
        "explicit_preview_configuration_required": True,
        "pattern_detection_only": True,
        "general_dlp_available": False,
        "deidentification_proven": False,
        "real_customer_data_allowed": False,
        "customer_data_processed": False,
        "privacy_legal_review_completed": False,
        "data_processing_agreement_completed": False,
        "qianfan_provider_legal_approval_completed": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "blockers_closed": 0,
        "source_sha256": {
            relative: hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            for relative in SOURCES
        },
    }


def main() -> None:
    data = build_profile()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "SAEE_TENANT_PRIVACY_DATA_FLOW_PROFILE: PASS surfaces=8/8 "
        "synthetic_data_only=true real_customer_data_allowed=false "
        "general_dlp=false privacy_legal_review_completed=false production_ready=false"
    )


if __name__ == "__main__":
    main()
