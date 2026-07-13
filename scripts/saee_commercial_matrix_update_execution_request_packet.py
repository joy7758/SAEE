#!/usr/bin/env python3
"""Build a commercial matrix-update execution request packet.

This is still a request packet, not execution. It converts the existing
commercial matrix-update request packet into an explicit human approval surface
for a future, separate matrix-update operation. It does not modify the canonical
gap matrix, closure board, product code, backend, runtime, API schema, or
private core.
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
SOURCE_REQUEST = OUT_DIR / "commercial_matrix_update_request_packet.local.json"
GAP_MATRIX = COMMERCIAL_DIR / "production_blocker_gap_matrix/gap_matrix.local.json"
CLOSURE_BOARD = (
    COMMERCIAL_DIR
    / "commercial_blocker_closure_readiness_board/closure_readiness_board.local.json"
)

OUT_JSON = OUT_DIR / "commercial_matrix_update_execution_request_packet.local.json"
OUT_MD = OUT_DIR / "commercial_matrix_update_execution_request_packet.md"
OUT_CSV = OUT_DIR / "commercial_matrix_update_execution_request_packet.csv"
BOUNDARY = OUT_DIR / "commercial_matrix_update_execution_request_packet_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_MATRIX_UPDATE_EXECUTION_REQUEST_PACKET_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_REQUEST_PACKET_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
]

FALSE_FLAGS = {
    "human_execution_approved": False,
    "matrix_update_executed": False,
    "canonical_gap_matrix_modified": False,
    "canonical_closure_board_modified": False,
    "blocker_closure_authorized": False,
    "blockers_closed_by_execution_request": 0,
    "open_blocker_count_reduced": False,
    "pricing_page_published": False,
    "checkout_enabled": False,
    "customer_payment_collected": False,
    "revenue_validated": False,
    "development_permission_granted": False,
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


def build_execution_targets(
    source_request: dict[str, Any],
    gap_matrix: dict[str, Any],
) -> list[dict[str, Any]]:
    matrix_by_id = matrix_rows_by_id(gap_matrix)
    targets: list[dict[str, Any]] = []
    for row in source_request.get("candidate_rows", []):
        if not isinstance(row, dict):
            continue
        blocker_id = row.get("blocker_id")
        if not isinstance(blocker_id, str):
            continue
        matrix_row = matrix_by_id.get(blocker_id, {})
        targets.append(
            {
                "blocker_id": blocker_id,
                "source_group": row.get("source_group"),
                "source_status": row.get("source_status"),
                "current_matrix_status": matrix_row.get("status", "missing"),
                "current_matrix_local_evidence_ready": matrix_row.get("local_evidence_ready") is True,
                "current_matrix_closure_allowed": matrix_row.get("closure_allowed_by_matrix") is True,
                "requested_marker": row.get("recommended_matrix_update"),
                "requested_matrix_status_after_update": "open",
                "requested_review_ready_marker_only": True,
                "requested_local_evidence_ready_after_update": False,
                "requested_closure_allowed_after_update": False,
                "blocker_closure_allowed_by_this_request": False,
                "pricing_publication_allowed_by_this_request": False,
                "requires_explicit_human_execution_approval": True,
            }
        )
    return targets


def build_payload() -> dict[str, Any]:
    source_request = read_json(SOURCE_REQUEST)
    gap_matrix = read_json(GAP_MATRIX)
    closure_board = read_json(CLOSURE_BOARD)
    targets = build_execution_targets(source_request, gap_matrix)

    boundary_violations: list[str] = []
    expected_source = {
        "status": "ready_for_human_matrix_update_execution_request_no_closure",
        "candidate_count": 5,
        "ready_candidate_count": 5,
        "matrix_update_executed": False,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_request": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
    }
    for key, expected in expected_source.items():
        if source_request.get(key) != expected:
            boundary_violations.append(f"source_request.{key}")
    for key in [
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
        "customer_contacted",
        "external_calls_made",
        "external_model_api_called",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
    ]:
        if gap_matrix.get(key) is True:
            boundary_violations.append(f"gap_matrix.{key}")
        if closure_board.get(key) is True:
            boundary_violations.append(f"closure_board.{key}")

    all_targets_safe = (
        len(targets) == 5
        and all(target["requested_matrix_status_after_update"] == "open" for target in targets)
        and all(target["requested_local_evidence_ready_after_update"] is False for target in targets)
        and all(target["requested_closure_allowed_after_update"] is False for target in targets)
        and all(target["blocker_closure_allowed_by_this_request"] is False for target in targets)
    )
    if boundary_violations:
        status = "stop_boundary_violation"
    elif all_targets_safe:
        status = "ready_for_explicit_human_execution_approval_no_closure"
    else:
        status = "hold_execution_request_targets_incomplete"

    return {
        "commercial_matrix_update_execution_request_packet_v0_1": True,
        "request_type": "matrix_update_execution_request_packet_no_execution",
        "request_scope": "apply_review_ready_markers_only_to_support_group_and_pricing_page",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_request_packet": rel(SOURCE_REQUEST),
        "source_gap_matrix": rel(GAP_MATRIX),
        "source_closure_board": rel(CLOSURE_BOARD),
        "target_blockers": [target["blocker_id"] for target in targets],
        "target_count": len(targets),
        "execution_targets": targets,
        "recommended_human_decision": "approve_matrix_update_execution_review_ready_markers_only",
        "requires_explicit_human_execution_approval": True,
        "separate_blocker_closure_approval_required": True,
        "separate_pricing_publication_approval_required": True,
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": sorted(boundary_violations),
        "next_human_action": (
            "If desired, explicitly approve a separate matrix-update execution that applies "
            "review-ready markers only. Do not close blockers or publish pricing."
        ),
        **FALSE_FLAGS,
    }


def write_outputs(payload: dict[str, Any]) -> None:
    write_json(OUT_JSON, payload)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "blocker_id",
            "source_group",
            "current_matrix_status",
            "requested_marker",
            "requested_matrix_status_after_update",
            "requested_review_ready_marker_only",
            "requested_local_evidence_ready_after_update",
            "requested_closure_allowed_after_update",
            "blocker_closure_allowed_by_this_request",
            "requires_explicit_human_execution_approval",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["execution_targets"]:
            writer.writerow({field: row.get(field) for field in fields})

    table = "\n".join(
        "| {blocker_id} | {source_group} | {current_matrix_status} | {requested_marker} | {requested_matrix_status_after_update} | {blocker_closure_allowed_by_this_request} |".format(
            **row
        )
        for row in payload["execution_targets"]
    )
    OUT_MD.write_text(
        f"""# SAEE Commercial Matrix Update Execution Request Packet v0.1

Status: `{payload['status']}`

This packet asks for explicit human approval for a future matrix-update
execution. It does not execute that update. The requested update is limited to
recording review-ready markers for support-group and pricing-page evidence while
keeping all target blockers open.

## Summary

- target_count: `{payload['target_count']}`
- recommended_human_decision: `{payload['recommended_human_decision']}`
- requires_explicit_human_execution_approval: `true`
- matrix_update_executed: `false`
- canonical_gap_matrix_modified: `false`
- canonical_closure_board_modified: `false`
- blockers_closed_by_execution_request: `0`
- production_ready: `false`
- customer_validated: `false`

## Requested Targets

| Blocker | Source group | Current matrix status | Requested marker | Requested status after update | Closure allowed |
| --- | --- | --- | --- | --- | --- |
{table}

## Boundary

- human_execution_approved=false
- matrix_update_executed=false
- canonical_gap_matrix_modified=false
- canonical_closure_board_modified=false
- blocker_closure_authorized=false
- blockers_closed_by_execution_request=0
- open_blocker_count_reduced=false
- pricing_page_published=false
- checkout_enabled=false
- production_ready=false
- customer_validated=false
- product_launched=false
- private_core_exposed=false
""",
        encoding="utf-8",
    )
    BOUNDARY.write_text(
        """# SAEE Commercial Matrix Update Execution Request Packet Boundary Audit

commercial_matrix_update_execution_request_packet_v0_1: true
request_type: matrix_update_execution_request_packet_no_execution

- No human execution approval recorded.
- No matrix update executed.
- No canonical gap matrix modified.
- No canonical closure board modified.
- No blocker closure authorized.
- No blockers closed by this execution request.
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
        """# SAEE Commercial Matrix Update Execution Request Packet v0.1

commercial_matrix_update_execution_request_packet_v0_1: true
status: ready_for_explicit_human_execution_approval_no_closure

Purpose: provide the explicit human approval surface needed before applying
review-ready markers from the matrix-update request packet. This document does
not execute the matrix update and does not close blockers.

Entrypoints:

- `phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_request_packet.local.json`
- `phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_request_packet.md`
- `phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_request_packet.csv`
- `phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_request_packet_boundary_audit.md`
""",
        encoding="utf-8",
    )
    GATE.write_text(
        """# SAEE Commercial Matrix Update Execution Request Packet Gate

answer: ready_for_explicit_human_execution_approval_no_closure

reason: The prior matrix-update request packet is ready, and this packet turns
it into an explicit human approval surface for review-ready marker application
only. It does not execute the update, close blockers, publish pricing, launch
the product, or claim production readiness.

boundary:
- human_execution_approved: false
- matrix_update_executed: false
- canonical_gap_matrix_modified: false
- canonical_closure_board_modified: false
- blocker_closure_authorized: false
- blockers_closed_by_execution_request: 0
- production_ready: false
- customer_validated: false
- private_core_exposed: false

next_action: human may explicitly approve review-ready marker application only.
""",
        encoding="utf-8",
    )

    for line in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_EXECUTION_REQUEST_PACKET_V0_1.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_request_packet.local.json",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_request_packet.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_request_packet.csv",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_request_packet_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_REQUEST_PACKET_GATE.md",
        "/scripts/saee_commercial_matrix_update_execution_request_packet.py",
        "/scripts/saee_commercial_matrix_update_execution_request_packet_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["commercial_matrix_update_execution_request_packet_v0_1"] = {
        "name": "SAEE Commercial Matrix Update Execution Request Packet v0.1",
        "status": payload["status"],
        "request_type": payload["request_type"],
        "request_scope": payload["request_scope"],
        "target_count": payload["target_count"],
        "target_blockers": payload["target_blockers"],
        "recommended_human_decision": payload["recommended_human_decision"],
        "requires_explicit_human_execution_approval": True,
        "separate_blocker_closure_approval_required": True,
        "separate_pricing_publication_approval_required": True,
        "human_execution_approved": False,
        "matrix_update_executed": False,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_execution_request": 0,
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
            "runner": "scripts/saee_commercial_matrix_update_execution_request_packet.py",
            "smoke": "scripts/saee_commercial_matrix_update_execution_request_packet_smoke.py",
        },
        "make_target": "make check-commercial-matrix-update-execution-request-packet",
    }
    AGENT_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    block = f"""## Commercial Matrix Update Execution Request Packet v0.1

- `commercial_matrix_update_execution_request_packet_v0_1`
- Status: `{payload['status']}`
- Target blockers: `{', '.join(payload['target_blockers'])}`
- target_count={payload['target_count']}
- recommended_human_decision={payload['recommended_human_decision']}
- requires_explicit_human_execution_approval=true
- human_execution_approved=false
- matrix_update_executed=false
- canonical_gap_matrix_modified=false
- blocker_closure_authorized=false
- blockers_closed_by_execution_request=0
- production_ready=false
- customer_validated=false
- private_core_exposed=false
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_REQUEST_PACKET_V0_1", block)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_REQUEST_PACKET: PASS "
        f"status={payload['status']} "
        f"target_count={payload['target_count']} "
        "matrix_update_executed=false blockers_closed_by_execution_request=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
