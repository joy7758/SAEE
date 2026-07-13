#!/usr/bin/env python3
"""Build the Phase 3 support/security/legal priority evidence collection packet.

This runner extracts Phase 3 support, SLA, security-review, privacy/legal,
DPA, and vulnerability-management rows from the cross-phase commercial
production evidence collection packet and creates a human-fillable priority
template. It does not contact support vendors, contact security reviewers,
contact legal counsel, approve DPA, activate vulnerability operations, collect
evidence, process customer data, close blockers, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PACKET_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_production_evidence_collection_packet/commercial_production_evidence_collection_packet.local.json"
)
OUTPUT_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/phase_3_support_security_legal_priority_evidence_collection"
)
OUTPUT_JSON = OUTPUT_DIR / "phase_3_support_security_legal_priority_evidence_collection.local.json"
OUTPUT_MD = OUTPUT_DIR / "phase_3_support_security_legal_priority_evidence_collection.md"
OUTPUT_CSV = OUTPUT_DIR / "phase_3_support_security_legal_priority_evidence_collection.csv"
OUTPUT_CHECKLIST = OUTPUT_DIR / "phase_3_support_security_legal_priority_collection_checklist.md"
OUTPUT_TEMPLATE = OUTPUT_DIR / "phase_3_support_security_legal_evidence_input.priority.template.json"
OUTPUT_BOUNDARY = OUTPUT_DIR / "phase_3_support_security_legal_priority_boundary_audit.md"
README_PATH = OUTPUT_DIR / "README.md"
DOC_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/PHASE_3_SUPPORT_SECURITY_LEGAL_PRIORITY_EVIDENCE_COLLECTION_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_PHASE_3_SUPPORT_SECURITY_LEGAL_PRIORITY_EVIDENCE_COLLECTION_RECOMMENDATION_GATE.md"
)


PHASE_ID = "phase_3_support_security_legal"
TARGET_BLOCKERS = [
    "sla",
    "support_contact",
    "customer_support",
    "formal_security_review",
    "privacy_legal_review",
    "data_processing_agreement",
    "vulnerability_management",
]
BLOCKER_PRIORITY = {blocker: index + 1 for index, blocker in enumerate(TARGET_BLOCKERS)}


BOUNDARY_FALSE_FLAGS = [
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "private_core_exposed",
    "product_launched",
    "production_ready",
    "customer_validated",
    "customer_contacted",
    "customer_data_processed",
    "public_sdk_released",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "execution_authorized",
    "evidence_collection_authorized",
    "support_vendor_contacted_by_codex",
    "support_contact_published_by_codex",
    "sla_published_by_codex",
    "support_channel_activated_by_codex",
    "security_reviewer_contacted_by_codex",
    "formal_security_review_completed_by_codex",
    "legal_counsel_contacted_by_codex",
    "privacy_legal_review_completed_by_codex",
    "dpa_approved_by_codex",
    "vulnerability_operations_activated_by_codex",
    "vulnerability_disclosure_published_by_codex",
    "codex_inferred_missing_evidence",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def phase3_rows(packet: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        row
        for row in packet.get("evidence_collection_queue", [])
        if row.get("phase_id") == PHASE_ID
    ]
    rows.sort(
        key=lambda row: (
            BLOCKER_PRIORITY.get(str(row.get("blocker_id")), 99),
            0 if row.get("production_evidence_missing") is True else 1,
            str(row.get("evidence_key", "")),
        )
    )
    return rows


def build_priority_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    priority_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        missing = row.get("production_evidence_missing") is True
        priority_rows.append(
            {
                "phase_3_record_id": f"P3-ECP-{index:03d}",
                "source_collection_record_id": row.get("collection_record_id", ""),
                "priority_rank": index,
                "priority_tier": "missing_production_evidence" if missing else "local_public_shell_requires_human_approval",
                "blocker_id": row.get("blocker_id", ""),
                "blocker_priority": BLOCKER_PRIORITY.get(str(row.get("blocker_id")), 99),
                "evidence_file_type": row.get("evidence_file_type", ""),
                "evidence_key": row.get("evidence_key", ""),
                "gap_status": row.get("gap_status", ""),
                "local_public_shell_value": row.get("local_public_shell_value") is True,
                "production_evidence_missing": missing,
                "owner_review_lane": row.get("owner_review_lane", "support_security_legal"),
                "human_fill_status": "not_started",
                "human_evidence_value": None,
                "human_source_note": "",
                "accepted_for_blocker_closure": False,
                "human_review_required": True,
                "manual_collection_required": True,
                "execution_authorized": False,
                "evidence_collection_authorized": False,
                "requires_separate_execution_request": True,
                "must_not_touch": [
                    "runtime",
                    "backend",
                    "kernel",
                    "api_schema",
                    "private_core",
                    "production_customer_data",
                    "customer_contact_without_approval",
                    "support_vendor_without_approval",
                    "security_reviewer_without_approval",
                    "legal_counsel_without_approval",
                    "dpa_approval_without_approval",
                    "vulnerability_operations_without_approval",
                ],
                "required_human_action": (
                    "Provide source-backed support/security/legal evidence and a reviewer note; do not mark accepted for closure without a separate human approval."
                ),
            }
        )
    return priority_rows


def build_priority_template(priority_rows: list[dict[str, Any]]) -> dict[str, Any]:
    evidence_keys = [row["evidence_key"] for row in priority_rows]
    return {
        "phase_3_support_security_legal_priority_evidence_collection_v0_1": True,
        "input_status": "priority_template_not_filled",
        "human_reviewer_name": "",
        "review_date": "",
        "evidence_source_notes": "",
        "source_collection_packet": rel(SOURCE_PACKET_PATH),
        "priority_collection_source": rel(OUTPUT_JSON),
        "template_note": (
            "Human owners fill evidence_review and source_notes_by_key. Codex must not infer missing evidence, contact support vendors, contact security reviewers, contact legal counsel, approve DPA, activate vulnerability operations, or process customer data."
        ),
        "evidence_review": {key: False for key in evidence_keys},
        "source_notes_by_key": {key: "" for key in evidence_keys},
        "priority_evidence_key_order": evidence_keys,
        "priority_collection_map_by_key": {
            row["evidence_key"]: {
                "phase_3_record_id": row["phase_3_record_id"],
                "source_collection_record_id": row["source_collection_record_id"],
                "blocker_id": row["blocker_id"],
                "priority_tier": row["priority_tier"],
                "evidence_file_type": row["evidence_file_type"],
            }
            for row in priority_rows
        },
        "boundary_review": {
            "support_vendor_contacted": False,
            "support_contact_published": False,
            "sla_published": False,
            "security_reviewer_contacted": False,
            "formal_security_review_completed": False,
            "legal_counsel_contacted": False,
            "privacy_legal_review_completed": False,
            "dpa_approved": False,
            "vulnerability_operations_activated": False,
            "customer_contacted": False,
            "customer_data_processed": False,
            "production_ready_claim": False,
        },
    }


def summarize_by_blocker(priority_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for blocker_id in TARGET_BLOCKERS:
        subset = [row for row in priority_rows if row["blocker_id"] == blocker_id]
        local_present = sum(1 for row in subset if row["local_public_shell_value"])
        missing = sum(1 for row in subset if row["production_evidence_missing"])
        summary.append(
            {
                "blocker_id": blocker_id,
                "required_items": len(subset),
                "local_public_shell_present": local_present,
                "missing_production_evidence": missing,
                "ready_to_close": False,
                "human_review_required": True,
                "execution_authorized": False,
                "evidence_collection_authorized": False,
                "next_action": (
                    "Human owner must provide source-backed production evidence in the priority template."
                ),
            }
        )
    return summary


def build_packet() -> dict[str, Any]:
    source_packet = read_json(SOURCE_PACKET_PATH)
    rows = phase3_rows(source_packet)
    priority_rows = build_priority_rows(rows)
    local_present = sum(1 for row in priority_rows if row["local_public_shell_value"])
    missing = sum(1 for row in priority_rows if row["production_evidence_missing"])
    packet: dict[str, Any] = {
        "packet_type": "saee_phase_3_support_security_legal_priority_evidence_collection",
        "packet_version": "0.1",
        "status": "ready_for_human_review_not_execution",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_phase3_support_security_legal_priority_evidence_collection.py",
        "scope": "phase_3_support_security_legal_priority_human_evidence_collection",
        "source_collection_packet": rel(SOURCE_PACKET_PATH),
        "human_fillable_template": rel(OUTPUT_TEMPLATE),
        "phase_id": PHASE_ID,
        "target_blocker_count": len(TARGET_BLOCKERS),
        "target_blockers": TARGET_BLOCKERS,
        "required_evidence_item_count": len(priority_rows),
        "local_public_shell_present_count": local_present,
        "missing_production_evidence_count": missing,
        "accepted_for_blocker_closure_count": 0,
        "blockers_closed_by_collection": 0,
        "blockers_ready_to_close": [],
        "human_review_required": True,
        "manual_collection_required": True,
        "separate_execution_approval_required": True,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "recommended_next_action": (
            "Human support/security/legal owner fills the priority template with source-backed evidence, then opens a separate execution or blocker-closure request if justified."
        ),
        "post_fill_commands": [
            "python3 scripts/saee_support_evidence_runner.py",
            "python3 scripts/saee_privacy_security_legal_evidence_runner.py",
            "python3 scripts/saee_phase3_support_security_legal_gap_audit.py",
            "python3 scripts/mainline_guard.py",
        ],
        "blocker_summary": summarize_by_blocker(priority_rows),
        "priority_rows": priority_rows,
    }
    for flag in BOUNDARY_FALSE_FLAGS:
        packet[flag] = False
    return packet


def csv_text(rows: list[dict[str, Any]]) -> str:
    output = StringIO()
    fieldnames = [
        "phase_3_record_id",
        "source_collection_record_id",
        "priority_rank",
        "priority_tier",
        "blocker_id",
        "evidence_file_type",
        "evidence_key",
        "gap_status",
        "local_public_shell_value",
        "production_evidence_missing",
        "owner_review_lane",
        "human_fill_status",
        "human_evidence_value",
        "human_source_note",
        "accepted_for_blocker_closure",
        "execution_authorized",
        "evidence_collection_authorized",
        "required_human_action",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows([{key: row.get(key, "") for key in fieldnames} for row in rows])
    return output.getvalue()


def render_readme(packet: dict[str, Any]) -> str:
    return f"""# SAEE Phase 3 Support/Security/Legal Priority Evidence Collection

Status: ready for human review, not execution.

This directory extracts the Phase 3 support contact, customer support, SLA,
formal security review, privacy/legal review, DPA, and vulnerability-management
evidence items from the cross-phase commercial production evidence collection
packet and provides a human-fillable priority template.

Counts:

- required_evidence_item_count: {packet['required_evidence_item_count']}
- local_public_shell_present_count: {packet['local_public_shell_present_count']}
- missing_production_evidence_count: {packet['missing_production_evidence_count']}
- blockers_closed_by_collection: {packet['blockers_closed_by_collection']}

Boundary:

- no support vendor contacted by Codex
- no support contact published by Codex
- no SLA published by Codex
- no security reviewer contacted by Codex
- no formal security review completed by Codex
- no legal counsel contacted by Codex
- no privacy/legal review completed by Codex
- no DPA approved by Codex
- no vulnerability operations activated by Codex
- no customer contact or customer data processing
- no runtime, backend, kernel, API schema, or private-core modification
- no blocker closure
- No blocker closure
- no production-ready claim
"""


def render_report(packet: dict[str, Any]) -> str:
    blocker_lines = "\n".join(
        "- `{blocker_id}`: required={required_items}, local_public_shell={local_public_shell_present}, missing_production={missing_production_evidence}, ready_to_close=false".format(
            **row
        )
        for row in packet["blocker_summary"]
    )
    row_lines = "\n".join(
        "| {phase_3_record_id} | {priority_tier} | {blocker_id} | {evidence_key} | {human_fill_status} |".format(
            **row
        )
        for row in packet["priority_rows"]
    )
    return f"""# SAEE Phase 3 Support/Security/Legal Priority Evidence Collection v0.1

## Summary

- status: {packet['status']}
- required_evidence_item_count: {packet['required_evidence_item_count']}
- local_public_shell_present_count: {packet['local_public_shell_present_count']}
- missing_production_evidence_count: {packet['missing_production_evidence_count']}
- accepted_for_blocker_closure_count: {packet['accepted_for_blocker_closure_count']}
- blockers_closed_by_collection: {packet['blockers_closed_by_collection']}

## Blocker Summary

{blocker_lines}

## Priority Rows

| Record | Priority tier | Blocker | Evidence key | Human fill status |
| --- | --- | --- | --- | --- |
{row_lines}

## How Human Owners Use This

1. Fill `phase_3_support_security_legal_evidence_input.priority.template.json`
   with source-backed production evidence.
2. Keep every boundary flag false unless a separate approved execution request
   exists.
3. Re-run the existing support and privacy/security/legal evidence runners only
   after local evidence paths are configured by a human.
4. Re-run the Phase 3 gap audit and mainline guard.

## What This Does Not Do

It does not collect evidence, contact support vendors, contact security
reviewers, contact legal counsel, approve DPA, publish SLA or support contact,
activate vulnerability operations, process customer data, close blockers, or
claim production readiness.
"""


def render_checklist(packet: dict[str, Any]) -> str:
    lines = [
        "# SAEE Phase 3 Support/Security/Legal Priority Collection Checklist",
        "",
        "Use this only after a human owner decides to collect Phase 3 evidence.",
        "",
    ]
    for row in packet["priority_rows"]:
        lines.append(
            f"- [ ] {row['phase_3_record_id']} `{row['blocker_id']}` / `{row['evidence_key']}` "
            "-> fill `evidence_review` and `source_notes_by_key` in the priority template"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Do not contact support vendors from this packet.",
            "- Do not publish support contact or SLA from this packet.",
            "- Do not contact security reviewers from this packet.",
            "- Do not contact legal counsel from this packet.",
            "- Do not approve DPA from this packet.",
            "- Do not activate vulnerability operations from this packet.",
            "- Do not contact customers or process customer data from this packet.",
            "- Do not close blockers from this packet.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_boundary(packet: dict[str, Any]) -> str:
    return f"""# SAEE Phase 3 Priority Collection Boundary Audit

- support_vendor_contacted_by_codex: false
- support_contact_published_by_codex: false
- sla_published_by_codex: false
- support_channel_activated_by_codex: false
- security_reviewer_contacted_by_codex: false
- formal_security_review_completed_by_codex: false
- legal_counsel_contacted_by_codex: false
- privacy_legal_review_completed_by_codex: false
- dpa_approved_by_codex: false
- vulnerability_operations_activated_by_codex: false
- vulnerability_disclosure_published_by_codex: false
- customer_contacted: false
- customer_data_processed: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- product_launched: false
- production_ready: false
- customer_validated: false
- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_collection: {packet['blockers_closed_by_collection']}

This packet is a human-review collection planner only.
"""


def render_doc(packet: dict[str, Any]) -> str:
    return f"""# Phase 3 Support/Security/Legal Priority Evidence Collection v0.1

phase_3_support_security_legal_priority_evidence_collection_v0_1: true
status: ready_for_human_review_not_execution
scope: phase_3_support_security_legal_priority_human_evidence_collection
required_evidence_item_count: {packet['required_evidence_item_count']}
local_public_shell_present_count: {packet['local_public_shell_present_count']}
missing_production_evidence_count: {packet['missing_production_evidence_count']}
accepted_for_blocker_closure_count: {packet['accepted_for_blocker_closure_count']}
blockers_closed_by_collection: {packet['blockers_closed_by_collection']}
execution_authorized: false
evidence_collection_authorized: false
support_vendor_contacted_by_codex: false
support_contact_published_by_codex: false
sla_published_by_codex: false
security_reviewer_contacted_by_codex: false
formal_security_review_completed_by_codex: false
legal_counsel_contacted_by_codex: false
privacy_legal_review_completed_by_codex: false
dpa_approved_by_codex: false
vulnerability_operations_activated_by_codex: false
customer_contacted: false
customer_data_processed: false
production_ready: false
customer_validated: false
private_core_exposed: false

This packet extracts the 45 Phase 3 evidence items from the cross-phase queue
and provides a human-fillable priority evidence template. It is not production
evidence and does not close blockers.
"""


def render_gate(packet: dict[str, Any]) -> str:
    return f"""# SAEE Phase 3 Support/Security/Legal Priority Evidence Collection Recommendation Gate

answer: conditional

recommend_for_human_review: true
recommend_for_human_evidence_input: true
recommend_for_evidence_collection_authorization: false
recommend_for_execution_authorization: false
recommend_for_blocker_closure: false
recommend_for_support_vendor_contact: false
recommend_for_support_contact_publication: false
recommend_for_sla_publication: false
recommend_for_security_reviewer_contact: false
recommend_for_legal_counsel_contact: false
recommend_for_dpa_approval: false
recommend_for_vulnerability_operations_activation: false
recommend_for_production_launch: false

reason: This packet improves Phase 3 commercial readiness by creating a
human-fillable priority input surface for 45 support, SLA, security,
privacy/legal, DPA, and vulnerability-management evidence items. It does not
supply evidence or authorize execution.

counts:
- required_evidence_item_count: {packet['required_evidence_item_count']}
- local_public_shell_present_count: {packet['local_public_shell_present_count']}
- missing_production_evidence_count: {packet['missing_production_evidence_count']}
- blockers_closed_by_collection: {packet['blockers_closed_by_collection']}

boundary:
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
- execution_authorized: false
- evidence_collection_authorized: false
"""


def write_outputs(packet: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    template = build_priority_template(packet["priority_rows"])
    OUTPUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_TEMPLATE.write_text(json.dumps(template, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_CSV.write_text(csv_text(packet["priority_rows"]), encoding="utf-8")
    OUTPUT_MD.write_text(render_report(packet), encoding="utf-8")
    OUTPUT_CHECKLIST.write_text(render_checklist(packet), encoding="utf-8")
    OUTPUT_BOUNDARY.write_text(render_boundary(packet), encoding="utf-8")
    README_PATH.write_text(render_readme(packet), encoding="utf-8")
    DOC_PATH.write_text(render_doc(packet), encoding="utf-8")
    GATE_PATH.write_text(render_gate(packet), encoding="utf-8")


def main() -> None:
    packet = build_packet()
    write_outputs(packet)
    print(
        "SAEE_PHASE3_SUPPORT_SECURITY_LEGAL_PRIORITY_EVIDENCE_COLLECTION: PASS "
        f"required_items={packet['required_evidence_item_count']} "
        f"local_public_shell={packet['local_public_shell_present_count']} "
        f"missing_production={packet['missing_production_evidence_count']} "
        f"blockers_closed_by_collection={packet['blockers_closed_by_collection']}"
    )


if __name__ == "__main__":
    main()
