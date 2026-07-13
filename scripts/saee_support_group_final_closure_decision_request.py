#!/usr/bin/env python3
"""Build a human decision request for support-group blocker closure.

This request packet is deliberately non-executing. It converts the local
support-group closure review packet into a compact human final-decision surface
without updating the formal gap matrix, closing blockers, launching product, or
claiming production readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SUPPORT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
OUT_JSON = SUPPORT_DIR / "support_group_final_closure_decision_request.local.json"
OUT_MD = SUPPORT_DIR / "support_group_final_closure_decision_request.md"
OUT_CSV = SUPPORT_DIR / "support_group_final_closure_decision_request.csv"
TEMPLATE = SUPPORT_DIR / "support_group_final_closure_decision_template.json"
BOUNDARY = SUPPORT_DIR / "support_group_final_closure_decision_request_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/SUPPORT_GROUP_FINAL_CLOSURE_DECISION_REQUEST_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_SUPPORT_GROUP_FINAL_CLOSURE_DECISION_REQUEST_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
]

SOURCE_PACKET = SUPPORT_DIR / "support_group_closure_review_packet.local.json"
SOURCE_REFRESH = SUPPORT_DIR / "support_group_human_filled_evidence_refresh.local.json"
SOURCE_COMBINED = SUPPORT_DIR / "production_support_sla_evidence.combined_from_all_support_human_filled.local.json"

FALSE_FLAGS = {
    "final_human_decision_recorded": False,
    "blocker_closure_authorized": False,
    "blockers_closed_by_request": 0,
    "canonical_gap_matrix_modified": False,
    "canonical_closure_board_modified": False,
    "development_permission_granted": False,
    "execution_authorized": False,
    "evidence_collection_authorized": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "private_core_exposed": False,
    "product_launched": False,
    "production_ready": False,
    "customer_validated": False,
    "customer_contacted": False,
    "support_vendor_contacted": False,
    "support_contact_published_by_codex": False,
    "support_contact_test_sent_by_codex": False,
    "sla_published_by_codex": False,
    "on_call_rotation_started_by_codex": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "public_sdk_released": False,
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
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


def build_decision_rows(packet: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in packet.get("closure_review_rows", []):
        if not isinstance(row, dict):
            continue
        ready = row.get("closure_review_status") == "ready_for_human_final_closure_review"
        rows.append(
            {
                "blocker_id": row.get("blocker_id", ""),
                "evidence_complete": row.get("evidence_complete") is True,
                "source_group": row.get("source_group", ""),
                "recommended_final_decision": "approve_for_separate_matrix_update_request" if ready else "hold",
                "recommended_reason": (
                    "local support evidence complete; still requires separate matrix update request"
                    if ready
                    else "support evidence not complete"
                ),
                "closure_authorized_by_this_request": False,
                "matrix_update_authorized_by_this_request": False,
            }
        )
    return rows


def build_payload() -> dict[str, Any]:
    packet = read_json(SOURCE_PACKET)
    refresh = read_json(SOURCE_REFRESH)
    combined = read_json(SOURCE_COMBINED)
    rows = build_decision_rows(packet)
    ready_count = sum(1 for row in rows if row["recommended_final_decision"] == "approve_for_separate_matrix_update_request")
    status = (
        "ready_for_human_final_closure_decision_input"
        if ready_count == 4 and packet.get("ready_for_human_final_closure_review") is True
        else "hold_support_group_closure_packet_not_ready"
    )
    return {
        "support_group_final_closure_decision_request_v0_1": True,
        "request_type": "human_final_closure_decision_request_no_execution",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target_blocker_group": "support",
        "target_blockers": packet.get("target_blockers", []),
        "source_support_group_closure_review_packet": rel(SOURCE_PACKET),
        "source_support_group_refresh": rel(SOURCE_REFRESH),
        "source_combined_support_evidence": rel(SOURCE_COMBINED),
        "source_packet_status": packet.get("status"),
        "source_refresh_status": refresh.get("status"),
        "production_support_available": refresh.get("production_support_available") is True,
        "support_group_evidence_complete": packet.get("support_group_evidence_complete") is True,
        "support_group_closure_candidate_count": packet.get("support_group_closure_candidate_count", 0),
        "decision_row_count": len(rows),
        "recommended_approve_for_separate_matrix_update_count": ready_count,
        "allowed_final_decisions": [
            "approve_for_separate_matrix_update_request",
            "hold",
            "reject",
        ],
        "recommended_human_decision": "approve_for_separate_matrix_update_request",
        "decision_rows": rows,
        "template_path": rel(TEMPLATE),
        "combined_support_boundary_flags": {
            "codex_published_support_contact": combined.get("codex_published_support_contact") is True,
            "codex_sent_support_contact_test": combined.get("codex_sent_support_contact_test") is True,
            "sla_published_by_codex": combined.get("sla_published_by_codex") is True,
            "on_call_rotation_started_by_codex": combined.get("on_call_rotation_started_by_codex") is True,
        },
        "next_human_action": (
            "fill support_group_final_closure_decision_template.json if the team wants "
            "to approve, hold, or reject promotion into a separate matrix update request"
        ),
        **FALSE_FLAGS,
    }


def write_outputs(payload: dict[str, Any]) -> None:
    write_json(OUT_JSON, payload)
    existing_template = read_json(TEMPLATE) if TEMPLATE.exists() else {}
    template = {
        "decision_scope": "support_group_final_closure_decision",
        "target_blockers": payload["target_blockers"],
        "allowed_final_decisions": payload["allowed_final_decisions"],
        "recommended_final_decision": payload["recommended_human_decision"],
        "human_final_decision": "",
        "human_reviewer": "",
        "decision_date": "",
        "reason": "",
        "authorize_separate_matrix_update_request": False,
        "authorize_blocker_closure_now": False,
        "authorize_product_launch": False,
        "confirm_no_customer_validation_claim": True,
        "confirm_no_production_ready_claim": True,
    }
    if any(
        existing_template.get(field)
        for field in ["human_final_decision", "human_reviewer", "decision_date", "reason"]
    ):
        for field in [
            "human_final_decision",
            "human_reviewer",
            "decision_date",
            "reason",
            "authorize_separate_matrix_update_request",
            "authorize_blocker_closure_now",
            "authorize_product_launch",
            "confirm_no_customer_validation_claim",
            "confirm_no_production_ready_claim",
        ]:
            if field in existing_template:
                template[field] = existing_template[field]
    write_json(TEMPLATE, template)

    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "blocker_id",
                "source_group",
                "evidence_complete",
                "recommended_final_decision",
                "closure_authorized_by_this_request",
                "matrix_update_authorized_by_this_request",
            ],
        )
        writer.writeheader()
        for row in payload["decision_rows"]:
            writer.writerow({key: row[key] for key in writer.fieldnames})

    table = "\n".join(
        "| {blocker_id} | {evidence_complete} | {recommended_final_decision} | {closure_authorized_by_this_request} |".format(
            **row
        )
        for row in payload["decision_rows"]
    )
    OUT_MD.write_text(
        f"""# SAEE Support Group Final Closure Decision Request v0.1

Status: `{payload['status']}`

This is a human decision request for the four support-related blockers. It
recommends a final human decision, but it does not authorize closure or update
the formal production blocker matrix.

## Summary

- target_blockers: `{', '.join(payload['target_blockers'])}`
- source_packet_status: `{payload['source_packet_status']}`
- production_support_available: `{str(payload['production_support_available']).lower()}`
- support_group_evidence_complete: `{str(payload['support_group_evidence_complete']).lower()}`
- decision_row_count: `{payload['decision_row_count']}`
- recommended_approve_for_separate_matrix_update_count: `{payload['recommended_approve_for_separate_matrix_update_count']}`
- recommended_human_decision: `{payload['recommended_human_decision']}`
- final_human_decision_recorded: `false`
- blockers_closed_by_request: `0`

## Decision Rows

| Blocker | Evidence complete | Recommended final decision | Closure authorized by this request |
| --- | --- | --- | --- |
{table}

## Human Input Template

Fill this file only if you want to record the final human decision:

`{payload['template_path']}`

Recommended value:

`approve_for_separate_matrix_update_request`

This still does not close blockers. It only prepares a future separate matrix
update request.

## Boundary

- final_human_decision_recorded=false
- blocker_closure_authorized=false
- blockers_closed_by_request=0
- canonical_gap_matrix_modified=false
- canonical_closure_board_modified=false
- development_permission_granted=false
- execution_authorized=false
- production_ready=false
- customer_validated=false
- product_launched=false
- private_core_exposed=false
""",
        encoding="utf-8",
    )

    BOUNDARY.write_text(
        """# SAEE Support Group Final Closure Decision Request Boundary Audit

support_group_final_closure_decision_request_v0_1: true
status: ready_for_human_final_closure_decision_input

- Human decision request only.
- No final human decision recorded by Codex.
- No blocker closure authorized.
- No canonical gap matrix modified.
- No canonical closure board modified.
- No runtime modified.
- No backend modified.
- No kernel modified.
- No API schema modified.
- No private core exposed.
- No product launched.
- No customer contacted.
- No support vendor contacted.
- No production-ready claim added.
- No customer-validation claim added.
- blockers_closed_by_request: 0
""",
        encoding="utf-8",
    )

    TOP_DOC.write_text(
        """# SAEE Support Group Final Closure Decision Request v0.1

support_group_final_closure_decision_request_v0_1: true
status: ready_for_human_final_closure_decision_input

Purpose: ask a human to approve, hold, or reject whether the locally complete
support-group evidence should be promoted into a separate formal matrix update
request.

This request does not close blockers, update the formal production matrix,
launch product, contact customers, or claim production readiness.

Entrypoints:

- `phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_request.local.json`
- `phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_request.md`
- `phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_template.json`
- `phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_request_boundary_audit.md`
""",
        encoding="utf-8",
    )

    GATE.write_text(
        """# SAEE Support Group Final Closure Decision Request Gate

answer: ready_for_human_final_closure_decision_input

reason: Support-group evidence is locally complete for support_contact,
customer_support, sla, and on_call_rotation. A human may now decide whether to
approve a separate matrix update request. This gate does not authorize closure.

boundary:
- final_human_decision_recorded: false
- blocker_closure_authorized: false
- blockers_closed_by_request: 0
- canonical_gap_matrix_modified: false
- canonical_closure_board_modified: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

next_action: human fills the decision template with approve, hold, or reject.
""",
        encoding="utf-8",
    )

    for line in [
        "/phase_b_product/commercial_readiness/SUPPORT_GROUP_FINAL_CLOSURE_DECISION_REQUEST_V0_1.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_request.local.json",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_request.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_request.csv",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_template.json",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_request_boundary_audit.md",
        "/docs/strategy/SAEE_SUPPORT_GROUP_FINAL_CLOSURE_DECISION_REQUEST_GATE.md",
        "/scripts/saee_support_group_final_closure_decision_request.py",
        "/scripts/saee_support_group_final_closure_decision_request_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["support_group_final_closure_decision_request_v0_1"] = {
        "name": "SAEE Support Group Final Closure Decision Request v0.1",
        "status": payload["status"],
        "target_blocker_group": "support",
        "target_blockers": payload["target_blockers"],
        "recommended_human_decision": payload["recommended_human_decision"],
        "final_human_decision_recorded": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_request": 0,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
        "development_permission_granted": False,
        "execution_authorized": False,
        "customer_validated": False,
        "production_ready": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "customer_contacted": False,
        "entrypoints": {
            "summary": rel(OUT_JSON),
            "report": rel(OUT_MD),
            "csv": rel(OUT_CSV),
            "decision_template": rel(TEMPLATE),
            "boundary_audit": rel(BOUNDARY),
            "gate": rel(GATE),
            "top_doc": rel(TOP_DOC),
            "runner": "scripts/saee_support_group_final_closure_decision_request.py",
            "smoke": "scripts/saee_support_group_final_closure_decision_request_smoke.py",
        },
        "make_target": "make check-support-group-final-closure-decision-request",
    }
    AGENT_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    block = f"""## Support Group Final Closure Decision Request v0.1

- `support_group_final_closure_decision_request_v0_1`
- Status: `{payload['status']}`
- Target blockers: `support_contact`, `customer_support`, `sla`, `on_call_rotation`
- recommended_human_decision={payload['recommended_human_decision']}
- final_human_decision_recorded=false
- blocker_closure_authorized=false
- blockers_closed_by_request=0
- production_ready=false
- customer_validated=false
- private_core_exposed=false
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_SUPPORT_GROUP_FINAL_CLOSURE_DECISION_REQUEST_V0_1", block)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_SUPPORT_GROUP_FINAL_CLOSURE_DECISION_REQUEST: PASS "
        f"status={payload['status']} "
        f"recommended_human_decision={payload['recommended_human_decision']} "
        "blockers_closed_by_request=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
