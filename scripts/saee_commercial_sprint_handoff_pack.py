#!/usr/bin/env python3
"""Create the human handoff pack for the current commercial evidence sprint.

The pack consolidates the five selected blockers from the current local
commercial evidence sprint and points a human reviewer to the existing input
surfaces. It is a local coordination layer only: it does not fill inputs, run
validators on real input, collect evidence, execute builders, contact anyone,
close blockers, launch product, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
OUT_JSON = SPRINT_DIR / "commercial_sprint_handoff_pack.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_handoff_pack.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_handoff_pack.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_handoff_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_SPRINT_HANDOFF_PACK_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_SPRINT_HANDOFF_PACK_RECOMMENDATION_GATE.md"

SPRINT_JSON = SPRINT_DIR / "commercial_next_evidence_sprint.local.json"

PROMPT_MAP: dict[str, dict[str, str]] = {
    "support_contact": {
        "handoff_type": "bridge_checkpoint",
        "prompt_json": "phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge/support_contact_bridge_human_handoff_checkpoint.local.json",
        "prompt_markdown": "phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge/support_contact_bridge_human_handoff_checkpoint.md",
        "copy_target": "phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge/support_contact_human_input_bridge_input.human_filled.local.json",
        "human_prompt_status_key": "status",
    },
    "pricing_page": {
        "handoff_type": "approval_input_prompt",
        "prompt_json": "phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_approval_input_prompt.local.json",
        "prompt_markdown": "phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_approval_input_prompt.md",
        "copy_target": "phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_evidence_input.human_filled.local.json",
        "human_prompt_status_key": "status",
    },
    "formal_security_review": {
        "handoff_type": "approval_input_prompt",
        "prompt_json": "phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_approval_input_prompt.local.json",
        "prompt_markdown": "phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_approval_input_prompt.md",
        "copy_target": "phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_evidence_input.human_filled.local.json",
        "human_prompt_status_key": "status",
    },
    "production_restore_policy": {
        "handoff_type": "approval_input_prompt",
        "prompt_json": "phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_approval_input_prompt.local.json",
        "prompt_markdown": "phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_approval_input_prompt.md",
        "copy_target": "phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_approval_input.human_filled.local.json",
        "human_prompt_status_key": "status",
    },
    "production_monitoring": {
        "handoff_type": "approval_input_prompt",
        "prompt_json": "phase_b_product/commercial_readiness/operations_evidence/production_monitoring_approval_input_prompt.local.json",
        "prompt_markdown": "phase_b_product/commercial_readiness/operations_evidence/production_monitoring_approval_input_prompt.md",
        "copy_target": "phase_b_product/commercial_readiness/operations_evidence/production_monitoring_evidence_input.human_filled.local.json",
        "human_prompt_status_key": "status",
    },
}

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
    "development_permission_granted",
    "execution_authorized",
    "evidence_collection_authorized",
    "evidence_builder_executed",
    "owner_assigned_by_codex",
    "owner_contacted_by_codex",
    "support_contact_configured",
    "support_contact_published",
    "support_contact_test_performed",
    "vendor_contacted",
    "payment_collected",
    "revenue_validated",
    "blocker_closure_authorized",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"SAEE_COMMERCIAL_SPRINT_HANDOFF_PACK: FAIL invalid JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"SAEE_COMMERCIAL_SPRINT_HANDOFF_PACK: FAIL {path} must contain a JSON object")
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def prompt_status(blocker_id: str) -> tuple[str, bool]:
    info = PROMPT_MAP[blocker_id]
    prompt_path = ROOT / info["prompt_json"]
    if not prompt_path.exists():
        return "missing_prompt", False
    data = read_json(prompt_path)
    return str(data.get(info["human_prompt_status_key"], "unknown")), True


def build_rows(sprint: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rank, blocker in enumerate(sprint.get("selected_blockers", []), 1):
        blocker_id = blocker.get("blocker_id")
        if blocker_id not in PROMPT_MAP:
            prompt_state, prompt_available = "missing_mapping", False
            mapping = {
                "handoff_type": "missing_mapping",
                "prompt_json": "",
                "prompt_markdown": "",
                "copy_target": "",
            }
        else:
            prompt_state, prompt_available = prompt_status(blocker_id)
            mapping = PROMPT_MAP[blocker_id]
        rows.append(
            {
                "rank": rank,
                "blocker_id": blocker_id,
                "category": blocker.get("category"),
                "owner_review_lane": blocker.get("owner_review_lane"),
                "dependency_state": blocker.get("dependency_state"),
                "handoff_type": mapping["handoff_type"],
                "handoff_status": "ready_for_human_input" if prompt_available else "hold_missing_prompt",
                "prompt_status": prompt_state,
                "prompt_json": mapping["prompt_json"],
                "prompt_markdown": mapping["prompt_markdown"],
                "human_filled_input_target": mapping["copy_target"],
                "external_dependency_required": blocker.get("external_dependency_required"),
                "engineering_implementation_required": blocker.get("engineering_implementation_required"),
                "requires_human_approval": True,
                "evidence_collection_authorized": False,
                "execution_authorized": False,
                "closure_authorized": False,
                "default_decision": "hold",
                "recommended_human_action": blocker.get("recommended_human_action"),
            }
        )
    return rows


def build_payload() -> dict[str, Any]:
    sprint = read_json(SPRINT_JSON)
    rows = build_rows(sprint)
    ready_count = sum(1 for row in rows if row["handoff_status"] == "ready_for_human_input")
    payload: dict[str, Any] = {
        "commercial_sprint_handoff_pack_v0_1": True,
        "pack_type": "local_human_handoff_index_for_current_commercial_sprint",
        "pack_scope": "selected_blocker_human_input_surfaces_only",
        "status": "ready_for_human_sprint_handoff" if ready_count == len(rows) and rows else "hold_missing_handoff_surface",
        "source_sprint": rel(SPRINT_JSON),
        "selected_blocker_count": len(rows),
        "handoff_ready_count": ready_count,
        "human_input_required": True,
        "human_review_required": True,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blockers_closed_by_pack": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "rows": rows,
        "next_human_action": (
            "Use this pack to choose and fill one selected blocker handoff surface. "
            "Run only the local prompt or validator commands listed in each surface. "
            "Evidence collection or builder execution still requires a separate explicit request."
        ),
        "generated_by": "scripts/saee_commercial_sprint_handoff_pack.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    payload["blockers_closed_by_pack"] = 0
    return payload


def shared_lines(payload: dict[str, Any]) -> str:
    return f"""commercial_sprint_handoff_pack_v0_1: true
status: {payload['status']}
pack_scope: selected_blocker_human_input_surfaces_only
selected_blocker_count: {payload['selected_blocker_count']}
handoff_ready_count: {payload['handoff_ready_count']}
human_input_required: true
human_review_required: true
evidence_collection_authorized: false
execution_authorized: false
evidence_builder_executed: false
blockers_closed_by_pack: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false"""


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "rank",
        "blocker_id",
        "category",
        "owner_review_lane",
        "dependency_state",
        "handoff_type",
        "handoff_status",
        "prompt_status",
        "prompt_markdown",
        "human_filled_input_target",
        "evidence_collection_authorized",
        "execution_authorized",
        "closure_authorized",
        "default_decision",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_docs(payload: dict[str, Any]) -> None:
    shared = shared_lines(payload)
    table_lines = [
        "| Rank | Blocker | Lane | Handoff | Status | Prompt | Human target |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        table_lines.append(
            "| {rank} | `{blocker_id}` | {owner_review_lane} | {handoff_type} | "
            "{handoff_status} | `{prompt_markdown}` | `{human_filled_input_target}` |".format(
                **row
            )
        )
    table = "\n".join(table_lines)
    boundary_text = f"""# Commercial Sprint Handoff Pack Boundary Audit

{shared}

## Confirmed Boundaries

- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- product_launched: false
- production_ready: false
- customer_validated: false
- customer_contacted: false
- evidence_collection_authorized: false
- execution_authorized: false
- evidence_builder_executed: false
- blockers_closed_by_pack: 0
"""
    OUT_MD.write_text(
        f"""# Commercial Sprint Handoff Pack

{shared}

## Purpose

This pack consolidates the human input surfaces for the current five selected
commercial-readiness blockers. It is an index and handoff surface only.

## Handoff Rows

{table}

## Boundary

This pack does not fill inputs, run validators on real human input, run evidence
builders, collect evidence, contact customers or vendors, close blockers, launch
product, or claim production readiness.
""",
        encoding="utf-8",
    )
    OUT_BOUNDARY.write_text(boundary_text, encoding="utf-8")
    TOP_DOC.write_text(
        f"""# SAEE Commercial Sprint Handoff Pack v0.1

{shared}

## Agent Recommendation Gate

recommendation_gate:
  feature_or_direction: commercial_sprint_handoff_pack
  target_customer_need: coordinate human evidence input for selected commercial blockers
  agent_answer: recommend
  reason: This local pack improves commercial-readiness handoff clarity without executing evidence collection or changing product behavior.
  recommend_for_human_handoff: true
  recommend_for_real_evidence: false
  recommend_for_evidence_collection: false
  recommend_for_automatic_execution: false
  recommend_for_blocker_closure: false
  recommend_for_product_launch: false
  recommend_for_production_readiness_claim: false

## Boundary

This pack is a local human handoff index. It does not execute tasks, collect
evidence, contact anyone, close blockers, launch product, or claim production
readiness.
""",
        encoding="utf-8",
    )
    GATE.write_text(
        f"""# SAEE Commercial Sprint Handoff Pack Recommendation Gate

answer: recommend
recommend_for_human_handoff: true
recommend_for_real_evidence: false
recommend_for_evidence_collection: false
recommend_for_automatic_execution: false
recommend_for_blocker_closure: false
recommend_for_product_launch: false
recommend_for_production_readiness_claim: false

## Reason

The handoff pack makes the current five selected commercial blockers easier for
a human reviewer to route without granting Codex execution authority.

## Boundary

{shared}
""",
        encoding="utf-8",
    )


def main() -> int:
    payload = build_payload()
    write_json(OUT_JSON, payload)
    write_csv(OUT_CSV, payload["rows"])
    write_docs(payload)
    print(
        "SAEE_COMMERCIAL_SPRINT_HANDOFF_PACK: PASS "
        f"status={payload['status']} selected_blocker_count={payload['selected_blocker_count']} "
        f"handoff_ready_count={payload['handoff_ready_count']} "
        "evidence_collection_authorized=false blockers_closed_by_pack=0 production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
