#!/usr/bin/env python3
"""Local support-contact preflight for SAEE commercial readiness.

The preflight reads only the local environment. It does not publish a support
contact, send test messages, contact customers or vendors, close blockers,
modify backend behavior, or claim production readiness.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
OUTPUT_JSON = OUTPUT_DIR / "support_contact_preflight.local.json"
OUTPUT_MD = OUTPUT_DIR / "support_contact_preflight.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/SUPPORT_CONTACT_PREFLIGHT_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_SUPPORT_CONTACT_PREFLIGHT_RECOMMENDATION_GATE.md"

FALSE_FLAGS = [
    "support_contact_published",
    "support_contact_test_performed",
    "customer_contacted",
    "support_vendor_contacted",
    "customer_support_available",
    "production_support_available",
    "support_process_available",
    "sla_available",
    "on_call_rotation_available",
    "customer_validated",
    "product_launched",
    "public_sdk_released",
    "production_ready",
    "private_core_exposed",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "external_calls_made",
    "external_model_api_called",
]


def channel_type(value: str) -> str:
    lowered = value.strip().lower()
    if not lowered:
        return "not_configured"
    if "@" in lowered and not lowered.startswith("http"):
        return "email_like"
    if lowered.startswith("https://") or lowered.startswith("http://"):
        return "url_like"
    if lowered.startswith("slack:") or lowered.startswith("discord:"):
        return "chat_route_like"
    return "other"


def redacted_value(value: str) -> str:
    if not value.strip():
        return ""
    return "<configured-redacted>"


def evaluate(env: Mapping[str, str] | None = None) -> dict[str, object]:
    source = os.environ if env is None else env
    raw_contact = str(source.get("SAEE_SUPPORT_CONTACT", "")).strip()
    configured = bool(raw_contact)
    status = "ready_for_human_review" if configured else "hold_missing_candidate"
    result: dict[str, object] = {
        "support_contact_preflight_v0_1": True,
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "generated_by": "scripts/saee_support_contact_preflight.py",
        "status": status,
        "blocker_target": "support_contact",
        "preflight_scope": "local_candidate_support_contact_review",
        "source_env_var": "SAEE_SUPPORT_CONTACT",
        "support_contact_candidate_configured": configured,
        "support_contact_candidate_channel_type": channel_type(raw_contact),
        "support_contact_candidate_value_redacted": redacted_value(raw_contact),
        "raw_support_contact_value_recorded": False,
        "raw_support_contact_value_exposed": False,
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "support_contact_available_for_review": configured,
        "support_contact_configured_for_production": False,
        "blockers_closed_by_preflight": 0,
        "next_human_action": (
            "Fill the support contact decision packet only after a human owner "
            "approves the candidate contact route."
            if configured
            else "Set SAEE_SUPPORT_CONTACT locally if a human owner wants to review a candidate support route."
        ),
    }
    for flag in FALSE_FLAGS:
        result[flag] = False
    return result


def write_json(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# SAEE Support Contact Preflight Result",
        "",
        f"- status: {data['status']}",
        f"- blocker_target: {data['blocker_target']}",
        f"- support_contact_candidate_configured: {str(data['support_contact_candidate_configured']).lower()}",
        f"- support_contact_candidate_channel_type: {data['support_contact_candidate_channel_type']}",
        f"- support_contact_candidate_value_redacted: {data['support_contact_candidate_value_redacted'] or 'not_configured'}",
        f"- raw_support_contact_value_recorded: {str(data['raw_support_contact_value_recorded']).lower()}",
        f"- support_contact_available_for_review: {str(data['support_contact_available_for_review']).lower()}",
        f"- support_contact_published: {str(data['support_contact_published']).lower()}",
        f"- support_contact_test_performed: {str(data['support_contact_test_performed']).lower()}",
        f"- customer_contacted: {str(data['customer_contacted']).lower()}",
        f"- production_support_available: {str(data['production_support_available']).lower()}",
        f"- production_ready: {str(data['production_ready']).lower()}",
        f"- blockers_closed_by_preflight: {data['blockers_closed_by_preflight']}",
        "",
        "## Boundary",
        "",
        "This result is a local preflight only. It does not publish a support",
        "contact, send test messages, create customer support, approve SLA terms,",
        "close blockers, launch product, or claim production readiness.",
        "",
        "## Next Human Action",
        "",
        str(data["next_human_action"]),
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Print JSON summary")
    parser.add_argument("--no-write", action="store_true", help="Do not write output files")
    args = parser.parse_args()

    result = evaluate()
    if not args.no_write:
        write_json(OUTPUT_JSON, result)
        write_markdown(OUTPUT_MD, result)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(
            "SAEE_SUPPORT_CONTACT_PREFLIGHT: PASS "
            f"status={result['status']} "
            "support_contact_published=false production_ready=false "
            "blockers_closed_by_preflight=0"
        )


if __name__ == "__main__":
    main()

