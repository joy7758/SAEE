#!/usr/bin/env python3
"""Smoke check for SAEE Legal / DPA Readiness API v0.1."""

from __future__ import annotations

import importlib.util
import py_compile
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.legal_readiness import evaluate_legal_readiness


ROUTE_PATH = ROOT / "saee_backend/api/readiness.py"
MAIN_PATH = ROOT / "saee_backend/main.py"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/LEGAL_READINESS_API_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_LEGAL_READINESS_API_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_LEGAL_READINESS_API_SMOKE: FAIL: {message}")


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

    required_tokens = [
        "APIRouter",
        "Depends(require_api_key)",
        "require_tenant_boundary",
        "require_rbac_route",
        "evaluate_legal_readiness",
        '"/legal"',
        'require_rbac_route("GET /readiness/legal")',
        "public_shell_legal_readiness_read_only",
        '"legal_readiness_api_v0_1"] = True',
        '"legal_readiness_api_available"] = True',
        '"read_only_legal_readiness_api"] = True',
        '"task_candidates_executed"] = False',
        '"blockers_closed_by_route"] = 0',
        '"terms_published_by_route"] = False',
        '"privacy_notice_published_by_route"] = False',
        '"legal_review_completed_by_route"] = False',
        '"dpa_approved_by_route"] = False',
        '"customer_data_processing_enabled_by_route"] = False',
        '"contract_template_created_by_route"] = False',
        '"production_ready"] = False',
        '"customer_validated"] = False',
        '"customer_contacted"] = False',
        '"product_launched"] = False',
        '"body_inspected"] = False',
        '"credentials_inspected"] = False',
        '"private_core_inspected"] = False',
        'prefix="/readiness"',
        'tags=["readiness"]',
        "legal_readiness_api_v0_1: true",
        "legal_readiness_api_available: true",
        "read_only_legal_readiness_api: true",
        "legal_readiness_route: GET /readiness/legal",
        "route_scope: public_shell_legal_readiness_read_only",
        "legal_readiness_status_default: hold",
        "terms_of_service_draft_available_default: true",
        "terms_of_service_published_default: false",
        "terms_legal_review_completed_default: false",
        "privacy_notice_draft_available_default: true",
        "privacy_notice_published_default: false",
        "privacy_legal_review_completed_default: false",
        "dpa_review_packet_available_default: true",
        "data_processing_agreement_draft_available_default: true",
        "data_processing_agreement_available_default: false",
        "customer_data_processing_ready_default: false",
        "customer_contract_template_available_default: false",
        "legal_approval_completed_default: false",
        "production_legal_ready_default: false",
        "blockers_closed_by_route: 0",
        "task_candidates_executed: false",
        "terms_published_by_route: false",
        "privacy_notice_published_by_route: false",
        "legal_review_completed_by_route: false",
        "dpa_approved_by_route: false",
        "customer_data_processing_enabled_by_route: false",
        "contract_template_created_by_route: false",
        "body_inspected: false",
        "credentials_inspected: false",
        "private_core_inspected: false",
        "customer_contacted: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "public_sdk_released: false",
        "private_core_exposed: false",
        "api_schema_modified: false",
        "runtime_modified: false",
        "kernel_modified: false",
        "external_calls_made: false",
        "answer: conditional",
        "recommend_for_controlled_preview_legal_readiness_review: true",
        "recommend_for_terms_publication: false",
        "recommend_for_privacy_notice_publication: false",
        "recommend_for_legal_review_completion: false",
        "recommend_for_dpa_approval: false",
        "recommend_for_customer_data_processing_enablement: false",
        "recommend_for_customer_contracting: false",
        "recommend_for_production_legal_ready_claim: false",
        "recommend_for_public_launch_now: false",
    ]
    missing = [token for token in required_tokens if token not in combined]
    require(not missing, "missing tokens: " + ", ".join(missing))

    report = evaluate_legal_readiness(load_settings({}))
    require(report["legal_readiness_status"] == "hold", "default status must be hold")
    require(report["terms_of_service_draft_available"] is True, "terms draft true")
    require(report["privacy_notice_draft_available"] is True, "privacy notice draft true")
    require(report["dpa_review_packet_available"] is True, "DPA packet true")
    require(report["data_processing_agreement_draft_available"] is True, "DPA draft true")
    assert_false(
        report,
        [
            "terms_of_service_published",
            "terms_legal_review_completed",
            "privacy_notice_published",
            "privacy_legal_review_completed",
            "data_processing_agreement_available",
            "customer_data_processing_ready",
            "customer_contract_template_available",
            "legal_approval_completed",
            "production_legal_ready",
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
            "external_model_api_called",
        ],
    )

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
        "terms_published_by_route: true",
        '"terms_published_by_route": true',
        "privacy_notice_published_by_route: true",
        '"privacy_notice_published_by_route": true',
        "legal_review_completed_by_route: true",
        '"legal_review_completed_by_route": true',
        "dpa_approved_by_route: true",
        '"dpa_approved_by_route": true',
        "customer_data_processing_enabled_by_route: true",
        '"customer_data_processing_enabled_by_route": true',
        "contract_template_created_by_route: true",
        '"contract_template_created_by_route": true',
        "production_legal_ready: true",
        '"production_legal_ready": true',
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
        response = client.get("/readiness/legal")
        require(response.status_code == 200, "legal route must return 200")
        payload = response.json()
        require(
            payload["route_scope"] == "public_shell_legal_readiness_read_only",
            "legal route scope mismatch",
        )
        require(payload["legal_readiness_status"] == "hold", "route status hold")
        require(payload["legal_readiness_api_available"] is True, "route API available")
        require(payload["terms_of_service_draft_available"] is True, "route terms draft true")
        require(payload["privacy_notice_draft_available"] is True, "route privacy draft true")
        require(payload["dpa_review_packet_available"] is True, "route DPA packet true")
        require(payload["blockers_closed_by_route"] == 0, "route must close zero blockers")
        require(payload["task_candidates_executed"] is False, "route must execute no tasks")
        assert_false(
            payload,
            [
                "terms_of_service_published",
                "terms_legal_review_completed",
                "privacy_notice_published",
                "privacy_legal_review_completed",
                "data_processing_agreement_available",
                "customer_data_processing_ready",
                "customer_contract_template_available",
                "legal_approval_completed",
                "production_legal_ready",
                "terms_published_by_route",
                "privacy_notice_published_by_route",
                "legal_review_completed_by_route",
                "dpa_approved_by_route",
                "customer_data_processing_enabled_by_route",
                "contract_template_created_by_route",
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

    print(
        "SAEE_LEGAL_READINESS_API_SMOKE: PASS "
        "route=/readiness/legal read_only=true status=hold "
        "blockers_closed_by_route=0 legal_review_completed=false "
        "dpa_approved=false production_legal_ready=false"
    )


if __name__ == "__main__":
    main()

