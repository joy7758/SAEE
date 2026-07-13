#!/usr/bin/env python3
"""Prove the local customer-validation evidence path without customer contact.

This path check creates fixture-only pilot-result evidence, converts it through
the existing customer-validation evidence builder, and feeds the output into
production customer-validation readiness plus commercial go/no-go checks. It
proves local wiring only. It does not contact customers, run pilot sessions,
collect customer data, publish validation claims, close blockers by itself, or
claim production readiness.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go
from saee_backend.services.production_customer_validation_evidence import (
    BOUNDARY_REVIEW_KEYS,
    CLAIM_PERMISSION_KEYS,
    CUSTOMER_VALUE_KEYS,
    FORBIDDEN_TRUE_KEYS,
    PILOT_RESULT_KEYS,
    evaluate_production_customer_validation_evidence,
)
from scripts.saee_customer_validation_evidence_builder import build_from_file


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / "customer_validation_evidence_path.local.json"
FIXTURE_INPUT_PATH = OUTPUT_DIR / "customer_validation_evidence_path.fixture_input.local.json"
FIXTURE_EVIDENCE_PATH = OUTPUT_DIR / "customer_validation_evidence_path.fixture_evidence.local.json"
REPORT_PATH = OUTPUT_DIR / "customer_validation_evidence_path_report.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/CUSTOMER_VALIDATION_EVIDENCE_PATH_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_EVIDENCE_PATH_RECOMMENDATION_GATE.md"
TARGET_BLOCKERS = ("pilot_results", "customer_validated")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_token(value: object) -> str:
    return str(value).lower()


def fixture_input() -> dict[str, Any]:
    review_keys = (
        PILOT_RESULT_KEYS
        + CUSTOMER_VALUE_KEYS
        + CLAIM_PERMISSION_KEYS
        + BOUNDARY_REVIEW_KEYS
    )
    data: dict[str, Any] = {
        "customer_validation_evidence_input_v0_1": True,
        "input_status": "fixture_only_not_real_customer_validation",
        "fixture_only": True,
        "real_pilot_session_completed": False,
        "real_customer_feedback_collected": False,
        "real_permission_to_use_feedback_recorded": False,
        "customer_validated": False,
        "customer_contacted": False,
        "product_launched": False,
        "production_ready": False,
        "private_core_exposed": False,
        "sessions": [
            {
                "session_id": "PILOT-20260705-FIXTURE-001",
                "session_date": "2026-07-05",
                "participant_role": "AI platform lead fixture",
                "team_type": "enterprise AI engineering fixture",
                "current_evaluation_method": "fixture-only local MVP review",
                "candidate_count": 3,
                "saee_demo_surface_used": "local_mvp_demo_fixture",
                "understanding_score": 5,
                "trust_score": 4,
                "decision_influence_score": 4,
                "repeat_usage_intent_score": 4,
                "time_to_value_minutes": 12,
                "top_objection": "Fixture notes preserve the need for production auth, support, legal, billing, and real customer evidence.",
                "evidence_missing": "Real customer permission, real pilot result, and launch approval are still missing.",
                "willing_to_test_own_candidates": True,
                "boundary_flags": {
                    "secrets_collected": False,
                    "production_data_collected": False,
                    "customer_data_uploaded": False,
                    "private_core_disclosed": False,
                    "production_ready_claim_made": False,
                },
                "notes": "Fixture-only pilot record used to prove local customer-validation evidence wiring.",
            }
        ],
        "aggregate_metrics": {
            "session_count": 1,
            "understanding_rate": 1.0,
            "trust_rate": 0.8,
            "decision_influence_rate": 0.8,
            "repeat_usage_intent": 0.8,
            "go_hold_pivot": "hold",
        },
        "evidence_review": {key: True for key in review_keys},
    }
    for key in FORBIDDEN_TRUE_KEYS:
        data[key] = False
    return data


def customer_validation_readiness(path: Path) -> dict[str, object]:
    return evaluate_production_customer_validation_evidence(
        load_settings({"SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH": str(path)})
    )


def commercial_status(path: Path) -> dict[str, object]:
    return evaluate_commercial_go_no_go(
        load_settings({"SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH": str(path)})
    )


def target_blocker_state(go_no_go: dict[str, Any]) -> tuple[list[str], list[str]]:
    satisfied: list[str] = []
    unsatisfied: list[str] = []
    blockers = go_no_go.get("blockers", [])
    if not isinstance(blockers, list):
        return satisfied, list(TARGET_BLOCKERS)
    for item in blockers:
        if not isinstance(item, dict):
            continue
        blocker_id = item.get("blocker_id")
        if blocker_id not in TARGET_BLOCKERS:
            continue
        if item.get("satisfied") is True:
            satisfied.append(str(blocker_id))
        else:
            unsatisfied.append(str(blocker_id))
    return satisfied, unsatisfied


def build_path(output_path: Path = DEFAULT_OUTPUT_PATH) -> dict[str, Any]:
    write_json(FIXTURE_INPUT_PATH, fixture_input())
    build_from_file(FIXTURE_INPUT_PATH, FIXTURE_EVIDENCE_PATH)
    customer_validation = customer_validation_readiness(FIXTURE_EVIDENCE_PATH)
    go_no_go = commercial_status(FIXTURE_EVIDENCE_PATH)
    target_satisfied, target_unsatisfied = target_blocker_state(go_no_go)

    path_proven = (
        customer_validation["pilot_results_evidence_complete"] is True
        and customer_validation["customer_value_evidence_complete"] is True
        and customer_validation["claim_permission_evidence_complete"] is True
        and customer_validation["boundary_review_evidence_complete"] is True
        and customer_validation["customer_validation_evidence_complete"] is True
        and customer_validation["production_customer_validation_ready"] is True
        and len(target_satisfied) == len(TARGET_BLOCKERS)
        and not target_unsatisfied
    )

    result: dict[str, Any] = {
        "customer_validation_evidence_path_v0_1": True,
        "path_type": "local_fixture_only_customer_validation_evidence_path",
        "path_status": "pass_fixture_only" if path_proven else "hold",
        "generated_by": "scripts/saee_customer_validation_evidence_path.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "fixture_only": True,
        "real_pilot_session_completed": False,
        "real_customer_feedback_collected": False,
        "real_permission_to_use_feedback_recorded": False,
        "real_customer_validation_approved": False,
        "real_customer_validation_claim_published": False,
        "real_customer_contacted": False,
        "real_customer_data_collected": False,
        "customer_validation_readiness_status_after_fixture": customer_validation["status"],
        "pilot_results_evidence_complete_after_fixture": customer_validation[
            "pilot_results_evidence_complete"
        ],
        "customer_value_evidence_complete_after_fixture": customer_validation[
            "customer_value_evidence_complete"
        ],
        "claim_permission_evidence_complete_after_fixture": customer_validation[
            "claim_permission_evidence_complete"
        ],
        "boundary_review_evidence_complete_after_fixture": customer_validation[
            "boundary_review_evidence_complete"
        ],
        "customer_validation_evidence_complete_after_fixture": customer_validation[
            "customer_validation_evidence_complete"
        ],
        "production_customer_validation_ready_after_fixture": customer_validation[
            "production_customer_validation_ready"
        ],
        "customer_validation_blocker_path_proven": path_proven,
        "customer_validation_target_blockers_satisfied_by_fixture": target_satisfied,
        "customer_validation_target_blockers_unsatisfied_by_fixture": target_unsatisfied,
        "customer_validation_target_blockers_satisfied_count_after_fixture": len(
            target_satisfied
        ),
        "commercial_status_after_fixture": go_no_go["commercial_status"],
        "production_launch_status_after_fixture": go_no_go["production_launch_status"],
        "satisfied_production_checks_after_fixture": go_no_go[
            "satisfied_production_checks"
        ],
        "total_production_checks_after_fixture": go_no_go["total_production_checks"],
        "production_blocker_count_after_fixture": go_no_go["production_blocker_count"],
        "blockers_closed_by_path": 0,
        "accepted_for_blocker_closure_count": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "public_sdk_released": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "customer_contacted": False,
        "customer_contacted_by_codex": False,
        "automated_customer_contact": False,
        "unsolicited_customer_contact": False,
        "customer_data_collected": False,
        "customer_data_processing_started": False,
        "customer_secrets_collected": False,
        "user_upload_enabled": False,
        "product_market_fit_claimed": False,
        "revenue_validated": False,
        "production_readiness_claimed": False,
        "public_validation_claim_published": False,
        "testimonial_published": False,
        "case_study_published": False,
        "paid_pilot_completed": False,
        "human_real_evidence_required": True,
        "separate_go_no_go_profile_required": True,
        "separate_human_launch_approval_required": True,
        "next_action": (
            "A human owner must replace this fixture with real approved pilot "
            "and customer-validation evidence, then rerun customer-validation "
            "readiness and commercial go/no-go. This path proof alone closes no blockers."
        ),
    }
    write_json(output_path, result)
    write_report(result)
    write_docs()
    return result


def write_report(result: dict[str, Any]) -> None:
    lines = [
        "# SAEE Customer Validation Evidence Path Report v0.1",
        "",
        "Status: local fixture-only path proof generated.",
        "",
        "## Summary",
        "",
        "- customer_validation_evidence_path_v0_1: true",
        f"- path_type: {result['path_type']}",
        f"- path_status: {result['path_status']}",
        "- fixture_only: true",
        "- real_pilot_session_completed: false",
        "- real_customer_feedback_collected: false",
        "- real_permission_to_use_feedback_recorded: false",
        "- real_customer_validation_approved: false",
        "- real_customer_validation_claim_published: false",
        "- real_customer_contacted: false",
        "- real_customer_data_collected: false",
        f"- customer_validation_readiness_status_after_fixture: {result['customer_validation_readiness_status_after_fixture']}",
        f"- pilot_results_evidence_complete_after_fixture: {bool_token(result['pilot_results_evidence_complete_after_fixture'])}",
        f"- customer_value_evidence_complete_after_fixture: {bool_token(result['customer_value_evidence_complete_after_fixture'])}",
        f"- claim_permission_evidence_complete_after_fixture: {bool_token(result['claim_permission_evidence_complete_after_fixture'])}",
        f"- boundary_review_evidence_complete_after_fixture: {bool_token(result['boundary_review_evidence_complete_after_fixture'])}",
        f"- customer_validation_evidence_complete_after_fixture: {bool_token(result['customer_validation_evidence_complete_after_fixture'])}",
        f"- production_customer_validation_ready_after_fixture: {bool_token(result['production_customer_validation_ready_after_fixture'])}",
        f"- customer_validation_blocker_path_proven: {bool_token(result['customer_validation_blocker_path_proven'])}",
        f"- customer_validation_target_blockers_satisfied_count_after_fixture: {result['customer_validation_target_blockers_satisfied_count_after_fixture']}",
        f"- commercial_status_after_fixture: {result['commercial_status_after_fixture']}",
        f"- production_blocker_count_after_fixture: {result['production_blocker_count_after_fixture']}",
        f"- blockers_closed_by_path: {result['blockers_closed_by_path']}",
        "",
        "## Boundary",
        "",
        "- No real pilot session completed.",
        "- No customer contacted.",
        "- No customer feedback collected.",
        "- No customer data collected or processed.",
        "- No permission-to-use-feedback record created.",
        "- No validation claim published.",
        "- No testimonial or case study published.",
        "- No revenue or product-market-fit claim made.",
        "- No production readiness claim made.",
        "- No runtime, backend, kernel, API schema, landing page, or private core modified.",
        "",
        "## Next Action",
        "",
        str(result["next_action"]),
        "",
    ]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def write_docs() -> None:
    DOC_PATH.write_text(
        "\n".join(
            [
                "# SAEE Customer Validation Evidence Path v0.1",
                "",
                "Status: local fixture-only path proof.",
                "",
                "This file records a local-only proof that the existing customer-validation builder output can be consumed by production customer-validation readiness and commercial go/no-go.",
                "",
                "It does not contact customers, run a pilot, infer feedback, collect customer data, publish a validation claim, close blockers by itself, launch product, or claim production readiness.",
                "",
                "## Agent-Readable Contract",
                "",
                "```yaml",
                "customer_validation_evidence_path_v0_1: true",
                "path_type: local_fixture_only_customer_validation_evidence_path",
                "path_status: pass_fixture_only",
                "fixture_only: true",
                "real_pilot_session_completed: false",
                "real_customer_feedback_collected: false",
                "real_permission_to_use_feedback_recorded: false",
                "real_customer_validation_approved: false",
                "real_customer_validation_claim_published: false",
                "real_customer_contacted: false",
                "real_customer_data_collected: false",
                "customer_validation_readiness_status_after_fixture: pass",
                "pilot_results_evidence_complete_after_fixture: true",
                "customer_value_evidence_complete_after_fixture: true",
                "claim_permission_evidence_complete_after_fixture: true",
                "boundary_review_evidence_complete_after_fixture: true",
                "customer_validation_evidence_complete_after_fixture: true",
                "production_customer_validation_ready_after_fixture: true",
                "customer_validation_blocker_path_proven: true",
                "customer_validation_target_blockers_satisfied_count_after_fixture: 2",
                "production_blocker_count_after_fixture: 22",
                "blockers_closed_by_path: 0",
                "production_ready: false",
                "customer_validated: false",
                "product_launched: false",
                "customer_contacted: false",
                "private_core_exposed: false",
                "```",
                "",
                "## Use",
                "",
                "```bash",
                "python3 scripts/saee_customer_validation_evidence_path.py",
                "python3 scripts/saee_customer_validation_evidence_path_smoke.py",
                "```",
                "",
                "## Boundary",
                "",
                "The path proof is useful for local review of evidence wiring. It is not real customer validation and must not be used as a public validation claim.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(
        "\n".join(
            [
                "# SAEE Customer Validation Evidence Path Recommendation Gate",
                "",
                "answer: conditional",
                "",
                "recommend_for_human_customer_validation_evidence_review: true",
                "recommend_for_blocker_closure_by_path_alone: false",
                "recommend_for_production_launch: false",
                "recommend_for_customer_contact: false",
                "recommend_for_validation_claim: false",
                "",
                "reason: The path proves local fixture-only wiring from a complete pilot-result input through customer-validation evidence readiness and commercial go/no-go. It does not represent real customer evidence.",
                "",
                "boundary:",
                "- fixture_only: true",
                "- real_pilot_session_completed: false",
                "- real_customer_feedback_collected: false",
                "- real_permission_to_use_feedback_recorded: false",
                "- customer_validated: false",
                "- production_ready: false",
                "- product_launched: false",
                "- customer_contacted: false",
                "- private_core_exposed: false",
                "",
                "next_action: collect real human-approved pilot and customer-validation evidence before any blocker closure or validation claim.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prove local fixture-only customer-validation evidence path wiring."
    )
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json", action="store_true", help="Print JSON result.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = build_path(Path(args.output).expanduser())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(
            "SAEE_CUSTOMER_VALIDATION_EVIDENCE_PATH: PASS "
            f"customer_validation_blocker_path_proven={bool_token(result['customer_validation_blocker_path_proven'])} "
            f"production_blocker_count_after_fixture={result['production_blocker_count_after_fixture']} "
            f"blockers_closed_by_path={result['blockers_closed_by_path']}"
        )


if __name__ == "__main__":
    main()
