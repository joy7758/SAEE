#!/usr/bin/env python3
"""Build a local commercial evidence sprint sequencer for SAEE.

The sequencer is a read-only planning surface. It orders current commercial
blockers for human review, but it does not assign owners, collect evidence,
execute work, close blockers, launch product, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_evidence_sprint_sequencer"
OUTPUT_JSON = OUTPUT_DIR / "commercial_evidence_sprint_sequencer.local.json"
OUTPUT_MD = OUTPUT_DIR / "commercial_evidence_sprint_sequencer.md"
OUTPUT_CSV = OUTPUT_DIR / "commercial_evidence_sprint_sequencer.csv"
OUTPUT_BOUNDARY = OUTPUT_DIR / "commercial_evidence_sprint_sequencer_boundary_audit.md"
README_PATH = OUTPUT_DIR / "README.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_EVIDENCE_SPRINT_SEQUENCER_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_COMMERCIAL_EVIDENCE_SPRINT_SEQUENCER_RECOMMENDATION_GATE.md"

DASHBOARD_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_readiness_dashboard/"
    "commercial_readiness_dashboard.local.json"
)
HUMAN_ACTION_BOARD_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_human_action_board/"
    "commercial_human_action_board.local.json"
)
DEPENDENCY_PLAN_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_blocker_dependency_plan/"
    "dependency_plan.local.json"
)
CLOSURE_BOARD_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_blocker_closure_readiness_board/"
    "closure_readiness_board.local.json"
)
NEXT_ACTION_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_action_summary/"
    "commercial_next_action_summary.local.json"
)

FALSE_FLAGS = [
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
    "task_candidates_executed",
    "development_permission_granted",
    "execution_authorized",
    "evidence_collection_authorized",
    "owner_contacted_by_codex",
    "owner_assigned_by_codex",
    "sprint_execution_authorized",
    "sprint_evidence_collection_authorized",
    "blocker_closure_authorized",
    "production_claim_added",
    "launch_claim_added",
    "customer_validation_claim_added",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"SAEE_COMMERCIAL_EVIDENCE_SPRINT_SEQUENCER: FAIL invalid JSON {rel(path)}: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise SystemExit(
            f"SAEE_COMMERCIAL_EVIDENCE_SPRINT_SEQUENCER: FAIL {rel(path)} must be object"
        )
    return data


def index_by_blocker(rows: list[dict[str, Any]], key: str = "blocker_id") -> dict[str, dict[str, Any]]:
    return {str(row.get(key)): row for row in rows if row.get(key)}


def selection_bucket(row: dict[str, Any], current_blocker_id: str) -> str:
    if row["blocker_id"] == current_blocker_id:
        return "current_next_human_input"
    if row["dependency_state"] == "ready_for_human_review":
        if not row["engineering_implementation_required"] and not row["external_dependency_required"]:
            return "ready_human_only"
        if not row["engineering_implementation_required"]:
            return "ready_external_human_review"
        return "ready_engineering_review"
    return "blocked_by_dependency"


def bucket_rank(bucket: str) -> int:
    return {
        "current_next_human_input": 0,
        "ready_human_only": 1,
        "ready_external_human_review": 2,
        "ready_engineering_review": 3,
        "blocked_by_dependency": 4,
    }.get(bucket, 9)


def build_candidate_rows(
    dashboard: dict[str, Any],
    human_action: dict[str, Any],
    dependency_plan: dict[str, Any],
    closure_board: dict[str, Any],
    next_action: dict[str, Any],
) -> list[dict[str, Any]]:
    dashboard_rows = index_by_blocker(dashboard.get("blocker_dashboard", []))
    dependency_rows = index_by_blocker(dependency_plan.get("blockers", []))
    closure_rows = index_by_blocker(
        closure_board.get("blocker_closure_readiness_review", [])
    )
    current_blocker_id = "support_contact"
    actions = next_action.get("next_actions", [])
    if actions:
        current_blocker_id = str(actions[0].get("blocker_id") or current_blocker_id)

    rows: list[dict[str, Any]] = []
    for action in human_action.get("action_rows", []):
        blocker_id = str(action.get("blocker_id"))
        dashboard_row = dashboard_rows.get(blocker_id, {})
        dependency_row = dependency_rows.get(blocker_id, {})
        closure_row = closure_rows.get(blocker_id, {})
        row = {
            "sequence_rank": 0,
            "blocker_id": blocker_id,
            "category": action.get("category"),
            "phase_id": action.get("phase_id"),
            "phase_order": int(action.get("phase_order", 99)),
            "owner_review_lane": action.get("owner_review_lane"),
            "dependency_state": action.get("dependency_state"),
            "depends_on_blockers": action.get("depends_on_blockers", []),
            "unblocks_blockers": action.get("unblocks_blockers", []),
            "engineering_implementation_required": action.get(
                "engineering_implementation_required"
            )
            is True,
            "external_dependency_required": action.get("external_dependency_required")
            is True,
            "required_evidence_item_count": int(
                dashboard_row.get("required_evidence_item_count", 0)
            ),
            "local_public_shell_present_count": int(
                dashboard_row.get("local_public_shell_present_count", 0)
            ),
            "missing_production_evidence_count": int(
                dashboard_row.get("missing_production_evidence_count", 0)
            ),
            "closure_ready_for_human_final_review": closure_row.get(
                "closure_ready_for_human_final_review"
            )
            is True,
            "closure_status": closure_row.get("closure_status", "not_ready"),
            "can_start_without_external_dependency": dependency_row.get(
                "can_start_without_external_dependency"
            )
            is True,
            "required_evidence": action.get("required_evidence"),
            "default_decision": "hold",
            "requires_human_approval": True,
            "requires_separate_execution_request": True,
            "execution_allowed_by_sequencer": False,
            "evidence_collection_authorized": False,
            "blocker_closure_allowed_by_sequencer": False,
            "next_required_action": (
                "Human reviewer may choose this row for a separate approved evidence "
                "or owner-assignment request; the sequencer itself authorizes no work."
            ),
        }
        bucket = selection_bucket(row, current_blocker_id)
        row["selection_bucket"] = bucket
        row["_sort_key"] = (
            bucket_rank(bucket),
            row["phase_order"],
            row["missing_production_evidence_count"],
            -len(row["unblocks_blockers"]),
            row["blocker_id"],
        )
        rows.append(row)

    rows.sort(key=lambda item: item["_sort_key"])
    for index, row in enumerate(rows, start=1):
        row["sequence_rank"] = index
        row.pop("_sort_key", None)
    return rows


def count_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key))
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def build_payload() -> dict[str, Any]:
    dashboard = read_json(DASHBOARD_PATH)
    human_action = read_json(HUMAN_ACTION_BOARD_PATH)
    dependency_plan = read_json(DEPENDENCY_PLAN_PATH)
    closure_board = read_json(CLOSURE_BOARD_PATH)
    next_action = read_json(NEXT_ACTION_PATH)
    rows = build_candidate_rows(dashboard, human_action, dependency_plan, closure_board, next_action)
    top_candidates = rows[:5]
    payload: dict[str, Any] = {
        "commercial_evidence_sprint_sequencer_v0_1": True,
        "sequencer_type": "saee_commercial_evidence_sprint_sequencer",
        "sequencer_version": "v0.1",
        "sequencer_scope": "local_read_only_commercial_evidence_sprint_ordering",
        "status": "hold_human_sprint_selection_required",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_evidence_sprint_sequencer.py",
        "source_dashboard": rel(DASHBOARD_PATH),
        "source_human_action_board": rel(HUMAN_ACTION_BOARD_PATH),
        "source_dependency_plan": rel(DEPENDENCY_PLAN_PATH),
        "source_closure_board": rel(CLOSURE_BOARD_PATH),
        "source_next_action_summary": rel(NEXT_ACTION_PATH),
        "commercial_status": dashboard.get("commercial_status", "hold"),
        "production_launch_status": dashboard.get("production_launch_status", "hold"),
        "production_blocker_count": int(dashboard.get("production_blocker_count", 24)),
        "open_blocker_count": int(dashboard.get("open_blocker_count", len(rows))),
        "total_required_evidence_item_count": int(
            dashboard.get("total_required_evidence_item_count", 149)
        ),
        "total_missing_production_evidence_count": int(
            dashboard.get("total_missing_production_evidence_count", 112)
        ),
        "sequenced_blocker_count": len(rows),
        "top_candidate_count": len(top_candidates),
        "selection_bucket_counts": count_by(rows, "selection_bucket"),
        "owner_review_lane_counts": count_by(rows, "owner_review_lane"),
        "engineering_required_candidate_count": sum(
            1 for row in rows if row["engineering_implementation_required"]
        ),
        "external_dependency_candidate_count": sum(
            1 for row in rows if row["external_dependency_required"]
        ),
        "closure_candidate_count": int(closure_board.get("closure_candidate_count", 0)),
        "blockers_closed_by_sequencer": 0,
        "current_next_human_input_blocker_id": top_candidates[0]["blocker_id"]
        if top_candidates
        else None,
        "recommended_default_decision": "hold",
        "next_human_action": (
            "Review the sequenced rows, pick one blocker for a separate human-approved "
            "owner or evidence request, and keep all execution and launch claims false."
        ),
        "top_sprint_candidates": top_candidates,
        "sequenced_blockers": rows,
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_csv(rows: list[dict[str, Any]]) -> None:
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "sequence_rank",
            "blocker_id",
            "selection_bucket",
            "category",
            "owner_review_lane",
            "dependency_state",
            "missing_production_evidence_count",
            "engineering_implementation_required",
            "external_dependency_required",
            "default_decision",
            "execution_allowed_by_sequencer",
            "blocker_closure_allowed_by_sequencer",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fieldnames})


def write_outputs(payload: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = payload["sequenced_blockers"]
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(rows)

    candidate_lines = "\n".join(
        "- {rank}. `{blocker}`: bucket={bucket}, lane={lane}, missing={missing}, default_decision=hold".format(
            rank=row["sequence_rank"],
            blocker=row["blocker_id"],
            bucket=row["selection_bucket"],
            lane=row["owner_review_lane"],
            missing=row["missing_production_evidence_count"],
        )
        for row in payload["top_sprint_candidates"]
    )
    OUTPUT_MD.write_text(
        f"""# SAEE Commercial Evidence Sprint Sequencer v0.1

status: {payload['status']}

This local sequencer orders current commercial blockers for human sprint
selection. It does not assign owners, collect evidence, execute work, close
blockers, launch product, or claim production readiness.

## Summary

- sequenced_blocker_count: {payload['sequenced_blocker_count']}
- top_candidate_count: {payload['top_candidate_count']}
- current_next_human_input_blocker_id: {payload['current_next_human_input_blocker_id']}
- production_blocker_count: {payload['production_blocker_count']}
- open_blocker_count: {payload['open_blocker_count']}
- total_required_evidence_item_count: {payload['total_required_evidence_item_count']}
- total_missing_production_evidence_count: {payload['total_missing_production_evidence_count']}
- closure_candidate_count: {payload['closure_candidate_count']}
- blockers_closed_by_sequencer: 0
- execution_authorized: false
- evidence_collection_authorized: false
- production_ready: false
- customer_validated: false
- product_launched: false

## Top Sprint Candidates

{candidate_lines}

## Bucket Counts

```json
{json.dumps(payload['selection_bucket_counts'], indent=2, sort_keys=True)}
```

## Boundary

- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- sprint_execution_authorized: false
- sprint_evidence_collection_authorized: false
- blocker_closure_authorized: false
- product_launched: false
- production_ready: false
""",
        encoding="utf-8",
    )

    OUTPUT_BOUNDARY.write_text(
        """# SAEE Commercial Evidence Sprint Sequencer Boundary Audit

- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- product_launched: false
- production_ready: false
- customer_validated: false
- customer_contacted: false
- external_calls_made: false
- external_model_api_called: false
- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_sequencer: 0
- sprint_execution_authorized: false
- sprint_evidence_collection_authorized: false
- blocker_closure_authorized: false
""",
        encoding="utf-8",
    )

    README_PATH.write_text(
        """# SAEE Commercial Evidence Sprint Sequencer

This directory contains a local, read-only sequencer for choosing the next
human commercial evidence sprint candidate.

It reads existing commercial readiness boards and writes a deterministic order
for human review. It does not assign owners, collect evidence, execute work,
close blockers, launch product, or claim production readiness.

Files:

- `commercial_evidence_sprint_sequencer.local.json`
- `commercial_evidence_sprint_sequencer.md`
- `commercial_evidence_sprint_sequencer.csv`
- `commercial_evidence_sprint_sequencer_boundary_audit.md`
""",
        encoding="utf-8",
    )

    DOC_PATH.write_text(
        f"""# SAEE Commercial Evidence Sprint Sequencer v0.1

commercial_evidence_sprint_sequencer_v0_1: true
status: {payload['status']}
sequencer_scope: local_read_only_commercial_evidence_sprint_ordering
sequenced_blocker_count: {payload['sequenced_blocker_count']}
top_candidate_count: {payload['top_candidate_count']}
current_next_human_input_blocker_id: {payload['current_next_human_input_blocker_id']}
closure_candidate_count: {payload['closure_candidate_count']}
blockers_closed_by_sequencer: 0
evidence_collection_authorized: false
execution_authorized: false
sprint_execution_authorized: false
sprint_evidence_collection_authorized: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This sequencer helps a human reviewer choose the next commercial evidence
sprint candidate from the current blocker surfaces. It is a planning layer
only.

## Boundary

The sequencer does not assign owners, contact anyone, collect evidence,
execute work, close blockers, modify runtime/backend/kernel/API schema/private
core, launch product, or claim production readiness.
""",
        encoding="utf-8",
    )

    GATE_PATH.write_text(
        """# SAEE Commercial Evidence Sprint Sequencer Recommendation Gate

answer: recommend

recommend_for_sprint_selection_guidance: true
recommend_for_evidence_collection: false
recommend_for_automatic_execution: false
recommend_for_blocker_closure: false
recommend_for_product_launch: false
recommend_for_production_readiness_claim: false

## Reason

The sequencer is useful because it compresses current blocker, dependency,
gap, closure, and next-action surfaces into one deterministic human-review
ordering. It preserves all launch and execution boundaries.

## Boundary

- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_sequencer: 0
- sprint_execution_authorized: false
- sprint_evidence_collection_authorized: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
""",
        encoding="utf-8",
    )


def main() -> int:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_COMMERCIAL_EVIDENCE_SPRINT_SEQUENCER: PASS "
        f"status={payload['status']} "
        f"sequenced_blockers={payload['sequenced_blocker_count']} "
        f"top_candidate={payload['current_next_human_input_blocker_id']} "
        "blockers_closed_by_sequencer=0 production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
