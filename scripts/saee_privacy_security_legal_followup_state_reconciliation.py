#!/usr/bin/env python3
"""Reconcile privacy/security/legal evidence without enabling production claims.

This local surface records that human-filled evidence for formal security
review, privacy/legal review, data processing agreement, and vulnerability
management is ready for human review through the combined privacy/security/legal
profile. It does not perform security review, publish legal documents, process
customer data, activate vulnerability operations, close blockers, or claim
production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
EVIDENCE_DIR = COMMERCIAL_DIR / "privacy_security_legal_evidence"
OUT_DIR = EVIDENCE_DIR / "privacy_security_legal_followup_state_reconciliation"
OUT_JSON = OUT_DIR / "privacy_security_legal_followup_state_reconciliation.local.json"
OUT_MD = OUT_DIR / "privacy_security_legal_followup_state_reconciliation.md"
BOUNDARY = OUT_DIR / "privacy_security_legal_followup_state_reconciliation_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "PRIVACY_SECURITY_LEGAL_FOLLOWUP_STATE_RECONCILIATION_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_PRIVACY_SECURITY_LEGAL_FOLLOWUP_STATE_RECONCILIATION_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
]

TARGETS = [
    "formal_security_review",
    "privacy_legal_review",
    "data_processing_agreement",
    "vulnerability_management",
]

SOURCES = {
    "formal_security_review_validation": EVIDENCE_DIR
    / "formal_security_review_approval_input_validation.human_filled.local.json",
    "formal_security_review_builder": EVIDENCE_DIR
    / "formal_security_review_evidence_builder_output.human_filled.local.json",
    "formal_security_review_evidence": EVIDENCE_DIR
    / "production_privacy_security_legal_evidence.from_formal_security_review.human_filled.local.json",
    "privacy_legal_dpa_validation": EVIDENCE_DIR
    / "privacy_legal_dpa_approval_input_validation.human_filled.local.json",
    "privacy_legal_dpa_builder": EVIDENCE_DIR
    / "privacy_legal_dpa_evidence_builder_output.human_filled.local.json",
    "privacy_legal_dpa_evidence": EVIDENCE_DIR
    / "production_privacy_security_legal_evidence.from_privacy_legal_dpa.human_filled.local.json",
    "vulnerability_management_validation": EVIDENCE_DIR
    / "vulnerability_management_approval_input_validation.human_filled.local.json",
    "vulnerability_management_builder": EVIDENCE_DIR
    / "vulnerability_management_evidence_builder_output.human_filled.local.json",
    "vulnerability_management_evidence": EVIDENCE_DIR
    / "production_privacy_security_legal_evidence.from_vulnerability_management.human_filled.local.json",
    "combined_privacy_security_legal_profile": EVIDENCE_DIR
    / "privacy_security_legal_evidence_profile.from_formal_privacy_dpa_vulnerability_human_filled.local.json",
    "combined_privacy_security_legal_evidence": EVIDENCE_DIR
    / "production_privacy_security_legal_evidence.combined_from_formal_privacy_dpa_vulnerability_human_filled.local.json",
    "gap_matrix": COMMERCIAL_DIR / "production_blocker_gap_matrix/gap_matrix.local.json",
    "closure_readiness_board": COMMERCIAL_DIR
    / "commercial_blocker_closure_readiness_board/closure_readiness_board.local.json",
}

FALSE_FLAGS = {
    "formal_security_review_completed_by_codex": False,
    "codex_performed_security_review": False,
    "codex_inspected_private_core": False,
    "codex_contacted_security_reviewer": False,
    "codex_contacted_vendor": False,
    "security_vendor_contacted": False,
    "security_review_claim_published": False,
    "production_security_claim_published": False,
    "production_security_enabled": False,
    "privacy_legal_review_completed_by_codex": False,
    "codex_performed_legal_review": False,
    "codex_contacted_legal_counsel": False,
    "legal_counsel_contacted": False,
    "privacy_notice_published": False,
    "codex_created_dpa": False,
    "codex_approved_dpa": False,
    "dpa_sent_to_customer": False,
    "customer_data_processed": False,
    "customer_data_processing_started": False,
    "codex_processed_customer_data": False,
    "codex_activated_vulnerability_management": False,
    "codex_published_security_contact": False,
    "codex_ran_vulnerability_scan": False,
    "codex_contacted_security_reporter": False,
    "codex_contacted_security_vendor": False,
    "security_contact_published": False,
    "vulnerability_management_operational": False,
    "vulnerability_management_completed_by_codex": False,
    "vulnerability_management_claim_published": False,
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
    "external_ai_assistant_tested": False,
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
    data = {name: read_json(path) for name, path in SOURCES.items()}
    profile = data["combined_privacy_security_legal_profile"]
    gap = data["gap_matrix"]
    board = data["closure_readiness_board"]

    formal_security_ready = (
        data["formal_security_review_validation"].get("validation_status") == "pass"
        and data["formal_security_review_validation"].get("input_complete") is True
        and data["formal_security_review_validation"].get("builder_ready") is True
        and data["formal_security_review_builder"].get("status") == "pass"
        and data["formal_security_review_builder"].get("formal_security_review_completed_for_review") is True
        and data["formal_security_review_evidence"].get("formal_security_review_report") is True
        and data["formal_security_review_evidence"].get("private_core_non_exposure_review_completed") is True
        and data["formal_security_review_evidence"].get("codex_performed_security_review") is False
    )
    privacy_legal_ready = (
        data["privacy_legal_dpa_validation"].get("validation_status") == "pass"
        and data["privacy_legal_dpa_validation"].get("input_complete") is True
        and data["privacy_legal_dpa_validation"].get("builder_ready") is True
        and data["privacy_legal_dpa_builder"].get("status") == "pass"
        and data["privacy_legal_dpa_builder"].get("privacy_legal_review_completed_for_review") is True
        and data["privacy_legal_dpa_evidence"].get("privacy_notice_approved") is True
        and data["privacy_legal_dpa_evidence"].get("terms_of_service_approved") is True
        and data["privacy_legal_dpa_evidence"].get("legal_counsel_contacted") is False
    )
    dpa_ready = (
        data["privacy_legal_dpa_validation"].get("validation_status") == "pass"
        and data["privacy_legal_dpa_evidence"].get("customer_dpa_template_available") is True
        and data["privacy_legal_dpa_evidence"].get("dpa_terms_approved") is True
        and data["privacy_legal_dpa_evidence"].get("dpa_sent_to_customer") is False
        and data["privacy_legal_dpa_evidence"].get("customer_data_processed") is False
    )
    vulnerability_ready = (
        data["vulnerability_management_validation"].get("validation_status") == "pass"
        and data["vulnerability_management_validation"].get("input_complete") is True
        and data["vulnerability_management_validation"].get("builder_ready") is True
        and data["vulnerability_management_builder"].get("status") == "pass"
        and data["vulnerability_management_builder"].get("vulnerability_management_available_for_review") is True
        and data["vulnerability_management_evidence"].get("vulnerability_case_dry_run_recorded") is True
        and data["vulnerability_management_evidence"].get("vulnerability_management_operational") is False
    )
    profile_ready = (
        profile.get("profile_status") == "pass"
        and profile.get("privacy_security_legal_readiness_status") == "pass"
        and profile.get("privacy_security_legal_target_blockers_satisfied_count") == 4
        and profile.get("production_ready") is False
        and profile.get("production_launch_status_after_profile") == "hold"
    )
    readiness = {
        "formal_security_review": formal_security_ready,
        "privacy_legal_review": privacy_legal_ready,
        "data_processing_agreement": dpa_ready,
        "vulnerability_management": vulnerability_ready,
    }
    all_ready = all(readiness.values()) and profile_ready
    any_ready = any(readiness.values())

    gap_open = {bid: find_row(gap, bid).get("status") == "open" for bid in TARGETS}
    board_not_ready = {
        bid: find_row(board, bid).get("status") in {"not_ready", None, ""} for bid in TARGETS
    }

    if all_ready:
        status = "ready_for_human_privacy_security_legal_review_no_closure"
        resolved_path = "combined_privacy_security_legal_profile"
        next_action = (
            "Human privacy/security/legal owner may review the combined evidence "
            "for a later matrix update request. Do not perform security review, "
            "publish privacy or DPA documents, activate vulnerability operations, "
            "process customer data, close blockers, or claim production readiness."
        )
    elif any_ready:
        status = "partial_privacy_security_legal_review_ready_no_closure"
        resolved_path = "individual_human_filled_evidence_outputs"
        next_action = "Review ready privacy/security/legal evidence only; no closure or production enablement is allowed."
    else:
        status = "hold_privacy_security_legal_human_input_required"
        resolved_path = "approval_input_validation"
        next_action = "Complete human-filled privacy/security/legal input before follow-up review."

    payload: dict[str, Any] = {
        "privacy_security_legal_followup_state_reconciliation_v0_1": True,
        "reconciliation_type": "local_privacy_security_legal_followup_state_reconciliation_no_security_review_no_legal_publication_no_closure",
        "target_blocker_ids": TARGETS,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "resolved_current_path": resolved_path,
        "formal_security_review_ready_for_review": formal_security_ready,
        "privacy_legal_review_ready_for_review": privacy_legal_ready,
        "data_processing_agreement_ready_for_review": dpa_ready,
        "vulnerability_management_ready_for_review": vulnerability_ready,
        "combined_privacy_security_legal_profile_ready": profile_ready,
        "ready_for_review_count": sum(1 for value in readiness.values() if value),
        "privacy_security_legal_target_blockers_satisfied_count": profile.get(
            "privacy_security_legal_target_blockers_satisfied_count"
        ),
        "privacy_security_legal_satisfied_blockers": profile.get("privacy_security_legal_satisfied_blockers", []),
        "support_data_ops_operations_privacy_security_legal_unsatisfied_blockers": profile.get(
            "support_data_ops_operations_privacy_security_legal_unsatisfied_blockers", []
        ),
        "gap_matrix_open_by_blocker": gap_open,
        "closure_board_not_ready_by_blocker": board_not_ready,
        "source_paths": {name: rel(path) for name, path in SOURCES.items()},
        "human_review_required": True,
        "separate_matrix_update_request_required": True,
        "next_human_action": next_action,
        "why_this_exists": (
            "Human-filled privacy/security/legal evidence can satisfy local review "
            "criteria while canonical blocker surfaces remain open. This file records "
            "review readiness without performing legal/security operations or closing blockers."
        ),
    }
    payload.update(FALSE_FLAGS)
    return payload


def write_outputs(payload: dict[str, Any]) -> None:
    write_json(OUT_JSON, payload)
    OUT_MD.write_text(
        f"""# SAEE Privacy/Security/Legal Follow-up State Reconciliation v0.1

Status: `{payload['status']}`

This local board reconciles privacy/security/legal follow-up evidence for
`formal_security_review`, `privacy_legal_review`, `data_processing_agreement`,
and `vulnerability_management`. It does not perform security review, publish
privacy or legal documents, process customer data, activate vulnerability
operations, close blockers, or claim production readiness.

## Current Finding

- target_blocker_ids: `formal_security_review`, `privacy_legal_review`, `data_processing_agreement`, `vulnerability_management`
- formal_security_review_ready_for_review: `{str(payload['formal_security_review_ready_for_review']).lower()}`
- privacy_legal_review_ready_for_review: `{str(payload['privacy_legal_review_ready_for_review']).lower()}`
- data_processing_agreement_ready_for_review: `{str(payload['data_processing_agreement_ready_for_review']).lower()}`
- vulnerability_management_ready_for_review: `{str(payload['vulnerability_management_ready_for_review']).lower()}`
- combined_privacy_security_legal_profile_ready: `{str(payload['combined_privacy_security_legal_profile_ready']).lower()}`
- ready_for_review_count: `{payload['ready_for_review_count']}`
- resolved_current_path: `{payload['resolved_current_path']}`

## Next Human Action

{payload['next_human_action']}

## Boundary

- codex_performed_security_review=false
- privacy_notice_published=false
- dpa_sent_to_customer=false
- customer_data_processed=false
- vulnerability_management_operational=false
- blockers_closed_by_reconciliation=0
- production_ready=false
- customer_validated=false
- product_launched=false
- private_core_exposed=false
""",
        encoding="utf-8",
    )
    BOUNDARY.write_text(
        """# Privacy/Security/Legal Follow-up State Reconciliation Boundary Audit

- Only local status and agent-readable evidence surfaces were written.
- No security review performed by Codex.
- No private core inspected by Codex.
- No security vendor or reviewer contacted by Codex.
- No legal counsel contacted by Codex.
- No privacy notice published.
- No DPA created, approved, or sent by Codex.
- No customer data processed.
- No vulnerability scan run by Codex.
- No vulnerability management activated.
- No security contact published.
- No runtime modified.
- No backend modified.
- No kernel modified.
- No API schema modified.
- No private core exposed.
- No product launched.
- No customer contacted.
- No public SDK released.
- No blocker closed.
- No production-ready claim added.

codex_performed_security_review=false
privacy_notice_published=false
dpa_sent_to_customer=false
customer_data_processed=false
vulnerability_management_operational=false
blockers_closed_by_reconciliation=0
production_ready=false
customer_validated=false
product_launched=false
private_core_exposed=false
""",
        encoding="utf-8",
    )
    TOP_DOC.write_text(
        f"""# SAEE Privacy/Security/Legal Follow-up State Reconciliation v0.1

status: {payload['status']}
target_blocker_ids: formal_security_review,privacy_legal_review,data_processing_agreement,vulnerability_management
resolved_current_path: {payload['resolved_current_path']}
formal_security_review_ready_for_review: {str(payload['formal_security_review_ready_for_review']).lower()}
privacy_legal_review_ready_for_review: {str(payload['privacy_legal_review_ready_for_review']).lower()}
data_processing_agreement_ready_for_review: {str(payload['data_processing_agreement_ready_for_review']).lower()}
vulnerability_management_ready_for_review: {str(payload['vulnerability_management_ready_for_review']).lower()}
combined_privacy_security_legal_profile_ready: {str(payload['combined_privacy_security_legal_profile_ready']).lower()}
ready_for_review_count: {payload['ready_for_review_count']}
human_review_required: true
separate_matrix_update_request_required: true
codex_performed_security_review=false
privacy_notice_published=false
dpa_sent_to_customer=false
customer_data_processed=false
vulnerability_management_operational=false
blockers_closed_by_reconciliation=0
production_ready=false
customer_validated=false
product_launched=false
private_core_exposed=false

This is a local state reconciliation layer for privacy/security/legal follow-up
evidence. It may point a human reviewer to source-backed evidence, but it does
not perform security/legal operations, update the production blocker matrix,
close blockers, or claim production readiness.
""",
        encoding="utf-8",
    )
    GATE.write_text(
        f"""# SAEE Privacy/Security/Legal Follow-up State Reconciliation Gate

answer: hold_human_privacy_security_legal_review_required_no_security_review_no_legal_publication_no_auto_closure

reason:
Human-filled privacy/security/legal evidence can be reviewed, but Codex has not
performed security review, inspected private core, contacted legal or security
vendors, published privacy/DPA documents, activated vulnerability management,
processed customer data, changed runtime behavior, or closed blockers.

status: {payload['status']}
target_blocker_ids: formal_security_review,privacy_legal_review,data_processing_agreement,vulnerability_management
resolved_current_path: {payload['resolved_current_path']}

boundary:
codex_performed_security_review: false
privacy_notice_published: false
dpa_sent_to_customer: false
customer_data_processed: false
vulnerability_management_operational: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
private_core_exposed: false
product_launched: false
production_ready: false
customer_validated: false
blockers_closed_by_reconciliation: 0

next_action:
Human privacy/security/legal owner may review the state reconciliation and
decide whether a separate matrix update request should be created. This gate
does not authorize execution, publication, or closure.
""",
        encoding="utf-8",
    )

    block = f"""## Privacy/Security/Legal Follow-up State Reconciliation v0.1

Status: `{payload['status']}`.

`formal_security_review`, `privacy_legal_review`,
`data_processing_agreement`, and `vulnerability_management` human-filled
evidence is reconciled into a review-only state.
`ready_for_review_count={payload['ready_for_review_count']}`,
`combined_privacy_security_legal_profile_ready={str(payload['combined_privacy_security_legal_profile_ready']).lower()}`,
`formal_security_review_ready_for_review={str(payload['formal_security_review_ready_for_review']).lower()}`,
`privacy_legal_review_ready_for_review={str(payload['privacy_legal_review_ready_for_review']).lower()}`,
`data_processing_agreement_ready_for_review={str(payload['data_processing_agreement_ready_for_review']).lower()}`,
`vulnerability_management_ready_for_review={str(payload['vulnerability_management_ready_for_review']).lower()}`,
`blockers_closed_by_reconciliation=0`, `production_ready=false`,
`customer_validated=false`, `product_launched=false`, and
`private_core_exposed=false`. No security review, legal publication, customer
data processing, vulnerability activation, customer contact, or vendor contact
was performed by Codex.
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_PRIVACY_SECURITY_LEGAL_FOLLOWUP_STATE_RECONCILIATION", block)

    for line in [
        "/phase_b_product/commercial_readiness/PRIVACY_SECURITY_LEGAL_FOLLOWUP_STATE_RECONCILIATION_V0_1.md",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_security_legal_followup_state_reconciliation/privacy_security_legal_followup_state_reconciliation.local.json",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_security_legal_followup_state_reconciliation/privacy_security_legal_followup_state_reconciliation.md",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_security_legal_followup_state_reconciliation/privacy_security_legal_followup_state_reconciliation_boundary_audit.md",
        "/docs/strategy/SAEE_PRIVACY_SECURITY_LEGAL_FOLLOWUP_STATE_RECONCILIATION_GATE.md",
        "/scripts/saee_privacy_security_legal_followup_state_reconciliation.py",
        "/scripts/saee_privacy_security_legal_followup_state_reconciliation_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["privacy_security_legal_followup_state_reconciliation_v0_1"] = {
        "status": payload["status"],
        "target_blocker_ids": payload["target_blocker_ids"],
        "resolved_current_path": payload["resolved_current_path"],
        "formal_security_review_ready_for_review": payload["formal_security_review_ready_for_review"],
        "privacy_legal_review_ready_for_review": payload["privacy_legal_review_ready_for_review"],
        "data_processing_agreement_ready_for_review": payload["data_processing_agreement_ready_for_review"],
        "vulnerability_management_ready_for_review": payload["vulnerability_management_ready_for_review"],
        "combined_privacy_security_legal_profile_ready": payload[
            "combined_privacy_security_legal_profile_ready"
        ],
        "ready_for_review_count": payload["ready_for_review_count"],
        "human_review_required": True,
        "separate_matrix_update_request_required": True,
        "codex_performed_security_review": False,
        "privacy_notice_published": False,
        "dpa_sent_to_customer": False,
        "customer_data_processed": False,
        "vulnerability_management_operational": False,
        "blockers_closed_by_reconciliation": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
    }
    write_json(AGENT_INDEX, index)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_PRIVACY_SECURITY_LEGAL_FOLLOWUP_STATE_RECONCILIATION: PASS "
        f"status={payload['status']} blockers_closed_by_reconciliation=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
