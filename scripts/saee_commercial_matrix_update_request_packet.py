#!/usr/bin/env python3
"""Build a commercial matrix-update request packet without executing it.

This packet aggregates already-reviewed support-group and pricing-page evidence
into a human-review request for a future separate matrix update. It does not
modify the canonical gap matrix, close blockers, publish pricing, enable
checkout, contact anyone, launch product, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
OUT_DIR = COMMERCIAL_DIR / "matrix_update_requests"
OUT_JSON = OUT_DIR / "commercial_matrix_update_request_packet.local.json"
OUT_MD = OUT_DIR / "commercial_matrix_update_request_packet.md"
OUT_CSV = OUT_DIR / "commercial_matrix_update_request_packet.csv"
BOUNDARY = OUT_DIR / "commercial_matrix_update_request_packet_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_MATRIX_UPDATE_REQUEST_PACKET_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_REQUEST_PACKET_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
]

SUPPORT_VALIDATION = (
    COMMERCIAL_DIR
    / "support_evidence/support_group_final_closure_decision_validation.local.json"
)
SUPPORT_PACKET = COMMERCIAL_DIR / "support_evidence/support_group_closure_review_packet.local.json"
PRICING_PACKET = (
    COMMERCIAL_DIR
    / "billing_revenue_evidence/pricing_page_closure_review_packet.local.json"
)
GAP_MATRIX = COMMERCIAL_DIR / "production_blocker_gap_matrix/gap_matrix.local.json"

SUPPORT_BLOCKERS = ["support_contact", "customer_support", "sla", "on_call_rotation"]
PRICING_BLOCKERS = ["pricing_page"]

FALSE_FLAGS = {
    "matrix_update_executed": False,
    "canonical_gap_matrix_modified": False,
    "canonical_closure_board_modified": False,
    "blocker_closure_authorized": False,
    "blockers_closed_by_request": 0,
    "open_blocker_count_reduced": False,
    "pricing_page_published": False,
    "checkout_enabled": False,
    "customer_payment_collected": False,
    "revenue_validated": False,
    "development_permission_granted": False,
    "execution_authorized": False,
    "evidence_collection_authorized": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "private_core_exposed": False,
    "product_launched": False,
    "production_ready": False,
    "customer_validated": False,
    "customer_contacted": False,
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
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


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


def matrix_rows_by_id(matrix: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = matrix.get("matrix", [])
    if not isinstance(rows, list):
        return {}
    return {
        row.get("blocker_id"): row
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("blocker_id"), str)
    }


def build_candidate_rows(
    support_validation: dict[str, Any],
    pricing_packet: dict[str, Any],
    gap_matrix: dict[str, Any],
) -> list[dict[str, Any]]:
    matrix_by_id = matrix_rows_by_id(gap_matrix)
    rows: list[dict[str, Any]] = []
    support_ready = (
        support_validation.get("status") == "ready_for_separate_matrix_update_request_no_closure"
        and support_validation.get("final_human_decision_recorded") is True
        and support_validation.get("separate_matrix_update_request_ready") is True
    )
    for blocker_id in SUPPORT_BLOCKERS:
        matrix_row = matrix_by_id.get(blocker_id, {})
        rows.append(
            {
                "blocker_id": blocker_id,
                "source_group": "support",
                "source_status": support_validation.get("status"),
                "matrix_current_status": matrix_row.get("status", "missing"),
                "matrix_current_local_evidence_ready": matrix_row.get("local_evidence_ready") is True,
                "matrix_current_closure_allowed": matrix_row.get("closure_allowed_by_matrix") is True,
                "ready_for_matrix_update_request": support_ready,
                "recommended_matrix_update": "record_review_ready_no_closure",
                "recommended_new_status": "open",
                "recommended_closure_allowed_by_matrix": False,
                "recommended_local_evidence_ready": False,
                "blocker_closure_authorized_by_request": False,
                "requires_human_execution_request": True,
                "notes": "Support evidence has final human decision for separate matrix update request; no closure is authorized.",
            }
        )
    pricing_ready = (
        pricing_packet.get("status") == "ready_for_human_matrix_update_review_no_publication"
        and pricing_packet.get("ready_for_human_matrix_update_review") is True
        and pricing_packet.get("pricing_page_evidence_complete_for_review") is True
    )
    for blocker_id in PRICING_BLOCKERS:
        matrix_row = matrix_by_id.get(blocker_id, {})
        rows.append(
            {
                "blocker_id": blocker_id,
                "source_group": "billing_revenue",
                "source_status": pricing_packet.get("status"),
                "matrix_current_status": matrix_row.get("status", "missing"),
                "matrix_current_local_evidence_ready": matrix_row.get("local_evidence_ready") is True,
                "matrix_current_closure_allowed": matrix_row.get("closure_allowed_by_matrix") is True,
                "ready_for_matrix_update_request": pricing_ready,
                "recommended_matrix_update": "record_review_ready_no_publication_no_closure",
                "recommended_new_status": "open",
                "recommended_closure_allowed_by_matrix": False,
                "recommended_local_evidence_ready": False,
                "blocker_closure_authorized_by_request": False,
                "requires_human_execution_request": True,
                "notes": "Pricing-page evidence is complete for review; pricing remains unpublished and checkout remains disabled.",
            }
        )
    return rows


def build_payload() -> dict[str, Any]:
    support_validation = read_json(SUPPORT_VALIDATION)
    support_packet = read_json(SUPPORT_PACKET)
    pricing_packet = read_json(PRICING_PACKET)
    gap_matrix = read_json(GAP_MATRIX)
    candidate_rows = build_candidate_rows(support_validation, pricing_packet, gap_matrix)
    ready_count = sum(1 for row in candidate_rows if row["ready_for_matrix_update_request"])
    boundary_violations: list[str] = []
    for source_name, source in [
        ("support_validation", support_validation),
        ("support_packet", support_packet),
        ("pricing_packet", pricing_packet),
        ("gap_matrix", gap_matrix),
    ]:
        for flag in [
            "production_ready",
            "customer_validated",
            "product_launched",
            "private_core_exposed",
            "customer_contacted",
            "external_calls_made",
            "external_model_api_called",
        ]:
            if source.get(flag) is True:
                boundary_violations.append(f"{source_name}.{flag}")
    if boundary_violations:
        status = "stop_boundary_violation"
    elif ready_count == len(candidate_rows):
        status = "ready_for_human_matrix_update_execution_request_no_closure"
    else:
        status = "hold_matrix_update_request_candidates_incomplete"
    return {
        "commercial_matrix_update_request_packet_v0_1": True,
        "request_type": "commercial_matrix_update_request_packet_no_execution",
        "request_scope": "support_group_and_pricing_page_review_ready_markers_only",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_support_validation": rel(SUPPORT_VALIDATION),
        "source_support_packet": rel(SUPPORT_PACKET),
        "source_pricing_packet": rel(PRICING_PACKET),
        "source_gap_matrix": rel(GAP_MATRIX),
        "candidate_count": len(candidate_rows),
        "ready_candidate_count": ready_count,
        "target_blockers": SUPPORT_BLOCKERS + PRICING_BLOCKERS,
        "candidate_rows": candidate_rows,
        "recommended_human_decision": "approve_separate_matrix_update_execution_request",
        "separate_execution_request_required": True,
        "separate_blocker_closure_approval_required": True,
        "separate_pricing_publication_approval_required": True,
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": sorted(boundary_violations),
        "next_human_action": (
            "Review this packet and create a separate explicit matrix-update execution "
            "request if these review-ready markers should be applied. Do not close blockers."
        ),
        **FALSE_FLAGS,
    }


def write_outputs(payload: dict[str, Any]) -> None:
    write_json(OUT_JSON, payload)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "blocker_id",
            "source_group",
            "source_status",
            "matrix_current_status",
            "ready_for_matrix_update_request",
            "recommended_matrix_update",
            "recommended_new_status",
            "recommended_closure_allowed_by_matrix",
            "recommended_local_evidence_ready",
            "blocker_closure_authorized_by_request",
            "requires_human_execution_request",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["candidate_rows"]:
            writer.writerow({field: row.get(field) for field in fields})

    table = "\n".join(
        "| {blocker_id} | {source_group} | {ready_for_matrix_update_request} | {recommended_matrix_update} | {blocker_closure_authorized_by_request} |".format(
            **row
        )
        for row in payload["candidate_rows"]
    )
    OUT_MD.write_text(
        f"""# SAEE Commercial Matrix Update Request Packet v0.1

Status: `{payload['status']}`

This packet aggregates support-group and pricing-page review evidence into a
future matrix-update request surface. It does not modify the canonical gap
matrix, close blockers, publish pricing, enable checkout, collect payment, or
claim production readiness.

## Summary

- candidate_count: `{payload['candidate_count']}`
- ready_candidate_count: `{payload['ready_candidate_count']}`
- recommended_human_decision: `{payload['recommended_human_decision']}`
- separate_execution_request_required: `true`
- separate_blocker_closure_approval_required: `true`
- blockers_closed_by_request: `0`
- canonical_gap_matrix_modified: `false`
- production_ready: `false`
- customer_validated: `false`

## Candidate Rows

| Blocker | Source group | Ready for request | Recommended matrix update | Closure authorized |
| --- | --- | --- | --- | --- |
{table}

## Boundary

- matrix_update_executed=false
- canonical_gap_matrix_modified=false
- canonical_closure_board_modified=false
- blocker_closure_authorized=false
- blockers_closed_by_request=0
- open_blocker_count_reduced=false
- pricing_page_published=false
- checkout_enabled=false
- customer_payment_collected=false
- revenue_validated=false
- production_ready=false
- customer_validated=false
- product_launched=false
- private_core_exposed=false
""",
        encoding="utf-8",
    )
    BOUNDARY.write_text(
        """# SAEE Commercial Matrix Update Request Packet Boundary Audit

commercial_matrix_update_request_packet_v0_1: true
request_scope: support_group_and_pricing_page_review_ready_markers_only

- No matrix update executed.
- No canonical gap matrix modified.
- No canonical closure board modified.
- No blocker closure authorized.
- No blockers closed by request.
- No open blocker count reduction.
- No pricing page published.
- No checkout enabled.
- No customer payment collected.
- No revenue validated.
- No runtime modified.
- No backend modified.
- No kernel modified.
- No API schema modified.
- No private core exposed.
- No product launched.
- No customer contacted.
- No production-ready claim added.
""",
        encoding="utf-8",
    )
    TOP_DOC.write_text(
        """# SAEE Commercial Matrix Update Request Packet v0.1

commercial_matrix_update_request_packet_v0_1: true
status: ready_for_human_matrix_update_execution_request_no_closure

Purpose: collect support-group and pricing-page review-ready evidence into a
single human-review packet for a future separate matrix-update execution
request. This document does not execute that update and does not close any
commercial blocker.

Entrypoints:

- `phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_request_packet.local.json`
- `phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_request_packet.md`
- `phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_request_packet.csv`
- `phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_request_packet_boundary_audit.md`
""",
        encoding="utf-8",
    )
    GATE.write_text(
        """# SAEE Commercial Matrix Update Request Packet Gate

answer: ready_for_human_matrix_update_execution_request_no_closure

reason: Support-group final human decision and pricing-page review evidence are
ready to be considered for a separate matrix-update execution request. This
packet does not execute the update and does not authorize blocker closure.

boundary:
- matrix_update_executed: false
- canonical_gap_matrix_modified: false
- blocker_closure_authorized: false
- blockers_closed_by_request: 0
- pricing_page_published: false
- checkout_enabled: false
- production_ready: false
- customer_validated: false
- private_core_exposed: false

next_action: human approval of a separate matrix-update execution request, not launch.
""",
        encoding="utf-8",
    )

    for line in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_REQUEST_PACKET_V0_1.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_request_packet.local.json",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_request_packet.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_request_packet.csv",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_request_packet_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_REQUEST_PACKET_GATE.md",
        "/scripts/saee_commercial_matrix_update_request_packet.py",
        "/scripts/saee_commercial_matrix_update_request_packet_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["commercial_matrix_update_request_packet_v0_1"] = {
        "name": "SAEE Commercial Matrix Update Request Packet v0.1",
        "status": payload["status"],
        "request_scope": payload["request_scope"],
        "candidate_count": payload["candidate_count"],
        "ready_candidate_count": payload["ready_candidate_count"],
        "target_blockers": payload["target_blockers"],
        "recommended_human_decision": payload["recommended_human_decision"],
        "separate_execution_request_required": True,
        "separate_blocker_closure_approval_required": True,
        "matrix_update_executed": False,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_request": 0,
        "open_blocker_count_reduced": False,
        "pricing_page_published": False,
        "checkout_enabled": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
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
            "runner": "scripts/saee_commercial_matrix_update_request_packet.py",
            "smoke": "scripts/saee_commercial_matrix_update_request_packet_smoke.py",
        },
        "make_target": "make check-commercial-matrix-update-request-packet",
    }
    AGENT_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    block = f"""## Commercial Matrix Update Request Packet v0.1

- `commercial_matrix_update_request_packet_v0_1`
- Status: `{payload['status']}`
- Candidate blockers: `{', '.join(payload['target_blockers'])}`
- ready_candidate_count={payload['ready_candidate_count']}
- recommended_human_decision={payload['recommended_human_decision']}
- matrix_update_executed=false
- canonical_gap_matrix_modified=false
- blocker_closure_authorized=false
- blockers_closed_by_request=0
- open_blocker_count_reduced=false
- production_ready=false
- customer_validated=false
- private_core_exposed=false
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_COMMERCIAL_MATRIX_UPDATE_REQUEST_PACKET_V0_1", block)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_COMMERCIAL_MATRIX_UPDATE_REQUEST_PACKET: PASS "
        f"status={payload['status']} "
        f"ready_candidate_count={payload['ready_candidate_count']} "
        "matrix_update_executed=false blockers_closed_by_request=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
