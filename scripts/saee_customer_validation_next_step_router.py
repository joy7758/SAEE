#!/usr/bin/env python3
"""Route the next local customer-validation step.

This is a read-only navigation helper. It checks whether the human answer
sheet and final session-entry JSON exist, then writes a local next-step report.
It does not contact customers, fill answers, run importers, run processors,
close blockers, or claim production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
OUT = EVIDENCE / "customer_validation_next_step_router"
SUMMARY = OUT / "customer_validation_next_step_router.local.json"
REPORT = OUT / "customer_validation_next_step_router.md"
BOUNDARY = OUT / "customer_validation_next_step_router_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_NEXT_STEP_ROUTER_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
]

ONE_PAGE_CARD = EVIDENCE / "customer_validation_one_page_run_card/customer_validation_one_page_run_card.md"
MINIMUM_SESSION_FORM = (
    EVIDENCE / "external_customer_validation_minimum_session_packet/minimum_session_form.html"
)
MINIMUM_SESSION_QUESTIONS = (
    EVIDENCE / "external_customer_validation_minimum_session_packet/MINIMUM_SESSION_QUESTIONS.md"
)
MINIMUM_ANSWER_TEMPLATE = (
    EVIDENCE
    / "external_customer_validation_minimum_session_answer_converter/minimum_session_answers.template.md"
)
MINIMUM_ANSWER_INPUT = (
    EVIDENCE
    / "external_customer_validation_minimum_session_answer_converter/minimum_session_answers.human_filled.md"
)
MINIMUM_ANSWER_CONVERTER_SUMMARY = (
    EVIDENCE
    / "external_customer_validation_minimum_session_answer_converter/minimum_session_answer_converter.local.json"
)
PREFLIGHT_SUMMARY = EVIDENCE / "customer_validation_answer_sheet_preflight/customer_validation_answer_sheet_preflight.local.json"
TARGET_ENTRY = EVIDENCE / "external_customer_validation_session_entry.human_filled.local.json"
POST_SESSION_SUMMARY = (
    EVIDENCE
    / "external_customer_validation_post_session_processor/external_customer_validation_post_session_processor.local.json"
)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def route(answer_exists: bool, target_exists: bool) -> dict[str, str]:
    if target_exists:
        return {
            "status": "ready_for_post_session_processor",
            "next_action": "Run the local post-session processor, then review outputs before any go/no-go update.",
            "next_command": "python3 scripts/saee_external_customer_validation_post_session_processor.py",
        }
    if answer_exists:
        return {
            "status": "ready_for_minimum_answer_converter_apply_request",
            "next_action": "Run the 12-question minimum answer converter with explicit --apply, then run the post-session processor.",
            "next_command": "python3 scripts/saee_external_customer_validation_minimum_session_answer_converter.py --apply",
        }
    return {
        "status": "waiting_for_real_external_customer_session",
        "next_action": "Open the locked 12-question minimum session form, or fill the 12-question Markdown answer template after a real external customer or target-user conversation.",
        "next_command": "open phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/minimum_session_form.html",
    }


def build_payload() -> dict[str, Any]:
    preflight = read_json(PREFLIGHT_SUMMARY)
    answer_exists = MINIMUM_ANSWER_INPUT.exists()
    target_exists = TARGET_ENTRY.exists()
    post_session_exists = POST_SESSION_SUMMARY.exists()
    converter_summary = read_json(MINIMUM_ANSWER_CONVERTER_SUMMARY) if MINIMUM_ANSWER_CONVERTER_SUMMARY.exists() else {}
    decision = route(answer_exists, target_exists)
    return {
        "customer_validation_next_step_router_v0_1": True,
        "router_type": "local_read_only_customer_validation_next_step_router",
        "status": decision["status"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_goal_blocker": "customer_validated",
        "recommended_path_locked": True,
        "recommended_path_id": "minimum_session_packet",
        "recommended_form": rel(MINIMUM_SESSION_FORM),
        "recommended_questions": rel(MINIMUM_SESSION_QUESTIONS),
        "recommended_text_answer_template": rel(MINIMUM_ANSWER_TEMPLATE),
        "recommended_text_answer_input": rel(MINIMUM_ANSWER_INPUT),
        "minimum_answer_converter_summary": rel(MINIMUM_ANSWER_CONVERTER_SUMMARY),
        "minimum_answer_converter_status": converter_summary.get("status", "not_run"),
        "reference_one_page_run_card": rel(ONE_PAGE_CARD),
        "one_page_run_card": rel(ONE_PAGE_CARD),
        "human_answer_input": rel(MINIMUM_ANSWER_INPUT),
        "human_answer_input_exists": answer_exists,
        "target_session_entry": rel(TARGET_ENTRY),
        "target_session_entry_exists": target_exists,
        "preflight_summary": rel(PREFLIGHT_SUMMARY),
        "current_preflight_status": preflight.get("status"),
        "current_preflight_missing_field_count": preflight.get("missing_field_count"),
        "ready_for_explicit_apply_request": preflight.get("ready_for_explicit_apply_request") is True,
        "post_session_summary": rel(POST_SESSION_SUMMARY),
        "post_session_summary_exists": post_session_exists,
        "next_action": decision["next_action"],
        "next_command": decision["next_command"],
        "customer_validated": False,
        "production_ready": False,
        "product_launched": False,
        "customer_contacted_by_codex": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "public_sdk_released": False,
        "blockers_closed_by_router": 0,
    }


def write_outputs(payload: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(SUMMARY, payload)

    REPORT.write_text(
        f"""# SAEE Customer Validation Next Step Router v0.1

Status: `{payload["status"]}`

This is a local read-only routing report. It only tells the human what to do
next for the remaining `customer_validated` blocker.

## Current Inputs

- Recommended form: `{payload["recommended_form"]}`
- Recommended questions: `{payload["recommended_questions"]}`
- Recommended 12-question text template: `{payload["recommended_text_answer_template"]}`
- Recommended 12-question text input: `{payload["recommended_text_answer_input"]}`
- Minimum answer converter status: `{payload["minimum_answer_converter_status"]}`
- Reference-only one-page run card: `{payload["reference_one_page_run_card"]}`
- Human answer sheet exists: `{payload["human_answer_input_exists"]}`
- Final session-entry JSON exists: `{payload["target_session_entry_exists"]}`
- Current preflight status: `{payload["current_preflight_status"]}`
- Current missing field count: `{payload["current_preflight_missing_field_count"]}`
- Ready for explicit apply request: `{payload["ready_for_explicit_apply_request"]}`

## Next Action

{payload["next_action"]}

Suggested local command:

```bash
{payload["next_command"]}
```

## Boundary

- customer_validated: false
- production_ready: false
- product_launched: false
- customer_contacted_by_codex: false
- private_core_exposed: false
- recommended_path_locked: true
- recommended_path_id: minimum_session_packet
- blockers_closed_by_router: 0
""",
        encoding="utf-8",
    )

    BOUNDARY.write_text(
        """# SAEE Customer Validation Next Step Router Boundary Audit

- Read-only local routing report only.
- No customer was contacted by Codex.
- No external calls were made.
- No answer sheet was created or filled.
- No final session-entry JSON was written.
- No importer, processor, validator, or evidence builder was run by this router.
- No customer-validation claim was made.
- No production-ready claim was made.
- No runtime, backend, kernel, API schema, landing interaction, or private core was modified.

customer_validation_next_step_router_v0_1: true
recommended_path_locked: true
recommended_path_id: minimum_session_packet
customer_validated: false
production_ready: false
product_launched: false
private_core_exposed: false
blockers_closed_by_router: 0
""",
        encoding="utf-8",
    )

    GATE.write_text(
        """# SAEE Customer Validation Next Step Router Gate

answer: local_next_step_route_ready

reason: The remaining customer-validation blocker now has a local read-only
router that points the human to the correct next action based on whether the
answer sheet or final session-entry JSON exists.

boundary:
- recommended_path_locked: true
- recommended_path_id: minimum_session_packet
- customer_validated: false
- production_ready: false
- product_launched: false
- customer_contacted_by_codex: false
- private_core_exposed: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- blockers_closed_by_router: 0

next_action: Follow the router output. Real customer or target-user input is
still required before customer validation can proceed.
""",
        encoding="utf-8",
    )


def update_indexes(payload: dict[str, Any]) -> None:
    for line in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_next_step_router/customer_validation_next_step_router.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_next_step_router/customer_validation_next_step_router.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_next_step_router/customer_validation_next_step_router_boundary_audit.md",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_NEXT_STEP_ROUTER_GATE.md",
        "/scripts/saee_customer_validation_next_step_router.py",
        "/scripts/saee_customer_validation_next_step_router_smoke.py",
    ]:
        ensure_line(LLMS, line)

    agent_index = read_json(AGENT_INDEX)
    agent_index["customer_validation_next_step_router_v0_1"] = {
        "name": "SAEE Customer Validation Next Step Router v0.1",
        "status": payload["status"],
        "current_goal_blocker": payload["current_goal_blocker"],
        "recommended_path_locked": payload["recommended_path_locked"],
        "recommended_path_id": payload["recommended_path_id"],
        "recommended_form": payload["recommended_form"],
        "recommended_questions": payload["recommended_questions"],
        "recommended_text_answer_template": payload["recommended_text_answer_template"],
        "recommended_text_answer_input": payload["recommended_text_answer_input"],
        "minimum_answer_converter_summary": payload["minimum_answer_converter_summary"],
        "minimum_answer_converter_status": payload["minimum_answer_converter_status"],
        "reference_one_page_run_card": payload["reference_one_page_run_card"],
        "human_answer_input_exists": payload["human_answer_input_exists"],
        "target_session_entry_exists": payload["target_session_entry_exists"],
        "current_preflight_status": payload["current_preflight_status"],
        "current_preflight_missing_field_count": payload["current_preflight_missing_field_count"],
        "ready_for_explicit_apply_request": payload["ready_for_explicit_apply_request"],
        "next_action": payload["next_action"],
        "next_command": payload["next_command"],
        "customer_validated": payload["customer_validated"],
        "production_ready": payload["production_ready"],
        "product_launched": payload["product_launched"],
        "customer_contacted_by_codex": payload["customer_contacted_by_codex"],
        "private_core_exposed": payload["private_core_exposed"],
        "runtime_modified": payload["runtime_modified"],
        "backend_modified": payload["backend_modified"],
        "kernel_modified": payload["kernel_modified"],
        "api_schema_modified": payload["api_schema_modified"],
        "external_calls_made": payload["external_calls_made"],
        "blockers_closed_by_router": payload["blockers_closed_by_router"],
        "entrypoints": {
            "summary": rel(SUMMARY),
            "report": rel(REPORT),
            "boundary_audit": rel(BOUNDARY),
            "gate": rel(GATE),
            "runner": "scripts/saee_customer_validation_next_step_router.py",
            "smoke": "scripts/saee_customer_validation_next_step_router_smoke.py",
        },
    }
    write_json(AGENT_INDEX, agent_index)

    status_block = f"""## SAEE Customer Validation Next Step Router v0.1

- `customer_validation_next_step_router_v0_1`
- Status: `{payload["status"]}`
- Current blocker: `customer_validated`
- Report: `{rel(REPORT)}`
- Recommended form: `{payload["recommended_form"]}`
- Recommended questions: `{payload["recommended_questions"]}`
- Recommended 12-question text template: `{payload["recommended_text_answer_template"]}`
- Next command: `{payload["next_command"]}`
- `customer_validated=false`
- `production_ready=false`
- `private_core_exposed=false`
- `blockers_closed_by_router=0`
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_CUSTOMER_VALIDATION_NEXT_STEP_ROUTER_V0_1", status_block)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    update_indexes(payload)
    print(
        "SAEE_CUSTOMER_VALIDATION_NEXT_STEP_ROUTER: PASS "
        f"status={payload['status']} customer_validated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
