#!/usr/bin/env python3
"""Reconcile production-restore-policy evidence without closing blockers.

This local surface separates source-backed restore-policy evidence readiness
from production readiness. It does not approve policy, run restores, touch live
data paths, import external data, close blockers, or claim production
readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
EVIDENCE_DIR = COMMERCIAL_DIR / "data_operations_evidence"
OUT_DIR = EVIDENCE_DIR / "production_restore_policy_state_reconciliation"
OUT_JSON = OUT_DIR / "production_restore_policy_state_reconciliation.local.json"
OUT_MD = OUT_DIR / "production_restore_policy_state_reconciliation.md"
BOUNDARY = OUT_DIR / "production_restore_policy_state_reconciliation_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "PRODUCTION_RESTORE_POLICY_STATE_RECONCILIATION_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_PRODUCTION_RESTORE_POLICY_STATE_RECONCILIATION_GATE.md"
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
    "minimum_human_input_workspace": EVIDENCE_DIR
    / "production_restore_policy_minimum_human_input_workspace/production_restore_policy_minimum_human_input_workspace.local.json",
    "approval_input_validation": EVIDENCE_DIR
    / "production_restore_policy_approval_input_validation.human_filled.local.json",
    "evidence_builder_output": EVIDENCE_DIR
    / "production_restore_policy_evidence_builder_output.human_filled.local.json",
    "restore_policy_evidence": EVIDENCE_DIR
    / "production_data_operations_evidence.from_restore_policy.human_filled.local.json",
    "restore_tested_profile": EVIDENCE_DIR / "restore_tested_evidence_profile.local.json",
    "combined_evidence": EVIDENCE_DIR
    / "production_data_operations_evidence.combined_from_restore_tested_and_restore_policy_human_filled.local.json",
    "combined_profile": EVIDENCE_DIR
    / "data_operations_evidence_profile.from_restore_tested_and_restore_policy_human_filled.local.json",
    "review_packet": EVIDENCE_DIR / "production_restore_policy_review_packet.local.json",
    "closure_readiness_board": COMMERCIAL_DIR
    / "commercial_blocker_closure_readiness_board/closure_readiness_board.local.json",
    "gap_matrix": COMMERCIAL_DIR / "production_blocker_gap_matrix/gap_matrix.local.json",
}

FALSE_FLAGS = {
    "restore_run_by_codex": False,
    "restore_policy_published_by_codex": False,
    "restore_policy_approved_by_codex": False,
    "live_data_path_touched": False,
    "customer_data_processed": False,
    "customer_data_collected": False,
    "evidence_collection_authorized": False,
    "execution_authorized": False,
    "blocker_closure_authorized": False,
    "blockers_closed_by_reconciliation": 0,
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


def find_row(data: dict[str, Any], blocker_id: str) -> dict[str, Any]:
    rows = data.get("matrix") or data.get("rows") or data.get("blockers") or []
    if not isinstance(rows, list):
        return {}
    for row in rows:
        if isinstance(row, dict) and row.get("blocker_id") == blocker_id:
            return row
    return {}


def build_payload() -> dict[str, Any]:
    source_data = {name: read_json(path) for name, path in SOURCES.items()}
    minimum = source_data["minimum_human_input_workspace"]
    approval = source_data["approval_input_validation"]
    builder = source_data["evidence_builder_output"]
    restore_tested = source_data["restore_tested_profile"]
    combined = source_data["combined_profile"]
    gap_row = find_row(source_data["gap_matrix"], "production_restore_policy")
    closure_row = find_row(source_data["closure_readiness_board"], "production_restore_policy")

    input_path_ready = approval.get("validation_status") == "pass" and approval.get("builder_ready") is True
    builder_ready = (
        builder.get("status") == "pass"
        and builder.get("input_complete") is True
        and builder.get("production_restore_policy_available") is True
    )
    restore_tested_ready = restore_tested.get("status") == "pass"
    combined_profile_ready = (
        combined.get("production_restore_policy_satisfied_by_profile") is True
        and combined.get("restore_tested_satisfied_by_profile") is True
        and combined.get("production_ready") is False
    )
    gap_matrix_open = gap_row.get("status") == "open"
    closure_board_not_ready = closure_row.get("closure_status") == "not_ready" or closure_row.get("status") == "not_ready"

    if combined_profile_ready:
        status = "ready_for_human_data_operations_profile_review_no_closure"
        resolved_path = "combined_profile"
        next_action = (
            "Human data-operations owner may review combined restore-tested and "
            "restore-policy evidence for a later matrix update request. Do not run "
            "restore, touch live data paths, close blockers, or claim production readiness."
        )
    elif builder_ready and restore_tested_ready:
        status = "ready_for_combined_data_operations_profile_review"
        resolved_path = "evidence_builder_output"
        next_action = "Review restore-policy builder output together with restore-tested profile; no closure is allowed."
    elif input_path_ready:
        status = "ready_for_restore_policy_evidence_builder_review_only"
        resolved_path = "approval_input_validation"
        next_action = "Use the validator output for review only; builder execution remains separate."
    else:
        status = "hold_restore_policy_human_input_required"
        resolved_path = "minimum_human_input_workspace"
        next_action = "Complete human-filled restore-policy input before builder or profile review."

    payload: dict[str, Any] = {
        "production_restore_policy_state_reconciliation_v0_1": True,
        "reconciliation_type": "local_production_restore_policy_state_reconciliation_no_restore_no_closure",
        "target_blocker_id": "production_restore_policy",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "resolved_current_path": resolved_path,
        "previous_minimum_workspace_status": minimum.get("status"),
        "approval_validation_status": approval.get("validation_status"),
        "approval_input_complete": approval.get("input_complete") is True,
        "approval_builder_ready": input_path_ready,
        "builder_output_status": builder.get("status"),
        "builder_output_ready": builder_ready,
        "production_restore_policy_available_for_review": builder.get("production_restore_policy_available") is True,
        "restore_tested_profile_ready": restore_tested_ready,
        "combined_profile_ready": combined_profile_ready,
        "production_restore_policy_satisfied_by_profile": combined.get(
            "production_restore_policy_satisfied_by_profile"
        )
        is True,
        "restore_tested_satisfied_by_profile": combined.get("restore_tested_satisfied_by_profile") is True,
        "gap_matrix_open": gap_matrix_open,
        "closure_board_not_ready": closure_board_not_ready,
        "source_paths": {name: rel(path) for name, path in SOURCES.items()},
        "human_review_required": True,
        "separate_matrix_update_request_required": True,
        "next_human_action": next_action,
        "why_this_exists": (
            "Older restore-policy surfaces can remain at first-input state while combined "
            "data-operations evidence is ready for human review. This file selects one "
            "safe next human action without running restore or closing blockers."
        ),
    }
    payload.update(FALSE_FLAGS)
    return payload


def write_outputs(payload: dict[str, Any]) -> None:
    write_json(OUT_JSON, payload)
    OUT_MD.write_text(
        f"""# SAEE Production Restore Policy State Reconciliation v0.1

Status: `{payload['status']}`

This local board reconciles the current `production_restore_policy` blocker
surfaces. It does not approve policy, run restores, touch live data paths,
close blockers, or claim production readiness.

## Current Finding

- target_blocker_id: `production_restore_policy`
- previous_minimum_workspace_status: `{payload['previous_minimum_workspace_status']}`
- approval_validation_status: `{payload['approval_validation_status']}`
- approval_input_complete: `{str(payload['approval_input_complete']).lower()}`
- builder_output_ready: `{str(payload['builder_output_ready']).lower()}`
- production_restore_policy_available_for_review: `{str(payload['production_restore_policy_available_for_review']).lower()}`
- restore_tested_profile_ready: `{str(payload['restore_tested_profile_ready']).lower()}`
- combined_profile_ready: `{str(payload['combined_profile_ready']).lower()}`
- production_restore_policy_satisfied_by_profile: `{str(payload['production_restore_policy_satisfied_by_profile']).lower()}`
- restore_tested_satisfied_by_profile: `{str(payload['restore_tested_satisfied_by_profile']).lower()}`
- gap_matrix_open: `{str(payload['gap_matrix_open']).lower()}`
- closure_board_not_ready: `{str(payload['closure_board_not_ready']).lower()}`
- resolved_current_path: `{payload['resolved_current_path']}`

## Next Human Action

{payload['next_human_action']}

## Boundary

- restore_run_by_codex=false
- restore_policy_published_by_codex=false
- live_data_path_touched=false
- blockers_closed_by_reconciliation=0
- production_ready=false
- customer_validated=false
- product_launched=false
- private_core_exposed=false
""",
        encoding="utf-8",
    )
    BOUNDARY.write_text(
        """# SAEE Production Restore Policy State Reconciliation Boundary Audit

- No restore run by Codex.
- No live data path touched.
- No restore policy approved by Codex.
- No restore policy published by Codex.
- No customer data collected or processed.
- No evidence collection authorized.
- No execution authorized.
- No canonical gap matrix modified.
- No canonical closure board modified.
- No blocker closure authorized.
- No blocker closed.
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
        f"""# SAEE Production Restore Policy State Reconciliation v0.1

Status: `{payload['status']}`

This is an agent-readable current-state board for the
`production_restore_policy` blocker. It reconciles existing local evidence only
and keeps restore execution, live-data access, matrix update, and blocker
closure behind separate human gates.

## Canonical Files

- `{rel(OUT_JSON)}`
- `{rel(OUT_MD)}`
- `{rel(BOUNDARY)}`
- `{rel(GATE)}`
- `scripts/saee_production_restore_policy_state_reconciliation.py`
- `scripts/saee_production_restore_policy_state_reconciliation_smoke.py`

## Truth State

- production_restore_policy_satisfied_by_profile={str(payload['production_restore_policy_satisfied_by_profile']).lower()}
- restore_tested_satisfied_by_profile={str(payload['restore_tested_satisfied_by_profile']).lower()}
- restore_run_by_codex=false
- live_data_path_touched=false
- blockers_closed_by_reconciliation=0
- production_ready=false
- customer_validated=false
- private_core_exposed=false
""",
        encoding="utf-8",
    )
    GATE.parent.mkdir(parents=True, exist_ok=True)
    GATE.write_text(
        f"""# SAEE Production Restore Policy State Reconciliation Gate

answer: hold_human_review_required_no_restore_no_auto_closure

reason: Combined restore-tested and restore-policy evidence is ready for human
review, but Codex has not run restore, touched live data paths, closed blockers,
or claimed production readiness.

status: `{payload['status']}`

boundary:
- restore_run_by_codex: false
- live_data_path_touched: false
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
        "/scripts/saee_production_restore_policy_state_reconciliation.py",
        "/scripts/saee_production_restore_policy_state_reconciliation_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["production_restore_policy_state_reconciliation_v0_1"] = {
        "name": "SAEE Production Restore Policy State Reconciliation v0.1",
        "status": payload["status"],
        "target_blocker_id": "production_restore_policy",
        "resolved_current_path": payload["resolved_current_path"],
        "production_restore_policy_available_for_review": payload[
            "production_restore_policy_available_for_review"
        ],
        "restore_tested_profile_ready": payload["restore_tested_profile_ready"],
        "combined_profile_ready": payload["combined_profile_ready"],
        "production_restore_policy_satisfied_by_profile": payload[
            "production_restore_policy_satisfied_by_profile"
        ],
        "restore_tested_satisfied_by_profile": payload["restore_tested_satisfied_by_profile"],
        "separate_matrix_update_request_required": True,
        "human_review_required": True,
        "restore_run_by_codex": False,
        "live_data_path_touched": False,
        "customer_data_processed": False,
        "blockers_closed_by_reconciliation": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "make_target": "make check-production-restore-policy-state-reconciliation",
    }
    write_json(AGENT_INDEX, index)

    block = f"""## Production Restore Policy State Reconciliation v0.1

- `production_restore_policy_state_reconciliation_v0_1`
- Status: `{payload['status']}`
- Target blocker: `production_restore_policy`
- Resolved current path: `{payload['resolved_current_path']}`
- production_restore_policy_satisfied_by_profile={str(payload['production_restore_policy_satisfied_by_profile']).lower()}
- restore_tested_satisfied_by_profile={str(payload['restore_tested_satisfied_by_profile']).lower()}
- restore_run_by_codex=false
- live_data_path_touched=false
- blockers_closed_by_reconciliation=0
- production_ready=false
- customer_validated=false
"""
    for surface in STATUS_SURFACES:
        replace_block(surface, "SAEE_PRODUCTION_RESTORE_POLICY_STATE_RECONCILIATION_V0_1", block)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_PRODUCTION_RESTORE_POLICY_STATE_RECONCILIATION: PASS "
        f"status={payload['status']} blockers_closed_by_reconciliation=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
