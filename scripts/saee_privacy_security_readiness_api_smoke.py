#!/usr/bin/env python3
"""Smoke check for SAEE Privacy/Security Readiness API v0.1."""

from __future__ import annotations

import importlib.util
import py_compile
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.privacy_security_readiness import (
    evaluate_privacy_security_readiness,
)


ROUTE_PATH = ROOT / "saee_backend/api/readiness.py"
MAIN_PATH = ROOT / "saee_backend/main.py"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/PRIVACY_SECURITY_READINESS_API_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PRIVACY_SECURITY_READINESS_API_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_PRIVACY_SECURITY_READINESS_API_SMOKE: FAIL: {message}")


def assert_false(payload: dict[str, object], keys: list[str]) -> None:
    for key in keys:
        require(payload.get(key) is False, f"{key} must be false")


def main() -> None:
    for path in [ROUTE_PATH, MAIN_PATH, DOC_PATH, GATE_PATH]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")
    py_compile.compile(str(ROUTE_PATH), doraise=True)
    py_compile.compile(str(MAIN_PATH), doraise=True)

    route = ROUTE_PATH.read_text(encoding="utf-8")
    main = MAIN_PATH.read_text(encoding="utf-8")
    doc = DOC_PATH.read_text(encoding="utf-8")
    gate = GATE_PATH.read_text(encoding="utf-8")
    combined = "\n".join([route, main, doc, gate])

    route_tokens = [
        "APIRouter",
        "Depends(require_api_key)",
        "require_tenant_boundary",
        "require_rbac_route",
        "evaluate_privacy_security_readiness",
        '"/privacy-security"',
        'require_rbac_route("GET /readiness/privacy-security")',
        "public_shell_privacy_security_readiness_read_only",
        '"privacy_security_readiness_api_v0_1"] = True',
        '"privacy_security_readiness_api_available"] = True',
        '"read_only_privacy_security_readiness_api"] = True',
        '"task_candidates_executed"] = False',
        '"blockers_closed_by_route"] = 0',
        '"formal_security_review_completed_by_route"] = False',
        '"privacy_legal_review_completed_by_route"] = False',
        '"dpa_approved_by_route"] = False',
        '"security_certification_created_by_route"] = False',
        '"customer_data_processing_enabled_by_route"] = False',
        '"production_ready"] = False',
        '"customer_validated"] = False',
        '"customer_contacted"] = False',
        '"product_launched"] = False',
        '"body_inspected"] = False',
        '"credentials_inspected"] = False',
        '"private_core_inspected"] = False',
    ]
    missing_route = [token for token in route_tokens if token not in route]
    require(not missing_route, "route missing tokens: " + ", ".join(missing_route))

    main_tokens = [
        "readiness_router",
        'prefix="/readiness"',
        'tags=["readiness"]',
    ]
    missing_main = [token for token in main_tokens if token not in main]
    require(not missing_main, "main.py missing tokens: " + ", ".join(missing_main))

    report = evaluate_privacy_security_readiness(load_settings({}))
    require(report["privacy_security_review_status"] == "hold", "default status must be hold")
    require(report["data_classification_available"] is True, "data classification true")
    require(report["public_shell_data_map_available"] is True, "data map true")
    require(report["pii_policy_draft_available"] is True, "PII policy draft true")
    require(report["secret_handling_guidance_available"] is True, "secret guidance true")
    require(report["third_party_processor_inventory_available"] is True, "processor inventory true")
    require(report["legal_readiness_status"] == "hold", "legal readiness hold")
    require(report["terms_of_service_draft_available"] is True, "terms draft true")
    require(report["privacy_notice_draft_available"] is True, "privacy notice draft true")
    require(report["dpa_review_packet_available"] is True, "DPA review packet true")
    require(report["data_processing_agreement_draft_available"] is True, "DPA draft true")
    assert_false(
        report,
        [
            "personal_data_allowed",
            "terms_of_service_published",
            "terms_legal_review_completed",
            "privacy_notice_published",
            "data_processing_agreement_available",
            "formal_security_review_completed",
            "privacy_legal_review_completed",
            "security_certification_available",
            "soc2_available",
            "iso27001_available",
            "penetration_test_completed",
            "vulnerability_management_available",
            "production_vulnerability_management_ready",
            "compliance_logging_available",
            "production_security_ready",
            "customer_data_processing_ready",
            "production_ready",
            "customer_validated",
            "customer_contacted",
            "product_launched",
            "public_sdk_released",
            "private_core_exposed",
            "api_schema_modified",
            "runtime_modified",
            "kernel_modified",
            "external_calls_made",
        ],
    )

    required_doc_tokens = [
        "privacy_security_readiness_api_v0_1: true",
        "privacy_security_readiness_api_available: true",
        "read_only_privacy_security_readiness_api: true",
        "privacy_security_readiness_route: GET /readiness/privacy-security",
        "route_scope: public_shell_privacy_security_readiness_read_only",
        "privacy_security_review_status_default: hold",
        "data_classification_available_default: true",
        "public_shell_data_map_available_default: true",
        "pii_policy_draft_available_default: true",
        "personal_data_allowed_default: false",
        "secret_handling_guidance_available_default: true",
        "third_party_processor_inventory_available_default: true",
        "legal_readiness_status_default: hold",
        "terms_of_service_draft_available_default: true",
        "terms_of_service_published_default: false",
        "privacy_notice_draft_available_default: true",
        "privacy_notice_published_default: false",
        "dpa_review_packet_available_default: true",
        "data_processing_agreement_draft_available_default: true",
        "data_processing_agreement_available_default: false",
        "vulnerability_management_readiness_status_default: hold",
        "formal_security_review_completed_default: false",
        "privacy_legal_review_completed_default: false",
        "security_certification_available_default: false",
        "soc2_available_default: false",
        "iso27001_available_default: false",
        "penetration_test_completed_default: false",
        "vulnerability_management_available_default: false",
        "production_vulnerability_management_ready_default: false",
        "compliance_logging_available_default: false",
        "production_security_ready_default: false",
        "customer_data_processing_ready_default: false",
        "blockers_closed_by_route: 0",
        "task_candidates_executed: false",
        "formal_security_review_completed_by_route: false",
        "privacy_legal_review_completed_by_route: false",
        "dpa_approved_by_route: false",
        "security_certification_created_by_route: false",
        "customer_data_processing_enabled_by_route: false",
        "body_inspected: false",
        "credentials_inspected: false",
        "private_core_inspected: false",
        "production_ready: false",
        "customer_validated: false",
        "customer_contacted: false",
        "product_launched: false",
        "public_sdk_released: false",
        "private_core_exposed: false",
        "api_schema_modified: false",
        "runtime_modified: false",
        "kernel_modified: false",
        "external_calls_made: false",
        "answer: conditional",
        "recommend_for_controlled_preview_privacy_security_readiness_review: true",
        "recommend_for_formal_security_review_completion: false",
        "recommend_for_privacy_legal_review_completion: false",
        "recommend_for_dpa_approval: false",
        "recommend_for_security_certification: false",
        "recommend_for_customer_data_processing_enablement: false",
        "recommend_for_production_security_ready_claim: false",
        "recommend_for_public_launch_now: false",
    ]
    missing_doc = [token for token in required_doc_tokens if token not in combined]
    require(not missing_doc, "doc/gate missing tokens: " + ", ".join(missing_doc))

    forbidden_tokens = [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "customer_contacted: true",
        '"customer_contacted": true',
        "product_launched: true",
        '"product_launched": true',
        "public_sdk_released: true",
        '"public_sdk_released": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "task_candidates_executed: true",
        '"task_candidates_executed": true',
        "formal_security_review_completed_by_route: true",
        '"formal_security_review_completed_by_route": true',
        "privacy_legal_review_completed_by_route: true",
        '"privacy_legal_review_completed_by_route": true',
        "dpa_approved_by_route: true",
        '"dpa_approved_by_route": true',
        "security_certification_created_by_route: true",
        '"security_certification_created_by_route": true',
        "customer_data_processing_enabled_by_route: true",
        '"customer_data_processing_enabled_by_route": true',
        "production_security_ready: true",
        '"production_security_ready": true',
        "customer_data_processing_ready: true",
        '"customer_data_processing_ready": true',
        "api_schema_modified: true",
        '"api_schema_modified": true',
        "runtime_modified: true",
        '"runtime_modified": true',
        "kernel_modified: true",
        '"kernel_modified": true',
        "external_calls_made: true",
        '"external_calls_made": true',
    ]
    found = [token for token in forbidden_tokens if token in combined]
    require(not found, "forbidden true claims found: " + ", ".join(found))

    if importlib.util.find_spec("fastapi") and importlib.util.find_spec("starlette"):
        from fastapi.testclient import TestClient

        from saee_backend.main import app

        client = TestClient(app)
        response = client.get("/readiness/privacy-security")
        require(response.status_code == 200, "privacy-security route must return 200")
        payload = response.json()
        require(
            payload["route_scope"] == "public_shell_privacy_security_readiness_read_only",
            "privacy-security route scope mismatch",
        )
        require(payload["privacy_security_review_status"] == "hold", "route status hold")
        require(payload["data_classification_available"] is True, "route classification true")
        require(payload["terms_of_service_draft_available"] is True, "route terms draft true")
        require(payload["privacy_notice_draft_available"] is True, "route privacy draft true")
        require(payload["dpa_review_packet_available"] is True, "route DPA packet true")
        require(payload["blockers_closed_by_route"] == 0, "route must close zero blockers")
        require(payload["task_candidates_executed"] is False, "route must execute no tasks")
        assert_false(
            payload,
            [
                "personal_data_allowed",
                "terms_of_service_published",
                "privacy_notice_published",
                "data_processing_agreement_available",
                "formal_security_review_completed",
                "privacy_legal_review_completed",
                "security_certification_available",
                "soc2_available",
                "iso27001_available",
                "penetration_test_completed",
                "vulnerability_management_available",
                "production_vulnerability_management_ready",
                "compliance_logging_available",
                "production_security_ready",
                "customer_data_processing_ready",
                "production_ready",
                "customer_validated",
                "customer_contacted",
                "product_launched",
                "public_sdk_released",
                "private_core_exposed",
                "api_schema_modified",
                "runtime_modified",
                "kernel_modified",
                "external_calls_made",
                "body_inspected",
                "credentials_inspected",
                "private_core_inspected",
                "formal_security_review_completed_by_route",
                "privacy_legal_review_completed_by_route",
                "dpa_approved_by_route",
                "security_certification_created_by_route",
                "customer_data_processing_enabled_by_route",
            ],
        )

    print(
        "SAEE_PRIVACY_SECURITY_READINESS_API_SMOKE: PASS "
        "route=/readiness/privacy-security read_only=true status=hold "
        "blockers_closed_by_route=0 formal_security_review_completed=false "
        "privacy_legal_review_completed=false production_security_ready=false"
    )


if __name__ == "__main__":
    main()
