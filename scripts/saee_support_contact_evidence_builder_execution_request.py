#!/usr/bin/env python3
"""Record and execute the approved local support-contact evidence-builder request.

This is a narrow commercial-readiness evidence step for ERD-001. It converts the
already human-filled support-contact decision input into local evidence outputs.
It does not publish a support contact, contact customers or vendors, close
commercial blockers, modify runtime/backend/kernel/API schema, or claim
production readiness.
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_support_contact_evidence_builder import build_from_input


SUPPORT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
NEXT_SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"

ERD_APPROVAL_VALIDATION = NEXT_SPRINT_DIR / "evidence_request_approval_input_validation.local.json"
SUPPORT_APPROVAL_VALIDATION = SUPPORT_DIR / "support_contact_approval_input_validation.local.json"
REQUEST_TEMPLATE = SUPPORT_DIR / "support_contact_evidence_builder_request.template.json"
HUMAN_INPUT = SUPPORT_DIR / "support_contact_decision_input.human_filled.local.json"
BUILDER_OUTPUT = SUPPORT_DIR / "support_contact_evidence_builder_output.human_filled.local.json"
SUPPORT_OUTPUT = SUPPORT_DIR / "production_support_sla_evidence.from_support_contact.human_filled.local.json"

REQUEST_OUTPUT = SUPPORT_DIR / "support_contact_evidence_builder_execution_request.local.json"
REQUEST_REPORT = SUPPORT_DIR / "support_contact_evidence_builder_execution_request.md"
BOUNDARY_AUDIT = SUPPORT_DIR / "support_contact_evidence_builder_execution_request_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_SUPPORT_CONTACT_EVIDENCE_BUILDER_EXECUTION_REQUEST_GATE.md"

REQUEST_ID = "ERD-001-support-contact-evidence-builder-request-2026-07-09"
HUMAN_CONFIRMATION_REFERENCE = "human-confirmed-manual-check-no-issues-2026-07-09"


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{path} must contain a JSON object")
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_SUPPORT_CONTACT_EVIDENCE_BUILDER_EXECUTION_REQUEST: FAIL: " + message)


def validate_prerequisites() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    for path in [ERD_APPROVAL_VALIDATION, SUPPORT_APPROVAL_VALIDATION, REQUEST_TEMPLATE, HUMAN_INPUT]:
        require(path.exists(), f"missing prerequisite {rel(path)}")

    erd_validation = read_json(ERD_APPROVAL_VALIDATION)
    support_validation = read_json(SUPPORT_APPROVAL_VALIDATION)
    request_template = read_json(REQUEST_TEMPLATE)

    require(erd_validation.get("status") == "pass", "ERD approval input validation must pass")
    require(
        "ERD-001" in erd_validation.get("approved_request_ids", []),
        "ERD approval input must approve ERD-001",
    )
    require(
        erd_validation.get("ready_for_separate_execution_request") is True,
        "ERD-001 must be ready for a separate execution request",
    )
    require(
        support_validation.get("validation_status") == "pass",
        "support-contact approval input validation must pass",
    )
    require(support_validation.get("builder_ready") is True, "support-contact builder must be ready")
    require(
        request_template.get("template_type") == "saee_support_contact_evidence_builder_request",
        "support-contact builder request template type mismatch",
    )
    return erd_validation, support_validation, request_template


def boundary_flags() -> dict[str, bool]:
    return {
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "landing_page_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "customer_contacted": False,
        "customer_contacted_by_codex": False,
        "support_vendor_contacted": False,
        "support_vendor_contacted_by_codex": False,
        "support_contact_published": False,
        "support_contact_published_by_codex": False,
        "support_contact_test_performed": False,
        "support_contact_test_sent_by_codex": False,
        "customer_facing_support_contact_configured": False,
        "customer_support_available": False,
        "production_support_available": False,
        "support_process_available": False,
        "sla_available": False,
        "on_call_rotation_available": False,
        "development_permission_granted": False,
        "production_ready": False,
        "customer_validated": False,
        "public_sdk_released": False,
        "external_calls_made_by_codex": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "blocker_closure_authorized": False,
    }


def build_payload(summary: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "support_contact_evidence_builder_execution_request_v0_1": True,
        "request_id": REQUEST_ID,
        "source_request_id": "ERD-001",
        "status": "local_evidence_builder_executed_pending_closure_review",
        "request_scope": "local_support_contact_evidence_builder_execution_only",
        "target_blocker_id": "support_contact",
        "target_builder": "scripts/saee_support_contact_evidence_builder.py",
        "human_requester_name": "张斌",
        "request_date": date.today().isoformat(),
        "human_confirmation_reference": HUMAN_CONFIRMATION_REFERENCE,
        "source_erd_approval_validation": rel(ERD_APPROVAL_VALIDATION),
        "source_support_contact_approval_validation": rel(SUPPORT_APPROVAL_VALIDATION),
        "source_request_template": rel(REQUEST_TEMPLATE),
        "validated_input_path": rel(HUMAN_INPUT),
        "builder_output": rel(BUILDER_OUTPUT),
        "support_evidence_output": rel(SUPPORT_OUTPUT),
        "request_approved": True,
        "approval_input_validator_passed": True,
        "human_filled_input_available": True,
        "evidence_builder_execution_authorized": True,
        "evidence_builder_executed": True,
        "support_evidence_output_created_by_request": True,
        "builder_status": summary.get("status"),
        "builder_input_complete": summary.get("input_complete"),
        "support_contact_available_for_review": summary.get("support_contact_available_for_review"),
        "production_support_available": False,
        "blockers_closed_by_request": 0,
        "blockers_closed_by_builder": summary.get("blockers_closed_by_builder", 0),
        "accepted_for_blocker_closure_count": summary.get("accepted_for_blocker_closure_count", 0),
        "human_review_required_for_closure": True,
        "separate_closure_approval_required": True,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_support_contact_evidence_builder_execution_request.py",
        "next_action": (
            "Use the human-filled support-contact builder output only in a separate "
            "human closure-review gate. Customer support process, SLA, and on-call "
            "evidence remain unresolved."
        ),
    }
    payload.update(boundary_flags())
    return payload


def write_report(payload: dict[str, Any]) -> None:
    REQUEST_REPORT.write_text(
        f"""# SAEE Support Contact Evidence Builder Execution Request

Status: {payload['status']}.

This record captures the human-confirmed local execution request for ERD-001.
It authorizes and records only a local support-contact evidence-builder run from
the already human-filled input. It does not publish a support contact, send
support messages, contact customers or vendors, close blockers, launch product,
or claim production readiness.

## Summary

- request_id: {payload['request_id']}
- source_request_id: ERD-001
- target_blocker_id: support_contact
- target_builder: `{payload['target_builder']}`
- request_approved: true
- evidence_builder_execution_authorized: true
- evidence_builder_executed: true
- builder_status: {payload['builder_status']}
- builder_input_complete: {str(payload['builder_input_complete']).lower()}
- support_contact_available_for_review: {str(payload['support_contact_available_for_review']).lower()}
- production_support_available: false
- blockers_closed_by_request: 0
- blockers_closed_by_builder: 0

## Boundary

- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- product_launched: false
- customer_contacted: false
- support_vendor_contacted: false
- support_contact_published_by_codex: false
- support_contact_test_sent_by_codex: false
- production_ready: false
- customer_validated: false

## Next Action

The output may be reviewed in a separate human blocker-closure gate. This
request itself closes no blockers.
""",
        encoding="utf-8",
    )
    BOUNDARY_AUDIT.write_text(
        """# SAEE Support Contact Evidence Builder Execution Boundary Audit

- Only local support-contact evidence-builder output was generated.
- No runtime modified.
- No backend modified.
- No kernel modified.
- No API schema modified.
- No landing page modified.
- No private core exposed.
- No support contact published by Codex.
- No support-contact test sent by Codex.
- No customer contacted.
- No support vendor contacted.
- No product launched.
- No public SDK released.
- No production-ready claim added.
- No blocker closed by this request.
""",
        encoding="utf-8",
    )
    GATE.parent.mkdir(parents=True, exist_ok=True)
    GATE.write_text(
        """# SAEE Support Contact Evidence Builder Execution Request Gate

answer: local_evidence_builder_execution_recorded_pending_closure_review

reason:
ERD-001 was approved for a separate local support-contact evidence-builder
execution request, and the builder was run against the human-filled local input.
This produces reviewable local evidence only.

boundary:
development_permission_granted: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
private_core_exposed: false
product_launched: false
customer_contacted: false
support_vendor_contacted: false
production_ready: false
blockers_closed_by_request: 0

next_action:
Use this output only in a separate human blocker-closure review. Customer
support process, SLA, and on-call evidence remain unresolved.
""",
        encoding="utf-8",
    )


def main() -> None:
    validate_prerequisites()
    summary = build_from_input(
        HUMAN_INPUT,
        BUILDER_OUTPUT,
        SUPPORT_OUTPUT,
        write_documentation=False,
    )
    require(summary.get("status") == "pass", "human-filled support-contact builder output must pass")
    require(summary.get("input_complete") is True, "human-filled builder input must be complete")
    require(
        summary.get("support_contact_available_for_review") is True,
        "support contact must be available for review",
    )
    require(
        summary.get("production_support_available") is False,
        "support-contact evidence alone must not imply production support",
    )
    require(summary.get("blockers_closed_by_builder") == 0, "builder must close no blockers")

    payload = build_payload(summary)
    write_json(REQUEST_OUTPUT, payload)
    write_report(payload)
    print(
        "SAEE_SUPPORT_CONTACT_EVIDENCE_BUILDER_EXECUTION_REQUEST: PASS "
        f"status={payload['status']} request_id={REQUEST_ID} "
        "blockers_closed_by_request=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
