#!/usr/bin/env python3
"""Validate the commercial sprint human input workbook completion state.

This validator reads the local human-fillable workbook CSV and reports whether
required rows have human-provided values. It does not copy values into
blocker-specific templates, run validators on real input, collect evidence,
execute builders, contact anyone, close blockers, launch product, or claim
production readiness.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
DEFAULT_WORKBOOK_CSV = SPRINT_DIR / "commercial_sprint_human_input_workbook.csv"
SOURCE_WORKBOOK_JSON = SPRINT_DIR / "commercial_sprint_human_input_workbook.local.json"
OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_workbook_validation.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_workbook_validation.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_workbook_validation.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_workbook_validation_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_WORKBOOK_VALIDATOR_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_WORKBOOK_VALIDATOR_RECOMMENDATION_GATE.md"
)

EXPECTED_BLOCKERS = [
    "support_contact",
    "pricing_page",
    "formal_security_review",
    "production_restore_policy",
    "production_monitoring",
]
EXPECTED_COUNTS = {
    "support_contact": 16,
    "pricing_page": 14,
    "formal_security_review": 12,
    "production_restore_policy": 13,
    "production_monitoring": 10,
}
EXPECTED_ROW_COUNT = 65
EXPECTED_REQUIRED_ROW_COUNT = 64

FALSE_FLAGS = [
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "private_core_exposed",
    "product_launched",
    "production_ready",
    "customer_validated",
    "customer_contacted",
    "vendor_contacted",
    "public_sdk_released",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "development_permission_granted",
    "evidence_collection_authorized",
    "execution_authorized",
    "evidence_builder_executed",
    "blocker_closure_authorized",
    "task_candidates_executed",
    "owner_assigned_by_codex",
    "owner_contacted_by_codex",
    "human_input_filled_by_codex",
    "validators_run_on_real_input",
    "support_contact_configured",
    "support_contact_published",
    "support_contact_test_performed",
    "payment_collected",
    "revenue_validated",
]

FORBIDDEN_VALUE_TOKENS = [
    "production_ready=true",
    "product_launched=true",
    "customer_validated=true",
    "private_core_exposed=true",
    "customer_contacted=true",
    "vendor_contacted=true",
    "evidence_collection_authorized=true",
    "execution_authorized=true",
    "evidence_builder_executed=true",
    "blocker_closure_authorized=true",
    "blockers_closed=true",
]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def parse_bool(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "y"}
    return False


def read_rows(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))
    except OSError as exc:
        raise SystemExit(
            "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_WORKBOOK_VALIDATOR: "
            f"FAIL cannot read CSV {path}: {exc}"
        ) from exc


def row_value(row: dict[str, str]) -> str:
    return str(row.get("human_value_placeholder", "")).strip()


def boundary_violations(rows: list[dict[str, str]]) -> list[str]:
    violations: list[str] = []
    ids = [row.get("workbook_row_id", "") for row in rows]
    if len(rows) != EXPECTED_ROW_COUNT:
        violations.append("unexpected_workbook_row_count")
    if len(set(ids)) != len(ids):
        violations.append("duplicate_workbook_row_id")
    counts = Counter(row.get("blocker_id", "") for row in rows)
    for blocker_id, expected_count in EXPECTED_COUNTS.items():
        if counts.get(blocker_id) != expected_count:
            violations.append(f"unexpected_row_count_for_{blocker_id}")
    if any(row.get("blocker_id") not in EXPECTED_BLOCKERS for row in rows):
        violations.append("unexpected_blocker_id")
    if any(parse_bool(row.get("codex_may_fill")) for row in rows):
        violations.append("codex_may_fill_true")
    for row in rows:
        value = row_value(row).lower().replace(" ", "")
        for token in FORBIDDEN_VALUE_TOKENS:
            if token in value:
                violations.append(f"forbidden_value_token:{token}")
    return sorted(set(violations))


def classify_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    checked: list[dict[str, Any]] = []
    for row in rows:
        required = parse_bool(row.get("minimum_required"))
        filled = bool(row_value(row))
        checked.append(
            {
                "workbook_row_id": row.get("workbook_row_id", ""),
                "blocker_id": row.get("blocker_id", ""),
                "owner_review_lane": row.get("owner_review_lane", ""),
                "input_group": row.get("input_group", ""),
                "input_key": row.get("input_key", ""),
                "input_kind": row.get("input_kind", ""),
                "minimum_required": required,
                "human_value_present": filled,
                "row_complete": (filled if required else True),
                "status": "complete" if (filled or not required) else "missing_human_input",
                "source_path": row.get("source_path", ""),
                "human_filled_input_target": row.get("human_filled_input_target", ""),
            }
        )
    return checked


def blocker_summaries(checked_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for blocker_id in EXPECTED_BLOCKERS:
        subset = [row for row in checked_rows if row["blocker_id"] == blocker_id]
        required = [row for row in subset if row["minimum_required"]]
        complete = [row for row in required if row["row_complete"]]
        summaries.append(
            {
                "blocker_id": blocker_id,
                "workbook_row_count": len(subset),
                "required_row_count": len(required),
                "completed_required_row_count": len(complete),
                "missing_required_row_count": len(required) - len(complete),
                "blocker_workbook_complete": len(required) == len(complete),
                "ready_for_template_transfer": len(required) == len(complete),
            }
        )
    return summaries


def build_validation(input_csv: Path) -> dict[str, Any]:
    rows = read_rows(input_csv)
    checked = classify_rows(rows)
    violations = boundary_violations(rows)
    summaries = blocker_summaries(checked)
    completed_required = sum(1 for row in checked if row["minimum_required"] and row["row_complete"])
    missing_required = sum(1 for row in checked if row["minimum_required"] and not row["row_complete"])
    workbook_complete = (
        len(rows) == EXPECTED_ROW_COUNT
        and completed_required == EXPECTED_REQUIRED_ROW_COUNT
        and not violations
    )
    status = "stop_boundary_violation" if violations else (
        "ready_for_template_transfer" if workbook_complete else "hold_human_input_required"
    )
    payload: dict[str, Any] = {
        "commercial_sprint_human_input_workbook_validator_v0_1": True,
        "validator_type": "local_human_input_workbook_completion_validator",
        "validator_scope": "commercial_sprint_human_input_workbook_completion_only",
        "status": status,
        "source_workbook_json": rel(SOURCE_WORKBOOK_JSON),
        "input_csv": rel(input_csv),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_human_input_workbook_validator.py",
        "selected_blocker_count": len(EXPECTED_BLOCKERS),
        "selected_blocker_ids": EXPECTED_BLOCKERS,
        "workbook_row_count": len(rows),
        "expected_workbook_row_count": EXPECTED_ROW_COUNT,
        "required_row_count": EXPECTED_REQUIRED_ROW_COUNT,
        "completed_required_row_count": completed_required,
        "missing_required_row_count": missing_required,
        "workbook_complete": workbook_complete,
        "ready_for_template_transfer": workbook_complete,
        "ready_for_existing_local_validators": False,
        "human_input_required": True,
        "human_review_required": True,
        "human_input_filled_by_codex": False,
        "validators_run_on_real_input": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_validator": 0,
        "boundary_violation_count": len(violations),
        "boundary_violations": violations,
        "blocker_summaries": summaries,
        "rows": checked,
        "next_human_action": (
            "If status is hold, fill missing human_value_placeholder cells. "
            "If status is ready_for_template_transfer, copy values into the "
            "blocker-specific human-filled templates in a separate human-approved step."
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(payload: dict[str, Any]) -> None:
    fieldnames = [
        "workbook_row_id",
        "blocker_id",
        "owner_review_lane",
        "input_group",
        "input_key",
        "input_kind",
        "minimum_required",
        "human_value_present",
        "row_complete",
        "status",
        "source_path",
        "human_filled_input_target",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(payload["rows"])


def write_md(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Workbook Validation",
        "",
        "commercial_sprint_human_input_workbook_validator_v0_1: true",
        f"status: {payload['status']}",
        f"validator_scope: {payload['validator_scope']}",
        f"workbook_row_count: {payload['workbook_row_count']}",
        f"required_row_count: {payload['required_row_count']}",
        f"completed_required_row_count: {payload['completed_required_row_count']}",
        f"missing_required_row_count: {payload['missing_required_row_count']}",
        f"workbook_complete: {str(payload['workbook_complete']).lower()}",
        f"ready_for_template_transfer: {str(payload['ready_for_template_transfer']).lower()}",
        "ready_for_existing_local_validators: false",
        "human_input_filled_by_codex: false",
        "validators_run_on_real_input: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blockers_closed_by_validator: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "",
        "## Purpose",
        "",
        "This validator checks whether the local workbook has human-provided values",
        "for required rows. It does not transfer values into blocker-specific",
        "templates or run existing validators on real input.",
        "",
        "## Blocker Summaries",
        "",
        "| Blocker | Required | Complete | Missing | Ready for transfer |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for item in payload["blocker_summaries"]:
        lines.append(
            "| `{blocker_id}` | {required_row_count} | {completed_required_row_count} | "
            "{missing_required_row_count} | {ready_for_template_transfer} |".format(**item)
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "No input values were filled by Codex. No validator was run on real input.",
            "No evidence builder was executed. No blocker was closed.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_boundary(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Workbook Validator Boundary Audit",
        "",
        "commercial_sprint_human_input_workbook_validator_v0_1: true",
        f"status: {payload['status']}",
        "human_input_filled_by_codex: false",
        "validators_run_on_real_input: false",
        "ready_for_existing_local_validators: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blockers_closed_by_validator: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "",
        "## Confirmed Boundaries",
        "",
    ]
    for flag in FALSE_FLAGS:
        lines.append(f"- {flag}: false")
    OUT_BOUNDARY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_top_doc(payload: dict[str, Any]) -> None:
    TOP_DOC.write_text(
        "\n".join(
            [
                "# SAEE Commercial Sprint Human Input Workbook Validator v0.1",
                "",
                "commercial_sprint_human_input_workbook_validator_v0_1: true",
                f"status: {payload['status']}",
                f"validator_scope: {payload['validator_scope']}",
                f"workbook_row_count: {payload['workbook_row_count']}",
                f"required_row_count: {payload['required_row_count']}",
                f"missing_required_row_count: {payload['missing_required_row_count']}",
                "ready_for_existing_local_validators: false",
                "human_input_filled_by_codex: false",
                "validators_run_on_real_input: false",
                "evidence_collection_authorized: false",
                "execution_authorized: false",
                "evidence_builder_executed: false",
                "blockers_closed_by_validator: 0",
                "production_ready: false",
                "customer_validated: false",
                "product_launched: false",
                "private_core_exposed: false",
                "",
                "## Agent Recommendation Gate",
                "",
                "recommendation_gate:",
                "  feature_or_direction: commercial_sprint_human_input_workbook_validator",
                "  target_customer_need: check whether commercial sprint human input is complete before any evidence work",
                "  agent_answer: recommend",
                "  reason: This local validator improves commercial-readiness workflow quality without executing evidence collection or changing product behavior.",
                "  recommend_for_human_input_completion_check: true",
                "  recommend_for_real_evidence: false",
                "  recommend_for_evidence_collection: false",
                "  recommend_for_automatic_execution: false",
                "  recommend_for_blocker_closure: false",
                "  recommend_for_product_launch: false",
                "  recommend_for_production_readiness_claim: false",
                "",
                "## Boundary",
                "",
                "This validator reads a local workbook CSV and reports completion state only.",
                "It does not transfer values, run validators on real input, collect evidence,",
                "execute builders, close blockers, or claim production readiness.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_gate(payload: dict[str, Any]) -> None:
    GATE.write_text(
        "\n".join(
            [
                "# SAEE Commercial Sprint Human Input Workbook Validator Recommendation Gate",
                "",
                "answer: recommend",
                "recommend_for_human_input_completion_check: true",
                "recommend_for_real_evidence: false",
                "recommend_for_evidence_collection: false",
                "recommend_for_automatic_execution: false",
                "recommend_for_blocker_closure: false",
                "recommend_for_product_launch: false",
                "recommend_for_production_readiness_claim: false",
                "",
                "## Reason",
                "",
                "The validator tells a human reviewer whether the commercial sprint workbook",
                "is complete enough for a later, separate template-transfer step without",
                "granting Codex execution authority.",
                "",
                "## Boundary",
                "",
                "commercial_sprint_human_input_workbook_validator_v0_1: true",
                f"status: {payload['status']}",
                f"validator_scope: {payload['validator_scope']}",
                f"workbook_row_count: {payload['workbook_row_count']}",
                f"missing_required_row_count: {payload['missing_required_row_count']}",
                "ready_for_existing_local_validators: false",
                "human_input_filled_by_codex: false",
                "validators_run_on_real_input: false",
                "evidence_collection_authorized: false",
                "execution_authorized: false",
                "evidence_builder_executed: false",
                "blockers_closed_by_validator: 0",
                "production_ready: false",
                "customer_validated: false",
                "product_launched: false",
                "private_core_exposed: false",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-csv", default=str(DEFAULT_WORKBOOK_CSV))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_csv = Path(args.input_csv)
    if not input_csv.is_absolute():
        input_csv = ROOT / input_csv
    payload = build_validation(input_csv)
    write_json(OUT_JSON, payload)
    write_csv(payload)
    write_md(payload)
    write_boundary(payload)
    write_top_doc(payload)
    write_gate(payload)
    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_WORKBOOK_VALIDATOR: PASS "
        f"status={payload['status']} "
        f"workbook_row_count={payload['workbook_row_count']} "
        f"completed_required_row_count={payload['completed_required_row_count']} "
        f"missing_required_row_count={payload['missing_required_row_count']} "
        f"blockers_closed_by_validator={payload['blockers_closed_by_validator']} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
