#!/usr/bin/env python3
"""Preflight the real-session customer-validation answer sheet.

This checks whether the human-filled answer sheet is present and complete
enough for a later explicit apply/import run. It does not write the final
session-entry JSON, does not infer missing answers, does not contact customers,
and does not close the customer_validated blocker.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
HELPER_DIR = EVIDENCE_DIR / "customer_validation_answer_intake_helper"
OUT = EVIDENCE_DIR / "customer_validation_answer_sheet_preflight"
SUMMARY = OUT / "customer_validation_answer_sheet_preflight.local.json"
REPORT = OUT / "customer_validation_answer_sheet_preflight.md"
MISSING_FIELDS = OUT / "customer_validation_answer_sheet_missing_fields.md"
BOUNDARY = OUT / "customer_validation_answer_sheet_preflight_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_ANSWER_SHEET_PREFLIGHT_GATE.md"
ANSWER_TEMPLATE = HELPER_DIR / "customer_validation_answers.template.md"
ANSWER_INPUT = HELPER_DIR / "customer_validation_answers.human_filled.md"
TARGET_ENTRY = EVIDENCE_DIR / "external_customer_validation_session_entry.human_filled.local.json"
ENTRY_TEMPLATE = EVIDENCE_DIR / "external_customer_validation_session_entry.template.json"
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


def parse_bool(raw: str) -> bool | None:
    value = raw.strip().lower()
    if value in {"true", "yes", "y", "是", "确认", "1"}:
        return True
    if value in {"false", "no", "n", "否", "0"}:
        return False
    return None


def evidence_review_keys() -> list[str]:
    template = read_json(ENTRY_TEMPLATE)
    review = template.get("evidence_review", {})
    if not isinstance(review, dict):
        return []
    return sorted(review)


def validate_answers(answers: dict[str, str]) -> dict[str, Any]:
    missing_text = [field for field in TEXT_FIELDS if not answers.get(field, "").strip()]
    missing_int = []
    invalid_int = []
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
        if field == "time_to_value_minutes" and value < 0:
            invalid_int.append(field)

    missing_scores = []
    invalid_scores = []
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

    missing_bool = []
    invalid_bool = []
    for field in BOOL_FIELDS:
        raw = answers.get(field, "").strip()
        if not raw:
            missing_bool.append(field)
        elif parse_bool(raw) is None:
            invalid_bool.append(field)

    missing_boundary_confirmations = []
    unsafe_boundary_confirmations = []
    for field in BOUNDARY_CONFIRMATIONS:
        raw = answers.get(field, "").strip()
        if not raw:
            missing_boundary_confirmations.append(field)
            continue
        if parse_bool(raw) is not True:
            unsafe_boundary_confirmations.append(field)

    missing_review = []
    unsafe_review = []
    for field in evidence_review_keys():
        raw = answers.get(field, "").strip()
        if not raw:
            missing_review.append(field)
            continue
        if parse_bool(raw) is not True:
            unsafe_review.append(field)

    missing = sorted(
        set(
            missing_text
            + missing_int
            + missing_scores
            + missing_bool
            + missing_boundary_confirmations
            + missing_review
        )
    )
    invalid = sorted(set(invalid_int + invalid_scores + invalid_bool + unsafe_boundary_confirmations + unsafe_review))
    ready_for_apply = not missing and not invalid
    return {
        "ready_for_apply": ready_for_apply,
        "missing_field_count": len(missing),
        "invalid_field_count": len(invalid),
        "missing_fields": missing,
        "invalid_fields": invalid,
        "missing_text_fields": missing_text,
        "missing_int_fields": missing_int,
        "invalid_int_fields": invalid_int,
        "missing_score_fields": missing_scores,
        "invalid_score_fields": invalid_scores,
        "missing_bool_fields": missing_bool,
        "invalid_bool_fields": invalid_bool,
        "missing_boundary_confirmations": missing_boundary_confirmations,
        "unsafe_boundary_confirmations": unsafe_boundary_confirmations,
        "missing_evidence_review_fields": missing_review,
        "unsafe_evidence_review_fields": unsafe_review,
    }


def build_payload() -> dict[str, Any]:
    answer_exists = ANSWER_INPUT.exists()
    validation = validate_answers(parse_answers(ANSWER_INPUT)) if answer_exists else validate_answers({})
    status = "ready_for_explicit_apply_request" if answer_exists and validation["ready_for_apply"] else "hold_human_answer_sheet_missing"
    if answer_exists and not validation["ready_for_apply"]:
        status = "hold_human_answer_sheet_incomplete_or_invalid"
    return {
        "customer_validation_answer_sheet_preflight_v0_1": True,
        "preflight_type": "real_external_customer_answer_sheet_preflight",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_goal_blocker": "customer_validated",
        "answer_template": rel(ANSWER_TEMPLATE),
        "human_answer_input": rel(ANSWER_INPUT),
        "human_answer_input_exists": answer_exists,
        "target_session_entry": rel(TARGET_ENTRY),
        "target_session_entry_exists": TARGET_ENTRY.exists(),
        "ready_for_explicit_apply_request": bool(answer_exists and validation["ready_for_apply"]),
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
        "blockers_closed_by_preflight": 0,
        **validation,
    }


def write_outputs(payload: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(SUMMARY, payload)
    missing_lines = "\n".join(f"- `{field}`" for field in payload["missing_fields"]) or "- None"
    invalid_lines = "\n".join(f"- `{field}`" for field in payload["invalid_fields"]) or "- None"

    REPORT.write_text(
        f"""# SAEE Customer Validation Answer Sheet Preflight v0.1

Status: `{payload['status']}`.

This preflight checks whether the real external customer or target-user answer
sheet is ready for a later explicit apply/import request. It does not write the
final session-entry JSON, does not infer missing answers, and does not close
`customer_validated`.

```yaml
customer_validation_answer_sheet_preflight_v0_1: true
human_answer_input_exists: {str(payload['human_answer_input_exists']).lower()}
ready_for_explicit_apply_request: {str(payload['ready_for_explicit_apply_request']).lower()}
explicit_apply_required: true
customer_validated: false
production_ready: false
product_launched: false
private_core_exposed: false
blockers_closed_by_preflight: 0
```
""",
        encoding="utf-8",
    )

    MISSING_FIELDS.write_text(
        f"""# Customer Validation Answer Sheet Missing Or Invalid Fields

Status: `{payload['status']}`.

Answer sheet expected at:

`{payload['human_answer_input']}`

Missing fields:

{missing_lines}

Invalid or unsafe fields:

{invalid_lines}

If this remains incomplete, do not run `--apply` and do not claim
customer validation.
""",
        encoding="utf-8",
    )

    BOUNDARY.write_text(
        f"""# SAEE Customer Validation Answer Sheet Preflight Boundary Audit

customer_validation_answer_sheet_preflight_v0_1: true
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
- blockers_closed_by_preflight: 0
""",
        encoding="utf-8",
    )

    GATE.write_text(
        """# SAEE Customer Validation Answer Sheet Preflight Gate

answer: hold_until_real_external_answer_sheet_ready

reason: Customer validation requires a complete human-filled answer sheet from a real external customer or target-user session. This preflight only checks readiness and does not close the blocker.

boundary:
  customer_validated: false
  production_ready: false
  product_launched: false
  private_core_exposed: false
  blockers_closed_by_preflight: 0

next_action: Fill the answer sheet from a real external session. If the preflight becomes ready, request a separate explicit apply/import run.
""",
        encoding="utf-8",
    )

    for line in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_sheet_preflight/customer_validation_answer_sheet_preflight.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_sheet_preflight/customer_validation_answer_sheet_preflight.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_sheet_preflight/customer_validation_answer_sheet_missing_fields.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_sheet_preflight/customer_validation_answer_sheet_preflight_boundary_audit.md",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_ANSWER_SHEET_PREFLIGHT_GATE.md",
        "/scripts/saee_customer_validation_answer_sheet_preflight.py",
        "/scripts/saee_customer_validation_answer_sheet_preflight_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["customer_validation_answer_sheet_preflight_v0_1"] = {
        "name": "SAEE Customer Validation Answer Sheet Preflight v0.1",
        "status": payload["status"],
        "current_goal_blocker": "customer_validated",
        "human_answer_input_exists": payload["human_answer_input_exists"],
        "target_session_entry_exists": payload["target_session_entry_exists"],
        "ready_for_explicit_apply_request": payload["ready_for_explicit_apply_request"],
        "explicit_apply_required": True,
        "missing_field_count": payload["missing_field_count"],
        "invalid_field_count": payload["invalid_field_count"],
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
        "blockers_closed_by_preflight": 0,
        "entrypoints": {
            "summary": rel(SUMMARY),
            "report": rel(REPORT),
            "missing_fields": rel(MISSING_FIELDS),
            "boundary_audit": rel(BOUNDARY),
            "gate": rel(GATE),
            "runner": "scripts/saee_customer_validation_answer_sheet_preflight.py",
            "smoke": "scripts/saee_customer_validation_answer_sheet_preflight_smoke.py",
        },
    }
    AGENT_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    block = f"""## Customer Validation Answer Sheet Preflight v0.1

- `customer_validation_answer_sheet_preflight_v0_1`
- Status: `{payload['status']}`
- Current blocker: `customer_validated`
- Human answer input: `{payload['human_answer_input']}`
- Ready for explicit apply request: `{str(payload['ready_for_explicit_apply_request']).lower()}`
- Missing field count: `{payload['missing_field_count']}`
- Invalid field count: `{payload['invalid_field_count']}`
- `customer_validated=false`; `production_ready=false`; `private_core_exposed=false`.
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_CUSTOMER_VALIDATION_ANSWER_SHEET_PREFLIGHT_V0_1", block)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_CUSTOMER_VALIDATION_ANSWER_SHEET_PREFLIGHT: PASS "
        f"status={payload['status']} ready_for_apply={str(payload['ready_for_explicit_apply_request']).lower()} "
        "customer_validated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
