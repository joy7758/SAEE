#!/usr/bin/env python3
"""Record a local human confirmation without upgrading customer validation.

This records the user's latest local inspection confirmation as boundary-safe
evidence. It deliberately does not create external customer validation evidence,
does not write the final session-entry JSON, and does not close the
customer_validated blocker.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
OUT = EVIDENCE_DIR / "customer_validation_human_confirmation_boundary_record"
SUMMARY = OUT / "customer_validation_human_confirmation_boundary_record.local.json"
REPORT = OUT / "customer_validation_human_confirmation_boundary_record.md"
NEXT_INPUT = OUT / "customer_validation_next_required_input.md"
BOUNDARY = OUT / "customer_validation_human_confirmation_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_HUMAN_CONFIRMATION_BOUNDARY_RECORD_GATE.md"
ANSWER_TEMPLATE = EVIDENCE_DIR / "customer_validation_answer_intake_helper/customer_validation_answers.template.md"
ANSWER_INPUT = EVIDENCE_DIR / "customer_validation_answer_intake_helper/customer_validation_answers.human_filled.md"
TARGET_ENTRY = EVIDENCE_DIR / "external_customer_validation_session_entry.human_filled.local.json"
ANSWER_HELPER_SUMMARY = EVIDENCE_DIR / "customer_validation_answer_intake_helper/customer_validation_answer_intake_helper.local.json"
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


def build_payload() -> dict[str, Any]:
    helper = read_json(ANSWER_HELPER_SUMMARY)
    return {
        "customer_validation_human_confirmation_boundary_record_v0_1": True,
        "record_type": "local_human_confirmation_boundary_record",
        "status": "local_human_confirmation_recorded_customer_validation_still_missing",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "human_confirmation_text": "人工检查完毕，没有问题，确认",
        "confirmation_classification": "local_human_inspection_confirmation_not_external_customer_validation",
        "current_goal_blocker": "customer_validated",
        "customer_validation_acceptance": False,
        "reason_not_accepted_as_customer_validation": (
            "The confirmation does not include a real external customer or target-user session record, "
            "structured answers, participant role, candidate count, scores, or boundary confirmations."
        ),
        "answer_template": rel(ANSWER_TEMPLATE),
        "required_human_answer_input": rel(ANSWER_INPUT),
        "human_answer_input_exists": ANSWER_INPUT.exists(),
        "target_session_entry": rel(TARGET_ENTRY),
        "target_session_entry_exists": TARGET_ENTRY.exists(),
        "answer_intake_helper_status": helper.get("status"),
        "next_required_action": "Fill customer_validation_answers.human_filled.md from a real external customer or target-user session.",
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
        "blockers_closed_by_confirmation_record": 0,
    }


def write_outputs(payload: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(SUMMARY, payload)

    REPORT.write_text(
        f"""# SAEE Customer Validation Human Confirmation Boundary Record v0.1

Status: `{payload['status']}`.

The latest human statement was recorded as local inspection confirmation:

> 人工检查完毕，没有问题，确认

This is useful local review evidence, but it is not accepted as external
customer validation because it does not include a real external customer or
target-user session record.

```yaml
customer_validation_human_confirmation_boundary_record_v0_1: true
confirmation_classification: {payload['confirmation_classification']}
customer_validation_acceptance: false
current_goal_blocker: customer_validated
human_answer_input_exists: {str(payload['human_answer_input_exists']).lower()}
target_session_entry_exists: {str(payload['target_session_entry_exists']).lower()}
customer_validated: false
production_ready: false
product_launched: false
private_core_exposed: false
blockers_closed_by_confirmation_record: 0
```
""",
        encoding="utf-8",
    )

    NEXT_INPUT.write_text(
        f"""# Next Required Input For Customer Validation

Current blocker: `customer_validated`.

The local human confirmation has been recorded, but the next required input is
still a structured answer sheet from a real external customer or target-user
session.

Fill this file manually after the real session:

`{payload['required_human_answer_input']}`

Use this template:

`{payload['answer_template']}`

Do not use internal self-review, internal demo checks, or Codex-generated
answers as customer validation evidence.
""",
        encoding="utf-8",
    )

    BOUNDARY.write_text(
        f"""# SAEE Customer Validation Human Confirmation Boundary Audit

customer_validation_human_confirmation_boundary_record_v0_1: true
status: {payload['status']}

- Local human confirmation recorded: true
- Accepted as customer validation: false
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
- blockers_closed_by_confirmation_record: 0
""",
        encoding="utf-8",
    )

    GATE.write_text(
        """# SAEE Customer Validation Human Confirmation Boundary Record Gate

answer: local_confirmation_recorded_customer_validation_still_missing

reason: The local human inspection confirmation is recorded, but it is not a real external customer or target-user validation session and cannot close `customer_validated`.

boundary:
  customer_validated: false
  production_ready: false
  product_launched: false
  customer_contacted_by_codex: false
  private_core_exposed: false
  blockers_closed_by_confirmation_record: 0

next_action: Fill the structured answer sheet from a real external customer or target-user session, then request a separate apply/post-session processor run.
""",
        encoding="utf-8",
    )

    for line in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_human_confirmation_boundary_record/customer_validation_human_confirmation_boundary_record.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_human_confirmation_boundary_record/customer_validation_human_confirmation_boundary_record.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_human_confirmation_boundary_record/customer_validation_next_required_input.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_human_confirmation_boundary_record/customer_validation_human_confirmation_boundary_audit.md",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_HUMAN_CONFIRMATION_BOUNDARY_RECORD_GATE.md",
        "/scripts/saee_customer_validation_human_confirmation_boundary_record.py",
        "/scripts/saee_customer_validation_human_confirmation_boundary_record_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["customer_validation_human_confirmation_boundary_record_v0_1"] = {
        "name": "SAEE Customer Validation Human Confirmation Boundary Record v0.1",
        "status": payload["status"],
        "confirmation_classification": payload["confirmation_classification"],
        "current_goal_blocker": "customer_validated",
        "customer_validation_acceptance": False,
        "human_answer_input_exists": payload["human_answer_input_exists"],
        "target_session_entry_exists": payload["target_session_entry_exists"],
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
        "blockers_closed_by_confirmation_record": 0,
        "entrypoints": {
            "summary": rel(SUMMARY),
            "report": rel(REPORT),
            "next_required_input": rel(NEXT_INPUT),
            "boundary_audit": rel(BOUNDARY),
            "gate": rel(GATE),
            "runner": "scripts/saee_customer_validation_human_confirmation_boundary_record.py",
            "smoke": "scripts/saee_customer_validation_human_confirmation_boundary_record_smoke.py",
        },
    }
    AGENT_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    block = f"""## Customer Validation Human Confirmation Boundary Record v0.1

- `customer_validation_human_confirmation_boundary_record_v0_1`
- Status: `{payload['status']}`
- Recorded statement: `人工检查完毕，没有问题，确认`
- Classification: `{payload['confirmation_classification']}`
- Current blocker: `customer_validated`
- Next required input: `{payload['required_human_answer_input']}`
- `customer_validated=false`; `production_ready=false`; `private_core_exposed=false`.
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_CUSTOMER_VALIDATION_HUMAN_CONFIRMATION_BOUNDARY_RECORD_V0_1", block)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_CUSTOMER_VALIDATION_HUMAN_CONFIRMATION_BOUNDARY_RECORD: PASS "
        f"status={payload['status']} customer_validated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
