#!/usr/bin/env python3
"""Reconcile current pricing-page readiness surfaces without publishing pricing.

This local surface exists because older pricing-page entrypoints can still say
"human input required" while later human-filled evidence surfaces already
reached closure-review state. The reconciler chooses the next safe human action
from existing local artifacts only. It does not publish pricing, enable
checkout, execute a matrix update, close blockers, or claim production
readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
BILLING_DIR = COMMERCIAL_DIR / "billing_revenue_evidence"
MATRIX_DIR = COMMERCIAL_DIR / "matrix_update_requests"
OUT_DIR = BILLING_DIR / "pricing_page_state_reconciliation"
OUT_JSON = OUT_DIR / "pricing_page_state_reconciliation.local.json"
OUT_MD = OUT_DIR / "pricing_page_state_reconciliation.md"
BOUNDARY = OUT_DIR / "pricing_page_state_reconciliation_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "PRICING_PAGE_STATE_RECONCILIATION_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_PRICING_PAGE_STATE_RECONCILIATION_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
]

SOURCES = {
    "minimum_human_input_workspace": BILLING_DIR
    / "pricing_page_minimum_human_input_workspace/pricing_page_minimum_human_input_workspace.local.json",
    "approval_input_validation": BILLING_DIR / "pricing_page_approval_input_validation.human_filled.local.json",
    "evidence_builder_output": BILLING_DIR / "pricing_page_evidence_builder_output.human_filled.local.json",
    "production_evidence": BILLING_DIR / "production_billing_revenue_evidence.from_pricing_page.human_filled.local.json",
    "review_packet": BILLING_DIR / "pricing_page_review_packet.local.json",
    "closure_review_packet": BILLING_DIR / "pricing_page_closure_review_packet.local.json",
    "matrix_update_request_packet": MATRIX_DIR / "commercial_matrix_update_request_packet.local.json",
    "matrix_update_execution_request_packet": MATRIX_DIR
    / "commercial_matrix_update_execution_request_packet.local.json",
    "matrix_update_approval_copy_card": MATRIX_DIR
    / "commercial_matrix_update_execution_approval_copy_card.local.json",
    "matrix_update_approval_validation": MATRIX_DIR
    / "commercial_matrix_update_execution_approval_validation.local.json",
    "matrix_update_dry_run": MATRIX_DIR / "commercial_matrix_update_execution_dry_run.local.json",
    "matrix_update_applier": MATRIX_DIR / "commercial_matrix_update_execution_applier.local.json",
}

EXACT_APPROVAL_PHRASE = (
    "批准矩阵更新执行：仅应用 review-ready markers，不关闭 blocker，不发布价格页，不启用 checkout，不声明生产可用。"
)

FALSE_FLAGS = {
    "pricing_page_available": False,
    "pricing_page_published": False,
    "customer_facing_pricing_page_created": False,
    "pricing_page_approved": False,
    "checkout_enabled": False,
    "payment_provider_configured": False,
    "production_billing_enabled": False,
    "customer_payment_collected": False,
    "revenue_validated": False,
    "evidence_collection_authorized": False,
    "execution_authorized": False,
    "blocker_closure_authorized": False,
    "blockers_closed_by_reconciliation": 0,
    "matrix_update_executed": False,
    "canonical_gap_matrix_modified": False,
    "canonical_closure_board_modified": False,
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
    if not path.exists():
        return {}
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


def build_payload() -> dict[str, Any]:
    source_data = {name: read_json(path) for name, path in SOURCES.items()}
    minimum = source_data["minimum_human_input_workspace"]
    approval = source_data["approval_input_validation"]
    builder = source_data["evidence_builder_output"]
    closure = source_data["closure_review_packet"]
    matrix_request = source_data["matrix_update_request_packet"]
    execution_request = source_data["matrix_update_execution_request_packet"]
    approval_copy_card = source_data["matrix_update_approval_copy_card"]
    approval_validation = source_data["matrix_update_approval_validation"]
    dry_run = source_data["matrix_update_dry_run"]
    applier = source_data["matrix_update_applier"]

    input_path_ready = approval.get("validation_status") == "pass" and approval.get("builder_ready") is True
    builder_ready = (
        builder.get("status") == "pass"
        and builder.get("input_complete") is True
        and builder.get("pricing_page_evidence_complete_for_review") is True
    )
    closure_review_ready = (
        closure.get("status") == "ready_for_human_matrix_update_review_no_publication"
        and closure.get("pricing_page_evidence_complete_for_review") is True
        and closure.get("blockers_closed_by_packet") == 0
    )
    matrix_request_ready = (
        matrix_request.get("status") == "ready_for_human_matrix_update_execution_request_no_closure"
        and "pricing_page" in matrix_request.get("target_blockers", [])
    )
    execution_request_ready = (
        execution_request.get("status") == "ready_for_explicit_human_execution_approval_no_closure"
        and "pricing_page" in execution_request.get("target_blockers", [])
    )
    approval_copy_ready = approval_copy_card.get("status") == "ready_for_exact_phrase_human_approval_no_execution"
    approval_validated = approval_validation.get("ready_for_matrix_update_execution") is True
    dry_run_ready = dry_run.get("ready_for_matrix_update_execution") is True
    applier_executed = applier.get("matrix_update_executed") is True

    if applier_executed:
        status = "matrix_update_markers_applied_no_blocker_closure"
        resolved_path = "matrix_update_applier"
        next_action = "Review matrix update output. Pricing publication and blocker closure remain separate gates."
    elif approval_validated or dry_run_ready:
        status = "ready_for_matrix_update_applier_no_publication_no_auto_closure"
        resolved_path = "matrix_update_approval_validation"
        next_action = "Run the matrix update applier only if the separate human approval still applies."
    elif closure_review_ready and matrix_request_ready and execution_request_ready and approval_copy_ready:
        status = "ready_for_exact_matrix_update_execution_approval_phrase_no_publication_no_auto_closure"
        resolved_path = "matrix_update_approval_copy_card"
        next_action = (
            "If the human wants to apply review-ready markers only, copy the exact phrase "
            "from commercial_matrix_update_execution_approval_copy_card.md. Do not publish "
            "pricing, enable checkout, close blockers, or claim production readiness."
        )
    elif closure_review_ready and matrix_request_ready:
        status = "ready_for_explicit_pricing_page_matrix_update_execution_request_no_publication"
        resolved_path = "matrix_update_request_packet"
        next_action = "Review the matrix update request packet before any execution approval."
    elif closure_review_ready:
        status = "ready_for_human_pricing_page_closure_review_no_publication"
        resolved_path = "closure_review_packet"
        next_action = "Review pricing_page_closure_review_packet.md; keep publication and checkout separate."
    elif builder_ready:
        status = "ready_for_pricing_page_closure_review_packet"
        resolved_path = "evidence_builder_output"
        next_action = "Generate or review the pricing-page closure review packet before any matrix update request."
    elif input_path_ready:
        status = "ready_for_pricing_page_evidence_builder_review_only"
        resolved_path = "approval_input_validation"
        next_action = "Use the human-filled validator output for review only; builder execution remains separate."
    else:
        status = "hold_pricing_page_human_input_or_evidence_required"
        resolved_path = "minimum_human_input_workspace"
        next_action = "Complete pricing-page human input before evidence builder or closure review."

    payload: dict[str, Any] = {
        "pricing_page_state_reconciliation_v0_1": True,
        "reconciliation_type": "local_pricing_page_state_reconciliation_no_publication_no_closure",
        "target_blocker_id": "pricing_page",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "resolved_current_path": resolved_path,
        "previous_minimum_workspace_status": minimum.get("status"),
        "approval_validation_status": approval.get("validation_status"),
        "approval_input_complete": approval.get("input_complete") is True,
        "approval_builder_ready": input_path_ready,
        "builder_output_status": builder.get("status"),
        "builder_output_ready": builder_ready,
        "closure_review_packet_status": closure.get("status"),
        "closure_review_ready": closure_review_ready,
        "matrix_update_request_ready": matrix_request_ready,
        "matrix_update_execution_request_ready": execution_request_ready,
        "matrix_update_approval_copy_card_ready": approval_copy_ready,
        "matrix_update_approval_validated": approval_validated,
        "matrix_update_dry_run_ready": dry_run_ready,
        "exact_approval_phrase_required": True,
        "exact_approval_phrase": EXACT_APPROVAL_PHRASE,
        "source_paths": {name: rel(path) for name, path in SOURCES.items()},
        "human_review_required": True,
        "next_human_action": next_action,
        "why_this_exists": (
            "Older pricing-page surfaces can remain at first-input state while newer "
            "human-filled evidence is ready for matrix update review. This file selects "
            "one safe next human action without publishing pricing or closing blockers."
        ),
    }
    payload.update(FALSE_FLAGS)
    return payload


def write_outputs(payload: dict[str, Any]) -> None:
    write_json(OUT_JSON, payload)
    OUT_MD.write_text(
        f"""# SAEE Pricing Page State Reconciliation v0.1

Status: `{payload['status']}`

This local board reconciles the current `pricing_page` blocker surfaces. It
does not publish a pricing page, enable checkout, execute a matrix update,
close blockers, contact customers, or claim production readiness.

## Current Finding

- target_blocker_id: `pricing_page`
- previous_minimum_workspace_status: `{payload['previous_minimum_workspace_status']}`
- approval_validation_status: `{payload['approval_validation_status']}`
- approval_input_complete: `{str(payload['approval_input_complete']).lower()}`
- builder_output_ready: `{str(payload['builder_output_ready']).lower()}`
- closure_review_ready: `{str(payload['closure_review_ready']).lower()}`
- matrix_update_request_ready: `{str(payload['matrix_update_request_ready']).lower()}`
- matrix_update_execution_request_ready: `{str(payload['matrix_update_execution_request_ready']).lower()}`
- matrix_update_approval_copy_card_ready: `{str(payload['matrix_update_approval_copy_card_ready']).lower()}`
- resolved_current_path: `{payload['resolved_current_path']}`

## Next Human Action

{payload['next_human_action']}

Exact phrase, if the human chooses the narrow matrix marker path:

`{EXACT_APPROVAL_PHRASE}`

## Boundary

- pricing_page_published=false
- checkout_enabled=false
- matrix_update_executed=false
- blockers_closed_by_reconciliation=0
- production_ready=false
- customer_validated=false
- product_launched=false
- private_core_exposed=false
""",
        encoding="utf-8",
    )
    BOUNDARY.write_text(
        """# SAEE Pricing Page State Reconciliation Boundary Audit

- No pricing page published by Codex.
- No checkout enabled.
- No payment provider configured.
- No customer payment collected.
- No matrix update executed by this reconciler.
- No canonical gap matrix modified.
- No canonical closure board modified.
- No blocker closure authorized.
- No blocker closed.
- No customer contacted.
- No runtime modified.
- No backend modified.
- No kernel modified.
- No API schema modified.
- No private core exposed.
- No product launch.
- No production-ready claim.
- No customer-validation claim.
""",
        encoding="utf-8",
    )
    TOP_DOC.write_text(
        f"""# SAEE Pricing Page State Reconciliation v0.1

Status: `{payload['status']}`

This is an agent-readable current-state board for the `pricing_page` blocker.
It reconciles existing local evidence only and keeps all publication, checkout,
matrix execution, and blocker closure actions behind separate human gates.

## Canonical Files

- `{rel(OUT_JSON)}`
- `{rel(OUT_MD)}`
- `{rel(BOUNDARY)}`
- `{rel(GATE)}`
- `scripts/saee_pricing_page_state_reconciliation.py`
- `scripts/saee_pricing_page_state_reconciliation_smoke.py`

## Truth State

- pricing_page_published=false
- checkout_enabled=false
- matrix_update_executed=false
- blockers_closed_by_reconciliation=0
- production_ready=false
- customer_validated=false
- private_core_exposed=false
""",
        encoding="utf-8",
    )
    GATE.parent.mkdir(parents=True, exist_ok=True)
    GATE.write_text(
        f"""# SAEE Pricing Page State Reconciliation Gate

answer: hold_human_review_required_no_publication_no_auto_closure

reason: Existing human-filled pricing-page evidence is ready for matrix update
review, but pricing publication, checkout enablement, matrix execution, and
blocker closure still require separate explicit human approval.

status: `{payload['status']}`

boundary:
- pricing_page_published: false
- checkout_enabled: false
- matrix_update_executed: false
- blockers_closed_by_reconciliation: 0
- production_ready: false
- customer_validated: false
- private_core_exposed: false

next_action: {payload['next_human_action']}
""",
        encoding="utf-8",
    )

    for line in [
        f"/{rel(TOP_DOC)}",
        f"/{rel(OUT_JSON)}",
        f"/{rel(OUT_MD)}",
        f"/{rel(BOUNDARY)}",
        f"/{rel(GATE)}",
        "/scripts/saee_pricing_page_state_reconciliation.py",
        "/scripts/saee_pricing_page_state_reconciliation_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["pricing_page_state_reconciliation_v0_1"] = {
        "name": "SAEE Pricing Page State Reconciliation v0.1",
        "status": payload["status"],
        "target_blocker_id": "pricing_page",
        "resolved_current_path": payload["resolved_current_path"],
        "closure_review_ready": payload["closure_review_ready"],
        "matrix_update_request_ready": payload["matrix_update_request_ready"],
        "matrix_update_execution_request_ready": payload["matrix_update_execution_request_ready"],
        "matrix_update_approval_copy_card_ready": payload["matrix_update_approval_copy_card_ready"],
        "exact_approval_phrase_required": True,
        "human_review_required": True,
        "pricing_page_published": False,
        "checkout_enabled": False,
        "matrix_update_executed": False,
        "blockers_closed_by_reconciliation": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "make_target": "make check-pricing-page-state-reconciliation",
    }
    write_json(AGENT_INDEX, index)

    block = f"""## Pricing Page State Reconciliation v0.1

- `pricing_page_state_reconciliation_v0_1`
- Status: `{payload['status']}`
- Target blocker: `pricing_page`
- Resolved current path: `{payload['resolved_current_path']}`
- closure_review_ready={str(payload['closure_review_ready']).lower()}
- matrix_update_approval_copy_card_ready={str(payload['matrix_update_approval_copy_card_ready']).lower()}
- pricing_page_published=false
- checkout_enabled=false
- blockers_closed_by_reconciliation=0
- production_ready=false
- customer_validated=false
"""
    for surface in STATUS_SURFACES:
        replace_block(surface, "SAEE_PRICING_PAGE_STATE_RECONCILIATION_V0_1", block)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_PRICING_PAGE_STATE_RECONCILIATION: PASS "
        f"status={payload['status']} blockers_closed_by_reconciliation=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
