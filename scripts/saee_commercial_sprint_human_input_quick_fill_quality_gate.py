#!/usr/bin/env python3
"""Quality gate for commercial sprint human-input quick-fill values.

This gate checks future human-entered quick-fill values for basic usefulness:
the value should be non-placeholder, boundary-safe, and structured enough to
support a later human-approved workbook import decision. It never records raw
human values in its outputs and it does not import, transfer, validate real
evidence, execute builders, contact anyone, close blockers, launch product, or
claim production readiness.
"""

from __future__ import annotations

import csv
import json
import argparse
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
SPRINT_DIR = COMMERCIAL_DIR / "commercial_next_evidence_sprint"

QUICK_FILL_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"
QUICK_FILL_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.local.json"
SAFETY_PREFLIGHT_JSON = SPRINT_DIR / "commercial_sprint_human_input_safety_preflight.local.json"
COMPLETION_VALIDATOR_JSON = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet_validation.local.json"
)
READINESS_AUDIT_JSON = SPRINT_DIR / "commercial_sprint_human_input_readiness_audit.local.json"

OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_quality_gate.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_quality_gate.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_quality_gate.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_quality_gate_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_QUALITY_GATE_V0_1.md"
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_QUALITY_GATE_RECOMMENDATION_GATE.md"
)

EXPECTED_ROW_COUNT = 64
EXPECTED_BLOCKERS = {
    "support_contact",
    "pricing_page",
    "formal_security_review",
    "production_restore_policy",
    "production_monitoring",
}

PLACEHOLDER_VALUES = {
    "",
    "todo",
    "tbd",
    "n/a",
    "na",
    "none",
    "unknown",
    "placeholder",
    "fill later",
    "to be filled",
}

ACTIONABLE_ANCHORS = {
    "approved",
    "approval",
    "assigned",
    "owner",
    "review",
    "decision",
    "evidence",
    "policy",
    "runbook",
    "report",
    "ticket",
    "path",
    "url",
    "provider",
    "threshold",
    "schedule",
    "configured",
    "tested",
    "handoff",
    "reference",
    "artifact",
    "snapshot",
    "date",
    "status",
}

CHINESE_ACTIONABLE_ANCHORS = {
    "批准",
    "不公开",
    "不得",
    "人工",
    "保持",
    "候选",
    "备份",
    "复核",
    "客户",
    "审查",
    "审核",
    "工单",
    "已确认",
    "恢复",
    "报告",
    "指标",
    "文档",
    "日期",
    "方案",
    "日志",
    "本地",
    "条款",
    "正式",
    "法律",
    "状态",
    "独立",
    "生产",
    "监控",
    "定义",
    "编号",
    "策略",
    "尚未",
    "未完成",
    "联系人",
    "联系",
    "记录",
    "计划",
    "证据",
    "负责人",
    "路径",
    "边界",
    "通知",
    "部署",
    "仪表盘",
    "邮箱",
    "SLO",
}

SECRET_PATTERNS = {
    "openai_or_provider_api_key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    "langsmith_api_key": re.compile(r"\bls__[A-Za-z0-9_=-]{10,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private_key_block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "bearer_token": re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}\b"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    "jwt_like_token": re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
}

FORBIDDEN_CLAIM_PATTERNS = {
    "production_ready_claim": re.compile(r"\bproduction[_ -]?ready\s*[:=]\s*true\b", re.I),
    "customer_validated_claim": re.compile(r"\bcustomer[_ -]?validated\s*[:=]\s*true\b", re.I),
    "product_launched_claim": re.compile(r"\bproduct[_ -]?launched\s*[:=]\s*true\b", re.I),
    "external_validation_claim": re.compile(r"\bexternal[_ -]?validation\s*[:=]\s*true\b", re.I),
    "private_core_exposed_claim": re.compile(r"\bprivate[_ -]?core[_ -]?exposed\s*[:=]\s*true\b", re.I),
}

PRIVATE_CORE_TERMS = [
    "fitness logic",
    "selection logic",
    "mutation logic",
    "lineage internals",
    "private core",
    "evolution kernel",
]

FALSE_FLAGS = [
    "raw_values_recorded",
    "human_values_generated_by_codex",
    "quick_fill_values_entered_by_codex",
    "quick_fill_imported_to_workbook",
    "workbook_import_authorized",
    "workbook_import_performed",
    "workbook_written",
    "validators_run_on_real_input",
    "values_transferred",
    "human_filled_templates_written",
    "evidence_collection_authorized",
    "execution_authorized",
    "evidence_builder_executed",
    "blocker_closure_authorized",
    "blockers_closed",
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
    "task_candidates_executed",
    "payment_collected",
    "revenue_validated",
    "production_ready_claim",
    "customer_validation_claim",
]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--quick-fill-csv",
        default=str(QUICK_FILL_CSV),
        help="Quick-fill CSV to quality-check without recording raw values.",
    )
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def has_iso_date(value: str) -> bool:
    return bool(re.search(r"\b20\d{2}-\d{2}-\d{2}\b", value))


def field_has_token(field_context: str, token: str) -> bool:
    return token in re.split(r"[^a-z0-9]+", field_context)


def is_person_or_contact_field(field_context: str) -> bool:
    return any(
        token in field_context
        for token in ["owner", "contact", "reviewer", "name"]
    )


def has_cjk_person_value(value: str) -> bool:
    return len(re.findall(r"[\u4e00-\u9fff]", value)) >= 2


def has_url_or_path(value: str) -> bool:
    return bool(re.search(r"\bhttps?://", value)) or "/" in value or ".md" in value or ".json" in value


def has_actionable_anchor(value: str, lowered: str) -> bool:
    return any(anchor in lowered for anchor in ACTIONABLE_ANCHORS) or any(
        anchor in value for anchor in CHINESE_ACTIONABLE_ANCHORS
    )


def scan_for_boundary_issues(text: str) -> list[str]:
    issues: list[str] = []
    for name, pattern in SECRET_PATTERNS.items():
        if pattern.search(text):
            issues.append(name)
    for name, pattern in FORBIDDEN_CLAIM_PATTERNS.items():
        if pattern.search(text):
            issues.append(name)
    lowered = text.lower()
    if any(term in lowered for term in PRIVATE_CORE_TERMS):
        issues.append("private_core_reference")
    return sorted(set(issues))


def classify_quality(row: dict[str, str]) -> tuple[str, list[str]]:
    value = row.get("human_value_to_enter", "").strip()
    notes = row.get("notes_for_human", "").strip()
    lowered = value.lower()
    combined = "\n".join([value, notes])
    issues: list[str] = []

    if not value:
        return "missing_human_value", ["missing_human_value"]
    if lowered in PLACEHOLDER_VALUES:
        issues.append("placeholder_value")
    issues.extend(scan_for_boundary_issues(combined))

    input_key = row.get("input_key", "").lower()
    input_kind = row.get("input_kind", "").lower()
    field_context = f"{input_key} {input_kind}"
    value_len = len(value)

    person_or_contact_field = is_person_or_contact_field(field_context)

    if field_has_token(field_context, "date"):
        if not has_iso_date(value):
            issues.append("date_field_should_use_iso_date")
    elif person_or_contact_field:
        if value_len < 5 and not has_cjk_person_value(value):
            issues.append("owner_or_contact_value_too_short")
    elif any(token in field_context for token in ["acknowledged", "approval", "approved", "decision"]):
        if value_len < 8:
            issues.append("decision_value_too_short")
    elif value_len < 12 and not has_actionable_anchor(value, lowered):
        issues.append("value_too_short")

    if not (
        has_iso_date(value)
        or has_url_or_path(value)
        or has_actionable_anchor(value, lowered)
        or person_or_contact_field
        or field_has_token(field_context, "date")
    ):
        issues.append("insufficient_actionable_anchor")

    boundary_issue_prefixes = set(SECRET_PATTERNS) | set(FORBIDDEN_CLAIM_PATTERNS) | {"private_core_reference"}
    if any(issue in boundary_issue_prefixes for issue in issues):
        return "stop_boundary_or_sensitive_value", sorted(set(issues))
    if issues:
        return "needs_human_quality_review", sorted(set(issues))
    return "quality_pass_pending_safety_preflight", []


def build_payload(quick_fill_csv: Path) -> dict[str, Any]:
    quick_fill = read_json(QUICK_FILL_JSON)
    safety = read_json(SAFETY_PREFLIGHT_JSON)
    completion = read_json(COMPLETION_VALIDATOR_JSON)
    readiness = read_json(READINESS_AUDIT_JSON)
    rows = read_rows(quick_fill_csv)

    blocker_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    issue_counts: Counter[str] = Counter()
    boundary_violations: list[str] = []
    quality_rows: list[dict[str, Any]] = []

    if len(rows) != EXPECTED_ROW_COUNT:
        boundary_violations.append("unexpected_quick_fill_row_count")

    for row in rows:
        row_id = row.get("quick_fill_row_id", "")
        blocker_id = row.get("blocker_id", "")
        blocker_counts[blocker_id] += 1
        if blocker_id not in EXPECTED_BLOCKERS:
            boundary_violations.append(f"{row_id}:unexpected_blocker_id")
        for flag in ["value_imported_to_workbook", "value_transferred", "template_written"]:
            if parse_bool(row.get(flag, "")):
                boundary_violations.append(f"{row_id}:{flag}_is_true")

        quality_status, issues = classify_quality(row)
        status_counts[quality_status] += 1
        issue_counts.update(issues)
        if quality_status == "stop_boundary_or_sensitive_value":
            boundary_violations.extend(f"{row_id}:{issue}" for issue in issues)

        value = row.get("human_value_to_enter", "").strip()
        notes = row.get("notes_for_human", "").strip()
        quality_rows.append(
            {
                "quick_fill_row_id": row_id,
                "queue_item_id": row.get("queue_item_id", ""),
                "workbook_row_id": row.get("workbook_row_id", ""),
                "blocker_id": blocker_id,
                "owner_review_lane": row.get("owner_review_lane", ""),
                "input_group": row.get("input_group", ""),
                "input_key": row.get("input_key", ""),
                "input_kind": row.get("input_kind", ""),
                "value_present": bool(value),
                "note_present": bool(notes),
                "value_length": len(value),
                "note_length": len(notes),
                "quality_status": quality_status,
                "issue_codes": issues,
                "target_workbook_csv": row.get("target_workbook_csv", ""),
                "target_workbook_column": row.get("target_workbook_column", ""),
                "target_json_pointer": row.get("target_json_pointer", ""),
            }
        )

    completed_count = len(rows) - status_counts["missing_human_value"]
    quality_checked_count = completed_count
    quality_pass_count = status_counts["quality_pass_pending_safety_preflight"]
    quality_review_count = status_counts["needs_human_quality_review"]
    quality_stop_count = status_counts["stop_boundary_or_sensitive_value"]
    quality_issue_count = quality_review_count + quality_stop_count
    missing_count = status_counts["missing_human_value"]

    if boundary_violations:
        status = "stop_boundary_or_sensitive_value_detected"
    elif missing_count:
        status = "hold_human_quick_fill_required"
    elif quality_issue_count:
        status = "hold_human_quality_review_required"
    else:
        status = "pass_quality_gate_pending_safety_preflight_and_human_import_approval"

    quality_gate_passed = (
        status == "pass_quality_gate_pending_safety_preflight_and_human_import_approval"
    )

    payload: dict[str, Any] = {
        "commercial_sprint_human_input_quick_fill_quality_gate_v0_1": True,
        "quality_gate_type": "local_quick_fill_human_value_quality_gate",
        "quality_gate_scope": "quick_fill_value_quality_only_no_raw_value_storage_no_import_no_evidence",
        "status": status,
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_human_input_quick_fill_quality_gate.py",
        "source_files": {
            "quick_fill_csv": rel(quick_fill_csv),
            "quick_fill_json": rel(QUICK_FILL_JSON),
            "safety_preflight_json": rel(SAFETY_PREFLIGHT_JSON),
            "completion_validator_json": rel(COMPLETION_VALIDATOR_JSON),
            "readiness_audit_json": rel(READINESS_AUDIT_JSON),
        },
        "source_statuses": {
            "quick_fill_packet": quick_fill.get("status"),
            "safety_preflight": safety.get("status"),
            "completion_validator": completion.get("status"),
            "readiness_audit": readiness.get("status"),
        },
        "quick_fill_row_count": len(rows),
        "expected_quick_fill_row_count": EXPECTED_ROW_COUNT,
        "completed_value_row_count": completed_count,
        "missing_value_row_count": missing_count,
        "quality_checked_row_count": quality_checked_count,
        "quality_pass_row_count": quality_pass_count,
        "quality_review_row_count": quality_review_count,
        "quality_stop_row_count": quality_stop_count,
        "quality_issue_count": quality_issue_count,
        "placeholder_value_row_count": issue_counts.get("placeholder_value", 0),
        "insufficient_actionability_row_count": issue_counts.get("insufficient_actionable_anchor", 0),
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": boundary_violations,
        "quality_gate_passed": quality_gate_passed,
        "human_input_required": missing_count > 0,
        "human_review_required": True,
        "ready_for_safety_preflight": quality_gate_passed,
        "ready_for_workbook_import": False,
        "safe_to_import_after_human_approval": False,
        "blockers_closed_by_quality_gate": 0,
        "selected_blocker_count": len(blocker_counts),
        "selected_blocker_ids": sorted(blocker_counts),
        "blocker_row_counts": dict(sorted(blocker_counts.items())),
        "quality_status_counts": dict(sorted(status_counts.items())),
        "quality_issue_counts": dict(sorted(issue_counts.items())),
        "raw_value_storage_policy": "never_record_raw_human_values",
        "rows": quality_rows,
        "next_human_action": (
            "Fill human_value_to_enter cells with concrete, non-secret, "
            "boundary-safe evidence summaries or decision records; rerun this "
            "quality gate and the safety preflight before any separate "
            "human-approved workbook import request."
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_json(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(payload: dict[str, Any]) -> None:
    fields = [
        "quick_fill_row_id",
        "queue_item_id",
        "workbook_row_id",
        "blocker_id",
        "owner_review_lane",
        "input_group",
        "input_key",
        "input_kind",
        "value_present",
        "note_present",
        "value_length",
        "note_length",
        "quality_status",
        "issue_codes",
        "target_workbook_csv",
        "target_workbook_column",
        "target_json_pointer",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["rows"]:
            sanitized = dict(row)
            sanitized["issue_codes"] = "|".join(row["issue_codes"])
            writer.writerow({field: sanitized.get(field, "") for field in fields})


def status_lines(payload: dict[str, Any]) -> list[str]:
    return [
        "commercial_sprint_human_input_quick_fill_quality_gate_v0_1: true",
        f"quality_gate_scope: {payload['quality_gate_scope']}",
        f"status: {payload['status']}",
        "commercial_status: hold",
        "production_launch_status: hold",
        f"quick_fill_row_count: {payload['quick_fill_row_count']}",
        f"expected_quick_fill_row_count: {payload['expected_quick_fill_row_count']}",
        f"completed_value_row_count: {payload['completed_value_row_count']}",
        f"missing_value_row_count: {payload['missing_value_row_count']}",
        f"quality_checked_row_count: {payload['quality_checked_row_count']}",
        f"quality_pass_row_count: {payload['quality_pass_row_count']}",
        f"quality_review_row_count: {payload['quality_review_row_count']}",
        f"quality_stop_row_count: {payload['quality_stop_row_count']}",
        f"quality_issue_count: {payload['quality_issue_count']}",
        f"placeholder_value_row_count: {payload['placeholder_value_row_count']}",
        f"insufficient_actionability_row_count: {payload['insufficient_actionability_row_count']}",
        f"quality_gate_passed: {str(payload['quality_gate_passed']).lower()}",
        f"ready_for_safety_preflight: {str(payload['ready_for_safety_preflight']).lower()}",
        "ready_for_workbook_import: false",
        "safe_to_import_after_human_approval: false",
        "raw_values_recorded: false",
        "human_values_generated_by_codex: false",
        "quick_fill_values_entered_by_codex: false",
        "quick_fill_imported_to_workbook: false",
        "workbook_import_authorized: false",
        "validators_run_on_real_input: false",
        "values_transferred: false",
        "human_filled_templates_written: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blocker_closure_authorized: false",
        f"blockers_closed_by_quality_gate: {payload['blockers_closed_by_quality_gate']}",
        f"boundary_violation_count: {payload['boundary_violation_count']}",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
    ]


def write_markdown(payload: dict[str, Any]) -> None:
    blocker_lines = "\n".join(
        f"- `{blocker}`: {count} rows" for blocker, count in payload["blocker_row_counts"].items()
    )
    status_count_lines = "\n".join(
        f"- `{status}`: {count}" for status, count in payload["quality_status_counts"].items()
    )
    lines = [
        "# Commercial Sprint Human Input Quick-Fill Quality Gate",
        "",
        *status_lines(payload),
        "",
        "## Purpose",
        "",
        "This gate checks whether future human-entered quick-fill values are",
        "specific enough to support later human review. It does not record raw",
        "human values and does not authorize workbook import.",
        "",
        "## Current Quality State",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Quick-fill rows | {payload['quick_fill_row_count']} |",
        f"| Completed value rows | {payload['completed_value_row_count']} |",
        f"| Missing value rows | {payload['missing_value_row_count']} |",
        f"| Quality checked rows | {payload['quality_checked_row_count']} |",
        f"| Quality pass rows | {payload['quality_pass_row_count']} |",
        f"| Quality review rows | {payload['quality_review_row_count']} |",
        f"| Quality stop rows | {payload['quality_stop_row_count']} |",
        "",
        "## Quality Status Counts",
        "",
        status_count_lines,
        "",
        "## Blocker Row Counts",
        "",
        blocker_lines,
        "",
        "## Boundary",
        "",
        "No raw human values are recorded in this output. No values were generated",
        "by Codex. No workbook import, template transfer, validator execution on",
        "real input, evidence collection, blocker closure, customer contact,",
        "product launch, or production-readiness claim was performed.",
        "",
        "## Local Fixture Coverage",
        "",
        "The smoke test uses temporary synthetic CSV fixtures to verify two future",
        "states without mutating the source quick-fill packet: a complete",
        "boundary-safe fixture must pass the quality gate pending safety preflight,",
        "and an unsafe fixture containing forbidden claims or secret-like tokens",
        "must stop. The official output is restored to the current hold state after",
        "fixture checks.",
        "",
        "## Next Human Action",
        "",
        payload["next_human_action"],
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def write_boundary(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Quick-Fill Quality Gate Boundary Audit",
        "",
        *status_lines(payload),
        "",
        "This boundary audit confirms the quality gate is local and read-only with",
        "respect to human evidence. It records only metadata, status codes, row",
        "ids, value lengths, and issue codes. It never stores raw human-entered",
        "values and does not mutate the workbook or templates.",
    ]
    OUT_BOUNDARY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_top_doc(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Quick-Fill Quality Gate v0.1",
        "",
        *status_lines(payload),
        "",
        "## Role",
        "",
        "This document records the local quality gate for human quick-fill values.",
        "It is used after humans enter values and before any separate request to",
        "import values into the workbook.",
        "",
        "## Recommendation Gate Answer",
        "",
        "recommend_for_human_value_quality_screening: true",
        "recommend_for_workbook_import: false",
        "recommend_for_validator_execution: false",
        "recommend_for_evidence_collection: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_production: false",
        "",
        "## Boundary",
        "",
        "The gate does not fill values, record raw values, import values, transfer",
        "templates, run validators on real input, collect evidence, close blockers,",
        "contact customers, launch product, or claim production readiness.",
        "",
        "## Local Fixture Coverage",
        "",
        "The smoke test verifies a synthetic complete-pass fixture and a synthetic",
        "unsafe-stop fixture, then restores the default official output to",
        "`hold_human_quick_fill_required`.",
    ]
    TOP_DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_gate(payload: dict[str, Any]) -> None:
    lines = [
        "# SAEE Commercial Sprint Human Input Quick-Fill Quality Gate Recommendation Gate",
        "",
        "answer: recommend_for_human_value_quality_screening_only",
        "recommend_for_human_value_quality_screening: true",
        "recommend_for_workbook_import: false",
        "recommend_for_validator_execution: false",
        "recommend_for_evidence_collection: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_production: false",
        "",
        "## Reason",
        "",
        "The quality gate is useful because it can catch placeholder or weak human",
        "inputs before a later human-approved workbook import. It is not evidence",
        "completion and does not authorize execution.",
        "",
        "## Status",
        "",
        *status_lines(payload),
    ]
    GATE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    payload = build_payload(Path(args.quick_fill_csv))
    write_json(payload)
    write_csv(payload)
    write_markdown(payload)
    write_boundary(payload)
    write_top_doc(payload)
    write_gate(payload)
    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_QUALITY_GATE: PASS "
        f"status={payload['status']} "
        f"missing_value_row_count={payload['missing_value_row_count']} "
        "raw_values_recorded=false production_ready=false"
    )


if __name__ == "__main__":
    main()
