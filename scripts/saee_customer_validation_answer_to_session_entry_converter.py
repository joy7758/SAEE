#!/usr/bin/env python3
"""Convert a human-filled customer validation answer sheet into session-entry JSON.

This is a local bridge between the plain Chinese answer sheet and the existing
external customer validation session-entry importer. It never contacts
customers, never infers missing feedback, and never claims customer validation.
By default it only writes a status report. With ``--apply`` it writes the
session-entry JSON only when the answer sheet is complete and boundary-safe.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
OUT = EVIDENCE / "customer_validation_answer_to_session_entry_converter"
SUMMARY = OUT / "customer_validation_answer_to_session_entry_converter.local.json"
REPORT = OUT / "customer_validation_answer_to_session_entry_converter.md"
BOUNDARY = OUT / "customer_validation_answer_to_session_entry_converter_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_ANSWER_TO_SESSION_ENTRY_CONVERTER_GATE.md"
ANSWER_INPUT = EVIDENCE / "customer_validation_answer_intake_helper/customer_validation_answers.human_filled.md"
ENTRY_TEMPLATE = EVIDENCE / "external_customer_validation_session_entry.template.json"
TARGET_ENTRY = EVIDENCE / "external_customer_validation_session_entry.human_filled.local.json"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
]

TEXT_FIELDS = [
    "session_id",
    "session_date",
    "human_reviewer_name",
    "participant_role",
    "team_type",
    "current_evaluation_method",
    "top_objection",
    "evidence_missing",
    "notes",
    "human_source_context",
    "human_entry_confirmed",
]
INT_FIELDS = ["candidate_count", "time_to_value_minutes"]
SCORE_FIELDS = [
    "understanding_score",
    "trust_score",
    "decision_influence_score",
    "repeat_usage_intent_score",
]
BOOL_FIELDS = ["willing_to_test_own_candidates"]
BOUNDARY_CONFIRMATIONS = [
    "no_secrets_collected",
    "no_production_data_collected",
    "no_customer_data_uploaded",
    "no_private_core_disclosed",
    "no_production_ready_claim_made",
]
SESSION_BOUNDARY_FALSE_KEYS = [
    "secrets_collected",
    "production_data_collected",
    "customer_data_uploaded",
    "private_core_disclosed",
    "production_ready_claim_made",
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ensure_line(path: Path, line: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if line not in text.splitlines():
        path.write_text(text.rstrip() + "\n" + line + "\n", encoding="utf-8")


def replace_block(path: Path, marker: str, body: str) -> None:
    start = f"<!-- {marker}:START -->"
    end = f"<!-- {marker}:END -->"
    block = f"{start}\n{body.rstrip()}\n{end}\n"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if start in text and end in text:
        before = text.split(start, 1)[0]
        after = text.split(end, 1)[1]
        path.write_text(before.rstrip() + "\n\n" + block + after.lstrip(), encoding="utf-8")
    else:
        path.write_text(text.rstrip() + "\n\n" + block, encoding="utf-8")


def parse_bool(raw: str) -> bool | None:
    value = raw.strip().lower()
    if value in {"true", "yes", "y", "是", "确认", "1"}:
        return True
    if value in {"false", "no", "n", "否", "0"}:
        return False
    return None


def parse_answers(path: Path) -> dict[str, str]:
    answers: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" in stripped:
            key, value = stripped.split(":", 1)
        elif "：" in stripped:
            key, value = stripped.split("：", 1)
        else:
            continue
        answers[key.strip()] = value.strip()
    return answers


def evidence_review_keys() -> list[str]:
    template = read_json(ENTRY_TEMPLATE)
    review = template.get("evidence_review", {})
    return sorted(review) if isinstance(review, dict) else []


def validate_answers(answers: dict[str, str]) -> dict[str, Any]:
    missing_text = [field for field in TEXT_FIELDS if not answers.get(field, "").strip()]
    missing_int: list[str] = []
    invalid_int: list[str] = []
    parsed_int: dict[str, int] = {}
    for field in INT_FIELDS:
        raw = answers.get(field, "").strip()
        if not raw:
            missing_int.append(field)
            continue
        try:
            value = int(raw)
        except ValueError:
            invalid_int.append(field)
            continue
        if field == "candidate_count" and value <= 0:
            invalid_int.append(field)
        elif field == "time_to_value_minutes" and value < 0:
            invalid_int.append(field)
        else:
            parsed_int[field] = value

    missing_scores: list[str] = []
    invalid_scores: list[str] = []
    parsed_scores: dict[str, int] = {}
    for field in SCORE_FIELDS:
        raw = answers.get(field, "").strip()
        if not raw:
            missing_scores.append(field)
            continue
        try:
            value = int(raw)
        except ValueError:
            invalid_scores.append(field)
            continue
        if not 1 <= value <= 5:
            invalid_scores.append(field)
        else:
            parsed_scores[field] = value

    missing_bool: list[str] = []
    invalid_bool: list[str] = []
    parsed_bool: dict[str, bool] = {}
    for field in BOOL_FIELDS:
        raw = answers.get(field, "").strip()
        if not raw:
            missing_bool.append(field)
            continue
        value = parse_bool(raw)
        if value is None:
            invalid_bool.append(field)
        else:
            parsed_bool[field] = value

    missing_boundary: list[str] = []
    unsafe_boundary: list[str] = []
    for field in BOUNDARY_CONFIRMATIONS:
        raw = answers.get(field, "").strip()
        if not raw:
            missing_boundary.append(field)
            continue
        if parse_bool(raw) is not True:
            unsafe_boundary.append(field)

    missing_review: list[str] = []
    unsafe_review: list[str] = []
    for field in evidence_review_keys():
        raw = answers.get(field, "").strip()
        if not raw:
            missing_review.append(field)
            continue
        if parse_bool(raw) is not True:
            unsafe_review.append(field)

    missing = sorted(set(missing_text + missing_int + missing_scores + missing_bool + missing_boundary + missing_review))
    invalid = sorted(set(invalid_int + invalid_scores + invalid_bool + unsafe_boundary + unsafe_review))
    return {
        "ready_for_conversion": not missing and not invalid,
        "missing_field_count": len(missing),
        "invalid_field_count": len(invalid),
        "missing_fields": missing,
        "invalid_fields": invalid,
        "parsed_int": parsed_int,
        "parsed_scores": parsed_scores,
        "parsed_bool": parsed_bool,
    }


def build_session_entry(answers: dict[str, str], validation: dict[str, Any]) -> dict[str, Any]:
    template = read_json(ENTRY_TEMPLATE)
    session = dict(template.get("session", {}))
    parsed_int = validation["parsed_int"]
    parsed_scores = validation["parsed_scores"]
    parsed_bool = validation["parsed_bool"]
    for field in [
        "session_id",
        "session_date",
        "participant_role",
        "team_type",
        "current_evaluation_method",
        "top_objection",
        "evidence_missing",
        "notes",
    ]:
        session[field] = answers[field]
    session["candidate_count"] = parsed_int["candidate_count"]
    session["time_to_value_minutes"] = parsed_int["time_to_value_minutes"]
    for field in SCORE_FIELDS:
        session[field] = parsed_scores[field]
    session["willing_to_test_own_candidates"] = parsed_bool["willing_to_test_own_candidates"]
    session["saee_demo_surface_used"] = session.get("saee_demo_surface_used") or "local_or_online_demo"
    session["boundary_flags"] = {key: False for key in SESSION_BOUNDARY_FALSE_KEYS}

    entry = dict(template)
    entry["human_entry_confirmed"] = True
    entry["human_reviewer_name"] = answers["human_reviewer_name"]
    entry["review_date"] = answers["session_date"]
    entry["human_source_context"] = answers["human_source_context"]
    entry["session"] = session
    entry["evidence_review"] = {key: True for key in evidence_review_keys()}
    entry["boundary_confirmation"] = {key: True for key in BOUNDARY_CONFIRMATIONS}
    entry["customer_contacted"] = False
    entry["customer_validated"] = False
    entry["product_launched"] = False
    entry["production_ready"] = False
    entry["private_core_exposed"] = False
    entry["public_validation_claim_published"] = False
    entry["testimonial_published"] = False
    entry["case_study_published"] = False
    return entry


def build_payload(apply: bool) -> tuple[dict[str, Any], dict[str, Any] | None]:
    answer_exists = ANSWER_INPUT.exists()
    answers = parse_answers(ANSWER_INPUT) if answer_exists else {}
    validation = validate_answers(answers)
    output_written = False
    session_entry = None
    if apply and answer_exists and validation["ready_for_conversion"]:
        session_entry = build_session_entry(answers, validation)
        write_json(TARGET_ENTRY, session_entry)
        output_written = True
    status = "ready_for_apply_conversion" if answer_exists and validation["ready_for_conversion"] else "hold_human_answer_sheet_missing"
    if answer_exists and not validation["ready_for_conversion"]:
        status = "hold_human_answer_sheet_incomplete_or_invalid"
    if output_written:
        status = "session_entry_written_pending_importer"
    payload = {
        "customer_validation_answer_to_session_entry_converter_v0_1": True,
        "converter_type": "local_human_answer_sheet_to_session_entry_json",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_goal_blocker": "customer_validated",
        "human_answer_input": rel(ANSWER_INPUT),
        "human_answer_input_exists": answer_exists,
        "target_session_entry": rel(TARGET_ENTRY),
        "target_session_entry_exists": TARGET_ENTRY.exists(),
        "apply_requested": apply,
        "session_entry_written": output_written,
        "ready_for_importer": output_written,
        "explicit_apply_required": True,
        "customer_validated": False,
        "production_ready": False,
        "product_launched": False,
        "customer_contacted_by_codex": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "public_sdk_released": False,
        "blockers_closed_by_converter": 0,
        **{k: v for k, v in validation.items() if k not in {"parsed_int", "parsed_scores", "parsed_bool"}},
    }
    return payload, session_entry


def write_outputs(payload: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(SUMMARY, payload)
    missing = "\n".join(f"- `{field}`" for field in payload["missing_fields"]) or "- None"
    invalid = "\n".join(f"- `{field}`" for field in payload["invalid_fields"]) or "- None"
    REPORT.write_text(
        f"""# SAEE Customer Validation Answer-to-Session-Entry Converter v0.1

Status: `{payload['status']}`.

This converter bridges the human-filled plain Chinese answer sheet into the
existing session-entry JSON expected by the customer-validation importer. It
does not contact customers, infer missing answers, import evidence, close
blockers, launch SAEE, or claim customer validation.

## Current Inputs

- Answer sheet: `{payload['human_answer_input']}`
- Target session entry: `{payload['target_session_entry']}`
- Apply requested: `{str(payload['apply_requested']).lower()}`
- Session entry written: `{str(payload['session_entry_written']).lower()}`

## Missing Fields

{missing}

## Invalid Or Unsafe Fields

{invalid}

## Boundary

- customer_validated=false
- production_ready=false
- product_launched=false
- customer_contacted_by_codex=false
- private_core_exposed=false
- blockers_closed_by_converter=0
""",
        encoding="utf-8",
    )
    BOUNDARY.write_text(
        f"""# SAEE Customer Validation Answer-to-Session-Entry Converter Boundary Audit

customer_validation_answer_to_session_entry_converter_v0_1: true
status: {payload['status']}

- customer_validated: false
- production_ready: false
- product_launched: false
- customer_contacted_by_codex: false
- private_core_exposed: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- external_calls_made: false
- external_model_api_called: false
- blockers_closed_by_converter: 0
""",
        encoding="utf-8",
    )
    GATE.write_text(
        """# SAEE Customer Validation Answer-to-Session-Entry Converter Gate

answer: local_converter_ready_explicit_apply_required

reason: Human reviewers can fill a plain Chinese answer sheet first, then use
this converter to create the session-entry JSON required by the existing
importer. The converter requires explicit `--apply` and does not infer missing
customer feedback.

boundary:
  customer_validated: false
  production_ready: false
  product_launched: false
  customer_contacted_by_codex: false
  private_core_exposed: false
  blockers_closed_by_converter: 0

next_action: After a real external customer or target-user session, fill the
answer sheet, run preflight, then run this converter with `--apply` only if the
answer sheet is complete.
""",
        encoding="utf-8",
    )


def update_indexes(payload: dict[str, Any]) -> None:
    for line in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_to_session_entry_converter/customer_validation_answer_to_session_entry_converter.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_to_session_entry_converter/customer_validation_answer_to_session_entry_converter.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_to_session_entry_converter/customer_validation_answer_to_session_entry_converter_boundary_audit.md",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_ANSWER_TO_SESSION_ENTRY_CONVERTER_GATE.md",
        "/scripts/saee_customer_validation_answer_to_session_entry_converter.py",
        "/scripts/saee_customer_validation_answer_to_session_entry_converter_smoke.py",
    ]:
        ensure_line(LLMS, line)
    index = read_json(AGENT_INDEX)
    index["customer_validation_answer_to_session_entry_converter_v0_1"] = {
        "name": "SAEE Customer Validation Answer-to-Session-Entry Converter v0.1",
        "status": payload["status"],
        "current_goal_blocker": payload["current_goal_blocker"],
        "human_answer_input_exists": payload["human_answer_input_exists"],
        "target_session_entry_exists": payload["target_session_entry_exists"],
        "apply_requested": payload["apply_requested"],
        "session_entry_written": payload["session_entry_written"],
        "ready_for_importer": payload["ready_for_importer"],
        "explicit_apply_required": payload["explicit_apply_required"],
        "customer_validated": False,
        "production_ready": False,
        "product_launched": False,
        "customer_contacted_by_codex": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "blockers_closed_by_converter": 0,
        "entrypoints": {
            "summary": rel(SUMMARY),
            "report": rel(REPORT),
            "boundary_audit": rel(BOUNDARY),
            "gate": rel(GATE),
            "runner": "scripts/saee_customer_validation_answer_to_session_entry_converter.py",
            "smoke": "scripts/saee_customer_validation_answer_to_session_entry_converter_smoke.py",
        },
    }
    write_json(AGENT_INDEX, index)
    block = f"""## Customer Validation Answer-to-Session-Entry Converter v0.1

- `customer_validation_answer_to_session_entry_converter_v0_1`
- Status: `{payload['status']}`
- Current blocker: `customer_validated`
- Human answer input exists: `{payload['human_answer_input_exists']}`
- Session entry written: `{payload['session_entry_written']}`
- Explicit apply required: `true`
- `customer_validated=false`; `production_ready=false`; `private_core_exposed=false`.
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_CUSTOMER_VALIDATION_ANSWER_TO_SESSION_ENTRY_CONVERTER_V0_1", block)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert human answer sheet to customer-validation session-entry JSON.")
    parser.add_argument("--apply", action="store_true", help="Write the target session-entry JSON if the answer sheet is complete.")
    parser.add_argument("--json", action="store_true", help="Print summary JSON.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    payload, _ = build_payload(args.apply)
    write_outputs(payload)
    update_indexes(payload)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(
            "SAEE_CUSTOMER_VALIDATION_ANSWER_TO_SESSION_ENTRY_CONVERTER: PASS "
            f"status={payload['status']} session_entry_written={str(payload['session_entry_written']).lower()} "
            "customer_validated=false production_ready=false"
        )


if __name__ == "__main__":
    main()
