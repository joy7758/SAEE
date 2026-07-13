#!/usr/bin/env python3
"""Smoke test for the commercial blocker priority index."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_blocker_priority_index"
OUT_JSON = OUT_DIR / "commercial_blocker_priority_index.local.json"
OUT_MD = OUT_DIR / "commercial_blocker_priority_index.md"
OUT_CSV = OUT_DIR / "commercial_blocker_priority_index.csv"
OUT_HTML = OUT_DIR / "commercial_blocker_priority_index.html"
OUT_AUDIT = OUT_DIR / "commercial_blocker_priority_index_boundary_audit.md"
OUT_README = OUT_DIR / "README.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_BLOCKER_PRIORITY_INDEX_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_BLOCKER_PRIORITY_INDEX_V0_1.md"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_COMMERCIAL_BLOCKER_PRIORITY_INDEX_SMOKE: FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    subprocess.run(
        [sys.executable, "scripts/saee_commercial_blocker_priority_index.py"],
        cwd=ROOT,
        check=True,
    )
    for path in [OUT_JSON, OUT_MD, OUT_CSV, OUT_HTML, OUT_AUDIT, OUT_README, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected_values = {
        "commercial_blocker_priority_index_v0_1": True,
        "index_type": "local_commercial_blocker_priority_index",
        "index_scope": "human_review_priority_only_no_execution_no_closure",
        "status": "ready_for_separate_evidence_builder_request",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "production_blocker_count": 24,
        "open_blocker_count": 24,
        "missing_value_row_count": 0,
        "preferred_template_missing_value_row_count": 0,
        "selected_blocker_count": 5,
        "first_priority_blocker_id": "support_contact",
        "first_priority_tier": "validators_passed_pending_evidence_builder_request",
        "human_review_required": True,
        "boundary_violation_count": 0,
    }
    for key, value in expected_values.items():
        require(payload.get(key) == value, f"{key} must be {value}")

    false_flags = [
        "production_ready",
        "product_launched",
        "customer_validated",
        "customer_contacted",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
        "external_model_api_called",
        "external_ai_assistant_tested",
        "workbook_import_authorized",
        "evidence_collection_authorized",
        "execution_authorized",
        "blocker_closure_authorized",
        "development_permission_granted",
        "production_ready_claim",
        "customer_validation_claim",
    ]
    for flag in false_flags:
        require(payload.get(flag) is False, f"{flag} must be false")

    require(payload.get("boundary_violations") == [], "boundary violations must be empty")
    priority_rows = payload.get("priority_rows", [])
    selected_rows = payload.get("selected_sprint_blockers", [])
    require(len(priority_rows) == 24, "priority rows must include 24 blockers")
    require(len(selected_rows) == 5, "selected sprint rows must include 5 blockers")
    require(priority_rows[0]["blocker_id"] == "support_contact", "first priority blocker")
    require(
        priority_rows[0]["priority_tier"]
        == "validators_passed_pending_evidence_builder_request",
        "first priority tier",
    )
    require(
        [row["blocker_id"] for row in selected_rows]
        == [
            "support_contact",
            "pricing_page",
            "formal_security_review",
            "production_restore_policy",
            "production_monitoring",
        ],
        "selected blocker order",
    )
    for row in priority_rows:
        require(row.get("closure_allowed") is False, "row closure_allowed false")
        require(row.get("execution_allowed") is False, "row execution_allowed false")
        require(
            row.get("evidence_collection_allowed") is False,
            "row evidence_collection_allowed false",
        )
        require(
            row.get("requires_separate_execution_request") is True,
            "row separate execution request true",
        )

    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 24, "CSV must include 24 rows")
    require(rows[0]["blocker_id"] == "support_contact", "CSV first blocker")

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [OUT_MD, OUT_HTML, OUT_AUDIT, OUT_README, TOP_DOC, GATE]
    )
    required_tokens = [
        "commercial_blocker_priority_index_v0_1",
        "status: ready_for_separate_evidence_builder_request",
        "first_priority_blocker_id: support_contact",
        "production_blocker_count: 24",
        "open_blocker_count: 24",
        "missing_value_row_count: 0",
        "preferred_template_missing_value_row_count: 0",
        "workbook_import_authorized: false",
        "evidence_collection_authorized: false",
        "blocker_closure_authorized: false",
        "production_ready: false",
        "product_launched: false",
        "customer_validated: false",
        "runtime_modified: false",
        "backend_modified: false",
        "kernel_modified: false",
        "api_schema_modified: false",
        "private_core_exposed: false",
        "recommend_for_product_launch: false",
    ]
    for token in required_tokens:
        require(token in combined, "missing token " + token)

    forbidden_tokens = [
        "production_ready: true",
        '"production_ready": true',
        "product_launched: true",
        '"product_launched": true',
        "customer_validated: true",
        '"customer_validated": true',
        "workbook_import_authorized: true",
        '"workbook_import_authorized": true',
        "blocker_closure_authorized: true",
        '"blocker_closure_authorized": true',
        "recommend_for_product_launch: true",
        "<script",
        "fetch(",
        "XMLHttpRequest",
    ]
    for token in forbidden_tokens:
        require(token not in combined, "forbidden token " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_BLOCKER_PRIORITY_INDEX_V0_1.md",
        "/phase_b_product/commercial_readiness/commercial_blocker_priority_index/commercial_blocker_priority_index.local.json",
        "/phase_b_product/commercial_readiness/commercial_blocker_priority_index/commercial_blocker_priority_index.md",
        "/phase_b_product/commercial_readiness/commercial_blocker_priority_index/commercial_blocker_priority_index.csv",
        "/phase_b_product/commercial_readiness/commercial_blocker_priority_index/commercial_blocker_priority_index.html",
        "/phase_b_product/commercial_readiness/commercial_blocker_priority_index/commercial_blocker_priority_index_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_BLOCKER_PRIORITY_INDEX_V0_1.md",
        "/scripts/saee_commercial_blocker_priority_index.py",
        "/scripts/saee_commercial_blocker_priority_index_smoke.py",
    ]:
        require(path in llms, "llms.txt missing " + path)

    status_surfaces = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
    )
    for token in [
        "Commercial Blocker Priority Index v0.1",
        "commercial_blocker_priority_index_v0_1",
        "ready_for_separate_evidence_builder_request",
        "first_priority_blocker_id=support_contact",
        "open_blocker_count=24",
        "missing_value_row_count=0",
        "production_ready=false",
    ]:
        require(token in status_surfaces, "status surfaces missing " + token)

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    for token in [
        "check-commercial-blocker-priority-index:",
        "commercial-blocker-priority-index-smoke:",
        "scripts/saee_commercial_blocker_priority_index_smoke.py",
    ]:
        require(token in makefile, "Makefile missing " + token)

    agent_index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = agent_index.get("commercial_blocker_priority_index_v0_1", {})
    require(entry, "agent-index missing commercial_blocker_priority_index_v0_1")
    for key, value in expected_values.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")
    for flag in false_flags:
        require(entry.get(flag) is False, f"agent-index {flag} must be false")
    require(
        entry.get("make_target") == "make check-commercial-blocker-priority-index",
        "agent-index make target",
    )

    print(
        "SAEE_COMMERCIAL_BLOCKER_PRIORITY_INDEX_SMOKE: PASS "
        f"status={payload['status']} "
        f"open_blockers={payload['open_blocker_count']} "
        f"first_priority={payload['first_priority_blocker_id']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
