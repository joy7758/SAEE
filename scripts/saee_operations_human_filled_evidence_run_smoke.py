#!/usr/bin/env python3
"""Smoke check for the local operations human-filled evidence run.

This check verifies the review-only artifacts generated for production
monitoring, external alert delivery, and operations on-call rotation. It does
not deploy monitoring, enable alert delivery, start on-call, contact vendors or
customers, close blockers, or claim production readiness.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/operations_evidence"
SUMMARY_PATH = EVIDENCE_DIR / "operations_human_filled_evidence_run_summary.local.json"
PROFILE_PATH = (
    EVIDENCE_DIR
    / "operations_evidence_profile.from_monitoring_alert_on_call_human_filled.local.json"
)
DEFAULT_PROFILE_PATH = EVIDENCE_DIR / "operations_evidence_profile.local.json"


FALSE_KEYS = (
    "production_ready",
    "customer_validated",
    "product_launched",
    "customer_contacted",
    "private_core_exposed",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "production_monitoring_deployed",
    "external_alert_delivery_enabled",
    "on_call_rotation_started_by_codex",
    "alert_provider_contacted",
    "monitoring_vendor_contacted",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_OPERATIONS_HUMAN_FILLED_EVIDENCE_RUN_SMOKE: FAIL {message}")


def read_json(path: Path) -> dict[str, object]:
    require(path.exists(), f"missing {path.relative_to(ROOT)}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(
            "SAEE_OPERATIONS_HUMAN_FILLED_EVIDENCE_RUN_SMOKE: FAIL "
            f"invalid JSON {path.relative_to(ROOT)}: {exc}"
        ) from exc
    require(isinstance(data, dict), f"{path.relative_to(ROOT)} must be object")
    return data


def main() -> None:
    summary = read_json(SUMMARY_PATH)
    profile = read_json(PROFILE_PATH)
    default_profile = read_json(DEFAULT_PROFILE_PATH)

    require(summary["run_status"] == "pass", "run_status must be pass")
    require(summary["validation_status"] == "pass", "validation_status must be pass")
    require(
        summary["production_monitoring_validation_status"] == "pass",
        "production monitoring validation must pass",
    )
    require(
        summary["external_alert_delivery_validation_status"] == "pass",
        "external alert delivery validation must pass",
    )
    require(
        summary["operations_on_call_rotation_validation_status"] == "pass",
        "operations on-call validation must pass",
    )
    require(
        summary["operations_profile_status"] == "pass",
        "operations profile status must be pass",
    )
    require(
        summary["production_operations_ready"] is True,
        "production operations evidence must be ready for go/no-go review",
    )
    require(
        summary["operations_satisfied_blockers"]
        == ["production_monitoring", "external_alert_delivery", "on_call_rotation"],
        "operations satisfied blockers must match the three operations blockers",
    )
    require(
        summary["support_data_ops_operations_production_blocker_count"] == 16,
        "combined support/data-ops/operations blocker count must be 16",
    )
    require(
        profile["support_contact_used_for_go_no_go"] == "joy7758@gmail.com",
        "support contact used for local go/no-go must be recorded",
    )
    require(
        default_profile["profile_status"] == "hold",
        "default operations profile must remain hold",
    )
    require(
        default_profile["production_operations_ready"] is False,
        "default operations evidence must not be production ready",
    )

    for key in FALSE_KEYS:
        require(summary.get(key) is False, f"summary {key} must be false")
        require(profile.get(key) is False, f"profile {key} must be false")

    for path_text in summary["input_files"] + summary["output_files"]:
        path = Path(path_text)
        require(path.exists(), f"referenced evidence file missing: {path}")

    print(
        "SAEE_OPERATIONS_HUMAN_FILLED_EVIDENCE_RUN_SMOKE: PASS "
        "operations_profile_status=pass production_operations_ready=true "
        "production_blockers=16 production_ready=false"
    )


if __name__ == "__main__":
    main()
