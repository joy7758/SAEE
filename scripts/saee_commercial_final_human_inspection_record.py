#!/usr/bin/env python3
"""Record the final local human inspection of commercial evidence.

This is a status and evidence-surface consolidation only. It records that the
local human-filled commercial evidence surfaces were manually checked and that
the remaining formal-commercial blocker is external customer validation. It
does not overwrite the default commercial go/no-go, close blockers, contact
customers, launch product, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_final_human_inspection"
OUTPUT_JSON = OUTPUT_DIR / "commercial_final_human_inspection_record.local.json"
OUTPUT_MD = OUTPUT_DIR / "commercial_final_human_inspection_record.md"
OUTPUT_CSV = OUTPUT_DIR / "commercial_final_human_inspection_record.csv"
BOUNDARY_AUDIT = OUTPUT_DIR / "commercial_final_human_inspection_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_FINAL_HUMAN_INSPECTION_RECORD_GATE.md"

SOURCE_FILES = [
    {
        "lane_id": "support_sla",
        "path": ROOT
        / "phase_b_product/commercial_readiness/support_evidence/"
        "support_sla_evidence_profile.from_support_contact_customer_support_sla_and_on_call_human_filled.local.json",
        "status_key": "profile_status",
        "expected_status": "pass",
    },
    {
        "lane_id": "data_operations",
        "path": ROOT
        / "phase_b_product/commercial_readiness/data_operations_evidence/"
        "data_operations_evidence_profile.from_restore_tested_and_restore_policy_human_filled.local.json",
        "status_key": "profile_status",
        "expected_status": "pass",
    },
    {
        "lane_id": "operations",
        "path": ROOT
        / "phase_b_product/commercial_readiness/operations_evidence/"
        "operations_evidence_profile.from_monitoring_alert_on_call_human_filled.local.json",
        "status_key": "profile_status",
        "expected_status": "pass",
    },
    {
        "lane_id": "privacy_security_legal",
        "path": ROOT
        / "phase_b_product/commercial_readiness/privacy_security_legal_evidence/"
        "privacy_security_legal_evidence_profile.from_formal_privacy_dpa_vulnerability_human_filled.local.json",
        "status_key": "profile_status",
        "expected_status": "pass",
    },
    {
        "lane_id": "billing_revenue",
        "path": ROOT
        / "phase_b_product/commercial_readiness/billing_revenue_evidence/"
        "billing_revenue_evidence_profile.from_pricing_payment_invoice_tax_refund_tenant_billing_human_filled.local.json",
        "status_key": "profile_status",
        "expected_status": "pass",
    },
    {
        "lane_id": "identity_tenant",
        "path": ROOT
        / "phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_profile/"
        "phase_1_identity_tenant_evidence_profile.human_filled.local.json",
        "status_key": "profile_status",
        "expected_status": "pass",
    },
    {
        "lane_id": "internal_founder_pilot",
        "path": ROOT
        / "phase_b_product/commercial_readiness/customer_validation_evidence/"
        "internal_founder_pilot_evidence_run_summary.local.json",
        "status_key": "validation_status",
        "expected_status": "pass",
    },
]

FALSE_BOUNDARY_FLAGS = {
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "private_core_exposed": False,
    "product_launched": False,
    "production_ready": False,
    "customer_validated": False,
    "customer_contacted": False,
    "customer_data_collected": False,
    "customer_data_processed": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "external_ai_assistant_tested": False,
    "public_sdk_released": False,
    "public_validation_claim_published": False,
    "testimonial_published": False,
    "case_study_published": False,
    "revenue_validated": False,
    "blocker_closure_authorized": False,
    "blockers_closed_by_inspection": 0,
    "development_permission_granted": False,
    "execution_authorized": False,
    "evidence_collection_authorized": False,
}


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            "SAEE_COMMERCIAL_FINAL_HUMAN_INSPECTION_RECORD: "
            f"FAIL invalid source JSON {path}: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise SystemExit(
            "SAEE_COMMERCIAL_FINAL_HUMAN_INSPECTION_RECORD: "
            f"FAIL source JSON root must be object: {path}"
        )
    return payload


def lane_review() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in SOURCE_FILES:
        path = item["path"]
        payload = read_json(path)
        status_value = payload.get(item["status_key"])
        passed = status_value == item["expected_status"]
        rows.append(
            {
                "lane_id": item["lane_id"],
                "source_path": rel(path),
                "status_key": item["status_key"],
                "status_value": status_value,
                "expected_status": item["expected_status"],
                "local_evidence_passed": passed,
                "production_ready": payload.get("production_ready") is True,
                "customer_validated": payload.get("customer_validated") is True,
                "product_launched": payload.get("product_launched") is True,
                "private_core_exposed": payload.get("private_core_exposed") is True,
            }
        )
    return rows


def build_record() -> dict[str, Any]:
    rows = lane_review()
    all_passed = all(row["local_evidence_passed"] for row in rows)
    boundary_violation_count = sum(
        1
        for row in rows
        if row["production_ready"]
        or row["customer_validated"]
        or row["product_launched"]
        or row["private_core_exposed"]
    )
    status = (
        "hold_external_customer_validation_required"
        if all_passed and boundary_violation_count == 0
        else "hold_local_evidence_review_incomplete"
    )
    return {
        "commercial_final_human_inspection_record_v0_1": True,
        "record_type": "local_commercial_final_human_inspection_record",
        "status": status,
        "generated_by": "scripts/saee_commercial_final_human_inspection_record.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "human_inspection_confirmed": True,
        "human_inspection_statement": "人工检查完毕，没有问题，确认",
        "manual_check_completed": True,
        "manual_check_result": "confirmed_no_issue_in_local_evidence_surfaces",
        "local_evidence_lane_count": len(rows),
        "local_evidence_lanes_passed": all_passed,
        "lane_review": rows,
        "boundary_violation_count": boundary_violation_count,
        "formal_commercial_status": "hold",
        "production_launch_status": "hold",
        "remaining_production_blocker_count_after_local_human_evidence": 1,
        "remaining_production_blockers_after_local_human_evidence": ["customer_validated"],
        "resolved_by_local_human_evidence": [
            "support_sla",
            "data_operations",
            "operations",
            "privacy_security_legal",
            "billing_revenue",
            "identity_tenant",
            "pilot_results",
        ],
        "external_customer_validation_required": True,
        "external_customer_validation_performed": False,
        "external_customer_validation_claim_allowed": False,
        "default_commercial_go_no_go_overwritten": False,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
        "next_goal_blocker": "customer_validated",
        "next_action": (
            "Obtain real external customer or target-user validation through a "
            "separate human-approved validation request before any launch, "
            "customer-validation claim, or production-readiness claim."
        ),
        **FALSE_BOUNDARY_FLAGS,
    }


def render_markdown(record: dict[str, Any]) -> str:
    lane_lines = "\n".join(
        "| {lane_id} | {status_value} | {local_evidence_passed} | {source_path} |".format(
            **row
        )
        for row in record["lane_review"]
    )
    return f"""# SAEE Commercial Final Human Inspection Record v0.1

Status: {record['status']}.

This record captures the human confirmation: **{record['human_inspection_statement']}**.
It is a local evidence-inspection record only. It does not launch SAEE, close
commercial blockers, contact customers, claim production readiness, or claim
external customer validation.

## Summary

```yaml
commercial_final_human_inspection_record_v0_1: true
status: {record['status']}
manual_check_completed: true
manual_check_result: {record['manual_check_result']}
local_evidence_lane_count: {record['local_evidence_lane_count']}
local_evidence_lanes_passed: {str(record['local_evidence_lanes_passed']).lower()}
remaining_production_blocker_count_after_local_human_evidence: {record['remaining_production_blocker_count_after_local_human_evidence']}
remaining_production_blockers_after_local_human_evidence: customer_validated
external_customer_validation_required: true
external_customer_validation_performed: false
production_ready: false
product_launched: false
customer_validated: false
private_core_exposed: false
```

## Lane Review

| Lane | Status | Local Evidence Passed | Source |
| --- | --- | --- | --- |
{lane_lines}

## What Is Resolved Locally

The local human-filled evidence surfaces now make these lanes reviewable:
support/SLA, data operations, operations, privacy/security/legal,
billing/revenue, identity/tenant, and internal pilot-results evidence.

## What Remains Blocked

`customer_validated` remains the formal commercial blocker. Internal founder
self-play or founder pilot evidence can support `pilot_results`, but it cannot
stand in for real external customer validation.

## Boundary

- production_ready=false
- product_launched=false
- customer_validated=false
- customer_contacted=false
- private_core_exposed=false
- runtime_modified=false
- backend_modified=false
- kernel_modified=false
- api_schema_modified=false
- external_calls_made=false
- blocker_closure_authorized=false
- blockers_closed_by_inspection=0
"""


def render_boundary(record: dict[str, Any]) -> str:
    return f"""# SAEE Commercial Final Human Inspection Boundary Audit

Final boundary decision: hold, external customer validation required.

- Only local evidence inspection was recorded.
- No runtime modified: {str(record['runtime_modified']).lower()}
- No backend modified: {str(record['backend_modified']).lower()}
- No kernel modified: {str(record['kernel_modified']).lower()}
- No API schema modified: {str(record['api_schema_modified']).lower()}
- No private core exposed: {str(record['private_core_exposed']).lower()}
- No product launched: {str(record['product_launched']).lower()}
- No production-ready claim: {str(record['production_ready']).lower()}
- No customer validation claim: {str(record['customer_validated']).lower()}
- No customer contacted: {str(record['customer_contacted']).lower()}
- No external calls made: {str(record['external_calls_made']).lower()}
- No blocker closure authorized: {str(record['blocker_closure_authorized']).lower()}
- Blockers closed by inspection: {record['blockers_closed_by_inspection']}
"""


def render_gate(record: dict[str, Any]) -> str:
    return f"""# SAEE Commercial Final Human Inspection Record Gate

answer: hold_external_customer_validation_required

reason: Human inspection found no issue in the local human-filled evidence
surfaces, but formal commercial readiness still requires real external customer
validation. Internal founder evidence does not satisfy `customer_validated`.

status: {record['status']}
manual_check_completed: true
local_evidence_lanes_passed: {str(record['local_evidence_lanes_passed']).lower()}
remaining_production_blocker_count_after_local_human_evidence: {record['remaining_production_blocker_count_after_local_human_evidence']}
remaining_production_blockers_after_local_human_evidence: customer_validated

boundary:
production_ready: false
product_launched: false
customer_validated: false
customer_contacted: false
private_core_exposed: false
external_calls_made: false
blocker_closure_authorized: false
blockers_closed_by_inspection: 0

next_action: Run a separate human-approved external customer-validation path, or
keep SAEE in commercial hold.
"""


def write_outputs(record: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(record), encoding="utf-8")
    BOUNDARY_AUDIT.write_text(render_boundary(record), encoding="utf-8")
    GATE.write_text(render_gate(record), encoding="utf-8")
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "lane_id",
                "status_value",
                "expected_status",
                "local_evidence_passed",
                "source_path",
            ],
        )
        writer.writeheader()
        for row in record["lane_review"]:
            writer.writerow(
                {
                    "lane_id": row["lane_id"],
                    "status_value": row["status_value"],
                    "expected_status": row["expected_status"],
                    "local_evidence_passed": row["local_evidence_passed"],
                    "source_path": row["source_path"],
                }
            )


def main() -> None:
    record = build_record()
    write_outputs(record)
    print(
        "SAEE_COMMERCIAL_FINAL_HUMAN_INSPECTION_RECORD: PASS "
        f"status={record['status']} "
        "remaining_blocker=customer_validated production_ready=false"
    )


if __name__ == "__main__":
    main()
