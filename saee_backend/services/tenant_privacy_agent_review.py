"""Validate narrow independent-agent privacy-boundary evidence.

This service proves only a controlled-preview input boundary for synthetic or
sanitized data. It does not approve general DLP, legal notices, a DPA, provider
terms, customer-data processing, or production use.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


PRIVACY_SOURCE_SET = frozenset(
    {
        "saee_backend/services/public_input_contract.py",
        "saee_backend/config.py",
        "saee_backend/models/request.py",
        "saee_backend/core/runner.py",
        "saee_backend/api/experiment.py",
        "saee_backend/api/security.py",
        "saee_backend/api/audit.py",
        "saee_backend/services/experiment_service.py",
        "saee_backend/services/jwt_preview_auth.py",
        "schemas/saee_mvp_api.schema.json",
        "saee_backend/schemas/saee_mvp_api.schema.json",
        "scripts/saee_personal_data_boundary_smoke.py",
        "scripts/saee_synthetic_data_only_mode_smoke.py",
        "scripts/saee_tenant_privacy_data_flow_profile.py",
        "scripts/saee_tenant_privacy_data_flow_smoke.py",
        "phase_b_product/commercial_readiness/tenant_privacy_agent_review/tenant_privacy_data_flow.local.json",
        "scripts/saee_controlled_preview_request_smoke.py",
        "scripts/saee_tenant_secret_boundary_smoke.py",
        "scripts/saee_request_audit_smoke.py",
        "scripts/saee_data_backup_smoke.py",
        "scripts/saee_data_retention_smoke.py",
        "scripts/saee_data_restore_drill_smoke.py",
        "scripts/saee_qianfan_provider_policy_snapshot_smoke.py",
        "phase_b_product/commercial_readiness/provider_data_processing/qianfan_provider_data_processing_profile.local.json",
    }
)

FALSE_KEYS = (
    "general_dlp_available",
    "deidentification_proven",
    "real_customer_data_allowed",
    "privacy_legal_review_completed",
    "data_processing_agreement_completed",
    "qianfan_provider_legal_approval_completed",
    "qianfan_retention_terms_verified",
    "customer_data_processing_ready",
    "production_ready",
    "customer_validated",
    "product_launched",
)


def _read(path: Path) -> tuple[bytes, dict[str, Any]]:
    raw = path.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("privacy review input must be an object")
    return raw, data


def evaluate_tenant_privacy_agent_review(
    root: Path,
    *,
    profile_path: Path | None = None,
    validation_path: Path | None = None,
) -> dict[str, Any]:
    profile_path = profile_path or root / (
        "phase_b_product/commercial_readiness/tenant_privacy_agent_review/"
        "tenant_privacy_agent_review.local.json"
    )
    validation_path = validation_path or root / (
        "agent_recommendation/tenant_privacy_agent_review/run_001/"
        "independent_agent_validation.local.json"
    )
    reasons: list[str] = []
    try:
        profile_raw, profile = _read(profile_path)
        validation_raw, validation = _read(validation_path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        profile_raw, validation_raw, profile, validation = b"", b"", {}, {}
        reasons.append("input_invalid_or_missing")

    manifest = profile.get("source_sha256")
    manifest_valid = isinstance(manifest, dict) and frozenset(manifest) == PRIVACY_SOURCE_SET
    if manifest_valid:
        for relative, expected in manifest.items():
            try:
                actual = hashlib.sha256((root / relative).read_bytes()).hexdigest()
            except OSError:
                manifest_valid = False
                break
            if actual != expected:
                manifest_valid = False
                break

    checks = (
        profile.get("tenant_privacy_agent_review_profile_v0_1") is True,
        profile.get("status") == "pass_whole_tenant_api_synthetic_only_controlled_preview_privacy_boundary",
        profile.get("review_actor_type") == "independent_agent",
        profile.get("review_scope") == "whole_tenant_api_synthetic_only_controlled_preview",
        profile.get("privacy_smokes_passed") == profile.get("privacy_smokes_total") == 10,
        profile.get("negative_cases_passed") == profile.get("negative_cases_total") == 16,
        profile.get("personal_data_boundary_cases_passed") == 29,
        profile.get("personal_data_boundary_cases_total") == 29,
        manifest_valid,
        validation.get("agent_validation_type") == "independent_agent_privacy_boundary_review",
        validation.get("independent_agent_profile") == "recommendation_agent_validation",
        validation.get("recommendation_scope") == "whole_tenant_api_synthetic_only_controlled_preview_privacy_boundary",
        validation.get("verdict") == "recommend",
        validation.get("round_2", {}).get("verdict") == "conditional",
        validation.get("round_2", {}).get("blocker_count") == 1,
        validation.get("round_3", {}).get("verdict") == "recommend",
        validation.get("round_3", {}).get("blocker_count") == 0,
        validation.get("round_4", {}).get("verdict") == "recommend",
        validation.get("round_4", {}).get("blocker_count") == 0,
        validation.get("blockers") == [],
        all(profile.get(key) is False for key in FALSE_KEYS),
        all(validation.get(key) is False for key in FALSE_KEYS),
    )
    if not all(checks):
        reasons.append("privacy_review_evidence_mismatch")
    accepted = not reasons
    return {
        "tenant_privacy_agent_review_evidence_v0_1": True,
        "status": "pass_agent_privacy_boundary_review" if accepted else "hold_agent_privacy_boundary_review",
        "review_actor_type": "independent_agent",
        "review_scope": "whole_tenant_api_synthetic_only_controlled_preview",
        "agent_privacy_boundary_review_completed": accepted,
        "agent_privacy_boundary_review_scope": "whole_tenant_api_synthetic_only_controlled_preview_independent_agent",
        "personal_data_detection_scope": "high_confidence_patterns_and_closed_keys",
        "general_dlp_available": False,
        "deidentification_proven": False,
        "real_customer_data_allowed": False,
        "human_validation_used": False,
        "agent_validation_primary": True,
        "privacy_legal_review_completed": False,
        "data_processing_agreement_completed": False,
        "qianfan_provider_legal_approval_completed": False,
        "qianfan_retention_terms_verified": False,
        "customer_data_processing_ready": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "blockers_closed": 0,
        "profile_sha256": hashlib.sha256(profile_raw).hexdigest(),
        "validation_sha256": hashlib.sha256(validation_raw).hexdigest(),
        "failure_reasons": sorted(set(reasons)),
    }
