#!/usr/bin/env python3
"""Stage 13 live-interview answers into a full answer-sheet draft.

Input is a simple key/value file with only the 13 customer-answer fields from
the live interview card. Output is a draft full answer sheet that keeps session
metadata, boundary confirmations, and human review confirmations blank. This
reduces field-mapping friction without creating official customer evidence.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
CARD = EVIDENCE / "customer_validation_live_interview_card"
INPUT = CARD / "customer_validation_live_interview_answers.human_filled.md"
OUT = EVIDENCE / "customer_validation_interview_answer_stager"
SUMMARY = OUT / "customer_validation_interview_answer_stager.local.json"
REPORT = OUT / "customer_validation_interview_answer_stager.md"
INPUT_TEMPLATE = OUT / "customer_validation_live_interview_answers.template.md"
STAGED_DRAFT = OUT / "customer_validation_answers.staged_from_interview.local.md"
BOUNDARY = OUT / "customer_validation_interview_answer_stager_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_INTERVIEW_ANSWER_STAGER_GATE.md"
ANSWER_TEMPLATE = EVIDENCE / "customer_validation_answer_intake_helper/customer_validation_answers.template.md"
ANSWER_TARGET = EVIDENCE / "customer_validation_answer_intake_helper/customer_validation_answers.human_filled.md"
CARD_SUMMARY = CARD / "customer_validation_live_interview_card.local.json"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
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


def parse_key_values(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
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
        values[key.strip()] = value.strip()
    return values


def customer_fields() -> list[str]:
    card = read_json(CARD_SUMMARY)
    return [item["field"] for item in card.get("interview_questions", [])]


def render_template(fields: list[str]) -> str:
    lines = [
        "# SAEE 13-question customer interview answers",
        "# Fill only after a real external customer or target-user interview.",
    ]
    lines.extend(f"{field}:" for field in fields)
    return "\n".join(lines) + "\n"


def render_staged_draft(values: dict[str, str]) -> str:
    template_lines = ANSWER_TEMPLATE.read_text(encoding="utf-8").splitlines()
    output: list[str] = []
    for line in template_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            output.append(line)
            continue
        key, _ = stripped.split(":", 1)
        key = key.strip()
        if key in values:
            output.append(f"{key}: {values[key]}")
        else:
            output.append(line)
    output.append("")
    output.append("# This is a staged draft, not official customer validation evidence.")
    output.append("# Copy to customer_validation_answers.human_filled.md only after completing")
    output.append("# session metadata, boundary confirmations, and human review confirmations.")
    return "\n".join(output) + "\n"


def build_payload() -> dict[str, Any]:
    fields = customer_fields()
    values = parse_key_values(INPUT)
    missing = [field for field in fields if not values.get(field, "").strip()]
    extra = sorted(field for field in values if field not in fields)
    status = "ready_staged_draft_from_customer_answers" if INPUT.exists() and not missing else "hold_interview_answers_missing_or_incomplete"
    return {
        "customer_validation_interview_answer_stager_v0_1": True,
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_goal_blocker": "customer_validated",
        "input_path": rel(INPUT),
        "input_exists": INPUT.exists(),
        "staged_draft_path": rel(STAGED_DRAFT),
        "official_answer_target": rel(ANSWER_TARGET),
        "customer_field_count": len(fields),
        "answered_customer_field_count": len([field for field in fields if values.get(field, "").strip()]),
        "missing_customer_field_count": len(missing),
        "missing_customer_fields": missing,
        "extra_input_fields": extra,
        "staged_draft_written": INPUT.exists() and not missing,
        "official_answer_sheet_written": False,
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
        "blockers_closed_by_stager": 0,
    }


def write_outputs(payload: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fields = customer_fields()
    values = parse_key_values(INPUT)
    INPUT_TEMPLATE.write_text(render_template(fields), encoding="utf-8")
    if payload["staged_draft_written"]:
        STAGED_DRAFT.write_text(render_staged_draft(values), encoding="utf-8")
    elif STAGED_DRAFT.exists():
        STAGED_DRAFT.unlink()
    write_json(SUMMARY, payload)
    REPORT.write_text(
        f"""# SAEE Customer Validation Interview Answer Stager v0.1

Status: `{payload['status']}`.

This helper converts the 13 live-interview answers into a full answer-sheet
draft. The draft is not official customer validation evidence. It still needs
session metadata, boundary confirmations, and human review confirmations before
the official answer sheet can be created.

## Current State

- input_exists: `{payload['input_exists']}`
- customer_field_count: `{payload['customer_field_count']}`
- answered_customer_field_count: `{payload['answered_customer_field_count']}`
- missing_customer_field_count: `{payload['missing_customer_field_count']}`
- staged_draft_written: `{payload['staged_draft_written']}`
- official_answer_sheet_written: false
- customer_validated=false
- production_ready=false
- private_core_exposed=false
- blockers_closed_by_stager=0

## Human Use

1. Fill: `{payload['input_path']}`
2. Run: `python3 scripts/saee_customer_validation_interview_answer_stager.py`
3. Review the staged draft: `{payload['staged_draft_path']}`
4. Complete the remaining metadata and boundary confirmations manually before
   creating `{payload['official_answer_target']}`.
""",
        encoding="utf-8",
    )
    BOUNDARY.write_text(
        f"""# SAEE Customer Validation Interview Answer Stager Boundary Audit

customer_validation_interview_answer_stager_v0_1: true
status: {payload['status']}

- official_answer_sheet_written: false
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
- blockers_closed_by_stager: 0
""",
        encoding="utf-8",
    )
    GATE.write_text(
        """# SAEE Customer Validation Interview Answer Stager Gate

answer: staged_customer_answers_only_no_validation_claim

reason: The stager can map 13 real customer answers into a draft answer sheet,
but it does not write official evidence or claim customer validation.

boundary:
  official_answer_sheet_written: false
  customer_validated: false
  production_ready: false
  product_launched: false
  customer_contacted_by_codex: false
  private_core_exposed: false
  blockers_closed_by_stager: 0

next_action: Human completes metadata, boundary confirmations, and review
confirmations before creating the official human-filled answer sheet.
""",
        encoding="utf-8",
    )


def update_indexes(payload: dict[str, Any]) -> None:
    for line in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_interview_answer_stager/customer_validation_interview_answer_stager.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_interview_answer_stager/customer_validation_interview_answer_stager.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_interview_answer_stager/customer_validation_live_interview_answers.template.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_interview_answer_stager/customer_validation_answers.staged_from_interview.local.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_interview_answer_stager/customer_validation_interview_answer_stager_boundary_audit.md",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_INTERVIEW_ANSWER_STAGER_GATE.md",
        "/scripts/saee_customer_validation_interview_answer_stager.py",
        "/scripts/saee_customer_validation_interview_answer_stager_smoke.py",
    ]:
        ensure_line(LLMS, line)
    index = read_json(AGENT_INDEX)
    index["customer_validation_interview_answer_stager_v0_1"] = {
        "name": "SAEE Customer Validation Interview Answer Stager v0.1",
        "status": payload["status"],
        "current_goal_blocker": "customer_validated",
        "input_exists": payload["input_exists"],
        "customer_field_count": payload["customer_field_count"],
        "answered_customer_field_count": payload["answered_customer_field_count"],
        "missing_customer_field_count": payload["missing_customer_field_count"],
        "staged_draft_written": payload["staged_draft_written"],
        "official_answer_sheet_written": False,
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
        "blockers_closed_by_stager": 0,
        "entrypoints": {
            "input_template": rel(INPUT_TEMPLATE),
            "input_path": rel(INPUT),
            "staged_draft": rel(STAGED_DRAFT),
            "summary": rel(SUMMARY),
            "report": rel(REPORT),
            "boundary_audit": rel(BOUNDARY),
            "gate": rel(GATE),
            "runner": "scripts/saee_customer_validation_interview_answer_stager.py",
            "smoke": "scripts/saee_customer_validation_interview_answer_stager_smoke.py",
        },
    }
    write_json(AGENT_INDEX, index)
    block = f"""## Customer Validation Interview Answer Stager v0.1

- `customer_validation_interview_answer_stager_v0_1`
- Status: `{payload['status']}`
- Current blocker: `customer_validated`
- Customer fields: `{payload['customer_field_count']}`
- Input template: `phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_interview_answer_stager/customer_validation_live_interview_answers.template.md`
- `customer_validated=false`; `production_ready=false`; `private_core_exposed=false`.
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_CUSTOMER_VALIDATION_INTERVIEW_ANSWER_STAGER_V0_1", block)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    update_indexes(payload)
    print(
        "SAEE_CUSTOMER_VALIDATION_INTERVIEW_ANSWER_STAGER: PASS "
        f"status={payload['status']} answered={payload['answered_customer_field_count']}/"
        f"{payload['customer_field_count']} customer_validated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
