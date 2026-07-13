#!/usr/bin/env python3
"""Run the local customer-validation answer-to-evidence pipeline.

This is a convenience orchestrator for the existing local customer-validation
surfaces:

1. answer-sheet preflight
2. answer-to-session-entry converter
3. post-session processor

It never contacts customers, never infers missing feedback, and never closes
the customer_validated blocker. By default it only refreshes hold-state outputs.
With ``--apply`` it requests conversion only if the human-filled answer sheet is
complete and boundary-safe according to the existing converter.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
OUT = EVIDENCE / "customer_validation_answer_to_evidence_pipeline"
SUMMARY = OUT / "customer_validation_answer_to_evidence_pipeline.local.json"
REPORT = OUT / "customer_validation_answer_to_evidence_pipeline.md"
BOUNDARY = OUT / "customer_validation_answer_to_evidence_pipeline_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_ANSWER_TO_EVIDENCE_PIPELINE_GATE.md"
ANSWER_INPUT = EVIDENCE / "customer_validation_answer_intake_helper/customer_validation_answers.human_filled.md"
SESSION_ENTRY = EVIDENCE / "external_customer_validation_session_entry.human_filled.local.json"
PREFLIGHT_SUMMARY = EVIDENCE / "customer_validation_answer_sheet_preflight/customer_validation_answer_sheet_preflight.local.json"
CONVERTER_SUMMARY = EVIDENCE / "customer_validation_answer_to_session_entry_converter/customer_validation_answer_to_session_entry_converter.local.json"
PROCESSOR_SUMMARY = EVIDENCE / "external_customer_validation_post_session_processor/external_customer_validation_post_session_processor.local.json"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
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


def run_local_script(script: str, *args: str) -> str:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script), *args],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def pipeline_status(apply: bool, preflight: dict[str, Any], converter: dict[str, Any], processor: dict[str, Any]) -> str:
    if not ANSWER_INPUT.exists():
        return "hold_human_answer_sheet_missing"
    if converter.get("status") == "hold_human_answer_sheet_incomplete_or_invalid":
        return "hold_human_answer_sheet_incomplete_or_invalid"
    if not apply and converter.get("status") == "ready_for_apply_conversion":
        return "ready_for_explicit_apply"
    if apply and converter.get("session_entry_written") is True:
        return "processed_pending_human_go_no_go_review"
    if preflight.get("ready_for_explicit_apply_request") is True:
        return "ready_for_explicit_apply"
    return "hold_human_answer_sheet_missing"


def build_payload(apply: bool) -> dict[str, Any]:
    preflight_stdout = run_local_script("saee_customer_validation_answer_sheet_preflight.py")
    converter_args = ["--apply"] if apply else []
    converter_stdout = run_local_script("saee_customer_validation_answer_to_session_entry_converter.py", *converter_args)
    processor_stdout = run_local_script("saee_external_customer_validation_post_session_processor.py")
    preflight = read_json(PREFLIGHT_SUMMARY)
    converter = read_json(CONVERTER_SUMMARY)
    processor = read_json(PROCESSOR_SUMMARY)
    status = pipeline_status(apply, preflight, converter, processor)
    return {
        "customer_validation_answer_to_evidence_pipeline_v0_1": True,
        "pipeline_type": "local_human_answer_sheet_to_customer_validation_evidence_pipeline",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_goal_blocker": "customer_validated",
        "human_answer_input": rel(ANSWER_INPUT),
        "human_answer_input_exists": ANSWER_INPUT.exists(),
        "session_entry": rel(SESSION_ENTRY),
        "session_entry_exists": SESSION_ENTRY.exists(),
        "apply_requested": apply,
        "preflight_status": preflight.get("status"),
        "preflight_ready_for_apply": preflight.get("ready_for_explicit_apply_request"),
        "converter_status": converter.get("status"),
        "converter_session_entry_written": converter.get("session_entry_written"),
        "processor_status": processor.get("status"),
        "processor_evidence_builder_ran": processor.get("evidence_builder_ran"),
        "processor_commercial_go_no_go_status": processor.get("commercial_go_no_go_status"),
        "blockers_closed_by_pipeline": 0,
        "preflight_stdout": preflight_stdout,
        "converter_stdout": converter_stdout,
        "processor_stdout": processor_stdout,
        "next_human_action": (
            "Run a real external customer or target-user session and fill the plain Chinese answer sheet."
            if not ANSWER_INPUT.exists()
            else "If the answer sheet is complete and boundary-safe, rerun this pipeline with --apply."
        ),
        **FALSE_FLAGS,
    }


def write_outputs(payload: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(SUMMARY, payload)
    REPORT.write_text(
        f"""# SAEE Customer Validation Answer-to-Evidence Pipeline v0.1

Status: `{payload['status']}`.

This local pipeline reduces the manual steps after a real external customer or
target-user session. It runs the existing answer-sheet preflight, the existing
answer-to-session-entry converter, and the existing post-session processor.

It does not contact customers, infer feedback, close blockers, launch SAEE, or
claim customer validation.

## Current State

- human_answer_input_exists: `{payload['human_answer_input_exists']}`
- apply_requested: `{payload['apply_requested']}`
- preflight_status: `{payload['preflight_status']}`
- converter_status: `{payload['converter_status']}`
- converter_session_entry_written: `{payload['converter_session_entry_written']}`
- processor_status: `{payload['processor_status']}`
- customer_validated=false
- production_ready=false
- product_launched=false
- private_core_exposed=false
- blockers_closed_by_pipeline=0

## Human Use

After a real external customer or target-user session, fill:

`{payload['human_answer_input']}`

Then run:

```bash
python3 scripts/saee_customer_validation_answer_to_evidence_pipeline.py --apply
```
""",
        encoding="utf-8",
    )
    BOUNDARY.write_text(
        f"""# SAEE Customer Validation Answer-to-Evidence Pipeline Boundary Audit

customer_validation_answer_to_evidence_pipeline_v0_1: true
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
- blockers_closed_by_pipeline: 0
""",
        encoding="utf-8",
    )
    GATE.write_text(
        """# SAEE Customer Validation Answer-to-Evidence Pipeline Gate

answer: local_pipeline_ready_explicit_apply_required

reason: The local pipeline can process a real human-filled customer-validation
answer sheet through existing local validators and processors. It requires
explicit `--apply` and does not replace the real customer session.

boundary:
  customer_validated: false
  production_ready: false
  product_launched: false
  customer_contacted_by_codex: false
  private_core_exposed: false
  blockers_closed_by_pipeline: 0

next_action: Run a real customer or target-user session, fill the answer sheet,
then run the pipeline with `--apply` only after the answer sheet is complete.
""",
        encoding="utf-8",
    )


def update_indexes(payload: dict[str, Any]) -> None:
    for line in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_to_evidence_pipeline/customer_validation_answer_to_evidence_pipeline.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_to_evidence_pipeline/customer_validation_answer_to_evidence_pipeline.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_to_evidence_pipeline/customer_validation_answer_to_evidence_pipeline_boundary_audit.md",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_ANSWER_TO_EVIDENCE_PIPELINE_GATE.md",
        "/scripts/saee_customer_validation_answer_to_evidence_pipeline.py",
        "/scripts/saee_customer_validation_answer_to_evidence_pipeline_smoke.py",
    ]:
        ensure_line(LLMS, line)
    index = read_json(AGENT_INDEX)
    index["customer_validation_answer_to_evidence_pipeline_v0_1"] = {
        "name": "SAEE Customer Validation Answer-to-Evidence Pipeline v0.1",
        "status": payload["status"],
        "current_goal_blocker": payload["current_goal_blocker"],
        "human_answer_input_exists": payload["human_answer_input_exists"],
        "session_entry_exists": payload["session_entry_exists"],
        "apply_requested": payload["apply_requested"],
        "preflight_status": payload["preflight_status"],
        "converter_status": payload["converter_status"],
        "processor_status": payload["processor_status"],
        "blockers_closed_by_pipeline": 0,
        **FALSE_FLAGS,
        "entrypoints": {
            "summary": rel(SUMMARY),
            "report": rel(REPORT),
            "boundary_audit": rel(BOUNDARY),
            "gate": rel(GATE),
            "runner": "scripts/saee_customer_validation_answer_to_evidence_pipeline.py",
            "smoke": "scripts/saee_customer_validation_answer_to_evidence_pipeline_smoke.py",
        },
    }
    write_json(AGENT_INDEX, index)
    block = f"""## Customer Validation Answer-to-Evidence Pipeline v0.1

- `customer_validation_answer_to_evidence_pipeline_v0_1`
- Status: `{payload['status']}`
- Current blocker: `customer_validated`
- Human answer input exists: `{payload['human_answer_input_exists']}`
- Explicit apply command: `python3 scripts/saee_customer_validation_answer_to_evidence_pipeline.py --apply`
- `customer_validated=false`; `production_ready=false`; `private_core_exposed=false`.
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_CUSTOMER_VALIDATION_ANSWER_TO_EVIDENCE_PIPELINE_V0_1", block)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the local customer-validation answer-to-evidence pipeline.")
    parser.add_argument("--apply", action="store_true", help="Apply conversion if the human answer sheet is complete.")
    parser.add_argument("--json", action="store_true", help="Print summary JSON.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    payload = build_payload(args.apply)
    write_outputs(payload)
    update_indexes(payload)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(
            "SAEE_CUSTOMER_VALIDATION_ANSWER_TO_EVIDENCE_PIPELINE: PASS "
            f"status={payload['status']} apply_requested={str(payload['apply_requested']).lower()} "
            "customer_validated=false production_ready=false"
        )


if __name__ == "__main__":
    main()
