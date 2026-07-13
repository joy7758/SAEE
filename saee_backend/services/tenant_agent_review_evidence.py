"""Verify independent-agent evidence for two local tenant review decisions.

This adapter accepts only the canonical bound-authorization and secret-boundary
profiles plus their independent-agent verdicts. It may advance two local review
fields atomically; it never completes formal security/privacy review or closes a
commercial blocker.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


AUTH_SOURCE_SET = frozenset(
    {
        "saee_backend/config.py",
        "saee_backend/api/security.py",
        "saee_backend/main.py",
        "saee_backend/services/authorization_context.py",
        "saee_backend/services/experiment_service.py",
        "saee_backend/storage/factory.py",
        "saee_backend/storage/memory_db.py",
        "saee_backend/storage/sqlite_store.py",
        "scripts/saee_bound_tenant_authorization_smoke.py",
    }
)
SECRET_SOURCE_SET = frozenset(
    {
        "saee_backend/api/audit.py",
        "saee_backend/main.py",
        "saee_backend/models/request.py",
        "saee_backend/services/public_input_contract.py",
        "saee_backend/storage/secret_boundary.py",
        "saee_backend/storage/tenant_key.py",
        "saee_backend/storage/memory_db.py",
        "saee_backend/storage/sqlite_store.py",
        "scripts/saee_tenant_secret_boundary_smoke.py",
    }
)
FALSE_PRODUCTION_KEYS = frozenset(
    {
        "security_review_completed",
        "privacy_legal_review_completed",
        "production_ready",
        "customer_validated",
        "product_launched",
        "tenant_authorization_enabled",
        "production_tenant_storage_isolated",
        "production_identity_provider_available",
        "oauth_oidc_available",
        "jwks_fetched",
        "tokens_validated_in_production",
    }
)


@dataclass(frozen=True)
class TenantAgentReviewPaths:
    auth_profile: Path
    auth_validation: Path
    secret_profile: Path
    secret_validation: Path


def canonical_paths(root: Path) -> TenantAgentReviewPaths:
    return TenantAgentReviewPaths(
        auth_profile=root
        / "phase_b_product/commercial_readiness/tenant_authorization/tenant_authorization.local.json",
        auth_validation=root
        / "agent_recommendation/bound_tenant_authorization/run_001/independent_agent_validation.local.json",
        secret_profile=root
        / "phase_b_product/commercial_readiness/tenant_secret_boundary/tenant_secret_boundary.local.json",
        secret_validation=root
        / "agent_recommendation/tenant_secret_boundary/run_001/independent_agent_validation.local.json",
    )


def _read_snapshot(path: Path) -> tuple[bytes, dict[str, Any]]:
    raw = path.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("agent review input must be a JSON object")
    return raw, data


def _false_invariants(data: dict[str, Any]) -> bool:
    return not any(data.get(key) is True for key in FALSE_PRODUCTION_KEYS)


def _source_manifest_valid(
    root: Path,
    profile: dict[str, Any],
    expected_sources: frozenset[str],
) -> bool:
    manifest = profile.get("source_sha256")
    if not isinstance(manifest, dict) or frozenset(manifest) != expected_sources:
        return False
    for relative, expected in manifest.items():
        if not isinstance(expected, str) or len(expected) != 64:
            return False
        try:
            actual = hashlib.sha256((root / relative).read_bytes()).hexdigest()
        except OSError:
            return False
        if actual != expected:
            return False
    return True


def evaluate_tenant_agent_review_evidence(
    root: Path,
    paths: TenantAgentReviewPaths | None = None,
) -> dict[str, Any]:
    paths = paths or canonical_paths(root)
    reasons: list[str] = []
    snapshots: dict[str, bytes] = {}
    parsed: dict[str, dict[str, Any]] = {}
    for name, path in (
        ("auth_profile", paths.auth_profile),
        ("auth_validation", paths.auth_validation),
        ("secret_profile", paths.secret_profile),
        ("secret_validation", paths.secret_validation),
    ):
        try:
            raw, data = _read_snapshot(path)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
            reasons.append(name + "_invalid_or_missing")
            continue
        snapshots[name] = raw
        parsed[name] = data

    if len(parsed) == 4:
        auth_profile = parsed["auth_profile"]
        auth_validation = parsed["auth_validation"]
        secret_profile = parsed["secret_profile"]
        secret_validation = parsed["secret_validation"]

        auth_checks = (
            auth_profile.get("bound_tenant_authorization_profile_v0_1") is True,
            auth_profile.get("status")
            == "pass_local_controlled_preview_bound_authorization",
            auth_profile.get("negative_cases_passed")
            == auth_profile.get("negative_cases_total")
            == 14,
            auth_validation.get("agent_validation_type")
            == "independent_agent_recommendation_gate",
            auth_validation.get("independent_agent_profile")
            == "recommendation_agent_validation",
            auth_validation.get("recommendation_scope")
            == "local_controlled_preview_bound_tenant_authorization_chain",
            auth_validation.get("verdict") == "recommend",
            auth_validation.get("round_3", {}).get("verdict") == "recommend",
            auth_validation.get("round_3", {}).get("blocker_count") == 0,
            auth_validation.get("blockers") == [],
            auth_validation.get("negative_cases_passed")
            == auth_validation.get("negative_cases_total")
            == 14,
            _source_manifest_valid(root, auth_profile, AUTH_SOURCE_SET),
            _false_invariants(auth_profile),
            _false_invariants(auth_validation),
        )
        secret_checks = (
            secret_profile.get("tenant_secret_boundary_profile_v0_1") is True,
            secret_profile.get("status")
            == "pass_local_controlled_preview_secret_boundary",
            secret_profile.get("negative_cases_passed")
            == secret_profile.get("negative_cases_total")
            == 24,
            secret_validation.get("agent_validation_type")
            == "independent_agent_recommendation_gate",
            secret_validation.get("independent_agent_profile")
            == "recommendation_agent_validation",
            secret_validation.get("recommendation_scope")
            == "local_controlled_preview_secret_exclusion_and_pseudonymous_storage_keys",
            secret_validation.get("verdict") == "recommend",
            secret_validation.get("round_4", {}).get("verdict") == "recommend",
            secret_validation.get("round_4", {}).get("blocker_count") == 0,
            secret_validation.get("blockers") == [],
            secret_validation.get("negative_cases_passed")
            == secret_validation.get("negative_cases_total")
            == 24,
            _source_manifest_valid(root, secret_profile, SECRET_SOURCE_SET),
            _false_invariants(secret_profile),
            _false_invariants(secret_validation),
        )
        if not all(auth_checks):
            reasons.append("bound_authorization_evidence_mismatch")
        if not all(secret_checks):
            reasons.append("secret_boundary_evidence_mismatch")

    accepted = not reasons and len(parsed) == 4
    input_sha256 = {
        name: hashlib.sha256(raw).hexdigest() for name, raw in snapshots.items()
    }
    manifest_digest = hashlib.sha256(
        json.dumps(input_sha256, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()
    return {
        "tenant_agent_review_evidence_v0_1": True,
        "status": "pass_agent_review_evidence" if accepted else "hold_agent_review_evidence",
        "review_actor_type": "independent_agent",
        "review_scope": "local_controlled_preview",
        "tenant_authorization_policy_reviewed": accepted,
        "tenant_secret_boundary_reviewed": accepted,
        "tenant_authorization_policy_review_scope": "local_controlled_preview_independent_agent",
        "tenant_secret_boundary_review_scope": "local_controlled_preview_independent_agent",
        "human_validation_used": False,
        "agent_validation_primary": True,
        "production_policy_approved": False,
        "security_review_completed": False,
        "privacy_legal_review_completed": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "tenant_authorization_enabled": False,
        "production_tenant_storage_isolated": False,
        "production_identity_provider_available": False,
        "oauth_oidc_available": False,
        "jwks_fetched": False,
        "tokens_validated_in_production": False,
        "blockers_closed": 0,
        "input_sha256": input_sha256,
        "input_manifest_sha256": manifest_digest,
        "failure_reasons": sorted(set(reasons)),
    }
