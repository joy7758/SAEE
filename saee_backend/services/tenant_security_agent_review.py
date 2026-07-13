"""Validate local independent-agent security review evidence for tenant storage."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


SECURITY_SOURCE_SET = frozenset(
    {
        "saee_backend/api/security.py",
        "saee_backend/api/audit.py",
        "saee_backend/services/jwt_preview_auth.py",
        "saee_backend/services/rbac_policy.py",
        "saee_backend/services/authorization_context.py",
        "saee_backend/services/public_input_contract.py",
        "saee_backend/services/data_backup.py",
        "saee_backend/services/data_retention.py",
        "saee_backend/services/data_restore_drill.py",
        "saee_backend/storage/factory.py",
        "saee_backend/storage/memory_db.py",
        "saee_backend/storage/sqlite_store.py",
        "saee_backend/storage/tenant_key.py",
        "saee_backend/storage/secret_boundary.py",
        "scripts/saee_bound_tenant_authorization_smoke.py",
        "scripts/saee_tenant_secret_boundary_smoke.py",
        "scripts/saee_request_audit_smoke.py",
        "scripts/saee_controlled_preview_tenant_storage_smoke.py",
        "scripts/saee_data_backup_smoke.py",
        "scripts/saee_data_retention_smoke.py",
        "scripts/saee_data_restore_drill_smoke.py",
    }
)
FALSE_KEYS = (
    "formal_production_security_review_completed",
    "production_restore_tested",
    "production_restore_policy_available",
    "production_tenant_storage_isolated",
    "production_ready",
    "customer_validated",
    "product_launched",
)


def _read(path: Path) -> tuple[bytes, dict[str, Any]]:
    raw = path.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("security review input must be an object")
    return raw, data


def evaluate_tenant_security_agent_review(
    root: Path,
    *,
    profile_path: Path | None = None,
    validation_path: Path | None = None,
) -> dict[str, Any]:
    profile_path = profile_path or root / "phase_b_product/commercial_readiness/tenant_security_agent_review/tenant_security_agent_review.local.json"
    validation_path = validation_path or root / "agent_recommendation/tenant_security_agent_review/run_001/independent_agent_validation.local.json"
    reasons: list[str] = []
    try:
        profile_raw, profile = _read(profile_path)
        validation_raw, validation = _read(validation_path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        profile_raw, validation_raw, profile, validation = b"", b"", {}, {}
        reasons.append("input_invalid_or_missing")

    manifest = profile.get("source_sha256")
    manifest_valid = isinstance(manifest, dict) and frozenset(manifest) == SECURITY_SOURCE_SET
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
        profile.get("tenant_security_agent_review_profile_v0_1") is True,
        profile.get("status") == "pass_local_controlled_preview_security_review",
        profile.get("review_actor_type") == "independent_agent",
        profile.get("review_scope") == "local_controlled_preview_tenant_storage",
        profile.get("security_smokes_passed") == profile.get("security_smokes_total") == 7,
        profile.get("negative_cases_passed") == profile.get("negative_cases_total") == 8,
        manifest_valid,
        validation.get("agent_validation_type") == "independent_agent_security_review",
        validation.get("independent_agent_profile") == "recommendation_agent_validation",
        validation.get("recommendation_scope") == "local_controlled_preview_tenant_security_review",
        validation.get("verdict") == "recommend",
        validation.get("round_2", {}).get("verdict") == "recommend",
        validation.get("round_2", {}).get("blocker_count") == 0,
        validation.get("blockers") == [],
        all(profile.get(key) is False for key in FALSE_KEYS),
        all(validation.get(key) is not True for key in FALSE_KEYS),
    )
    if not all(checks):
        reasons.append("security_review_evidence_mismatch")
    accepted = not reasons
    return {
        "tenant_security_agent_review_evidence_v0_1": True,
        "status": "pass_agent_security_review" if accepted else "hold_agent_security_review",
        "review_actor_type": "independent_agent",
        "review_scope": "local_controlled_preview_tenant_storage",
        "security_review_completed": accepted,
        "security_review_completion_scope": "local_controlled_preview_independent_agent",
        "human_validation_used": False,
        "agent_validation_primary": True,
        "formal_production_security_review_completed": False,
        "privacy_legal_review_completed": False,
        "production_restore_tested": False,
        "production_restore_policy_available": False,
        "production_tenant_storage_isolated": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "blockers_closed": 0,
        "profile_sha256": hashlib.sha256(profile_raw).hexdigest(),
        "validation_sha256": hashlib.sha256(validation_raw).hexdigest(),
        "failure_reasons": sorted(set(reasons)),
    }
