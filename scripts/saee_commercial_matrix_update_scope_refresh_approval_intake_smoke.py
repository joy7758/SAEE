#!/usr/bin/env python3
"""Smoke test the scope-refresh exact-phrase intake without activation."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_commercial_matrix_update_scope_refresh_approval_intake.py"
OUT_DIR = ROOT / "phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_scope_refresh_approval"
TEMPLATE = OUT_DIR / "scope_refresh_approval_input.template.json"
INTAKE = OUT_DIR / "scope_refresh_approval_intake.local.json"
COPY_MD = OUT_DIR / "scope_refresh_approval_copy_card.md"
COPY_HTML = OUT_DIR / "scope_refresh_approval_copy_card.html"
BOUNDARY = OUT_DIR / "scope_refresh_approval_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_SCOPE_REFRESH_APPROVAL_INTAKE_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_SCOPE_REFRESH_APPROVAL_INTAKE_GATE.md"
CURRENT_REQUEST = ROOT / "phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_request_packet.local.json"
EXACT_PHRASE = (
    "批准矩阵申请范围刷新：将活动申请从 5 项更新为 23 项，仅刷新 no-execution 申请范围，"
    "不执行矩阵更新，不关闭 blocker，不声明生产可用。"
)


def fail(message: str) -> None:
    raise SystemExit("SAEE_COMMERCIAL_MATRIX_UPDATE_SCOPE_REFRESH_APPROVAL_INTAKE_SMOKE: FAIL " + message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    try:
        display_path = path.relative_to(ROOT)
    except ValueError:
        # Fixture outputs intentionally live in a system temporary directory.
        # Keep the assertion readable without requiring every test artifact to
        # be a descendant of the repository root.
        display_path = path
    require(isinstance(data, dict), f"{display_path} must contain an object")
    return data


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(RUNNER), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )


def assert_false_boundaries(payload: dict[str, Any]) -> None:
    for key in [
        "active_matrix_request_replaced", "execution_request_regenerated",
        "approval_scope_changed", "matrix_update_execution_authorized",
        "matrix_update_executed", "canonical_gap_matrix_modified",
        "canonical_closure_board_modified", "blocker_closure_authorized",
        "open_blocker_count_reduced", "production_ready", "customer_validated",
        "product_launched", "private_core_exposed", "runtime_modified",
        "backend_modified", "kernel_modified", "api_schema_modified",
        "customer_contacted", "external_calls_made", "external_model_api_called",
    ]:
        require(payload.get(key) is False, f"{key} must be false")
    require(payload.get("blockers_closed_by_scope_approval_intake") == 0, "must close zero blockers")


def main() -> None:
    default = run()
    require("SAEE_COMMERCIAL_MATRIX_UPDATE_SCOPE_REFRESH_APPROVAL_INTAKE: PASS" in default.stdout, "default runner did not pass")
    for path in [TEMPLATE, INTAKE, COPY_MD, COPY_HTML, BOUNDARY, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(INTAKE)
    require(payload.get("status") == "waiting_for_exact_human_scope_refresh_phrase", "default status must wait")
    require(payload.get("scope_refresh_packet_ready") is True, "scope packet must be ready")
    require(payload.get("previous_target_count") == 5, "previous count must be 5")
    require(payload.get("refreshed_target_count") == 23, "refreshed count must be 23")
    require(payload.get("not_cataloged_blocker_ids") == ["customer_validated"], "customer validation must be excluded")
    require(payload.get("exact_scope_refresh_phrase") == EXACT_PHRASE, "exact phrase mismatch")
    require(payload.get("phrase_provided") is False, "default phrase must be absent")
    require(payload.get("phrase_matches_exactly") is False, "default phrase must not match")
    require(payload.get("human_filled_scope_approval_written") is False, "default must not write approval")
    require(payload.get("ready_for_separate_active_request_replacement_validator") is False, "default must not be replacement-ready")
    require(payload.get("separate_active_request_replacement_step_required") is True, "separate replacement required")
    require(payload.get("separate_matrix_execution_approval_still_required") is True, "separate execution approval required")
    assert_false_boundaries(payload)

    template = read_json(TEMPLATE)
    require(template.get("human_decision") == "", "template decision must be blank")
    require(template.get("approve_scope_refresh_5_to_23_no_execution") is False, "template approval must be false")
    require(len(template.get("refreshed_target_ids", [])) == 23, "template must carry 23 ids")

    with tempfile.TemporaryDirectory() as tmp:
        accepted_path = Path(tmp) / "accepted.local.json"
        accepted = run(
            "--phrase", EXACT_PHRASE,
            "--write-human-filled",
            "--human-filled-output", str(accepted_path),
            "--reviewer", "smoke-human",
            "--approval-reference", "smoke-scope-approval",
        )
        require("scope_refresh_phrase_accepted_human_record_written_no_activation" in accepted.stdout, "exact phrase must be accepted")
        require(accepted_path.is_file(), "accepted phrase must write only requested temp record")
        record = read_json(accepted_path)
        require(record.get("human_decision") == "approve_matrix_request_scope_refresh_5_to_23_no_execution", "human decision mismatch")
        require(record.get("approve_scope_refresh_5_to_23_no_execution") is True, "record approval must be true")
        require(record.get("confirm_active_request_replacement_requires_separate_step") is True, "replacement separation missing")
        require(record.get("confirm_no_matrix_update_execution") is True, "no-execution confirmation missing")
        require(record.get("confirm_no_blocker_closure") is True, "no-closure confirmation missing")

        rejected_path = Path(tmp) / "rejected.local.json"
        rejected = run(
            "--phrase", "按推荐确认",
            "--write-human-filled",
            "--human-filled-output", str(rejected_path),
        )
        require("waiting_for_exact_human_scope_refresh_phrase" in rejected.stdout, "generic phrase must be rejected")
        require(not rejected_path.exists(), "generic phrase must not write approval record")

    # Restore canonical default hold artifacts after fixture checks.
    run()
    payload = read_json(INTAKE)
    require(payload.get("status") == "waiting_for_exact_human_scope_refresh_phrase", "canonical intake must end waiting")
    assert_false_boundaries(payload)

    current_request = read_json(CURRENT_REQUEST)
    require(len(current_request.get("target_blockers", [])) == 5, "active request must remain five-row")
    require(current_request.get("matrix_update_executed") is False, "active request must not execute")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [COPY_MD, COPY_HTML, BOUNDARY, TOP_DOC, GATE])
    for token in [
        EXACT_PHRASE,
        "previous_target_count: 5",
        "refreshed_target_count: 23",
        "active_matrix_request_replaced=false",
        "approval_scope_changed=false",
        "matrix_update_executed=false",
        "blockers_closed_by_scope_approval_intake=0",
        "production_ready=false",
        "customer_validated=false",
    ]:
        require(token in combined, f"docs missing {token}")
    for forbidden in [
        "active_matrix_request_replaced=true", "approval_scope_changed=true",
        "matrix_update_executed=true", "blocker_closure_authorized=true",
        "production_ready=true", "customer_validated=true", "private_core_exposed=true",
    ]:
        require(forbidden not in combined, f"forbidden claim found {forbidden}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_SCOPE_REFRESH_APPROVAL_INTAKE_V0_1.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_scope_refresh_approval/scope_refresh_approval_input.template.json",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_scope_refresh_approval/scope_refresh_approval_intake.local.json",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_scope_refresh_approval/scope_refresh_approval_copy_card.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_scope_refresh_approval/scope_refresh_approval_copy_card.html",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_scope_refresh_approval/scope_refresh_approval_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_SCOPE_REFRESH_APPROVAL_INTAKE_GATE.md",
        "/scripts/saee_commercial_matrix_update_scope_refresh_approval_intake.py",
        "/scripts/saee_commercial_matrix_update_scope_refresh_approval_intake_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    entry = read_json(ROOT / "agent-index.json").get("commercial_matrix_update_scope_refresh_approval_intake_v0_1")
    require(isinstance(entry, dict), "agent-index entry missing")
    for key in [
        "status", "scope_refresh_packet_ready", "previous_target_count",
        "refreshed_target_count", "not_cataloged_blocker_ids",
        "exact_phrase_required", "phrase_matches_exactly",
        "human_filled_scope_approval_written",
        "ready_for_separate_active_request_replacement_validator",
        "separate_active_request_replacement_step_required",
        "separate_matrix_execution_approval_still_required",
        "active_matrix_request_replaced", "approval_scope_changed",
        "matrix_update_executed", "blocker_closure_authorized",
        "blockers_closed_by_scope_approval_intake", "production_ready",
        "customer_validated", "private_core_exposed",
    ]:
        require(entry.get(key) == payload.get(key), f"agent-index {key} mismatch")

    runner_text = RUNNER.read_text(encoding="utf-8")
    for forbidden in ["requests.", "urllib.", "httpx.", "webbrowser", "selenium"]:
        require(forbidden not in runner_text, f"runner must not call external services: {forbidden}")

    print(
        "SAEE_COMMERCIAL_MATRIX_UPDATE_SCOPE_REFRESH_APPROVAL_INTAKE_SMOKE: PASS "
        "status=waiting_for_exact_human_scope_refresh_phrase active_request_replaced=false "
        "matrix_update_executed=false blockers_closed=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
