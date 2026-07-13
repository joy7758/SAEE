#!/usr/bin/env python3
"""Prepare a 23-row matrix-request scope refresh without activating it."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
REQUEST_DIR = COMMERCIAL_DIR / "matrix_update_requests"
OUT_DIR = REQUEST_DIR / "commercial_matrix_update_scope_refresh"
CATALOG = (
    REQUEST_DIR
    / "commercial_review_ready_marker_catalog/commercial_review_ready_marker_catalog.local.json"
)
CURRENT_REQUEST = REQUEST_DIR / "commercial_matrix_update_request_packet.local.json"
CURRENT_EXECUTION_REQUEST = (
    REQUEST_DIR / "commercial_matrix_update_execution_request_packet.local.json"
)
GAP_MATRIX = COMMERCIAL_DIR / "production_blocker_gap_matrix/gap_matrix.local.json"
OUT_JSON = OUT_DIR / "commercial_matrix_update_scope_refresh.local.json"
OUT_MD = OUT_DIR / "commercial_matrix_update_scope_refresh.md"
OUT_CSV = OUT_DIR / "commercial_matrix_update_scope_refresh.csv"
BOUNDARY = OUT_DIR / "commercial_matrix_update_scope_refresh_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_MATRIX_UPDATE_SCOPE_REFRESH_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_SCOPE_REFRESH_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
]

FALSE_FLAGS: dict[str, Any] = {
    "active_matrix_request_replaced": False,
    "execution_request_regenerated": False,
    "approval_scope_changed": False,
    "scope_refresh_execution_authorized": False,
    "matrix_update_execution_authorized": False,
    "matrix_update_executed": False,
    "canonical_gap_matrix_modified": False,
    "canonical_closure_board_modified": False,
    "blocker_closure_authorized": False,
    "blockers_closed_by_scope_refresh": 0,
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
    if not path.is_file():
        raise SystemExit(f"missing required source: {rel(path)}")
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


def build_payload() -> dict[str, Any]:
    catalog = read_json(CATALOG)
    current_request = read_json(CURRENT_REQUEST)
    current_execution_request = read_json(CURRENT_EXECUTION_REQUEST)
    gap_matrix = read_json(GAP_MATRIX)

    catalog_rows = catalog.get("candidate_rows", [])
    current_ids = current_request.get("target_blockers", [])
    execution_ids = current_execution_request.get("target_blockers", [])
    if not isinstance(catalog_rows, list):
        catalog_rows = []
    if not isinstance(current_ids, list):
        current_ids = []
    if not isinstance(execution_ids, list):
        execution_ids = []

    proposed_rows: list[dict[str, Any]] = []
    for source_row in catalog_rows:
        if not isinstance(source_row, dict):
            continue
        blocker_id = source_row.get("blocker_id")
        if not isinstance(blocker_id, str):
            continue
        proposed_rows.append(
            {
                "blocker_id": blocker_id,
                "scope_change": "retain" if blocker_id in current_ids else "add",
                "source_group": source_row.get("source_group"),
                "source_path": source_row.get("source_path"),
                "source_status": source_row.get("source_status"),
                "requested_marker": source_row.get("requested_marker"),
                "review_ready_marker_candidate": source_row.get("review_ready_marker_candidate") is True,
                "current_matrix_status": source_row.get("matrix_current_status"),
                "current_matrix_local_evidence_ready": source_row.get("matrix_current_local_evidence_ready") is True,
                "current_matrix_closure_allowed": source_row.get("matrix_current_closure_allowed") is True,
                "proposed_status_after_future_update": "open",
                "proposed_local_evidence_ready_after_future_update": False,
                "proposed_closure_allowed_after_future_update": False,
                "requires_separate_human_scope_confirmation": True,
                "requires_exact_human_execution_approval_after_scope_confirmation": True,
                "execution_allowed_by_scope_refresh": False,
                "closure_allowed_by_scope_refresh": False,
            }
        )

    proposed_ids = [row["blocker_id"] for row in proposed_rows]
    retained_ids = [item for item in proposed_ids if item in current_ids]
    added_ids = [item for item in proposed_ids if item not in current_ids]
    removed_ids = [item for item in current_ids if item not in proposed_ids]
    canonical_rows = gap_matrix.get("matrix", [])
    canonical_ids = [
        row.get("blocker_id")
        for row in canonical_rows
        if isinstance(row, dict) and isinstance(row.get("blocker_id"), str)
    ]

    violations: list[str] = []
    for source_name, source in [
        ("catalog", catalog),
        ("current_request", current_request),
        ("current_execution_request", current_execution_request),
        ("gap_matrix", gap_matrix),
    ]:
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
                violations.append(f"{source_name}.{key}")

    catalog_is_safe = (
        catalog.get("status") == "ready_for_human_matrix_update_scope_review_no_execution"
        and catalog.get("review_ready_marker_candidate_count") == 23
        and catalog.get("not_cataloged_blocker_ids") == ["customer_validated"]
        and len(proposed_ids) == 23
        and len(set(proposed_ids)) == 23
        and "customer_validated" not in proposed_ids
        and all(row["review_ready_marker_candidate"] for row in proposed_rows)
        and all(row["current_matrix_status"] == "open" for row in proposed_rows)
        and all(row["current_matrix_local_evidence_ready"] is False for row in proposed_rows)
        and all(row["current_matrix_closure_allowed"] is False for row in proposed_rows)
        and all(row["execution_allowed_by_scope_refresh"] is False for row in proposed_rows)
        and all(row["closure_allowed_by_scope_refresh"] is False for row in proposed_rows)
    )
    active_pipeline_unchanged = (
        len(current_ids) == 5
        and current_ids == execution_ids
        and current_request.get("matrix_update_executed") is False
        and current_execution_request.get("matrix_update_executed") is False
    )
    if violations:
        status = "stop_boundary_violation"
    elif not catalog_is_safe:
        status = "hold_catalog_not_ready_for_scope_refresh"
    elif not active_pipeline_unchanged:
        status = "hold_active_pipeline_state_changed"
    else:
        status = "ready_for_human_scope_refresh_review_no_execution"

    payload: dict[str, Any] = {
        "commercial_matrix_update_scope_refresh_v0_1": True,
        "refresh_type": "review_ready_marker_scope_refresh_packet_no_activation_no_execution",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_catalog": rel(CATALOG),
        "source_current_request": rel(CURRENT_REQUEST),
        "source_current_execution_request": rel(CURRENT_EXECUTION_REQUEST),
        "source_gap_matrix": rel(GAP_MATRIX),
        "canonical_open_blocker_count": len(canonical_ids),
        "previous_target_count": len(current_ids),
        "previous_target_ids": current_ids,
        "refreshed_target_count": len(proposed_ids),
        "refreshed_target_ids": proposed_ids,
        "retained_target_count": len(retained_ids),
        "retained_target_ids": retained_ids,
        "added_target_count": len(added_ids),
        "added_target_ids": added_ids,
        "removed_target_count": len(removed_ids),
        "removed_target_ids": removed_ids,
        "not_cataloged_blocker_count": 1,
        "not_cataloged_blocker_ids": ["customer_validated"],
        "scope_refresh_rows": proposed_rows,
        "scope_refresh_packet_generated": True,
        "human_scope_review_required": True,
        "exact_human_execution_approval_still_required": True,
        "separate_blocker_closure_approval_still_required": True,
        "recommendation_gate": "conditional",
        "would_recommend_to_potential_customer": "conditional",
        "recommendation_reason": (
            "The local review scope can be expanded from five to twenty-three source-backed "
            "markers, but the active request must remain unchanged until human scope review, "
            "and customer validation remains missing."
        ),
        "boundary_violation_count": len(violations),
        "boundary_violations": sorted(violations),
        "next_human_action": (
            "Review this 23-row scope refresh. A separate explicit request is required to "
            "replace the active five-row request, and the exact execution approval phrase is "
            "still required after that replacement."
        ),
    }
    payload.update(FALSE_FLAGS)
    return payload


def write_outputs(payload: dict[str, Any]) -> None:
    write_json(OUT_JSON, payload)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        fields = [
            "blocker_id",
            "scope_change",
            "source_group",
            "source_status",
            "requested_marker",
            "review_ready_marker_candidate",
            "current_matrix_status",
            "requires_separate_human_scope_confirmation",
            "requires_exact_human_execution_approval_after_scope_confirmation",
            "execution_allowed_by_scope_refresh",
            "closure_allowed_by_scope_refresh",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["scope_refresh_rows"]:
            writer.writerow({field: row.get(field) for field in fields})

    table = "\n".join(
        f"| `{row['blocker_id']}` | `{row['scope_change']}` | `{row['source_group']}` | "
        f"`{row['requested_marker']}` | `false` |"
        for row in payload["scope_refresh_rows"]
    )
    OUT_MD.write_text(
        f"""# SAEE Commercial Matrix Update Scope Refresh v0.1

Status: `{payload['status']}`

This packet prepares a human-reviewable expansion from the current five-row
matrix request to 23 source-backed review-ready markers. It does not replace
the active request, alter the approval scope, execute a matrix update, or close
any blocker.

## Scope delta

- previous_target_count: `{payload['previous_target_count']}`
- refreshed_target_count: `{payload['refreshed_target_count']}`
- retained_target_count: `{payload['retained_target_count']}`
- added_target_count: `{payload['added_target_count']}`
- removed_target_count: `{payload['removed_target_count']}`
- not_cataloged_blocker_ids: `{','.join(payload['not_cataloged_blocker_ids'])}`

| Blocker | Change | Source | Marker | Execution allowed |
| --- | --- | --- | --- | --- |
{table}

## Boundary

- active_matrix_request_replaced=false
- execution_request_regenerated=false
- approval_scope_changed=false
- matrix_update_executed=false
- blockers_closed_by_scope_refresh=0
- exact_human_execution_approval_still_required=true
- production_ready=false
- customer_validated=false
""",
        encoding="utf-8",
    )
    BOUNDARY.write_text(
        """# Commercial Matrix Update Scope Refresh Boundary Audit

- Scope-review packet only; the active five-row request remains unchanged.
- No execution request was regenerated and no approval scope was changed.
- No canonical gap matrix or closure board was modified.
- No matrix update or blocker closure was authorized or performed.
- No production, customer, pricing-publication, checkout, or launch claim was added.
- No runtime, backend, kernel, API schema, or private core was modified.

active_matrix_request_replaced=false
execution_request_regenerated=false
approval_scope_changed=false
matrix_update_executed=false
blockers_closed_by_scope_refresh=0
production_ready=false
customer_validated=false
private_core_exposed=false
""",
        encoding="utf-8",
    )
    TOP_DOC.write_text(
        f"""# SAEE Commercial Matrix Update Scope Refresh v0.1

commercial_matrix_update_scope_refresh_v0_1: true
status: {payload['status']}
previous_target_count: {payload['previous_target_count']}
refreshed_target_count: {payload['refreshed_target_count']}
retained_target_count: {payload['retained_target_count']}
added_target_count: {payload['added_target_count']}
removed_target_count: {payload['removed_target_count']}
not_cataloged_blocker_ids: {','.join(payload['not_cataloged_blocker_ids'])}
human_scope_review_required: true
exact_human_execution_approval_still_required: true
active_matrix_request_replaced=false
approval_scope_changed=false
matrix_update_executed=false
blockers_closed_by_scope_refresh=0
production_ready=false
customer_validated=false
""",
        encoding="utf-8",
    )
    GATE.write_text(
        f"""# SAEE Commercial Matrix Update Scope Refresh Gate

answer: conditional_human_scope_review_required_no_execution
recommendation_gate: conditional

reason:
The 23-row source-backed scope is ready for human review, while the active
five-row request and its future execution authorization remain unchanged.
`customer_validated` is intentionally excluded because no external customer
validation evidence exists.

status: {payload['status']}
previous_target_count: {payload['previous_target_count']}
refreshed_target_count: {payload['refreshed_target_count']}
not_cataloged_blocker_ids: {','.join(payload['not_cataloged_blocker_ids'])}

boundary:
active_matrix_request_replaced: false
execution_request_regenerated: false
approval_scope_changed: false
matrix_update_execution_authorized: false
matrix_update_executed: false
blocker_closure_authorized: false
blockers_closed_by_scope_refresh: 0
production_ready: false
customer_validated: false
private_core_exposed: false

next_action:
Human review of this scope packet only. Replacing the active request and
executing marker application each require separate explicit approval.
""",
        encoding="utf-8",
    )

    for line in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_SCOPE_REFRESH_V0_1.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_scope_refresh/commercial_matrix_update_scope_refresh.local.json",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_scope_refresh/commercial_matrix_update_scope_refresh.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_scope_refresh/commercial_matrix_update_scope_refresh.csv",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_scope_refresh/commercial_matrix_update_scope_refresh_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_SCOPE_REFRESH_GATE.md",
        "/scripts/saee_commercial_matrix_update_scope_refresh.py",
        "/scripts/saee_commercial_matrix_update_scope_refresh_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    keys = [
        "status",
        "canonical_open_blocker_count",
        "previous_target_count",
        "previous_target_ids",
        "refreshed_target_count",
        "refreshed_target_ids",
        "retained_target_count",
        "retained_target_ids",
        "added_target_count",
        "added_target_ids",
        "removed_target_count",
        "removed_target_ids",
        "not_cataloged_blocker_count",
        "not_cataloged_blocker_ids",
        "scope_refresh_packet_generated",
        "human_scope_review_required",
        "exact_human_execution_approval_still_required",
        "recommendation_gate",
        "active_matrix_request_replaced",
        "execution_request_regenerated",
        "approval_scope_changed",
        "matrix_update_execution_authorized",
        "matrix_update_executed",
        "blocker_closure_authorized",
        "blockers_closed_by_scope_refresh",
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
    ]
    index["commercial_matrix_update_scope_refresh_v0_1"] = {
        key: payload[key] for key in keys
    }
    write_json(AGENT_INDEX, index)

    block = f"""## Commercial Matrix Update Scope Refresh v0.1

Status: `{payload['status']}`.

The no-execution review scope is prepared to expand from
`previous_target_count={payload['previous_target_count']}` to
`refreshed_target_count={payload['refreshed_target_count']}` source-backed
markers. `added_target_count={payload['added_target_count']}`,
`not_cataloged_blocker_ids={','.join(payload['not_cataloged_blocker_ids'])}`,
`active_matrix_request_replaced=false`, `approval_scope_changed=false`,
`matrix_update_executed=false`, `blockers_closed_by_scope_refresh=0`,
`production_ready=false`, and `customer_validated=false`.
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_COMMERCIAL_MATRIX_UPDATE_SCOPE_REFRESH", block)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_COMMERCIAL_MATRIX_UPDATE_SCOPE_REFRESH: PASS "
        f"status={payload['status']} previous={payload['previous_target_count']} "
        f"refreshed={payload['refreshed_target_count']} added={payload['added_target_count']} "
        "active_request_replaced=false matrix_update_executed=false "
        "blockers_closed=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
