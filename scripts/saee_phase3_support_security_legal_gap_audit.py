#!/usr/bin/env python3
"""Audit Phase 3 support/security/legal evidence gaps.

This runner compares Phase 3 support, security, privacy, legal, DPA, and
vulnerability-management production evidence requirements against existing
local public-shell evidence files. It is a planning and review aid only: it
does not contact support vendors, security reviewers, legal counsel, customers,
or external services; it does not approve SLAs, DPAs, vulnerability operations,
or production launch; it does not close blockers or claim production readiness.
"""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go
from scripts.saee_commercial_review_semantics import local_public_shell_go_no_go_summary


SUPPORT_EVIDENCE_PATH = (
    ROOT / "phase_b_product/commercial_readiness/support_evidence/support_evidence.local.json"
)
PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_security_legal_evidence.local.json"
)
DEPENDENCY_PLAN_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_blocker_dependency_plan/dependency_plan.local.json"
)
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/phase_3_support_security_legal_gap_audit"
OUTPUT_JSON = OUTPUT_DIR / "phase_3_support_security_legal_gap_audit.local.json"
OUTPUT_MD = OUTPUT_DIR / "phase_3_support_security_legal_gap_audit.md"
OUTPUT_CSV = OUTPUT_DIR / "phase_3_support_security_legal_gap_audit.csv"
README_PATH = OUTPUT_DIR / "README.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/PHASE_3_SUPPORT_SECURITY_LEGAL_GAP_AUDIT_V0_1.md"
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_PHASE_3_SUPPORT_SECURITY_LEGAL_GAP_AUDIT_RECOMMENDATION_GATE.md"
)


LOCAL_PROFILE_ENV = {
    "SAEE_PRODUCTION_AUTH_EVIDENCE_PATH": "phase_b_product/commercial_readiness/auth_evidence/auth_evidence.local.json",
    "SAEE_PRODUCTION_SUPPORT_EVIDENCE_PATH": str(
        SUPPORT_EVIDENCE_PATH.relative_to(ROOT)
    ),
    "SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH": "phase_b_product/commercial_readiness/data_operations_evidence/data_operations_evidence.local.json",
    "SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH": "phase_b_product/commercial_readiness/operations_evidence/operations_evidence.local.json",
    "SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH": str(
        PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH.relative_to(ROOT)
    ),
    "SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH": "phase_b_product/commercial_readiness/billing_revenue_evidence/billing_revenue_evidence.local.json",
    "SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH": "phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_isolation_evidence.local.json",
    "SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH": "phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence.local.json",
}


PHASE_ID = "phase_3_support_security_legal"
TARGET_BLOCKERS = [
    "sla",
    "support_contact",
    "customer_support",
    "formal_security_review",
    "privacy_legal_review",
    "data_processing_agreement",
    "vulnerability_management",
]


REQUIRED_EVIDENCE_ITEMS: list[dict[str, str]] = [
    {
        "blocker_id": "support_contact",
        "evidence_file_type": "production_support_sla_evidence",
        "evidence_key": "customer_facing_support_contact_configured",
    },
    {
        "blocker_id": "support_contact",
        "evidence_file_type": "production_support_sla_evidence",
        "evidence_key": "support_contact_owner_named",
    },
    {
        "blocker_id": "support_contact",
        "evidence_file_type": "production_support_sla_evidence",
        "evidence_key": "support_contact_test_recorded",
    },
    {
        "blocker_id": "support_contact",
        "evidence_file_type": "production_support_sla_evidence",
        "evidence_key": "abuse_handling_path_defined",
    },
    {
        "blocker_id": "support_contact",
        "evidence_file_type": "production_support_sla_evidence",
        "evidence_key": "customer_notice_route_defined",
    },
    {
        "blocker_id": "customer_support",
        "evidence_file_type": "production_support_sla_evidence",
        "evidence_key": "staffed_support_process_defined",
    },
    {
        "blocker_id": "customer_support",
        "evidence_file_type": "production_support_sla_evidence",
        "evidence_key": "case_triage_workflow_defined",
    },
    {
        "blocker_id": "customer_support",
        "evidence_file_type": "production_support_sla_evidence",
        "evidence_key": "customer_communication_template_approved",
    },
    {
        "blocker_id": "customer_support",
        "evidence_file_type": "production_support_sla_evidence",
        "evidence_key": "support_case_audit_trail_available",
    },
    {
        "blocker_id": "customer_support",
        "evidence_file_type": "production_support_sla_evidence",
        "evidence_key": "handoff_to_engineering_defined",
    },
    {
        "blocker_id": "sla",
        "evidence_file_type": "production_support_sla_evidence",
        "evidence_key": "human_approved_sla_terms",
    },
    {
        "blocker_id": "sla",
        "evidence_file_type": "production_support_sla_evidence",
        "evidence_key": "support_hours_approved",
    },
    {
        "blocker_id": "sla",
        "evidence_file_type": "production_support_sla_evidence",
        "evidence_key": "response_targets_approved",
    },
    {
        "blocker_id": "sla",
        "evidence_file_type": "production_support_sla_evidence",
        "evidence_key": "severity_definitions_approved",
    },
    {
        "blocker_id": "sla",
        "evidence_file_type": "production_support_sla_evidence",
        "evidence_key": "exclusions_approved",
    },
    {
        "blocker_id": "sla",
        "evidence_file_type": "production_support_sla_evidence",
        "evidence_key": "legal_review_completed",
    },
    {
        "blocker_id": "formal_security_review",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "formal_security_review_report",
    },
    {
        "blocker_id": "formal_security_review",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "public_shell_threat_model_reviewed",
    },
    {
        "blocker_id": "formal_security_review",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "dependency_review_completed",
    },
    {
        "blocker_id": "formal_security_review",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "auth_and_tenant_boundary_reviewed",
    },
    {
        "blocker_id": "formal_security_review",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "storage_backup_and_restore_reviewed",
    },
    {
        "blocker_id": "formal_security_review",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "review_findings_triaged",
    },
    {
        "blocker_id": "privacy_legal_review",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "privacy_notice_approved",
    },
    {
        "blocker_id": "privacy_legal_review",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "privacy_notice_published",
    },
    {
        "blocker_id": "privacy_legal_review",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "data_inventory_reviewed",
    },
    {
        "blocker_id": "privacy_legal_review",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "controller_processor_roles_defined",
    },
    {
        "blocker_id": "privacy_legal_review",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "subprocessor_inventory_reviewed",
    },
    {
        "blocker_id": "privacy_legal_review",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "retention_policy_approved",
    },
    {
        "blocker_id": "privacy_legal_review",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "terms_of_service_approved",
    },
    {
        "blocker_id": "privacy_legal_review",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "terms_published",
    },
    {
        "blocker_id": "privacy_legal_review",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "breach_notice_terms_approved",
    },
    {
        "blocker_id": "data_processing_agreement",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "customer_dpa_template_available",
    },
    {
        "blocker_id": "data_processing_agreement",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "dpa_terms_approved",
    },
    {
        "blocker_id": "data_processing_agreement",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "subprocessor_terms_approved",
    },
    {
        "blocker_id": "data_processing_agreement",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "deletion_or_return_terms_approved",
    },
    {
        "blocker_id": "data_processing_agreement",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "customer_data_processing_approved",
    },
    {
        "blocker_id": "data_processing_agreement",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "dpa_sent_to_customer",
    },
    {
        "blocker_id": "vulnerability_management",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "security_contact_configured",
    },
    {
        "blocker_id": "vulnerability_management",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "coordinated_disclosure_policy_approved",
    },
    {
        "blocker_id": "vulnerability_management",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "vulnerability_case_dry_run_recorded",
    },
    {
        "blocker_id": "vulnerability_management",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "triage_owner_named",
    },
    {
        "blocker_id": "vulnerability_management",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "severity_model_approved",
    },
    {
        "blocker_id": "vulnerability_management",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "remediation_targets_approved",
    },
    {
        "blocker_id": "vulnerability_management",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "advisory_publication_policy_approved",
    },
    {
        "blocker_id": "vulnerability_management",
        "evidence_file_type": "production_privacy_security_legal_evidence",
        "evidence_key": "vulnerability_management_operational",
    },
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def phase_blockers(plan: dict[str, Any]) -> list[dict[str, Any]]:
    blockers = [
        blocker
        for blocker in plan.get("blockers", [])
        if blocker.get("phase_id") == PHASE_ID
    ]
    blocker_ids = [blocker["blocker_id"] for blocker in blockers]
    if blocker_ids != TARGET_BLOCKERS:
        raise SystemExit(
            "SAEE_PHASE3_SUPPORT_SECURITY_LEGAL_GAP_AUDIT: FAIL "
            f"unexpected phase blockers {blocker_ids}"
        )
    return blockers


def evidence_value(
    item: dict[str, str],
    support: dict[str, Any],
    privacy_security_legal: dict[str, Any],
) -> bool:
    key = item["evidence_key"]
    file_type = item["evidence_file_type"]
    if file_type == "production_support_sla_evidence":
        return support.get(key) is True
    if file_type == "production_privacy_security_legal_evidence":
        return privacy_security_legal.get(key) is True
    return False


def classify_item(local_value: bool) -> str:
    if local_value:
        return "local_public_shell_evidence_present_requires_human_production_approval"
    return "missing_external_or_human_production_evidence"


def build_gap_rows(
    support: dict[str, Any],
    privacy_security_legal: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in REQUIRED_EVIDENCE_ITEMS:
        local_value = evidence_value(item, support, privacy_security_legal)
        rows.append(
            {
                "blocker_id": item["blocker_id"],
                "evidence_file_type": item["evidence_file_type"],
                "evidence_key": item["evidence_key"],
                "local_public_shell_value": local_value,
                "accepted_for_blocker_closure": False,
                "gap_status": classify_item(local_value),
                "external_dependency_required": True,
                "human_review_required": True,
                "notes": (
                    "Local evidence is review input only; it does not close the production blocker."
                    if local_value
                    else "Production-grade external or human-approved evidence is still missing."
                ),
            }
        )
    return rows


def summarize_by_blocker(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for blocker_id in TARGET_BLOCKERS:
        subset = [row for row in rows if row["blocker_id"] == blocker_id]
        local_present = sum(1 for row in subset if row["local_public_shell_value"])
        missing = len(subset) - local_present
        summary.append(
            {
                "blocker_id": blocker_id,
                "required_items": len(subset),
                "local_public_shell_present": local_present,
                "missing_production_evidence": missing,
                "ready_to_close": False,
                "external_dependency_required": True,
                "next_action": (
                    "Human owners must provide real support, security, privacy, legal, "
                    "DPA, and vulnerability-management evidence before this blocker can close."
                ),
            }
        )
    return summary


def csv_text(rows: list[dict[str, Any]]) -> str:
    output = StringIO()
    fieldnames = [
        "blocker_id",
        "evidence_file_type",
        "evidence_key",
        "local_public_shell_value",
        "accepted_for_blocker_closure",
        "gap_status",
        "external_dependency_required",
        "human_review_required",
        "notes",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def build_audit() -> dict[str, Any]:
    support = read_json(SUPPORT_EVIDENCE_PATH)
    privacy_security_legal = read_json(PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH)
    plan = read_json(DEPENDENCY_PLAN_PATH)
    blockers = phase_blockers(plan)
    default_go_no_go = evaluate_commercial_go_no_go(load_settings({}))
    local_profile_go_no_go = evaluate_commercial_go_no_go(load_settings(LOCAL_PROFILE_ENV))
    rows = build_gap_rows(support, privacy_security_legal)
    blocker_summary = summarize_by_blocker(rows)
    local_present = sum(1 for row in rows if row["local_public_shell_value"])
    missing = len(rows) - local_present

    return {
        "audit_type": "saee_phase_3_support_security_legal_gap_audit",
        "audit_version": "v0.1",
        "audit_scope": "local_public_shell_to_production_support_security_legal_gap_review",
        "phase_id": PHASE_ID,
        "generated_by": "scripts/saee_phase3_support_security_legal_gap_audit.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_dependency_plan": str(DEPENDENCY_PLAN_PATH.relative_to(ROOT)),
        "source_support_evidence": str(SUPPORT_EVIDENCE_PATH.relative_to(ROOT)),
        "source_privacy_security_legal_evidence": str(
            PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH.relative_to(ROOT)
        ),
        "target_blockers": [blocker["blocker_id"] for blocker in blockers],
        "target_blocker_count": len(blockers),
        "required_evidence_item_count": len(rows),
        "local_public_shell_present_count": local_present,
        "missing_production_evidence_count": missing,
        "accepted_for_blocker_closure_count": 0,
        "blockers_ready_to_close": [],
        "blockers_closed_by_audit": 0,
        "default_go_no_go": {
            "commercial_status": default_go_no_go["commercial_status"],
            "production_launch_status": default_go_no_go["production_launch_status"],
            "satisfied_production_checks": default_go_no_go[
                "satisfied_production_checks"
            ],
            "production_blocker_count": default_go_no_go["production_blocker_count"],
            "total_production_checks": default_go_no_go["total_production_checks"],
        },
        "local_profile_go_no_go": local_public_shell_go_no_go_summary(local_profile_go_no_go),
        "blocker_summary": blocker_summary,
        "gap_rows": rows,
        "human_review_required": True,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "support_vendor_contacted_by_codex": False,
        "support_contact_published": False,
        "customer_support_activated": False,
        "sla_approved": False,
        "security_reviewer_contacted_by_codex": False,
        "formal_security_review_completed": False,
        "privacy_legal_review_completed": False,
        "legal_counsel_contacted_by_codex": False,
        "dpa_approved": False,
        "dpa_sent_to_customer": False,
        "vulnerability_management_activated": False,
        "security_contact_published": False,
        "customer_data_processed": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "public_sdk_released": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "customer_contacted": False,
        "next_action": (
            "Human owners must provide real approved support, security, privacy, "
            "legal, DPA, and vulnerability-management evidence before any Phase 3 "
            "blocker can close."
        ),
    }


def write_readme() -> None:
    README_PATH.write_text(
        """# SAEE Phase 3 Support/Security/Legal Gap Audit

Status: local gap audit only; no blocker closure.

This directory compares Phase 3 support, SLA, security review, privacy/legal,
DPA, and vulnerability-management evidence requirements against existing local
public-shell evidence. It is a commercial-readiness review surface, not an
execution task.

Boundary:

- no support vendor contacted
- no support contact published
- no customer support activated
- no SLA approved
- no security reviewer contacted
- no legal counsel contacted
- no DPA approved or sent
- no vulnerability-management process activated
- no customer data processing
- no blocker closure
- no production-ready claim
- no backend, runtime, kernel, API schema, or private core modification
""",
        encoding="utf-8",
    )


def markdown_report(audit: dict[str, Any]) -> str:
    lines = [
        "# SAEE Phase 3 Support/Security/Legal Gap Audit v0.1",
        "",
        "Status: local public-shell gap audit only; no blocker closure.",
        "",
        "This audit compares Phase 3 production evidence requirements against",
        "existing local support and privacy/security/legal evidence. Local",
        "evidence may support human review, but it is not accepted as production",
        "blocker closure by this audit.",
        "",
        "## Summary",
        "",
        f"- required_evidence_item_count: {audit['required_evidence_item_count']}",
        f"- local_public_shell_present_count: {audit['local_public_shell_present_count']}",
        f"- missing_production_evidence_count: {audit['missing_production_evidence_count']}",
        f"- accepted_for_blocker_closure_count: {audit['accepted_for_blocker_closure_count']}",
        f"- blockers_closed_by_audit: {audit['blockers_closed_by_audit']}",
        f"- default_go_no_go: {audit['default_go_no_go']['satisfied_production_checks']}/{audit['default_go_no_go']['total_production_checks']} satisfied",
        f"- local_profile_go_no_go: {audit['local_profile_go_no_go']['satisfied_production_checks']}/{audit['local_profile_go_no_go']['total_production_checks']} satisfied",
        f"- local_public_shell_review_candidate_count: {audit['local_profile_go_no_go']['local_public_shell_review_candidate_count']}",
        f"- production_ready: {str(audit['production_ready']).lower()}",
        f"- customer_validated: {str(audit['customer_validated']).lower()}",
        f"- product_launched: {str(audit['product_launched']).lower()}",
        f"- private_core_exposed: {str(audit['private_core_exposed']).lower()}",
        "",
        "## Blocker Summary",
        "",
        "| Blocker | Required items | Local public-shell present | Missing production evidence | Ready to close | External dependency |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in audit["blocker_summary"]:
        lines.append(
            "| {blocker_id} | {required_items} | {local_public_shell_present} | {missing_production_evidence} | {ready} | {external} |".format(
                blocker_id=row["blocker_id"],
                required_items=row["required_items"],
                local_public_shell_present=row["local_public_shell_present"],
                missing_production_evidence=row["missing_production_evidence"],
                ready=str(row["ready_to_close"]).lower(),
                external=str(row["external_dependency_required"]).lower(),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- No blocker is closed by this audit.",
            "- No support contact is published.",
            "- No customer support process is activated.",
            "- No SLA is approved.",
            "- No security reviewer or legal counsel is contacted.",
            "- No DPA is approved or sent to a customer.",
            "- No vulnerability-management process is activated.",
            "- No customer data is processed.",
            "- No production-ready claim is made.",
            "- No customer validation claim is made.",
            "- No product launch is authorized.",
            "- No private core is exposed.",
            "",
        ]
    )
    return "\n".join(lines)


def write_doc() -> None:
    DOC_PATH.write_text(
        """# SAEE Phase 3 Support/Security/Legal Gap Audit v0.1

phase_3_support_security_legal_gap_audit_v0_1: true
audit_scope: local_public_shell_to_production_support_security_legal_gap_review
required_evidence_item_count: 45
accepted_for_blocker_closure_count: 0
blockers_closed_by_audit: 0
execution_authorized: false
evidence_collection_authorized: false
support_vendor_contacted_by_codex: false
support_contact_published: false
customer_support_activated: false
sla_approved: false
security_reviewer_contacted_by_codex: false
legal_counsel_contacted_by_codex: false
dpa_approved: false
vulnerability_management_activated: false
customer_data_processed: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This audit compares Phase 3 support, security, privacy/legal, DPA, and
vulnerability-management production evidence requirements against existing
local public-shell evidence. It records which evidence keys are locally present
and which still need external or human production approval.

It is an audit only. It does not authorize execution, close blockers, contact
support vendors, contact security reviewers, contact legal counsel, publish a
support contact, approve SLAs or DPAs, activate vulnerability management, or
claim production readiness.

## Target Blockers

- support_contact
- customer_support
- sla
- formal_security_review
- privacy_legal_review
- data_processing_agreement
- vulnerability_management
""",
        encoding="utf-8",
    )


def write_gate() -> None:
    GATE_PATH.write_text(
        """# SAEE Phase 3 Support/Security/Legal Gap Audit Recommendation Gate

answer: conditional
recommend_for_human_review: true
recommend_for_blocker_closure: false
recommend_for_execution_authorization: false
recommend_for_support_activation: false
recommend_for_sla_approval: false
recommend_for_security_review_claim: false
recommend_for_legal_review_claim: false
recommend_for_dpa_use: false
recommend_for_vulnerability_management_activation: false
recommend_for_production_launch: false

## Reason

This audit is useful because it separates local public-shell support and
privacy/security/legal evidence from production-grade support, security, legal,
DPA, and vulnerability-management evidence. It does not close any blocker or
authorize any external action.

## Boundary

```yaml
audit_scope: local_public_shell_to_production_support_security_legal_gap_review
accepted_for_blocker_closure_count: 0
blockers_closed_by_audit: 0
execution_authorized: false
evidence_collection_authorized: false
support_vendor_contacted_by_codex: false
support_contact_published: false
customer_support_activated: false
sla_approved: false
security_reviewer_contacted_by_codex: false
legal_counsel_contacted_by_codex: false
dpa_approved: false
vulnerability_management_activated: false
customer_data_processed: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
```

## Next Action

Human reviewers may use the gap table to decide whether to authorize a
separate production evidence collection task. Until then, all Phase 3 blockers
remain open.
""",
        encoding="utf-8",
    )


def write_outputs(audit: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    OUTPUT_MD.write_text(markdown_report(audit), encoding="utf-8")
    OUTPUT_CSV.write_text(csv_text(audit["gap_rows"]), encoding="utf-8")
    write_readme()
    write_doc()
    write_gate()


def main() -> None:
    audit = build_audit()
    write_outputs(audit)
    print(
        "SAEE_PHASE3_SUPPORT_SECURITY_LEGAL_GAP_AUDIT: PASS "
        f"required_items={audit['required_evidence_item_count']} "
        f"local_present={audit['local_public_shell_present_count']} "
        f"missing_production={audit['missing_production_evidence_count']} "
        f"blockers_closed_by_audit={audit['blockers_closed_by_audit']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
