#!/usr/bin/env python3
"""Build the SAEE commercial production evidence collection packet.

This packet consolidates Phase 1-5 commercial gap audits into a single
human-readable evidence collection queue. It does not collect evidence, contact
customers or vendors, execute implementation work, close blockers, or claim
production readiness.
"""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_production_evidence_collection_packet"
)
OUTPUT_JSON = OUTPUT_DIR / "commercial_production_evidence_collection_packet.local.json"
OUTPUT_MD = OUTPUT_DIR / "commercial_production_evidence_collection_packet.md"
OUTPUT_CHECKLIST = OUTPUT_DIR / "commercial_production_evidence_collection_checklist.md"
OUTPUT_CSV = OUTPUT_DIR / "commercial_production_evidence_collection.csv"
README_PATH = OUTPUT_DIR / "README.md"
DOC_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/COMMERCIAL_PRODUCTION_EVIDENCE_COLLECTION_PACKET_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_COMMERCIAL_PRODUCTION_EVIDENCE_COLLECTION_PACKET_RECOMMENDATION_GATE.md"
)
DEPENDENCY_PLAN_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_blocker_dependency_plan/dependency_plan.local.json"
)


PHASE_AUDITS = [
    {
        "phase_number": 1,
        "phase_id": "phase_1_identity_and_tenant_boundary",
        "phase_title": "Identity, authorization, and tenant boundary",
        "audit_path": ROOT
        / "phase_b_product/commercial_readiness/phase_1_identity_tenant_gap_audit/phase_1_identity_tenant_gap_audit.local.json",
    },
    {
        "phase_number": 2,
        "phase_id": "phase_2_data_and_operations_resilience",
        "phase_title": "Data recovery and production operations",
        "audit_path": ROOT
        / "phase_b_product/commercial_readiness/phase_2_data_operations_gap_audit/phase_2_data_operations_gap_audit.local.json",
    },
    {
        "phase_number": 3,
        "phase_id": "phase_3_support_security_legal",
        "phase_title": "Support, security, privacy, and legal readiness",
        "audit_path": ROOT
        / "phase_b_product/commercial_readiness/phase_3_support_security_legal_gap_audit/phase_3_support_security_legal_gap_audit.local.json",
    },
    {
        "phase_number": 4,
        "phase_id": "phase_4_commercial_packaging_and_billing",
        "phase_title": "Commercial packaging and billing",
        "audit_path": ROOT
        / "phase_b_product/commercial_readiness/phase_4_commercial_packaging_billing_gap_audit/phase_4_commercial_packaging_billing_gap_audit.local.json",
    },
    {
        "phase_number": 5,
        "phase_id": "phase_5_customer_validation_and_launch_review",
        "phase_title": "Customer validation and launch review",
        "audit_path": ROOT
        / "phase_b_product/commercial_readiness/phase_5_customer_validation_launch_gap_audit/phase_5_customer_validation_launch_gap_audit.local.json",
    },
]


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
    "public_sdk_released",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "execution_authorized",
    "evidence_collection_authorized",
    "task_candidates_executed",
    "customer_contacted_by_codex",
    "vendor_contacted_by_codex",
    "support_vendor_contacted_by_codex",
    "monitoring_vendor_contacted_by_codex",
    "alert_provider_contacted_by_codex",
    "payment_provider_contacted_by_codex",
    "legal_counsel_contacted_by_codex",
    "tax_advisor_contacted_by_codex",
    "security_reviewer_contacted_by_codex",
    "pilot_executed_by_codex",
    "customer_feedback_collected_by_codex",
    "production_claim_added",
    "launch_claim_added",
    "revenue_claim_added",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def dependency_lookup(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["blocker_id"]: row for row in plan.get("blockers", [])}


def build_phase_summary(meta: dict[str, Any], audit: dict[str, Any]) -> dict[str, Any]:
    return {
        "phase_number": meta["phase_number"],
        "phase_id": meta["phase_id"],
        "phase_title": meta["phase_title"],
        "source_audit": rel(meta["audit_path"]),
        "target_blocker_count": len(audit.get("target_blockers", [])),
        "target_blockers": audit.get("target_blockers", []),
        "required_evidence_item_count": audit.get("required_evidence_item_count", 0),
        "local_public_shell_present_count": audit.get(
            "local_public_shell_present_count", 0
        ),
        "missing_production_evidence_count": audit.get(
            "missing_production_evidence_count", 0
        ),
        "accepted_for_blocker_closure_count": audit.get(
            "accepted_for_blocker_closure_count", 0
        ),
        "blockers_closed_by_audit": audit.get("blockers_closed_by_audit", 0),
        "phase_status": "hold",
        "manual_collection_required": True,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
    }


def build_queue_rows(
    meta: dict[str, Any],
    audit: dict[str, Any],
    blockers: dict[str, dict[str, Any]],
    start_index: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for offset, row in enumerate(audit.get("gap_rows", []), start=start_index):
        blocker_id = row.get("blocker_id", "")
        blocker = blockers.get(blocker_id, {})
        production_missing = row.get("local_public_shell_value") is not True
        rows.append(
            {
                "collection_record_id": f"ECP-{offset:03d}",
                "phase_number": meta["phase_number"],
                "phase_id": meta["phase_id"],
                "phase_title": meta["phase_title"],
                "source_audit": rel(meta["audit_path"]),
                "blocker_id": blocker_id,
                "evidence_file_type": row.get("evidence_file_type", ""),
                "evidence_key": row.get("evidence_key", ""),
                "gap_status": row.get("gap_status", ""),
                "local_public_shell_value": row.get("local_public_shell_value")
                is True,
                "production_evidence_missing": production_missing,
                "accepted_for_blocker_closure": False,
                "collection_status": "not_started",
                "allowed_collection_mode": "human_provided_evidence_only",
                "owner_review_lane": blocker.get("owner_review_lane", "human_review"),
                "external_dependency_required": row.get(
                    "external_dependency_required",
                    blocker.get("external_dependency_required") is True,
                )
                is True,
                "engineering_implementation_required": row.get(
                    "engineering_implementation_required",
                    blocker.get("engineering_implementation_required") is True,
                )
                is True,
                "human_review_required": True,
                "manual_collection_required": True,
                "requires_separate_execution_request": True,
                "execution_authorized": False,
                "evidence_collection_authorized": False,
                "must_not_touch": [
                    "runtime",
                    "backend",
                    "kernel",
                    "api_schema",
                    "private_core",
                    "production_customer_data",
                    "payment_collection",
                    "customer_contact_without_approval",
                ],
                "next_human_action": blocker.get(
                    "next_human_action",
                    "Collect real production evidence only after separate human approval.",
                ),
                "notes": (
                    "Local public-shell evidence is review input only; human-approved production evidence is still required."
                    if row.get("local_public_shell_value") is True
                    else "Production evidence is missing and must be supplied by a human owner."
                ),
            }
        )
    return rows


def csv_text(rows: list[dict[str, Any]]) -> str:
    output = StringIO()
    fieldnames = [
        "collection_record_id",
        "phase_number",
        "phase_id",
        "phase_title",
        "source_audit",
        "blocker_id",
        "evidence_file_type",
        "evidence_key",
        "gap_status",
        "local_public_shell_value",
        "production_evidence_missing",
        "accepted_for_blocker_closure",
        "collection_status",
        "allowed_collection_mode",
        "owner_review_lane",
        "external_dependency_required",
        "engineering_implementation_required",
        "human_review_required",
        "manual_collection_required",
        "requires_separate_execution_request",
        "execution_authorized",
        "evidence_collection_authorized",
        "next_human_action",
        "notes",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        serializable = {key: row.get(key, "") for key in fieldnames}
        writer.writerow(serializable)
    return output.getvalue()


def build_packet() -> dict[str, Any]:
    plan = read_json(DEPENDENCY_PLAN_PATH)
    blockers = dependency_lookup(plan)
    phase_summaries: list[dict[str, Any]] = []
    queue_rows: list[dict[str, Any]] = []
    source_audits: list[str] = []

    next_index = 1
    for meta in PHASE_AUDITS:
        audit = read_json(meta["audit_path"])
        phase_summaries.append(build_phase_summary(meta, audit))
        source_audits.append(rel(meta["audit_path"]))
        rows = build_queue_rows(meta, audit, blockers, next_index)
        queue_rows.extend(rows)
        next_index += len(rows)

    required_count = len(queue_rows)
    local_count = sum(1 for row in queue_rows if row["local_public_shell_value"])
    missing_count = sum(1 for row in queue_rows if row["production_evidence_missing"])
    blocker_ids = sorted({row["blocker_id"] for row in queue_rows})
    owner_lanes = sorted({row["owner_review_lane"] for row in queue_rows})

    packet: dict[str, Any] = {
        "packet_type": "saee_commercial_production_evidence_collection_packet",
        "packet_version": "0.1",
        "status": "hold",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_production_evidence_collection_packet.py",
        "scope": "phase_1_to_phase_5_human_production_evidence_collection_queue",
        "source_dependency_plan": rel(DEPENDENCY_PLAN_PATH),
        "source_gap_audits": source_audits,
        "phase_count": len(phase_summaries),
        "target_blocker_count": len(blocker_ids),
        "target_blockers": blocker_ids,
        "owner_review_lanes": owner_lanes,
        "total_required_evidence_item_count": required_count,
        "total_local_public_shell_present_count": local_count,
        "total_missing_production_evidence_count": missing_count,
        "accepted_for_blocker_closure_count": 0,
        "blockers_ready_to_close": [],
        "blockers_closed_by_packet": 0,
        "human_review_required": True,
        "manual_collection_required": True,
        "separate_execution_approval_required": True,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "task_candidates_executed": False,
        "recommended_next_action": (
            "Human owners should review the queue, assign owners, and provide real production evidence "
            "through a separate approved evidence-intake request."
        ),
        "phase_summaries": phase_summaries,
        "evidence_collection_queue": queue_rows,
    }
    for flag in BOUNDARY_FALSE_FLAGS:
        packet[flag] = False
    return packet


def render_readme(packet: dict[str, Any]) -> str:
    return f"""# SAEE Commercial Production Evidence Collection Packet

Status: hold; manual collection queue only.

This directory consolidates Phase 1-5 commercial gap-audit outputs into a
single human-review queue. It helps human owners see which production evidence
is still missing before SAEE can move toward formal commercial use.

It does not collect evidence automatically, contact customers, contact vendors,
execute implementation work, close blockers, enable billing, publish pricing,
or claim production readiness.

## Counts

- total_required_evidence_item_count: {packet['total_required_evidence_item_count']}
- total_local_public_shell_present_count: {packet['total_local_public_shell_present_count']}
- total_missing_production_evidence_count: {packet['total_missing_production_evidence_count']}
- blockers_closed_by_packet: {packet['blockers_closed_by_packet']}

## Files

- `commercial_production_evidence_collection_packet.local.json`
- `commercial_production_evidence_collection_packet.md`
- `commercial_production_evidence_collection_checklist.md`
- `commercial_production_evidence_collection.csv`

## Boundary

- execution_authorized: false
- evidence_collection_authorized: false
- customer_contacted: false
- vendor_contacted_by_codex: false
- production_ready: false
- product_launched: false
- private_core_exposed: false
"""


def render_report(packet: dict[str, Any]) -> str:
    phase_lines = "\n".join(
        "- Phase {phase_number}: {phase_title} | required={required_evidence_item_count} | local_public_shell={local_public_shell_present_count} | missing_production={missing_production_evidence_count} | blockers_closed={blockers_closed_by_audit}".format(
            **phase
        )
        for phase in packet["phase_summaries"]
    )
    queue_lines = "\n".join(
        "| {collection_record_id} | {phase_number} | {blocker_id} | {evidence_key} | {collection_status} | {owner_review_lane} |".format(
            **row
        )
        for row in packet["evidence_collection_queue"][:40]
    )
    return f"""# SAEE Commercial Production Evidence Collection Packet v0.1

## Summary

This packet converts the existing Phase 1-5 commercial gap audits into one
manual production evidence collection queue.

- packet_status: {packet['status']}
- total_required_evidence_item_count: {packet['total_required_evidence_item_count']}
- total_local_public_shell_present_count: {packet['total_local_public_shell_present_count']}
- total_missing_production_evidence_count: {packet['total_missing_production_evidence_count']}
- accepted_for_blocker_closure_count: {packet['accepted_for_blocker_closure_count']}
- blockers_closed_by_packet: {packet['blockers_closed_by_packet']}

## Phase Summary

{phase_lines}

## First 40 Queue Rows

| Record | Phase | Blocker | Evidence key | Status | Owner lane |
| --- | ---: | --- | --- | --- | --- |
{queue_lines}

The complete queue is available in
`commercial_production_evidence_collection_packet.local.json` and
`commercial_production_evidence_collection.csv`.

## What This Does Not Do

- No customer contact.
- No vendor contact.
- No evidence collection by Codex.
- No implementation or backend work.
- No runtime, kernel, API schema, or private-core modification.
- No blocker closure.
- No production-ready, customer-validation, launch, payment, or revenue claim.

## Next Human Action

Review the queue, choose the next phase and owner lane, and open a separate
human-approved evidence-intake request for the selected evidence items.
"""


def render_checklist(packet: dict[str, Any]) -> str:
    lines = [
        "# SAEE Commercial Production Evidence Collection Checklist",
        "",
        "Use this checklist only after a separate human decision authorizes evidence collection.",
        "",
    ]
    for phase in packet["phase_summaries"]:
        lines.append(f"## Phase {phase['phase_number']}: {phase['phase_title']}")
        rows = [
            row
            for row in packet["evidence_collection_queue"]
            if row["phase_number"] == phase["phase_number"]
        ]
        for row in rows:
            lines.append(
                f"- [ ] {row['collection_record_id']} `{row['blocker_id']}` / "
                f"`{row['evidence_key']}` - owner lane: `{row['owner_review_lane']}`"
            )
        lines.append("")
    lines.extend(
        [
            "## Collection Boundary",
            "",
            "- Do not contact customers unless separately approved.",
            "- Do not contact vendors unless separately approved.",
            "- Do not enable payments, checkout, invoices, or tax collection from this packet.",
            "- Do not modify runtime, backend, kernel, API schema, or private core from this packet.",
            "- Do not close blockers from this packet alone.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_doc(packet: dict[str, Any]) -> str:
    return f"""# SAEE Commercial Production Evidence Collection Packet v0.1

commercial_production_evidence_collection_packet_v0_1: true
status: hold
scope: phase_1_to_phase_5_human_production_evidence_collection_queue
total_required_evidence_item_count: {packet['total_required_evidence_item_count']}
total_local_public_shell_present_count: {packet['total_local_public_shell_present_count']}
total_missing_production_evidence_count: {packet['total_missing_production_evidence_count']}
accepted_for_blocker_closure_count: {packet['accepted_for_blocker_closure_count']}
blockers_closed_by_packet: {packet['blockers_closed_by_packet']}
execution_authorized: false
evidence_collection_authorized: false
customer_contacted: false
vendor_contacted_by_codex: false
payment_provider_contacted_by_codex: false
legal_counsel_contacted_by_codex: false
tax_advisor_contacted_by_codex: false
security_reviewer_contacted_by_codex: false
production_ready: false
product_launched: false
customer_validated: false
private_core_exposed: false

This is a planning packet for human production evidence collection. It
consolidates Phase 1-5 commercial gap audit rows into one queue. It does not
authorize execution, evidence collection, customer contact, vendor contact,
payment setup, production launch, or blocker closure.
"""


def render_gate(packet: dict[str, Any]) -> str:
    return f"""# SAEE Commercial Production Evidence Collection Packet Recommendation Gate

answer: conditional

recommend_for_human_review: true
recommend_for_evidence_collection_authorization: false
recommend_for_execution_authorization: false
recommend_for_blocker_closure: false
recommend_for_customer_contact: false
recommend_for_vendor_contact: false
recommend_for_payment_setup: false
recommend_for_production_launch: false

reason: The packet creates a bounded human-review queue from existing Phase 1-5
gap audits, but it does not provide real production evidence and closes zero
commercial blockers.

counts:
- total_required_evidence_item_count: {packet['total_required_evidence_item_count']}
- total_local_public_shell_present_count: {packet['total_local_public_shell_present_count']}
- total_missing_production_evidence_count: {packet['total_missing_production_evidence_count']}
- blockers_closed_by_packet: {packet['blockers_closed_by_packet']}

boundary:
- execution_authorized: false
- evidence_collection_authorized: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- product_launched: false
- customer_validated: false
- production_ready: false

next_action: Human review only. Open a separate evidence-intake request before
collecting or accepting any production evidence.
"""


def write_outputs(packet: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_report(packet), encoding="utf-8")
    OUTPUT_CHECKLIST.write_text(render_checklist(packet), encoding="utf-8")
    OUTPUT_CSV.write_text(csv_text(packet["evidence_collection_queue"]), encoding="utf-8")
    README_PATH.write_text(render_readme(packet), encoding="utf-8")
    DOC_PATH.write_text(render_doc(packet), encoding="utf-8")
    GATE_PATH.write_text(render_gate(packet), encoding="utf-8")


def main() -> None:
    packet = build_packet()
    write_outputs(packet)
    print(
        "SAEE_COMMERCIAL_PRODUCTION_EVIDENCE_COLLECTION_PACKET: PASS "
        f"required_items={packet['total_required_evidence_item_count']} "
        f"local_public_shell={packet['total_local_public_shell_present_count']} "
        f"missing_production={packet['total_missing_production_evidence_count']} "
        f"blockers_closed_by_packet={packet['blockers_closed_by_packet']}"
    )


if __name__ == "__main__":
    main()
