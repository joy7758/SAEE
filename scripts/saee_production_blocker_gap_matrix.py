#!/usr/bin/env python3
"""Build the SAEE production blocker evidence gap matrix.

This script converts the current commercial launch blocker work order into a
per-blocker evidence gap matrix. It is a local review aid only: it does not
close blockers, execute work items, contact customers, call external services,
launch product, claim production readiness, or modify runtime/backend/kernel/API
schema/private-core behavior.
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

from scripts.saee_commercial_evidence_profile import build_profile
from scripts.saee_commercial_launch_blocker_work_order import build_work_order
from scripts.saee_production_evidence_intake_audit import build_intake_audit


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/production_blocker_gap_matrix"
MATRIX_JSON = OUTPUT_DIR / "gap_matrix.local.json"
MATRIX_MD = OUTPUT_DIR / "gap_matrix.local.md"
MATRIX_CSV = OUTPUT_DIR / "gap_matrix.local.csv"
README_PATH = OUTPUT_DIR / "README.md"


DOC_PATH = ROOT / "phase_b_product/commercial_readiness/PRODUCTION_BLOCKER_EVIDENCE_GAP_MATRIX_V0_1.md"


GAP_TYPE_BY_CATEGORY = {
    "auth": "production_auth_evidence_gap",
    "tenant": "production_tenant_isolation_evidence_gap",
    "operations": "production_operations_evidence_gap",
    "support": "staffed_support_and_sla_evidence_gap",
    "privacy_security": "formal_security_privacy_legal_evidence_gap",
    "validation": "real_customer_validation_evidence_gap",
    "billing": "commercial_pricing_payment_revenue_evidence_gap",
    "data_ops": "production_backup_restore_data_operations_evidence_gap",
}


OWNER_LANE_BY_CATEGORY = {
    "auth": "engineering_security",
    "tenant": "engineering_data_security",
    "operations": "operations_engineering",
    "support": "support_operations",
    "privacy_security": "security_legal_privacy",
    "validation": "customer_validation",
    "billing": "commercial_finance_legal",
    "data_ops": "data_operations",
}


EXTERNAL_DEPENDENCY_REQUIRED = {
    "production_identity_provider",
    "oauth_oidc",
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
}


ENGINEERING_IMPLEMENTATION_REQUIRED = {
    "production_identity_provider",
    "oauth_oidc",
    "rbac",
    "tenant_storage_isolation",
    "production_monitoring",
    "external_alert_delivery",
    "tenant_billing_isolation",
    "restore_tested",
    "production_restore_policy",
}


def _category_by_blocker(intake: dict[str, Any]) -> dict[str, dict[str, Any]]:
    mapping: dict[str, dict[str, Any]] = {}
    for category in intake["category_results"]:
        for blocker_id in category["covered_blocker_ids"]:
            # Prefer a category whose intake_id/category matches the blocker category later.
            mapping.setdefault(blocker_id, category)
    return mapping


def _matching_category(
    blocker: dict[str, Any],
    intake: dict[str, Any],
    fallback: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    blocker_id = blocker["blocker_id"]
    category_name = blocker["category"]
    for category in intake["category_results"]:
        if blocker_id in category["covered_blocker_ids"] and (
            category["intake_id"] == category_name
            or category_name in category["intake_id"]
            or category["intake_id"] in category_name
        ):
            return category
    return fallback.get(blocker_id)


def _matrix_item(blocker: dict[str, Any], category: dict[str, Any] | None) -> dict[str, Any]:
    blocker_id = blocker["blocker_id"]
    completion = category.get("completion", {}) if category else {}
    complete_count = sum(1 for value in completion.values() if value)
    total_count = len(completion)
    local_ready = bool(category.get("ready")) if category else False
    local_path = str(category.get("local_path", "")) if category else ""
    env_var = str(category.get("env_var", "")) if category else ""
    blocker_category = str(blocker["category"])

    return {
        "blocker_id": blocker_id,
        "category": blocker_category,
        "status": "open",
        "required_evidence": blocker["required_evidence"],
        "source_message": blocker["source_message"],
        "local_evidence_path": local_path,
        "local_evidence_env_var": env_var,
        "local_evidence_file_exists": bool(category.get("evidence_file_exists")) if category else False,
        "local_evidence_ready": local_ready,
        "local_completion_checks_passed": complete_count,
        "local_completion_checks_total": total_count,
        "evidence_gap_type": GAP_TYPE_BY_CATEGORY.get(
            blocker_category, "production_evidence_gap"
        ),
        "owner_review_lane": OWNER_LANE_BY_CATEGORY.get(
            blocker_category, "human_commercial_review"
        ),
        "external_dependency_required": blocker_id in EXTERNAL_DEPENDENCY_REQUIRED,
        "engineering_implementation_required": blocker_id in ENGINEERING_IMPLEMENTATION_REQUIRED,
        "human_approval_required": True,
        "requires_separate_execution_request": True,
        "closure_allowed_by_matrix": False,
        "can_close_without_evidence": False,
        "next_required_action": (
            "Create a separate human-approved evidence task for this blocker; "
            "do not close it from the gap matrix."
        ),
    }


def build_gap_matrix() -> dict[str, Any]:
    """Build the production blocker evidence gap matrix."""

    work_order = build_work_order()
    intake = build_intake_audit()
    profile = build_profile()
    fallback = _category_by_blocker(intake)
    blockers = work_order["blockers"]
    matrix = [
        _matrix_item(blocker, _matching_category(blocker, intake, fallback))
        for blocker in blockers
    ]
    category_counts: dict[str, int] = {}
    for item in matrix:
        category_counts[item["category"]] = category_counts.get(item["category"], 0) + 1

    return {
        "matrix_type": "saee_production_blocker_evidence_gap_matrix",
        "matrix_version": "v0.1",
        "matrix_scope": "local_public_shell_commercial_blocker_review",
        "generated_by": "scripts/saee_production_blocker_gap_matrix.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_work_order": "phase_b_product/commercial_readiness/COMMERCIAL_LAUNCH_BLOCKER_WORK_ORDER_V0_1.json",
        "source_profile": "phase_b_product/commercial_readiness/commercial_evidence_profile/local_evidence_profile.json",
        "production_blocker_count": int(work_order["production_blocker_count"]),
        "open_blocker_count": len(matrix),
        "blockers_closed_by_matrix": 0,
        "local_evidence_categories": int(profile["local_evidence_categories"]),
        "all_profile_paths_present": bool(profile["all_profile_paths_present"]),
        "production_launch_status": work_order["production_launch_status"],
        "work_order_status": work_order["work_order_status"],
        "category_counts": dict(sorted(category_counts.items())),
        "matrix": matrix,
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
        "matrix_status": "hold",
        "next_action": (
            "Human reviewers should select one blocker lane, create a separate "
            "approved evidence task, and keep all launch claims false until the "
            "required evidence is complete and reviewed."
        ),
    }


def render_markdown(matrix: dict[str, Any]) -> str:
    rows = []
    for item in matrix["matrix"]:
        rows.append(
            "| {blocker} | {category} | {lane} | {local_ready} | {complete}/{total} | {gap} | {closure} |".format(
                blocker=item["blocker_id"],
                category=item["category"],
                lane=item["owner_review_lane"],
                local_ready="yes" if item["local_evidence_ready"] else "no",
                complete=item["local_completion_checks_passed"],
                total=item["local_completion_checks_total"],
                gap=item["evidence_gap_type"],
                closure="no" if not item["closure_allowed_by_matrix"] else "yes",
            )
        )

    return "\n".join(
        [
            "# SAEE Production Blocker Evidence Gap Matrix v0.1",
            "",
            "Status: local production-blocker evidence gap matrix; production launch remains hold.",
            "",
            "This matrix maps each current production launch blocker to the local",
            "evidence packet that currently covers it, the missing evidence class,",
            "and the review lane that must approve future closure. It does not",
            "execute blocker work, close blockers, contact customers, call external",
            "services, launch product, or claim production readiness.",
            "",
            "## Summary",
            "",
            f"- matrix_scope: {matrix['matrix_scope']}",
            f"- production_launch_status: {matrix['production_launch_status']}",
            f"- production_blocker_count: {matrix['production_blocker_count']}",
            f"- open_blocker_count: {matrix['open_blocker_count']}",
            f"- blockers_closed_by_matrix: {matrix['blockers_closed_by_matrix']}",
            f"- local_evidence_categories: {matrix['local_evidence_categories']}",
            f"- all_profile_paths_present: {str(matrix['all_profile_paths_present']).lower()}",
            "- production_ready: false",
            "- customer_validated: false",
            "- product_launched: false",
            "- private_core_exposed: false",
            "",
            "## Category Counts",
            "",
            *[
                f"- {category}: {count}"
                for category, count in matrix["category_counts"].items()
            ],
            "",
            "## Gap Matrix",
            "",
            "| Blocker | Category | Owner lane | Local evidence ready | Local checks | Gap type | Closure allowed here |",
            "| --- | --- | --- | --- | --- | --- | --- |",
            *rows,
            "",
            "## Boundary",
            "",
            "- No blocker is closed by this matrix.",
            "- No execution is authorized by this matrix.",
            "- No production-ready claim is made.",
            "- No customer validation claim is made.",
            "- No product launch is authorized.",
            "- No customer contact is authorized.",
            "- No backend runtime, kernel, API schema, or private core is modified.",
            "- Each blocker requires a separate human-approved evidence task before closure.",
            "",
        ]
    )


def render_readme() -> str:
    return """# SAEE Production Blocker Evidence Gap Matrix

Status: local production-blocker evidence gap review, not production readiness.

This directory contains generated local review artifacts that map each current
production-launch blocker to the local evidence packet that currently covers it
and the remaining evidence gap.

It does not execute blocker work, close blockers, contact customers, call
external services, launch product, claim customer validation, claim production
readiness, or expose private core.

Primary files:

```text
gap_matrix.local.json
gap_matrix.local.md
gap_matrix.local.csv
```

Generate them with:

```bash
python3 scripts/saee_production_blocker_gap_matrix.py
```

Boundary:

```yaml
matrix_scope: local_public_shell_commercial_blocker_review
production_launch_status: hold
production_blocker_count: 24
open_blocker_count: 24
blockers_closed_by_matrix: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
external_calls_made: false
```
"""


def write_csv(matrix: dict[str, Any]) -> None:
    fields = [
        "blocker_id",
        "category",
        "status",
        "owner_review_lane",
        "evidence_gap_type",
        "local_evidence_path",
        "local_evidence_ready",
        "local_completion_checks_passed",
        "local_completion_checks_total",
        "external_dependency_required",
        "engineering_implementation_required",
        "closure_allowed_by_matrix",
        "human_approval_required",
        "requires_separate_execution_request",
        "required_evidence",
    ]
    with MATRIX_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in matrix["matrix"]:
            writer.writerow({field: item[field] for field in fields})


def write_outputs(matrix: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MATRIX_JSON.write_text(json.dumps(matrix, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MATRIX_MD.write_text(render_markdown(matrix), encoding="utf-8")
    README_PATH.write_text(render_readme(), encoding="utf-8")
    write_csv(matrix)


def main() -> None:
    matrix = build_gap_matrix()
    write_outputs(matrix)
    print(
        "SAEE_PRODUCTION_BLOCKER_GAP_MATRIX: PASS "
        f"production_blockers={matrix['production_blocker_count']} "
        f"open_blockers={matrix['open_blocker_count']} "
        f"blockers_closed_by_matrix={matrix['blockers_closed_by_matrix']} "
        "production_ready=false customer_validated=false"
    )


if __name__ == "__main__":
    main()
