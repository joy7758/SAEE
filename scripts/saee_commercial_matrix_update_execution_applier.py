#!/usr/bin/env python3
"""Apply commercial matrix review-ready markers only after explicit approval.

Default mode is dry-run/no-write. A matrix output is written only when
`--apply` and `--confirm-human-approved-matrix-update` are both supplied and the
approval validator has already recorded `ready_for_matrix_update_execution=true`.

Even in apply mode, this script keeps blockers open and does not set
local_evidence_ready or closure_allowed_by_matrix.
"""

from __future__ import annotations

import argparse
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
DEFAULT_OUTPUT_GAP_MATRIX = GAP_MATRIX

OUT_JSON = OUT_DIR / "commercial_matrix_update_execution_applier.local.json"
OUT_MD = OUT_DIR / "commercial_matrix_update_execution_applier.md"
OUT_CSV = OUT_DIR / "commercial_matrix_update_execution_applier.csv"
BOUNDARY = OUT_DIR / "commercial_matrix_update_execution_applier_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPLIER_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPLIER_GATE.md"
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
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return str(resolved)


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


def target_rows_by_id(request: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = request.get("execution_targets", [])
    if not isinstance(rows, list):
        return {}
    return {
        row.get("blocker_id"): row
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("blocker_id"), str)
    }


def matrix_rows_by_id(matrix: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = matrix.get("matrix", [])
    if not isinstance(rows, list):
        return {}
    return {
        row.get("blocker_id"): row
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("blocker_id"), str)
    }


def apply_marker_to_matrix(
    matrix: dict[str, Any],
    request: dict[str, Any],
    output_path: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    now = datetime.now(timezone.utc).isoformat()
    targets = target_rows_by_id(request)
    updated = json.loads(json.dumps(matrix))
    rows = updated.get("matrix", [])
    apply_rows: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict) or row.get("blocker_id") not in TARGET_BLOCKERS:
            continue
        blocker_id = row["blocker_id"]
        target = targets.get(blocker_id, {})
        marker = target.get("requested_marker", "record_review_ready_no_closure")
        row["status"] = "open"
        row["local_evidence_ready"] = False
        row["closure_allowed_by_matrix"] = False
        row["review_ready_marker"] = marker
        row["review_ready_marker_applied"] = True
        row["review_ready_marker_applied_at"] = now
        row["review_ready_marker_source"] = rel(REQUEST)
        row["review_ready_marker_scope"] = "review_ready_markers_only_no_closure"
        row["next_required_action"] = (
            "Review-ready marker recorded. Keep blocker open until separate "
            "closure evidence and explicit closure approval exist."
        )
        apply_rows.append(
            {
                "blocker_id": blocker_id,
                "marker": marker,
                "status_after_apply": row["status"],
                "local_evidence_ready_after_apply": row["local_evidence_ready"],
                "closure_allowed_after_apply": row["closure_allowed_by_matrix"],
                "output_gap_matrix": rel(output_path),
            }
        )
    return updated, apply_rows


def build_payload(args: argparse.Namespace) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any] | None]:
    request = read_json(Path(args.request))
    approval = read_json(Path(args.approval_validation))
    matrix = read_json(Path(args.gap_matrix))
    output_gap_matrix = Path(args.output_gap_matrix)

    request_ready = request.get("status") == "ready_for_explicit_human_execution_approval_no_closure"
    approval_ready = approval.get("ready_for_matrix_update_execution") is True
    human_approved = approval.get("human_execution_approved") is True
    apply_requested = bool(args.apply)
    confirmation = bool(args.confirm_human_approved_matrix_update)
    target_count = len(request.get("target_blockers", []))
    boundary_violations: list[str] = []
    for source_name, source in [("request", request), ("approval", approval), ("gap_matrix", matrix)]:
        for key in [
            "runtime_modified",
            "backend_modified",
            "kernel_modified",
            "api_schema_modified",
            "private_core_exposed",
            "product_launched",
            "production_ready",
            "customer_validated",
            "customer_contacted",
            "external_calls_made",
            "external_model_api_called",
        ]:
            if source.get(key) is True:
                boundary_violations.append(f"{source_name}.{key}")

    output_matrix: dict[str, Any] | None = None
    apply_rows: list[dict[str, Any]] = []
    apply_preconditions_met = (
        apply_requested
        and confirmation
        and request_ready
        and approval_ready
        and human_approved
        and target_count == 5
        and not boundary_violations
    )
    if not request_ready:
        status = "hold_execution_request_not_ready"
    elif boundary_violations:
        status = "stop_boundary_violation"
    elif not approval_ready or not human_approved:
        status = "hold_human_execution_approval_required"
    elif not apply_requested:
        status = "ready_for_apply_pending_explicit_apply_flag"
    elif not confirmation:
        status = "hold_apply_confirmation_required"
    elif apply_preconditions_met:
        status = "review_ready_markers_applied_no_closure"
        output_matrix, apply_rows = apply_marker_to_matrix(matrix, request, output_gap_matrix)
        write_json(output_gap_matrix, output_matrix)
    else:
        status = "hold_apply_preconditions_not_met"

    apply_performed = output_matrix is not None
    execution_mode = "apply_write_gap_matrix_output" if apply_performed else "dry_run_no_write"
    return (
        {
            "commercial_matrix_update_execution_applier_v0_1": True,
            "applier_type": "matrix_review_ready_marker_applier",
            "status": status,
            "execution_mode": execution_mode,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_execution_request_packet": rel(Path(args.request)),
            "source_approval_validation": rel(Path(args.approval_validation)),
            "source_gap_matrix": rel(Path(args.gap_matrix)),
            "output_gap_matrix": rel(output_gap_matrix),
            "apply_requested": apply_requested,
            "human_apply_confirmation_provided": confirmation,
            "human_execution_approved": human_approved,
            "ready_for_matrix_update_execution": approval_ready,
            "apply_preconditions_met": apply_preconditions_met,
            "apply_performed": apply_performed,
            "matrix_update_executed": apply_performed,
            "canonical_gap_matrix_modified": apply_performed and output_gap_matrix.resolve() == GAP_MATRIX.resolve(),
            "canonical_closure_board_modified": False,
            "target_blockers": TARGET_BLOCKERS,
            "target_count": target_count,
            "apply_row_count": len(apply_rows),
            "applied_rows": apply_rows,
            "blocker_closure_authorized": False,
            "blockers_closed_by_applier": 0,
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
            "boundary_violation_count": len(boundary_violations),
            "boundary_violations": sorted(boundary_violations),
            "next_action": (
                "Create structured human approval and rerun with --apply --confirm-human-approved-matrix-update."
                if not apply_performed
                else "Review marker output, then run separate closure review only after evidence exists."
            ),
        },
        apply_rows,
        output_matrix,
    )


def write_outputs(payload: dict[str, Any], apply_rows: list[dict[str, Any]]) -> None:
    write_json(OUT_JSON, payload)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "blocker_id",
            "marker",
            "status_after_apply",
            "local_evidence_ready_after_apply",
            "closure_allowed_after_apply",
            "output_gap_matrix",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in apply_rows:
            writer.writerow({field: row.get(field, "") for field in fields})

    row_count = payload["apply_row_count"]
    OUT_MD.write_text(
        f"""# SAEE Commercial Matrix Update Execution Applier v0.1

Status: `{payload['status']}`

This applier is the controlled execution shell for review-ready matrix markers.
Default mode is no-write. Apply mode still keeps blockers open and never marks
local evidence ready or closure allowed.

## Summary

- execution_mode: `{payload['execution_mode']}`
- apply_requested: `{str(payload['apply_requested']).lower()}`
- human_apply_confirmation_provided: `{str(payload['human_apply_confirmation_provided']).lower()}`
- human_execution_approved: `{str(payload['human_execution_approved']).lower()}`
- ready_for_matrix_update_execution: `{str(payload['ready_for_matrix_update_execution']).lower()}`
- apply_preconditions_met: `{str(payload['apply_preconditions_met']).lower()}`
- apply_performed: `{str(payload['apply_performed']).lower()}`
- matrix_update_executed: `{str(payload['matrix_update_executed']).lower()}`
- canonical_gap_matrix_modified: `{str(payload['canonical_gap_matrix_modified']).lower()}`
- target_count: `{payload['target_count']}`
- apply_row_count: `{row_count}`
- blockers_closed_by_applier: `0`
- production_ready: `false`
- customer_validated: `false`

## Boundary

No blocker closure is authorized by this applier. No pricing page is published,
checkout is not enabled, customer validation is not claimed, and production
readiness is not claimed.
""",
        encoding="utf-8",
    )
    BOUNDARY.write_text(
        f"""# SAEE Commercial Matrix Update Execution Applier Boundary Audit

commercial_matrix_update_execution_applier_v0_1: true
execution_mode: {payload['execution_mode']}
status: {payload['status']}

- apply_performed: {str(payload['apply_performed']).lower()}
- matrix_update_executed: {str(payload['matrix_update_executed']).lower()}
- canonical_gap_matrix_modified: {str(payload['canonical_gap_matrix_modified']).lower()}
- canonical_closure_board_modified: false
- blocker_closure_authorized: false
- blockers_closed_by_applier: 0
- open_blocker_count_reduced: false
- pricing_page_published: false
- checkout_enabled: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- product_launched: false
- production_ready: false
- customer_validated: false
- customer_contacted: false
""",
        encoding="utf-8",
    )
    TOP_DOC.write_text(
        """# SAEE Commercial Matrix Update Execution Applier v0.1

commercial_matrix_update_execution_applier_v0_1: true
status: hold_human_execution_approval_required

Purpose: provide a controlled, explicit applier for review-ready markers in the
commercial gap matrix. Default mode is dry-run/no-write. Apply mode requires
structured human approval plus explicit command flags and still keeps all
blockers open.

Entrypoints:

- `phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_applier.local.json`
- `phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_applier.md`
- `phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_applier.csv`
- `phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_applier_boundary_audit.md`
""",
        encoding="utf-8",
    )
    GATE.write_text(
        f"""# SAEE Commercial Matrix Update Execution Applier Gate

answer: {payload['status']}

reason: The applier is available, but default state remains no-write unless
structured human approval and explicit apply confirmation are both present. It
does not close blockers or claim production readiness.

boundary:
- apply_performed: {str(payload['apply_performed']).lower()}
- matrix_update_executed: {str(payload['matrix_update_executed']).lower()}
- canonical_gap_matrix_modified: {str(payload['canonical_gap_matrix_modified']).lower()}
- blocker_closure_authorized: false
- blockers_closed_by_applier: 0
- production_ready: false
- customer_validated: false
- private_core_exposed: false

next_action: create structured human approval before any marker application.
""",
        encoding="utf-8",
    )

    for line in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPLIER_V0_1.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_applier.local.json",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_applier.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_applier.csv",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_applier_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPLIER_GATE.md",
        "/scripts/saee_commercial_matrix_update_execution_applier.py",
        "/scripts/saee_commercial_matrix_update_execution_applier_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["commercial_matrix_update_execution_applier_v0_1"] = {
        "name": "SAEE Commercial Matrix Update Execution Applier v0.1",
        "status": payload["status"],
        "execution_mode": payload["execution_mode"],
        "apply_requested": payload["apply_requested"],
        "human_apply_confirmation_provided": payload["human_apply_confirmation_provided"],
        "human_execution_approved": payload["human_execution_approved"],
        "ready_for_matrix_update_execution": payload["ready_for_matrix_update_execution"],
        "apply_preconditions_met": payload["apply_preconditions_met"],
        "apply_performed": payload["apply_performed"],
        "matrix_update_executed": payload["matrix_update_executed"],
        "canonical_gap_matrix_modified": payload["canonical_gap_matrix_modified"],
        "canonical_closure_board_modified": False,
        "target_count": payload["target_count"],
        "apply_row_count": payload["apply_row_count"],
        "blocker_closure_authorized": False,
        "blockers_closed_by_applier": 0,
        "open_blocker_count_reduced": False,
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
            "runner": "scripts/saee_commercial_matrix_update_execution_applier.py",
            "smoke": "scripts/saee_commercial_matrix_update_execution_applier_smoke.py",
        },
        "make_target": "make check-commercial-matrix-update-execution-applier",
    }
    AGENT_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    block = f"""## Commercial Matrix Update Execution Applier v0.1

- `commercial_matrix_update_execution_applier_v0_1`
- Status: `{payload['status']}`
- execution_mode={payload['execution_mode']}
- apply_requested={str(payload['apply_requested']).lower()}
- human_execution_approved={str(payload['human_execution_approved']).lower()}
- ready_for_matrix_update_execution={str(payload['ready_for_matrix_update_execution']).lower()}
- apply_performed={str(payload['apply_performed']).lower()}
- matrix_update_executed={str(payload['matrix_update_executed']).lower()}
- canonical_gap_matrix_modified={str(payload['canonical_gap_matrix_modified']).lower()}
- blocker_closure_authorized=false
- blockers_closed_by_applier=0
- production_ready=false
- customer_validated=false
- private_core_exposed=false
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPLIER_V0_1", block)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", default=str(REQUEST))
    parser.add_argument("--approval-validation", default=str(APPROVAL))
    parser.add_argument("--gap-matrix", default=str(GAP_MATRIX))
    parser.add_argument("--output-gap-matrix", default=str(DEFAULT_OUTPUT_GAP_MATRIX))
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--confirm-human-approved-matrix-update", action="store_true")
    return parser.parse_args()


def main() -> None:
    payload, apply_rows, _ = build_payload(parse_args())
    write_outputs(payload, apply_rows)
    print(
        "SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPLIER: PASS "
        f"status={payload['status']} "
        f"execution_mode={payload['execution_mode']} "
        f"apply_performed={str(payload['apply_performed']).lower()} "
        f"matrix_update_executed={str(payload['matrix_update_executed']).lower()} "
        "blockers_closed_by_applier=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
