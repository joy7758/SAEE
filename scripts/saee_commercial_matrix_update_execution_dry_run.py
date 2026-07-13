#!/usr/bin/env python3
"""Preview commercial matrix-update execution without writing the matrix.

This dry run reads the explicit execution request and the approval validator
state. It never modifies the canonical gap matrix or closure board. In the
current hold state, it records that human execution approval is still missing.
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
REQUEST = OUT_DIR / "commercial_matrix_update_execution_request_packet.local.json"
APPROVAL = OUT_DIR / "commercial_matrix_update_execution_approval_validation.local.json"
GAP_MATRIX = COMMERCIAL_DIR / "production_blocker_gap_matrix/gap_matrix.local.json"
CLOSURE_BOARD = (
    COMMERCIAL_DIR
    / "commercial_blocker_closure_readiness_board/closure_readiness_board.local.json"
)

OUT_JSON = OUT_DIR / "commercial_matrix_update_execution_dry_run.local.json"
OUT_MD = OUT_DIR / "commercial_matrix_update_execution_dry_run.md"
OUT_CSV = OUT_DIR / "commercial_matrix_update_execution_dry_run.csv"
BOUNDARY = OUT_DIR / "commercial_matrix_update_execution_dry_run_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_MATRIX_UPDATE_EXECUTION_DRY_RUN_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_DRY_RUN_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
]

TARGET_BLOCKERS = [
    "support_contact",
    "customer_support",
    "sla",
    "on_call_rotation",
    "pricing_page",
]


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


def request_targets_by_id(request: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = request.get("execution_targets", [])
    if not isinstance(rows, list):
        return {}
    return {
        row.get("blocker_id"): row
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("blocker_id"), str)
    }


def build_preview_rows(
    request: dict[str, Any],
    approval: dict[str, Any],
    gap_matrix: dict[str, Any],
) -> list[dict[str, Any]]:
    matrix_by_id = matrix_rows_by_id(gap_matrix)
    targets_by_id = request_targets_by_id(request)
    approval_ready = approval.get("ready_for_matrix_update_execution") is True
    rows: list[dict[str, Any]] = []
    for blocker_id in TARGET_BLOCKERS:
        matrix_row = matrix_by_id.get(blocker_id, {})
        target = targets_by_id.get(blocker_id, {})
        rows.append(
            {
                "blocker_id": blocker_id,
                "current_status": matrix_row.get("status", "missing"),
                "current_local_evidence_ready": matrix_row.get("local_evidence_ready") is True,
                "current_closure_allowed_by_matrix": matrix_row.get("closure_allowed_by_matrix") is True,
                "requested_marker": target.get("requested_marker", ""),
                "requested_review_ready_marker_only": target.get("requested_review_ready_marker_only") is True,
                "blocked_reason": "" if approval_ready else "human_execution_approval_missing",
                "would_update_if_approved": approval_ready,
                "would_keep_status": "open",
                "would_keep_local_evidence_ready": False,
                "would_keep_closure_allowed_by_matrix": False,
                "closure_allowed_by_dry_run": False,
            }
        )
    return rows


def build_payload() -> dict[str, Any]:
    request = read_json(REQUEST)
    approval = read_json(APPROVAL)
    gap_matrix = read_json(GAP_MATRIX)
    closure_board = read_json(CLOSURE_BOARD)

    boundary_violations: list[str] = []
    for source_name, source in [
        ("request", request),
        ("approval", approval),
        ("gap_matrix", gap_matrix),
        ("closure_board", closure_board),
    ]:
        for key in [
            "runtime_modified",
            "backend_modified",
            "kernel_modified",
            "api_schema_modified",
            "private_core_exposed",
            "product_launched",
            "customer_validated",
            "customer_contacted",
            "external_calls_made",
            "external_model_api_called",
        ]:
            if source.get(key) is True:
                boundary_violations.append(f"{source_name}.{key}")

    request_ready = request.get("status") == "ready_for_explicit_human_execution_approval_no_closure"
    approval_ready = approval.get("ready_for_matrix_update_execution") is True
    human_execution_approved = approval.get("human_execution_approved") is True
    if not request_ready:
        status = "hold_execution_request_not_ready"
    elif boundary_violations:
        status = "stop_boundary_violation"
    elif not approval_ready or not human_execution_approved:
        status = "hold_human_execution_approval_required"
    else:
        status = "ready_for_no_write_preview_only"

    preview_rows = build_preview_rows(request, approval, gap_matrix)
    would_update_count = 5 if status == "ready_for_no_write_preview_only" else 0
    blocked_preview_count = len([row for row in preview_rows if row["blocked_reason"]])

    return {
        "commercial_matrix_update_execution_dry_run_v0_1": True,
        "dry_run_type": "matrix_update_execution_no_write_preview",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_execution_request_packet": rel(REQUEST),
        "source_approval_validation": rel(APPROVAL),
        "source_gap_matrix": rel(GAP_MATRIX),
        "source_closure_board": rel(CLOSURE_BOARD),
        "dry_run_only": True,
        "human_execution_approved": human_execution_approved,
        "ready_for_matrix_update_execution": approval_ready,
        "apply_performed": False,
        "matrix_update_executed": False,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_dry_run": 0,
        "open_blocker_count_reduced": False,
        "target_blockers": TARGET_BLOCKERS,
        "target_count": len(TARGET_BLOCKERS),
        "would_update_count": would_update_count,
        "blocked_preview_count": blocked_preview_count,
        "preview_rows": preview_rows,
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": sorted(boundary_violations),
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
        "next_human_action": (
            "Provide explicit matrix-update execution approval if the owner wants to "
            "apply review-ready markers only. Keep blockers open until separate "
            "closure evidence exists."
        ),
    }


def write_outputs(payload: dict[str, Any]) -> None:
    write_json(OUT_JSON, payload)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "blocker_id",
            "current_status",
            "current_local_evidence_ready",
            "current_closure_allowed_by_matrix",
            "requested_marker",
            "blocked_reason",
            "would_update_if_approved",
            "would_keep_status",
            "would_keep_local_evidence_ready",
            "would_keep_closure_allowed_by_matrix",
            "closure_allowed_by_dry_run",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["preview_rows"]:
            writer.writerow({field: row.get(field) for field in fields})

    table = "\n".join(
        "| {blocker_id} | {current_status} | {requested_marker} | {blocked_reason} | {would_update_if_approved} | {would_keep_status} |".format(
            **row
        )
        for row in payload["preview_rows"]
    )
    OUT_MD.write_text(
        f"""# SAEE Commercial Matrix Update Execution Dry Run v0.1

Status: `{payload['status']}`

This is a no-write dry run. It previews the requested matrix marker update but
does not modify the canonical gap matrix, closure board, backend, runtime, API
schema, landing page, or private core.

## Summary

- dry_run_only: `true`
- human_execution_approved: `{str(payload['human_execution_approved']).lower()}`
- ready_for_matrix_update_execution: `{str(payload['ready_for_matrix_update_execution']).lower()}`
- target_count: `{payload['target_count']}`
- would_update_count: `{payload['would_update_count']}`
- blocked_preview_count: `{payload['blocked_preview_count']}`
- apply_performed: `false`
- matrix_update_executed: `false`
- canonical_gap_matrix_modified: `false`
- blocker_closure_authorized: `false`
- blockers_closed_by_dry_run: `0`
- production_ready: `false`
- customer_validated: `false`

## Preview Rows

| Blocker | Current status | Requested marker | Blocked reason | Would update if approved | Status after preview |
| --- | --- | --- | --- | --- | --- |
{table}

## Boundary

No official blocker status was changed. No blocker was closed. No production,
customer-validation, launch, pricing-publication, checkout, backend, runtime,
kernel, API schema, or private-core claim was added.
""",
        encoding="utf-8",
    )
    BOUNDARY.write_text(
        """# SAEE Commercial Matrix Update Execution Dry Run Boundary Audit

commercial_matrix_update_execution_dry_run_v0_1: true
dry_run_type: matrix_update_execution_no_write_preview

- No canonical gap matrix modified.
- No canonical closure board modified.
- No matrix update executed.
- No blocker closure authorized.
- No blockers closed by this dry run.
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
        """# SAEE Commercial Matrix Update Execution Dry Run v0.1

commercial_matrix_update_execution_dry_run_v0_1: true
status: hold_human_execution_approval_required

Purpose: preview the approved-scope matrix marker update path without writing
the canonical gap matrix or closing any blockers. Current output is blocked
because explicit human execution approval has not been entered as structured
approval input.

Entrypoints:

- `phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_dry_run.local.json`
- `phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_dry_run.md`
- `phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_dry_run.csv`
- `phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_dry_run_boundary_audit.md`
""",
        encoding="utf-8",
    )
    GATE.write_text(
        f"""# SAEE Commercial Matrix Update Execution Dry Run Gate

answer: {payload['status']}

reason: The matrix-update execution request exists, but structured human
execution approval is not yet ready. The dry run therefore records a blocked
no-write preview and does not modify the canonical matrix or close blockers.

boundary:
- dry_run_only: true
- apply_performed: false
- matrix_update_executed: false
- canonical_gap_matrix_modified: false
- canonical_closure_board_modified: false
- blocker_closure_authorized: false
- blockers_closed_by_dry_run: 0
- production_ready: false
- customer_validated: false
- private_core_exposed: false

next_action: provide explicit structured human approval before any separate
matrix marker update execution is attempted.
""",
        encoding="utf-8",
    )

    for line in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_EXECUTION_DRY_RUN_V0_1.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_dry_run.local.json",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_dry_run.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_dry_run.csv",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_dry_run_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_DRY_RUN_GATE.md",
        "/scripts/saee_commercial_matrix_update_execution_dry_run.py",
        "/scripts/saee_commercial_matrix_update_execution_dry_run_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["commercial_matrix_update_execution_dry_run_v0_1"] = {
        "name": "SAEE Commercial Matrix Update Execution Dry Run v0.1",
        "status": payload["status"],
        "dry_run_type": payload["dry_run_type"],
        "dry_run_only": True,
        "human_execution_approved": payload["human_execution_approved"],
        "ready_for_matrix_update_execution": payload["ready_for_matrix_update_execution"],
        "apply_performed": False,
        "matrix_update_executed": False,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_dry_run": 0,
        "open_blocker_count_reduced": False,
        "target_count": payload["target_count"],
        "would_update_count": payload["would_update_count"],
        "blocked_preview_count": payload["blocked_preview_count"],
        "target_blockers": payload["target_blockers"],
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "customer_contacted": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "entrypoints": {
            "summary": rel(OUT_JSON),
            "report": rel(OUT_MD),
            "csv": rel(OUT_CSV),
            "boundary_audit": rel(BOUNDARY),
            "gate": rel(GATE),
            "top_doc": rel(TOP_DOC),
            "runner": "scripts/saee_commercial_matrix_update_execution_dry_run.py",
            "smoke": "scripts/saee_commercial_matrix_update_execution_dry_run_smoke.py",
        },
        "make_target": "make check-commercial-matrix-update-execution-dry-run",
    }
    AGENT_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    block = f"""## Commercial Matrix Update Execution Dry Run v0.1

- `commercial_matrix_update_execution_dry_run_v0_1`
- Status: `{payload['status']}`
- dry_run_only=true
- human_execution_approved={str(payload['human_execution_approved']).lower()}
- ready_for_matrix_update_execution={str(payload['ready_for_matrix_update_execution']).lower()}
- target_count={payload['target_count']}
- would_update_count={payload['would_update_count']}
- blocked_preview_count={payload['blocked_preview_count']}
- apply_performed=false
- matrix_update_executed=false
- canonical_gap_matrix_modified=false
- blocker_closure_authorized=false
- blockers_closed_by_dry_run=0
- production_ready=false
- customer_validated=false
- private_core_exposed=false
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_DRY_RUN_V0_1", block)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_DRY_RUN: PASS "
        f"status={payload['status']} "
        f"target_count={payload['target_count']} "
        f"would_update_count={payload['would_update_count']} "
        "apply_performed=false matrix_update_executed=false blockers_closed_by_dry_run=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
