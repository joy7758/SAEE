#!/usr/bin/env python3
"""Build customer-validation evidence from a human-filled local pilot result.

This builder reads a local JSON file prepared by a human reviewer and converts
it into the evidence shape consumed by production customer-validation readiness.
It does not contact customers, infer missing results, publish claims, collect
customer data, modify backend/runtime/kernel/API schema, or mark SAEE as
customer validated.
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
from saee_backend.services.production_customer_validation_evidence import (
    BOUNDARY_REVIEW_KEYS,
    CLAIM_PERMISSION_KEYS,
    CUSTOMER_VALUE_KEYS,
    FORBIDDEN_TRUE_KEYS,
    PILOT_RESULT_KEYS,
    evaluate_production_customer_validation_evidence,
)


DEFAULT_INPUT_PATH = ROOT / "phase_b_product/validation/PILOT_RESULT_TEMPLATE.json"
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / "customer_validation_evidence.from_pilot.local.json"
INPUT_TEMPLATE_PATH = OUTPUT_DIR / "customer_validation_evidence_input.template.json"

NUMERIC_SCORE_FIELDS = (
    "understanding_score",
    "trust_score",
    "decision_influence_score",
    "repeat_usage_intent_score",
)
SESSION_REQUIRED_TEXT_FIELDS = (
    "session_id",
    "session_date",
    "participant_role",
    "team_type",
    "current_evaluation_method",
)
SESSION_OPTIONAL_SIGNAL_FIELDS = (
    "top_objection",
    "evidence_missing",
    "notes",
)
SESSION_BOUNDARY_FALSE_KEYS = (
    "secrets_collected",
    "production_data_collected",
    "customer_data_uploaded",
    "private_core_disclosed",
    "production_ready_claim_made",
)
REVIEW_KEY_GROUPS = (
    PILOT_RESULT_KEYS
    + CUSTOMER_VALUE_KEYS
    + CLAIM_PERMISSION_KEYS
    + BOUNDARY_REVIEW_KEYS
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_CUSTOMER_VALIDATION_EVIDENCE_BUILDER: FAIL: " + message)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"SAEE_CUSTOMER_VALIDATION_EVIDENCE_BUILDER: FAIL: invalid input {path}: {exc}"
        ) from exc
    require(isinstance(data, dict), "input JSON must be an object")
    return data


def bool_value(data: dict[str, Any], key: str) -> bool:
    return data.get(key) is True


def review_flags(data: dict[str, Any]) -> dict[str, bool]:
    review = data.get("evidence_review", {})
    if not isinstance(review, dict):
        review = {}
    return {key: bool_value(review, key) for key in REVIEW_KEY_GROUPS}


def is_number_score(value: Any) -> bool:
    return isinstance(value, (int, float)) and 1 <= value <= 5


def session_boundary_safe(session: dict[str, Any]) -> bool:
    flags = session.get("boundary_flags", {})
    if not isinstance(flags, dict):
        return False
    return all(flags.get(key) is False for key in SESSION_BOUNDARY_FALSE_KEYS)


def session_has_required_fields(session: dict[str, Any]) -> bool:
    if not all(str(session.get(field, "")).strip() for field in SESSION_REQUIRED_TEXT_FIELDS):
        return False
    if str(session.get("session_id", "")).startswith("PILOT-YYYYMMDD"):
        return False
    if not isinstance(session.get("candidate_count"), int) or session["candidate_count"] <= 0:
        return False
    if not all(is_number_score(session.get(field)) for field in NUMERIC_SCORE_FIELDS):
        return False
    if session.get("willing_to_test_own_candidates") not in {True, False}:
        return False
    return session_boundary_safe(session)


def completed_sessions(data: dict[str, Any]) -> list[dict[str, Any]]:
    sessions = data.get("sessions", [])
    if not isinstance(sessions, list):
        return []
    return [session for session in sessions if isinstance(session, dict) and session_has_required_fields(session)]


def boundary_violations(data: dict[str, Any], sessions: list[dict[str, Any]]) -> list[str]:
    violations: list[str] = []
    for key in FORBIDDEN_TRUE_KEYS:
        if data.get(key) is True:
            violations.append(key)
    raw_sessions = data.get("sessions", [])
    if isinstance(raw_sessions, list):
        for index, session in enumerate(raw_sessions):
            if isinstance(session, dict) and not session_boundary_safe(session):
                violations.append(f"session_{index}_boundary_flags")
    if not sessions:
        violations.append("no_completed_human_pilot_session")
    return violations


def signal_summary(sessions: list[dict[str, Any]]) -> dict[str, Any]:
    if not sessions:
        return {
            "session_count": 0,
            "average_understanding_score": None,
            "average_trust_score": None,
            "average_decision_influence_score": None,
            "average_repeat_usage_intent_score": None,
            "go_hold_pivot": "not_evaluated",
        }
    averages = {}
    for field in NUMERIC_SCORE_FIELDS:
        averages[f"average_{field}"] = round(
            sum(float(session[field]) for session in sessions) / len(sessions), 4
        )
    go_hold_pivot = "go" if all(averages[f"average_{field}"] >= 4 for field in NUMERIC_SCORE_FIELDS) else "hold"
    return {
        "session_count": len(sessions),
        **averages,
        "go_hold_pivot": go_hold_pivot,
    }


def build_evidence(input_data: dict[str, Any], input_path: Path) -> dict[str, Any]:
    sessions = completed_sessions(input_data)
    violations = boundary_violations(input_data, sessions)
    flags = review_flags(input_data)
    has_completed_session = bool(sessions)
    boundary_safe = not violations

    evidence: dict[str, Any] = {
        "customer_validation_evidence_type": "production_customer_validation_evidence",
        "evidence_scope": "human_filled_local_pilot_result_to_customer_validation_evidence",
        "evidence_version": "v0.1",
        "generated_by": "scripts/saee_customer_validation_evidence_builder.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_pilot_result_path": str(input_path),
        "source_template": "phase_b_product/validation/PILOT_RESULT_TEMPLATE.json",
        "completed_session_count": len(sessions),
        "input_boundary_violation_count": len(violations),
        "input_boundary_violations": violations,
        "signal_summary": signal_summary(sessions),
        "human_filled_input_required": True,
        "codex_contacted_customer": False,
        "codex_inferred_missing_results": False,
        "codex_executed_pilot": False,
        "codex_collected_customer_data": False,
    }

    for key in PILOT_RESULT_KEYS:
        evidence[key] = flags[key] and has_completed_session and boundary_safe
    evidence["boundary_flags_reviewed"] = flags["boundary_flags_reviewed"] and boundary_safe

    for key in CUSTOMER_VALUE_KEYS:
        evidence[key] = flags[key] and has_completed_session and boundary_safe

    for key in CLAIM_PERMISSION_KEYS:
        evidence[key] = flags[key] and has_completed_session and boundary_safe

    for key in BOUNDARY_REVIEW_KEYS:
        evidence[key] = flags[key] and boundary_safe

    for key in FORBIDDEN_TRUE_KEYS:
        evidence[key] = False

    evidence["session_summaries"] = [
        {
            "session_id": session.get("session_id", ""),
            "session_date": session.get("session_date", ""),
            "participant_role": session.get("participant_role", ""),
            "team_type": session.get("team_type", ""),
            "candidate_count": session.get("candidate_count", 0),
            "understanding_score": session.get("understanding_score"),
            "trust_score": session.get("trust_score"),
            "decision_influence_score": session.get("decision_influence_score"),
            "repeat_usage_intent_score": session.get("repeat_usage_intent_score"),
            "willing_to_test_own_candidates": session.get("willing_to_test_own_candidates"),
            "top_objection_recorded": bool(str(session.get("top_objection", "")).strip()),
            "evidence_missing_recorded": bool(str(session.get("evidence_missing", "")).strip()),
            "notes_recorded": bool(str(session.get("notes", "")).strip()),
        }
        for session in sessions
    ]
    return evidence


def input_template() -> dict[str, Any]:
    base = read_json(DEFAULT_INPUT_PATH)
    base["customer_validation_evidence_input_v0_1"] = True
    base["evidence_review"] = {key: False for key in REVIEW_KEY_GROUPS}
    base["boundary_note"] = (
        "A human reviewer must fill sessions and explicitly set evidence_review "
        "flags after an approved pilot. Codex must not infer missing results."
    )
    return base


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_template() -> dict[str, Any]:
    data = input_template()
    write_json(INPUT_TEMPLATE_PATH, data)
    return data


def build_from_file(input_path: Path, output_path: Path) -> dict[str, Any]:
    input_data = read_json(input_path)
    evidence = build_evidence(input_data, input_path)
    write_json(output_path, evidence)
    return evidence


def readiness_for(path: Path) -> dict[str, object]:
    return evaluate_production_customer_validation_evidence(
        load_settings({"SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH": str(path)})
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build local customer-validation evidence from a human-filled pilot result."
    )
    parser.add_argument("--input", default=str(DEFAULT_INPUT_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--write-template", action="store_true")
    parser.add_argument("--json", action="store_true", help="Print JSON summary.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.write_template:
        template = write_template()
        summary = {
            "customer_validation_evidence_builder_v0_1": True,
            "template_written": str(INPUT_TEMPLATE_PATH),
            "review_flag_count": len(template["evidence_review"]),
            "external_calls_made": False,
            "customer_contacted": False,
            "customer_validated": False,
            "production_ready": False,
        }
    else:
        output_path = Path(args.output).expanduser()
        evidence = build_from_file(Path(args.input).expanduser(), output_path)
        readiness = readiness_for(output_path)
        summary = {
            "customer_validation_evidence_builder_v0_1": True,
            "input": str(Path(args.input).expanduser()),
            "output": str(output_path),
            "readiness_status": readiness["status"],
            "customer_validation_evidence_complete": readiness[
                "customer_validation_evidence_complete"
            ],
            "production_customer_validation_ready": readiness[
                "production_customer_validation_ready"
            ],
            "completed_session_count": evidence["completed_session_count"],
            "input_boundary_violation_count": evidence["input_boundary_violation_count"],
            "codex_contacted_customer": False,
            "codex_inferred_missing_results": False,
            "codex_executed_pilot": False,
            "external_calls_made": False,
            "customer_validated": False,
            "production_ready": False,
        }
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(
            "SAEE_CUSTOMER_VALIDATION_EVIDENCE_BUILDER: "
            + " ".join(f"{key}={value}" for key, value in summary.items())
        )


if __name__ == "__main__":
    main()
