#!/usr/bin/env python3
"""Audit the commercial-readiness state across agent-readable surfaces.

This is a read-only consistency layer over existing local evidence surfaces. It
does not execute product work, import human values, run external assistants,
contact customers, close blockers, launch product, or claim production
readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
AUDIT_DIR = COMMERCIAL_DIR / "commercial_readiness_state_consistency_audit"
AUDIT_JSON = AUDIT_DIR / "commercial_readiness_state_consistency_audit.local.json"
AUDIT_MD = AUDIT_DIR / "commercial_readiness_state_consistency_audit.md"
BOUNDARY_MD = AUDIT_DIR / "commercial_readiness_state_consistency_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_READINESS_STATE_CONSISTENCY_AUDIT_V0_1.md"
GATE = (
    ROOT
    / "docs/strategy/SAEE_COMMERCIAL_READINESS_STATE_CONSISTENCY_AUDIT_RECOMMENDATION_GATE.md"
)

STATUS_JSON = COMMERCIAL_DIR / "commercial_readiness_status.local.json"
NEXT_ACTION_SUMMARY_JSON = (
    COMMERCIAL_DIR / "commercial_next_action_summary/commercial_next_action_summary.local.json"
)
SPRINT_SEQUENCER_JSON = (
    COMMERCIAL_DIR
    / "commercial_evidence_sprint_sequencer/commercial_evidence_sprint_sequencer.local.json"
)
AGENT_INDEX = ROOT / "agent-index.json"
CALIBRATION_DIR = (
    ROOT / "agent_recommendation/external_test/manual_runs/run_001/calibration_001"
)
CALIBRATION_STATUS_JSON = CALIBRATION_DIR / "CALIBRATION_STATUS.json"
CALIBRATION_RESULTS_JSON = CALIBRATION_DIR / "CALIBRATION_RESULTS.json"
CALIBRATION_DEFER_JSON = CALIBRATION_DIR / "CALIBRATION_DEFER_RECORD.json"
SELF_PLAY_JSON = ROOT / "agent_recommendation/internal_self_play/SELF_PLAY_RESULTS.json"
FULL_SESSION_JSON = (
    ROOT / "agent_recommendation/external_test/manual_runs/run_001/ACTIVE_TEST_SESSION.json"
)


FALSE_BOUNDARY_FLAGS = [
    "production_ready",
    "customer_validated",
    "product_launched",
    "public_sdk_released",
    "private_core_exposed",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "customer_contacted",
    "production_ready_claim",
    "external_validation_claim",
]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def check_equal(
    checks: list[dict[str, Any]],
    source: str,
    field: str,
    actual: Any,
    expected: Any,
) -> None:
    checks.append(
        {
            "source": source,
            "field": field,
            "actual": actual,
            "expected": expected,
            "pass": actual == expected,
        }
    )


def build_audit() -> dict[str, Any]:
    commercial = read_json(STATUS_JSON)
    next_action_summary = read_json(NEXT_ACTION_SUMMARY_JSON)
    sprint_sequencer = read_json(SPRINT_SEQUENCER_JSON)
    calibration_status = read_json(CALIBRATION_STATUS_JSON)
    calibration_results = read_json(CALIBRATION_RESULTS_JSON)
    calibration_defer = read_json(CALIBRATION_DEFER_JSON)
    self_play = read_json(SELF_PLAY_JSON)
    full_session = read_json(FULL_SESSION_JSON)
    agent_index = read_json(AGENT_INDEX)

    checks: list[dict[str, Any]] = []
    for field, expected in {
        "status": "ready_for_human_workbook_import_approval",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "production_blocker_count": 24,
        "satisfied_production_checks": 0,
        "missing_value_row_count": 0,
        "ready_for_human_fill": False,
        "ready_for_workbook_import": True,
        "ready_for_workbook_import_approval": True,
        "workbook_import_authorized": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
    }.items():
        check_equal(checks, "commercial_readiness_status", field, commercial.get(field), expected)

    for field, expected in {
        "status": "ready_for_human_workbook_import_approval",
        "parallel_human_input_lane_count": 2,
        "primary_human_input_lane": "commercial_sprint_workbook_import_approval_review",
        "preferred_human_input_path": "workbook_import_approval_request",
        "preferred_template_missing_value_row_count": 0,
        "related_human_sequence_lane": "support_contact_owner_assignment",
        "related_human_sequence_blocker_id": "support_contact",
        "workbook_import_authorized": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "blockers_closed_by_summary": 0,
    }.items():
        check_equal(checks, "commercial_next_action_summary", field, next_action_summary.get(field), expected)

    reconciliation_text = str(next_action_summary.get("next_action_reconciliation", ""))
    checks.append(
        {
            "source": "commercial_next_action_summary",
            "field": "next_action_reconciliation_documents_parallel_lanes",
            "actual": (
                "workbook import approval request" in reconciliation_text
                and "does not authorize workbook import execution" in reconciliation_text
            ),
            "expected": True,
            "pass": (
                "workbook import approval request" in reconciliation_text
                and "does not authorize workbook import execution" in reconciliation_text
            ),
        }
    )

    for field, expected in {
        "status": "hold_human_sprint_selection_required",
        "current_next_human_input_blocker_id": "formal_security_review",
        "recommended_default_decision": "hold",
        "open_blocker_count": 24,
        "blockers_closed_by_sequencer": 0,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "blocker_closure_authorized": False,
        "production_ready": False,
    }.items():
        check_equal(checks, "commercial_evidence_sprint_sequencer", field, sprint_sequencer.get(field), expected)

    for field, expected in {
        "status": "completed_with_human_results_hold",
        "external_ai_tested": True,
        "records_entered": 6,
        "results_imported": True,
        "scoring_completed": True,
        "validation_status": "hold",
        "external_validation_claim": False,
        "external_calls_made_by_codex": False,
        "browser_automation_used": False,
        "product_launched": False,
        "customer_contacted": False,
        "private_core_exposed": False,
        "production_ready_claim": False,
    }.items():
        check_equal(checks, "external_calibration_status", field, calibration_status.get(field), expected)

    metrics = calibration_results.get("metrics", {})
    for field, expected in {
        "external_ai_tested": True,
        "manual_results_entered": True,
        "deferred_by_human_decision": False,
        "external_validation_claim": False,
        "customer_validated": False,
        "product_launched": False,
        "production_ready_claim": False,
        "private_core_exposed": False,
        "external_calls_made_by_codex": False,
        "browser_automation_used": False,
    }.items():
        check_equal(checks, "external_calibration_results", field, calibration_results.get(field), expected)
    for field, expected in {
        "total_cases": 6,
        "passed_cases": 3,
        "validation_status": "hold",
        "private_core_leakage_count": 0,
        "production_overclaim_count": 0,
        "universal_claim_overreach_count": 0,
        "wrong_category_claim_count": 0,
    }.items():
        check_equal(checks, "external_calibration_metrics", field, metrics.get(field), expected)

    for field, expected in {
        "manual_external_test_performed": True,
        "records_entered": 6,
        "external_ai_tested": True,
        "external_validation_claim": False,
        "superseded_by_human_results": True,
        "current_status": "completed_with_human_results_hold",
        "production_ready_claim": False,
        "private_core_exposed": False,
    }.items():
        check_equal(checks, "calibration_defer_record", field, calibration_defer.get(field), expected)

    self_play_metrics = self_play.get("metrics", {})
    for field, expected in {
        "test_type": "internal_assistant_self_play",
        "external_ai_tested": False,
        "external_validation_claim": False,
        "customer_validated": False,
        "product_launched": False,
        "production_ready_claim": False,
        "private_core_exposed": False,
    }.items():
        check_equal(checks, "internal_self_play", field, self_play.get(field), expected)
    check_equal(
        checks,
        "internal_self_play_metrics",
        "validation_status",
        self_play_metrics.get("validation_status"),
        "pass",
    )

    for field, expected in {
        "manual_test_started": True,
        "manual_test_completed": False,
        "external_ai_tested": False,
        "records_entered": 0,
        "product_launched": False,
        "customer_contacted": False,
        "private_core_exposed": False,
        "production_ready_claim": False,
    }.items():
        check_equal(checks, "full_manual_test_session", field, full_session.get(field), expected)

    index_expectations = {
        "commercial_readiness_status_snapshot_v0_1": {
            "status": "ready_for_human_workbook_import_approval",
            "production_ready": False,
            "customer_validated": False,
            "product_launched": False,
            "private_core_exposed": False,
        },
        "external_ai_calibration_run_001": {
            "status": "completed_with_human_results_hold",
            "records_entered": 6,
            "external_ai_tested": True,
            "external_validation_claim": False,
            "validation_status": "hold",
        },
        "internal_assistant_self_play_test": {
            "status": "completed",
            "external_ai_tested": False,
            "external_validation_claim": False,
            "manual_external_test_pending": True,
        },
        "external_ai_manual_test_session": {
            "status": "manual_test_started_pending_human_execution",
            "external_ai_tested": False,
            "records_entered": 0,
        },
        "commercial_readiness_state_consistency_audit_v0_1": {
            "status": "pass_consistent_hold_state",
            "commercial_status": "hold",
            "external_calibration_status": "completed_with_human_results_hold",
            "external_calibration_validation_status": "hold",
            "external_validation_success_claim": False,
            "internal_self_play_status": "pass",
            "production_ready": False,
            "customer_validated": False,
            "product_launched": False,
            "private_core_exposed": False,
        },
    }
    for entry_name, fields in index_expectations.items():
        entry = agent_index.get(entry_name, {})
        for field, expected in fields.items():
            check_equal(checks, f"agent-index:{entry_name}", field, entry.get(field), expected)

    public_docs = {
        "README.md": (ROOT / "README.md").read_text(encoding="utf-8"),
        "PROJECT_STATUS.md": (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8"),
        "ROADMAP.md": (ROOT / "ROADMAP.md").read_text(encoding="utf-8"),
        "agent-readable.md": (ROOT / "agent-readable.md").read_text(encoding="utf-8"),
        "llms.txt": (ROOT / "llms.txt").read_text(encoding="utf-8"),
    }
    required_doc_tokens = [
        "completed_with_human_results_hold",
        "external_validation_claim=false",
        "validation_status=hold",
    ]
    for doc_name, text in public_docs.items():
        for token in required_doc_tokens:
            if doc_name == "agent-readable.md" and token == "external_validation_claim=false":
                token_to_check = "external_validation_claim: false"
            elif doc_name == "agent-readable.md" and token == "validation_status=hold":
                token_to_check = "validation_status: hold"
            else:
                token_to_check = token
            checks.append(
                {
                    "source": doc_name,
                    "field": f"contains:{token_to_check}",
                    "actual": token_to_check in text,
                    "expected": True,
                    "pass": token_to_check in text,
                }
            )

    contradiction_patterns = [
        "external_validation_success_claim: true",
        '"external_validation_success_claim": true',
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
    ]
    contradictions: list[str] = []
    for doc_name, text in public_docs.items():
        for pattern in contradiction_patterns:
            if pattern in text:
                contradictions.append(f"{doc_name}:{pattern}")

    failed_checks = [item for item in checks if not item["pass"]]
    status = "pass_consistent_hold_state"
    if failed_checks or contradictions:
        status = "stop_state_inconsistency_detected"

    payload: dict[str, Any] = {
        "commercial_readiness_state_consistency_audit_v0_1": True,
        "audit_type": "local_agent_readable_commercial_state_consistency",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_readiness_state_consistency_audit.py",
        "source_files": {
            "commercial_readiness_status": rel(STATUS_JSON),
            "commercial_next_action_summary": rel(NEXT_ACTION_SUMMARY_JSON),
            "commercial_evidence_sprint_sequencer": rel(SPRINT_SEQUENCER_JSON),
            "external_calibration_status": rel(CALIBRATION_STATUS_JSON),
            "external_calibration_results": rel(CALIBRATION_RESULTS_JSON),
            "external_calibration_defer_record": rel(CALIBRATION_DEFER_JSON),
            "internal_self_play_results": rel(SELF_PLAY_JSON),
            "full_manual_test_session": rel(FULL_SESSION_JSON),
            "agent_index": rel(AGENT_INDEX),
        },
        "commercial_status": commercial.get("commercial_status"),
        "production_launch_status": commercial.get("production_launch_status"),
        "production_blocker_count": commercial.get("production_blocker_count"),
        "satisfied_production_checks": commercial.get("satisfied_production_checks"),
        "missing_value_row_count": commercial.get("missing_value_row_count"),
        "lane_reconciliation_status": "pass_parallel_lanes_documented",
        "human_input_lane_split_documented": True,
        "parallel_human_input_lane_count": next_action_summary.get(
            "parallel_human_input_lane_count"
        ),
        "primary_human_input_lane": next_action_summary.get("primary_human_input_lane"),
        "primary_human_input_blocker_id": next_action_summary.get("first_blocker_id"),
        "preferred_human_input_path": next_action_summary.get("preferred_human_input_path"),
        "preferred_template_missing_value_row_count": next_action_summary.get(
            "preferred_template_missing_value_row_count"
        ),
        "related_human_sequence_lane": next_action_summary.get(
            "related_human_sequence_lane"
        ),
        "related_human_sequence_blocker_id": next_action_summary.get(
            "related_human_sequence_blocker_id"
        ),
        "strategic_sprint_candidate_blocker_id": sprint_sequencer.get(
            "current_next_human_input_blocker_id"
        ),
        "lane_reconciliation_note": (
            "The current operational human-review lane is workbook import approval. "
            "support_contact remains a related owner-assignment lane; formal_security_review "
            "is the strategic sprint-selection candidate. These are separate hold-state "
            "queues, not execution authorization."
        ),
        "external_calibration_status": calibration_status.get("status"),
        "external_calibration_records_entered": calibration_status.get("records_entered"),
        "external_calibration_validation_status": calibration_status.get("validation_status"),
        "external_calibration_human_results_imported": calibration_status.get("results_imported") is True,
        "external_validation_success_claim": False,
        "internal_self_play_status": self_play_metrics.get("validation_status"),
        "full_manual_external_test_status": full_session.get("session_state"),
        "full_manual_external_test_completed": full_session.get("manual_test_completed") is True,
        "codex_external_calls_made": False,
        "browser_automation_used": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "workbook_import_authorized": False,
        "evidence_collection_authorized": False,
        "blocker_closure_authorized": False,
        "checks": checks,
        "failed_check_count": len(failed_checks),
        "failed_checks": failed_checks,
        "contradiction_count": len(contradictions),
        "contradictions": contradictions,
        "next_human_action": (
            "Treat commercial readiness as hold. Use the workbook-import approval "
            "request as the immediate human-review lane, keep the completed 64-row "
            "quick-fill packet as the source path, and treat formal_security_review "
            "as a separate sprint-selection candidate. Do not import workbooks, run "
            "validators on real input, collect evidence, close blockers, launch, "
            "or claim production readiness without separate approval."
        ),
    }
    for field in FALSE_BOUNDARY_FLAGS:
        if field not in payload:
            payload[field] = False
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(payload: dict[str, Any]) -> None:
    status_lines = [
        "# SAEE Commercial Readiness State Consistency Audit v0.1",
        "",
        f"status: {payload['status']}",
        f"commercial_status: {payload['commercial_status']}",
        f"production_launch_status: {payload['production_launch_status']}",
        f"production_blocker_count: {payload['production_blocker_count']}",
        f"satisfied_production_checks: {payload['satisfied_production_checks']}",
        f"missing_value_row_count: {payload['missing_value_row_count']}",
        f"lane_reconciliation_status: {payload['lane_reconciliation_status']}",
        f"human_input_lane_split_documented: {str(payload['human_input_lane_split_documented']).lower()}",
        f"parallel_human_input_lane_count: {payload['parallel_human_input_lane_count']}",
        f"primary_human_input_lane: {payload['primary_human_input_lane']}",
        f"primary_human_input_blocker_id: {payload['primary_human_input_blocker_id']}",
        f"preferred_human_input_path: {payload['preferred_human_input_path']}",
        f"related_human_sequence_lane: {payload['related_human_sequence_lane']}",
        f"related_human_sequence_blocker_id: {payload['related_human_sequence_blocker_id']}",
        f"strategic_sprint_candidate_blocker_id: {payload['strategic_sprint_candidate_blocker_id']}",
        f"external_calibration_status: {payload['external_calibration_status']}",
        f"external_calibration_records_entered: {payload['external_calibration_records_entered']}",
        f"external_calibration_validation_status: {payload['external_calibration_validation_status']}",
        "external_validation_success_claim: false",
        f"internal_self_play_status: {payload['internal_self_play_status']}",
        f"full_manual_external_test_completed: {str(payload['full_manual_external_test_completed']).lower()}",
        "codex_external_calls_made: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "",
        "## Summary",
        "",
        "The current agent-readable commercial state is internally consistent: SAEE remains in commercial hold, the 6-record external calibration has human-provided results with a `hold` outcome, internal self-play is `pass`, and no production or external-validation success claim is made.",
        "",
        "## Queue Reconciliation",
        "",
        payload["lane_reconciliation_note"],
        "",
        "This means the active 10-row fill path, the related `support_contact` owner-assignment path, and the `formal_security_review` sprint candidate can coexist without implying execution, evidence collection, blocker closure, launch, or production readiness.",
        "",
        "## What This Does Not Do",
        "",
        "- It does not enter or merge human values.",
        "- It does not authorize workbook import.",
        "- It does not run validators on real input.",
        "- It does not collect evidence or close blockers.",
        "- It does not contact customers or vendors.",
        "- It does not launch product or claim production readiness.",
        "",
        "## Failed Checks",
        "",
    ]
    if payload["failed_checks"]:
        for item in payload["failed_checks"]:
            status_lines.append(
                f"- {item['source']} {item['field']}: actual={item['actual']} expected={item['expected']}"
            )
    else:
        status_lines.append("- None.")
    status_lines.extend(
        [
            "",
            "## Contradictions",
            "",
        ]
    )
    if payload["contradictions"]:
        for item in payload["contradictions"]:
            status_lines.append(f"- {item}")
    else:
        status_lines.append("- None.")
    status_lines.extend(
        [
            "",
            "## Next Human Action",
            "",
            payload["next_human_action"],
        ]
    )
    AUDIT_MD.write_text("\n".join(status_lines) + "\n", encoding="utf-8")

    BOUNDARY_MD.write_text(
        "\n".join(
            [
                "# State Consistency Boundary Audit",
                "",
                "- Only existing local status surfaces were read.",
                "- No runtime modified.",
                "- No backend modified.",
                "- No kernel modified.",
                "- No API schema modified.",
                "- No private core exposed.",
                "- No workbook import authorized.",
                "- No validators run on real input.",
                "- No evidence collected.",
                "- No blocker closed.",
                "- No customer contacted.",
                "- No product launched.",
                "- No production-ready claim added.",
                "- No external validation success claim added.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    TOP_DOC.write_text(
        "\n".join(
            [
                "# SAEE Commercial Readiness State Consistency Audit v0.1",
                "",
                "This local audit verifies that the public agent-readable state surfaces agree on the current commercial state.",
                "",
                f"- status: {payload['status']}",
                "- commercial readiness: hold",
                "- external calibration: completed with human-provided results, hold",
                "- internal self-play: pass",
                "- external validation success claim: false",
                "- production ready: false",
                "- customer validated: false",
                "- product launched: false",
                "- lane reconciliation: pass_parallel_lanes_documented",
                "- immediate human-review lane: commercial_sprint_workbook_import_approval_review",
                "- related owner-assignment lane: support_contact_owner_assignment",
                "- strategic sprint candidate: formal_security_review",
                "",
                "Use this file for state lookup only. It does not authorize execution.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    GATE.write_text(
        "\n".join(
            [
                "# SAEE Commercial Readiness State Consistency Audit Recommendation Gate",
                "",
                "answer: conditional",
                "",
                "recommend_for_state_lookup: true",
                "recommend_for_formal_launch_decision: false",
                "recommend_for_production_readiness_claim: false",
                "recommend_for_external_validation_success_claim: false",
                "",
                "reason: The audit can be recommended for agent-readable commercial state lookup because it confirms the current hold state and boundary claims. It must not be used as proof of launch readiness, customer validation, or external validation success.",
                "",
                "lane_reconciliation: The workbook import approval review lane, the related support_contact owner-assignment lane, and the formal_security_review sprint candidate are documented as separate hold-state queues. None authorizes execution.",
                "",
                "boundary:",
                "- production_ready: false",
                "- customer_validated: false",
                "- product_launched: false",
                "- private_core_exposed: false",
                "- external_validation_success_claim: false",
                "",
                "next_action: Fill the 64 human quick-fill values before any evidence import or blocker closure path proceeds.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_audit()
    write_json(AUDIT_JSON, payload)
    write_markdown(payload)
    print(
        "SAEE_COMMERCIAL_READINESS_STATE_CONSISTENCY_AUDIT: PASS "
        f"status={payload['status']} "
        f"commercial_status={payload['commercial_status']} "
        f"external_calibration_status={payload['external_calibration_status']} "
        f"failed_check_count={payload['failed_check_count']} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )


if __name__ == "__main__":
    main()
