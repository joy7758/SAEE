#!/usr/bin/env python3
"""Smoke check for SAEE commercial boundary hardening v0.1."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import DEFAULT_LOCAL_ORIGINS, load_settings


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_COMMERCIAL_BOUNDARY_SMOKE: FAIL: {message}")


def main() -> None:
    default = load_settings({})
    require(default.environment == "local", "default environment must be local")
    require(default.allowed_origins == DEFAULT_LOCAL_ORIGINS, "local origins must remain default")
    require(default.require_api_key is False, "local demo must not require API key by default")
    require(default.api_key_configured is False, "default API key must be absent")
    require(default.ready is True, "default local readiness must be true")

    protected = load_settings(
        {
            "SAEE_ENV": "preview",
            "SAEE_ALLOWED_ORIGINS": "https://preview.example.com, http://127.0.0.1:8765",
            "SAEE_REQUIRE_API_KEY": "true",
            "SAEE_API_KEY": "local-test-key",
            "SAEE_REQUIRE_TENANT_ID": "true",
            "SAEE_ALLOWED_TENANT_IDS": "preview-tenant",
            "SAEE_SYNTHETIC_DATA_ONLY": "true",
        }
    )
    require(protected.environment == "preview", "preview environment must be parsed")
    require(protected.require_api_key is True, "API key guard must be configurable")
    require(protected.api_key_configured is True, "configured API key must be detected")
    require(protected.require_tenant_id is True, "tenant boundary must be configurable")
    require(protected.allowed_tenant_ids == ("preview-tenant",), "tenant allowlist must be parsed")
    require(protected.ready is True, "protected preview must be ready when key exists")
    require(protected.max_agents == 100, "default max_agents must be preserved")
    require(protected.max_repeat_runs == 10_000, "default max_repeat_runs must be preserved")
    require(protected.max_time_horizon == 100_000, "default max_time_horizon must be preserved")
    require(protected.max_payload_bytes == 1_048_576, "default max_payload_bytes must be preserved")
    require(
        protected.allowed_origins == ("https://preview.example.com", "http://127.0.0.1:8765"),
        "allowed origins must be parsed from CSV",
    )

    missing_key = load_settings({"SAEE_REQUIRE_API_KEY": "true"})
    require(missing_key.ready is False, "required API key without secret must not be ready")
    missing_tenant_allowlist = load_settings({"SAEE_REQUIRE_TENANT_ID": "true"})
    require(
        missing_tenant_allowlist.ready is False,
        "required tenant boundary without allowlist must not be ready",
    )

    payload = protected.readiness_payload()
    require(payload.get("tenant_boundary_available") is True, "tenant boundary must be reported")
    require(payload.get("tenant_id_required") is True, "tenant requirement must be reported")
    require(payload.get("tenant_allowlist_configured") is True, "tenant allowlist must be reported")
    require(payload.get("tenant_storage_isolated") is False, "tenant storage isolation must not be claimed")
    require(payload.get("tenant_billing_isolated") is False, "tenant billing isolation must not be claimed")
    require(
        payload.get("multi_tenant_production_ready") is False,
        "multi-tenant production readiness must not be claimed",
    )
    require(payload.get("auth_boundary_available") is True, "auth boundary must be reported")
    require(payload.get("auth_mode") == "api_key_preview", "auth mode must be api_key_preview")
    require(payload.get("preview_auth_available") is True, "preview auth must be reported")
    require(payload.get("production_identity_provider_available") is False, "production IdP must not be claimed")
    require(payload.get("oauth_oidc_available") is False, "OAuth/OIDC must not be claimed")
    require(payload.get("sso_available") is False, "SSO must not be claimed")
    require(payload.get("rbac_available") is False, "RBAC must not be claimed")
    require(payload.get("production_auth_ready") is False, "production auth must not be claimed")
    require(payload.get("local_operations_telemetry_available") is True, "local telemetry must be reported")
    require(
        payload.get("operations_telemetry_external_export_available") is False,
        "telemetry external export must not be claimed",
    )
    require(payload.get("local_alert_policy_available") is True, "local alert policy must be reported")
    require(
        payload.get("external_alert_delivery_available") is False,
        "external alert delivery must not be claimed",
    )
    require(payload.get("operations_readiness_available") is True, "operations readiness must be reported")
    require(payload.get("operations_readiness_status") == "hold", "operations readiness must hold")
    require(payload.get("production_monitoring_available") is False, "production monitoring must not be claimed")
    require(payload.get("alerting_available") is False, "alerting must not be claimed")
    require(
        payload.get("incident_response_runbook_available") is True,
        "incident response runbook must be reported",
    )
    require(payload.get("support_readiness_v0_1") is True, "support readiness must be reported")
    require(payload.get("support_runbook_available") is True, "support runbook must be reported")
    require(payload.get("support_contact_configured") is False, "support contact must not be claimed")
    require(payload.get("customer_support_available") is False, "customer support must not be claimed")
    require(payload.get("production_support_available") is False, "production support must not be claimed")
    require(payload.get("on_call_rotation_available") is False, "on-call rotation must not be claimed")
    require(payload.get("sla_available") is False, "SLA must not be claimed")
    require(payload.get("support_process_available") is False, "support process must not be claimed")
    require(payload.get("production_operations_ready") is False, "production operations must not be claimed")
    expected_false_flags = [
        "production_ready",
        "customer_validated",
        "public_sdk_released",
        "product_launched",
        "private_core_connected",
        "private_core_exposed",
    ]
    for flag in expected_false_flags:
        require(payload.get(flag) is False, f"{flag} must remain false")

    required_files = [
        "saee_backend/config.py",
        "saee_backend/api/security.py",
        "docs/strategy/SAEE_COMMERCIAL_BOUNDARY_HARDENING_GATE.md",
        "phase_b_product/commercial_readiness/COMMERCIAL_BOUNDARY_V0_1.md",
    ]
    for relpath in required_files:
        require((ROOT / relpath).is_file(), f"missing {relpath}")

    main_source = (ROOT / "saee_backend/main.py").read_text(encoding="utf-8")
    security_source = (ROOT / "saee_backend/api/security.py").read_text(encoding="utf-8")
    boundary_doc = (
        ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_BOUNDARY_V0_1.md"
    ).read_text(encoding="utf-8")
    require('@app.get(' in main_source and '"/ready"' in main_source, "main.py must expose /ready")
    require(
        'require_rbac_route("GET /ready")' in main_source,
        "main.py /ready route must keep RBAC route guard",
    )
    require("SETTINGS.allowed_origins" in main_source, "main.py must use configured origins")
    require("X-SAEE-API-Key" in security_source, "security guard must use X-SAEE-API-Key")
    require("X-SAEE-Tenant-ID" in security_source, "security guard must use X-SAEE-Tenant-ID")
    require("production_ready: false" in boundary_doc, "boundary doc must preserve production false")
    require("auth_readiness_v0_1: true" in boundary_doc, "boundary doc must include auth readiness")
    require("operations_telemetry_v0_1: true" in boundary_doc, "boundary doc must include telemetry")
    require("operations_readiness_v0_1: true" in boundary_doc, "boundary doc must include operations readiness")
    require("production_auth_ready: false" in boundary_doc, "boundary doc must preserve auth false")
    require(
        "production_operations_ready: false" in boundary_doc,
        "boundary doc must preserve operations false",
    )
    require("private_core_exposed: false" in boundary_doc, "boundary doc must preserve private core false")

    print(
        "SAEE_COMMERCIAL_BOUNDARY_SMOKE: PASS "
        "configurable_cors=true "
        "optional_api_key_guard=true "
        "auth_readiness=true "
        "operations_telemetry=true "
        "operations_readiness=true "
        "tenant_request_boundary=true "
        "readiness_endpoint=true "
        "production_ready=false "
        "private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
