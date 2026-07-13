#!/usr/bin/env python3
"""Smoke check for the commercial blocker closure-readiness board."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/saee_commercial_blocker_closure_readiness_board.py"
DEFAULT_DASHBOARD = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_readiness_dashboard/commercial_readiness_dashboard.local.json"
)
DEFAULT_GAP_MATRIX = (
    ROOT / "phase_b_product/commercial_readiness/production_blocker_gap_matrix/gap_matrix.local.json"
)
OUTPUT_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_blocker_closure_readiness_board/closure_readiness_board.local.json"
)
OUTPUT_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_blocker_closure_readiness_board/closure_readiness_board.md"
)
OUTPUT_CSV = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_blocker_closure_readiness_board/closure_readiness_board.csv"
)
OUTPUT_HTML = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_blocker_closure_readiness_board/closure_readiness_board.html"
)
README = (
    ROOT / "phase_b_product/commercial_readiness/commercial_blocker_closure_readiness_board/README.md"
)
BOUNDARY_AUDIT = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_blocker_closure_readiness_board/closure_readiness_boundary_audit.md"
)
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/COMMERCIAL_BLOCKER_CLOSURE_READINESS_BOARD_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/SAEE_COMMERCIAL_BLOCKER_CLOSURE_READINESS_BOARD_RECOMMENDATION_GATE.md"
)

PASS_PREFIX = "SAEE_COMMERCIAL_BLOCKER_CLOSURE_READINESS_BOARD_SMOKE: PASS"
FAIL_PREFIX = "SAEE_COMMERCIAL_BLOCKER_CLOSURE_READINESS_BOARD_SMOKE: FAIL "


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(FAIL_PREFIX + message)


def check_boundary(payload: dict[str, object]) -> None:
    for key in [
        "evidence_collection_authorized",
        "execution_authorized",
        "owner_contacted_by_codex",
        "customer_contacted",
        "vendor_contacted",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "private_core_exposed",
        "product_launched",
        "production_ready",
        "customer_validated",
        "public_sdk_released",
        "external_calls_made",
        "external_model_api_called",
        "external_ai_assistant_tested",
        "task_candidates_executed",
        "development_permission_granted",
    ]:
        require(payload.get(key) is False, f"{key} must remain false")
    require(payload.get("blockers_closed_by_board") == 0, "board closes no blockers")


def run_board(*args: str) -> dict[str, object]:
    subprocess.run([sys.executable, str(SCRIPT), *args], cwd=ROOT, check=True, text=True)
    output_path = OUTPUT_JSON
    if "--output-json" in args:
        output_path = Path(args[args.index("--output-json") + 1])
    return json.loads(output_path.read_text(encoding="utf-8"))


def write_candidate_fixture(dashboard_path: Path, matrix_path: Path) -> None:
    dashboard = json.loads(DEFAULT_DASHBOARD.read_text(encoding="utf-8"))
    matrix = json.loads(DEFAULT_GAP_MATRIX.read_text(encoding="utf-8"))
    blocker_id = dashboard["blocker_dashboard"][0]["blocker_id"]
    dashboard["blocker_dashboard"][0]["status"] = "closed"
    dashboard["blocker_dashboard"][0]["satisfied"] = True
    dashboard["blocker_dashboard"][0]["closure_allowed_by_dashboard"] = True
    dashboard["blocker_dashboard"][0]["execution_allowed_by_dashboard"] = False
    dashboard["blocker_dashboard"][0]["missing_production_evidence_count"] = 0
    for row in matrix["matrix"]:
        if row["blocker_id"] == blocker_id:
            row["status"] = "closed"
            row["closure_allowed_by_matrix"] = True
            row["local_evidence_ready"] = True
            break
    dashboard_path.write_text(json.dumps(dashboard, indent=2) + "\n", encoding="utf-8")
    matrix_path.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    payload = run_board()
    for path in [
        OUTPUT_JSON,
        OUTPUT_MD,
        OUTPUT_CSV,
        OUTPUT_HTML,
        README,
        BOUNDARY_AUDIT,
        TOP_DOC,
        GATE,
    ]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")
    expected = {
        "commercial_blocker_closure_readiness_board_v0_1": True,
        "board_type": "saee_commercial_blocker_closure_readiness_board",
        "board_version": "v0.1",
        "status": "hold_no_blockers_ready_for_closure",
        "board_scope": "local_commercial_blocker_closure_readiness_diagnostic",
        "production_blocker_count": 24,
        "open_blocker_count": 24,
        "closure_candidate_count": 0,
        "not_ready_blocker_count": 24,
        "boundary_blocked_blocker_count": 0,
        "boundary_violation_count": 0,
        "ready_for_human_final_closure_review": False,
        "human_review_required": True,
        "separate_evidence_collection_request_required": True,
        "separate_execution_request_required": True,
        "separate_final_closure_approval_required": True,
        "source_closure_readiness_board_html": "phase_b_product/commercial_readiness/commercial_blocker_closure_readiness_board/closure_readiness_board.html",
        "local_static_closure_readiness_board_html": True,
        "browser_readable_closure_readiness_board": True,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"default {key} must be {value}")
    check_boundary(payload)
    review = payload.get("blocker_closure_readiness_review", [])
    require(len(review) == 24, "board must review 24 production blockers")
    require(
        all(item.get("closure_status") == "not_ready" for item in review),
        "default blockers must not be closure-ready",
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        fixture_dashboard = tmp / "dashboard.json"
        fixture_matrix = tmp / "matrix.json"
        write_candidate_fixture(fixture_dashboard, fixture_matrix)
        fixture = run_board(
            "--dashboard-json",
            str(fixture_dashboard),
            "--gap-matrix-json",
            str(fixture_matrix),
            "--output-json",
            str(tmp / "fixture_board.json"),
            "--output-md",
            str(tmp / "fixture_board.md"),
            "--output-csv",
            str(tmp / "fixture_board.csv"),
        )
        require(
            fixture["status"] == "hold_human_final_closure_review_required",
            "candidate fixture must still require human final closure review",
        )
        require(fixture["closure_candidate_count"] == 1, "fixture has one candidate")
        require(fixture["blockers_closed_by_board"] == 0, "fixture closes no blockers")
        check_boundary(fixture)

        unsafe_dashboard = json.loads(fixture_dashboard.read_text(encoding="utf-8"))
        unsafe_dashboard["production_ready"] = True
        unsafe_path = tmp / "unsafe_dashboard.json"
        unsafe_path.write_text(json.dumps(unsafe_dashboard, indent=2) + "\n", encoding="utf-8")
        unsafe = run_board(
            "--dashboard-json",
            str(unsafe_path),
            "--gap-matrix-json",
            str(fixture_matrix),
            "--output-json",
            str(tmp / "unsafe_board.json"),
            "--output-md",
            str(tmp / "unsafe_board.md"),
            "--output-csv",
            str(tmp / "unsafe_board.csv"),
        )
        require(
            unsafe["status"] == "stop_boundary_violation",
            "unsafe fixture must stop on boundary violation",
        )
        require(
            unsafe["boundary_violation_count"] >= 1,
            "unsafe fixture must report boundary violation",
        )

    # Restore default repo outputs after temp fixtures.
    payload = run_board()

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [OUTPUT_MD, OUTPUT_HTML, README, BOUNDARY_AUDIT, TOP_DOC, GATE]
    )
    for token in [
        "commercial_blocker_closure_readiness_board_v0_1: true",
        "status: hold_no_blockers_ready_for_closure",
        "board_scope: local_commercial_blocker_closure_readiness_diagnostic",
        "production_blocker_count: 24",
        "open_blocker_count: 24",
        "closure_candidate_count: 0",
        "not_ready_blocker_count: 24",
        "ready_for_human_final_closure_review: false",
        "separate_final_closure_approval_required: true",
        "SAEE 商用阻塞关闭准备度",
        "现在没有任何 blocker 可以关闭。",
        "下一步只允许人工补证据",
        "本页为本地静态 HTML 诊断页",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "owner_contacted_by_codex: false",
        "blockers_closed_by_board: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "answer: conditional",
        "recommend_for_closure_readiness_diagnostic: true",
        "recommend_for_blocker_closure: false",
        "recommend_for_evidence_collection: false",
        "recommend_for_automatic_execution: false",
    ]:
        require(token in combined, "missing doc/gate token " + token)

    forbidden = [
        "<script",
        "fetch(",
        "XMLHttpRequest",
        "http://",
        "https://",
        "mailto:",
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "evidence_collection_authorized: true",
        '"evidence_collection_authorized": true',
        "execution_authorized: true",
        '"execution_authorized": true',
        "owner_contacted_by_codex: true",
        '"owner_contacted_by_codex": true',
        "recommend_for_blocker_closure: true",
        "recommend_for_evidence_collection: true",
        "recommend_for_automatic_execution: true",
    ]
    found = [token for token in forbidden if token in combined]
    require(not found, "forbidden true claim present: " + ", ".join(found))

    print(
        PASS_PREFIX
        + " status=hold_no_blockers_ready_for_closure "
        + "closure_candidate_count=0 blockers_closed_by_board=0 "
        + "production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
