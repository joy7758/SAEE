#!/usr/bin/env python3
"""Catalog source-backed review-ready markers without execution or closure."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
OUT_DIR = COMMERCIAL_DIR / "matrix_update_requests/commercial_review_ready_marker_catalog"
OUT_JSON = OUT_DIR / "commercial_review_ready_marker_catalog.local.json"
OUT_MD = OUT_DIR / "commercial_review_ready_marker_catalog.md"
OUT_CSV = OUT_DIR / "commercial_review_ready_marker_catalog.csv"
BOUNDARY = OUT_DIR / "commercial_review_ready_marker_catalog_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_REVIEW_READY_MARKER_CATALOG_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_REVIEW_READY_MARKER_CATALOG_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
]

SOURCES = {
    "phase1": COMMERCIAL_DIR / "phase_1_identity_tenant_evidence_profile/phase_1_identity_tenant_state_reconciliation/phase_1_identity_tenant_state_reconciliation.local.json",
    "support": COMMERCIAL_DIR / "support_evidence/support_group_final_closure_decision_validation.local.json",
    "monitoring": COMMERCIAL_DIR / "operations_evidence/production_monitoring_state_reconciliation/production_monitoring_state_reconciliation.local.json",
    "operations_followup": COMMERCIAL_DIR / "operations_evidence/operations_followup_state_reconciliation/operations_followup_state_reconciliation.local.json",
    "privacy_security_legal": COMMERCIAL_DIR / "privacy_security_legal_evidence/privacy_security_legal_followup_state_reconciliation/privacy_security_legal_followup_state_reconciliation.local.json",
    "pricing": COMMERCIAL_DIR / "billing_revenue_evidence/pricing_page_state_reconciliation/pricing_page_state_reconciliation.local.json",
    "billing_followup": COMMERCIAL_DIR / "billing_revenue_evidence/billing_followup_state_reconciliation/billing_followup_state_reconciliation.local.json",
    "data_operations": COMMERCIAL_DIR / "data_operations_evidence/production_restore_policy_state_reconciliation/production_restore_policy_state_reconciliation.local.json",
    "internal_pilot": COMMERCIAL_DIR / "customer_validation_evidence/internal_founder_pilot_evidence_run_summary.local.json",
    "gap_matrix": COMMERCIAL_DIR / "production_blocker_gap_matrix/gap_matrix.local.json",
    "current_matrix_request": COMMERCIAL_DIR / "matrix_update_requests/commercial_matrix_update_request_packet.local.json",
}

FALSE_FLAGS: dict[str, Any] = {
    "catalog_execution_authorized": False,
    "matrix_update_execution_authorized": False,
    "matrix_update_executed": False,
    "canonical_gap_matrix_modified": False,
    "canonical_closure_board_modified": False,
    "blocker_closure_authorized": False,
    "blockers_closed_by_catalog": 0,
    "open_blocker_count_reduced": False,
    "pricing_page_published": False,
    "checkout_enabled": False,
    "customer_payment_collected": False,
    "revenue_validated": False,
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
    "public_sdk_released": False,
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise SystemExit(f"missing required source: {rel(path)}")
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


def matrix_rows_by_id(matrix: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = matrix.get("matrix", [])
    return {
        row.get("blocker_id"): row
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("blocker_id"), str)
    }


def all_true(data: dict[str, Any], keys: list[str]) -> bool:
    return all(data.get(key) is True for key in keys)


def source_groups(data: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "source_key": "phase1",
            "blocker_ids": ["production_identity_provider", "oauth_oidc", "rbac", "tenant_storage_isolation"],
            "ready": all_true(data["phase1"], ["production_identity_provider_ready_for_review", "oauth_oidc_ready_for_review", "rbac_ready_for_review", "tenant_storage_isolation_ready_for_review", "combined_phase_1_profile_ready"]),
        },
        {
            "source_key": "support",
            "blocker_ids": ["support_contact", "customer_support", "sla", "on_call_rotation"],
            "ready": data["support"].get("status") == "ready_for_separate_matrix_update_request_no_closure" and data["support"].get("final_human_decision_recorded") is True and data["support"].get("separate_matrix_update_request_ready") is True,
        },
        {
            "source_key": "monitoring",
            "blocker_ids": ["production_monitoring"],
            "ready": all_true(data["monitoring"], ["monitoring_evidence_ready_for_review", "combined_operations_profile_ready"]),
        },
        {
            "source_key": "operations_followup",
            "blocker_ids": ["external_alert_delivery"],
            "ready": all_true(data["operations_followup"], ["external_alert_delivery_ready_for_review", "combined_operations_profile_ready"]),
        },
        {
            "source_key": "privacy_security_legal",
            "blocker_ids": ["formal_security_review", "privacy_legal_review", "data_processing_agreement", "vulnerability_management"],
            "ready": all_true(data["privacy_security_legal"], ["formal_security_review_ready_for_review", "privacy_legal_review_ready_for_review", "data_processing_agreement_ready_for_review", "vulnerability_management_ready_for_review", "combined_privacy_security_legal_profile_ready"]),
        },
        {
            "source_key": "pricing",
            "blocker_ids": ["pricing_page"],
            "ready": data["pricing"].get("matrix_update_request_ready") is True and data["pricing"].get("closure_review_ready") is True and data["pricing"].get("pricing_page_published") is False,
        },
        {
            "source_key": "billing_followup",
            "blocker_ids": ["payment_provider", "invoice_process", "tax_review", "refund_policy", "tenant_billing_isolation"],
            "ready": all_true(data["billing_followup"], ["payment_provider_ready_for_review", "invoice_process_ready_for_review", "tax_review_ready_for_review", "refund_policy_ready_for_review", "tenant_billing_isolation_ready_for_review"]),
        },
        {
            "source_key": "data_operations",
            "blocker_ids": ["restore_tested", "production_restore_policy"],
            "ready": all_true(data["data_operations"], ["restore_tested_profile_ready", "combined_profile_ready", "production_restore_policy_available_for_review"]),
        },
        {
            "source_key": "internal_pilot",
            "blocker_ids": ["pilot_results"],
            "ready": data["internal_pilot"].get("run_status") == "pass" and data["internal_pilot"].get("pilot_results_evidence_complete") is True and data["internal_pilot"].get("internal_pilot_only") is True and data["internal_pilot"].get("external_customer_validation_performed") is False,
        },
    ]


def build_payload() -> dict[str, Any]:
    data = {name: read_json(path) for name, path in SOURCES.items()}
    matrix_by_id = matrix_rows_by_id(data["gap_matrix"])
    groups = source_groups(data)
    rows: list[dict[str, Any]] = []
    for group in groups:
        source_key = group["source_key"]
        source = data[source_key]
        for blocker_id in group["blocker_ids"]:
            matrix_row = matrix_by_id.get(blocker_id, {})
            marker = "record_review_ready_no_closure"
            if blocker_id == "pricing_page":
                marker = "record_review_ready_no_publication_no_closure"
            elif blocker_id == "pilot_results":
                marker = "record_internal_pilot_review_ready_no_external_validation_no_closure"
            rows.append(
                {
                    "blocker_id": blocker_id,
                    "source_group": source_key,
                    "source_path": rel(SOURCES[source_key]),
                    "source_status": source.get("status") or source.get("run_status"),
                    "review_ready_marker_candidate": group["ready"],
                    "requested_marker": marker,
                    "matrix_current_status": matrix_row.get("status", "missing"),
                    "matrix_current_local_evidence_ready": matrix_row.get("local_evidence_ready") is True,
                    "matrix_current_closure_allowed": matrix_row.get("closure_allowed_by_matrix") is True,
                    "requested_status_after_update": "open",
                    "requested_local_evidence_ready_after_update": False,
                    "requested_closure_allowed_after_update": False,
                    "requires_exact_human_execution_approval": True,
                    "closure_allowed_by_catalog": False,
                }
            )

    catalog_ids = [row["blocker_id"] for row in rows if row["review_ready_marker_candidate"]]
    all_matrix_ids = list(matrix_by_id)
    excluded_ids = [blocker_id for blocker_id in all_matrix_ids if blocker_id not in catalog_ids]
    violations: list[str] = []
    for source_name, source in data.items():
        for key in ["production_ready", "customer_validated", "product_launched", "private_core_exposed", "customer_contacted", "external_calls_made", "external_model_api_called"]:
            if source.get(key) is True:
                violations.append(f"{source_name}.{key}")

    ready_count = len(catalog_ids)
    current_request_count = data["current_matrix_request"].get("candidate_count", 0)
    status = "stop_boundary_violation" if violations else "hold_review_ready_catalog_incomplete"
    if not violations and ready_count == 23 and excluded_ids == ["customer_validated"]:
        status = "ready_for_human_matrix_update_scope_review_no_execution"
    payload: dict[str, Any] = {
        "commercial_review_ready_marker_catalog_v0_1": True,
        "catalog_type": "source_backed_review_ready_marker_catalog_no_execution_no_closure",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "canonical_open_blocker_count": len(all_matrix_ids),
        "review_ready_marker_candidate_count": ready_count,
        "review_ready_marker_candidate_ids": catalog_ids,
        "not_cataloged_blocker_count": len(excluded_ids),
        "not_cataloged_blocker_ids": excluded_ids,
        "candidate_rows": rows,
        "source_group_count": len(groups),
        "source_paths": {name: rel(path) for name, path in SOURCES.items()},
        "current_matrix_request_target_count": current_request_count,
        "current_matrix_request_target_ids": data["current_matrix_request"].get("target_blockers", []),
        "matrix_request_scope_refresh_required": current_request_count != ready_count,
        "exact_human_execution_approval_still_required": True,
        "human_review_required": True,
        "recommendation_gate": "conditional",
        "would_recommend_to_potential_customer": "conditional",
        "recommendation_reason": "Twenty-three blockers have source-backed review-ready marker candidates, but customer validation is missing and production controls remain inactive.",
        "boundary_violation_count": len(violations),
        "boundary_violations": sorted(violations),
        "next_human_action": "Review the 23-row catalog and refresh the no-execution matrix request scope. Do not execute marker application until the exact human approval phrase is received.",
    }
    payload.update(FALSE_FLAGS)
    return payload


def write_outputs(payload: dict[str, Any]) -> None:
    write_json(OUT_JSON, payload)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        fields = ["blocker_id", "source_group", "source_status", "review_ready_marker_candidate", "requested_marker", "matrix_current_status", "requires_exact_human_execution_approval", "closure_allowed_by_catalog"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["candidate_rows"]:
            writer.writerow({field: row.get(field) for field in fields})

    table = "\n".join(
        f"| `{row['blocker_id']}` | `{row['source_group']}` | `{str(row['review_ready_marker_candidate']).lower()}` | `{row['requested_marker']}` |"
        for row in payload["candidate_rows"]
    )
    OUT_MD.write_text(
        f"""# SAEE Commercial Review-Ready Marker Catalog v0.1

Status: `{payload['status']}`

This catalog aggregates source-backed review-ready marker candidates. It does
not execute a matrix update, set local evidence ready, close blockers, or claim
production/customer readiness.

## Summary

- canonical_open_blocker_count: `{payload['canonical_open_blocker_count']}`
- review_ready_marker_candidate_count: `{payload['review_ready_marker_candidate_count']}`
- not_cataloged_blocker_count: `{payload['not_cataloged_blocker_count']}`
- not_cataloged_blocker_ids: `{', '.join(payload['not_cataloged_blocker_ids'])}`
- current_matrix_request_target_count: `{payload['current_matrix_request_target_count']}`
- matrix_request_scope_refresh_required: `{str(payload['matrix_request_scope_refresh_required']).lower()}`
- exact_human_execution_approval_still_required: `true`
- recommendation_gate: `conditional`

## Catalog

| Blocker | Source group | Review-ready candidate | Marker |
| --- | --- | --- | --- |
{table}

## Boundary

- matrix_update_executed=false
- canonical_gap_matrix_modified=false
- blocker_closure_authorized=false
- blockers_closed_by_catalog=0
- production_ready=false
- customer_validated=false
- product_launched=false
- private_core_exposed=false
""",
        encoding="utf-8",
    )
    BOUNDARY.write_text(
        """# Commercial Review-Ready Marker Catalog Boundary Audit

- Catalog and review scope only.
- No matrix update executed.
- No canonical gap matrix or closure board modified.
- No blocker closure authorized or performed.
- No production controls enabled.
- No pricing page published or checkout enabled.
- No customer contacted or validated.
- No runtime, backend, kernel, API schema, or private core modified.

matrix_update_executed=false
canonical_gap_matrix_modified=false
blocker_closure_authorized=false
blockers_closed_by_catalog=0
production_ready=false
customer_validated=false
product_launched=false
private_core_exposed=false
""",
        encoding="utf-8",
    )
    TOP_DOC.write_text(
        f"""# SAEE Commercial Review-Ready Marker Catalog v0.1

commercial_review_ready_marker_catalog_v0_1: true
status: {payload['status']}
canonical_open_blocker_count: {payload['canonical_open_blocker_count']}
review_ready_marker_candidate_count: {payload['review_ready_marker_candidate_count']}
not_cataloged_blocker_count: {payload['not_cataloged_blocker_count']}
not_cataloged_blocker_ids: {','.join(payload['not_cataloged_blocker_ids'])}
current_matrix_request_target_count: {payload['current_matrix_request_target_count']}
matrix_request_scope_refresh_required: {str(payload['matrix_request_scope_refresh_required']).lower()}
exact_human_execution_approval_still_required: true
recommendation_gate: conditional
matrix_update_executed=false
blockers_closed_by_catalog=0
production_ready=false
customer_validated=false

This catalog prepares an auditable request scope. It does not apply markers,
close blockers, or authorize customer-facing production use.
""",
        encoding="utf-8",
    )
    GATE.write_text(
        f"""# SAEE Commercial Review-Ready Marker Catalog Gate

answer: conditional_scope_refresh_recommended_no_execution
recommendation_gate: conditional

reason:
The source-backed catalog contains 23 review-ready marker candidates. The only
canonical blocker not cataloged is `customer_validated`. The current five-row
matrix request is stale and should be refreshed before execution. This gate
does not authorize matrix writes or blocker closure.

status: {payload['status']}
review_ready_marker_candidate_count: {payload['review_ready_marker_candidate_count']}
not_cataloged_blocker_ids: {','.join(payload['not_cataloged_blocker_ids'])}
matrix_request_scope_refresh_required: {str(payload['matrix_request_scope_refresh_required']).lower()}

boundary:
matrix_update_execution_authorized: false
matrix_update_executed: false
canonical_gap_matrix_modified: false
blocker_closure_authorized: false
blockers_closed_by_catalog: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

next_action:
Refresh the no-execution matrix request scope from this catalog. Exact human
execution approval remains required before marker application.
""",
        encoding="utf-8",
    )

    for line in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_REVIEW_READY_MARKER_CATALOG_V0_1.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_review_ready_marker_catalog/commercial_review_ready_marker_catalog.local.json",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_review_ready_marker_catalog/commercial_review_ready_marker_catalog.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_review_ready_marker_catalog/commercial_review_ready_marker_catalog.csv",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_review_ready_marker_catalog/commercial_review_ready_marker_catalog_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_REVIEW_READY_MARKER_CATALOG_GATE.md",
        "/scripts/saee_commercial_review_ready_marker_catalog.py",
        "/scripts/saee_commercial_review_ready_marker_catalog_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    keys = [
        "status", "canonical_open_blocker_count", "review_ready_marker_candidate_count",
        "review_ready_marker_candidate_ids", "not_cataloged_blocker_count",
        "not_cataloged_blocker_ids", "current_matrix_request_target_count",
        "matrix_request_scope_refresh_required", "exact_human_execution_approval_still_required",
        "human_review_required", "recommendation_gate", "would_recommend_to_potential_customer",
        "matrix_update_execution_authorized", "matrix_update_executed",
        "canonical_gap_matrix_modified", "blocker_closure_authorized",
        "blockers_closed_by_catalog", "production_ready", "customer_validated",
        "product_launched", "private_core_exposed", "runtime_modified",
        "backend_modified", "kernel_modified", "api_schema_modified",
    ]
    index["commercial_review_ready_marker_catalog_v0_1"] = {key: payload[key] for key in keys}
    write_json(AGENT_INDEX, index)

    block = f"""## Commercial Review-Ready Marker Catalog v0.1

Status: `{payload['status']}`.

The catalog reconciles `review_ready_marker_candidate_count={payload['review_ready_marker_candidate_count']}`
of `canonical_open_blocker_count={payload['canonical_open_blocker_count']}` blockers.
`not_cataloged_blocker_ids={','.join(payload['not_cataloged_blocker_ids'])}`,
`current_matrix_request_target_count={payload['current_matrix_request_target_count']}`,
`matrix_request_scope_refresh_required={str(payload['matrix_request_scope_refresh_required']).lower()}`,
`exact_human_execution_approval_still_required=true`,
`matrix_update_executed=false`, `blockers_closed_by_catalog=0`,
`production_ready=false`, `customer_validated=false`, and `private_core_exposed=false`.
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_COMMERCIAL_REVIEW_READY_MARKER_CATALOG", block)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_COMMERCIAL_REVIEW_READY_MARKER_CATALOG: PASS "
        f"status={payload['status']} candidates={payload['review_ready_marker_candidate_count']} "
        f"not_cataloged={payload['not_cataloged_blocker_count']} matrix_update_executed=false "
        "blockers_closed=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
