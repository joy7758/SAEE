#!/usr/bin/env python3
"""Prepare completion help for the support-group final closure decision.

This helper does not fill the decision template. It gives the exact recommended
human values for the already generated template, while preserving the boundary
that no matrix update, blocker closure, product launch, or production-ready
claim is authorized by the helper itself.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SUPPORT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
REQUEST_JSON = SUPPORT_DIR / "support_group_final_closure_decision_request.local.json"
VALIDATION_JSON = SUPPORT_DIR / "support_group_final_closure_decision_validation.local.json"
TEMPLATE_JSON = SUPPORT_DIR / "support_group_final_closure_decision_template.json"
OUT_JSON = SUPPORT_DIR / "support_group_final_closure_decision_completion_helper.local.json"
OUT_MD = SUPPORT_DIR / "support_group_final_closure_decision_completion_helper.md"
OUT_CSV = SUPPORT_DIR / "support_group_final_closure_decision_completion_helper.csv"
BOUNDARY = SUPPORT_DIR / "support_group_final_closure_decision_completion_helper_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/SUPPORT_GROUP_FINAL_CLOSURE_DECISION_COMPLETION_HELPER_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_SUPPORT_GROUP_FINAL_CLOSURE_DECISION_COMPLETION_HELPER_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
]

TARGET_BLOCKERS = ["support_contact", "customer_support", "sla", "on_call_rotation"]
RECOMMENDED_VALUES = {
    "human_final_decision": "approve_for_separate_matrix_update_request",
    "authorize_separate_matrix_update_request": True,
    "authorize_blocker_closure_now": False,
    "authorize_product_launch": False,
    "confirm_no_customer_validation_claim": True,
    "confirm_no_production_ready_claim": True,
}

FALSE_FLAGS = {
    "template_modified_by_helper": False,
    "human_final_decision_recorded": False,
    "separate_matrix_update_request_ready": False,
    "matrix_update_executed": False,
    "canonical_gap_matrix_modified": False,
    "canonical_closure_board_modified": False,
    "blocker_closure_authorized": False,
    "blockers_closed_by_helper": 0,
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


def build_payload() -> dict[str, Any]:
    request = read_json(REQUEST_JSON)
    validation = read_json(VALIDATION_JSON)
    template = read_json(TEMPLATE_JSON)
    template_blank = all(
        template.get(key, "") == ""
        for key in ["human_final_decision", "human_reviewer", "decision_date", "reason"]
    )
    return {
        "support_group_final_closure_decision_completion_helper_v0_1": True,
        "helper_type": "human_final_closure_decision_completion_helper_no_write",
        "status": "ready_for_human_confirmation_values_prepared",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target_blocker_group": "support",
        "target_blockers": TARGET_BLOCKERS,
        "source_request_json": rel(REQUEST_JSON),
        "source_validation_json": rel(VALIDATION_JSON),
        "source_template_json": rel(TEMPLATE_JSON),
        "source_request_status": request.get("status"),
        "source_validation_status": validation.get("status"),
        "template_blank": template_blank,
        "recommended_values": RECOMMENDED_VALUES,
        "recommended_reason": (
            "Support-group evidence is locally complete. Approve only a separate "
            "matrix update request; do not authorize immediate blocker closure or launch."
        ),
        "human_reviewer_required": True,
        "decision_date_required": True,
        "reason_required": True,
        "next_human_action": (
            "copy the recommended values into support_group_final_closure_decision_template.json "
            "with human_reviewer, decision_date, and reason, then rerun the validator"
        ),
        **FALSE_FLAGS,
    }


def write_outputs(payload: dict[str, Any]) -> None:
    write_json(OUT_JSON, payload)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        fields = ["field", "recommended_value", "required", "notes"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for field, value in payload["recommended_values"].items():
            writer.writerow(
                {
                    "field": field,
                    "recommended_value": str(value).lower() if isinstance(value, bool) else value,
                    "required": True,
                    "notes": "copy into template",
                }
            )
        for field in ["human_reviewer", "decision_date", "reason"]:
            writer.writerow(
                {
                    "field": field,
                    "recommended_value": "",
                    "required": True,
                    "notes": "must be filled by human",
                }
            )

    OUT_MD.write_text(
        f"""# SAEE Support Group Final Closure Decision Completion Helper v0.1

Status: `{payload['status']}`

This helper prepares the exact recommended human-fill values for the support
group final closure decision template. It does not modify the template.

## Recommended Values

Use these values in:

`{payload['source_template_json']}`

```json
{json.dumps(payload['recommended_values'], ensure_ascii=False, indent=2)}
```

You must also fill:

- `human_reviewer`
- `decision_date`
- `reason`

Recommended reason:

`{payload['recommended_reason']}`

## Current State

- source_request_status: `{payload['source_request_status']}`
- source_validation_status: `{payload['source_validation_status']}`
- template_blank: `{str(payload['template_blank']).lower()}`
- template_modified_by_helper: `false`
- human_final_decision_recorded: `false`
- separate_matrix_update_request_ready: `false`
- blockers_closed_by_helper: `0`

## Boundary

- matrix_update_executed=false
- canonical_gap_matrix_modified=false
- blocker_closure_authorized=false
- blockers_closed_by_helper=0
- production_ready=false
- customer_validated=false
- product_launched=false
- private_core_exposed=false
""",
        encoding="utf-8",
    )

    BOUNDARY.write_text(
        """# SAEE Support Group Final Closure Decision Completion Helper Boundary Audit

support_group_final_closure_decision_completion_helper_v0_1: true
status: ready_for_human_confirmation_values_prepared

- Completion helper only.
- Template not modified by helper.
- No human final decision recorded.
- No matrix update executed.
- No canonical gap matrix modified.
- No blocker closure authorized.
- No blockers closed.
- No runtime modified.
- No backend modified.
- No kernel modified.
- No API schema modified.
- No private core exposed.
- No product launched.
- No customer contacted.
- No production-ready claim added.
- No customer-validation claim added.
- blockers_closed_by_helper: 0
""",
        encoding="utf-8",
    )

    TOP_DOC.write_text(
        """# SAEE Support Group Final Closure Decision Completion Helper v0.1

support_group_final_closure_decision_completion_helper_v0_1: true
status: ready_for_human_confirmation_values_prepared

Purpose: reduce the support-group final closure decision to explicit
human-fill values without writing the template or executing closure.

Entrypoints:

- `phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_completion_helper.local.json`
- `phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_completion_helper.md`
- `phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_completion_helper.csv`
- `phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_completion_helper_boundary_audit.md`
""",
        encoding="utf-8",
    )

    GATE.write_text(
        """# SAEE Support Group Final Closure Decision Completion Helper Gate

answer: ready_for_human_confirmation_values_prepared

reason: Recommended human-fill values are prepared for the support-group final
closure decision template. The helper did not write the template, record a
decision, update the matrix, or close blockers.

boundary:
- template_modified_by_helper: false
- human_final_decision_recorded: false
- matrix_update_executed: false
- blocker_closure_authorized: false
- blockers_closed_by_helper: 0
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

next_action: human confirms the recommended values and fills the decision
template, then reruns the validator.
""",
        encoding="utf-8",
    )

    for line in [
        "/phase_b_product/commercial_readiness/SUPPORT_GROUP_FINAL_CLOSURE_DECISION_COMPLETION_HELPER_V0_1.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_completion_helper.local.json",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_completion_helper.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_completion_helper.csv",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_completion_helper_boundary_audit.md",
        "/docs/strategy/SAEE_SUPPORT_GROUP_FINAL_CLOSURE_DECISION_COMPLETION_HELPER_GATE.md",
        "/scripts/saee_support_group_final_closure_decision_completion_helper.py",
        "/scripts/saee_support_group_final_closure_decision_completion_helper_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["support_group_final_closure_decision_completion_helper_v0_1"] = {
        "name": "SAEE Support Group Final Closure Decision Completion Helper v0.1",
        "status": payload["status"],
        "target_blocker_group": "support",
        "target_blockers": TARGET_BLOCKERS,
        "template_blank": payload["template_blank"],
        "template_modified_by_helper": False,
        "human_final_decision_recorded": False,
        "separate_matrix_update_request_ready": False,
        "matrix_update_executed": False,
        "canonical_gap_matrix_modified": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_helper": 0,
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
            "boundary_audit": rel(BOUNDARY),
            "gate": rel(GATE),
            "top_doc": rel(TOP_DOC),
            "runner": "scripts/saee_support_group_final_closure_decision_completion_helper.py",
            "smoke": "scripts/saee_support_group_final_closure_decision_completion_helper_smoke.py",
        },
        "make_target": "make check-support-group-final-closure-decision-completion-helper",
    }
    AGENT_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    block = f"""## Support Group Final Closure Decision Completion Helper v0.1

- `support_group_final_closure_decision_completion_helper_v0_1`
- Status: `{payload['status']}`
- Target blockers: `support_contact`, `customer_support`, `sla`, `on_call_rotation`
- recommended_human_final_decision=approve_for_separate_matrix_update_request
- template_modified_by_helper=false
- human_final_decision_recorded=false
- separate_matrix_update_request_ready=false
- blockers_closed_by_helper=0
- production_ready=false
- customer_validated=false
- private_core_exposed=false
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_SUPPORT_GROUP_FINAL_CLOSURE_DECISION_COMPLETION_HELPER_V0_1", block)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_SUPPORT_GROUP_FINAL_CLOSURE_DECISION_COMPLETION_HELPER: PASS "
        f"status={payload['status']} template_blank={str(payload['template_blank']).lower()} "
        "template_modified_by_helper=false blockers_closed_by_helper=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
