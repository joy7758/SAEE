#!/usr/bin/env python3
"""Audit Phase 2 data/operations evidence gaps.

This runner compares the Phase 2 evidence task requirements against the
existing local public-shell operations and data-operations evidence files. It
is a planning and review aid only: it does not deploy monitoring, contact
vendors, send alerts, activate on-call, run restore tests, modify production
data paths, process customer data, close blockers, or claim production
readiness.
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
    / "phase_b_product/commercial_readiness/phase_2_data_operations_evidence_task/phase_2_data_operations_evidence_task.local.json"
)
OPERATIONS_EVIDENCE_PATH = (
    ROOT / "phase_b_product/commercial_readiness/operations_evidence/operations_evidence.local.json"
)
DATA_OPERATIONS_EVIDENCE_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/data_operations_evidence/data_operations_evidence.local.json"
)
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/phase_2_data_operations_gap_audit"
OUTPUT_JSON = OUTPUT_DIR / "phase_2_data_operations_gap_audit.local.json"
OUTPUT_MD = OUTPUT_DIR / "phase_2_data_operations_gap_audit.md"
OUTPUT_CSV = OUTPUT_DIR / "phase_2_data_operations_gap_audit.csv"
README_PATH = OUTPUT_DIR / "README.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/PHASE_2_DATA_OPERATIONS_GAP_AUDIT_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PHASE_2_DATA_OPERATIONS_GAP_AUDIT_RECOMMENDATION_GATE.md"


LOCAL_PROFILE_ENV = {
    "SAEE_PRODUCTION_AUTH_EVIDENCE_PATH": "phase_b_product/commercial_readiness/auth_evidence/auth_evidence.local.json",
    "SAEE_PRODUCTION_SUPPORT_EVIDENCE_PATH": "phase_b_product/commercial_readiness/support_evidence/support_evidence.local.json",
    "SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH": str(
        DATA_OPERATIONS_EVIDENCE_PATH.relative_to(ROOT)
    ),
    "SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH": str(
        OPERATIONS_EVIDENCE_PATH.relative_to(ROOT)
    ),
    "SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH": "phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_security_legal_evidence.local.json",
    "SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH": "phase_b_product/commercial_readiness/billing_revenue_evidence/billing_revenue_evidence.local.json",
    "SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH": "phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_isolation_evidence.local.json",
    "SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH": "phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence.local.json",
}


EXTERNAL_DEPENDENCY_BLOCKERS = {
    "production_monitoring",
    "external_alert_delivery",
    "on_call_rotation",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def evidence_value(
    item: dict[str, Any], operations: dict[str, Any], data_operations: dict[str, Any]
) -> bool:
    key = item["evidence_key"]
    file_type = item["evidence_file_type"]
    if file_type == "production_operations_evidence":
        return operations.get(key) is True
    if file_type == "production_data_operations_evidence":
        return data_operations.get(key) is True
    return False


def classify_item(item: dict[str, Any], local_value: bool) -> str:
    if local_value:
        return "local_public_shell_evidence_present_requires_human_production_approval"
    if item["blocker_id"] in EXTERNAL_DEPENDENCY_BLOCKERS:
        return "missing_external_or_human_production_evidence"
    return "missing_human_production_evidence"


def build_gap_rows(
    task: dict[str, Any],
    operations: dict[str, Any],
    data_operations: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in task["required_evidence_items"]:
        local_value = evidence_value(item, operations, data_operations)
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
                "external_dependency_required": blocker_id
                in EXTERNAL_DEPENDENCY_BLOCKERS,
                "next_action": (
                    "Human must provide real monitoring, alert delivery, and operations coverage evidence."
                    if blocker_id in EXTERNAL_DEPENDENCY_BLOCKERS
                    else "Human must approve remaining production restore evidence and boundary reviews."
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
    operations = read_json(OPERATIONS_EVIDENCE_PATH)
    data_operations = read_json(DATA_OPERATIONS_EVIDENCE_PATH)
    default_go_no_go = evaluate_commercial_go_no_go(load_settings({}))
    local_profile_go_no_go = evaluate_commercial_go_no_go(load_settings(LOCAL_PROFILE_ENV))
    rows = build_gap_rows(task, operations, data_operations)
    blocker_summary = summarize_by_blocker(rows)
    local_present = sum(1 for row in rows if row["local_public_shell_value"])
    missing = len(rows) - local_present

    return {
        "audit_type": "saee_phase_2_data_operations_gap_audit",
        "audit_version": "v0.1",
        "audit_scope": "local_public_shell_to_production_data_operations_gap_review",
        "generated_by": "scripts/saee_phase2_data_operations_gap_audit.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_task": str(TASK_PATH.relative_to(ROOT)),
        "source_operations_evidence": str(OPERATIONS_EVIDENCE_PATH.relative_to(ROOT)),
        "source_data_operations_evidence": str(
            DATA_OPERATIONS_EVIDENCE_PATH.relative_to(ROOT)
        ),
        "target_blockers": [
            "production_monitoring",
            "external_alert_delivery",
            "on_call_rotation",
            "restore_tested",
            "production_restore_policy",
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
        "restore_test_authorized": False,
        "monitoring_deployment_authorized": False,
        "external_alert_delivery_authorized": False,
        "on_call_activation_authorized": False,
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
        "monitoring_vendor_contacted_by_codex": False,
        "alert_provider_contacted_by_codex": False,
        "external_alert_sent_by_codex": False,
        "on_call_rotation_activated": False,
        "restore_test_executed": False,
        "production_data_path_modified": False,
        "live_restore_performed": False,
        "next_action": (
            "Human owners must replace local public-shell evidence with real "
            "approved production operations and restore evidence before any "
            "Phase 2 blocker can close."
        ),
    }


def write_readme() -> None:
    README_PATH.write_text(
        """# SAEE Phase 2 Data/Operations Gap Audit

Status: local gap audit only; no blocker closure.

This directory compares Phase 2 production monitoring, alerting, on-call,
restore-test, and restore-policy evidence requirements against existing local
public-shell operations and data-operations evidence. It is a
commercial-readiness review surface, not an execution task.

Boundary:

- no monitoring vendor contacted
- no alert provider contacted
- no external alert sent
- no on-call rotation activated
- no restore test executed
- no production data path modified
- no customer data processing
- no blocker closure
- no production-ready claim
- no backend, runtime, kernel, API schema, or private core modification
""",
        encoding="utf-8",
    )


def markdown_report(audit: dict[str, Any]) -> str:
    lines = [
        "# SAEE Phase 2 Data/Operations Gap Audit v0.1",
        "",
        "Status: local public-shell gap audit only; no blocker closure.",
        "",
        "This audit compares Phase 2 production evidence requirements against",
        "existing local public-shell operations and data-operations evidence.",
        "Local evidence may support human review, but it is not accepted as",
        "production blocker closure by this audit.",
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
            "- No monitoring deployment is authorized.",
            "- No external alert delivery is authorized.",
            "- No on-call activation is authorized.",
            "- No restore test is executed or authorized.",
            "- No production data path is modified.",
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
        """# SAEE Phase 2 Data/Operations Gap Audit v0.1

phase_2_data_operations_gap_audit_v0_1: true
audit_scope: local_public_shell_to_production_data_operations_gap_review
required_evidence_item_count: 26
accepted_for_blocker_closure_count: 0
blockers_closed_by_audit: 0
execution_authorized: false
evidence_collection_authorized: false
restore_test_authorized: false
monitoring_deployment_authorized: false
external_alert_delivery_authorized: false
on_call_activation_authorized: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This audit compares Phase 2 data/operations production evidence requirements
against existing local public-shell evidence. It records which evidence keys
are locally present and which still need production-grade human approval.

It is an audit only. It does not authorize execution, close blockers, run
restore tests, deploy monitoring, send alerts, activate on-call, or claim
production readiness.

## Target Blockers

- production_monitoring
- external_alert_delivery
- on_call_rotation
- restore_tested
- production_restore_policy
""",
        encoding="utf-8",
    )


def write_gate() -> None:
    GATE_PATH.write_text(
        """# SAEE Phase 2 Data/Operations Gap Audit Recommendation Gate

answer: conditional
recommend_for_human_review: true
recommend_for_blocker_closure: false
recommend_for_execution_authorization: false
recommend_for_restore_test_execution: false
recommend_for_monitoring_deployment: false
recommend_for_external_alert_delivery: false
recommend_for_on_call_activation: false
recommend_for_production_launch: false

## Reason

This audit is useful because it separates local public-shell evidence from
production-grade operations and restore evidence. It does not close any
blocker or authorize any external action.

## Boundary

```yaml
audit_scope: local_public_shell_to_production_data_operations_gap_review
accepted_for_blocker_closure_count: 0
blockers_closed_by_audit: 0
execution_authorized: false
evidence_collection_authorized: false
restore_test_authorized: false
monitoring_deployment_authorized: false
external_alert_delivery_authorized: false
on_call_activation_authorized: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
```

## Next Action

Human reviewers may use the gap table to decide whether to authorize a
separate production evidence collection task. Until then, all Phase 2 blockers
remain open.
""",
        encoding="utf-8",
    )


def write_outputs(audit: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(markdown_report(audit), encoding="utf-8")
    OUTPUT_CSV.write_text(csv_text(audit["gap_rows"]), encoding="utf-8")
    write_readme()
    write_doc()
    write_gate()


def main() -> None:
    audit = build_audit()
    write_outputs(audit)
    print(
        "SAEE_PHASE2_DATA_OPERATIONS_GAP_AUDIT: PASS "
        f"required_items={audit['required_evidence_item_count']} "
        f"local_present={audit['local_public_shell_present_count']} "
        f"missing_production={audit['missing_production_evidence_count']} "
        f"blockers_closed_by_audit={audit['blockers_closed_by_audit']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
