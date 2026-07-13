#!/usr/bin/env python3
"""Convert an exact human approval phrase into structured approval input.

Default behavior is hold/no-write. A human-filled approval file is written only
when the caller supplies the exact narrow approval phrase through --phrase and
sets --write-human-filled.
"""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
OUT_DIR = COMMERCIAL_DIR / "matrix_update_requests"
TEMPLATE = OUT_DIR / "commercial_matrix_update_execution_approval_input.template.json"
HUMAN_FILLED = OUT_DIR / "commercial_matrix_update_execution_approval_input.human_filled.local.json"
PHRASE_INTAKE = OUT_DIR / "commercial_matrix_update_execution_approval_phrase_intake.local.json"
PHRASE_INTAKE_MD = OUT_DIR / "commercial_matrix_update_execution_approval_phrase_intake.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_PHRASE_INTAKE_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_PHRASE_INTAKE_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
]

EXACT_APPROVAL_PHRASE = (
    "批准矩阵更新执行：仅应用 review-ready markers，不关闭 blocker，不发布价格页，不启用 checkout，不声明生产可用。"
)

FALSE_FLAGS = {
    "matrix_update_executed": False,
    "canonical_gap_matrix_modified": False,
    "canonical_closure_board_modified": False,
    "blocker_closure_authorized": False,
    "blockers_closed_by_phrase_intake": 0,
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


def build_human_filled(template: dict[str, Any], reviewer: str, approval_reference: str) -> dict[str, Any]:
    data = dict(template)
    data.update(
        {
            "human_decision": "approve_matrix_update_execution_review_ready_markers_only",
            "human_reviewer": reviewer,
            "decision_date": date.today().isoformat(),
            "approval_reference": approval_reference,
            "approval_scope": "review_ready_markers_only_no_closure",
            "approve_matrix_update_execution_review_ready_markers_only": True,
            "confirm_no_blocker_closure": True,
            "confirm_no_pricing_publication": True,
            "confirm_no_checkout_enablement": True,
            "confirm_no_production_ready_claim": True,
            "confirm_no_customer_validation_claim": True,
            "confirm_no_product_launch": True,
            "notes": (
                "Human-approved narrow matrix marker update only. This approval "
                "does not authorize blocker closure, pricing publication, checkout "
                "enablement, launch, customer-validation claim, or production-ready claim."
            ),
        }
    )
    return data


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    phrase = args.phrase.strip()
    phrase_matches = phrase == EXACT_APPROVAL_PHRASE
    human_filled_written = False
    approval_reference = args.approval_reference or f"human-phrase-approval-{date.today().isoformat()}"
    if args.write_human_filled and phrase_matches:
        template = read_json(TEMPLATE)
        write_json(HUMAN_FILLED, build_human_filled(template, args.reviewer, approval_reference))
        human_filled_written = True
    status = (
        "approval_phrase_accepted_human_filled_written"
        if human_filled_written
        else "hold_exact_approval_phrase_required"
    )
    return {
        "commercial_matrix_update_execution_approval_phrase_intake_v0_1": True,
        "intake_type": "exact_phrase_to_structured_human_approval",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "exact_phrase_required": True,
        "exact_phrase": EXACT_APPROVAL_PHRASE,
        "phrase_provided": bool(phrase),
        "phrase_matches_exactly": phrase_matches,
        "write_human_filled_requested": args.write_human_filled,
        "human_filled_approval_written": human_filled_written,
        "human_filled_approval_path": rel(HUMAN_FILLED),
        "human_execution_approved_by_phrase_intake": human_filled_written,
        "ready_for_approval_validator": human_filled_written,
        "source_template": rel(TEMPLATE),
        "recommended_validator_command": "python3 scripts/saee_commercial_matrix_update_execution_approval_validator.py",
        "recommended_next_command": (
            "python3 scripts/saee_commercial_matrix_update_execution_approval_validator.py"
            if human_filled_written
            else "Re-run with --phrase EXACT_APPROVAL_PHRASE --write-human-filled only after explicit human approval."
        ),
        **FALSE_FLAGS,
    }


def write_outputs(payload: dict[str, Any]) -> None:
    write_json(PHRASE_INTAKE, payload)
    PHRASE_INTAKE_MD.write_text(
        f"""# SAEE Commercial Matrix Update Execution Approval Phrase Intake v0.1

Status: `{payload['status']}`

This local intake accepts one exact approval phrase and can convert it into the
structured human-filled approval input. Default execution is hold/no-write.

## Exact Phrase Required

`{EXACT_APPROVAL_PHRASE}`

## Current Result

- phrase_provided: `{str(payload['phrase_provided']).lower()}`
- phrase_matches_exactly: `{str(payload['phrase_matches_exactly']).lower()}`
- write_human_filled_requested: `{str(payload['write_human_filled_requested']).lower()}`
- human_filled_approval_written: `{str(payload['human_filled_approval_written']).lower()}`
- human_execution_approved_by_phrase_intake: `{str(payload['human_execution_approved_by_phrase_intake']).lower()}`
- ready_for_approval_validator: `{str(payload['ready_for_approval_validator']).lower()}`
- matrix_update_executed: `false`
- canonical_gap_matrix_modified: `false`
- blocker_closure_authorized: `false`
- blockers_closed_by_phrase_intake: `0`
- production_ready: `false`
- customer_validated: `false`

## Boundary

This phrase intake does not execute the matrix update, modify the canonical gap
matrix, close blockers, publish pricing, enable checkout, launch the product, or
claim production readiness.
""",
        encoding="utf-8",
    )
    TOP_DOC.write_text(
        """# SAEE Commercial Matrix Update Execution Approval Phrase Intake v0.1

commercial_matrix_update_execution_approval_phrase_intake_v0_1: true
status: hold_exact_approval_phrase_required

Purpose: provide a narrow, exact-phrase path for turning explicit human approval
into the structured human-filled approval input used by the approval validator.
It does not execute the matrix update and does not close blockers.

Entrypoints:

- `phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_phrase_intake.local.json`
- `phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_phrase_intake.md`
- `scripts/saee_commercial_matrix_update_execution_approval_phrase_intake.py`
- `scripts/saee_commercial_matrix_update_execution_approval_phrase_intake_smoke.py`
""",
        encoding="utf-8",
    )
    GATE.write_text(
        f"""# SAEE Commercial Matrix Update Execution Approval Phrase Intake Gate

answer: {payload['status']}

reason: The phrase intake is available as a narrow local approval-entry helper.
It does not execute matrix updates or close blockers. The current default state
requires the exact approval phrase before a human-filled approval file can be
written.

boundary:
- matrix_update_executed: false
- canonical_gap_matrix_modified: false
- blocker_closure_authorized: false
- blockers_closed_by_phrase_intake: 0
- production_ready: false
- customer_validated: false
- private_core_exposed: false

next_action: provide the exact approval phrase only if the owner explicitly
wants to create the human-filled approval input for validator review.
""",
        encoding="utf-8",
    )
    for line in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_PHRASE_INTAKE_V0_1.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_phrase_intake.local.json",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_phrase_intake.md",
        "/docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_PHRASE_INTAKE_GATE.md",
        "/scripts/saee_commercial_matrix_update_execution_approval_phrase_intake.py",
        "/scripts/saee_commercial_matrix_update_execution_approval_phrase_intake_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["commercial_matrix_update_execution_approval_phrase_intake_v0_1"] = {
        "name": "SAEE Commercial Matrix Update Execution Approval Phrase Intake v0.1",
        "status": payload["status"],
        "intake_type": payload["intake_type"],
        "exact_phrase_required": True,
        "phrase_matches_exactly": payload["phrase_matches_exactly"],
        "human_filled_approval_written": payload["human_filled_approval_written"],
        "human_execution_approved_by_phrase_intake": payload["human_execution_approved_by_phrase_intake"],
        "ready_for_approval_validator": payload["ready_for_approval_validator"],
        "matrix_update_executed": False,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_phrase_intake": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "customer_contacted": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "entrypoints": {
            "summary": rel(PHRASE_INTAKE),
            "report": rel(PHRASE_INTAKE_MD),
            "gate": rel(GATE),
            "top_doc": rel(TOP_DOC),
            "runner": "scripts/saee_commercial_matrix_update_execution_approval_phrase_intake.py",
            "smoke": "scripts/saee_commercial_matrix_update_execution_approval_phrase_intake_smoke.py",
        },
        "make_target": "make check-commercial-matrix-update-execution-approval-phrase-intake",
    }
    AGENT_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    block = f"""## Commercial Matrix Update Execution Approval Phrase Intake v0.1

- `commercial_matrix_update_execution_approval_phrase_intake_v0_1`
- Status: `{payload['status']}`
- exact_phrase_required=true
- phrase_matches_exactly={str(payload['phrase_matches_exactly']).lower()}
- human_filled_approval_written={str(payload['human_filled_approval_written']).lower()}
- human_execution_approved_by_phrase_intake={str(payload['human_execution_approved_by_phrase_intake']).lower()}
- ready_for_approval_validator={str(payload['ready_for_approval_validator']).lower()}
- matrix_update_executed=false
- canonical_gap_matrix_modified=false
- blocker_closure_authorized=false
- blockers_closed_by_phrase_intake=0
- production_ready=false
- customer_validated=false
- private_core_exposed=false
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_PHRASE_INTAKE_V0_1", block)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phrase", default="")
    parser.add_argument("--reviewer", default="张斌")
    parser.add_argument("--approval-reference", default="")
    parser.add_argument("--write-human-filled", action="store_true")
    return parser.parse_args()


def main() -> None:
    payload = build_payload(parse_args())
    write_outputs(payload)
    print(
        "SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_PHRASE_INTAKE: PASS "
        f"status={payload['status']} "
        f"human_filled_approval_written={str(payload['human_filled_approval_written']).lower()} "
        "matrix_update_executed=false blockers_closed_by_phrase_intake=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
