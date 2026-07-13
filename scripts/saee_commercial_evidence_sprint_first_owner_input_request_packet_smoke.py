#!/usr/bin/env python3
"""Smoke check for the first-owner input request packet."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_commercial_evidence_sprint_first_owner_input_request_packet.py"
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
OUTPUT_JSON = SPRINT_DIR / "first_owner_input_request_packet.local.json"
OUTPUT_MD = SPRINT_DIR / "first_owner_input_request_packet.md"
OUTPUT_CSV = SPRINT_DIR / "first_owner_input_request_packet.csv"
OUTPUT_HTML = SPRINT_DIR / "first_owner_input_request_packet.html"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_REQUEST_PACKET_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_REQUEST_PACKET_RECOMMENDATION_GATE.md"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_REQUEST_PACKET_SMOKE: "
            "FAIL: " + message
        )


def read_json(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"{path} must contain an object")
    return data


def main() -> None:
    require(RUNNER.exists(), "runner missing")
    result = subprocess.run(
        [sys.executable, str(RUNNER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    require(
        "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_REQUEST_PACKET: PASS"
        in result.stdout,
        "runner did not print PASS",
    )
    for path in [OUTPUT_JSON, OUTPUT_MD, OUTPUT_CSV, OUTPUT_HTML, TOP_DOC, GATE]:
        require(path.exists(), f"{path} missing")

    payload = read_json(OUTPUT_JSON)
    expected = {
        "first_owner_input_request_packet_v0_1": True,
        "packet_type": "saee_commercial_evidence_sprint_first_owner_input_request_packet",
        "packet_version": "v0.1",
        "status": "hold_human_first_owner_input_request_required",
        "action_id": "NEXT-001",
        "sequence_step_id": "SEQ-001",
        "first_blocker_id": "support_contact",
        "request_packet_ready": True,
        "source_first_owner_input_request_html": "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_request_packet.html",
        "source_first_owner_input_template": "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input.template.json",
        "recommended_human_filled_input_path": "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input.human_filled.local.json",
        "local_static_first_owner_input_request_html": True,
        "browser_readable_first_owner_input_request": True,
        "copy_ready_blank_json_template_in_html": True,
        "human_input_required": True,
        "required_human_field_count": 5,
        "completed_human_field_count": 0,
        "missing_human_field_count": 5,
        "ready_for_first_owner_input_validator": False,
        "ready_for_evidence_collection": False,
        "ready_for_separate_evidence_collection_request": False,
        "separate_validator_required": True,
        "separate_evidence_collection_request_required": True,
        "blockers_closed_by_request_packet": 0,
        "owner_assigned_by_codex": False,
        "owner_contacted_by_codex": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "task_candidates_executed": False,
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
        "external_ai_assistant_tested": False,
        "public_sdk_released": False,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")

    fields = payload.get("required_human_fields")
    require(isinstance(fields, list), "required_human_fields must be a list")
    require(len(fields) == 5, "required_human_fields must contain 5 fields")
    for field in [
        "assigned_human_owner",
        "owner_contact_reference",
        "target_review_date",
        "owner_acknowledged_scope",
        "human_approval_reference",
    ]:
        require(field in fields, "missing required field " + field)

    with OUTPUT_CSV.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 5, "CSV must contain five request rows")
    require(all(row["provided"] == "false" for row in rows), "CSV rows must default not provided")

    command = payload.get("next_generation_command_template")
    require(isinstance(command, str), "next_generation_command_template must be a string")
    require(command.strip(), "next_generation_command_template must not be blank")
    for token in [
        "scripts/saee_commercial_evidence_sprint_owner_assignment_completion_helper.py",
        "--single-blocker-id support_contact",
        "--assigned-human-owner",
        "--owner-contact-reference",
        "--target-review-date",
        "--owner-acknowledged-scope true",
        "--human-approval-reference",
        "owner_assignment_input.human_filled.local.json",
    ]:
        require(token in command, "command template missing " + token)
    require(
        payload.get("next_generation_command_template_available") is True,
        "next_generation_command_template_available must be true",
    )

    html_text = OUTPUT_HTML.read_text(encoding="utf-8")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [OUTPUT_MD, TOP_DOC, GATE]
    ) + "\n" + html_text
    for token in [
        "first_owner_input_request_packet_v0_1: true",
        "hold_human_first_owner_input_request_required",
        "local_static_first_owner_input_request_html: true",
        "browser_readable_first_owner_input_request: true",
        "copy_ready_blank_json_template_in_html: true",
        "source_first_owner_input_request_html: phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_request_packet.html",
        "source_first_owner_input_template: phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input.template.json",
        "recommended_human_filled_input_path: phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input.human_filled.local.json",
        "required_human_field_count: 5",
        "completed_human_field_count: 0",
        "owner_assigned_by_codex: false",
        "owner_contacted_by_codex: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "blockers_closed_by_request_packet: 0",
        "production_ready: false",
        "answer: recommend",
        "recommend_for_human_first_owner_input_request: true",
        "recommend_for_owner_assignment_by_codex: false",
        "recommend_for_evidence_collection: false",
        "recommend_for_execution: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_production: false",
        "scripts/saee_commercial_evidence_sprint_owner_assignment_completion_helper.py",
        "--single-blocker-id support_contact",
        "SAEE 支持联系人负责人填写页",
        "先指定“支持联系人”的真人负责人",
        "负责人姓名或内部代号",
        "空白 JSON 模板",
        "first_owner_input.human_filled.local.json",
        "不要写客户隐私",
        "owner_assigned_by_codex:</strong> false",
        "owner_contacted_by_codex:</strong> false",
        "execution_authorized:</strong> false",
        "evidence_collection_authorized:</strong> false",
        "production_ready:</strong> false",
    ]:
        require(token in combined, "missing token " + token)
    for token in ["<script", "fetch(", "XMLHttpRequest", "http://", "https://", "mailto:"]:
        require(token not in html_text, "HTML contains forbidden token " + token)

    runner = RUNNER.read_text(encoding="utf-8")
    for forbidden in [
        "os.environ",
        "os.getenv",
        "getenv(",
        "environ[",
        "requests.",
        "urllib",
        "subprocess.run",
    ]:
        require(forbidden not in runner, "runner contains forbidden token " + forbidden)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_REQUEST_PACKET_V0_1.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_request_packet.local.json",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_request_packet.html",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_request_packet.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_request_packet.csv",
        "/docs/strategy/SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_REQUEST_PACKET_RECOMMENDATION_GATE.md",
        "/scripts/saee_commercial_evidence_sprint_first_owner_input_request_packet.py",
        "/scripts/saee_commercial_evidence_sprint_first_owner_input_request_packet_smoke.py",
    ]:
        require(path in llms, "llms.txt missing " + path)

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("commercial_evidence_sprint_first_owner_input_request_packet_v0_1")
    require(isinstance(entry, dict), "agent-index entry missing")
    for key, value in expected.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print("SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_REQUEST_PACKET_SMOKE: PASS")


if __name__ == "__main__":
    main()
