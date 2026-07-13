#!/usr/bin/env python3
"""Convert the 12-question minimum customer-validation answers into session JSON.

This is a local bridge for the current `customer_validated` blocker. It does
not run a customer session, contact anyone, infer feedback, close blockers, or
claim customer validation. With `--apply`, it writes the existing session-entry
JSON only when a human-filled 12-question answer sheet is complete and
boundary-safe.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
BASE = EVIDENCE / "external_customer_validation_minimum_session_answer_converter"
SUMMARY = BASE / "minimum_session_answer_converter.local.json"
REPORT = BASE / "minimum_session_answer_converter.md"
ANSWER_TEMPLATE = BASE / "minimum_session_answers.template.md"
ANSWER_INPUT = BASE / "minimum_session_answers.human_filled.md"
BOUNDARY = BASE / "minimum_session_answer_converter_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_MINIMUM_SESSION_ANSWER_CONVERTER_GATE.md"
ENTRY_TEMPLATE = EVIDENCE / "external_customer_validation_session_entry.template.json"
TARGET_ENTRY = EVIDENCE / "external_customer_validation_session_entry.human_filled.local.json"
MINIMUM_QUESTIONS = EVIDENCE / "external_customer_validation_minimum_session_packet/MINIMUM_SESSION_QUESTIONS.md"
POST_SESSION_PROCESSOR = ROOT / "scripts/saee_external_customer_validation_post_session_processor.py"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
]

BOUNDARY_CONFIRMATIONS = [
    "no_secrets_collected",
    "no_production_data_collected",
    "no_customer_data_uploaded",
    "no_private_core_disclosed",
    "no_production_ready_claim_made",
]

FALSE_FLAGS = {
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
}


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


def parse_score(raw: str) -> int | None:
    match = re.search(r"\b([1-5])\b", raw)
    if not match:
        return None
    return int(match.group(1))


def parse_int(raw: str) -> int | None:
    match = re.search(r"\d+", raw)
    if not match:
        return None
    return int(match.group(0))


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
        normalized = key.strip().lower().replace(" ", "_")
        if re.fullmatch(r"q0?[1-9]|q1[0-2]", normalized):
            normalized = "q" + str(int(normalized[1:])).zfill(2)
        answers[normalized] = value.strip()
    return answers


def review_keys() -> list[str]:
    review = read_json(ENTRY_TEMPLATE).get("evidence_review", {})
    return sorted(review) if isinstance(review, dict) else []


def validate_answers(answers: dict[str, str]) -> dict[str, Any]:
    missing: list[str] = []
    invalid: list[str] = []
    for key in [f"q{index:02d}" for index in range(1, 13)]:
        if not answers.get(key, "").strip():
            missing.append(key)
    for key in ["session_id", "session_date", "human_reviewer_name", "human_source_context", "human_entry_confirmed"]:
        if not answers.get(key, "").strip():
            missing.append(key)
    for key in BOUNDARY_CONFIRMATIONS:
        if not answers.get(key, "").strip():
            missing.append(key)
        elif parse_bool(answers[key]) is not True:
            invalid.append(key)
    if answers.get("human_entry_confirmed") and parse_bool(answers["human_entry_confirmed"]) is not True:
        invalid.append("human_entry_confirmed")

    parsed = {
        "candidate_count": parse_int(answers.get("q04", "")),
        "understanding_score": parse_score(answers.get("q05", "")),
        "trust_score": parse_score(answers.get("q06", "")),
        "decision_influence_score": parse_score(answers.get("q07", "")),
        "repeat_usage_intent_score": parse_score(answers.get("q08", "")),
        "time_to_value_minutes": parse_int(answers.get("q09", "")),
        "willing_to_test_own_candidates": parse_bool(answers.get("willing_to_test_own_candidates", "")),
    }
    for key, value in parsed.items():
        if value is None:
            missing.append(key)
    if parsed.get("candidate_count") is not None and parsed["candidate_count"] <= 0:
        invalid.append("candidate_count")
    if parsed.get("time_to_value_minutes") is not None and parsed["time_to_value_minutes"] < 0:
        invalid.append("time_to_value_minutes")

    return {
        "ready_for_conversion": not missing and not invalid,
        "missing_field_count": len(sorted(set(missing))),
        "invalid_field_count": len(sorted(set(invalid))),
        "missing_fields": sorted(set(missing)),
        "invalid_fields": sorted(set(invalid)),
        "parsed": parsed,
    }


def build_session_entry(answers: dict[str, str], validation: dict[str, Any]) -> dict[str, Any]:
    template = read_json(ENTRY_TEMPLATE)
    parsed = validation["parsed"]
    session = dict(template.get("session", {}))
    session.update(
        {
            "session_id": answers["session_id"],
            "session_date": answers["session_date"],
            "participant_role": answers["q01"],
            "team_type": answers["q02"],
            "current_evaluation_method": answers["q03"],
            "candidate_count": parsed["candidate_count"],
            "saee_demo_surface_used": "local_or_online_demo",
            "understanding_score": parsed["understanding_score"],
            "trust_score": parsed["trust_score"],
            "decision_influence_score": parsed["decision_influence_score"],
            "repeat_usage_intent_score": parsed["repeat_usage_intent_score"],
            "time_to_value_minutes": parsed["time_to_value_minutes"],
            "willing_to_test_own_candidates": parsed["willing_to_test_own_candidates"],
            "notes": "Most valuable output: " + answers["q10"],
            "top_objection": answers["q11"],
            "evidence_missing": answers["q12"],
            "boundary_flags": {
                "secrets_collected": False,
                "production_data_collected": False,
                "customer_data_uploaded": False,
                "private_core_disclosed": False,
                "production_ready_claim_made": False,
            },
        }
    )
    entry = dict(template)
    entry.update(
        {
            "external_customer_validation_session_entry_template_v0_1": True,
            "human_entry_confirmed": True,
            "human_reviewer_name": answers["human_reviewer_name"],
            "review_date": answers.get("review_date") or answers["session_date"],
            "human_source_context": answers["human_source_context"],
            "session": session,
            "evidence_review": {key: True for key in review_keys()},
            "boundary_confirmation": {key: True for key in BOUNDARY_CONFIRMATIONS},
            "customer_contacted": False,
            "customer_validated": False,
            "product_launched": False,
            "production_ready": False,
            "private_core_exposed": False,
            "public_validation_claim_published": False,
            "testimonial_published": False,
            "case_study_published": False,
        }
    )
    return entry


def write_answer_template() -> None:
    lines = [
        "# SAEE Minimum Session Human Answers",
        "",
        "Only fill this after a real external customer or target-user session.",
        "Use short answers. Do not include secrets, source code, production data, customer data, or private workflow internals.",
        "",
        "session_id:",
        "session_date:",
        "human_reviewer_name:",
        "human_source_context:",
        "human_entry_confirmed:",
        "",
        "q01:",
        "q02:",
        "q03:",
        "q04:",
        "q05:",
        "q06:",
        "q07:",
        "q08:",
        "willing_to_test_own_candidates:",
        "q09:",
        "q10:",
        "q11:",
        "q12:",
        "",
        "# Boundary confirmations. Use true only if factually true.",
    ]
    lines.extend(f"{key}:" for key in BOUNDARY_CONFIRMATIONS)
    ANSWER_TEMPLATE.parent.mkdir(parents=True, exist_ok=True)
    ANSWER_TEMPLATE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_payload(apply: bool) -> tuple[dict[str, Any], dict[str, Any] | None]:
    answer_exists = ANSWER_INPUT.exists()
    answers = parse_answers(ANSWER_INPUT) if answer_exists else {}
    validation = validate_answers(answers)
    entry: dict[str, Any] | None = None
    output_written = False
    if apply and answer_exists and validation["ready_for_conversion"]:
        entry = build_session_entry(answers, validation)
        write_json(TARGET_ENTRY, entry)
        output_written = True
    if not answer_exists:
        status = "hold_minimum_session_answers_missing"
    elif not validation["ready_for_conversion"]:
        status = "hold_minimum_session_answers_incomplete_or_invalid"
    elif output_written:
        status = "session_entry_written_pending_post_session_processor"
    else:
        status = "ready_for_explicit_apply"
    payload = {
        "external_customer_validation_minimum_session_answer_converter_v0_1": True,
        "converter_type": "local_12_question_minimum_session_to_session_entry_json",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_goal_blocker": "customer_validated",
        "minimum_question_count": 12,
        "source_questions": rel(MINIMUM_QUESTIONS),
        "answer_template": rel(ANSWER_TEMPLATE),
        "human_answer_input": rel(ANSWER_INPUT),
        "human_answer_input_exists": answer_exists,
        "target_session_entry": rel(TARGET_ENTRY),
        "target_session_entry_exists": TARGET_ENTRY.exists(),
        "apply_requested": apply,
        "session_entry_written": output_written,
        "explicit_apply_required": True,
        "post_session_processor_command": "python3 scripts/saee_external_customer_validation_post_session_processor.py",
        "post_session_processor": rel(POST_SESSION_PROCESSOR),
        "missing_field_count": validation["missing_field_count"],
        "invalid_field_count": validation["invalid_field_count"],
        "missing_fields": validation["missing_fields"],
        "invalid_fields": validation["invalid_fields"],
        "next_human_action": (
            "Run one real external customer or target-user session and fill the 12-question answer sheet."
            if not answer_exists
            else "Rerun this converter with --apply after confirming the answer sheet is complete and boundary-safe."
        ),
        **FALSE_FLAGS,
    }
    return payload, entry


def write_outputs(payload: dict[str, Any]) -> None:
    BASE.mkdir(parents=True, exist_ok=True)
    write_answer_template()
    write_json(SUMMARY, payload)
    missing = "\n".join(f"- `{field}`" for field in payload["missing_fields"]) or "- None"
    invalid = "\n".join(f"- `{field}`" for field in payload["invalid_fields"]) or "- None"
    REPORT.write_text(
        f"""# SAEE Minimum Session Answer Converter v0.1

Status: `{payload['status']}`.

This local converter lets a human reviewer record the 12 minimum external
customer-validation questions in a simple text sheet and convert them into the
existing session-entry JSON shape.

It does not contact customers, infer missing feedback, close blockers, launch
SAEE, claim customer validation, or claim production readiness.

## Files

- Source questions: `{payload['source_questions']}`
- Answer template: `{payload['answer_template']}`
- Human answer input: `{payload['human_answer_input']}`
- Target session entry: `{payload['target_session_entry']}`

## Current State

```yaml
external_customer_validation_minimum_session_answer_converter_v0_1: true
status: {payload['status']}
human_answer_input_exists: {str(payload['human_answer_input_exists']).lower()}
session_entry_written: {str(payload['session_entry_written']).lower()}
customer_validated: false
production_ready: false
product_launched: false
private_core_exposed: false
blockers_closed_by_converter: 0
```

## Missing Fields

{missing}

## Invalid Fields

{invalid}

## Human Use

After a real external customer or target-user session, fill:

`{payload['human_answer_input']}`

Then run:

```bash
python3 scripts/saee_external_customer_validation_minimum_session_answer_converter.py --apply
python3 scripts/saee_external_customer_validation_post_session_processor.py
```
""",
        encoding="utf-8",
    )
    BOUNDARY.write_text(
        f"""# SAEE Minimum Session Answer Converter Boundary Audit

external_customer_validation_minimum_session_answer_converter_v0_1: true
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
        """# SAEE Minimum Session Answer Converter Gate

answer: conditional

reason: Recommend this converter only as a local bridge after a real external customer or target-user session. It reduces evidence-entry friction but is not customer validation by itself.

boundary:
  customer_validated: false
  production_ready: false
  product_launched: false
  customer_contacted_by_codex: false
  private_core_exposed: false
  blockers_closed_by_converter: 0

next_action: Human must complete a real external session, fill the 12-question answer sheet, then run the converter with explicit `--apply`.
""",
        encoding="utf-8",
    )


def update_indexes(payload: dict[str, Any]) -> None:
    for line in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_answer_converter/minimum_session_answer_converter.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_answer_converter/minimum_session_answer_converter.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_answer_converter/minimum_session_answers.template.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_answer_converter/minimum_session_answer_converter_boundary_audit.md",
        "/docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_MINIMUM_SESSION_ANSWER_CONVERTER_GATE.md",
        "/scripts/saee_external_customer_validation_minimum_session_answer_converter.py",
        "/scripts/saee_external_customer_validation_minimum_session_answer_converter_smoke.py",
    ]:
        ensure_line(LLMS, line)
    index = read_json(AGENT_INDEX)
    index["external_customer_validation_minimum_session_answer_converter_v0_1"] = {
        "name": "SAEE Minimum Session Answer Converter v0.1",
        "status": payload["status"],
        "current_goal_blocker": payload["current_goal_blocker"],
        "minimum_question_count": 12,
        "human_answer_input_exists": payload["human_answer_input_exists"],
        "target_session_entry_exists": payload["target_session_entry_exists"],
        "session_entry_written": payload["session_entry_written"],
        "apply_requested": payload["apply_requested"],
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
        "blockers_closed_by_converter": 0,
        "entrypoints": {
            "summary": rel(SUMMARY),
            "report": rel(REPORT),
            "answer_template": rel(ANSWER_TEMPLATE),
            "boundary_audit": rel(BOUNDARY),
            "gate": rel(GATE),
            "runner": "scripts/saee_external_customer_validation_minimum_session_answer_converter.py",
            "smoke": "scripts/saee_external_customer_validation_minimum_session_answer_converter_smoke.py",
        },
    }
    write_json(AGENT_INDEX, index)
    block = f"""## Minimum Session Answer Converter v0.1

- `external_customer_validation_minimum_session_answer_converter_v0_1`
- Status: `{payload['status']}`
- Current blocker: `customer_validated`
- 12-question answer template: `{payload['answer_template']}`
- Target session entry: `{payload['target_session_entry']}`
- Explicit apply command: `python3 scripts/saee_external_customer_validation_minimum_session_answer_converter.py --apply`
- `customer_validated=false`; `production_ready=false`; `private_core_exposed=false`.
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_EXTERNAL_CUSTOMER_VALIDATION_MINIMUM_SESSION_ANSWER_CONVERTER_V0_1", block)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert 12-question minimum customer-validation answers.")
    parser.add_argument("--apply", action="store_true", help="write session-entry JSON if answers are complete")
    args = parser.parse_args()
    payload, _entry = build_payload(apply=args.apply)
    write_outputs(payload)
    update_indexes(payload)
    print(
        "SAEE_EXTERNAL_CUSTOMER_VALIDATION_MINIMUM_SESSION_ANSWER_CONVERTER: PASS "
        f"status={payload['status']} apply_requested={str(payload['apply_requested']).lower()} "
        "customer_validated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
