#!/usr/bin/env python3
"""Generate draft-only evidence requests for the next commercial sprint.

This packet converts the five selected commercial next-evidence sprint
blockers into separate evidence request drafts. It does not assign owners,
collect evidence, execute work, contact customers or vendors, close blockers,
launch product, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
SPRINT_PATH = SPRINT_DIR / "commercial_next_evidence_sprint.local.json"
OWNER_STATUS_PATH = SPRINT_DIR / "owner_assignment_completion_status.local.json"

OUTPUT_JSON = SPRINT_DIR / "evidence_request_draft_packet.local.json"
OUTPUT_MD = SPRINT_DIR / "evidence_request_draft_packet.md"
OUTPUT_CSV = SPRINT_DIR / "evidence_request_draft_packet.csv"
OUTPUT_BOUNDARY = SPRINT_DIR / "evidence_request_draft_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_EVIDENCE_REQUEST_DRAFT_PACKET_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_EVIDENCE_REQUEST_DRAFT_PACKET_RECOMMENDATION_GATE.md"

FALSE_FLAGS = {
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "private_core_exposed": False,
    "product_launched": False,
    "production_ready": False,
    "customer_validated": False,
    "customer_contacted": False,
    "public_sdk_released": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "external_ai_assistant_tested": False,
    "task_candidates_executed": False,
    "development_permission_granted": False,
    "execution_authorized": False,
    "evidence_collection_authorized": False,
    "owner_contacted_by_codex": False,
    "customer_data_collected": False,
    "customer_data_processed": False,
    "vendor_contacted": False,
    "payment_collected": False,
    "revenue_validated": False,
    "production_claim_added": False,
    "launch_claim_added": False,
    "customer_validation_claim_added": False,
}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"SAEE_COMMERCIAL_EVIDENCE_REQUEST_DRAFT_PACKET: FAIL invalid JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"SAEE_COMMERCIAL_EVIDENCE_REQUEST_DRAFT_PACKET: FAIL {path} must contain an object")
    return value


def request_title(blocker_id: str) -> str:
    words = blocker_id.replace("_", " ")
    return f"Evidence request draft for {words}"


def build_draft(row: dict[str, Any], index: int) -> dict[str, Any]:
    evidence_items = row.get("first_evidence_items", [])
    if not isinstance(evidence_items, list):
        evidence_items = []
    blocker_id = str(row.get("blocker_id", "unknown_blocker"))
    return {
        "request_id": f"ERD-{index:03d}",
        "blocker_id": blocker_id,
        "title": request_title(blocker_id),
        "request_status": "draft_only_hold",
        "request_type": "commercial_evidence_collection_request_draft",
        "phase_id": row.get("phase_id"),
        "category": row.get("category"),
        "owner_review_lane": row.get("owner_review_lane"),
        "required_evidence": row.get("required_evidence"),
        "evidence_items": evidence_items,
        "evidence_item_count": len(evidence_items),
        "external_dependency_required": row.get("external_dependency_required") is True,
        "engineering_implementation_required": row.get("engineering_implementation_required") is True,
        "assigned_human_owner": "",
        "owner_assignment_required": True,
        "owner_assignment_complete": False,
        "human_approval_required": True,
        "separate_execution_request_required": True,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "closure_authorized": False,
        "default_decision": "hold",
        "allowed_scope": "human review of evidence requirements and request wording only",
        "forbidden_scope": [
            "runtime",
            "backend",
            "kernel",
            "api_schema",
            "private_core",
            "customer_contact_without_approval",
            "vendor_contact_without_approval",
            "payment_collection",
            "production_launch",
            "production_ready_claim",
            "customer_validation_claim",
        ],
        "blocked_by": [
            "human_owner_assignment",
            "separate_execution_approval",
        ],
        "next_required_human_action": (
            "Assign a human owner, record explicit approval, then create a "
            "separate evidence collection or implementation request if this "
            "draft should proceed."
        ),
    }


def build_packet() -> dict[str, Any]:
    sprint = read_json(SPRINT_PATH)
    owner_status = read_json(OWNER_STATUS_PATH)
    selected = sprint.get("selected_blockers", [])
    if not isinstance(selected, list):
        selected = []
    drafts = [build_draft(row, index + 1) for index, row in enumerate(selected)]
    return {
        "commercial_evidence_request_draft_packet_v0_1": True,
        "packet_type": "saee_commercial_evidence_request_draft_packet",
        "packet_version": "v0.1",
        "status": "hold_separate_human_execution_request_required",
        "draft_scope": "local_evidence_request_drafts_for_selected_sprint_blockers",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_evidence_request_draft_packet.py",
        "source_sprint": rel(SPRINT_PATH),
        "source_owner_assignment_status": rel(OWNER_STATUS_PATH),
        "source_sprint_status": sprint.get("sprint_status"),
        "source_owner_assignment_complete": owner_status.get("owner_assignment_complete") is True,
        "selected_blocker_count": len(selected),
        "draft_request_count": len(drafts),
        "selected_blocker_ids": [draft["blocker_id"] for draft in drafts],
        "request_drafts": drafts,
        "human_review_required": True,
        "human_owner_assignment_required": True,
        "separate_execution_approval_required": True,
        "separate_evidence_collection_request_required": True,
        "all_requests_default_hold": all(draft["default_decision"] == "hold" for draft in drafts),
        "requests_ready_for_execution": False,
        "blockers_closed_by_draft_packet": 0,
        "next_allowed_action": (
            "Human review may select a draft, assign an owner, and open a "
            "separate explicit execution request. This packet itself does not "
            "authorize evidence collection."
        ),
        **FALSE_FLAGS,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_text(value: object) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return str(value)


def write_csv(packet: dict[str, Any]) -> None:
    fields = [
        "request_id",
        "blocker_id",
        "category",
        "owner_review_lane",
        "request_status",
        "evidence_item_count",
        "external_dependency_required",
        "engineering_implementation_required",
        "owner_assignment_required",
        "evidence_collection_authorized",
        "execution_authorized",
        "closure_authorized",
        "default_decision",
        "next_required_human_action",
    ]
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for draft in packet["request_drafts"]:
            writer.writerow({field: draft.get(field, "") for field in fields})


def write_report(packet: dict[str, Any]) -> None:
    rows = []
    for draft in packet["request_drafts"]:
        rows.append(
            "| {request_id} | {blocker_id} | {category} | {owner_review_lane} | "
            "{evidence_item_count} | {request_status} | {default_decision} |".format(
                **draft
            )
        )
    OUTPUT_MD.write_text(
        f"""# SAEE Commercial Evidence Request Draft Packet

commercial_evidence_request_draft_packet_v0_1: true
packet_type: saee_commercial_evidence_request_draft_packet
status: {packet['status']}
draft_scope: {packet['draft_scope']}
draft_request_count: {packet['draft_request_count']}
human_owner_assignment_required: true
separate_execution_approval_required: true
evidence_collection_authorized: false
execution_authorized: false
requests_ready_for_execution: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
blockers_closed_by_draft_packet: 0

## Purpose

This packet converts the five selected commercial evidence sprint blockers into
separate draft evidence requests for human review. It exists to reduce handoff
friction after owner assignment, not to authorize evidence collection.

## Draft Requests

| Request ID | Blocker | Category | Owner Lane | Evidence Items | Status | Default |
| --- | --- | --- | --- | ---: | --- | --- |
{chr(10).join(rows)}

## What This Packet Does Not Do

- It does not assign owners.
- It does not contact owners, customers, vendors, or external services.
- It does not collect evidence.
- It does not execute implementation work.
- It does not close blockers.
- It does not launch product.
- It does not claim customer validation or production readiness.

## Next Human Action

{packet['next_allowed_action']}
""",
        encoding="utf-8",
    )


def write_boundary(packet: dict[str, Any]) -> None:
    OUTPUT_BOUNDARY.write_text(
        f"""# SAEE Commercial Evidence Request Draft Boundary Audit

commercial_evidence_request_draft_packet_v0_1: true
draft_scope: {packet['draft_scope']}
evidence_collection_authorized: false
execution_authorized: false
task_candidates_executed: false
owner_contacted_by_codex: false
customer_contacted: false
vendor_contacted: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
blockers_closed_by_draft_packet: 0

## Checked Forbidden Actions

- runtime modification: false
- backend modification: false
- kernel modification: false
- API schema modification: false
- private core exposure: false
- owner contact by Codex: false
- customer contact: false
- vendor contact: false
- evidence collection: false
- task execution: false
- product launch: false
- production-ready claim: false
- customer-validation claim: false

Final boundary decision: local evidence request drafting only.
""",
        encoding="utf-8",
    )


def write_top_doc() -> None:
    TOP_DOC.write_text(
        """# SAEE Commercial Evidence Request Draft Packet v0.1

commercial_evidence_request_draft_packet_v0_1: true
status: hold_separate_human_execution_request_required
draft_scope: local_evidence_request_drafts_for_selected_sprint_blockers
evidence_collection_authorized: false
execution_authorized: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
blockers_closed_by_draft_packet: 0

## Purpose

This packet prepares draft-only evidence requests for the five selected
commercial next-evidence sprint blockers. It is a handoff layer between owner
assignment and any later separately approved evidence collection request.

## Boundary

This packet does not assign owners, contact owners, collect evidence, execute
tasks, close blockers, modify runtime/backend/kernel/API schema, expose private
core, launch product, or claim production readiness.
""",
        encoding="utf-8",
    )


def write_gate() -> None:
    GATE.write_text(
        """# SAEE Commercial Evidence Request Draft Packet Recommendation Gate

answer: conditional

recommend_for_evidence_request_drafting: true
recommend_for_evidence_collection: false
recommend_for_automatic_execution: false
recommend_for_blocker_closure: false
recommend_for_product_launch: false
recommend_for_production_readiness_claim: false

## Reason

If the team needs to turn selected commercial blockers into reviewable evidence
request drafts, this packet is useful. It remains conditional because owners
are not assigned and no execution approval has been granted.

## Boundary

- evidence_collection_authorized: false
- execution_authorized: false
- owner_contacted_by_codex: false
- customer_contacted: false
- vendor_contacted: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
- blockers_closed_by_draft_packet: 0
""",
        encoding="utf-8",
    )


def write_readme_note() -> None:
    readme = SPRINT_DIR / "README.md"
    text = readme.read_text(encoding="utf-8") if readme.exists() else "# Commercial Next Evidence Sprint\n"
    note = (
        "\nThe evidence request draft packet turns the selected blocker list into "
        "draft-only separate evidence request records. It does not assign owners, "
        "authorize evidence collection, execute work, or close blockers.\n"
    )
    if "evidence request draft packet" not in text:
        marker = "The owner assignment completion helper creates"
        if marker in text:
            text = text.replace(marker, note + "\n" + marker)
        else:
            text += note
        files_marker = "- `owner_assignment_completion_status.md`\n"
        additions = (
            "- `evidence_request_draft_packet.local.json`\n"
            "- `evidence_request_draft_packet.md`\n"
            "- `evidence_request_draft_packet.csv`\n"
            "- `evidence_request_draft_boundary_audit.md`\n"
        )
        if files_marker in text and "evidence_request_draft_packet.local.json" not in text:
            text = text.replace(files_marker, files_marker + additions)
        readme.write_text(text, encoding="utf-8")


def run() -> dict[str, Any]:
    packet = build_packet()
    write_json(OUTPUT_JSON, packet)
    write_report(packet)
    write_csv(packet)
    write_boundary(packet)
    write_top_doc()
    write_gate()
    write_readme_note()
    print(
        "SAEE_COMMERCIAL_EVIDENCE_REQUEST_DRAFT_PACKET: PASS "
        f"draft_request_count={packet['draft_request_count']} "
        "evidence_collection_authorized=false execution_authorized=false "
        "blockers_closed_by_draft_packet=0 production_ready=false"
    )
    return packet


def main() -> int:
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
