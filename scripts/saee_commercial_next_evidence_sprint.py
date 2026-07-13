#!/usr/bin/env python3
"""Build the SAEE commercial next evidence sprint.

The sprint narrows the current human action board into a small, balanced set of
ready-for-review production blockers. It does not collect evidence, execute
tasks, contact customers or vendors, close blockers, launch product, or claim
production readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
OUTPUT_JSON = OUTPUT_DIR / "commercial_next_evidence_sprint.local.json"
OUTPUT_MD = OUTPUT_DIR / "commercial_next_evidence_sprint.md"
OUTPUT_CSV = OUTPUT_DIR / "commercial_next_evidence_sprint.csv"
OUTPUT_BOUNDARY = OUTPUT_DIR / "commercial_next_evidence_sprint_boundary_audit.md"
README_PATH = OUTPUT_DIR / "README.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_NEXT_EVIDENCE_SPRINT_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_COMMERCIAL_NEXT_EVIDENCE_SPRINT_RECOMMENDATION_GATE.md"
BOARD_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_human_action_board/commercial_human_action_board.local.json"
)

MAX_SPRINT_BLOCKERS = 5
BLOCKER_PRIORITY = [
    "support_contact",
    "pricing_page",
    "formal_security_review",
    "production_restore_policy",
    "production_monitoring",
    "privacy_legal_review",
    "refund_policy",
    "tax_review",
    "production_identity_provider",
]

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
    "customer_data_collected",
    "customer_data_processed",
    "payment_collected",
    "revenue_validated",
    "production_claim_added",
    "launch_claim_added",
    "customer_validation_claim_added",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def priority_index(blocker_id: str) -> int:
    try:
        return BLOCKER_PRIORITY.index(blocker_id)
    except ValueError:
        return len(BLOCKER_PRIORITY) + 100


def recommended_human_action(row: dict[str, Any]) -> str:
    blocker_id = row["blocker_id"]
    if blocker_id == "support_contact":
        return "Draft or confirm the controlled-preview support contact evidence in a separate approved evidence request."
    if blocker_id == "pricing_page":
        return "Review the pricing-page evidence packet and decide whether a human-approved public pricing draft is appropriate."
    if blocker_id == "formal_security_review":
        return "Assign a human owner to prepare the formal security review scope without contacting external reviewers automatically."
    if blocker_id == "production_restore_policy":
        return "Review the production restore policy evidence requirements and decide whether a separate policy execution request is warranted."
    if blocker_id == "production_monitoring":
        return "Review production monitoring evidence requirements without configuring external monitoring or alert delivery."
    return "Review the listed evidence samples and create a separate explicit request before any collection or execution."


def transform_selected_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "blocker_id": row["blocker_id"],
        "phase_id": row["phase_id"],
        "category": row["category"],
        "dependency_state": row["dependency_state"],
        "owner_review_lane": row["owner_review_lane"],
        "required_evidence": row["required_evidence"],
        "evidence_sample_count": row["evidence_sample_count"],
        "first_evidence_items": row["first_evidence_items"],
        "external_dependency_required": row["external_dependency_required"],
        "engineering_implementation_required": row["engineering_implementation_required"],
        "requires_human_approval": True,
        "requires_separate_execution_request": True,
        "default_decision": "hold",
        "recommended_human_action": recommended_human_action(row),
        "evidence_collection_allowed_by_sprint": False,
        "execution_allowed_by_sprint": False,
        "closure_allowed_by_sprint": False,
        "must_not_touch": [
            "runtime",
            "backend",
            "kernel",
            "api_schema",
            "private_core",
            "customer_contact_without_approval",
            "vendor_contact_without_approval",
            "payment_collection",
            "production_launch",
        ],
    }


def select_sprint_rows(board: dict[str, Any]) -> list[dict[str, Any]]:
    ready_rows = [
        row
        for row in board.get("action_rows", [])
        if row.get("dependency_state") == "ready_for_human_review"
    ]
    by_id = {row["blocker_id"]: row for row in ready_rows}

    selected: list[dict[str, Any]] = []
    used_lanes: set[str] = set()
    for blocker_id in BLOCKER_PRIORITY:
        row = by_id.get(blocker_id)
        if not row:
            continue
        lane = row["owner_review_lane"]
        if lane in used_lanes:
            continue
        selected.append(row)
        used_lanes.add(lane)
        if len(selected) == MAX_SPRINT_BLOCKERS:
            break

    if len(selected) < MAX_SPRINT_BLOCKERS:
        selected_ids = {row["blocker_id"] for row in selected}
        remaining = sorted(
            [row for row in ready_rows if row["blocker_id"] not in selected_ids],
            key=lambda row: (priority_index(row["blocker_id"]), row["blocker_id"]),
        )
        for row in remaining:
            selected.append(row)
            if len(selected) == MAX_SPRINT_BLOCKERS:
                break

    return [transform_selected_row(row) for row in selected]


def build_sprint() -> dict[str, Any]:
    board = read_json(BOARD_PATH)
    selected_blockers = select_sprint_rows(board)
    sprint: dict[str, Any] = {
        "sprint_type": "saee_commercial_next_evidence_sprint",
        "sprint_version": "0.1",
        "sprint_status": "hold_human_review_only",
        "sprint_scope": "local_next_evidence_sprint_planning",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_next_evidence_sprint.py",
        "source_action_board": rel(BOARD_PATH),
        "commercial_status": board.get("commercial_status", "hold"),
        "production_launch_status": board.get("production_launch_status", "hold"),
        "production_blocker_count": board.get("production_blocker_count", 24),
        "open_blocker_count": board.get("open_blocker_count", 24),
        "ready_for_human_review_blocker_count": board.get(
            "ready_for_human_review_blocker_count", 0
        ),
        "selected_blocker_count": len(selected_blockers),
        "selected_blockers": selected_blockers,
        "selected_blocker_ids": [row["blocker_id"] for row in selected_blockers],
        "sprint_selection_rules": {
            "max_sprint_blockers": MAX_SPRINT_BLOCKERS,
            "source_rows_required_state": "ready_for_human_review",
            "balance_owner_lanes_first": True,
            "default_decision": "hold",
        },
        "human_review_required": True,
        "manual_collection_required": True,
        "separate_execution_approval_required": True,
        "blockers_closed_by_sprint": 0,
        "blockers_ready_to_close": [],
        "next_allowed_action": (
            "A human may choose one selected blocker and create a separate explicit "
            "evidence-collection or implementation request."
        ),
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
        "customer_data_collected": False,
        "customer_data_processed": False,
        "payment_collected": False,
        "revenue_validated": False,
        "production_claim_added": False,
        "launch_claim_added": False,
        "customer_validation_claim_added": False,
    }
    return sprint


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(sprint: dict[str, Any]) -> None:
    fields = [
        "blocker_id",
        "phase_id",
        "category",
        "dependency_state",
        "owner_review_lane",
        "external_dependency_required",
        "engineering_implementation_required",
        "evidence_sample_count",
        "default_decision",
        "evidence_collection_allowed_by_sprint",
        "execution_allowed_by_sprint",
        "closure_allowed_by_sprint",
        "recommended_human_action",
    ]
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in sprint["selected_blockers"]:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_markdown(sprint: dict[str, Any]) -> None:
    lines = [
        "# SAEE Commercial Next Evidence Sprint",
        "",
        "Status: hold_human_review_only.",
        "",
        "This sprint narrows the current commercial human action board into a",
        "small, balanced set of production blockers for human review. It does not",
        "collect evidence, execute tasks, contact customers or vendors, close",
        "blockers, launch product, or claim production readiness.",
        "",
        "## Summary",
        "",
        f"- production_blocker_count: {sprint['production_blocker_count']}",
        f"- open_blocker_count: {sprint['open_blocker_count']}",
        f"- ready_for_human_review_blocker_count: {sprint['ready_for_human_review_blocker_count']}",
        f"- selected_blocker_count: {sprint['selected_blocker_count']}",
        f"- selected_blocker_ids: {', '.join(sprint['selected_blocker_ids'])}",
        f"- blockers_closed_by_sprint: {sprint['blockers_closed_by_sprint']}",
        "- execution_authorized: false",
        "- evidence_collection_authorized: false",
        "- production_ready: false",
        "- customer_validated: false",
        "",
        "## Selected Blockers",
        "",
        "| Blocker | Lane | Category | External dep | Engineering impl | Human action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in sprint["selected_blockers"]:
        lines.append(
            f"| {row['blocker_id']} | {row['owner_review_lane']} | {row['category']} | "
            f"{str(row['external_dependency_required']).lower()} | "
            f"{str(row['engineering_implementation_required']).lower()} | "
            f"{row['recommended_human_action']} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "No selected blocker is approved for execution by this sprint. Each item",
            "requires a separate human-approved evidence or implementation request.",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_boundary_audit(sprint: dict[str, Any]) -> None:
    lines = [
        "# Commercial Next Evidence Sprint Boundary Audit",
        "",
        "- runtime_modified: false",
        "- backend_modified: false",
        "- kernel_modified: false",
        "- api_schema_modified: false",
        "- private_core_exposed: false",
        "- product_launched: false",
        "- production_ready: false",
        "- customer_validated: false",
        "- customer_contacted: false",
        "- public_sdk_released: false",
        "- external_calls_made: false",
        "- external_model_api_called: false",
        "- external_ai_assistant_tested: false",
        "- task_candidates_executed: false",
        "- development_permission_granted: false",
        "- execution_authorized: false",
        "- evidence_collection_authorized: false",
        "- blockers_closed_by_sprint: 0",
        "",
        "Final boundary decision: local next-evidence planning only.",
    ]
    OUTPUT_BOUNDARY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_readme() -> None:
    README_PATH.write_text(
        "\n".join(
            [
                "# Commercial Next Evidence Sprint",
                "",
                "Status: local planning packet, hold, no execution.",
                "",
                "This directory contains the generated next evidence sprint over a",
                "small subset of commercial production blockers. It is intended to",
                "help a human pick the next evidence lane to open in a separate",
                "approved request.",
                "",
                "It does not authorize execution, evidence collection, vendor contact,",
                "customer contact, product launch, production-ready claims,",
                "customer-validation claims, or blocker closure.",
                "",
                "Files:",
                "",
                "- `commercial_next_evidence_sprint.local.json`",
                "- `commercial_next_evidence_sprint.md`",
                "- `commercial_next_evidence_sprint.csv`",
                "- `commercial_next_evidence_sprint_boundary_audit.md`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_doc(sprint: dict[str, Any]) -> None:
    DOC_PATH.write_text(
        "\n".join(
            [
                "# SAEE Commercial Next Evidence Sprint v0.1",
                "",
                "commercial_next_evidence_sprint_v0_1: true",
                "sprint_scope: local_next_evidence_sprint_planning",
                "status: hold_human_review_only",
                f"production_blocker_count: {sprint['production_blocker_count']}",
                f"open_blocker_count: {sprint['open_blocker_count']}",
                f"ready_for_human_review_blocker_count: {sprint['ready_for_human_review_blocker_count']}",
                f"selected_blocker_count: {sprint['selected_blocker_count']}",
                f"selected_blocker_ids: {', '.join(sprint['selected_blocker_ids'])}",
                "blockers_closed_by_sprint: 0",
                "execution_authorized: false",
                "evidence_collection_authorized: false",
                "production_ready: false",
                "customer_validated: false",
                "product_launched: false",
                "private_core_exposed: false",
                "",
                "## Purpose",
                "",
                "This sprint selects a small, balanced set of ready-for-human-review",
                "commercial blockers from the current action board so the next human",
                "evidence step is concrete instead of spread across all 24 blockers.",
                "",
                "## Boundary",
                "",
                "The sprint is planning-only. It does not execute tasks, collect",
                "evidence, contact customers or vendors, close blockers, modify",
                "runtime/backend/kernel/API schema/private core, launch product, or",
                "claim production readiness.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_gate(sprint: dict[str, Any]) -> None:
    GATE_PATH.write_text(
        "\n".join(
            [
                "# SAEE Commercial Next Evidence Sprint Recommendation Gate",
                "",
                "answer: conditional",
                "",
                "recommend_for_human_evidence_prioritization: true",
                "recommend_for_automatic_execution: false",
                "recommend_for_evidence_collection_authorization: false",
                "recommend_for_blocker_closure: false",
                "recommend_for_product_launch: false",
                "recommend_for_production_readiness_claim: false",
                "",
                "## Reason",
                "",
                "The sprint is useful because it reduces the next commercial action from",
                "24 open blockers to a short human-review list. It does not grant",
                "execution permission and does not close blockers.",
                "",
                "## Current Evidence",
                "",
                f"- production_blocker_count: {sprint['production_blocker_count']}",
                f"- selected_blocker_count: {sprint['selected_blocker_count']}",
                f"- selected_blocker_ids: {', '.join(sprint['selected_blocker_ids'])}",
                "- blockers_closed_by_sprint: 0",
                "- production_ready: false",
                "- customer_validated: false",
                "- private_core_exposed: false",
                "",
                "## Next Action",
                "",
                "A human may choose one selected blocker and open a separate explicit",
                "evidence-collection or implementation request.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_outputs(sprint: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUT_JSON, sprint)
    write_csv(sprint)
    write_markdown(sprint)
    write_boundary_audit(sprint)
    write_readme()
    write_doc(sprint)
    write_gate(sprint)


def main() -> int:
    sprint = build_sprint()
    for flag in FALSE_FLAGS:
        if sprint.get(flag) not in (False, 0):
            raise SystemExit(f"SAEE_COMMERCIAL_NEXT_EVIDENCE_SPRINT: FAIL {flag}")
    if sprint["selected_blocker_count"] == 0:
        raise SystemExit("SAEE_COMMERCIAL_NEXT_EVIDENCE_SPRINT: FAIL no selected blockers")
    write_outputs(sprint)
    print(
        "SAEE_COMMERCIAL_NEXT_EVIDENCE_SPRINT: PASS "
        f"selected_blockers={sprint['selected_blocker_count']} "
        f"blockers_closed_by_sprint={sprint['blockers_closed_by_sprint']} "
        f"production_ready={str(sprint['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
