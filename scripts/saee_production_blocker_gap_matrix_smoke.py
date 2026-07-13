#!/usr/bin/env python3
"""Smoke check for the SAEE production blocker evidence gap matrix."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX_DIR = ROOT / "phase_b_product/commercial_readiness/production_blocker_gap_matrix"
MATRIX_JSON = MATRIX_DIR / "gap_matrix.local.json"
MATRIX_MD = MATRIX_DIR / "gap_matrix.local.md"
MATRIX_CSV = MATRIX_DIR / "gap_matrix.local.csv"
README_PATH = MATRIX_DIR / "README.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/PRODUCTION_BLOCKER_EVIDENCE_GAP_MATRIX_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PRODUCTION_BLOCKER_EVIDENCE_GAP_MATRIX_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        print(f"SAEE_PRODUCTION_BLOCKER_GAP_MATRIX_SMOKE: FAIL {message}")
        sys.exit(1)


def main() -> None:
    for path in [MATRIX_JSON, MATRIX_MD, MATRIX_CSV, README_PATH, DOC_PATH, GATE_PATH]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    matrix = json.loads(MATRIX_JSON.read_text(encoding="utf-8"))

    expected_false = [
        "task_candidates_executed",
        "development_permission_granted",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "private_core_exposed",
        "product_launched",
        "customer_contacted",
        "customer_validated",
        "production_ready",
        "public_sdk_released",
        "external_calls_made",
        "external_model_api_called",
        "external_ai_assistant_tested",
    ]
    for key in expected_false:
        require(matrix.get(key) is False, f"{key} must be false")

    require(
        matrix.get("matrix_type") == "saee_production_blocker_evidence_gap_matrix",
        "wrong matrix_type",
    )
    require(
        matrix.get("matrix_scope") == "local_public_shell_commercial_blocker_review",
        "wrong matrix_scope",
    )
    require(matrix.get("production_launch_status") == "hold", "launch must remain hold")
    require(matrix.get("production_blocker_count") == 24, "must keep 24 blockers")
    require(matrix.get("open_blocker_count") == 24, "must keep 24 open blockers")
    require(matrix.get("blockers_closed_by_matrix") == 0, "matrix closes zero blockers")
    require(matrix.get("local_evidence_categories") == 8, "must map 8 evidence categories")
    require(matrix.get("all_profile_paths_present") is True, "all profile paths present")
    require(matrix.get("human_review_required") is True, "human review required")
    require(matrix.get("matrix_status") == "hold", "matrix status must be hold")

    items = matrix.get("matrix", [])
    require(len(items) == 24, "matrix must contain 24 blocker rows")
    for item in items:
        require(item.get("status") == "open", "each blocker stays open")
        require(item.get("local_evidence_file_exists") is True, "local evidence file exists")
        require(item.get("local_evidence_ready") is False, "local evidence not ready")
        require(item.get("human_approval_required") is True, "human approval required")
        require(
            item.get("requires_separate_execution_request") is True,
            "separate execution request required",
        )
        require(item.get("closure_allowed_by_matrix") is False, "closure not allowed")
        require(item.get("can_close_without_evidence") is False, "cannot close without evidence")
        require(item.get("required_evidence"), "required evidence text present")
        require(item.get("owner_review_lane"), "owner review lane present")

    with MATRIX_CSV.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 24, "CSV must contain 24 blocker rows")

    combined_docs = "\n".join(
        [
            MATRIX_MD.read_text(encoding="utf-8"),
            README_PATH.read_text(encoding="utf-8"),
            DOC_PATH.read_text(encoding="utf-8"),
            GATE_PATH.read_text(encoding="utf-8"),
        ]
    )
    required_tokens = [
        "local_public_shell_commercial_blocker_review",
        "production_launch_status: hold",
        "production_blocker_count: 24",
        "open_blocker_count: 24",
        "blockers_closed_by_matrix: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
    ]
    for token in required_tokens:
        require(token in combined_docs, f"docs missing {token}")

    forbidden_tokens = [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "blockers_closed_by_matrix: 1",
        '"blockers_closed_by_matrix": 1',
        "external_calls_made: true",
        '"external_calls_made": true',
    ]
    found = [token for token in forbidden_tokens if token in combined_docs]
    require(not found, "forbidden claims found: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    required_llms = [
        "/phase_b_product/commercial_readiness/PRODUCTION_BLOCKER_EVIDENCE_GAP_MATRIX_V0_1.md",
        "/docs/strategy/SAEE_PRODUCTION_BLOCKER_EVIDENCE_GAP_MATRIX_RECOMMENDATION_GATE.md",
        "/phase_b_product/commercial_readiness/production_blocker_gap_matrix/README.md",
        "/phase_b_product/commercial_readiness/production_blocker_gap_matrix/gap_matrix.local.json",
        "/phase_b_product/commercial_readiness/production_blocker_gap_matrix/gap_matrix.local.md",
        "/phase_b_product/commercial_readiness/production_blocker_gap_matrix/gap_matrix.local.csv",
        "/scripts/saee_production_blocker_gap_matrix.py",
        "/scripts/saee_production_blocker_gap_matrix_smoke.py",
    ]
    missing = [path for path in required_llms if path not in llms]
    require(not missing, "llms missing " + ", ".join(missing))

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("production_blocker_evidence_gap_matrix_v0_1", {})
    expected_entry = {
        "status": "hold",
        "production_blocker_evidence_gap_matrix_v0_1": True,
        "matrix_scope": "local_public_shell_commercial_blocker_review",
        "production_launch_status": "hold",
        "production_blocker_count": 24,
        "open_blocker_count": 24,
        "blockers_closed_by_matrix": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "external_calls_made": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
    }
    for key, value in expected_entry.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_PRODUCTION_BLOCKER_GAP_MATRIX_SMOKE: PASS "
        "production_blockers=24 open_blockers=24 blockers_closed_by_matrix=0 "
        "production_ready=false customer_validated=false"
    )


if __name__ == "__main__":
    main()
