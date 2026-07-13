#!/usr/bin/env python3
"""Smoke test for the commercial review-ready marker catalog."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_commercial_review_ready_marker_catalog.py"
OUT_DIR = ROOT / "phase_b_product/commercial_readiness/matrix_update_requests/commercial_review_ready_marker_catalog"
SUMMARY = OUT_DIR / "commercial_review_ready_marker_catalog.local.json"
REPORT = OUT_DIR / "commercial_review_ready_marker_catalog.md"
CSV = OUT_DIR / "commercial_review_ready_marker_catalog.csv"
BOUNDARY = OUT_DIR / "commercial_review_ready_marker_catalog_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_REVIEW_READY_MARKER_CATALOG_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_REVIEW_READY_MARKER_CATALOG_GATE.md"


def fail(message: str) -> None:
    raise SystemExit("SAEE_COMMERCIAL_REVIEW_READY_MARKER_CATALOG_SMOKE: FAIL " + message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"{path.relative_to(ROOT)} must contain an object")
    return data


def main() -> None:
    result = subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, text=True, capture_output=True, check=True)
    require("SAEE_COMMERCIAL_REVIEW_READY_MARKER_CATALOG: PASS" in result.stdout, "runner did not pass")
    for path in [SUMMARY, REPORT, CSV, BOUNDARY, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "commercial_review_ready_marker_catalog_v0_1": True,
        "catalog_type": "source_backed_review_ready_marker_catalog_no_execution_no_closure",
        "status": "ready_for_human_matrix_update_scope_review_no_execution",
        "canonical_open_blocker_count": 24,
        "review_ready_marker_candidate_count": 23,
        "not_cataloged_blocker_count": 1,
        "not_cataloged_blocker_ids": ["customer_validated"],
        "source_group_count": 9,
        "current_matrix_request_target_count": 5,
        "matrix_request_scope_refresh_required": True,
        "exact_human_execution_approval_still_required": True,
        "human_review_required": True,
        "recommendation_gate": "conditional",
        "would_recommend_to_potential_customer": "conditional",
        "catalog_execution_authorized": False,
        "matrix_update_execution_authorized": False,
        "matrix_update_executed": False,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_catalog": 0,
        "open_blocker_count_reduced": False,
        "pricing_page_published": False,
        "checkout_enabled": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
        "development_permission_granted": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "external_calls_made": False,
        "external_model_api_called": False,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value!r}")
    require(payload.get("boundary_violations") == [], "boundary violations must be empty")
    ids = payload.get("review_ready_marker_candidate_ids")
    require(isinstance(ids, list) and len(ids) == 23 and len(set(ids)) == 23, "candidate ids must be 23 unique blockers")
    require("customer_validated" not in ids, "customer validation must not be cataloged")
    rows = payload.get("candidate_rows")
    require(isinstance(rows, list) and len(rows) == 23, "catalog must contain 23 rows")
    for row in rows:
        require(row.get("review_ready_marker_candidate") is True, "every row must be review-ready")
        require(row.get("matrix_current_status") == "open", "canonical blocker must remain open")
        require(row.get("matrix_current_local_evidence_ready") is False, "canonical evidence-ready must remain false")
        require(row.get("matrix_current_closure_allowed") is False, "canonical closure must remain false")
        require(row.get("requested_status_after_update") == "open", "requested status must remain open")
        require(row.get("requested_local_evidence_ready_after_update") is False, "request must not set evidence ready")
        require(row.get("requested_closure_allowed_after_update") is False, "request must not allow closure")
        require(row.get("requires_exact_human_execution_approval") is True, "exact approval must be required")
        require(row.get("closure_allowed_by_catalog") is False, "catalog must not allow closure")

    with CSV.open(encoding="utf-8", newline="") as handle:
        require(len(list(csv.DictReader(handle))) == 23, "CSV must contain 23 rows")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, BOUNDARY, TOP_DOC, GATE])
    for token in [
        "Commercial Review-Ready Marker Catalog",
        "review_ready_marker_candidate_count: 23",
        "not_cataloged_blocker_ids: customer_validated",
        "matrix_request_scope_refresh_required: true",
        "exact_human_execution_approval_still_required: true",
        "recommendation_gate: conditional",
        "matrix_update_executed=false",
        "blockers_closed_by_catalog=0",
        "production_ready=false",
        "customer_validated=false",
        "answer: conditional_scope_refresh_recommended_no_execution",
    ]:
        require(token in combined, f"docs missing {token}")
    for forbidden in ["matrix_update_executed=true", "canonical_gap_matrix_modified=true", "blocker_closure_authorized=true", "production_ready=true", "customer_validated=true", "product_launched=true", "private_core_exposed=true"]:
        require(forbidden not in combined, f"forbidden claim found {forbidden}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_REVIEW_READY_MARKER_CATALOG_V0_1.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_review_ready_marker_catalog/commercial_review_ready_marker_catalog.local.json",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_review_ready_marker_catalog/commercial_review_ready_marker_catalog.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_review_ready_marker_catalog/commercial_review_ready_marker_catalog.csv",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_review_ready_marker_catalog/commercial_review_ready_marker_catalog_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_REVIEW_READY_MARKER_CATALOG_GATE.md",
        "/scripts/saee_commercial_review_ready_marker_catalog.py",
        "/scripts/saee_commercial_review_ready_marker_catalog_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    entry = read_json(ROOT / "agent-index.json").get("commercial_review_ready_marker_catalog_v0_1")
    require(isinstance(entry, dict), "agent-index entry missing")
    for key in ["status", "canonical_open_blocker_count", "review_ready_marker_candidate_count", "review_ready_marker_candidate_ids", "not_cataloged_blocker_count", "not_cataloged_blocker_ids", "current_matrix_request_target_count", "matrix_request_scope_refresh_required", "exact_human_execution_approval_still_required", "recommendation_gate", "matrix_update_execution_authorized", "matrix_update_executed", "canonical_gap_matrix_modified", "blocker_closure_authorized", "blockers_closed_by_catalog", "production_ready", "customer_validated", "product_launched", "private_core_exposed"]:
        require(entry.get(key) == payload.get(key), f"agent-index {key} must match")

    runner_text = RUNNER.read_text(encoding="utf-8")
    for forbidden in ["requests.", "urllib.", "httpx.", "webbrowser", "selenium"]:
        require(forbidden not in runner_text, f"runner must not call external services: {forbidden}")

    print("SAEE_COMMERCIAL_REVIEW_READY_MARKER_CATALOG_SMOKE: PASS candidates=23 not_cataloged=customer_validated matrix_update_executed=false blockers_closed=0 production_ready=false")


if __name__ == "__main__":
    main()
