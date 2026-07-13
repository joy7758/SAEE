#!/usr/bin/env python3
"""Build a local support-contact readiness board.

This board consolidates existing support-contact readiness artifacts into a
single human-review surface. It does not configure or publish a support contact,
send support tests, contact customers or vendors, collect evidence, close
blockers, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
OUTPUT_JSON = OUTPUT_DIR / "support_contact_readiness_board.local.json"
OUTPUT_MD = OUTPUT_DIR / "support_contact_readiness_board.md"
OUTPUT_CSV = OUTPUT_DIR / "support_contact_readiness_board.csv"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/SUPPORT_CONTACT_READINESS_BOARD_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_SUPPORT_CONTACT_READINESS_BOARD_RECOMMENDATION_GATE.md"

SOURCE_PATHS = {
    "first_owner_input_completion": ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_completion_status.local.json",
    "commercial_next_action_summary": ROOT
    / "phase_b_product/commercial_readiness/commercial_next_action_summary/commercial_next_action_summary.local.json",
    "support_contact_preflight": OUTPUT_DIR / "support_contact_preflight.local.json",
    "support_contact_approval_input_validation": OUTPUT_DIR
    / "support_contact_approval_input_validation.local.json",
    "support_contact_evidence_builder": OUTPUT_DIR
    / "support_contact_evidence_builder_output.local.json",
    "support_sla_evidence_profile": OUTPUT_DIR / "support_sla_evidence_profile.local.json",
}

FALSE_FLAGS = {
    "support_contact_configured": False,
    "support_contact_published": False,
    "support_contact_test_performed": False,
    "support_contact_raw_value_exposed": False,
    "support_contact_raw_value_recorded": False,
    "customer_contacted": False,
    "support_vendor_contacted": False,
    "customer_support_available": False,
    "production_support_available": False,
    "support_process_available": False,
    "sla_available": False,
    "on_call_rotation_available": False,
    "evidence_collection_authorized": False,
    "execution_authorized": False,
    "blockers_closed_by_board": 0,
    "production_ready": False,
    "customer_validated": False,
    "product_launched": False,
    "public_sdk_released": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "external_ai_assistant_tested": False,
    "private_core_exposed": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"SAEE_SUPPORT_CONTACT_READINESS_BOARD: FAIL invalid JSON {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"SAEE_SUPPORT_CONTACT_READINESS_BOARD: FAIL {path} must contain an object")
    return data


def commercial_support_contact_state() -> dict[str, Any]:
    go_no_go = evaluate_commercial_go_no_go(load_settings({}))
    blockers = go_no_go.get("blockers", [])
    support_blocker = {}
    if isinstance(blockers, list):
        for item in blockers:
            if isinstance(item, dict) and item.get("blocker_id") == "support_contact":
                support_blocker = item
                break
    return {
        "commercial_status": go_no_go.get("commercial_status"),
        "production_launch_status": go_no_go.get("production_launch_status"),
        "production_blocker_count": go_no_go.get("production_blocker_count"),
        "support_contact_blocker_satisfied": support_blocker.get("satisfied") is True,
        "support_contact_blocker_message": support_blocker.get(
            "message",
            "Support contact must be configured before customer-facing preview support.",
        ),
    }


def step_state(
    step_id: str,
    title: str,
    source_key: str,
    status: str,
    complete: bool,
    next_action: str,
) -> dict[str, Any]:
    return {
        "step_id": step_id,
        "title": title,
        "source": source_key,
        "source_path": rel(SOURCE_PATHS[source_key]),
        "status": status,
        "complete": complete,
        "next_action": next_action,
        "human_review_required": True,
    }


def board_status(steps: list[dict[str, Any]], support_blocker_satisfied: bool) -> str:
    if support_blocker_satisfied:
        return "hold_human_closure_review_required"
    for step in steps:
        if not step["complete"]:
            if step["step_id"] == "SCB-001":
                return "hold_human_first_owner_input_required"
            if step["step_id"] == "SCB-002":
                return "hold_support_contact_candidate_required"
            if step["step_id"] == "SCB-003":
                return "hold_support_contact_approval_input_required"
            if step["step_id"] == "SCB-004":
                return "hold_support_contact_evidence_builder_required"
            return "hold_support_contact_profile_incomplete"
    return "hold_go_no_go_and_closure_review_required"


def build_board() -> dict[str, Any]:
    sources = {name: read_json(path) for name, path in SOURCE_PATHS.items()}
    commercial = commercial_support_contact_state()

    first_owner = sources["first_owner_input_completion"]
    next_summary = sources["commercial_next_action_summary"]
    preflight = sources["support_contact_preflight"]
    approval = sources["support_contact_approval_input_validation"]
    builder = sources["support_contact_evidence_builder"]
    profile = sources["support_sla_evidence_profile"]

    steps = [
        step_state(
            "SCB-001",
            "Human owner input for support_contact",
            "first_owner_input_completion",
            str(first_owner.get("status", "missing")),
            first_owner.get("first_owner_assignment_complete") is True,
            "Fill assigned_human_owner, owner_contact_reference, target_review_date, owner_acknowledged_scope, and human_approval_reference.",
        ),
        step_state(
            "SCB-002",
            "Candidate support route preflight",
            "support_contact_preflight",
            str(preflight.get("status", "missing")),
            preflight.get("support_contact_candidate_configured") is True,
            "Set SAEE_SUPPORT_CONTACT locally only after a human owner approves a candidate route for review.",
        ),
        step_state(
            "SCB-003",
            "Support contact approval input validation",
            "support_contact_approval_input_validation",
            str(approval.get("validation_status", "missing")),
            approval.get("builder_ready") is True,
            "Complete the human-filled support contact decision input and pass the approval input validator.",
        ),
        step_state(
            "SCB-004",
            "Support contact evidence builder",
            "support_contact_evidence_builder",
            str(builder.get("status", "missing")),
            builder.get("status") == "pass" and builder.get("support_contact_available_for_review") is True,
            "Run the evidence builder only after separate human approval and validated human input.",
        ),
        step_state(
            "SCB-005",
            "Combined support/SLA evidence profile",
            "support_sla_evidence_profile",
            str(profile.get("profile_status", "missing")),
            profile.get("support_contact_evidence_complete") is True,
            "Regenerate the support/SLA evidence profile after real support-contact evidence is available.",
        ),
    ]

    completed_steps = sum(1 for step in steps if step["complete"])
    status = board_status(steps, commercial["support_contact_blocker_satisfied"])
    next_action = (
        str(next_summary.get("next_human_action", "")).strip()
        or next((step["next_action"] for step in steps if not step["complete"]), "")
        or "Run commercial go/no-go and human closure review before any blocker closure."
    )

    board: dict[str, Any] = {
        "support_contact_readiness_board_v0_1": True,
        "board_type": "saee_support_contact_readiness_board",
        "board_scope": "local_support_contact_blocker_readiness_review",
        "target_blocker_id": "support_contact",
        "generated_by": "scripts/saee_support_contact_readiness_board.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "commercial_status": commercial["commercial_status"],
        "production_launch_status": commercial["production_launch_status"],
        "production_blocker_count": commercial["production_blocker_count"],
        "support_contact_blocker_satisfied": commercial["support_contact_blocker_satisfied"],
        "support_contact_blocker_message": commercial["support_contact_blocker_message"],
        "readiness_step_count": len(steps),
        "completed_step_count": completed_steps,
        "incomplete_step_count": len(steps) - completed_steps,
        "steps": steps,
        "source_paths": {name: rel(path) for name, path in SOURCE_PATHS.items()},
        "human_review_required": True,
        "separate_evidence_collection_request_required": True,
        "separate_human_closure_approval_required": True,
        "next_human_action": next_action,
    }
    board.update(FALSE_FLAGS)
    return board


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "step_id",
                "title",
                "source",
                "status",
                "complete",
                "human_review_required",
                "next_action",
            ],
        )
        writer.writeheader()
        for step in data["steps"]:
            writer.writerow(
                {
                    "step_id": step["step_id"],
                    "title": step["title"],
                    "source": step["source"],
                    "status": step["status"],
                    "complete": step["complete"],
                    "human_review_required": step["human_review_required"],
                    "next_action": step["next_action"],
                }
            )


def bool_text(value: Any) -> str:
    return str(bool(value)).lower()


def write_markdown(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# SAEE Support Contact Readiness Board",
        "",
        f"Status: {data['status']}.",
        "",
        "This board summarizes the current `support_contact` commercial blocker path.",
        "It is a local human-review surface only. It does not configure or",
        "publish a support contact, send tests, contact customers or vendors,",
        "collect evidence, close blockers, launch product, or claim production",
        "readiness.",
        "",
        "## Summary",
        "",
        f"- target_blocker_id: {data['target_blocker_id']}",
        f"- commercial_status: {data['commercial_status']}",
        f"- production_launch_status: {data['production_launch_status']}",
        f"- production_blocker_count: {data['production_blocker_count']}",
        f"- support_contact_blocker_satisfied: {bool_text(data['support_contact_blocker_satisfied'])}",
        f"- readiness_step_count: {data['readiness_step_count']}",
        f"- completed_step_count: {data['completed_step_count']}",
        f"- blockers_closed_by_board: {data['blockers_closed_by_board']}",
        f"- production_ready: {bool_text(data['production_ready'])}",
        f"- customer_validated: {bool_text(data['customer_validated'])}",
        f"- product_launched: {bool_text(data['product_launched'])}",
        "",
        "## Step State",
        "",
        "| Step | Title | Status | Complete | Source |",
        "| --- | --- | --- | --- | --- |",
    ]
    for step in data["steps"]:
        lines.append(
            f"| {step['step_id']} | {step['title']} | {step['status']} | "
            f"{bool_text(step['complete'])} | `{step['source_path']}` |"
        )
    lines.extend(
        [
            "",
            "## Next Human Action",
            "",
            str(data["next_human_action"]),
            "",
            "## Boundary",
            "",
            "- support_contact_configured: false",
            "- support_contact_published: false",
            "- support_contact_test_performed: false",
            "- support_contact_raw_value_exposed: false",
            "- support_contact_raw_value_recorded: false",
            "- customer_contacted: false",
            "- support_vendor_contacted: false",
            "- evidence_collection_authorized: false",
            "- execution_authorized: false",
            "- production_ready: false",
            "- customer_validated: false",
            "- product_launched: false",
            "- private_core_exposed: false",
            "- runtime_modified: false",
            "- backend_modified: false",
            "- kernel_modified: false",
            "- api_schema_modified: false",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_top_doc() -> None:
    TOP_DOC.write_text(
        """# SAEE Support Contact Readiness Board v0.1

Status: local board available.

This board consolidates the current `support_contact` commercial blocker
surface into one local human-review artifact. It reads existing local evidence
and validation outputs only. It does not configure or publish a support contact,
send test messages, contact customers or vendors, collect evidence, close
blockers, launch product, or claim production readiness.

## Outputs

- board JSON: `phase_b_product/commercial_readiness/support_evidence/support_contact_readiness_board.local.json`
- board report: `phase_b_product/commercial_readiness/support_evidence/support_contact_readiness_board.md`
- board CSV: `phase_b_product/commercial_readiness/support_evidence/support_contact_readiness_board.csv`

## Command

```bash
python3 scripts/saee_support_contact_readiness_board.py
```

## Boundary

- support_contact_configured: false
- support_contact_published: false
- support_contact_test_performed: false
- support_contact_raw_value_exposed: false
- support_contact_raw_value_recorded: false
- customer_contacted: false
- support_vendor_contacted: false
- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_board: 0
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
""",
        encoding="utf-8",
    )


def write_gate() -> None:
    GATE.write_text(
        """# SAEE Support Contact Readiness Board Recommendation Gate

answer: recommend

recommend_for_local_human_review: true
recommend_for_production: false

## Need

The `support_contact` blocker has several local artifacts. A human reviewer
needs one concise status board that explains which step is incomplete and what
must happen next.

## Recommendation

Recommend this board as a local human-review and agent-readable coordination
surface. It should not be treated as evidence collection, support-contact
publication, blocker closure, or production readiness.

## Boundary

- support_contact_configured: false
- support_contact_published: false
- support_contact_test_performed: false
- customer_contacted: false
- support_vendor_contacted: false
- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_board: 0
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
""",
        encoding="utf-8",
    )


def main() -> None:
    board = build_board()
    write_json(OUTPUT_JSON, board)
    write_markdown(OUTPUT_MD, board)
    write_csv(OUTPUT_CSV, board)
    write_top_doc()
    write_gate()
    print(
        "SAEE_SUPPORT_CONTACT_READINESS_BOARD: PASS "
        f"status={board['status']} "
        f"completed_step_count={board['completed_step_count']} "
        "blockers_closed_by_board=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
