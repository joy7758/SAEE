#!/usr/bin/env python3
"""Audit Phase 1 identity/tenant evidence gaps.

This runner compares the Phase 1 evidence task requirements against the
existing local public-shell evidence files. It is a planning and review aid
only: it does not contact identity providers, fetch JWKS, validate production
tokens, run migrations, process customer data, close blockers, or claim
production readiness.
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


TASK_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_task/phase_1_identity_tenant_evidence_task.local.json"
)
AUTH_EVIDENCE_PATH = ROOT / "phase_b_product/commercial_readiness/auth_evidence/auth_evidence.local.json"
TENANT_EVIDENCE_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_isolation_evidence.local.json"
)
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/phase_1_identity_tenant_gap_audit"
OUTPUT_JSON = OUTPUT_DIR / "phase_1_identity_tenant_gap_audit.local.json"
OUTPUT_MD = OUTPUT_DIR / "phase_1_identity_tenant_gap_audit.md"
OUTPUT_CSV = OUTPUT_DIR / "phase_1_identity_tenant_gap_audit.csv"
README_PATH = OUTPUT_DIR / "README.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/PHASE_1_IDENTITY_TENANT_GAP_AUDIT_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PHASE_1_IDENTITY_TENANT_GAP_AUDIT_RECOMMENDATION_GATE.md"


LOCAL_PROFILE_ENV = {
    "SAEE_PRODUCTION_AUTH_EVIDENCE_PATH": str(AUTH_EVIDENCE_PATH.relative_to(ROOT)),
    "SAEE_PRODUCTION_SUPPORT_EVIDENCE_PATH": "phase_b_product/commercial_readiness/support_evidence/support_evidence.local.json",
    "SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH": "phase_b_product/commercial_readiness/data_operations_evidence/data_operations_evidence.local.json",
    "SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH": "phase_b_product/commercial_readiness/operations_evidence/operations_evidence.local.json",
    "SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH": "phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_security_legal_evidence.local.json",
    "SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH": "phase_b_product/commercial_readiness/billing_revenue_evidence/billing_revenue_evidence.local.json",
    "SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH": str(TENANT_EVIDENCE_PATH.relative_to(ROOT)),
    "SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH": "phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence.local.json",
}


EXTERNAL_DEPENDENCY_BLOCKERS = {
    "production_identity_provider",
    "oauth_oidc",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def evidence_value(item: dict[str, Any], auth: dict[str, Any], tenant: dict[str, Any]) -> bool:
    key = item["evidence_key"]
    file_type = item["evidence_file_type"]
    if file_type == "production_auth_evidence":
        return auth.get(key) is True
    if file_type == "production_tenant_storage_evidence":
        return tenant.get(key) is True
    return False


def classify_item(item: dict[str, Any], local_value: bool) -> str:
    if local_value:
        return "local_public_shell_evidence_present_requires_human_production_approval"
    if item["blocker_id"] in EXTERNAL_DEPENDENCY_BLOCKERS:
        return "missing_external_or_human_production_evidence"
    return "missing_human_production_evidence"


def build_gap_rows(task: dict[str, Any], auth: dict[str, Any], tenant: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in task["required_evidence_items"]:
        local_value = evidence_value(item, auth, tenant)
        rows.append(
            {
                "blocker_id": item["blocker_id"],
                "evidence_file_type": item["evidence_file_type"],
                "evidence_key": item["evidence_key"],
                "local_public_shell_value": local_value,
                "accepted_for_blocker_closure": False,
                "gap_status": classify_item(item, local_value),
                "external_dependency_required": item["blocker_id"]
                in EXTERNAL_DEPENDENCY_BLOCKERS,
                "human_review_required": True,
                "notes": (
                    "Local evidence is review input only; it does not close the production blocker."
                    if local_value
                    else "Production-grade human-approved evidence is still missing."
                ),
            }
        )
    return rows


def summarize_by_blocker(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    blocker_ids = []
    for row in rows:
        if row["blocker_id"] not in blocker_ids:
            blocker_ids.append(row["blocker_id"])
    summary = []
    for blocker_id in blocker_ids:
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
                "external_dependency_required": blocker_id in EXTERNAL_DEPENDENCY_BLOCKERS,
                "next_action": (
                    "Human must provide real identity-provider/OIDC evidence."
                    if blocker_id in EXTERNAL_DEPENDENCY_BLOCKERS
                    else "Human must approve remaining production evidence and boundary reviews."
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
    task = read_json(TASK_PATH)
    auth = read_json(AUTH_EVIDENCE_PATH)
    tenant = read_json(TENANT_EVIDENCE_PATH)
    default_go_no_go = evaluate_commercial_go_no_go(load_settings({}))
    local_profile_go_no_go = evaluate_commercial_go_no_go(load_settings(LOCAL_PROFILE_ENV))
    rows = build_gap_rows(task, auth, tenant)
    blocker_summary = summarize_by_blocker(rows)
    local_present = sum(1 for row in rows if row["local_public_shell_value"])
    missing = len(rows) - local_present

    return {
        "audit_type": "saee_phase_1_identity_tenant_gap_audit",
        "audit_version": "v0.1",
        "audit_scope": "local_public_shell_to_production_evidence_gap_review",
        "generated_by": "scripts/saee_phase1_identity_tenant_gap_audit.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_task": str(TASK_PATH.relative_to(ROOT)),
        "source_auth_evidence": str(AUTH_EVIDENCE_PATH.relative_to(ROOT)),
        "source_tenant_storage_evidence": str(TENANT_EVIDENCE_PATH.relative_to(ROOT)),
        "target_blockers": [
            "production_identity_provider",
            "oauth_oidc",
            "rbac",
            "tenant_storage_isolation",
        ],
        "required_evidence_item_count": len(rows),
        "local_public_shell_present_count": local_present,
        "missing_production_evidence_count": missing,
        "accepted_for_blocker_closure_count": 0,
        "blockers_ready_to_close": [],
        "blockers_closed_by_audit": 0,
        "default_go_no_go": {
            "commercial_status": default_go_no_go["commercial_status"],
            "production_launch_status": default_go_no_go["production_launch_status"],
            "satisfied_production_checks": default_go_no_go["satisfied_production_checks"],
            "production_blocker_count": default_go_no_go["production_blocker_count"],
            "total_production_checks": default_go_no_go["total_production_checks"],
        },
        "local_profile_go_no_go": local_public_shell_go_no_go_summary(local_profile_go_no_go),
        "blocker_summary": blocker_summary,
        "gap_rows": rows,
        "human_review_required": True,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
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
            "Human owners must replace local public-shell evidence with real "
            "approved production evidence before any Phase 1 blocker can close."
        ),
    }


def write_readme() -> None:
    README_PATH.write_text(
        """# SAEE Phase 1 Identity/Tenant Gap Audit

Status: local gap audit only; no blocker closure.

This directory compares Phase 1 production identity/OIDC/RBAC/tenant-storage
evidence requirements against existing local public-shell evidence. It is a
commercial-readiness review surface, not an execution task.

Boundary:

- no identity provider contacted
- no JWKS fetched
- no production token validation
- no storage migration
- no customer data processing
- no blocker closure
- no production-ready claim
- no backend, runtime, kernel, API schema, or private core modification
""",
        encoding="utf-8",
    )


def markdown_report(audit: dict[str, Any]) -> str:
    lines = [
        "# SAEE Phase 1 Identity/Tenant Gap Audit v0.1",
        "",
        "Status: local public-shell gap audit only; no blocker closure.",
        "",
        "This audit compares Phase 1 production evidence requirements against",
        "existing local public-shell auth and tenant-storage evidence. Local",
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
        f"- private_core_exposed: {str(audit['private_core_exposed']).lower()}",
        "",
        "## Blocker Summary",
        "",
        "| Blocker | Required Items | Local Present | Missing Production Evidence | Ready To Close | Next Action |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for item in audit["blocker_summary"]:
        lines.append(
            "| {blocker_id} | {required_items} | {local_public_shell_present} | "
            "{missing_production_evidence} | {ready_to_close} | {next_action} |".format(
                **item
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- No backend modified.",
            "- No runtime modified.",
            "- No kernel modified.",
            "- No API schema modified.",
            "- No identity provider contacted.",
            "- No JWKS fetched.",
            "- No production token validation performed.",
            "- No storage migration run.",
            "- No customer data processed.",
            "- No product launched.",
            "- No production-ready claim made.",
            "- No private core exposed.",
            "",
            "## Next Action",
            "",
            audit["next_action"],
            "",
        ]
    )
    return "\n".join(lines)


def write_doc(audit: dict[str, Any]) -> None:
    DOC_PATH.write_text(markdown_report(audit), encoding="utf-8")


def write_gate(audit: dict[str, Any]) -> None:
    GATE_PATH.write_text(
        f"""# SAEE Phase 1 Identity/Tenant Gap Audit Recommendation Gate

answer: conditional

recommend_for_human_review: true
recommend_for_blocker_closure: false
recommend_for_production_launch: false

reason:
The audit makes Phase 1 identity/OIDC/RBAC/tenant-storage evidence gaps
explicit. It is useful for commercial readiness review, but it does not provide
production identity-provider evidence, production token validation, production
RBAC approval, security/privacy approval, or tenant-storage production
authorization.

evidence:
- required_evidence_item_count: {audit['required_evidence_item_count']}
- local_public_shell_present_count: {audit['local_public_shell_present_count']}
- missing_production_evidence_count: {audit['missing_production_evidence_count']}
- accepted_for_blocker_closure_count: {audit['accepted_for_blocker_closure_count']}
- blockers_closed_by_audit: {audit['blockers_closed_by_audit']}
- local_profile_go_no_go_satisfied_checks: {audit['local_profile_go_no_go']['satisfied_production_checks']}/{audit['local_profile_go_no_go']['total_production_checks']}
- local_public_shell_review_candidate_count: {audit['local_profile_go_no_go']['local_public_shell_review_candidate_count']}

boundary:
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
- backend_modified: false
- runtime_modified: false
- kernel_modified: false
- api_schema_modified: false
- external_calls_made: false

next_action:
Human owners must replace local public-shell evidence with real approved
production evidence before any Phase 1 blocker can close.
""",
        encoding="utf-8",
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    audit = build_audit()
    write_readme()
    OUTPUT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(markdown_report(audit), encoding="utf-8")
    OUTPUT_CSV.write_text(csv_text(audit["gap_rows"]), encoding="utf-8")
    write_doc(audit)
    write_gate(audit)
    print(
        "SAEE_PHASE1_IDENTITY_TENANT_GAP_AUDIT: PASS "
        f"required_items={audit['required_evidence_item_count']} "
        f"local_present={audit['local_public_shell_present_count']} "
        f"missing_production={audit['missing_production_evidence_count']} "
        f"blockers_closed_by_audit={audit['blockers_closed_by_audit']} "
        f"production_ready={str(audit['production_ready']).lower()}"
    )


if __name__ == "__main__":
    main()
