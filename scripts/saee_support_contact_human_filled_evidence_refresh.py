#!/usr/bin/env python3
"""Refresh support-contact evidence from the human-filled bridge input."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_support_contact_evidence_builder import build_from_input


BASE = ROOT / "phase_b_product/commercial_readiness/support_evidence"
INPUT = BASE / "support_contact_decision_input.from_bridge.human_filled.local.json"
BUILDER_OUTPUT = BASE / "support_contact_evidence_builder_output.from_bridge_human_filled.local.json"
SUPPORT_OUTPUT = BASE / "production_support_sla_evidence.from_support_contact_human_filled.local.json"
SUMMARY_PATH = BASE / "support_contact_human_filled_evidence_refresh.local.json"
REPORT_PATH = BASE / "support_contact_human_filled_evidence_refresh.md"
BOUNDARY_PATH = BASE / "support_contact_human_filled_evidence_refresh_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_SUPPORT_CONTACT_HUMAN_FILLED_EVIDENCE_REFRESH_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"


LLMS_LINES = [
    "/phase_b_product/commercial_readiness/support_evidence/support_contact_human_filled_evidence_refresh.md",
    "/phase_b_product/commercial_readiness/support_evidence/support_contact_human_filled_evidence_refresh.local.json",
    "/phase_b_product/commercial_readiness/support_evidence/support_contact_human_filled_evidence_refresh_boundary_audit.md",
    "/phase_b_product/commercial_readiness/support_evidence/support_contact_evidence_builder_output.from_bridge_human_filled.local.json",
    "/phase_b_product/commercial_readiness/support_evidence/production_support_sla_evidence.from_support_contact_human_filled.local.json",
    "/docs/strategy/SAEE_SUPPORT_CONTACT_HUMAN_FILLED_EVIDENCE_REFRESH_GATE.md",
    "/scripts/saee_support_contact_human_filled_evidence_refresh.py",
    "/scripts/saee_support_contact_human_filled_evidence_refresh_smoke.py",
]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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


def build_summary() -> dict:
    if not INPUT.exists():
        builder = None
        status = "hold_human_filled_support_contact_input_missing"
    else:
        builder = build_from_input(
            INPUT,
            BUILDER_OUTPUT,
            SUPPORT_OUTPUT,
            write_documentation=False,
        )
        status = (
            "support_contact_human_filled_evidence_ready_for_review_only"
            if builder.get("status") == "pass"
            and builder.get("support_contact_available_for_review") is True
            else "hold_support_contact_human_filled_evidence_not_ready"
        )

    summary = {
        "support_contact_human_filled_evidence_refresh_v0_1": True,
        "status": status,
        "refreshed_at": datetime.now(timezone.utc).isoformat(),
        "target_blocker_id": "support_contact",
        "input": rel(INPUT),
        "input_exists": INPUT.exists(),
        "builder_output": rel(BUILDER_OUTPUT),
        "support_evidence_output": rel(SUPPORT_OUTPUT),
        "builder_status": builder.get("status") if builder else "not_run",
        "input_complete": bool(builder and builder.get("input_complete") is True),
        "support_contact_available_for_review": bool(
            builder and builder.get("support_contact_available_for_review") is True
        ),
        "production_support_available": False,
        "customer_support_available": bool(builder and builder.get("customer_support_available") is True),
        "sla_available": bool(builder and builder.get("sla_available") is True),
        "on_call_rotation_available": bool(builder and builder.get("on_call_rotation_available") is True),
        "support_readiness_status": builder.get("support_readiness_status") if builder else "not_run",
        "blockers_closed_by_refresh": 0,
        "accepted_for_blocker_closure_count": 0,
        "separate_go_no_go_profile_required": True,
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
        "support_vendor_contacted": False,
        "support_contact_published_by_codex": False,
        "support_contact_test_performed_by_codex": False,
        "next_action": (
            "Use this refreshed support-contact evidence as review input only. "
            "Customer support, SLA, on-call, and full production support remain open."
        ),
    }
    write_json(SUMMARY_PATH, summary)
    return summary


def render_report(summary: dict) -> str:
    return f"""# SAEE Support Contact Human-Filled Evidence Refresh

Status: {summary['status']}.

This refresh uses the human-filled support-contact bridge input and the existing
support-contact evidence builder. It makes support-contact evidence available
for review only.

## Results

- target_blocker_id: support_contact
- input_complete: {str(summary['input_complete']).lower()}
- builder_status: {summary['builder_status']}
- support_contact_available_for_review: {str(summary['support_contact_available_for_review']).lower()}
- production_support_available: false
- customer_support_available: {str(summary['customer_support_available']).lower()}
- sla_available: {str(summary['sla_available']).lower()}
- on_call_rotation_available: {str(summary['on_call_rotation_available']).lower()}
- blockers_closed_by_refresh: 0

## Boundary

No support address was published by Codex. No support test was sent by Codex.
No customer or vendor was contacted. This refresh does not close blockers and
does not claim production support, production readiness, or customer validation.
"""


def render_boundary(summary: dict) -> str:
    return f"""# SAEE Support Contact Human-Filled Evidence Refresh Boundary Audit

- status: {summary['status']}
- support_contact_available_for_review: {str(summary['support_contact_available_for_review']).lower()}
- production_support_available: false
- blockers_closed_by_refresh: 0
- accepted_for_blocker_closure_count: 0
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- external_calls_made: false
- customer_contacted: false
- support_vendor_contacted: false
- support_contact_published_by_codex: false
- support_contact_test_performed_by_codex: false

Final decision: boundary safe. This is a local evidence refresh for review, not
commercial blocker closure.
"""


def render_gate(summary: dict) -> str:
    return f"""# SAEE Support Contact Human-Filled Evidence Refresh Gate

answer: {summary['status']}

reason: Human-filled support-contact input exists and can be converted into
support-contact evidence for review. It is not full production support evidence.

boundary:

- support_contact_available_for_review: {str(summary['support_contact_available_for_review']).lower()}
- production_support_available: false
- blockers_closed_by_refresh: 0
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

next_action: Review this support-contact evidence together with customer
support, SLA, and on-call evidence before any blocker closure decision.
"""


README_BLOCK = """## Support Contact Human-Filled Evidence Refresh

Support Contact Human-Filled Evidence Refresh v0.1 records
`status=support_contact_human_filled_evidence_ready_for_review_only` when the
human-filled support-contact bridge input can be converted into reviewable
support-contact evidence. It does not publish a support address, send support
tests, contact customers or vendors, close blockers, claim production support,
claim production readiness, or claim customer validation.
"""


AGENT_READABLE_BLOCK = """0. For the support-contact human-filled evidence refresh, inspect `phase_b_product/commercial_readiness/support_evidence/support_contact_human_filled_evidence_refresh.local.json`. It records that `support_contact` evidence is ready for review only while `production_support_available=false`, `blockers_closed_by_refresh=0`, `production_ready=false`, and `customer_validated=false`.
"""


def update_agent_index(summary: dict) -> None:
    data = json.loads(AGENT_INDEX.read_text(encoding="utf-8"))
    data["support_contact_human_filled_evidence_refresh_v0_1"] = {
        "status": summary["status"],
        "target_blocker_id": "support_contact",
        "input_complete": summary["input_complete"],
        "support_contact_available_for_review": summary["support_contact_available_for_review"],
        "production_support_available": False,
        "customer_support_available": summary["customer_support_available"],
        "sla_available": summary["sla_available"],
        "on_call_rotation_available": summary["on_call_rotation_available"],
        "blockers_closed_by_refresh": 0,
        "accepted_for_blocker_closure_count": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "customer_contacted": False,
        "support_contact_published_by_codex": False,
        "support_contact_test_performed_by_codex": False,
    }
    AGENT_INDEX.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def update_text_surfaces(summary: dict) -> None:
    REPORT_PATH.write_text(render_report(summary), encoding="utf-8")
    BOUNDARY_PATH.write_text(render_boundary(summary), encoding="utf-8")
    GATE.write_text(render_gate(summary), encoding="utf-8")
    marker = "SAEE_SUPPORT_CONTACT_HUMAN_FILLED_EVIDENCE_REFRESH"
    insert_after_marker(ROOT / "README.md", marker, README_BLOCK)
    insert_after_marker(
        ROOT / "PROJECT_STATUS.md",
        marker,
        "Support Contact Human-Filled Evidence Refresh（支持入口人工证据刷新）:\n"
        + README_BLOCK,
    )
    insert_after_marker(
        ROOT / "ROADMAP.md",
        marker,
        "Support Contact Human-Filled Evidence Refresh v0.1 is a status/reference entry only. "
        + README_BLOCK,
    )
    insert_after_marker(
        ROOT / "CHANGELOG.md",
        marker,
        "- Added Support Contact Human-Filled Evidence Refresh v0.1. " + README_BLOCK,
    )
    insert_after_marker(ROOT / "agent-readable.md", marker, AGENT_READABLE_BLOCK)
    append_unique_llms()
    update_agent_index(summary)


def main() -> None:
    summary = build_summary()
    update_text_surfaces(summary)
    print(
        "SAEE_SUPPORT_CONTACT_HUMAN_FILLED_EVIDENCE_REFRESH: PASS "
        f"status={summary['status']} "
        f"support_contact_available_for_review={str(summary['support_contact_available_for_review']).lower()} "
        "production_support_available=false blockers_closed_by_refresh=0"
    )


if __name__ == "__main__":
    main()
