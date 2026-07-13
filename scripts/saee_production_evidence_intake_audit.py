#!/usr/bin/env python3
"""Audit local production evidence intake paths for SAEE launch review.

This script aggregates the existing local public-shell evidence packets and
maps them to the commercial go/no-go blockers. It does not contact customers,
call external services, run pilots, deploy production infrastructure, modify
runtime/backend/kernel/API schema behavior, or close blockers without real
human-approved production evidence.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, NamedTuple


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go
from saee_backend.services.production_auth_evidence import evaluate_production_auth_evidence
from saee_backend.services.production_billing_revenue_evidence import (
    evaluate_production_billing_revenue_evidence,
)
from saee_backend.services.production_customer_validation_evidence import (
    evaluate_production_customer_validation_evidence,
)
from saee_backend.services.production_data_operations_evidence import (
    evaluate_production_data_operations_evidence,
)
from saee_backend.services.production_operations_evidence import (
    evaluate_production_operations_evidence,
)
from saee_backend.services.production_privacy_security_legal_evidence import (
    evaluate_production_privacy_security_legal_evidence,
)
from saee_backend.services.production_support_evidence import (
    evaluate_production_support_evidence,
)
from saee_backend.services.production_tenant_storage_evidence import (
    evaluate_production_tenant_storage_evidence,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/production_evidence_intake"
OUTPUT_JSON = OUTPUT_DIR / "production_evidence_intake.local.json"
OUTPUT_MD = OUTPUT_DIR / "production_evidence_intake.local.md"
README_PATH = OUTPUT_DIR / "README.md"


class IntakeSpec(NamedTuple):
    intake_id: str
    name: str
    env_var: str
    local_path: str
    evaluator: Callable[[Any], dict[str, Any]]
    path_configured_key: str
    ready_key: str
    completion_keys: tuple[str, ...]
    blocker_ids: tuple[str, ...]


INTAKE_SPECS: tuple[IntakeSpec, ...] = (
    IntakeSpec(
        intake_id="auth",
        name="Production Auth Evidence",
        env_var="SAEE_PRODUCTION_AUTH_EVIDENCE_PATH",
        local_path="phase_b_product/commercial_readiness/auth_evidence/auth_evidence.local.json",
        evaluator=evaluate_production_auth_evidence,
        path_configured_key="auth_evidence_path_configured",
        ready_key="production_auth_ready",
        completion_keys=(
            "production_identity_provider_evidence_complete",
            "oauth_oidc_evidence_complete",
            "rbac_evidence_complete",
        ),
        blocker_ids=("production_identity_provider", "oauth_oidc", "rbac"),
    ),
    IntakeSpec(
        intake_id="support",
        name="Production Support/SLA Evidence",
        env_var="SAEE_PRODUCTION_SUPPORT_EVIDENCE_PATH",
        local_path="phase_b_product/commercial_readiness/support_evidence/support_evidence.local.json",
        evaluator=evaluate_production_support_evidence,
        path_configured_key="support_evidence_path_configured",
        ready_key="production_support_available",
        completion_keys=(
            "support_contact_evidence_complete",
            "customer_support_evidence_complete",
            "sla_evidence_complete",
            "on_call_rotation_evidence_complete",
        ),
        blocker_ids=("support_contact", "customer_support", "sla", "on_call_rotation"),
    ),
    IntakeSpec(
        intake_id="data_operations",
        name="Production Data Operations Evidence",
        env_var="SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH",
        local_path=(
            "phase_b_product/commercial_readiness/data_operations_evidence/"
            "production_data_operations_evidence.combined_profile.local.json"
        ),
        evaluator=evaluate_production_data_operations_evidence,
        path_configured_key="data_operations_evidence_path_configured",
        ready_key="production_data_operations_ready",
        completion_keys=(
            "restore_test_evidence_complete",
            "production_restore_policy_evidence_complete",
        ),
        blocker_ids=("restore_tested", "production_restore_policy"),
    ),
    IntakeSpec(
        intake_id="operations",
        name="Production Operations Evidence",
        env_var="SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH",
        local_path=(
            "phase_b_product/commercial_readiness/operations_evidence/"
            "production_operations_evidence.combined_profile.local.json"
        ),
        evaluator=evaluate_production_operations_evidence,
        path_configured_key="operations_evidence_path_configured",
        ready_key="production_operations_ready",
        completion_keys=(
            "production_monitoring_evidence_complete",
            "external_alert_delivery_evidence_complete",
            "on_call_rotation_evidence_complete",
        ),
        blocker_ids=(
            "production_monitoring",
            "external_alert_delivery",
            "on_call_rotation",
        ),
    ),
    IntakeSpec(
        intake_id="privacy_security_legal",
        name="Production Privacy/Security/Legal Evidence",
        env_var="SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH",
        local_path=(
            "phase_b_product/commercial_readiness/privacy_security_legal_evidence/"
            "privacy_security_legal_evidence.local.json"
        ),
        evaluator=evaluate_production_privacy_security_legal_evidence,
        path_configured_key="privacy_security_legal_evidence_path_configured",
        ready_key="production_privacy_security_legal_ready",
        completion_keys=(
            "formal_security_review_evidence_complete",
            "privacy_legal_review_evidence_complete",
            "data_processing_agreement_evidence_complete",
            "vulnerability_management_evidence_complete",
        ),
        blocker_ids=(
            "formal_security_review",
            "privacy_legal_review",
            "data_processing_agreement",
            "vulnerability_management",
        ),
    ),
    IntakeSpec(
        intake_id="billing_revenue",
        name="Production Billing/Revenue Evidence",
        env_var="SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH",
        local_path=(
            "phase_b_product/commercial_readiness/billing_revenue_evidence/"
            "billing_revenue_evidence.local.json"
        ),
        evaluator=evaluate_production_billing_revenue_evidence,
        path_configured_key="billing_revenue_evidence_path_configured",
        ready_key="production_billing_revenue_ready",
        completion_keys=(
            "pricing_page_evidence_complete",
            "payment_provider_evidence_complete",
            "invoice_process_evidence_complete",
            "tax_review_evidence_complete",
            "refund_policy_evidence_complete",
            "tenant_billing_isolation_evidence_complete",
        ),
        blocker_ids=(
            "pricing_page",
            "payment_provider",
            "invoice_process",
            "tax_review",
            "refund_policy",
            "tenant_billing_isolation",
        ),
    ),
    IntakeSpec(
        intake_id="tenant_storage",
        name="Production Tenant Storage Evidence",
        env_var="SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH",
        local_path=(
            "phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/"
            "tenant_storage_isolation_evidence.local.json"
        ),
        evaluator=evaluate_production_tenant_storage_evidence,
        path_configured_key="tenant_storage_evidence_path_configured",
        ready_key="production_tenant_storage_evidence_complete",
        completion_keys=(
            "tenant_storage_model_evidence_complete",
            "tenant_isolation_test_evidence_complete",
            "tenant_operations_evidence_complete",
            "tenant_security_privacy_evidence_complete",
        ),
        blocker_ids=("tenant_storage_isolation",),
    ),
    IntakeSpec(
        intake_id="customer_validation",
        name="Production Customer Validation Evidence",
        env_var="SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH",
        local_path=(
            "phase_b_product/commercial_readiness/customer_validation_evidence/"
            "customer_validation_evidence.local.json"
        ),
        evaluator=evaluate_production_customer_validation_evidence,
        path_configured_key="customer_validation_evidence_path_configured",
        ready_key="production_customer_validation_ready",
        completion_keys=(
            "pilot_results_evidence_complete",
            "customer_value_evidence_complete",
            "claim_permission_evidence_complete",
            "boundary_review_evidence_complete",
            "customer_validation_evidence_complete",
        ),
        blocker_ids=("pilot_results", "customer_validated"),
    ),
)


BOUNDARY_FALSE_KEYS = (
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
    "external_ai_assistant_tested",
)


def _local_evidence_env() -> dict[str, str]:
    return {spec.env_var: spec.local_path for spec in INTAKE_SPECS}


def _evaluate_spec(spec: IntakeSpec, env: dict[str, str]) -> dict[str, Any]:
    path = ROOT / spec.local_path
    result = spec.evaluator(load_settings(env))
    completion = {key: bool(result.get(key)) for key in spec.completion_keys}
    boundary = {
        key: result.get(key, False)
        for key in BOUNDARY_FALSE_KEYS
        if key in result
    }
    return {
        "intake_id": spec.intake_id,
        "name": spec.name,
        "env_var": spec.env_var,
        "local_path": spec.local_path,
        "evidence_file_exists": path.exists(),
        "status": result.get("status"),
        "path_configured": bool(result.get(spec.path_configured_key)),
        "ready_key": spec.ready_key,
        "ready": bool(result.get(spec.ready_key)),
        "completion": completion,
        "covered_blocker_ids": list(spec.blocker_ids),
        "boundary": boundary,
    }


def build_intake_audit() -> dict[str, Any]:
    env = _local_evidence_env()
    category_results = [_evaluate_spec(spec, env) for spec in INTAKE_SPECS]
    go_no_go = evaluate_commercial_go_no_go(load_settings(env))
    local_public_shell_review_candidates = (
        int(go_no_go["total_production_checks"])
        - int(go_no_go["production_blocker_count"])
    )
    all_blocker_ids = [item["blocker_id"] for item in go_no_go["blockers"]]

    return {
        "intake_audit_type": "saee_production_evidence_intake_audit",
        "intake_audit_version": "v0.1",
        "intake_scope": "local_public_shell_evidence_intake_audit",
        "generated_by": "scripts/saee_production_evidence_intake_audit.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "local_evidence_categories_reviewed": len(category_results),
        "expected_evidence_categories": len(INTAKE_SPECS),
        "all_local_evidence_files_present": all(
            item["evidence_file_exists"] for item in category_results
        ),
        "all_local_evidence_paths_configured": all(
            item["path_configured"] for item in category_results
        ),
        "all_evidence_categories_ready": all(item["ready"] for item in category_results),
        "category_results": category_results,
        "commercial_go_no_go": {
            "commercial_status": go_no_go["commercial_status"],
            "controlled_preview_status": go_no_go["controlled_preview_status"],
            "production_launch_status": go_no_go["production_launch_status"],
            "production_blocker_count": go_no_go["total_production_checks"],
            "total_production_checks": go_no_go["total_production_checks"],
            "blockers_closed_by_intake": 0,
            "local_public_shell_review_candidate_count": local_public_shell_review_candidates,
            "local_profile_unsatisfied_blocker_count": go_no_go["production_blocker_count"],
            "unsatisfied_blocker_ids": [
                item["blocker_id"] for item in go_no_go["unsatisfied_blockers"]
            ],
            "open_blocker_ids": all_blocker_ids,
        },
        "human_review_required": True,
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
        "intake_status": "hold",
        "next_action": (
            "Human reviewers must replace local public-shell evidence with real "
            "approved production evidence before any blocker can close."
        ),
    }


def render_markdown(audit: dict[str, Any]) -> str:
    rows = []
    for item in audit["category_results"]:
        complete_count = sum(1 for value in item["completion"].values() if value)
        total_count = len(item["completion"])
        rows.append(
            "| {id} | {status} | {path} | {ready} | {complete}/{total} | {blockers} |".format(
                id=item["intake_id"],
                status=item["status"],
                path="yes" if item["evidence_file_exists"] else "no",
                ready="yes" if item["ready"] else "no",
                complete=complete_count,
                total=total_count,
                blockers=", ".join(item["covered_blocker_ids"]),
            )
        )

    go = audit["commercial_go_no_go"]
    return "\n".join(
        [
            "# SAEE Production Evidence Intake Audit v0.1",
            "",
            "Status: local public-shell evidence intake audit; production launch remains hold.",
            "",
            "This audit gathers the current local evidence packets into one",
            "commercial go/no-go intake view. It does not create real production",
            "evidence, contact customers, call external services, close blockers,",
            "launch the product, or claim production readiness.",
            "",
            "## Summary",
            "",
            f"- intake_scope: {audit['intake_scope']}",
            f"- local_evidence_categories_reviewed: {audit['local_evidence_categories_reviewed']}",
            f"- all_local_evidence_files_present: {str(audit['all_local_evidence_files_present']).lower()}",
            f"- all_local_evidence_paths_configured: {str(audit['all_local_evidence_paths_configured']).lower()}",
            f"- all_evidence_categories_ready: {str(audit['all_evidence_categories_ready']).lower()}",
            f"- production_launch_status: {go['production_launch_status']}",
            f"- production_blocker_count: {go['production_blocker_count']}",
            f"- total_production_checks: {go['total_production_checks']}",
            f"- blockers_closed_by_intake: {go['blockers_closed_by_intake']}",
            f"- local_public_shell_review_candidate_count: {go['local_public_shell_review_candidate_count']}",
            "- production_ready: false",
            "- customer_validated: false",
            "- product_launched: false",
            "- private_core_exposed: false",
            "",
            "## Category Results",
            "",
            "| Category | Status | File exists | Ready | Complete checks | Covered blockers |",
            "| --- | --- | --- | --- | --- | --- |",
            *rows,
            "",
            "## Boundary",
            "",
            "- No runtime modified.",
            "- No backend modified.",
            "- No kernel modified.",
            "- No API schema modified.",
            "- No private core exposed.",
            "- No customer contacted.",
            "- No external service called.",
            "- No product launched.",
            "- No production readiness claim made.",
            "- No customer validation claim made.",
            "",
            "## Next Action",
            "",
            audit["next_action"],
            "",
        ]
    )


def write_readme(audit: dict[str, Any]) -> None:
    go = audit["commercial_go_no_go"]
    README_PATH.write_text(
        f"""# SAEE Production Evidence Intake

Status: local public-shell evidence intake audit, not production readiness.

This directory contains a generated intake audit over the current local
commercial-readiness evidence packets. It helps human reviewers see which
evidence paths are present and how they map to commercial go/no-go blockers.

It does not create production evidence, contact customers, call external
services, close blockers, launch product, claim customer validation, or expose
private core.

Primary files:

```text
production_evidence_intake.local.json
production_evidence_intake.local.md
```

Generate them with:

```bash
python3 scripts/saee_production_evidence_intake_audit.py
```

Boundary:

```yaml
intake_scope: local_public_shell_evidence_intake_audit
local_evidence_categories_reviewed: {audit['local_evidence_categories_reviewed']}
production_launch_status: {go['production_launch_status']}
production_blocker_count: {go['production_blocker_count']}
total_production_checks: {go['total_production_checks']}
blockers_closed_by_intake: {go['blockers_closed_by_intake']}
local_public_shell_review_candidate_count: {go['local_public_shell_review_candidate_count']}
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
external_calls_made: false
```
""",
        encoding="utf-8",
    )


def write_outputs(audit: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MD.write_text(render_markdown(audit), encoding="utf-8")
    write_readme(audit)


def main() -> None:
    audit = build_intake_audit()
    write_outputs(audit)
    go = audit["commercial_go_no_go"]
    print(
        "SAEE_PRODUCTION_EVIDENCE_INTAKE_AUDIT: PASS "
        f"categories={audit['local_evidence_categories_reviewed']} "
        f"production_launch_status={go['production_launch_status']} "
        f"blockers_closed_by_intake={go['blockers_closed_by_intake']} "
        "production_ready=false customer_validated=false"
    )


if __name__ == "__main__":
    main()
