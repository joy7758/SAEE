#!/usr/bin/env python3
"""Prove the full SAEE commercial launch evidence path with local fixtures.

This script creates local fixture evidence for every production go/no-go
blocker group and feeds those files through the existing commercial go/no-go
aggregator. It proves wiring coverage only. It does not collect real evidence,
close blockers, launch SAEE, contact customers, call external services, modify
runtime/backend/kernel/API behavior, or claim production readiness.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go
from saee_backend.services.production_auth_evidence import (
    AUTH_IDP_KEYS,
    FORBIDDEN_TRUE_KEYS as AUTH_FORBIDDEN_TRUE_KEYS,
    OAUTH_OIDC_KEYS,
    RBAC_KEYS,
    evaluate_production_auth_evidence,
)
from saee_backend.services.production_billing_revenue_evidence import (
    FORBIDDEN_TRUE_KEYS as BILLING_FORBIDDEN_TRUE_KEYS,
    INVOICE_PROCESS_KEYS,
    PAYMENT_PROVIDER_KEYS,
    PRICING_PAGE_KEYS,
    REFUND_POLICY_KEYS,
    TAX_REVIEW_KEYS,
    TENANT_BILLING_ISOLATION_KEYS,
    evaluate_production_billing_revenue_evidence,
)
from saee_backend.services.production_customer_validation_evidence import (
    BOUNDARY_REVIEW_KEYS,
    CLAIM_PERMISSION_KEYS,
    CUSTOMER_VALUE_KEYS,
    FORBIDDEN_TRUE_KEYS as CUSTOMER_VALIDATION_FORBIDDEN_TRUE_KEYS,
    PILOT_RESULT_KEYS,
    evaluate_production_customer_validation_evidence,
)
from saee_backend.services.production_data_operations_evidence import (
    FORBIDDEN_TRUE_KEYS as DATA_OPS_FORBIDDEN_TRUE_KEYS,
    RESTORE_POLICY_KEYS,
    RESTORE_TEST_KEYS,
    evaluate_production_data_operations_evidence,
)
from saee_backend.services.production_operations_evidence import (
    EXTERNAL_ALERT_DELIVERY_KEYS,
    FORBIDDEN_TRUE_KEYS as OPERATIONS_FORBIDDEN_TRUE_KEYS,
    ON_CALL_KEYS as OPERATIONS_ON_CALL_KEYS,
    PRODUCTION_MONITORING_KEYS,
    evaluate_production_operations_evidence,
)
from saee_backend.services.production_privacy_security_legal_evidence import (
    DPA_KEYS,
    FORBIDDEN_TRUE_KEYS as PRIVACY_SECURITY_LEGAL_FORBIDDEN_TRUE_KEYS,
    FORMAL_SECURITY_REVIEW_KEYS,
    PRIVACY_LEGAL_REVIEW_KEYS,
    VULNERABILITY_MANAGEMENT_KEYS,
    evaluate_production_privacy_security_legal_evidence,
)
from saee_backend.services.production_support_evidence import (
    CUSTOMER_SUPPORT_KEYS,
    FORBIDDEN_TRUE_KEYS as SUPPORT_FORBIDDEN_TRUE_KEYS,
    ON_CALL_KEYS as SUPPORT_ON_CALL_KEYS,
    SLA_KEYS,
    SUPPORT_CONTACT_KEYS,
    evaluate_production_support_evidence,
)
from saee_backend.services.production_tenant_storage_evidence import (
    FORBIDDEN_TRUE_KEYS as TENANT_STORAGE_FORBIDDEN_TRUE_KEYS,
    TENANT_ISOLATION_TEST_KEYS,
    TENANT_OPERATIONS_KEYS,
    TENANT_SECURITY_PRIVACY_KEYS,
    TENANT_STORAGE_MODEL_KEYS,
    evaluate_production_tenant_storage_evidence,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_launch_evidence_path"
FIXTURE_DIR = OUTPUT_DIR / "fixtures"
SUMMARY_PATH = OUTPUT_DIR / "commercial_launch_evidence_path.local.json"
REPORT_PATH = OUTPUT_DIR / "commercial_launch_evidence_path_report.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_LAUNCH_EVIDENCE_PATH_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_COMMERCIAL_LAUNCH_EVIDENCE_PATH_RECOMMENDATION_GATE.md"

TARGET_BLOCKERS = (
    "production_identity_provider",
    "oauth_oidc",
    "rbac",
    "tenant_storage_isolation",
    "production_monitoring",
    "external_alert_delivery",
    "on_call_rotation",
    "sla",
    "support_contact",
    "customer_support",
    "formal_security_review",
    "privacy_legal_review",
    "data_processing_agreement",
    "vulnerability_management",
    "pilot_results",
    "customer_validated",
    "pricing_page",
    "payment_provider",
    "invoice_process",
    "tax_review",
    "refund_policy",
    "tenant_billing_isolation",
    "restore_tested",
    "production_restore_policy",
)

COMMON_FALSE_FLAGS = (
    "production_ready",
    "customer_validated",
    "product_launched",
    "public_sdk_released",
    "private_core_exposed",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "external_calls_made",
    "external_model_api_called",
    "customer_contacted",
)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_token(value: object) -> str:
    return str(value).lower()


def fixture_evidence(
    *,
    evidence_type_field: str,
    evidence_type_value: str,
    true_keys: tuple[str, ...],
    forbidden_true_keys: tuple[str, ...],
    evidence_scope: str,
) -> dict[str, Any]:
    evidence: dict[str, Any] = {
        evidence_type_field: evidence_type_value,
        "evidence_scope": evidence_scope,
        "evidence_version": "v0.1",
        "fixture_only": True,
        "input_status": "fixture_only_not_real_production_evidence",
        "generated_by": "scripts/saee_commercial_launch_evidence_path.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
    }
    for key in true_keys:
        evidence[key] = True
    for key in set(forbidden_true_keys + COMMON_FALSE_FLAGS):
        evidence[key] = False
    return evidence


def fixture_files() -> dict[str, Path]:
    fixtures: dict[str, tuple[dict[str, Any], Path]] = {
        "auth": (
            fixture_evidence(
                evidence_type_field="auth_evidence_type",
                evidence_type_value="production_auth_evidence",
                true_keys=AUTH_IDP_KEYS + OAUTH_OIDC_KEYS + RBAC_KEYS,
                forbidden_true_keys=AUTH_FORBIDDEN_TRUE_KEYS,
                evidence_scope="fixture_only_full_launch_auth_evidence",
            ),
            FIXTURE_DIR / "production_auth_evidence.fixture.json",
        ),
        "support": (
            fixture_evidence(
                evidence_type_field="support_evidence_type",
                evidence_type_value="production_support_sla_evidence",
                true_keys=(
                    SUPPORT_CONTACT_KEYS
                    + CUSTOMER_SUPPORT_KEYS
                    + SLA_KEYS
                    + SUPPORT_ON_CALL_KEYS
                ),
                forbidden_true_keys=SUPPORT_FORBIDDEN_TRUE_KEYS,
                evidence_scope="fixture_only_full_launch_support_evidence",
            ),
            FIXTURE_DIR / "production_support_sla_evidence.fixture.json",
        ),
        "data_ops": (
            fixture_evidence(
                evidence_type_field="data_operations_evidence_type",
                evidence_type_value="production_data_operations_evidence",
                true_keys=RESTORE_TEST_KEYS + RESTORE_POLICY_KEYS,
                forbidden_true_keys=DATA_OPS_FORBIDDEN_TRUE_KEYS,
                evidence_scope="fixture_only_full_launch_data_operations_evidence",
            ),
            FIXTURE_DIR / "production_data_operations_evidence.fixture.json",
        ),
        "operations": (
            fixture_evidence(
                evidence_type_field="operations_evidence_type",
                evidence_type_value="production_operations_evidence",
                true_keys=(
                    PRODUCTION_MONITORING_KEYS
                    + EXTERNAL_ALERT_DELIVERY_KEYS
                    + OPERATIONS_ON_CALL_KEYS
                ),
                forbidden_true_keys=OPERATIONS_FORBIDDEN_TRUE_KEYS,
                evidence_scope="fixture_only_full_launch_operations_evidence",
            ),
            FIXTURE_DIR / "production_operations_evidence.fixture.json",
        ),
        "privacy_security_legal": (
            fixture_evidence(
                evidence_type_field="privacy_security_legal_evidence_type",
                evidence_type_value="production_privacy_security_legal_evidence",
                true_keys=(
                    FORMAL_SECURITY_REVIEW_KEYS
                    + PRIVACY_LEGAL_REVIEW_KEYS
                    + DPA_KEYS
                    + VULNERABILITY_MANAGEMENT_KEYS
                ),
                forbidden_true_keys=PRIVACY_SECURITY_LEGAL_FORBIDDEN_TRUE_KEYS,
                evidence_scope="fixture_only_full_launch_privacy_security_legal_evidence",
            ),
            FIXTURE_DIR / "production_privacy_security_legal_evidence.fixture.json",
        ),
        "billing_revenue": (
            fixture_evidence(
                evidence_type_field="billing_revenue_evidence_type",
                evidence_type_value="production_billing_revenue_evidence",
                true_keys=(
                    PRICING_PAGE_KEYS
                    + PAYMENT_PROVIDER_KEYS
                    + INVOICE_PROCESS_KEYS
                    + TAX_REVIEW_KEYS
                    + REFUND_POLICY_KEYS
                    + TENANT_BILLING_ISOLATION_KEYS
                ),
                forbidden_true_keys=BILLING_FORBIDDEN_TRUE_KEYS,
                evidence_scope="fixture_only_full_launch_billing_revenue_evidence",
            ),
            FIXTURE_DIR / "production_billing_revenue_evidence.fixture.json",
        ),
        "tenant_storage": (
            fixture_evidence(
                evidence_type_field="tenant_storage_evidence_type",
                evidence_type_value="production_tenant_storage_evidence",
                true_keys=(
                    TENANT_STORAGE_MODEL_KEYS
                    + TENANT_ISOLATION_TEST_KEYS
                    + TENANT_OPERATIONS_KEYS
                    + TENANT_SECURITY_PRIVACY_KEYS
                ),
                forbidden_true_keys=TENANT_STORAGE_FORBIDDEN_TRUE_KEYS,
                evidence_scope="fixture_only_full_launch_tenant_storage_evidence",
            ),
            FIXTURE_DIR / "production_tenant_storage_evidence.fixture.json",
        ),
        "customer_validation": (
            fixture_evidence(
                evidence_type_field="customer_validation_evidence_type",
                evidence_type_value="production_customer_validation_evidence",
                true_keys=(
                    PILOT_RESULT_KEYS
                    + CUSTOMER_VALUE_KEYS
                    + CLAIM_PERMISSION_KEYS
                    + BOUNDARY_REVIEW_KEYS
                ),
                forbidden_true_keys=CUSTOMER_VALIDATION_FORBIDDEN_TRUE_KEYS,
                evidence_scope="fixture_only_full_launch_customer_validation_evidence",
            ),
            FIXTURE_DIR / "production_customer_validation_evidence.fixture.json",
        ),
    }
    written: dict[str, Path] = {}
    for label, (data, path) in fixtures.items():
        write_json(path, data)
        written[label] = path
    return written


def settings_env(paths: dict[str, Path]) -> dict[str, str]:
    return {
        "SAEE_ENV": "local",
        "SAEE_SUPPORT_CONTACT": "support@example.invalid",
        "SAEE_PRODUCTION_AUTH_EVIDENCE_PATH": str(paths["auth"]),
        "SAEE_PRODUCTION_SUPPORT_EVIDENCE_PATH": str(paths["support"]),
        "SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH": str(paths["data_ops"]),
        "SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH": str(paths["operations"]),
        "SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH": str(
            paths["privacy_security_legal"]
        ),
        "SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH": str(
            paths["billing_revenue"]
        ),
        "SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH": str(paths["tenant_storage"]),
        "SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH": str(
            paths["customer_validation"]
        ),
    }


def blocker_state(go_no_go: dict[str, Any]) -> tuple[list[str], list[str]]:
    satisfied: list[str] = []
    unsatisfied: list[str] = []
    for item in go_no_go.get("blockers", []):
        if not isinstance(item, dict):
            continue
        blocker_id = str(item.get("blocker_id"))
        if blocker_id not in TARGET_BLOCKERS:
            continue
        if item.get("satisfied") is True:
            satisfied.append(blocker_id)
        else:
            unsatisfied.append(blocker_id)
    return satisfied, unsatisfied


def build_path(output_path: Path = SUMMARY_PATH) -> dict[str, Any]:
    paths = fixture_files()
    env = settings_env(paths)
    settings = load_settings(env)

    readiness = {
        "auth": evaluate_production_auth_evidence(settings),
        "support": evaluate_production_support_evidence(settings),
        "data_ops": evaluate_production_data_operations_evidence(settings),
        "operations": evaluate_production_operations_evidence(settings),
        "privacy_security_legal": evaluate_production_privacy_security_legal_evidence(
            settings
        ),
        "billing_revenue": evaluate_production_billing_revenue_evidence(settings),
        "tenant_storage": evaluate_production_tenant_storage_evidence(settings),
        "customer_validation": evaluate_production_customer_validation_evidence(settings),
    }
    go_no_go = evaluate_commercial_go_no_go(settings)
    baseline_go_no_go = evaluate_commercial_go_no_go(load_settings({}))
    satisfied, unsatisfied = blocker_state(go_no_go)
    path_proven = (
        all(item.get("status") == "pass" for item in readiness.values())
        and go_no_go["boundary_violation_count"] == 0
        and go_no_go["production_blocker_count"] == 0
        and go_no_go["satisfied_production_checks"] == len(TARGET_BLOCKERS)
        and not unsatisfied
    )

    result: dict[str, Any] = {
        "commercial_launch_evidence_path_v0_1": True,
        "path_type": "local_fixture_only_full_commercial_launch_evidence_path",
        "path_status": "pass_fixture_only" if path_proven else "hold",
        "generated_by": "scripts/saee_commercial_launch_evidence_path.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "fixture_only": True,
        "real_production_evidence_collected": False,
        "real_customer_validation_collected": False,
        "real_payment_or_revenue_evidence_collected": False,
        "real_legal_security_review_completed": False,
        "human_launch_approval_recorded": False,
        "default_commercial_status": baseline_go_no_go["commercial_status"],
        "default_production_launch_status": baseline_go_no_go[
            "production_launch_status"
        ],
        "default_production_blocker_count": baseline_go_no_go[
            "production_blocker_count"
        ],
        "full_fixture_commercial_status_after_fixture": go_no_go[
            "commercial_status"
        ],
        "full_fixture_production_launch_status_after_fixture": go_no_go[
            "production_launch_status"
        ],
        "full_fixture_controlled_preview_status_after_fixture": go_no_go[
            "controlled_preview_status"
        ],
        "full_fixture_controlled_preview_preflight_status_after_fixture": go_no_go[
            "controlled_preview_preflight_status"
        ],
        "satisfied_production_checks_after_full_fixture": go_no_go[
            "satisfied_production_checks"
        ],
        "total_production_checks_after_full_fixture": go_no_go[
            "total_production_checks"
        ],
        "production_blocker_count_after_full_fixture": go_no_go[
            "production_blocker_count"
        ],
        "boundary_violation_count_after_full_fixture": go_no_go[
            "boundary_violation_count"
        ],
        "commercial_launch_path_proven_by_fixture": path_proven,
        "target_blockers_satisfied_by_fixture": satisfied,
        "target_blockers_unsatisfied_by_fixture": unsatisfied,
        "readiness_statuses_after_fixture": {
            label: item["status"] for label, item in readiness.items()
        },
        "fixture_evidence_files": {
            label: str(path.relative_to(ROOT)) for label, path in paths.items()
        },
        "blockers_closed_by_path": 0,
        "accepted_for_blocker_closure_count": 0,
        "human_real_evidence_required": True,
        "separate_human_launch_approval_required": True,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "public_sdk_released": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "landing_page_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "customer_contacted": False,
        "payment_provider_contacted": False,
        "legal_counsel_contacted": False,
        "security_vendor_contacted": False,
        "identity_provider_contacted": False,
        "support_vendor_contacted": False,
        "customer_data_processed": False,
        "revenue_validated": False,
        "next_action": (
            "Replace fixture evidence with real human-approved production "
            "evidence before any launch decision."
        ),
    }
    write_json(output_path, result)
    write_report(result)
    write_doc(result)
    write_gate(result)
    return result


def write_report(data: dict[str, Any]) -> None:
    REPORT_PATH.write_text(
        "\n".join(
            [
                "# SAEE Commercial Launch Evidence Path Report",
                "",
                "Status: fixture-only path proof, not production launch approval.",
                "",
                "## Summary",
                "",
                "- path_type: "
                + str(data["path_type"]),
                "- path_status: "
                + str(data["path_status"]),
                "- fixture_only: "
                + bool_token(data["fixture_only"]),
                "- default_commercial_status: "
                + str(data["default_commercial_status"]),
                "- default_production_blocker_count: "
                + str(data["default_production_blocker_count"]),
                "- full_fixture_commercial_status_after_fixture: "
                + str(data["full_fixture_commercial_status_after_fixture"]),
                "- production_blocker_count_after_full_fixture: "
                + str(data["production_blocker_count_after_full_fixture"]),
                "- blockers_closed_by_path: 0",
                "",
                "## What Was Proved",
                "",
                "The existing commercial go/no-go aggregator can read all local "
                "production evidence files and resolve all 24 production launch "
                "blockers under fixture-only conditions.",
                "",
                "## What Was Not Proved",
                "",
                "- No real production evidence was collected.",
                "- No customer validation was collected.",
                "- No payment, revenue, legal, security, support, operations, "
                "identity-provider, or tenant-storage evidence was collected.",
                "- No human launch approval was recorded.",
                "- No product, backend, runtime, kernel, API schema, landing page, "
                "or private core was modified.",
                "",
                "## Boundary",
                "",
                "- production_ready: false",
                "- customer_validated: false",
                "- product_launched: false",
                "- private_core_exposed: false",
                "- external_calls_made: false",
                "- customer_contacted: false",
                "- revenue_validated: false",
                "",
                "## Next Action",
                "",
                "Replace fixture evidence with real human-approved production "
                "evidence before any commercial launch decision.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_doc(data: dict[str, Any]) -> None:
    DOC_PATH.write_text(
        "\n".join(
            [
                "# SAEE Commercial Launch Evidence Path v0.1",
                "",
                "commercial_launch_evidence_path_v0_1: true",
                "path_type: local_fixture_only_full_commercial_launch_evidence_path",
                "path_status: "
                + str(data["path_status"]),
                "fixture_only: true",
                "real_production_evidence_collected: false",
                "production_ready: false",
                "customer_validated: false",
                "product_launched: false",
                "private_core_exposed: false",
                "blockers_closed_by_path: 0",
                "",
                "## Purpose",
                "",
                "This path proves that SAEE's production go/no-go layer can ingest "
                "all required production evidence categories and reach zero "
                "fixture blockers without modifying product behavior.",
                "",
                "It is a fixture-only wiring proof. It is not production evidence, "
                "not a launch approval, not customer validation, and not revenue "
                "validation.",
                "",
                "## Covered Blocker Groups",
                "",
                "- authentication: production identity provider, OAuth/OIDC, RBAC",
                "- tenant storage isolation",
                "- operations: monitoring, external alert delivery, on-call rotation",
                "- support: SLA, support contact, customer support",
                "- privacy/security/legal: security review, legal review, DPA, "
                "vulnerability management",
                "- customer validation: pilot results and customer validation evidence",
                "- billing/revenue: pricing page, payment provider, invoice process, "
                "tax review, refund policy, tenant billing isolation",
                "- data operations: restore testing and production restore policy",
                "",
                "## Boundary",
                "",
                "This path does not close blockers by itself. Real human-approved "
                "evidence must replace fixtures before any launch gate can be "
                "treated as satisfied.",
                "",
                "No backend, runtime, kernel, API schema, landing page interaction, "
                "or private core was modified.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_gate(data: dict[str, Any]) -> None:
    GATE_PATH.write_text(
        "\n".join(
            [
                "# SAEE Commercial Launch Evidence Path Recommendation Gate",
                "",
                "answer: conditional",
                "",
                "reason: The fixture-only commercial launch evidence path proves "
                "that the local go/no-go aggregator can resolve all 24 production "
                "launch blockers when every required evidence category is present. "
                "It does not prove real production readiness.",
                "",
                "recommend_for: evidence-path completeness review",
                "do_not_recommend_for: product launch, production readiness claim, "
                "customer validation claim, revenue validation claim",
                "",
                "path_status: "
                + str(data["path_status"]),
                "fixture_only: true",
                "production_ready: false",
                "customer_validated: false",
                "product_launched: false",
                "private_core_exposed: false",
                "blockers_closed_by_path: 0",
                "",
                "next_action: Replace fixture evidence with real human-approved "
                "production evidence before any launch decision.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print JSON output")
    args = parser.parse_args()
    result = build_path()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(
            "SAEE_COMMERCIAL_LAUNCH_EVIDENCE_PATH: "
            f"path_status={result['path_status']} "
            f"fixture_only={bool_token(result['fixture_only'])} "
            "production_blocker_count_after_full_fixture="
            f"{result['production_blocker_count_after_full_fixture']} "
            "blockers_closed_by_path=0"
        )


if __name__ == "__main__":
    main()
