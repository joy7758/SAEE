#!/usr/bin/env python3
"""Smoke test the local static customer-validation session entry workbench."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
WORKBENCH_HTML = EVIDENCE_DIR / "external_customer_validation_session_entry_workbench.html"
WORKBENCH_SUMMARY = EVIDENCE_DIR / "external_customer_validation_session_entry_workbench.local.json"
WORKBENCH_REPORT = EVIDENCE_DIR / "external_customer_validation_session_entry_workbench.md"
BOUNDARY_AUDIT = EVIDENCE_DIR / "external_customer_validation_session_entry_workbench_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_SESSION_ENTRY_WORKBENCH_GATE.md"
RUNNER = ROOT / "scripts/saee_external_customer_validation_session_entry_workbench.py"


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_EXTERNAL_CUSTOMER_VALIDATION_SESSION_ENTRY_WORKBENCH_SMOKE: FAIL "
        + message
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic only
        fail(f"{path.relative_to(ROOT)} must be valid JSON: {exc}")
    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)} must be a JSON object")
    return data


def main() -> None:
    for path in [WORKBENCH_HTML, WORKBENCH_SUMMARY, WORKBENCH_REPORT, BOUNDARY_AUDIT, GATE, RUNNER]:
        require(path.is_file(), f"missing required file {path.relative_to(ROOT)}")

    summary = read_json(WORKBENCH_SUMMARY)
    expected = {
        "external_customer_validation_session_entry_workbench_v0_1": True,
        "status": "local_static_human_entry_workbench_ready",
        "workbench_type": "local_static_manual_entry_helper",
        "html_has_form": True,
        "download_json_helper": True,
        "copy_json_helper": True,
        "human_action_required": True,
        "current_goal_blocker": "customer_validated",
        "remaining_blocker_count": 1,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted_by_codex": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "public_sdk_released": False,
        "public_validation_claim_published": False,
        "testimonial_published": False,
        "case_study_published": False,
        "development_permission_granted": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_workbench": 0,
    }
    for key, value in expected.items():
        require(summary.get(key) == value, f"{key} must be {value}")
    require(summary.get("review_checkbox_count") == 25, "review_checkbox_count must be 25")

    html = WORKBENCH_HTML.read_text(encoding="utf-8")
    for token in [
        "SAEE 客户验证录入工作台",
        "不上传、不提交、不联网",
        "external_customer_validation_session_entry.human_filled.local.json",
        "function buildPayload()",
        "downloadJson()",
        "baseTemplate",
    ]:
        require(token in html, "workbench html missing token: " + token)
    forbidden_html_tokens = [
        "fetch(",
        "XMLHttpRequest",
        "https://",
        "http://",
        "sendBeacon",
        "localStorage",
    ]
    for token in forbidden_html_tokens:
        require(token not in html, "workbench html must not contain external/browser persistence token: " + token)

    combined = (
        WORKBENCH_REPORT.read_text(encoding="utf-8")
        + "\n"
        + BOUNDARY_AUDIT.read_text(encoding="utf-8")
        + "\n"
        + GATE.read_text(encoding="utf-8")
    )
    for token in [
        "external_customer_validation_session_entry_workbench_v0_1: true",
        "status: local_static_human_entry_workbench_ready",
        "customer_validated: false",
        "production_ready: false",
        "product_launched: false",
        "private_core_exposed: false",
        "blockers_closed_by_workbench: 0",
        "answer: local_static_human_entry_workbench_ready",
    ]:
        require(token in combined, "report/gate missing token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry_workbench.html",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry_workbench.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry_workbench.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry_workbench_boundary_audit.md",
        "/docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_SESSION_ENTRY_WORKBENCH_GATE.md",
        "/scripts/saee_external_customer_validation_session_entry_workbench.py",
        "/scripts/saee_external_customer_validation_session_entry_workbench_smoke.py",
    ]:
        require(token in llms, "llms.txt missing token: " + token)

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    for token in [
        "external-customer-validation-session-entry-workbench-smoke:",
        "check-external-customer-validation-session-entry-workbench:",
        "scripts/saee_external_customer_validation_session_entry_workbench_smoke.py",
    ]:
        require(token in makefile, "Makefile missing token: " + token)

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("external_customer_validation_session_entry_workbench_v0_1", {})
    require(isinstance(entry, dict), "agent-index entry must be an object")
    for key, value in expected.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")
    require(entry.get("review_checkbox_count") == 25, "agent-index review_checkbox_count must be 25")

    print(
        "SAEE_EXTERNAL_CUSTOMER_VALIDATION_SESSION_ENTRY_WORKBENCH_SMOKE: PASS "
        "status=local_static_human_entry_workbench_ready "
        "customer_validated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
