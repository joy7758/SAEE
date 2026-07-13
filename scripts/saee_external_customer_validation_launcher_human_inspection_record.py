#!/usr/bin/env python3
"""Record human inspection of the local customer-validation launcher."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = (
    ROOT
    / "phase_b_product/commercial_readiness/customer_validation_evidence/"
    "external_customer_validation_local_session_launcher"
)
SUMMARY_PATH = BASE / "launcher_human_inspection_record.local.json"
REPORT_PATH = BASE / "launcher_human_inspection_record.md"
BOUNDARY_PATH = BASE / "launcher_human_inspection_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_LAUNCHER_HUMAN_INSPECTION_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"


SUMMARY = {
    "external_customer_validation_launcher_human_inspection_record_v0_1": True,
    "status": "launcher_human_inspection_confirmed_no_issue",
    "inspection_subject": (
        "phase_b_product/commercial_readiness/customer_validation_evidence/"
        "external_customer_validation_local_session_launcher/"
        "external_customer_validation_local_session_launcher.html"
    ),
    "inspection_source": "human_confirmation_in_current_codex_thread",
    "human_inspection_confirmed": True,
    "human_reported_issue_count": 0,
    "current_goal_blocker": "customer_validated",
    "next_human_action": "Run one real external customer or target-user validation session.",
    "external_customer_session_performed": False,
    "human_external_session_required": True,
    "customer_contacted_by_codex": False,
    "customer_validated": False,
    "production_ready": False,
    "product_launched": False,
    "private_core_exposed": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "public_sdk_released": False,
    "blockers_closed_by_inspection": 0,
}


REPORT = """# SAEE Customer Validation Launcher Human Inspection Record

Status: launcher_human_inspection_confirmed_no_issue.

The human reviewer confirmed that the local customer-validation session
launcher has no issue for the intended manual flow. This records inspection of
the local launcher only.

## What This Confirms

- The launcher can be used as the next human entry point.
- The session-day sequence is acceptable for manual execution.
- No launcher issue was reported by the human reviewer.

## What This Does Not Confirm

- It does not mean a real external customer session happened.
- It does not mean `customer_validated` is satisfied.
- It does not mean SAEE is production-ready.
- It does not authorize product launch, customer contact by Codex, SDK release,
  backend changes, runtime changes, API schema changes, or private core
  disclosure.

## Next Action

Run one real external customer or target-user validation session, save the
generated JSON, then run the post-session processor.
"""


BOUNDARY = """# SAEE Customer Validation Launcher Human Inspection Boundary Audit

- Human inspection of launcher recorded.
- No real external customer session performed by Codex.
- No customer contacted by Codex.
- No external calls made.
- No runtime modified.
- No backend modified.
- No kernel modified.
- No API schema modified.
- No private core exposed.
- No product launched.
- No customer validation claimed.
- No production-ready claim added.
- No blocker closed by this inspection record.

Final decision: boundary safe. Inspection confirms the launcher is acceptable
for human use, but the `customer_validated` blocker remains open.
"""


GATE_TEXT = """# SAEE External Customer Validation Launcher Human Inspection Gate

answer: launcher_human_inspection_confirmed_no_issue

reason: The human reviewer confirmed that the local customer-validation session
launcher has no issue. This is an inspection record only and is not customer
validation evidence.

boundary:

- human_inspection_confirmed: true
- external_customer_session_performed: false
- customer_validated: false
- production_ready: false
- product_launched: false
- customer_contacted_by_codex: false
- private_core_exposed: false
- blockers_closed_by_inspection: 0

next_action: Run one real external customer or target-user validation session.
"""


README_BLOCK = """## Customer Validation Launcher Human Inspection Record

Customer Validation Launcher Human Inspection Record v0.1 records
`status=launcher_human_inspection_confirmed_no_issue` after human inspection of
the local launcher. It confirms the launcher is acceptable for manual use, but
does not perform a customer session, contact customers, close
`customer_validated`, claim production readiness, launch product, or expose
private core.
"""


AGENT_READABLE_BLOCK = """0. For the customer validation launcher human inspection record, inspect `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_local_session_launcher/launcher_human_inspection_record.local.json`. It records human confirmation that the local launcher has no issue, while `customer_validated=false`, `production_ready=false`, and `blockers_closed_by_inspection=0` remain true.
"""


LLMS_LINES = [
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_local_session_launcher/launcher_human_inspection_record.md",
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_local_session_launcher/launcher_human_inspection_record.local.json",
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_local_session_launcher/launcher_human_inspection_boundary_audit.md",
    "/docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_LAUNCHER_HUMAN_INSPECTION_GATE.md",
]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"recorded_at": datetime.now(timezone.utc).isoformat(), **data}
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def insert_after_marker(path: Path, marker: str, block: str) -> None:
    text = path.read_text(encoding="utf-8")
    start = f"<!-- BEGIN {marker} -->"
    end = f"<!-- END {marker} -->"
    wrapped = f"{start}\n\n{block.rstrip()}\n\n{end}\n\n"
    if start in text and end in text:
        before, rest = text.split(start, 1)
        _, after = rest.split(end, 1)
        path.write_text(before + wrapped + after.lstrip("\n"), encoding="utf-8")
        return
    insert_at = text.find("\n\n")
    if insert_at == -1:
        path.write_text(text.rstrip() + "\n\n" + wrapped, encoding="utf-8")
    else:
        path.write_text(text[: insert_at + 2] + wrapped + text[insert_at + 2 :], encoding="utf-8")


def append_unique_llms() -> None:
    text = LLMS.read_text(encoding="utf-8") if LLMS.exists() else ""
    lines = text.splitlines()
    changed = False
    for line in LLMS_LINES:
        if line not in lines:
            lines.append(line)
            changed = True
    if changed:
        LLMS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_agent_index() -> None:
    data = json.loads(AGENT_INDEX.read_text(encoding="utf-8"))
    data["external_customer_validation_launcher_human_inspection_record_v0_1"] = {
        "status": SUMMARY["status"],
        "inspection_subject": SUMMARY["inspection_subject"],
        "human_inspection_confirmed": True,
        "human_reported_issue_count": 0,
        "current_goal_blocker": "customer_validated",
        "external_customer_session_performed": False,
        "customer_contacted_by_codex": False,
        "customer_validated": False,
        "production_ready": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "blockers_closed_by_inspection": 0,
    }
    AGENT_INDEX.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    write_json(SUMMARY_PATH, SUMMARY)
    write(REPORT_PATH, REPORT)
    write(BOUNDARY_PATH, BOUNDARY)
    write(GATE, GATE_TEXT)
    marker = "SAEE_EXTERNAL_CUSTOMER_VALIDATION_LAUNCHER_HUMAN_INSPECTION"
    insert_after_marker(ROOT / "README.md", marker, README_BLOCK)
    insert_after_marker(
        ROOT / "PROJECT_STATUS.md",
        marker,
        "Customer Validation Launcher Human Inspection（客户验证启动器人工检查）:\n"
        + README_BLOCK,
    )
    insert_after_marker(
        ROOT / "ROADMAP.md",
        marker,
        "Customer Validation Launcher Human Inspection Record v0.1 is a status/reference entry only. "
        + README_BLOCK,
    )
    insert_after_marker(
        ROOT / "CHANGELOG.md",
        marker,
        "- Added Customer Validation Launcher Human Inspection Record v0.1. " + README_BLOCK,
    )
    insert_after_marker(ROOT / "agent-readable.md", marker, AGENT_READABLE_BLOCK)
    append_unique_llms()
    update_agent_index()
    print("SAEE_EXTERNAL_CUSTOMER_VALIDATION_LAUNCHER_HUMAN_INSPECTION_RECORD: generated")


if __name__ == "__main__":
    main()
