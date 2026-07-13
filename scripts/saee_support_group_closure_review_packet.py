#!/usr/bin/env python3
"""Build a support-group blocker closure review packet without closing blockers.

The packet uses the local human-filled support-group evidence to identify
support-related blockers that are ready for a separate human final closure
review. It does not update the formal blocker matrix, close blockers, publish
support channels, contact customers or vendors, launch product, or claim
production readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SUPPORT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
OUT_JSON = SUPPORT_DIR / "support_group_closure_review_packet.local.json"
OUT_MD = SUPPORT_DIR / "support_group_closure_review_packet.md"
OUT_CSV = SUPPORT_DIR / "support_group_closure_review_packet.csv"
BOUNDARY = SUPPORT_DIR / "support_group_closure_review_packet_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/SUPPORT_GROUP_CLOSURE_REVIEW_PACKET_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_SUPPORT_GROUP_CLOSURE_REVIEW_PACKET_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
]

SUPPORT_GROUP_REFRESH = SUPPORT_DIR / "support_group_human_filled_evidence_refresh.local.json"
SUPPORT_GAP_REVIEW = SUPPORT_DIR / "support_contact_closure_gap_review.local.json"
COMBINED_SUPPORT_EVIDENCE = (
    SUPPORT_DIR / "production_support_sla_evidence.combined_from_all_support_human_filled.local.json"
)

SUPPORT_BLOCKERS = [
    {
        "blocker_id": "support_contact",
        "evidence_key": "support_contact_evidence_complete",
        "source_group": "support_contact",
        "review_scope": "support intake contact, owner, abuse path, notice route, and test record",
    },
    {
        "blocker_id": "customer_support",
        "evidence_key": "customer_support_evidence_complete",
        "source_group": "customer_support",
        "review_scope": "staffed support workflow, triage, audit trail, engineering handoff, customer template, and dry run",
    },
    {
        "blocker_id": "sla",
        "evidence_key": "sla_evidence_complete",
        "source_group": "sla",
        "review_scope": "SLA terms, severity definitions, support hours, response targets, exclusions, and legal review",
    },
    {
        "blocker_id": "on_call_rotation",
        "evidence_key": "on_call_rotation_evidence_complete",
        "source_group": "on_call",
        "review_scope": "on-call rotation, escalation schedule, and incident commander ownership",
    },
]

FALSE_FLAGS = {
    "blocker_closure_authorized": False,
    "blockers_closed_by_packet": 0,
    "development_permission_granted": False,
    "evidence_collection_authorized": False,
    "execution_authorized": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "private_core_exposed": False,
    "product_launched": False,
    "production_ready": False,
    "customer_validated": False,
    "customer_contacted": False,
    "support_vendor_contacted": False,
    "support_contact_published_by_codex": False,
    "support_contact_test_sent_by_codex": False,
    "sla_published_by_codex": False,
    "on_call_rotation_started_by_codex": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "public_sdk_released": False,
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{rel(path)} must contain a JSON object")
    return data


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


def build_rows(refresh: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in SUPPORT_BLOCKERS:
        evidence_complete = refresh.get(item["evidence_key"]) is True
        rows.append(
            {
                "blocker_id": item["blocker_id"],
                "source_group": item["source_group"],
                "evidence_key": item["evidence_key"],
                "evidence_complete": evidence_complete,
                "review_scope": item["review_scope"],
                "closure_review_status": (
                    "ready_for_human_final_closure_review"
                    if evidence_complete
                    else "hold_evidence_incomplete"
                ),
                "recommended_human_action": (
                    "review_for_separate_blocker_closure_decision"
                    if evidence_complete
                    else "collect_missing_support_evidence"
                ),
                "execution_allowed": False,
                "development_allowed": False,
            }
        )
    return rows


def build_payload() -> dict[str, Any]:
    refresh = read_json(SUPPORT_GROUP_REFRESH)
    gap = read_json(SUPPORT_GAP_REVIEW)
    combined = read_json(COMBINED_SUPPORT_EVIDENCE)
    rows = build_rows(refresh)
    candidate_count = sum(
        1 for row in rows if row["closure_review_status"] == "ready_for_human_final_closure_review"
    )
    missing_count = len(rows) - candidate_count
    status = (
        "ready_for_human_final_closure_review_no_auto_closure"
        if candidate_count == len(rows)
        else "hold_support_group_evidence_incomplete"
    )
    return {
        "support_group_closure_review_packet_v0_1": True,
        "review_type": "local_support_group_closure_review_packet_no_auto_closure",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target_blocker_group": "support",
        "target_blockers": [item["blocker_id"] for item in SUPPORT_BLOCKERS],
        "source_support_group_refresh": rel(SUPPORT_GROUP_REFRESH),
        "source_support_contact_gap_review": rel(SUPPORT_GAP_REVIEW),
        "source_combined_support_evidence": rel(COMBINED_SUPPORT_EVIDENCE),
        "support_group_refresh_status": refresh.get("status"),
        "support_contact_gap_review_status": gap.get("status"),
        "combined_support_evidence_available": COMBINED_SUPPORT_EVIDENCE.exists(),
        "production_support_available": refresh.get("production_support_available") is True,
        "support_group_evidence_complete": refresh.get("production_support_available") is True,
        "support_contact_available_for_review": gap.get("support_contact_available_for_review") is True,
        "support_group_closure_candidate_count": candidate_count,
        "support_group_missing_candidate_count": missing_count,
        "closure_review_rows": rows,
        "combined_support_evidence_boundary_flags": {
            "codex_published_support_contact": combined.get("codex_published_support_contact") is True,
            "codex_sent_support_contact_test": combined.get("codex_sent_support_contact_test") is True,
            "sla_published_by_codex": combined.get("sla_published_by_codex") is True,
            "on_call_rotation_started_by_codex": combined.get("on_call_rotation_started_by_codex") is True,
        },
        "ready_for_human_final_closure_review": candidate_count == len(rows),
        "separate_final_closure_approval_required": True,
        "next_required_human_action": (
            "review support_contact, customer_support, sla, and on_call_rotation in a "
            "separate final blocker-closure decision; do not treat this packet as closure"
        ),
        **FALSE_FLAGS,
    }


def write_outputs(payload: dict[str, Any]) -> None:
    write_json(OUT_JSON, payload)

    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "blocker_id",
                "source_group",
                "evidence_key",
                "evidence_complete",
                "closure_review_status",
                "recommended_human_action",
                "execution_allowed",
                "development_allowed",
            ],
        )
        writer.writeheader()
        for row in payload["closure_review_rows"]:
            writer.writerow({key: row[key] for key in writer.fieldnames})

    table = "\n".join(
        "| {blocker_id} | {source_group} | {evidence_complete} | {closure_review_status} | {recommended_human_action} |".format(
            **row
        )
        for row in payload["closure_review_rows"]
    )
    OUT_MD.write_text(
        f"""# SAEE Support Group Closure Review Packet v0.1

Status: `{payload['status']}`

This packet summarizes the local human-filled support evidence as candidates
for a separate human final blocker-closure decision. It does not close blockers
and does not update the formal commercial readiness matrix.

## Summary

- target_blocker_group: `support`
- target_blockers: `{', '.join(payload['target_blockers'])}`
- support_group_refresh_status: `{payload['support_group_refresh_status']}`
- support_contact_gap_review_status: `{payload['support_contact_gap_review_status']}`
- production_support_available: `{str(payload['production_support_available']).lower()}`
- support_group_evidence_complete: `{str(payload['support_group_evidence_complete']).lower()}`
- support_group_closure_candidate_count: `{payload['support_group_closure_candidate_count']}`
- support_group_missing_candidate_count: `{payload['support_group_missing_candidate_count']}`
- ready_for_human_final_closure_review: `{str(payload['ready_for_human_final_closure_review']).lower()}`
- blockers_closed_by_packet: `0`

## Closure Review Rows

| Blocker | Source group | Evidence complete | Closure review status | Recommended human action |
| --- | --- | --- | --- | --- |
{table}

## Next Human Action

Review these support-group candidates in a separate final closure decision.
Do not treat this packet as blocker closure.

## Boundary

- blocker_closure_authorized=false
- blockers_closed_by_packet=0
- development_permission_granted=false
- execution_authorized=false
- evidence_collection_authorized=false
- customer_validated=false
- production_ready=false
- product_launched=false
- private_core_exposed=false
- customer_contacted=false
- support_vendor_contacted=false
""",
        encoding="utf-8",
    )

    BOUNDARY.write_text(
        """# SAEE Support Group Closure Review Packet Boundary Audit

support_group_closure_review_packet_v0_1: true
status: ready_for_human_final_closure_review_no_auto_closure

- Local closure-review packet only.
- No blocker closure is authorized.
- No support contact published by Codex.
- No support-contact test sent by Codex.
- No SLA published by Codex.
- No on-call rotation started by Codex.
- No customer contacted.
- No support vendor contacted.
- No runtime modified.
- No backend modified.
- No kernel modified.
- No API schema modified.
- No private core exposed.
- No product launched.
- No production-ready claim added.
- blockers_closed_by_packet: 0
""",
        encoding="utf-8",
    )

    TOP_DOC.write_text(
        """# SAEE Support Group Closure Review Packet v0.1

support_group_closure_review_packet_v0_1: true
status: ready_for_human_final_closure_review_no_auto_closure

Purpose: present locally complete support-group evidence as support-related
blocker closure candidates for a separate human final closure decision.

This packet does not close blockers, update the formal production matrix,
contact customers or vendors, publish support channels, launch product, or
claim production readiness.

Entrypoints:

- `phase_b_product/commercial_readiness/support_evidence/support_group_closure_review_packet.local.json`
- `phase_b_product/commercial_readiness/support_evidence/support_group_closure_review_packet.md`
- `phase_b_product/commercial_readiness/support_evidence/support_group_closure_review_packet.csv`
- `phase_b_product/commercial_readiness/support_evidence/support_group_closure_review_packet_boundary_audit.md`
""",
        encoding="utf-8",
    )

    GATE.write_text(
        """# SAEE Support Group Closure Review Packet Gate

answer: ready_for_human_final_closure_review_no_auto_closure

reason: The local human-filled support-group evidence is complete for
support_contact, customer_support, sla, and on_call_rotation, so those blockers
can be reviewed in a separate final closure decision. This packet itself does
not close any blocker.

boundary:
- blocker_closure_authorized: false
- blockers_closed_by_packet: 0
- development_permission_granted: false
- execution_authorized: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

next_action: human final closure decision for the four support-related blockers
only if the team wants to promote this local evidence into the formal blocker
matrix.
""",
        encoding="utf-8",
    )

    for line in [
        "/phase_b_product/commercial_readiness/SUPPORT_GROUP_CLOSURE_REVIEW_PACKET_V0_1.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_closure_review_packet.local.json",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_closure_review_packet.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_closure_review_packet.csv",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_closure_review_packet_boundary_audit.md",
        "/docs/strategy/SAEE_SUPPORT_GROUP_CLOSURE_REVIEW_PACKET_GATE.md",
        "/scripts/saee_support_group_closure_review_packet.py",
        "/scripts/saee_support_group_closure_review_packet_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["support_group_closure_review_packet_v0_1"] = {
        "name": "SAEE Support Group Closure Review Packet v0.1",
        "status": payload["status"],
        "target_blocker_group": "support",
        "target_blockers": payload["target_blockers"],
        "support_group_evidence_complete": payload["support_group_evidence_complete"],
        "production_support_available": payload["production_support_available"],
        "support_group_closure_candidate_count": payload["support_group_closure_candidate_count"],
        "ready_for_human_final_closure_review": payload["ready_for_human_final_closure_review"],
        "separate_final_closure_approval_required": True,
        "blocker_closure_authorized": False,
        "blockers_closed_by_packet": 0,
        "development_permission_granted": False,
        "execution_authorized": False,
        "customer_validated": False,
        "production_ready": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "customer_contacted": False,
        "entrypoints": {
            "summary": rel(OUT_JSON),
            "report": rel(OUT_MD),
            "csv": rel(OUT_CSV),
            "boundary_audit": rel(BOUNDARY),
            "gate": rel(GATE),
            "top_doc": rel(TOP_DOC),
            "runner": "scripts/saee_support_group_closure_review_packet.py",
            "smoke": "scripts/saee_support_group_closure_review_packet_smoke.py",
        },
        "make_target": "make check-support-group-closure-review-packet",
    }
    AGENT_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    block = f"""## Support Group Closure Review Packet v0.1

- `support_group_closure_review_packet_v0_1`
- Status: `{payload['status']}`
- Target blockers: `support_contact`, `customer_support`, `sla`, `on_call_rotation`
- support_group_evidence_complete={str(payload['support_group_evidence_complete']).lower()}
- production_support_available={str(payload['production_support_available']).lower()}
- support_group_closure_candidate_count={payload['support_group_closure_candidate_count']}
- ready_for_human_final_closure_review={str(payload['ready_for_human_final_closure_review']).lower()}
- blockers_closed_by_packet=0
- production_ready=false
- customer_validated=false
- private_core_exposed=false
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_SUPPORT_GROUP_CLOSURE_REVIEW_PACKET_V0_1", block)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_SUPPORT_GROUP_CLOSURE_REVIEW_PACKET: PASS "
        f"status={payload['status']} "
        f"support_group_closure_candidate_count={payload['support_group_closure_candidate_count']} "
        "blockers_closed_by_packet=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
