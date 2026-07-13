#!/usr/bin/env python3
"""Review support-contact closure gaps without closing the blocker.

This local review reads the already generated support-contact evidence and the
commercial closure board, then explains why `support_contact` still is not
eligible for blocker closure. It does not publish a support contact, send test
messages, contact customers or vendors, close blockers, modify runtime/backend,
or claim production readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SUPPORT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
OUT_JSON = SUPPORT_DIR / "support_contact_closure_gap_review.local.json"
OUT_MD = SUPPORT_DIR / "support_contact_closure_gap_review.md"
OUT_CSV = SUPPORT_DIR / "support_contact_closure_gap_review.csv"
BOUNDARY = SUPPORT_DIR / "support_contact_closure_gap_review_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/SUPPORT_CONTACT_CLOSURE_GAP_REVIEW_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_SUPPORT_CONTACT_CLOSURE_GAP_REVIEW_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
]

SUPPORT_EVIDENCE = SUPPORT_DIR / "production_support_sla_evidence.from_support_contact.human_filled.local.json"
SUPPORT_GROUP_REFRESH = SUPPORT_DIR / "support_group_human_filled_evidence_refresh.local.json"
COMBINED_SUPPORT_EVIDENCE = (
    SUPPORT_DIR / "production_support_sla_evidence.combined_from_all_support_human_filled.local.json"
)
BUILDER_REQUEST = SUPPORT_DIR / "support_contact_evidence_builder_execution_request.local.json"
CLOSURE_BOARD = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_blocker_closure_readiness_board/"
    "closure_readiness_board.local.json"
)

SUPPORT_CONTACT_KEYS = (
    "customer_facing_support_contact_configured",
    "support_contact_owner_named",
    "abuse_handling_path_defined",
    "customer_notice_route_defined",
    "support_contact_test_recorded",
)
CUSTOMER_SUPPORT_KEYS = (
    "staffed_support_process_defined",
    "case_triage_workflow_defined",
    "support_case_audit_trail_available",
    "handoff_to_engineering_defined",
    "customer_communication_template_approved",
    "support_process_dry_run_recorded",
)
SLA_KEYS = (
    "human_approved_sla_terms",
    "severity_definitions_approved",
    "support_hours_approved",
    "response_targets_approved",
    "exclusions_approved",
    "legal_review_completed",
)
ON_CALL_KEYS = (
    "on_call_rotation_defined",
    "escalation_schedule_defined",
    "incident_commander_named",
)

FALSE_FLAGS = {
    "customer_validated": False,
    "production_ready": False,
    "product_launched": False,
    "private_core_exposed": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "customer_contacted": False,
    "support_vendor_contacted": False,
    "support_contact_published_by_codex": False,
    "support_contact_test_sent_by_codex": False,
    "blocker_closure_authorized": False,
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


def missing_keys(data: dict[str, Any], keys: tuple[str, ...]) -> list[str]:
    return [key for key in keys if data.get(key) is not True]


def closure_board_support_contact(board: dict[str, Any]) -> dict[str, Any]:
    for item in board.get("blocker_closure_readiness_review", []):
        if isinstance(item, dict) and item.get("blocker_id") == "support_contact":
            return item
    return {}


def build_gap_rows(support: dict[str, Any]) -> list[dict[str, Any]]:
    groups = [
        ("support_contact", SUPPORT_CONTACT_KEYS, "Support intake contact, owner, abuse path, notice route, and test record."),
        ("customer_support", CUSTOMER_SUPPORT_KEYS, "Staffed support workflow, triage, audit trail, engineering handoff, customer template, and dry run."),
        ("sla", SLA_KEYS, "Human-approved SLA terms, severity definitions, hours, response targets, exclusions, and legal review."),
        ("on_call", ON_CALL_KEYS, "On-call rotation, escalation schedule, and incident commander ownership."),
    ]
    rows: list[dict[str, Any]] = []
    for group_id, keys, purpose in groups:
        missing = missing_keys(support, keys)
        rows.append(
            {
                "group_id": group_id,
                "purpose": purpose,
                "required_count": len(keys),
                "complete_count": len(keys) - len(missing),
                "missing_count": len(missing),
                "missing_keys": missing,
                "ready_for_review": not missing,
            }
        )
    return rows


def build_payload() -> dict[str, Any]:
    support = read_json(COMBINED_SUPPORT_EVIDENCE)
    refresh = read_json(SUPPORT_GROUP_REFRESH)
    request = read_json(BUILDER_REQUEST)
    board = read_json(CLOSURE_BOARD)
    board_item = closure_board_support_contact(board)
    gap_rows = build_gap_rows(support)
    missing_total = sum(row["missing_count"] for row in gap_rows)
    support_contact_ready = next(row for row in gap_rows if row["group_id"] == "support_contact")[
        "ready_for_review"
    ]
    return {
        "support_contact_closure_gap_review_v0_1": True,
        "review_type": "local_support_contact_closure_gap_review_no_closure",
        "status": "hold_support_group_complete_pending_go_no_go_and_closure_review",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target_blocker_id": "support_contact",
        "source_support_contact_evidence": rel(SUPPORT_EVIDENCE),
        "source_support_group_refresh": rel(SUPPORT_GROUP_REFRESH),
        "source_combined_support_evidence": rel(COMBINED_SUPPORT_EVIDENCE),
        "source_builder_execution_request": rel(BUILDER_REQUEST),
        "source_closure_board": rel(CLOSURE_BOARD),
        "support_group_refresh_status": refresh.get("status"),
        "support_group_evidence_complete": refresh.get("production_support_available") is True,
        "builder_execution_status": request.get("status"),
        "evidence_builder_executed": request.get("evidence_builder_executed") is True,
        "support_contact_available_for_review": support_contact_ready,
        "production_support_available": refresh.get("production_support_available") is True,
        "closure_board_status": board_item.get("closure_status"),
        "closure_ready_for_human_final_review": False,
        "closure_blocking_reasons": sorted(
            set(
                list(board_item.get("blocking_reasons", []))
                + [
                    "commercial_go_no_go_not_refreshed_for_human_filled_support_group",
                    "separate_blocker_closure_approval_required",
                ]
            )
        ),
        "gap_group_count": len(gap_rows),
        "missing_evidence_group_count": sum(1 for row in gap_rows if row["missing_count"]),
        "missing_evidence_item_count": missing_total,
        "gap_rows": gap_rows,
        "next_required_human_evidence": [
            "rerun the commercial go/no-go/profile using the combined human-filled support evidence",
            "review support group evidence in a separate blocker-closure gate",
            "keep customer validation and production launch claims separate",
        ],
        "blockers_closed_by_gap_review": 0,
        "accepted_for_blocker_closure_count": 0,
        "human_review_required": True,
        **FALSE_FLAGS,
    }


def write_outputs(payload: dict[str, Any]) -> None:
    write_json(OUT_JSON, payload)

    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "group_id",
                "purpose",
                "required_count",
                "complete_count",
                "missing_count",
                "missing_keys",
                "ready_for_review",
            ],
        )
        writer.writeheader()
        for row in payload["gap_rows"]:
            csv_row = dict(row)
            csv_row["missing_keys"] = ";".join(row["missing_keys"])
            writer.writerow(csv_row)

    rows_md = "\n".join(
        "| {group_id} | {complete_count}/{required_count} | {missing_count} | {ready_for_review} | `{missing}` |".format(
            **row,
            missing=", ".join(row["missing_keys"]) or "none",
        )
        for row in payload["gap_rows"]
    )
    OUT_MD.write_text(
        f"""# SAEE Support Contact Closure Gap Review v0.1

Status: `{payload['status']}`

This is a local review of the `support_contact` blocker after the support-contact
evidence builder and full support-group human-filled evidence refresh have run.
It explains why the blocker still cannot be closed automatically.

## Summary

- target_blocker_id: `support_contact`
- builder_execution_status: `{payload['builder_execution_status']}`
- evidence_builder_executed: `{str(payload['evidence_builder_executed']).lower()}`
- support_group_refresh_status: `{payload['support_group_refresh_status']}`
- support_group_evidence_complete: `{str(payload['support_group_evidence_complete']).lower()}`
- support_contact_available_for_review: `{str(payload['support_contact_available_for_review']).lower()}`
- production_support_available: `{str(payload['production_support_available']).lower()}`
- closure_ready_for_human_final_review: `false`
- missing_evidence_item_count: `{payload['missing_evidence_item_count']}`
- blockers_closed_by_gap_review: `0`

## Gap Table

| Group | Complete | Missing | Ready | Missing Keys |
| --- | ---: | ---: | --- | --- |
{rows_md}

## Next Required Human Review

- Rerun or review the commercial go/no-go/profile using the combined
  human-filled support evidence.
- Review the support group evidence in a separate blocker-closure gate.
- Keep customer validation and production launch claims separate.

## Boundary

- production_support_available={str(payload['production_support_available']).lower()}
- closure_ready_for_human_final_review=false
- customer_validated=false
- production_ready=false
- product_launched=false
- private_core_exposed=false
- customer_contacted=false
- support_contact_published_by_codex=false
- blockers_closed_by_gap_review=0
""",
        encoding="utf-8",
    )

    BOUNDARY.write_text(
        """# SAEE Support Contact Closure Gap Review Boundary Audit

support_contact_closure_gap_review_v0_1: true
status: hold_support_group_complete_pending_go_no_go_and_closure_review

- Local review only.
- Support group evidence may be locally complete, but no blocker closure is authorized.
- No support contact published by Codex.
- No support-contact test sent by Codex.
- No customer contacted.
- No support vendor contacted.
- No runtime modified.
- No backend modified.
- No kernel modified.
- No API schema modified.
- No private core exposed.
- No product launched.
- No production-ready claim added.
- blockers_closed_by_gap_review: 0
""",
        encoding="utf-8",
    )

    TOP_DOC.write_text(
        """# SAEE Support Contact Closure Gap Review v0.1

support_contact_closure_gap_review_v0_1: true
status: hold_support_group_complete_pending_go_no_go_and_closure_review

Purpose: make the remaining `support_contact` closure gate state agent-readable
after the local support-contact evidence builder and support-group human-filled
evidence refresh have run.

This is not blocker closure and does not authorize support publication, support
testing, customer contact, launch, or production-readiness claims.

Entrypoints:

- `phase_b_product/commercial_readiness/support_evidence/support_contact_closure_gap_review.local.json`
- `phase_b_product/commercial_readiness/support_evidence/support_contact_closure_gap_review.md`
- `phase_b_product/commercial_readiness/support_evidence/support_contact_closure_gap_review.csv`
- `phase_b_product/commercial_readiness/support_evidence/support_contact_closure_gap_review_boundary_audit.md`
""",
        encoding="utf-8",
    )

    GATE.write_text(
        """# SAEE Support Contact Closure Gap Review Gate

answer: hold_support_group_complete_pending_go_no_go_and_closure_review

reason: Support-group evidence is locally complete for review, but the broader
commercial go/no-go and a separate blocker-closure approval have not been run.
The blocker is not closed by this review.

boundary:
- blocker_closure_authorized: false
- blockers_closed_by_gap_review: 0
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

next_action: review or rerun the commercial go/no-go/profile using the combined
human-filled support evidence, then use a separate closure gate if appropriate.
""",
        encoding="utf-8",
    )

    for line in [
        "/phase_b_product/commercial_readiness/SUPPORT_CONTACT_CLOSURE_GAP_REVIEW_V0_1.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_closure_gap_review.local.json",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_closure_gap_review.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_closure_gap_review.csv",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_closure_gap_review_boundary_audit.md",
        "/docs/strategy/SAEE_SUPPORT_CONTACT_CLOSURE_GAP_REVIEW_GATE.md",
        "/scripts/saee_support_contact_closure_gap_review.py",
        "/scripts/saee_support_contact_closure_gap_review_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["support_contact_closure_gap_review_v0_1"] = {
        "name": "SAEE Support Contact Closure Gap Review v0.1",
        "status": payload["status"],
        "target_blocker_id": "support_contact",
        "support_contact_available_for_review": payload["support_contact_available_for_review"],
        "production_support_available": payload["production_support_available"],
        "closure_ready_for_human_final_review": False,
        "missing_evidence_item_count": payload["missing_evidence_item_count"],
        "blockers_closed_by_gap_review": 0,
        "accepted_for_blocker_closure_count": 0,
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
            "boundary_audit": rel(BOUNDARY),
            "gate": rel(GATE),
            "top_doc": rel(TOP_DOC),
            "runner": "scripts/saee_support_contact_closure_gap_review.py",
            "smoke": "scripts/saee_support_contact_closure_gap_review_smoke.py",
        },
        "make_target": "make check-support-contact-closure-gap-review",
    }
    AGENT_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    block = f"""## Support Contact Closure Gap Review v0.1

- `support_contact_closure_gap_review_v0_1`
- Status: `{payload['status']}`
- Target blocker: `support_contact`
- support_contact_available_for_review=true
- production_support_available={str(payload['production_support_available']).lower()}
- closure_ready_for_human_final_review=false
- missing_evidence_item_count={payload['missing_evidence_item_count']}
- blockers_closed_by_gap_review=0
- production_ready=false
- customer_validated=false
- private_core_exposed=false
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_SUPPORT_CONTACT_CLOSURE_GAP_REVIEW_V0_1", block)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_SUPPORT_CONTACT_CLOSURE_GAP_REVIEW: PASS "
        f"status={payload['status']} missing_evidence_item_count={payload['missing_evidence_item_count']} "
        "blockers_closed_by_gap_review=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
