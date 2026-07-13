#!/usr/bin/env python3
"""Smoke check for SAEE Auth Readiness v0.1."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.auth_readiness import evaluate_auth_readiness


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_AUTH_READINESS_SMOKE: FAIL: {message}")


def finding(report: dict[str, object], check_id: str) -> dict[str, object]:
    for item in report["findings"]:
        if item["check_id"] == check_id:
            return item
    raise SystemExit(f"SAEE_AUTH_READINESS_SMOKE: FAIL: missing finding {check_id}")


def main() -> None:
    local = evaluate_auth_readiness(load_settings({}))
    require(local["auth_readiness_type"] == "public_shell_auth_readiness", "wrong readiness type")
    require(local["public_use_required"] is False, "local environment must not require public auth")
    require(local["status"] == "hold", "local demo auth readiness must hold, not pass")
    require(local["auth_mode"] == "local_none", "default auth mode must be local_none")
    require(local["preview_auth_available"] is False, "default preview auth must be false")
    require(local["production_auth_ready"] is False, "production auth must remain false")
    require(local["production_identity_provider_available"] is False, "IdP must remain false")
    require(local["oauth_oidc_available"] is False, "OAuth/OIDC must remain false")
    require(local["sso_available"] is False, "SSO must remain false")
    require(local["rbac_available"] is False, "RBAC must remain false")
    require(local["production_ready"] is False, "production ready must remain false")
    require(local["private_core_exposed"] is False, "private core exposed must remain false")
    require(local["external_calls_made"] is False, "auth readiness must not call external services")

    unsafe_preview = evaluate_auth_readiness(load_settings({"SAEE_ENV": "preview"}))
    require(unsafe_preview["public_use_required"] is True, "preview must require auth")
    require(unsafe_preview["status"] == "hold", "preview without API key must hold")
    require(
        finding(unsafe_preview, "preview_api_key_auth")["passed"] is False,
        "preview API key auth finding must fail",
    )

    safe_preview = evaluate_auth_readiness(
        load_settings(
            {
                "SAEE_ENV": "preview",
                "SAEE_REQUIRE_API_KEY": "true",
                "SAEE_API_KEY": "local-preview-key",
            }
        )
    )
    require(safe_preview["status"] == "pass", "preview with API key must pass auth readiness")
    require(safe_preview["auth_mode"] == "api_key_preview", "preview auth mode must be api_key_preview")
    require(safe_preview["preview_auth_available"] is True, "preview auth must be available")
    require(safe_preview["production_auth_ready"] is False, "preview auth must not claim production auth")
    require(safe_preview["production_ready"] is False, "preview auth must not claim production readiness")
    require(safe_preview["customer_validated"] is False, "preview auth must not claim customer validation")
    require(safe_preview["product_launched"] is False, "preview auth must not claim launch")
    require(safe_preview["private_core_exposed"] is False, "preview auth must not expose private core")

    readiness_payload = load_settings(
        {
            "SAEE_REQUIRE_API_KEY": "true",
            "SAEE_API_KEY": "local-preview-key",
        }
    ).readiness_payload()
    require(readiness_payload["auth_boundary_available"] is True, "ready payload must report auth boundary")
    require(readiness_payload["auth_mode"] == "api_key_preview", "ready payload must report auth mode")
    require(readiness_payload["preview_auth_available"] is True, "ready payload must report preview auth")
    require(readiness_payload["production_auth_ready"] is False, "ready payload must keep production auth false")

    doc = (ROOT / "phase_b_product/commercial_readiness/AUTH_READINESS_V0_1.md").read_text(
        encoding="utf-8"
    )
    gate = (ROOT / "docs/strategy/SAEE_AUTH_READINESS_RECOMMENDATION_GATE.md").read_text(
        encoding="utf-8"
    )
    require("auth_readiness_v0_1: true" in doc, "auth readiness doc missing state")
    require("preview_auth_available: true" in doc, "auth readiness doc must mention preview auth")
    require("production_auth_ready: false" in doc, "auth readiness doc must preserve production false")
    require("oauth_oidc_available: false" in doc, "auth readiness doc must preserve OIDC false")
    require("rbac_available: false" in doc, "auth readiness doc must preserve RBAC false")
    require("answer: conditional" in gate, "auth readiness gate must remain conditional")
    require("recommend_public_launch_now: false" in gate, "auth readiness gate must not recommend launch")

    print(
        "SAEE_AUTH_READINESS_SMOKE: PASS "
        "local_hold=true "
        "preview_api_key_pass=true "
        "production_auth_ready=false "
        "oauth_oidc_available=false "
        "rbac_available=false "
        "private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
