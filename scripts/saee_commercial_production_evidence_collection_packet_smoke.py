#!/usr/bin/env python3
"""Smoke check for the SAEE commercial production evidence collection packet."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_production_evidence_collection_packet"
)
OUTPUT_JSON = OUTPUT_DIR / "commercial_production_evidence_collection_packet.local.json"
OUTPUT_MD = OUTPUT_DIR / "commercial_production_evidence_collection_packet.md"
OUTPUT_CHECKLIST = OUTPUT_DIR / "commercial_production_evidence_collection_checklist.md"
OUTPUT_CSV = OUTPUT_DIR / "commercial_production_evidence_collection.csv"
README_PATH = OUTPUT_DIR / "README.md"
DOC_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/COMMERCIAL_PRODUCTION_EVIDENCE_COLLECTION_PACKET_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_COMMERCIAL_PRODUCTION_EVIDENCE_COLLECTION_PACKET_RECOMMENDATION_GATE.md"
)


def fail(message: str) -> None:
    print(
        f"SAEE_COMMERCIAL_PRODUCTION_EVIDENCE_COLLECTION_PACKET_SMOKE: FAIL {message}",
        file=sys.stderr,
    )
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    for path in [
        OUTPUT_JSON,
        OUTPUT_MD,
        OUTPUT_CHECKLIST,
        OUTPUT_CSV,
        README_PATH,
        DOC_PATH,
        GATE_PATH,
    ]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    packet = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
    require(
        packet.get("packet_type")
        == "saee_commercial_production_evidence_collection_packet",
        "wrong packet type",
    )
    require(packet.get("packet_version") == "0.1", "wrong packet version")
    require(packet.get("status") == "hold", "status must hold")
    require(packet.get("phase_count") == 5, "expected 5 phases")
    require(packet.get("target_blocker_count") == 24, "expected 24 blockers")
    require(
        packet.get("total_required_evidence_item_count") == 149,
        "expected 149 required evidence items",
    )
    require(
        packet.get("total_local_public_shell_present_count") == 37,
        "expected 37 local public-shell items",
    )
    require(
        packet.get("total_missing_production_evidence_count") == 112,
        "expected 112 missing production evidence items",
    )
    require(
        packet.get("accepted_for_blocker_closure_count") == 0,
        "no evidence can be accepted for closure",
    )
    require(packet.get("blockers_ready_to_close") == [], "no blocker ready to close")
    require(packet.get("blockers_closed_by_packet") == 0, "packet must close zero blockers")
    require(packet.get("manual_collection_required") is True, "manual collection required")
    require(packet.get("human_review_required") is True, "human review required")
    require(
        packet.get("separate_execution_approval_required") is True,
        "separate execution approval required",
    )

    required_false_flags = [
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "private_core_exposed",
        "product_launched",
        "production_ready",
        "customer_validated",
        "customer_contacted",
        "public_sdk_released",
        "external_calls_made",
        "external_model_api_called",
        "external_ai_assistant_tested",
        "execution_authorized",
        "evidence_collection_authorized",
        "task_candidates_executed",
        "customer_contacted_by_codex",
        "vendor_contacted_by_codex",
        "support_vendor_contacted_by_codex",
        "monitoring_vendor_contacted_by_codex",
        "alert_provider_contacted_by_codex",
        "payment_provider_contacted_by_codex",
        "legal_counsel_contacted_by_codex",
        "tax_advisor_contacted_by_codex",
        "security_reviewer_contacted_by_codex",
        "pilot_executed_by_codex",
        "customer_feedback_collected_by_codex",
        "production_claim_added",
        "launch_claim_added",
        "revenue_claim_added",
    ]
    drifted = [flag for flag in required_false_flags if packet.get(flag) is not False]
    require(not drifted, "false boundary flags drifted: " + ", ".join(drifted))

    queue = packet.get("evidence_collection_queue", [])
    require(len(queue) == 149, "queue must have 149 rows")
    record_ids = [row.get("collection_record_id") for row in queue]
    require(len(set(record_ids)) == 149, "collection record ids must be unique")
    require(record_ids[0] == "ECP-001", "first record id changed")
    require(record_ids[-1] == "ECP-149", "last record id changed")
    for row in queue:
        require(row.get("accepted_for_blocker_closure") is False, "row closes blocker")
        require(row.get("human_review_required") is True, "row must require review")
        require(row.get("manual_collection_required") is True, "row must be manual")
        require(row.get("execution_authorized") is False, "row authorizes execution")
        require(
            row.get("evidence_collection_authorized") is False,
            "row authorizes collection",
        )
        require(
            row.get("requires_separate_execution_request") is True,
            "row must require separate request",
        )
        forbidden = set(row.get("must_not_touch", []))
        for token in ["runtime", "backend", "kernel", "api_schema", "private_core"]:
            require(token in forbidden, f"row missing forbidden token {token}")

    phase_summaries = packet.get("phase_summaries", [])
    require(len(phase_summaries) == 5, "phase summary count changed")
    expected_phase_totals = {
        1: (33, 16, 17),
        2: (26, 8, 18),
        3: (45, 10, 35),
        4: (33, 2, 31),
        5: (12, 1, 11),
    }
    for phase in phase_summaries:
        actual = (
            phase.get("required_evidence_item_count"),
            phase.get("local_public_shell_present_count"),
            phase.get("missing_production_evidence_count"),
        )
        require(
            actual == expected_phase_totals.get(phase.get("phase_number")),
            f"phase {phase.get('phase_number')} totals changed",
        )
        require(phase.get("blockers_closed_by_audit") == 0, "phase closed blockers")
        require(phase.get("execution_authorized") is False, "phase authorizes execution")
        require(
            phase.get("evidence_collection_authorized") is False,
            "phase authorizes evidence collection",
        )

    with OUTPUT_CSV.open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    require(len(csv_rows) == 149, "CSV must have 149 rows")

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [OUTPUT_MD, OUTPUT_CHECKLIST, README_PATH, DOC_PATH, GATE_PATH]
    )
    required_phrases = [
        "manual production evidence collection queue",
        "No customer contact",
        "No vendor contact",
        "No runtime, kernel, API schema, or private-core modification",
        "No blocker closure",
        "recommend_for_evidence_collection_authorization: false",
        "recommend_for_execution_authorization: false",
        "recommend_for_blocker_closure: false",
        "production_ready: false",
        "product_launched: false",
        "customer_validated: false",
        "private_core_exposed: false",
    ]
    missing_phrases = [phrase for phrase in required_phrases if phrase not in combined]
    require(not missing_phrases, "missing boundary phrases: " + ", ".join(missing_phrases))

    forbidden_tokens = [
        "production_ready: true",
        '"production_ready": true',
        "product_launched: true",
        '"product_launched": true',
        "customer_validated: true",
        '"customer_validated": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "customer_contacted: true",
        '"customer_contacted": true',
        "vendor_contacted_by_codex: true",
        '"vendor_contacted_by_codex": true',
        "payment_provider_contacted_by_codex: true",
        "legal_counsel_contacted_by_codex: true",
        "tax_advisor_contacted_by_codex: true",
        "security_reviewer_contacted_by_codex: true",
        "execution_authorized: true",
        '"execution_authorized": true',
        "evidence_collection_authorized: true",
        '"evidence_collection_authorized": true',
        "blockers_closed_by_packet: 1",
        '"blockers_closed_by_packet": 1',
        "recommend_for_blocker_closure: true",
        "recommend_for_evidence_collection_authorization: true",
        "recommend_for_execution_authorization: true",
    ]
    found = [token for token in forbidden_tokens if token in combined]
    require(not found, "forbidden claims present: " + ", ".join(found))

    print(
        "SAEE_COMMERCIAL_PRODUCTION_EVIDENCE_COLLECTION_PACKET_SMOKE: PASS "
        f"required_items={packet['total_required_evidence_item_count']} "
        f"local_public_shell={packet['total_local_public_shell_present_count']} "
        f"missing_production={packet['total_missing_production_evidence_count']} "
        f"blockers_closed_by_packet={packet['blockers_closed_by_packet']}"
    )


if __name__ == "__main__":
    main()
