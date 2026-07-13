#!/usr/bin/env python3
"""Smoke check for optional JWT preview headers in the landing demo."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "phase_b_product/landing/app.js"
README = ROOT / "phase_b_product/landing/README.md"
DOC = ROOT / "phase_b_product/commercial_readiness/JWT_PREVIEW_LANDING_DEMO_AUTH_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_JWT_PREVIEW_LANDING_DEMO_AUTH_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_LANDING_JWT_PREVIEW_AUTH_SMOKE: FAIL: " + message)


def read(path: Path) -> str:
    require(path.is_file(), f"missing {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def main() -> None:
    app = read(APP)
    readme = read(README)
    doc = read(DOC)
    gate = read(GATE)

    app_required = [
        "readShortSessionPreviewValue",
        "authorizationValue",
        "requestHeaders",
        "__SAEE_LOCAL_DEMO_CONFIG__",
        "SAEE_PREVIEW_AUTHORIZATION",
        "SAEE_PREVIEW_TOKEN",
        "previewRole",
        "previewTenantId",
        "headers.Authorization",
        'headers["X-SAEE-Role"]',
        'headers["X-SAEE-Tenant-ID"]',
        "headers: requestHeaders()",
        "http://127.0.0.1:8000/experiment/run",
    ]
    missing_app = [token for token in app_required if token not in app]
    require(not missing_app, "app.js missing tokens: " + ", ".join(missing_app))
    require("https://" not in app, "landing app must not call external HTTPS")
    require("localStorage" not in app, "landing app must not persist preview values in localStorage")
    require("innerHTML" not in app, "landing app must render API values without innerHTML")
    require("sessionStorage" in app, "landing app must use short browser-session token storage")

    forbidden_app = [
        "SAEE_PREVIEW_JWT_HS256_SECRET",
        "local-controlled-preview-secret",
        "preview-idp.example.invalid",
        "saee_v1_0",
        "selection_engine",
        "mutation_engine",
        "lineage_engine",
        "fitness_engine",
    ]
    found_app = [token for token in forbidden_app if token in app]
    require(not found_app, "app.js contains forbidden token: " + ", ".join(found_app))

    for token in [
        "jwt_preview_landing_demo_auth_v0_1: true",
        "landing_demo_optional_preview_auth_headers: true",
        "production_auth_ready: false",
        "tokens_validated_in_production: false",
        "private_core_exposed: false",
        "blockers_closed_by_landing_demo_auth: 0",
    ]:
        require(token in doc, "doc missing token: " + token)
    for token in [
        "answer: conditional",
        "recommend_for_controlled_preview_landing_demo_auth: true",
        "recommend_for_production_auth: false",
        "production_auth_ready: false",
    ]:
        require(token in gate, "gate missing token: " + token)
    for token in [
        "jwt_preview_landing_demo_auth_v0_1: true",
        "landing_demo_optional_preview_auth_headers: true",
        "production_deployed: false",
        "product_launched: false",
        "private_core_exported: false",
    ]:
        require(token in readme, "landing README missing token: " + token)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("jwt_preview_landing_demo_auth_v0_1", {})
    expected = {
        "status": "optional_preview_auth_headers_available",
        "jwt_preview_landing_demo_auth_v0_1": True,
        "landing_demo_optional_preview_auth_headers": True,
        "default_required": False,
        "login_flow_available": False,
        "external_identity_provider_contacted": False,
        "jwks_fetched": False,
        "tokens_validated_in_production": False,
        "jwt_preview_production_oidc": False,
        "production_auth_ready": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "blockers_closed_by_landing_demo_auth": 0,
    }
    for key, value in expected.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_LANDING_JWT_PREVIEW_AUTH_SMOKE: PASS "
        "optional_preview_auth_headers=true production_auth_ready=false blockers_closed=0"
    )


if __name__ == "__main__":
    main()
