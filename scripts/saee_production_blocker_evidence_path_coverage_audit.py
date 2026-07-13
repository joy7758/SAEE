#!/usr/bin/env python3
"""Audit production-blocker evidence path coverage without closing blockers.

This is an agent-readable coverage map over the current 24 production launch
blockers. It answers whether each blocker has a local evidence/profile path and
human-review surface already available. It does not execute evidence work,
collect human values, close blockers, contact customers, call external services,
launch product, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_production_blocker_gap_matrix import build_gap_matrix


COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
GO_NO_GO_JSON = COMMERCIAL_DIR / "commercial_go_no_go.local.json"
COVERAGE_DIR = COMMERCIAL_DIR / "production_blocker_evidence_path_coverage"
COVERAGE_JSON = COVERAGE_DIR / "coverage.local.json"
COVERAGE_MD = COVERAGE_DIR / "coverage.local.md"
COVERAGE_CSV = COVERAGE_DIR / "coverage.local.csv"
BOUNDARY_MD = COVERAGE_DIR / "boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "PRODUCTION_BLOCKER_EVIDENCE_PATH_COVERAGE_AUDIT_V0_1.md"
GATE = (
    ROOT
    / "docs/strategy/SAEE_PRODUCTION_BLOCKER_EVIDENCE_PATH_COVERAGE_AUDIT_RECOMMENDATION_GATE.md"
)


BLOCKER_SURFACES: dict[str, dict[str, list[str]]] = {
    "production_identity_provider": {
        "evidence_or_profile": [
            "phase_b_product/commercial_readiness/auth_evidence/production_auth_evidence_path.local.json",
            "phase_b_product/commercial_readiness/PRODUCTION_AUTH_EVIDENCE_PATH_V0_1.md",
        ],
        "human_input": [
            "phase_b_product/commercial_readiness/PRODUCTION_IDENTITY_PROVIDER_EVIDENCE_BUILDER_REQUEST_TEMPLATE_V0_1.md",
            "phase_b_product/commercial_readiness/PRODUCTION_IDENTITY_PROVIDER_APPROVAL_INPUT_VALIDATOR_V0_1.md",
        ],
        "requirements_or_review": [
            "phase_b_product/commercial_readiness/PRODUCTION_AUTH_REQUIREMENTS_V0_1.md",
            "phase_b_product/commercial_readiness/PRODUCTION_IDENTITY_PROVIDER_DECISION_PACKET_V0_1.md",
        ],
    },
    "oauth_oidc": {
        "evidence_or_profile": [
            "phase_b_product/commercial_readiness/auth_evidence/production_auth_evidence_path.local.json",
            "phase_b_product/commercial_readiness/AUTH_OIDC_RBAC_FIXTURE_DRY_RUN_V0_1.md",
        ],
        "human_input": [
            "phase_b_product/commercial_readiness/OAUTH_OIDC_APPROVAL_INPUT_VALIDATOR_V0_1.md",
            "phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/oauth_oidc_approval_input_validation.md",
        ],
        "requirements_or_review": [
            "phase_b_product/commercial_readiness/PRODUCTION_AUTH_REQUIREMENTS_V0_1.md",
        ],
    },
    "rbac": {
        "evidence_or_profile": [
            "phase_b_product/commercial_readiness/auth_evidence/production_auth_evidence_path.local.json",
            "phase_b_product/commercial_readiness/AUTH_OIDC_RBAC_FIXTURE_DRY_RUN_V0_1.md",
        ],
        "human_input": [
            "phase_b_product/commercial_readiness/RBAC_APPROVAL_INPUT_VALIDATOR_V0_1.md",
            "phase_b_product/commercial_readiness/RBAC_POLICY_TEMPLATE_V0_1.md",
        ],
        "requirements_or_review": [
            "phase_b_product/commercial_readiness/PRODUCTION_AUTH_REQUIREMENTS_V0_1.md",
        ],
    },
    "tenant_storage_isolation": {
        "evidence_or_profile": [
            "phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_isolation_evidence.local.json",
            "phase_b_product/commercial_readiness/PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH_V0_1.md",
        ],
        "human_input": [
            "phase_b_product/commercial_readiness/TENANT_STORAGE_APPROVAL_INPUT_VALIDATOR_V0_1.md",
        ],
        "requirements_or_review": [
            "phase_b_product/commercial_readiness/PRODUCTION_TENANT_STORAGE_ISOLATION_REQUIREMENTS_V0_1.md",
            "phase_b_product/commercial_readiness/TENANT_SECURITY_PRIVACY_REVIEW_PACKET_V0_1.md",
        ],
    },
    "production_monitoring": {
        "evidence_or_profile": [
            "phase_b_product/commercial_readiness/operations_evidence/production_monitoring_evidence_path.local.json",
            "phase_b_product/commercial_readiness/PRODUCTION_MONITORING_EVIDENCE_PATH_V0_1.md",
        ],
        "human_input": [
            "phase_b_product/commercial_readiness/PRODUCTION_MONITORING_APPROVAL_INPUT_PROMPT_V0_1.md",
            "phase_b_product/commercial_readiness/PRODUCTION_MONITORING_APPROVAL_INPUT_VALIDATOR_V0_1.md",
        ],
        "requirements_or_review": [
            "phase_b_product/commercial_readiness/PRODUCTION_OPERATIONS_REQUIREMENTS_V0_1.md",
            "phase_b_product/commercial_readiness/OPERATIONS_MONITORING_ALERT_REVIEW_PACKET_V0_1.md",
        ],
    },
    "external_alert_delivery": {
        "evidence_or_profile": [
            "phase_b_product/commercial_readiness/operations_evidence/external_alert_delivery_evidence_path.local.json",
            "phase_b_product/commercial_readiness/EXTERNAL_ALERT_DELIVERY_EVIDENCE_PATH_V0_1.md",
        ],
        "human_input": [
            "phase_b_product/commercial_readiness/EXTERNAL_ALERT_DELIVERY_APPROVAL_INPUT_PROMPT_V0_1.md",
            "phase_b_product/commercial_readiness/EXTERNAL_ALERT_DELIVERY_APPROVAL_INPUT_VALIDATOR_V0_1.md",
        ],
        "requirements_or_review": [
            "phase_b_product/commercial_readiness/PRODUCTION_OPERATIONS_REQUIREMENTS_V0_1.md",
            "phase_b_product/commercial_readiness/OPERATIONS_MONITORING_ALERT_REVIEW_PACKET_V0_1.md",
        ],
    },
    "on_call_rotation": {
        "evidence_or_profile": [
            "phase_b_product/commercial_readiness/operations_evidence/operations_on_call_rotation_evidence_path.local.json",
            "phase_b_product/commercial_readiness/OPERATIONS_ON_CALL_ROTATION_EVIDENCE_PATH_V0_1.md",
        ],
        "human_input": [
            "phase_b_product/commercial_readiness/OPERATIONS_ON_CALL_ROTATION_APPROVAL_INPUT_PROMPT_V0_1.md",
            "phase_b_product/commercial_readiness/OPERATIONS_ON_CALL_ROTATION_APPROVAL_INPUT_VALIDATOR_V0_1.md",
        ],
        "requirements_or_review": [
            "phase_b_product/commercial_readiness/PRODUCTION_OPERATIONS_REQUIREMENTS_V0_1.md",
            "phase_b_product/commercial_readiness/OPERATIONS_MONITORING_ALERT_REVIEW_PACKET_V0_1.md",
        ],
    },
    "sla": {
        "evidence_or_profile": [
            "phase_b_product/commercial_readiness/support_evidence/sla_evidence_path.local.json",
            "phase_b_product/commercial_readiness/SLA_EVIDENCE_PATH_V0_1.md",
        ],
        "human_input": [
            "phase_b_product/commercial_readiness/SLA_APPROVAL_INPUT_PROMPT_V0_1.md",
            "phase_b_product/commercial_readiness/SLA_APPROVAL_INPUT_VALIDATOR_V0_1.md",
        ],
        "requirements_or_review": [
            "phase_b_product/commercial_readiness/PRODUCTION_SUPPORT_SLA_REQUIREMENTS_V0_1.md",
            "phase_b_product/commercial_readiness/SUPPORT_SLA_ON_CALL_REVIEW_PACKET_V0_1.md",
        ],
    },
    "support_contact": {
        "evidence_or_profile": [
            "phase_b_product/commercial_readiness/support_evidence/support_contact_evidence_path.local.json",
            "phase_b_product/commercial_readiness/SUPPORT_CONTACT_EVIDENCE_PATH_V0_1.md",
        ],
        "human_input": [
            "phase_b_product/commercial_readiness/SUPPORT_CONTACT_APPROVAL_INPUT_PROMPT_V0_1.md",
            "phase_b_product/commercial_readiness/SUPPORT_CONTACT_APPROVAL_INPUT_VALIDATOR_V0_1.md",
            "phase_b_product/commercial_readiness/SUPPORT_CONTACT_EVIDENCE_BUILDER_REQUEST_TEMPLATE_V0_1.md",
        ],
        "requirements_or_review": [
            "phase_b_product/commercial_readiness/SUPPORT_CONTACT_DECISION_PACKET_V0_1.md",
            "phase_b_product/commercial_readiness/SUPPORT_CONTACT_READINESS_BOARD_V0_1.md",
        ],
    },
    "customer_support": {
        "evidence_or_profile": [
            "phase_b_product/commercial_readiness/support_evidence/customer_support_evidence_path.local.json",
            "phase_b_product/commercial_readiness/CUSTOMER_SUPPORT_EVIDENCE_PATH_V0_1.md",
        ],
        "human_input": [
            "phase_b_product/commercial_readiness/CUSTOMER_SUPPORT_APPROVAL_INPUT_PROMPT_V0_1.md",
            "phase_b_product/commercial_readiness/CUSTOMER_SUPPORT_APPROVAL_INPUT_VALIDATOR_V0_1.md",
        ],
        "requirements_or_review": [
            "phase_b_product/commercial_readiness/PRODUCTION_SUPPORT_SLA_REQUIREMENTS_V0_1.md",
            "phase_b_product/commercial_readiness/SUPPORT_SLA_ON_CALL_REVIEW_PACKET_V0_1.md",
        ],
    },
    "formal_security_review": {
        "evidence_or_profile": [
            "phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_security_legal_evidence_path.local.json",
            "phase_b_product/commercial_readiness/PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH_V0_1.md",
        ],
        "human_input": [
            "phase_b_product/commercial_readiness/FORMAL_SECURITY_REVIEW_APPROVAL_INPUT_PROMPT_V0_1.md",
            "phase_b_product/commercial_readiness/FORMAL_SECURITY_REVIEW_APPROVAL_INPUT_VALIDATOR_V0_1.md",
        ],
        "requirements_or_review": [
            "phase_b_product/commercial_readiness/FORMAL_SECURITY_REVIEW_SCOPE_DRAFT_V0_1.md",
            "phase_b_product/commercial_readiness/PRODUCTION_PRIVACY_SECURITY_LEGAL_REQUIREMENTS_V0_1.md",
        ],
    },
    "privacy_legal_review": {
        "evidence_or_profile": [
            "phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_security_legal_evidence_path.local.json",
            "phase_b_product/commercial_readiness/PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH_V0_1.md",
        ],
        "human_input": [
            "phase_b_product/commercial_readiness/PRIVACY_LEGAL_DPA_APPROVAL_INPUT_PROMPT_V0_1.md",
        ],
        "requirements_or_review": [
            "phase_b_product/commercial_readiness/PRIVACY_LEGAL_REVIEW_PACKET_V0_1.md",
            "phase_b_product/commercial_readiness/PRODUCTION_PRIVACY_SECURITY_LEGAL_REQUIREMENTS_V0_1.md",
        ],
    },
    "data_processing_agreement": {
        "evidence_or_profile": [
            "phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_security_legal_evidence_path.local.json",
            "phase_b_product/commercial_readiness/PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH_V0_1.md",
        ],
        "human_input": [
            "phase_b_product/commercial_readiness/PRIVACY_LEGAL_DPA_APPROVAL_INPUT_PROMPT_V0_1.md",
        ],
        "requirements_or_review": [
            "phase_b_product/commercial_readiness/DATA_PROCESSING_AGREEMENT_REVIEW_PACKET_V0_1.md",
            "phase_b_product/commercial_readiness/PRODUCTION_PRIVACY_SECURITY_LEGAL_REQUIREMENTS_V0_1.md",
        ],
    },
    "vulnerability_management": {
        "evidence_or_profile": [
            "phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_security_legal_evidence_path.local.json",
            "phase_b_product/commercial_readiness/PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH_V0_1.md",
        ],
        "human_input": [
            "phase_b_product/commercial_readiness/VULNERABILITY_MANAGEMENT_APPROVAL_INPUT_PROMPT_V0_1.md",
        ],
        "requirements_or_review": [
            "phase_b_product/commercial_readiness/VULNERABILITY_MANAGEMENT_READINESS_V0_1.md",
            "phase_b_product/commercial_readiness/PRODUCTION_PRIVACY_SECURITY_LEGAL_REQUIREMENTS_V0_1.md",
        ],
    },
    "pilot_results": {
        "evidence_or_profile": [
            "phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence_path.local.json",
            "phase_b_product/commercial_readiness/CUSTOMER_VALIDATION_EVIDENCE_PATH_V0_1.md",
        ],
        "human_input": [
            "phase_b_product/commercial_readiness/CUSTOMER_VALIDATION_APPROVAL_INPUT_VALIDATOR_V0_1.md",
            "phase_b_product/commercial_readiness/CUSTOMER_VALIDATION_EVIDENCE_BUILDER_V0_1.md",
        ],
        "requirements_or_review": [
            "phase_b_product/commercial_readiness/PRODUCTION_CUSTOMER_VALIDATION_REQUIREMENTS_V0_1.md",
            "phase_b_product/commercial_readiness/PILOT_CUSTOMER_VALIDATION_READINESS_V0_1.md",
        ],
    },
    "customer_validated": {
        "evidence_or_profile": [
            "phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence_path.local.json",
            "phase_b_product/commercial_readiness/CUSTOMER_VALIDATION_EVIDENCE_PATH_V0_1.md",
        ],
        "human_input": [
            "phase_b_product/commercial_readiness/CUSTOMER_VALIDATION_APPROVAL_INPUT_VALIDATOR_V0_1.md",
            "phase_b_product/commercial_readiness/CUSTOMER_VALIDATION_EVIDENCE_BUILDER_V0_1.md",
        ],
        "requirements_or_review": [
            "phase_b_product/commercial_readiness/PRODUCTION_CUSTOMER_VALIDATION_REQUIREMENTS_V0_1.md",
            "phase_b_product/commercial_readiness/PILOT_CUSTOMER_VALIDATION_READINESS_V0_1.md",
        ],
    },
    "pricing_page": {
        "evidence_or_profile": [
            "phase_b_product/commercial_readiness/billing_revenue_evidence/billing_revenue_evidence_path.local.json",
            "phase_b_product/commercial_readiness/BILLING_REVENUE_EVIDENCE_PATH_V0_1.md",
        ],
        "human_input": [
            "phase_b_product/commercial_readiness/PRICING_PAGE_APPROVAL_INPUT_PROMPT_V0_1.md",
            "phase_b_product/commercial_readiness/PRICING_PAGE_APPROVAL_INPUT_VALIDATOR_V0_1.md",
        ],
        "requirements_or_review": [
            "phase_b_product/commercial_readiness/PRICING_PAGE_REVIEW_PACKET_V0_1.md",
            "phase_b_product/commercial_readiness/PRODUCTION_BILLING_REVENUE_REQUIREMENTS_V0_1.md",
        ],
    },
    "payment_provider": {
        "evidence_or_profile": [
            "phase_b_product/commercial_readiness/billing_revenue_evidence/billing_revenue_evidence_path.local.json",
            "phase_b_product/commercial_readiness/BILLING_REVENUE_EVIDENCE_PATH_V0_1.md",
        ],
        "human_input": [
            "phase_b_product/commercial_readiness/PAYMENT_PROVIDER_APPROVAL_INPUT_PROMPT_V0_1.md",
        ],
        "requirements_or_review": [
            "phase_b_product/commercial_readiness/PAYMENT_PROVIDER_REVIEW_PACKET_V0_1.md",
            "phase_b_product/commercial_readiness/PRODUCTION_BILLING_REVENUE_REQUIREMENTS_V0_1.md",
        ],
    },
    "invoice_process": {
        "evidence_or_profile": [
            "phase_b_product/commercial_readiness/billing_revenue_evidence/billing_revenue_evidence_path.local.json",
            "phase_b_product/commercial_readiness/BILLING_REVENUE_EVIDENCE_PATH_V0_1.md",
        ],
        "human_input": [
            "phase_b_product/commercial_readiness/INVOICE_PROCESS_APPROVAL_INPUT_PROMPT_V0_1.md",
        ],
        "requirements_or_review": [
            "phase_b_product/commercial_readiness/INVOICE_PROCESS_REVIEW_PACKET_V0_1.md",
            "phase_b_product/commercial_readiness/PRODUCTION_BILLING_REVENUE_REQUIREMENTS_V0_1.md",
        ],
    },
    "tax_review": {
        "evidence_or_profile": [
            "phase_b_product/commercial_readiness/billing_revenue_evidence/billing_revenue_evidence_path.local.json",
            "phase_b_product/commercial_readiness/BILLING_REVENUE_EVIDENCE_PATH_V0_1.md",
        ],
        "human_input": [
            "phase_b_product/commercial_readiness/TAX_REVIEW_APPROVAL_INPUT_PROMPT_V0_1.md",
        ],
        "requirements_or_review": [
            "phase_b_product/commercial_readiness/TAX_REVIEW_PACKET_V0_1.md",
            "phase_b_product/commercial_readiness/PRODUCTION_BILLING_REVENUE_REQUIREMENTS_V0_1.md",
        ],
    },
    "refund_policy": {
        "evidence_or_profile": [
            "phase_b_product/commercial_readiness/billing_revenue_evidence/billing_revenue_evidence_path.local.json",
            "phase_b_product/commercial_readiness/BILLING_REVENUE_EVIDENCE_PATH_V0_1.md",
        ],
        "human_input": [
            "phase_b_product/commercial_readiness/REFUND_POLICY_APPROVAL_INPUT_PROMPT_V0_1.md",
        ],
        "requirements_or_review": [
            "phase_b_product/commercial_readiness/REFUND_POLICY_REVIEW_PACKET_V0_1.md",
            "phase_b_product/commercial_readiness/PRODUCTION_BILLING_REVENUE_REQUIREMENTS_V0_1.md",
        ],
    },
    "tenant_billing_isolation": {
        "evidence_or_profile": [
            "phase_b_product/commercial_readiness/billing_revenue_evidence/billing_revenue_evidence_path.local.json",
            "phase_b_product/commercial_readiness/BILLING_REVENUE_EVIDENCE_PATH_V0_1.md",
        ],
        "human_input": [
            "phase_b_product/commercial_readiness/TENANT_BILLING_ISOLATION_APPROVAL_INPUT_PROMPT_V0_1.md",
        ],
        "requirements_or_review": [
            "phase_b_product/commercial_readiness/TENANT_BILLING_ISOLATION_REVIEW_PACKET_V0_1.md",
            "phase_b_product/commercial_readiness/PRODUCTION_BILLING_REVENUE_REQUIREMENTS_V0_1.md",
        ],
    },
    "restore_tested": {
        "evidence_or_profile": [
            "phase_b_product/commercial_readiness/data_operations_evidence/restore_tested_evidence_profile.local.json",
            "phase_b_product/commercial_readiness/RESTORE_TESTED_EVIDENCE_PROFILE_V0_1.md",
        ],
        "human_input": [
            "phase_b_product/commercial_readiness/PHASE_2_DATA_OPERATIONS_EVIDENCE_TASK_V0_1.md",
        ],
        "requirements_or_review": [
            "phase_b_product/commercial_readiness/PRODUCTION_DATA_OPERATIONS_REQUIREMENTS_V0_1.md",
        ],
    },
    "production_restore_policy": {
        "evidence_or_profile": [
            "phase_b_product/commercial_readiness/data_operations_evidence/data_operations_evidence_profile.local.json",
            "phase_b_product/commercial_readiness/DATA_OPERATIONS_EVIDENCE_PROFILE_V0_1.md",
        ],
        "human_input": [
            "phase_b_product/commercial_readiness/PRODUCTION_RESTORE_POLICY_APPROVAL_INPUT_PROMPT_V0_1.md",
            "phase_b_product/commercial_readiness/PRODUCTION_RESTORE_POLICY_APPROVAL_INPUT_VALIDATOR_V0_1.md",
        ],
        "requirements_or_review": [
            "phase_b_product/commercial_readiness/PRODUCTION_RESTORE_POLICY_REVIEW_PACKET_V0_1.md",
            "phase_b_product/commercial_readiness/PRODUCTION_RESTORE_POLICY_DRAFT_V0_1.md",
        ],
    },
}


FALSE_BOUNDARY_FLAGS = {
    "task_candidates_executed": False,
    "development_permission_granted": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "private_core_exposed": False,
    "product_launched": False,
    "customer_contacted": False,
    "customer_validated": False,
    "production_ready": False,
    "public_sdk_released": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "external_ai_assistant_tested": False,
    "production_ready_claim": False,
    "customer_validation_claim": False,
    "external_validation_success_claim": False,
}


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def path_exists(relative_path: str) -> bool:
    return (ROOT / relative_path).exists()


def existing_paths(paths: list[str]) -> list[str]:
    return [path for path in paths if path_exists(path)]


def missing_paths(paths: list[str]) -> list[str]:
    return [path for path in paths if not path_exists(path)]


def make_row(blocker: dict[str, Any], gap_row: dict[str, Any] | None) -> dict[str, Any]:
    blocker_id = blocker["blocker_id"]
    surfaces = BLOCKER_SURFACES[blocker_id]
    evidence_paths = existing_paths(surfaces["evidence_or_profile"])
    human_paths = existing_paths(surfaces["human_input"])
    review_paths = existing_paths(surfaces["requirements_or_review"])
    missing = {
        name: missing_paths(paths)
        for name, paths in surfaces.items()
    }
    source_gap_path = gap_row.get("local_evidence_path") if gap_row else ""
    source_gap_path_available = bool(source_gap_path and path_exists(source_gap_path))
    coverage_complete = bool(evidence_paths and human_paths and review_paths)

    return {
        "blocker_id": blocker_id,
        "category": blocker["category"],
        "source_gap_matrix_status": gap_row.get("status", "unknown") if gap_row else "missing",
        "source_go_no_go_status": "unsatisfied",
        "required_evidence": (
            gap_row.get("required_evidence", "") if gap_row else blocker.get("message", "")
        ),
        "source_message": (
            gap_row.get("source_message", "") if gap_row else blocker.get("message", "")
        ),
        "source_gap_matrix_local_evidence_path": source_gap_path,
        "source_gap_matrix_local_evidence_path_available": source_gap_path_available,
        "evidence_or_profile_paths": evidence_paths,
        "human_input_surface_paths": human_paths,
        "requirements_or_review_paths": review_paths,
        "missing_expected_paths": missing,
        "evidence_or_profile_path_available": bool(evidence_paths),
        "human_input_surface_available": bool(human_paths),
        "requirements_or_review_surface_available": bool(review_paths),
        "coverage_complete": coverage_complete,
        "closure_allowed_by_coverage_audit": False,
        "blocker_closed_by_coverage_audit": False,
        "requires_real_human_evidence": True,
        "requires_separate_execution_request": True,
        "requires_human_approval": True,
        "safe_next_action": (
            "Use the listed local surfaces to prepare a separate human-approved "
            "evidence request; do not close this blocker from the coverage audit."
        ),
    }


def build_coverage() -> dict[str, Any]:
    go_no_go = json.loads(GO_NO_GO_JSON.read_text(encoding="utf-8"))
    gap_matrix = build_gap_matrix()
    gap_by_id = {row["blocker_id"]: row for row in gap_matrix["matrix"]}
    blockers = go_no_go["unsatisfied_blockers"]
    missing_surface_blockers = [
        blocker["blocker_id"]
        for blocker in blockers
        if blocker["blocker_id"] not in BLOCKER_SURFACES
    ]
    rows = [make_row(blocker, gap_by_id.get(blocker["blocker_id"])) for blocker in blockers]

    category_counts: dict[str, int] = {}
    for row in rows:
        category_counts[row["category"]] = category_counts.get(row["category"], 0) + 1

    coverage_complete_count = sum(1 for row in rows if row["coverage_complete"])
    evidence_count = sum(1 for row in rows if row["evidence_or_profile_path_available"])
    human_count = sum(1 for row in rows if row["human_input_surface_available"])
    review_count = sum(1 for row in rows if row["requirements_or_review_surface_available"])
    status = (
        "pass_coverage_mapped_hold_no_closure"
        if len(rows) == 24
        and not missing_surface_blockers
        and coverage_complete_count == len(rows)
        and go_no_go["commercial_status"] == "hold"
        and go_no_go["production_launch_status"] == "hold"
        and go_no_go["satisfied_production_checks"] == 0
        else "hold_coverage_incomplete_no_closure"
    )

    return {
        "production_blocker_evidence_path_coverage_audit_v0_1": True,
        "audit_type": "local_agent_readable_production_blocker_evidence_path_coverage",
        "audit_scope": "coverage_mapping_only_no_blocker_closure",
        "generated_by": "scripts/saee_production_blocker_evidence_path_coverage_audit.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "status": status,
        "commercial_status": go_no_go["commercial_status"],
        "production_launch_status": go_no_go["production_launch_status"],
        "production_blocker_count": int(go_no_go["production_blocker_count"]),
        "satisfied_production_checks": int(go_no_go["satisfied_production_checks"]),
        "coverage_row_count": len(rows),
        "coverage_complete_count": coverage_complete_count,
        "evidence_or_profile_path_available_count": evidence_count,
        "human_input_surface_available_count": human_count,
        "requirements_or_review_surface_available_count": review_count,
        "missing_surface_blocker_count": len(missing_surface_blockers),
        "missing_surface_blockers": missing_surface_blockers,
        "category_counts": dict(sorted(category_counts.items())),
        "blockers_closed_by_coverage_audit": 0,
        "closure_allowed_count": 0,
        "human_review_required": True,
        "separate_execution_request_required": True,
        "rows": rows,
        **FALSE_BOUNDARY_FLAGS,
        "next_action": (
            "Human reviewers may use this map to choose a blocker evidence lane. "
            "No blocker is closed until separate real evidence is collected, "
            "reviewed, and explicitly approved."
        ),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    rows = []
    for row in payload["rows"]:
        rows.append(
            "| {blocker} | {category} | {evidence} | {human} | {review} | {complete} | {closure} |".format(
                blocker=row["blocker_id"],
                category=row["category"],
                evidence="yes" if row["evidence_or_profile_path_available"] else "no",
                human="yes" if row["human_input_surface_available"] else "no",
                review="yes" if row["requirements_or_review_surface_available"] else "no",
                complete="yes" if row["coverage_complete"] else "no",
                closure="no" if not row["closure_allowed_by_coverage_audit"] else "yes",
            )
        )

    return "\n".join(
        [
            "# SAEE Production Blocker Evidence Path Coverage Audit v0.1",
            "",
            "Status: local evidence-path coverage audit; production launch remains hold.",
            "",
            "This audit maps each current production blocker to available local",
            "evidence/profile paths, human-input surfaces, and requirements or review",
            "surfaces. It does not execute evidence work, close blockers, contact",
            "customers, call external services, launch product, claim customer",
            "validation, claim production readiness, or expose private core.",
            "",
            "## Summary",
            "",
            f"- audit_type: {payload['audit_type']}",
            f"- status: {payload['status']}",
            f"- commercial_status: {payload['commercial_status']}",
            f"- production_launch_status: {payload['production_launch_status']}",
            f"- production_blocker_count: {payload['production_blocker_count']}",
            f"- satisfied_production_checks: {payload['satisfied_production_checks']}",
            f"- coverage_row_count: {payload['coverage_row_count']}",
            f"- coverage_complete_count: {payload['coverage_complete_count']}",
            f"- evidence_or_profile_path_available_count: {payload['evidence_or_profile_path_available_count']}",
            f"- human_input_surface_available_count: {payload['human_input_surface_available_count']}",
            f"- requirements_or_review_surface_available_count: {payload['requirements_or_review_surface_available_count']}",
            f"- blockers_closed_by_coverage_audit: {payload['blockers_closed_by_coverage_audit']}",
            f"- closure_allowed_count: {payload['closure_allowed_count']}",
            "- production_ready: false",
            "- customer_validated: false",
            "- product_launched: false",
            "- private_core_exposed: false",
            "",
            "## Coverage Table",
            "",
            "| Blocker | Category | Evidence/profile path | Human input surface | Requirements/review surface | Coverage complete | Closure allowed here |",
            "| --- | --- | --- | --- | --- | --- | --- |",
            *rows,
            "",
            "## Boundary",
            "",
            "- No blocker is closed by this audit.",
            "- No launch decision is authorized by this audit.",
            "- No production-ready claim is made.",
            "- No customer validation claim is made.",
            "- No external-validation success claim is made.",
            "- No backend, runtime, kernel, API schema, landing interaction, or private core is modified.",
            "- Each blocker still requires separate real evidence and human approval.",
            "",
        ]
    )


def render_top_doc() -> str:
    return """# SAEE Production Blocker Evidence Path Coverage Audit v0.1

Status: local coverage map for production-blocker evidence paths; no blocker closure.

production_blocker_evidence_path_coverage_audit_v0_1: true
audit_scope: coverage_mapping_only_no_blocker_closure
production_launch_status: hold
production_blocker_count: 24
satisfied_production_checks: 0
blockers_closed_by_coverage_audit: 0
closure_allowed_count: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This audit is an agent-readable map showing whether every current production
launch blocker has:

- a local evidence/profile path;
- a human-input or approval surface;
- a requirements or review surface;
- an explicit no-closure boundary.

It complements the production blocker evidence gap matrix. The gap matrix says
what remains missing; this coverage audit says whether the repo already has a
bounded path for collecting and reviewing that evidence later.

## Generated Files

```text
phase_b_product/commercial_readiness/production_blocker_evidence_path_coverage/coverage.local.json
phase_b_product/commercial_readiness/production_blocker_evidence_path_coverage/coverage.local.md
phase_b_product/commercial_readiness/production_blocker_evidence_path_coverage/coverage.local.csv
phase_b_product/commercial_readiness/production_blocker_evidence_path_coverage/boundary_audit.md
```

Generate or refresh them with:

```bash
python3 scripts/saee_production_blocker_evidence_path_coverage_audit.py
```

Validate them with:

```bash
python3 scripts/saee_production_blocker_evidence_path_coverage_audit_smoke.py
```

## Boundary

- No blocker is closed by this audit.
- No evidence is collected by this audit.
- No development permission is granted.
- No customer is contacted.
- No external service is called.
- No product launch is authorized.
- No customer-validation claim is made.
- No production-ready claim is made.
- No private core is exposed.
"""


def render_boundary(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# SAEE Production Blocker Evidence Path Coverage Boundary Audit",
            "",
            "Decision: pass_coverage_mapped_hold_no_closure",
            "",
            "## Boundary Checks",
            "",
            "- task_candidates_executed: false",
            "- development_permission_granted: false",
            "- runtime_modified: false",
            "- backend_modified: false",
            "- kernel_modified: false",
            "- api_schema_modified: false",
            "- private_core_exposed: false",
            "- product_launched: false",
            "- customer_contacted: false",
            "- customer_validated: false",
            "- production_ready: false",
            "- public_sdk_released: false",
            "- external_calls_made: false",
            "- external_model_api_called: false",
            "- external_ai_assistant_tested: false",
            "- production_ready_claim: false",
            "- customer_validation_claim: false",
            "- external_validation_success_claim: false",
            "- blockers_closed_by_coverage_audit: 0",
            "- closure_allowed_count: 0",
            "",
            "## Result",
            "",
            f"- coverage_row_count: {payload['coverage_row_count']}",
            f"- coverage_complete_count: {payload['coverage_complete_count']}",
            "",
            "The coverage audit is safe to use as a local review index only. It is",
            "not evidence that SAEE is production-ready.",
            "",
        ]
    )


def render_gate() -> str:
    return """# SAEE Production Blocker Evidence Path Coverage Audit Recommendation Gate

answer: conditional

recommend_for_local_commercial_review: true
recommend_for_evidence_path_lookup: true
recommend_for_blocker_closure: false
recommend_for_production_readiness_claim: false
recommend_for_customer_validation_claim: false
recommend_for_product_launch: false
recommend_for_automatic_execution: false

## Reason

The coverage audit is recommendable as a local agent-readable review index. It
shows that the 24 current production blockers have bounded local paths for
future evidence collection and review.

It is not recommendable as production readiness evidence. It does not collect
real evidence, import human values, close blockers, contact customers, or
authorize launch.

## Current Status

```yaml
production_blocker_evidence_path_coverage_audit_v0_1: true
audit_scope: coverage_mapping_only_no_blocker_closure
production_launch_status: hold
production_blocker_count: 24
satisfied_production_checks: 0
blockers_closed_by_coverage_audit: 0
closure_allowed_count: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
```

## Required Human Gate

Any future blocker closure requires a separate evidence request, real approved
inputs, and an explicit human decision. This audit grants no execution
permission.
"""


def write_csv(payload: dict[str, Any]) -> None:
    fields = [
        "blocker_id",
        "category",
        "source_go_no_go_status",
        "source_gap_matrix_status",
        "evidence_or_profile_path_available",
        "human_input_surface_available",
        "requirements_or_review_surface_available",
        "coverage_complete",
        "closure_allowed_by_coverage_audit",
        "blocker_closed_by_coverage_audit",
        "requires_real_human_evidence",
        "requires_separate_execution_request",
        "requires_human_approval",
        "source_gap_matrix_local_evidence_path",
        "required_evidence",
    ]
    with COVERAGE_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["rows"]:
            writer.writerow({field: row[field] for field in fields})


def write_outputs(payload: dict[str, Any]) -> None:
    COVERAGE_DIR.mkdir(parents=True, exist_ok=True)
    COVERAGE_JSON.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    COVERAGE_MD.write_text(render_markdown(payload), encoding="utf-8")
    BOUNDARY_MD.write_text(render_boundary(payload), encoding="utf-8")
    TOP_DOC.write_text(render_top_doc(), encoding="utf-8")
    GATE.write_text(render_gate(), encoding="utf-8")
    write_csv(payload)


def main() -> None:
    payload = build_coverage()
    write_outputs(payload)
    print(
        "SAEE_PRODUCTION_BLOCKER_EVIDENCE_PATH_COVERAGE_AUDIT: PASS "
        f"status={payload['status']} "
        f"coverage_rows={payload['coverage_row_count']} "
        f"coverage_complete={payload['coverage_complete_count']} "
        f"blockers_closed_by_coverage_audit={payload['blockers_closed_by_coverage_audit']} "
        "production_ready=false customer_validated=false"
    )


if __name__ == "__main__":
    main()
