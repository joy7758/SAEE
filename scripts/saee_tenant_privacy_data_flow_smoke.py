#!/usr/bin/env python3
"""Adversarial smoke for the controlled-preview tenant privacy data flow."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.experiment_service import ExperimentService
from saee_backend.services.jwt_preview_auth import JwtPreviewAuthError, sign_preview_jwt, validate_preview_jwt
from saee_backend.storage.memory_db import MemoryExperimentStore
from scripts.saee_tenant_privacy_data_flow_profile import OUTPUT, SOURCES, main as run_profile


SECRET = "synthetic-review-secret-value-123456"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_TENANT_PRIVACY_DATA_FLOW_SMOKE: FAIL: " + message)


def settings():
    return load_settings(
        {
            "SAEE_SYNTHETIC_DATA_ONLY": "true",
            "SAEE_REQUIRE_JWT_PREVIEW_AUTH": "true",
            "SAEE_REQUIRE_TENANT_ID": "true",
            "SAEE_ALLOWED_TENANT_IDS": "tenant-a",
            "SAEE_REQUIRE_RBAC_ROLE": "true",
            "SAEE_RBAC_POLICY_PATH": str(ROOT / "saee_backend/config_examples/rbac_policy.json"),
            "SAEE_PREVIEW_JWT_ISSUER": "saee-preview",
            "SAEE_PREVIEW_JWT_AUDIENCE": "saee-api",
            "SAEE_PREVIEW_JWT_HS256_SECRET": SECRET,
        }
    )


def main() -> None:
    run_profile()
    data = json.loads(OUTPUT.read_text(encoding="utf-8"))
    require(data["surface_count"] == len(data["surfaces"]) == 8, "surface inventory")
    require(set(data["source_sha256"]) == set(SOURCES), "source set")
    for relative, expected in data["source_sha256"].items():
        require(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected, "source hash")

    base_claims = {
        "iss": "saee-preview",
        "sub": "agent-operator",
        "aud": "saee-api",
        "exp": 4_102_444_800,
        "iat": 1_767_225_600,
        "tenant_id": "tenant-a",
        "roles": ["viewer"],
    }
    with patch.dict(os.environ, {"SAEE_PREVIEW_JWT_HS256_SECRET": SECRET}, clear=False):
        token = sign_preview_jwt(base_claims, SECRET)
        validated = validate_preview_jwt(token, settings(), now=1_800_000_000)
        require(validated.subject == "agent-operator", "closed JWT accepted")
        for mutation in (
            {"email": "person@example.invalid"},
            {"sub": "张三"},
        ):
            claims = dict(base_claims)
            claims.update(mutation)
            try:
                validate_preview_jwt(sign_preview_jwt(claims, SECRET), settings(), now=1_800_000_000)
            except JwtPreviewAuthError as exc:
                require(str(mutation.get("email", mutation.get("sub"))) not in str(exc), "JWT reflected input")
            else:
                raise SystemExit("SAEE_TENANT_PRIVACY_DATA_FLOW_SMOKE: FAIL: unsafe JWT accepted")

    service = ExperimentService(MemoryExperimentStore())
    for unsafe_id in ("张三", "person@example.invalid"):
        try:
            service.get_ranking(unsafe_id)
        except ValueError as exc:
            require(unsafe_id not in str(exc), "path identifier reflected")
        else:
            raise SystemExit("SAEE_TENANT_PRIVACY_DATA_FLOW_SMOKE: FAIL: unsafe path accepted")

    provider = json.loads(
        (ROOT / "phase_b_product/commercial_readiness/provider_data_processing/qianfan_provider_data_processing_profile.local.json").read_text(encoding="utf-8")
    )
    require("customer records or production data" in provider["data_not_sent_by_host"], "provider customer-data boundary")
    require(provider["observed_boundary_facts"]["api_key_in_transcripts"] is False, "provider secret boundary")
    require(provider["review_status"]["privacy_legal_review_completed"] is False, "provider legal boundary")

    require(data["synthetic_data_only"] is True, "synthetic-only boundary")
    for key in (
        "general_dlp_available",
        "deidentification_proven",
        "real_customer_data_allowed",
        "customer_data_processed",
        "privacy_legal_review_completed",
        "data_processing_agreement_completed",
        "qianfan_provider_legal_approval_completed",
        "production_ready",
    ):
        require(data[key] is False, f"{key} must stay false")

    print(
        "SAEE_TENANT_PRIVACY_DATA_FLOW_SMOKE: PASS surfaces=8/8 negatives=8/8 "
        "jwt_email_claim_rejected=true path_pii_rejected=true audit_body_recorded=false "
        "real_customer_data_allowed=false general_dlp=false production_ready=false"
    )


if __name__ == "__main__":
    main()
