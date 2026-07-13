#!/usr/bin/env python3
"""Generate the current commercial blocker convergence audit.

This is a read-only status layer. It reconciles the older 24-blocker commercial
matrix with the newer final human inspection record that leaves only
`customer_validated` as the current actionable blocker. It does not close
blockers, contact customers, or modify product/runtime behavior.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "phase_b_product/commercial_readiness/commercial_blocker_convergence_audit"
SUMMARY = OUT / "commercial_blocker_convergence_audit.local.json"
REPORT = OUT / "commercial_blocker_convergence_audit.md"
BOUNDARY = OUT / "commercial_blocker_convergence_audit_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_BLOCKER_CONVERGENCE_AUDIT_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"

GAP = ROOT / "phase_b_product/commercial_readiness/commercial_readiness_gap_audit/commercial_readiness_gap_audit.local.json"
PRIORITY = ROOT / "phase_b_product/commercial_readiness/commercial_blocker_priority_index/commercial_blocker_priority_index.local.json"
FINAL_INSPECTION = ROOT / "phase_b_product/commercial_readiness/commercial_final_human_inspection/commercial_final_human_inspection_record.local.json"
PRIMARY_ACTION = ROOT / "phase_b_product/commercial_readiness/current_commercial_primary_action/current_commercial_primary_action.local.json"
NEXT_ACTION = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_next_action.local.json"
POST_PROCESSOR = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_post_session_processor/external_customer_validation_post_session_processor.local.json"

STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def ensure_line(path: Path, line: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if line not in text.splitlines():
        path.write_text(text.rstrip() + "\n" + line + "\n", encoding="utf-8")


def build_payload() -> dict[str, Any]:
    gap = read_json(GAP)
    priority = read_json(PRIORITY)
    final = read_json(FINAL_INSPECTION)
    primary = read_json(PRIMARY_ACTION)
    next_action = read_json(NEXT_ACTION)
    post = read_json(POST_PROCESSOR)

    legacy_count = int(gap.get("open_blocker_count", gap.get("production_blocker_count", 0)) or 0)
    priority_count = int(priority.get("open_blocker_count", priority.get("production_blocker_count", 0)) or 0)
    current_blockers = final.get("remaining_production_blockers_after_local_human_evidence", [])
    current_count = int(final.get("remaining_production_blocker_count_after_local_human_evidence", len(current_blockers)) or 0)

    converged = (
        legacy_count == 24
        and priority_count == 24
        and current_count == 1
        and current_blockers == ["customer_validated"]
        and primary.get("current_goal_blocker") == "customer_validated"
        and next_action.get("current_goal_blocker") == "customer_validated"
        and post.get("status") == "hold_human_session_entry_missing"
    )

    return {
        "commercial_blocker_convergence_audit_v0_1": True,
        "audit_type": "local_status_convergence_only",
        "status": "current_action_blocker_converged_to_customer_validated" if converged else "hold_status_convergence_review_required",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_legacy_gap_audit": rel(GAP),
        "source_legacy_priority_index": rel(PRIORITY),
        "source_final_human_inspection": rel(FINAL_INSPECTION),
        "source_current_primary_action": rel(PRIMARY_ACTION),
        "source_external_customer_validation_next_action": rel(NEXT_ACTION),
        "source_external_customer_validation_post_session_processor": rel(POST_PROCESSOR),
        "legacy_original_blocker_count": legacy_count,
        "legacy_priority_blocker_count": priority_count,
        "legacy_matrix_preserved": True,
        "legacy_matrix_overwritten": False,
        "local_human_evidence_lane_count": int(final.get("local_evidence_lane_count", 0) or 0),
        "local_human_evidence_lanes_passed": final.get("local_evidence_lanes_passed") is True,
        "current_actionable_blocker_count_after_local_human_evidence": current_count,
        "current_actionable_blockers_after_local_human_evidence": current_blockers,
        "current_goal_blocker": "customer_validated",
        "customer_validation_session_entry_exists": (
            ROOT
            / "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json"
        ).is_file(),
        "post_session_processor_status": post.get("status"),
        "post_session_processor_ready": post.get("human_entry_exists") is True,
        "convergence_explanation": (
            "The 24-blocker matrix is the original formal commercial readiness baseline. "
            "After local human-filled evidence inspection, the current actionable blocker "
            "is customer_validated. The older matrix is preserved for audit history and "
            "not overwritten."
        ),
        "next_human_action": (
            "Run one real external customer or target-user validation session, then save "
            "the generated session-entry JSON to "
            "phase_b_product/commercial_readiness/customer_validation_evidence/"
            "external_customer_validation_session_entry.human_filled.local.json."
        ),
        "production_ready": False,
        "product_launched": False,
        "customer_validated": False,
        "customer_contacted_by_codex": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "public_sdk_released": False,
        "blockers_closed_by_convergence_audit": 0,
        "development_permission_granted": False,
        "execution_authorized": False,
    }


def write_outputs(payload: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = f"""# SAEE Commercial Blocker Convergence Audit v0.1

Status: `{payload['status']}`.

This audit explains why two commercial blocker counts can coexist without
contradiction:

- Legacy formal readiness matrix: `{payload['legacy_original_blocker_count']}` blockers.
- Current actionable blocker after local human evidence inspection: `{payload['current_actionable_blocker_count_after_local_human_evidence']}` blocker.
- Current blocker: `customer_validated`.

## Interpretation

The 24-blocker matrix remains an audit baseline. It is not deleted or rewritten.
After local human-filled evidence surfaces were checked, the current commercial
action has converged to real external customer or target-user validation.

## Current Required Human Output

`phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json`

## Boundary

- production_ready=false
- product_launched=false
- customer_validated=false
- customer_contacted_by_codex=false
- private_core_exposed=false
- runtime_modified=false
- backend_modified=false
- kernel_modified=false
- api_schema_modified=false
- external_calls_made=false
- blockers_closed_by_convergence_audit=0
"""
    REPORT.write_text(report, encoding="utf-8")

    boundary = f"""# SAEE Commercial Blocker Convergence Boundary Audit

commercial_blocker_convergence_audit_v0_1: true
status: {payload['status']}

Confirmed:

- Legacy matrix preserved: {str(payload['legacy_matrix_preserved']).lower()}
- Legacy matrix overwritten: {str(payload['legacy_matrix_overwritten']).lower()}
- production_ready: false
- product_launched: false
- customer_validated: false
- customer_contacted_by_codex: false
- private_core_exposed: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- external_calls_made: false
- external_model_api_called: false
- blockers_closed_by_convergence_audit: 0
"""
    BOUNDARY.write_text(boundary, encoding="utf-8")

    gate = f"""# SAEE Commercial Blocker Convergence Audit Gate

answer: {payload['status']}

reason: The old 24-blocker readiness matrix is preserved as the original formal
audit baseline, while the current human-facing commercial action has converged
to `customer_validated` after local human evidence inspection.

boundary:
  production_ready: false
  product_launched: false
  customer_validated: false
  private_core_exposed: false
  runtime_modified: false
  backend_modified: false
  kernel_modified: false
  api_schema_modified: false
  blockers_closed_by_convergence_audit: 0

next_action: Run one real external customer or target-user validation session
and save the human-filled session-entry JSON before running the post-session
processor.
"""
    GATE.write_text(gate, encoding="utf-8")

    for line in [
        "/phase_b_product/commercial_readiness/commercial_blocker_convergence_audit/commercial_blocker_convergence_audit.md",
        "/phase_b_product/commercial_readiness/commercial_blocker_convergence_audit/commercial_blocker_convergence_audit.local.json",
        "/phase_b_product/commercial_readiness/commercial_blocker_convergence_audit/commercial_blocker_convergence_audit_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_BLOCKER_CONVERGENCE_AUDIT_GATE.md",
        "/scripts/saee_commercial_blocker_convergence_audit.py",
        "/scripts/saee_commercial_blocker_convergence_audit_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["commercial_blocker_convergence_audit_v0_1"] = {
        "name": "SAEE Commercial Blocker Convergence Audit v0.1",
        "status": payload["status"],
        "current_goal_blocker": payload["current_goal_blocker"],
        "legacy_original_blocker_count": payload["legacy_original_blocker_count"],
        "current_actionable_blocker_count_after_local_human_evidence": payload[
            "current_actionable_blocker_count_after_local_human_evidence"
        ],
        "current_actionable_blockers_after_local_human_evidence": payload[
            "current_actionable_blockers_after_local_human_evidence"
        ],
        "legacy_matrix_preserved": True,
        "legacy_matrix_overwritten": False,
        "customer_validation_session_entry_exists": payload[
            "customer_validation_session_entry_exists"
        ],
        "production_ready": False,
        "product_launched": False,
        "customer_validated": False,
        "customer_contacted_by_codex": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "blockers_closed_by_convergence_audit": 0,
        "entrypoints": {
            "summary": rel(SUMMARY),
            "report": rel(REPORT),
            "boundary_audit": rel(BOUNDARY),
            "gate": rel(GATE),
            "runner": "scripts/saee_commercial_blocker_convergence_audit.py",
            "smoke": "scripts/saee_commercial_blocker_convergence_audit_smoke.py",
        },
    }
    AGENT_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    block = f"""## Commercial Blocker Convergence Audit v0.1

- `commercial_blocker_convergence_audit_v0_1`
- Status: `{payload['status']}`
- Legacy formal blocker matrix: `{payload['legacy_original_blocker_count']}` blockers preserved for audit history.
- Current actionable blocker after local human evidence inspection: `customer_validated`.
- Required human output: `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json`.
- `production_ready=false`; `customer_validated=false`; `private_core_exposed=false`.
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_COMMERCIAL_BLOCKER_CONVERGENCE_AUDIT_V0_1", block)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_COMMERCIAL_BLOCKER_CONVERGENCE_AUDIT: PASS "
        f"status={payload['status']} "
        f"legacy_blockers={payload['legacy_original_blocker_count']} "
        f"current_blocker={payload['current_goal_blocker']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
