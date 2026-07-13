#!/usr/bin/env python3
"""Prepare and validate exact human approval for a 5-to-23 scope refresh.

Even when the exact phrase is accepted, this helper only writes a structured
human decision record. It never replaces the active request, regenerates an
execution request, applies matrix markers, or closes blockers.
"""

from __future__ import annotations

import argparse
import html
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
REQUEST_DIR = COMMERCIAL_DIR / "matrix_update_requests"
SCOPE_REFRESH = (
    REQUEST_DIR
    / "commercial_matrix_update_scope_refresh/commercial_matrix_update_scope_refresh.local.json"
)
OUT_DIR = REQUEST_DIR / "commercial_matrix_update_scope_refresh_approval"
TEMPLATE = OUT_DIR / "scope_refresh_approval_input.template.json"
HUMAN_FILLED = OUT_DIR / "scope_refresh_approval_input.human_filled.local.json"
INTAKE = OUT_DIR / "scope_refresh_approval_intake.local.json"
COPY_CARD_MD = OUT_DIR / "scope_refresh_approval_copy_card.md"
COPY_CARD_HTML = OUT_DIR / "scope_refresh_approval_copy_card.html"
BOUNDARY = OUT_DIR / "scope_refresh_approval_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_MATRIX_UPDATE_SCOPE_REFRESH_APPROVAL_INTAKE_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_SCOPE_REFRESH_APPROVAL_INTAKE_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
]

EXACT_SCOPE_REFRESH_PHRASE = (
    "批准矩阵申请范围刷新：将活动申请从 5 项更新为 23 项，仅刷新 no-execution 申请范围，"
    "不执行矩阵更新，不关闭 blocker，不声明生产可用。"
)

FALSE_FLAGS: dict[str, Any] = {
    "active_matrix_request_replaced": False,
    "execution_request_regenerated": False,
    "approval_scope_changed": False,
    "matrix_update_execution_authorized": False,
    "matrix_update_executed": False,
    "canonical_gap_matrix_modified": False,
    "canonical_closure_board_modified": False,
    "blocker_closure_authorized": False,
    "blockers_closed_by_scope_approval_intake": 0,
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
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return str(resolved)


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


def build_template(scope: dict[str, Any]) -> dict[str, Any]:
    return {
        "commercial_matrix_update_scope_refresh_approval_input_v0_1": True,
        "input_type": "human_scope_refresh_approval_no_execution",
        "source_scope_refresh": rel(SCOPE_REFRESH),
        "previous_target_count": scope.get("previous_target_count"),
        "refreshed_target_count": scope.get("refreshed_target_count"),
        "refreshed_target_ids": scope.get("refreshed_target_ids", []),
        "human_decision": "",
        "human_reviewer": "",
        "decision_date": "",
        "approval_reference": "",
        "approve_scope_refresh_5_to_23_no_execution": False,
        "confirm_active_request_replacement_requires_separate_step": False,
        "confirm_no_matrix_update_execution": False,
        "confirm_no_blocker_closure": False,
        "confirm_no_production_ready_claim": False,
        "confirm_customer_validation_remains_missing": False,
        "notes": "",
    }


def build_human_filled(
    template: dict[str, Any], reviewer: str, approval_reference: str
) -> dict[str, Any]:
    data = dict(template)
    data.update(
        {
            "human_decision": "approve_matrix_request_scope_refresh_5_to_23_no_execution",
            "human_reviewer": reviewer,
            "decision_date": date.today().isoformat(),
            "approval_reference": approval_reference,
            "approve_scope_refresh_5_to_23_no_execution": True,
            "confirm_active_request_replacement_requires_separate_step": True,
            "confirm_no_matrix_update_execution": True,
            "confirm_no_blocker_closure": True,
            "confirm_no_production_ready_claim": True,
            "confirm_customer_validation_remains_missing": True,
            "notes": (
                "Human approved the 5-to-23 no-execution request-scope refresh only. "
                "A separate replacement step and a later exact execution approval remain required."
            ),
        }
    )
    return data


def build_payload(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    scope = read_json(SCOPE_REFRESH)
    template = build_template(scope)
    phrase = args.phrase.strip()
    phrase_matches = phrase == EXACT_SCOPE_REFRESH_PHRASE
    scope_ready = (
        scope.get("status") == "ready_for_human_scope_refresh_review_no_execution"
        and scope.get("previous_target_count") == 5
        and scope.get("refreshed_target_count") == 23
        and scope.get("not_cataloged_blocker_ids") == ["customer_validated"]
        and scope.get("active_matrix_request_replaced") is False
        and scope.get("matrix_update_executed") is False
    )
    output_path = Path(args.human_filled_output).expanduser().resolve()
    human_filled_written = False
    if args.write_human_filled and phrase_matches and scope_ready:
        approval_reference = (
            args.approval_reference
            or f"human-scope-refresh-approval-{date.today().isoformat()}"
        )
        write_json(
            output_path,
            build_human_filled(template, args.reviewer, approval_reference),
        )
        human_filled_written = True

    if not scope_ready:
        status = "hold_scope_refresh_packet_not_ready"
    elif human_filled_written:
        status = "scope_refresh_phrase_accepted_human_record_written_no_activation"
    else:
        status = "waiting_for_exact_human_scope_refresh_phrase"

    payload: dict[str, Any] = {
        "commercial_matrix_update_scope_refresh_approval_intake_v0_1": True,
        "intake_type": "exact_phrase_to_scope_refresh_human_record_no_activation_no_execution",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_scope_refresh": rel(SCOPE_REFRESH),
        "scope_refresh_packet_ready": scope_ready,
        "previous_target_count": scope.get("previous_target_count"),
        "refreshed_target_count": scope.get("refreshed_target_count"),
        "not_cataloged_blocker_ids": scope.get("not_cataloged_blocker_ids", []),
        "exact_phrase_required": True,
        "exact_scope_refresh_phrase": EXACT_SCOPE_REFRESH_PHRASE,
        "phrase_provided": bool(phrase),
        "phrase_matches_exactly": phrase_matches,
        "write_human_filled_requested": args.write_human_filled,
        "human_filled_scope_approval_written": human_filled_written,
        "human_filled_scope_approval_path": rel(output_path),
        "scope_refresh_human_approved_by_intake": human_filled_written,
        "ready_for_separate_active_request_replacement_validator": human_filled_written,
        "separate_active_request_replacement_step_required": True,
        "separate_matrix_execution_approval_still_required": True,
        "recommendation_gate": "conditional",
        "next_human_action": (
            "Run a separate active-request replacement validator; do not execute matrix updates."
            if human_filled_written
            else "Provide the exact scope-refresh phrase only after reviewing the 23-row packet."
        ),
        **FALSE_FLAGS,
    }
    return payload, template


def write_outputs(payload: dict[str, Any], template: dict[str, Any]) -> None:
    write_json(TEMPLATE, template)
    write_json(INTAKE, payload)
    COPY_CARD_MD.write_text(
        f"""# SAEE Matrix Request Scope Refresh Approval Copy Card

Status: `{payload['status']}`

Review the 23-row scope packet before sending this exact phrase:

> {EXACT_SCOPE_REFRESH_PHRASE}

This phrase approves only a structured human record for a future 5-to-23
request-scope refresh. It does not replace the active request, regenerate the
execution request, execute matrix changes, or close blockers.

- previous_target_count: `5`
- refreshed_target_count: `23`
- not_cataloged_blocker_ids: `customer_validated`
- human_filled_scope_approval_written: `{str(payload['human_filled_scope_approval_written']).lower()}`
- active_matrix_request_replaced: `false`
- approval_scope_changed: `false`
- matrix_update_executed: `false`
- blockers_closed_by_scope_approval_intake: `0`
- production_ready: `false`
- customer_validated: `false`
""",
        encoding="utf-8",
    )
    escaped = html.escape(EXACT_SCOPE_REFRESH_PHRASE)
    COPY_CARD_HTML.write_text(
        f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>SAEE 范围刷新确认</title>
<style>body{{font-family:system-ui,sans-serif;max-width:760px;margin:48px auto;padding:0 24px;color:#171717}}pre{{white-space:pre-wrap;padding:20px;background:#f5f5f5;border:1px solid #ddd}}.hold{{color:#8a4b00}}</style></head>
<body><main><h1>SAEE 矩阵申请范围刷新确认</h1><p class="hold">仅确认 5→23 项申请范围，不执行矩阵更新。</p><pre>{escaped}</pre><p>当前活动申请仍为 5 项；customer_validated 仍未满足。</p></main></body></html>
""",
        encoding="utf-8",
    )
    BOUNDARY.write_text(
        """# Matrix Scope Refresh Approval Intake Boundary Audit

- Exact phrase helper only; default state is waiting.
- Accepted phrase may write only a structured human scope record.
- No active request replacement or execution-request regeneration.
- No matrix write, blocker closure, production claim, or customer-validation claim.
- No runtime, backend, kernel, API schema, or private core modification.

active_matrix_request_replaced=false
execution_request_regenerated=false
approval_scope_changed=false
matrix_update_executed=false
blockers_closed_by_scope_approval_intake=0
production_ready=false
customer_validated=false
private_core_exposed=false
""",
        encoding="utf-8",
    )
    TOP_DOC.write_text(
        f"""# SAEE Commercial Matrix Update Scope Refresh Approval Intake v0.1

commercial_matrix_update_scope_refresh_approval_intake_v0_1: true
status: {payload['status']}
previous_target_count: 5
refreshed_target_count: 23
exact_phrase_required: true
human_filled_scope_approval_written: {str(payload['human_filled_scope_approval_written']).lower()}
separate_active_request_replacement_step_required: true
separate_matrix_execution_approval_still_required: true
active_matrix_request_replaced=false
matrix_update_executed=false
blockers_closed_by_scope_approval_intake=0
production_ready=false
customer_validated=false
""",
        encoding="utf-8",
    )
    GATE.write_text(
        f"""# SAEE Commercial Matrix Update Scope Refresh Approval Intake Gate

answer: {payload['status']}
recommendation_gate: conditional

reason:
The 23-row scope packet is ready for explicit human review. This intake keeps
scope approval separate from active-request replacement and matrix execution.

boundary:
active_matrix_request_replaced: false
execution_request_regenerated: false
approval_scope_changed: false
matrix_update_execution_authorized: false
matrix_update_executed: false
blocker_closure_authorized: false
blockers_closed_by_scope_approval_intake: 0
production_ready: false
customer_validated: false
private_core_exposed: false

next_action:
Human may provide the exact scope-refresh phrase. A separate replacement step
and a later matrix-execution approval remain required.
""",
        encoding="utf-8",
    )

    for line in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_SCOPE_REFRESH_APPROVAL_INTAKE_V0_1.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_scope_refresh_approval/scope_refresh_approval_input.template.json",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_scope_refresh_approval/scope_refresh_approval_intake.local.json",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_scope_refresh_approval/scope_refresh_approval_copy_card.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_scope_refresh_approval/scope_refresh_approval_copy_card.html",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_scope_refresh_approval/scope_refresh_approval_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_SCOPE_REFRESH_APPROVAL_INTAKE_GATE.md",
        "/scripts/saee_commercial_matrix_update_scope_refresh_approval_intake.py",
        "/scripts/saee_commercial_matrix_update_scope_refresh_approval_intake_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    keys = [
        "status", "intake_type", "scope_refresh_packet_ready",
        "previous_target_count", "refreshed_target_count",
        "not_cataloged_blocker_ids", "exact_phrase_required",
        "phrase_matches_exactly", "human_filled_scope_approval_written",
        "scope_refresh_human_approved_by_intake",
        "ready_for_separate_active_request_replacement_validator",
        "separate_active_request_replacement_step_required",
        "separate_matrix_execution_approval_still_required", "recommendation_gate",
        "active_matrix_request_replaced", "execution_request_regenerated",
        "approval_scope_changed", "matrix_update_execution_authorized",
        "matrix_update_executed", "blocker_closure_authorized",
        "blockers_closed_by_scope_approval_intake", "production_ready",
        "customer_validated", "product_launched", "private_core_exposed",
        "runtime_modified", "backend_modified", "kernel_modified",
        "api_schema_modified",
    ]
    index["commercial_matrix_update_scope_refresh_approval_intake_v0_1"] = {
        key: payload[key] for key in keys
    }
    write_json(AGENT_INDEX, index)

    block = f"""## Commercial Matrix Update Scope Refresh Approval Intake v0.1

Status: `{payload['status']}`.

The exact-phrase intake is available for the `5→23` no-execution request-scope
refresh. `human_filled_scope_approval_written={str(payload['human_filled_scope_approval_written']).lower()}`,
`active_matrix_request_replaced=false`, `approval_scope_changed=false`,
`matrix_update_executed=false`, `blockers_closed_by_scope_approval_intake=0`,
`production_ready=false`, and `customer_validated=false`.
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_COMMERCIAL_MATRIX_UPDATE_SCOPE_REFRESH_APPROVAL_INTAKE", block)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phrase", default="")
    parser.add_argument("--reviewer", default="张斌")
    parser.add_argument("--approval-reference", default="")
    parser.add_argument("--write-human-filled", action="store_true")
    parser.add_argument("--human-filled-output", default=str(HUMAN_FILLED))
    return parser.parse_args()


def main() -> None:
    payload, template = build_payload(parse_args())
    write_outputs(payload, template)
    print(
        "SAEE_COMMERCIAL_MATRIX_UPDATE_SCOPE_REFRESH_APPROVAL_INTAKE: PASS "
        f"status={payload['status']} "
        f"human_record_written={str(payload['human_filled_scope_approval_written']).lower()} "
        "active_request_replaced=false matrix_update_executed=false "
        "blockers_closed=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
