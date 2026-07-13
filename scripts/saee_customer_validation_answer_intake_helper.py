#!/usr/bin/env python3
"""Prepare and optionally parse the final customer-validation answer sheet.

Default mode is non-mutating for customer-validation evidence: it creates a
human-fillable answer sheet and records a hold state. With `--apply`, it parses
an explicitly human-filled answer sheet into the existing
external_customer_validation_session_entry.human_filled.local.json shape. It
does not contact customers, infer missing answers, close blockers, or claim
customer validation.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
OUT = EVIDENCE_DIR / "customer_validation_answer_intake_helper"
SUMMARY = OUT / "customer_validation_answer_intake_helper.local.json"
REPORT = OUT / "customer_validation_answer_intake_helper.md"
ANSWER_TEMPLATE = OUT / "customer_validation_answers.template.md"
ANSWER_INPUT = OUT / "customer_validation_answers.human_filled.md"
BOUNDARY = OUT / "customer_validation_answer_intake_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_ANSWER_INTAKE_HELPER_RECOMMENDATION_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"

ENTRY_TEMPLATE = EVIDENCE_DIR / "external_customer_validation_session_entry.template.json"
TARGET_ENTRY = EVIDENCE_DIR / "external_customer_validation_session_entry.human_filled.local.json"
LAST_MILE = EVIDENCE_DIR / "customer_validation_last_mile_packet/customer_validation_last_mile_packet.local.json"
IMPORTER_SMOKE = ROOT / "scripts/saee_external_customer_validation_session_entry_importer_smoke.py"

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


def build_entry_from_answers(answers: dict[str, str]) -> tuple[dict[str, Any], list[str]]:
    template = read_json(ENTRY_TEMPLATE)
    entry = json.loads(json.dumps(template, ensure_ascii=False))
    missing: list[str] = []

    for field in TEXT_FIELDS:
        value = answers.get(field, "")
        if not value:
            missing.append(field)
        if field in {"human_reviewer_name"}:
            entry[field] = value
        elif field in {"session_date"}:
            entry["session"][field] = value
            entry["review_date"] = answers.get("review_date", value)
        else:
            entry["session"][field] = value

    entry["human_source_context"] = answers.get(
        "human_source_context",
        "Real external customer or target-user session recorded by human reviewer.",
    )
    if not entry["human_source_context"]:
        missing.append("human_source_context")

    for field in INT_FIELDS:
        raw = answers.get(field, "")
        try:
            value = int(raw)
        except ValueError:
            value = None
            missing.append(field)
        entry["session"][field] = value

    for field in SCORE_FIELDS:
        raw = answers.get(field, "")
        try:
            value = int(raw)
        except ValueError:
            value = None
        if not isinstance(value, int) or not 1 <= value <= 5:
            missing.append(field)
        entry["session"][field] = value

    for field in BOOL_FIELDS:
        value = parse_bool(answers.get(field, ""))
        if value is None:
            missing.append(field)
        entry["session"][field] = value

    confirmed = parse_bool(answers.get("human_entry_confirmed", ""))
    entry["human_entry_confirmed"] = confirmed is True
    if confirmed is not True:
        missing.append("human_entry_confirmed")

    for key in BOUNDARY_CONFIRMATIONS:
        value = parse_bool(answers.get(key, ""))
        entry["boundary_confirmation"][key] = value is True
        if value is not True:
            missing.append(key)

    entry["session"]["boundary_flags"] = {
        "secrets_collected": False,
        "production_data_collected": False,
        "customer_data_uploaded": False,
        "private_core_disclosed": False,
        "production_ready_claim_made": False,
    }
    for key in entry.get("evidence_review", {}):
        value = parse_bool(answers.get(key, "true"))
        entry["evidence_review"][key] = value is True
        if value is not True:
            missing.append(key)

    for key in [
        "customer_contacted",
        "customer_validated",
        "private_core_exposed",
        "product_launched",
        "production_ready",
        "public_validation_claim_published",
        "testimonial_published",
        "case_study_published",
    ]:
        entry[key] = False
    return entry, sorted(set(missing))


def write_answer_template() -> None:
    template = read_json(ENTRY_TEMPLATE)
    lines = [
        "# SAEE Customer Validation Human Answer Sheet",
        "",
        "Only fill this after a real external customer or target-user session.",
        "Use `key: value` lines. Do not use internal self-review as customer evidence.",
        "",
        "session_id:",
        "session_date:",
        "human_reviewer_name:",
        "participant_role:",
        "team_type:",
        "current_evaluation_method:",
        "candidate_count:",
        "understanding_score:",
        "trust_score:",
        "decision_influence_score:",
        "repeat_usage_intent_score:",
        "time_to_value_minutes:",
        "willing_to_test_own_candidates:",
        "top_objection:",
        "evidence_missing:",
        "notes:",
        "human_source_context:",
        "human_entry_confirmed:",
        "",
        "# Boundary confirmations. Use true only if factually true.",
    ]
    for key in BOUNDARY_CONFIRMATIONS:
        lines.append(f"{key}:")
    lines.append("")
    lines.append("# Evidence review confirmations. Use true only if reviewed.")
    for key in template.get("evidence_review", {}):
        lines.append(f"{key}: true")
    ANSWER_TEMPLATE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_payload(apply: bool) -> dict[str, Any]:
    input_exists = ANSWER_INPUT.exists()
    target_written = False
    parse_status = "hold_human_answer_sheet_missing"
    missing_fields: list[str] = []
    if input_exists:
        entry, missing_fields = build_entry_from_answers(parse_answers(ANSWER_INPUT))
        if missing_fields:
            parse_status = "hold_human_answer_sheet_incomplete"
        elif apply:
            write_json(TARGET_ENTRY, entry)
            target_written = True
            parse_status = "session_entry_written_pending_post_session_processor"
        else:
            parse_status = "ready_for_apply_to_session_entry"

    last_mile = read_json(LAST_MILE)
    return {
        "customer_validation_answer_intake_helper_v0_1": True,
        "helper_type": "human_answer_sheet_to_session_entry_helper",
        "status": parse_status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_goal_blocker": "customer_validated",
        "source_last_mile_packet": rel(LAST_MILE),
        "source_entry_template": rel(ENTRY_TEMPLATE),
        "answer_template": rel(ANSWER_TEMPLATE),
        "human_answer_input": rel(ANSWER_INPUT),
        "human_answer_input_exists": input_exists,
        "target_session_entry": rel(TARGET_ENTRY),
        "target_session_entry_written": target_written,
        "apply_requested": apply,
        "missing_field_count": len(missing_fields),
        "missing_fields": missing_fields,
        "post_session_processor_command": "python3 scripts/saee_external_customer_validation_post_session_processor.py",
        "importer_smoke": rel(IMPORTER_SMOKE),
        "required_question_count": last_mile.get("required_question_count"),
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
        "blockers_closed_by_answer_intake_helper": 0,
    }


def write_outputs(payload: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    write_answer_template()
    write_json(SUMMARY, payload)

    REPORT.write_text(
        f"""# SAEE Customer Validation Answer Intake Helper v0.1

Status: `{payload['status']}`.

This helper lets a human reviewer paste real external customer or target-user
session answers into one key-value answer sheet. It can then be applied to the
existing session-entry JSON shape. It does not contact customers, infer missing
answers, close blockers, claim customer validation, or claim production
readiness.

## Files

- Answer template: `{payload['answer_template']}`
- Human answer input: `{payload['human_answer_input']}`
- Target session entry: `{payload['target_session_entry']}`

## Current State

```yaml
customer_validation_answer_intake_helper_v0_1: true
status: {payload['status']}
human_answer_input_exists: {str(payload['human_answer_input_exists']).lower()}
target_session_entry_written: {str(payload['target_session_entry_written']).lower()}
customer_validated: false
production_ready: false
product_launched: false
private_core_exposed: false
blockers_closed_by_answer_intake_helper: 0
```
""",
        encoding="utf-8",
    )

    BOUNDARY.write_text(
        f"""# SAEE Customer Validation Answer Intake Boundary Audit

customer_validation_answer_intake_helper_v0_1: true
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
- blockers_closed_by_answer_intake_helper: 0
""",
        encoding="utf-8",
    )

    GATE.write_text(
        """# SAEE Customer Validation Answer Intake Helper Recommendation Gate

question: If a potential customer needed a simpler way to provide customer-validation evidence, would we recommend this helper?

answer: conditional

reason: Recommend only as an internal evidence-entry helper after a real external customer or target-user session has happened. Do not recommend it as customer validation itself.

evolution_subsystem: Global Sensing / Evolutionary Archive

boundary:
  customer_validated: false
  production_ready: false
  product_launched: false
  private_core_exposed: false
  blockers_closed_by_answer_intake_helper: 0

next_action: Human must fill the answer sheet from real external-session evidence before applying it to the target session-entry JSON.
""",
        encoding="utf-8",
    )

    for line in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_intake_helper/customer_validation_answer_intake_helper.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_intake_helper/customer_validation_answer_intake_helper.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_intake_helper/customer_validation_answers.template.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_intake_helper/customer_validation_answer_intake_boundary_audit.md",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_ANSWER_INTAKE_HELPER_RECOMMENDATION_GATE.md",
        "/scripts/saee_customer_validation_answer_intake_helper.py",
        "/scripts/saee_customer_validation_answer_intake_helper_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["customer_validation_answer_intake_helper_v0_1"] = {
        "name": "SAEE Customer Validation Answer Intake Helper v0.1",
        "status": payload["status"],
        "current_goal_blocker": "customer_validated",
        "answer_template": payload["answer_template"],
        "human_answer_input": payload["human_answer_input"],
        "human_answer_input_exists": payload["human_answer_input_exists"],
        "target_session_entry": payload["target_session_entry"],
        "target_session_entry_written": payload["target_session_entry_written"],
        "post_session_processor_command": payload["post_session_processor_command"],
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
        "blockers_closed_by_answer_intake_helper": 0,
        "entrypoints": {
            "summary": rel(SUMMARY),
            "report": rel(REPORT),
            "answer_template": rel(ANSWER_TEMPLATE),
            "boundary_audit": rel(BOUNDARY),
            "gate": rel(GATE),
            "runner": "scripts/saee_customer_validation_answer_intake_helper.py",
            "smoke": "scripts/saee_customer_validation_answer_intake_helper_smoke.py",
        },
    }
    AGENT_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    block = f"""## Customer Validation Answer Intake Helper v0.1

- `customer_validation_answer_intake_helper_v0_1`
- Status: `{payload['status']}`
- Current blocker: `customer_validated`
- Human answer template: `{payload['answer_template']}`
- Target session entry: `{payload['target_session_entry']}`
- `customer_validated=false`; `production_ready=false`; `private_core_exposed=false`.
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_CUSTOMER_VALIDATION_ANSWER_INTAKE_HELPER_V0_1", block)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write target session entry if human answers are complete")
    args = parser.parse_args()
    payload = build_payload(apply=args.apply)
    write_outputs(payload)
    print(
        "SAEE_CUSTOMER_VALIDATION_ANSWER_INTAKE_HELPER: PASS "
        f"status={payload['status']} "
        f"answer_input_exists={str(payload['human_answer_input_exists']).lower()} "
        "customer_validated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
