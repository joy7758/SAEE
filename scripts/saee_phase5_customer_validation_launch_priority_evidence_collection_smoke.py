#!/usr/bin/env python3
"""Smoke check for Phase 5 customer validation/launch priority collection."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/phase_5_customer_validation_launch_priority_evidence_collection"
)
OUTPUT_JSON = OUTPUT_DIR / "phase_5_customer_validation_launch_priority_evidence_collection.local.json"
OUTPUT_MD = OUTPUT_DIR / "phase_5_customer_validation_launch_priority_evidence_collection.md"
OUTPUT_CSV = OUTPUT_DIR / "phase_5_customer_validation_launch_priority_evidence_collection.csv"
OUTPUT_CHECKLIST = OUTPUT_DIR / "phase_5_customer_validation_launch_priority_collection_checklist.md"
OUTPUT_TEMPLATE = OUTPUT_DIR / "phase_5_customer_validation_launch_evidence_input.priority.template.json"
OUTPUT_BOUNDARY = OUTPUT_DIR / "phase_5_customer_validation_launch_priority_boundary_audit.md"
README_PATH = OUTPUT_DIR / "README.md"
DOC_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/PHASE_5_CUSTOMER_VALIDATION_LAUNCH_PRIORITY_EVIDENCE_COLLECTION_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_PHASE_5_CUSTOMER_VALIDATION_LAUNCH_PRIORITY_EVIDENCE_COLLECTION_RECOMMENDATION_GATE.md"
)

TARGET_BLOCKERS = {"pilot_results", "customer_validated"}


def fail(message: str) -> None:
    print(
        f"SAEE_PHASE5_CUSTOMER_VALIDATION_LAUNCH_PRIORITY_EVIDENCE_COLLECTION_SMOKE: FAIL {message}",
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
        OUTPUT_CSV,
        OUTPUT_CHECKLIST,
        OUTPUT_TEMPLATE,
        OUTPUT_BOUNDARY,
        README_PATH,
        DOC_PATH,
        GATE_PATH,
    ]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    packet = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
    template = json.loads(OUTPUT_TEMPLATE.read_text(encoding="utf-8"))

    require(
        packet.get("packet_type")
        == "saee_phase_5_customer_validation_launch_priority_evidence_collection",
        "wrong packet type",
    )
    require(packet.get("packet_version") == "0.1", "wrong packet version")
    require(packet.get("status") == "ready_for_human_review_not_execution", "wrong status")
    require(packet.get("phase_id") == "phase_5_customer_validation_and_launch_review", "wrong phase")
    require(set(packet.get("target_blockers", [])) == TARGET_BLOCKERS, "target blockers changed")
    require(packet.get("target_blocker_count") == 2, "expected 2 blockers")
    require(packet.get("required_evidence_item_count") == 12, "expected 12 evidence items")
    require(packet.get("local_public_shell_present_count") == 1, "expected 1 local item")
    require(packet.get("missing_production_evidence_count") == 11, "expected 11 missing items")
    require(packet.get("accepted_for_blocker_closure_count") == 0, "must accept zero closures")
    require(packet.get("blockers_closed_by_collection") == 0, "must close zero blockers")
    require(packet.get("blockers_ready_to_close") == [], "no blocker ready to close")
    require(packet.get("human_review_required") is True, "human review required")
    require(packet.get("manual_collection_required") is True, "manual collection required")
    require(packet.get("separate_execution_approval_required") is True, "separate approval required")

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
        "customer_contacted_by_codex",
        "automated_customer_contact",
        "unsolicited_customer_contact",
        "customer_data_collected",
        "customer_data_processing_started",
        "customer_data_processed",
        "customer_secrets_collected",
        "public_sdk_released",
        "external_calls_made",
        "external_model_api_called",
        "external_ai_assistant_tested",
        "execution_authorized",
        "evidence_collection_authorized",
        "codex_executed_pilot",
        "pilot_session_started",
        "pilot_session_completed",
        "pilot_results_recorded",
        "feedback_form_completed",
        "permission_to_use_feedback_recorded",
        "public_validation_claim_published",
        "case_study_published",
        "testimonial_published",
        "product_market_fit_claimed",
        "production_readiness_claimed",
        "launch_approved",
        "public_launch_claim_added",
        "revenue_validated",
        "user_upload_enabled",
        "codex_inferred_missing_evidence",
    ]
    drifted = [flag for flag in required_false_flags if packet.get(flag) is not False]
    require(not drifted, "boundary flags drifted: " + ", ".join(drifted))

    rows = packet.get("priority_rows", [])
    require(len(rows) == 12, "priority row count must be 12")
    require(len({row.get("phase_5_record_id") for row in rows}) == 12, "record ids not unique")
    require(rows[0].get("phase_5_record_id") == "P5-ECP-001", "first record id changed")
    require(rows[-1].get("phase_5_record_id") == "P5-ECP-012", "last record id changed")
    require({row.get("blocker_id") for row in rows} == TARGET_BLOCKERS, "row blockers changed")
    for row in rows:
        require(row.get("accepted_for_blocker_closure") is False, "row closes blocker")
        require(row.get("human_review_required") is True, "row must require review")
        require(row.get("manual_collection_required") is True, "row must be manual")
        require(row.get("execution_authorized") is False, "row authorizes execution")
        require(row.get("evidence_collection_authorized") is False, "row authorizes collection")
        require(row.get("requires_separate_execution_request") is True, "row needs separate request")
        must_not_touch = set(row.get("must_not_touch", []))
        for token in ["runtime", "backend", "kernel", "api_schema", "private_core"]:
            require(token in must_not_touch, f"row missing must_not_touch {token}")

    require(
        template.get("phase_5_customer_validation_launch_priority_evidence_collection_v0_1")
        is True,
        "template missing priority marker",
    )
    evidence_review = template.get("evidence_review", {})
    source_notes = template.get("source_notes_by_key", {})
    require(len(evidence_review) == 12, "template evidence_review must have 12 keys")
    require(len(source_notes) == 12, "template source_notes_by_key must have 12 keys")
    require(all(value is False for value in evidence_review.values()), "template must not prefill evidence")
    require(all(value == "" for value in source_notes.values()), "template must not prefill notes")
    key_order = template.get("priority_evidence_key_order", [])
    require(len(key_order) == 12, "priority key order must have 12 keys")
    require(set(key_order) == set(evidence_review), "priority key order does not match keys")
    collection_map = template.get("priority_collection_map_by_key", {})
    require(set(collection_map) == set(evidence_review), "collection map does not match keys")

    with OUTPUT_CSV.open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    require(len(csv_rows) == 12, "CSV must contain 12 rows")

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [OUTPUT_MD, OUTPUT_CHECKLIST, OUTPUT_BOUNDARY, README_PATH, DOC_PATH, GATE_PATH]
    )
    required_phrases = [
        "human-fillable",
        "No blocker closure",
        "recommend_for_evidence_collection_authorization: false",
        "recommend_for_execution_authorization: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_customer_contact: false",
        "recommend_for_pilot_execution: false",
        "recommend_for_feedback_inference: false",
        "recommend_for_customer_data_collection: false",
        "recommend_for_customer_validation_claim: false",
        "recommend_for_case_study_publication: false",
        "recommend_for_testimonial_publication: false",
        "recommend_for_product_market_fit_claim: false",
        "recommend_for_launch_approval: false",
        "production_ready: false",
        "customer_validated: false",
        "private_core_exposed: false",
        "revenue_validated: false",
    ]
    missing = [phrase for phrase in required_phrases if phrase not in combined]
    require(not missing, "missing boundary phrases: " + ", ".join(missing))

    forbidden_tokens = [
        "production_ready: true",
        '"production_ready": true',
        "product_launched: true",
        '"product_launched": true',
        "customer_validated: true",
        '"customer_validated": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "revenue_validated: true",
        '"revenue_validated": true',
        "customer_contacted_by_codex: true",
        "automated_customer_contact: true",
        "codex_executed_pilot: true",
        "pilot_session_started: true",
        "pilot_session_completed: true",
        "pilot_results_recorded: true",
        "feedback_form_completed: true",
        "customer_data_collected: true",
        "customer_data_processing_started: true",
        "customer_data_processed: true",
        "customer_secrets_collected: true",
        "permission_to_use_feedback_recorded: true",
        "public_validation_claim_published: true",
        "case_study_published: true",
        "testimonial_published: true",
        "product_market_fit_claimed: true",
        "launch_approved: true",
        "public_launch_claim_added: true",
        "execution_authorized: true",
        '"execution_authorized": true',
        "evidence_collection_authorized: true",
        '"evidence_collection_authorized": true',
        "recommend_for_evidence_collection_authorization: true",
        "recommend_for_execution_authorization: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_customer_contact: true",
        "recommend_for_pilot_execution: true",
        "recommend_for_feedback_inference: true",
        "recommend_for_customer_data_collection: true",
        "recommend_for_customer_validation_claim: true",
        "recommend_for_case_study_publication: true",
        "recommend_for_testimonial_publication: true",
        "recommend_for_product_market_fit_claim: true",
        "recommend_for_launch_approval: true",
    ]
    found = [token for token in forbidden_tokens if token in combined]
    require(not found, "forbidden claims found: " + ", ".join(found))

    print("SAEE_PHASE5_CUSTOMER_VALIDATION_LAUNCH_PRIORITY_EVIDENCE_COLLECTION_SMOKE: PASS")


if __name__ == "__main__":
    main()
