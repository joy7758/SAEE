#!/usr/bin/env python3
"""Refresh the human-filled support group evidence profile.

This refresh combines the already human-filled support-contact,
customer-support, SLA, and on-call evidence files into one local review profile.
It does not publish a support contact, start support operations, contact
customers or vendors, close blockers, or claim production readiness.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_support_sla_evidence_profile import build_profile


BASE = ROOT / "phase_b_product/commercial_readiness/support_evidence"
SOURCES = {
    "support_contact": BASE / "production_support_sla_evidence.from_support_contact_human_filled.local.json",
    "customer_support": BASE / "production_support_sla_evidence.from_customer_support.human_filled.local.json",
    "sla": BASE / "production_support_sla_evidence.from_sla.human_filled.local.json",
    "on_call_rotation": BASE / "production_support_sla_evidence.from_on_call.human_filled.local.json",
}
PROFILE_OUTPUT = BASE / "support_group_human_filled_evidence_refresh_profile.local.json"
COMBINED_OUTPUT = BASE / "production_support_sla_evidence.combined_from_all_support_human_filled.local.json"
SUMMARY_PATH = BASE / "support_group_human_filled_evidence_refresh.local.json"
REPORT_PATH = BASE / "support_group_human_filled_evidence_refresh.md"
BOUNDARY_PATH = BASE / "support_group_human_filled_evidence_refresh_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_SUPPORT_GROUP_HUMAN_FILLED_EVIDENCE_REFRESH_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"


LLMS_LINES = [
    "/phase_b_product/commercial_readiness/support_evidence/support_group_human_filled_evidence_refresh.md",
    "/phase_b_product/commercial_readiness/support_evidence/support_group_human_filled_evidence_refresh.local.json",
    "/phase_b_product/commercial_readiness/support_evidence/support_group_human_filled_evidence_refresh_boundary_audit.md",
    "/phase_b_product/commercial_readiness/support_evidence/support_group_human_filled_evidence_refresh_profile.local.json",
    "/phase_b_product/commercial_readiness/support_evidence/production_support_sla_evidence.combined_from_all_support_human_filled.local.json",
    "/docs/strategy/SAEE_SUPPORT_GROUP_HUMAN_FILLED_EVIDENCE_REFRESH_GATE.md",
    "/scripts/saee_support_group_human_filled_evidence_refresh.py",
    "/scripts/saee_support_group_human_filled_evidence_refresh_smoke.py",
]


README_BLOCK = """## Support Group Human-Filled Evidence Refresh

Support Group Human-Filled Evidence Refresh v0.1 combines human-filled
support-contact, customer-support, SLA, and on-call evidence into one local
review profile. It may make `production_support_available=true` for this
support/SLA evidence lane, but it still closes zero blockers by itself and keeps
`production_ready=false`, `customer_validated=false`, `product_launched=false`,
and `private_core_exposed=false`.
"""


AGENT_READABLE_BLOCK = """0. For the support group human-filled evidence refresh, inspect `phase_b_product/commercial_readiness/support_evidence/support_group_human_filled_evidence_refresh.local.json`. It records the four human-filled support evidence lanes together while keeping `blockers_closed_by_refresh=0`, `production_ready=false`, `customer_validated=false`, and `product_launched=false`.
"""


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
    missing_sources = [rel(path) for path in SOURCES.values() if not path.exists()]
    if missing_sources:
        profile = {
            "profile_status": "hold",
            "support_contact_evidence_complete": False,
            "customer_support_evidence_complete": False,
            "sla_evidence_complete": False,
            "on_call_rotation_evidence_complete": False,
            "production_support_available": False,
            "support_evidence_readiness_status": "hold",
            "target_blockers_satisfied": [],
            "target_blockers_unsatisfied": ["support_contact", "customer_support", "sla", "on_call_rotation"],
            "profile_production_blocker_count": 0,
            "source_boundary_violation_count": 0,
        }
        status = "hold_support_group_human_filled_sources_missing"
    else:
        profile = build_profile(
            SOURCES,
            PROFILE_OUTPUT,
            COMBINED_OUTPUT,
            support_contact="redacted_support_contact_review_token",
            write_documentation=False,
        )
        status = (
            "support_group_human_filled_evidence_complete_for_review_only"
            if profile.get("profile_status") == "pass"
            and profile.get("production_support_available") is True
            else "hold_support_group_human_filled_evidence_incomplete"
        )

    summary = {
        "support_group_human_filled_evidence_refresh_v0_1": True,
        "status": status,
        "refreshed_at": datetime.now(timezone.utc).isoformat(),
        "refresh_scope": "support_contact_customer_support_sla_on_call_human_filled_review_profile",
        "source_paths": {label: rel(path) for label, path in SOURCES.items()},
        "missing_source_paths": missing_sources,
        "profile_output": rel(PROFILE_OUTPUT),
        "combined_support_sla_evidence_output": rel(COMBINED_OUTPUT),
        "profile_status": profile.get("profile_status"),
        "support_evidence_readiness_status": profile.get("support_evidence_readiness_status"),
        "support_contact_evidence_complete": bool(profile.get("support_contact_evidence_complete") is True),
        "customer_support_evidence_complete": bool(profile.get("customer_support_evidence_complete") is True),
        "sla_evidence_complete": bool(profile.get("sla_evidence_complete") is True),
        "on_call_rotation_evidence_complete": bool(profile.get("on_call_rotation_evidence_complete") is True),
        "production_support_available": bool(profile.get("production_support_available") is True),
        "target_blockers_satisfied": profile.get("target_blockers_satisfied", []),
        "target_blockers_unsatisfied": profile.get("target_blockers_unsatisfied", []),
        "profile_production_blocker_count": int(profile.get("profile_production_blocker_count", 0) or 0),
        "source_boundary_violation_count": int(profile.get("source_boundary_violation_count", 0) or 0),
        "blockers_closed_by_refresh": 0,
        "accepted_for_blocker_closure_count": 0,
        "separate_go_no_go_profile_required": True,
        "separate_human_launch_approval_required": True,
        "development_permission_granted": False,
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
        "support_operations_started": False,
        "sla_published_by_codex": False,
        "on_call_rotation_started_by_codex": False,
        "next_action": (
            "Use this support group evidence refresh as local go/no-go input only. "
            "Do not claim production readiness or customer validation without a "
            "separate full commercial go/no-go pass and explicit human launch approval."
        ),
    }
    write_json(SUMMARY_PATH, summary)
    return summary


def render_report(summary: dict) -> str:
    return f"""# SAEE Support Group Human-Filled Evidence Refresh

Status: {summary['status']}.

This refresh combines the human-filled support-contact, customer-support, SLA,
and on-call evidence lanes into one local support/SLA review profile.

## Results

- support_contact_evidence_complete: {str(summary['support_contact_evidence_complete']).lower()}
- customer_support_evidence_complete: {str(summary['customer_support_evidence_complete']).lower()}
- sla_evidence_complete: {str(summary['sla_evidence_complete']).lower()}
- on_call_rotation_evidence_complete: {str(summary['on_call_rotation_evidence_complete']).lower()}
- production_support_available: {str(summary['production_support_available']).lower()}
- profile_status: {summary['profile_status']}
- support_evidence_readiness_status: {summary['support_evidence_readiness_status']}
- target_blockers_satisfied: {', '.join(summary['target_blockers_satisfied']) or 'none'}
- target_blockers_unsatisfied: {', '.join(summary['target_blockers_unsatisfied']) or 'none'}
- blockers_closed_by_refresh: 0

## What Changed

The local support evidence group is now summarized in one agent-readable file.
This is useful for later commercial go/no-go review.

## What Did Not Change

No support contact was published by Codex. No support test was sent by Codex.
No support operation was started. No SLA was published by Codex. No on-call
rotation was started by Codex. No customer or vendor was contacted.

## Boundary

- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- external_calls_made: false
- blockers_closed_by_refresh: 0

This refresh may satisfy the local support/SLA evidence lane, but it is not a
production launch approval and does not make SAEE commercially complete.
"""


def render_boundary(summary: dict) -> str:
    return f"""# SAEE Support Group Human-Filled Evidence Refresh Boundary Audit

- status: {summary['status']}
- production_support_available: {str(summary['production_support_available']).lower()}
- blockers_closed_by_refresh: 0
- accepted_for_blocker_closure_count: 0
- separate_go_no_go_profile_required: true
- separate_human_launch_approval_required: true
- development_permission_granted: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- external_calls_made: false
- external_model_api_called: false
- external_ai_assistant_tested: false
- customer_contacted: false
- support_vendor_contacted: false
- support_contact_published_by_codex: false
- support_contact_test_performed_by_codex: false
- support_operations_started: false
- sla_published_by_codex: false
- on_call_rotation_started_by_codex: false

Final decision: boundary safe. This is a local support/SLA evidence refresh for
review and go/no-go input only.
"""


def render_gate(summary: dict) -> str:
    return f"""# SAEE Support Group Human-Filled Evidence Refresh Gate

answer: {summary['status']}

reason: The human-filled support-contact, customer-support, SLA, and on-call
evidence lanes were combined into a local support/SLA review profile. This does
not authorize launch, customer contact, support publication, or blocker closure.

boundary:

- production_support_available: {str(summary['production_support_available']).lower()}
- blockers_closed_by_refresh: 0
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

next_action: Use this as one input to the full commercial go/no-go review. Do
not claim production readiness until all other commercial blockers are resolved
and a separate human launch approval exists.
"""


def update_agent_index(summary: dict) -> None:
    data = json.loads(AGENT_INDEX.read_text(encoding="utf-8"))
    data["support_group_human_filled_evidence_refresh_v0_1"] = {
        "status": summary["status"],
        "support_contact_evidence_complete": summary["support_contact_evidence_complete"],
        "customer_support_evidence_complete": summary["customer_support_evidence_complete"],
        "sla_evidence_complete": summary["sla_evidence_complete"],
        "on_call_rotation_evidence_complete": summary["on_call_rotation_evidence_complete"],
        "production_support_available": summary["production_support_available"],
        "blockers_closed_by_refresh": 0,
        "accepted_for_blocker_closure_count": 0,
        "separate_go_no_go_profile_required": True,
        "separate_human_launch_approval_required": True,
        "development_permission_granted": False,
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
        "support_operations_started": False,
        "sla_published_by_codex": False,
        "on_call_rotation_started_by_codex": False,
    }
    AGENT_INDEX.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def update_text_surfaces(summary: dict) -> None:
    REPORT_PATH.write_text(render_report(summary), encoding="utf-8")
    BOUNDARY_PATH.write_text(render_boundary(summary), encoding="utf-8")
    GATE.write_text(render_gate(summary), encoding="utf-8")
    marker = "SAEE_SUPPORT_GROUP_HUMAN_FILLED_EVIDENCE_REFRESH"
    insert_after_marker(ROOT / "README.md", marker, README_BLOCK)
    insert_after_marker(
        ROOT / "PROJECT_STATUS.md",
        marker,
        "Support Group Human-Filled Evidence Refresh（支持组人工证据刷新）:\n"
        + README_BLOCK,
    )
    insert_after_marker(
        ROOT / "ROADMAP.md",
        marker,
        "Support Group Human-Filled Evidence Refresh v0.1 is a status/reference entry only. "
        + README_BLOCK,
    )
    insert_after_marker(
        ROOT / "CHANGELOG.md",
        marker,
        "- Added Support Group Human-Filled Evidence Refresh v0.1. " + README_BLOCK,
    )
    insert_after_marker(ROOT / "agent-readable.md", marker, AGENT_READABLE_BLOCK)
    append_unique_llms()
    update_agent_index(summary)


def main() -> None:
    summary = build_summary()
    update_text_surfaces(summary)
    print(
        "SAEE_SUPPORT_GROUP_HUMAN_FILLED_EVIDENCE_REFRESH: PASS "
        f"status={summary['status']} "
        f"production_support_available={str(summary['production_support_available']).lower()} "
        "production_ready=false customer_validated=false blockers_closed_by_refresh=0"
    )


if __name__ == "__main__":
    main()
