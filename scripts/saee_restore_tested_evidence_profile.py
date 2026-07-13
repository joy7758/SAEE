#!/usr/bin/env python3
"""Build a restore-tested commercial evidence profile from local evidence.

This profile reads the existing local public-shell restore-test evidence and
feeds a derived data-operations evidence file into commercial go/no-go. It does
not run restore, touch live data paths, contact external services, modify
runtime/backend/kernel/API schema, close blockers, or claim production
readiness.
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
from saee_backend.services.production_data_operations_evidence import (
    FORBIDDEN_TRUE_KEYS,
    RESTORE_POLICY_KEYS,
    RESTORE_TEST_KEYS,
    evaluate_production_data_operations_evidence,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/data_operations_evidence"
DEFAULT_SOURCE_PATH = OUTPUT_DIR / "data_operations_evidence.local.json"
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / "restore_tested_evidence_profile.local.json"
DEFAULT_DATA_OPS_OUTPUT_PATH = (
    OUTPUT_DIR / "production_data_operations_evidence.from_restore_tested.local.json"
)
REPORT_PATH = OUTPUT_DIR / "restore_tested_evidence_profile_report.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/RESTORE_TESTED_EVIDENCE_PROFILE_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_RESTORE_TESTED_EVIDENCE_PROFILE_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_RESTORE_TESTED_EVIDENCE_PROFILE: FAIL: " + message)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_source(path: Path) -> tuple[bool, bool, dict[str, Any]]:
    if not path.exists():
        return False, False, {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return True, False, {}
    if not isinstance(data, dict):
        return True, False, {}
    return True, True, data


def restore_missing(data: dict[str, Any]) -> list[str]:
    return [key for key in RESTORE_TEST_KEYS if data.get(key) is not True]


def source_boundary_violations(data: dict[str, Any]) -> list[str]:
    return [key for key in FORBIDDEN_TRUE_KEYS if data.get(key) is True]


def build_data_operations_evidence(
    source: dict[str, Any],
    source_path: Path,
    *,
    restore_complete: bool,
    source_safe: bool,
) -> dict[str, Any]:
    evidence: dict[str, Any] = {
        "data_operations_evidence_type": "production_data_operations_evidence",
        "evidence_scope": "local_restore_tested_evidence_profile_from_public_shell_drill",
        "evidence_version": "v0.1",
        "generated_by": "scripts/saee_restore_tested_evidence_profile.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_evidence_path": str(source_path),
        "source_evidence_scope": source.get("evidence_scope", ""),
        "source_generated_by": source.get("generated_by", ""),
        "source_restore_drill_status": source.get("local_public_shell_results", {}).get(
            "restore_drill_status"
        )
        if isinstance(source.get("local_public_shell_results"), dict)
        else None,
        "profile_note": (
            "Restore-test evidence only. Production restore policy evidence remains "
            "separate and unavailable."
        ),
    }
    for key in RESTORE_TEST_KEYS:
        evidence[key] = source.get(key) is True and restore_complete and source_safe
    for key in RESTORE_POLICY_KEYS:
        evidence[key] = False
    for key in FORBIDDEN_TRUE_KEYS:
        evidence[key] = False
    return evidence


def data_operations_readiness(path: Path) -> dict[str, object]:
    return evaluate_production_data_operations_evidence(
        load_settings({"SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH": str(path)})
    )


def commercial_profile(path: Path) -> dict[str, object]:
    return evaluate_commercial_go_no_go(
        load_settings({"SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH": str(path)})
    )


def build_profile(
    source_path: Path,
    output_path: Path,
    data_ops_output_path: Path,
    *,
    write_documents: bool = True,
) -> dict[str, Any]:
    source_exists, source_parseable, source = read_source(source_path)
    source_type_valid = source.get("data_operations_evidence_type") == (
        "production_data_operations_evidence"
    )
    missing = restore_missing(source)
    violations = source_boundary_violations(source)
    restore_complete = source_parseable and source_type_valid and not missing
    source_safe = not violations
    status = "stop" if violations else ("pass" if restore_complete else "hold")

    data_ops_evidence = build_data_operations_evidence(
        source,
        source_path,
        restore_complete=restore_complete,
        source_safe=source_safe,
    )
    write_json(data_ops_output_path, data_ops_evidence)

    readiness = data_operations_readiness(data_ops_output_path)
    go_no_go = commercial_profile(data_ops_output_path)
    satisfied_blockers = [
        str(item["blocker_id"]) for item in go_no_go["blockers"] if item["satisfied"] is True
    ]

    summary: dict[str, Any] = {
        "restore_tested_evidence_profile_v0_1": True,
        "profile_scope": "local_restore_tested_evidence_profile_from_public_shell_drill",
        "generated_by": "scripts/saee_restore_tested_evidence_profile.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "status": status,
        "source_evidence_path": str(source_path),
        "profile_output": str(output_path),
        "data_operations_evidence_output": str(data_ops_output_path),
        "source_evidence_exists": source_exists,
        "source_evidence_parseable": source_parseable,
        "source_evidence_type_valid": source_type_valid,
        "source_restore_test_evidence_complete": restore_complete,
        "missing_restore_test_evidence": missing,
        "source_boundary_violation_count": len(violations),
        "source_boundary_violations": violations,
        "restore_tested_available_for_go_no_go": readiness["restore_tested"],
        "production_restore_tested": readiness["production_restore_tested"],
        "production_restore_policy_available": readiness[
            "production_restore_policy_available"
        ],
        "production_restore_policy_approved": readiness[
            "production_restore_policy_approved"
        ],
        "production_data_operations_ready": readiness["production_data_operations_ready"],
        "data_operations_readiness_status": readiness["status"],
        "data_operations_readiness_blocker_count": readiness["blocker_count"],
        "commercial_status_after_profile": go_no_go["commercial_status"],
        "production_launch_status_after_profile": go_no_go["production_launch_status"],
        "profile_satisfied_production_checks": go_no_go["satisfied_production_checks"],
        "profile_total_production_checks": go_no_go["total_production_checks"],
        "profile_production_blocker_count": go_no_go["production_blocker_count"],
        "profile_satisfied_blockers": satisfied_blockers,
        "target_blocker_ids": ["restore_tested"],
        "target_blocker_satisfied_by_profile": "restore_tested" in satisfied_blockers,
        "blockers_closed_by_profile": 0,
        "accepted_for_blocker_closure_count": 0,
        "human_review_required": True,
        "separate_production_restore_policy_required": True,
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
        "customer_contacted": False,
        "production_data_path_modified": False,
        "restore_to_live_path_enabled": False,
        "live_restore_performed": False,
        "credentials_restored": False,
        "private_core_restored": False,
        "next_action": (
            "Use this profile only as a human-review input for the restore_tested "
            "blocker. Production restore policy and all other production blockers "
            "remain separate."
        ),
    }
    write_json(output_path, summary)
    if write_documents:
        write_docs(summary)
    return summary


def report_markdown(summary: dict[str, Any]) -> str:
    return f"""# SAEE Restore Tested Evidence Profile Report

Status: local restore-tested evidence profile generated.

## Summary

- profile_scope: local_restore_tested_evidence_profile_from_public_shell_drill
- source_restore_test_evidence_complete: {str(summary['source_restore_test_evidence_complete']).lower()}
- restore_tested_available_for_go_no_go: {str(summary['restore_tested_available_for_go_no_go']).lower()}
- production_restore_tested: {str(summary['production_restore_tested']).lower()}
- production_restore_policy_available: {str(summary['production_restore_policy_available']).lower()}
- production_data_operations_ready: {str(summary['production_data_operations_ready']).lower()}
- commercial_status_after_profile: {summary['commercial_status_after_profile']}
- production_launch_status_after_profile: {summary['production_launch_status_after_profile']}
- profile_satisfied_production_checks: {summary['profile_satisfied_production_checks']}
- profile_total_production_checks: {summary['profile_total_production_checks']}
- profile_production_blocker_count: {summary['profile_production_blocker_count']}
- target_blocker_satisfied_by_profile: {str(summary['target_blocker_satisfied_by_profile']).lower()}
- blockers_closed_by_profile: 0

## What This Profile Does

It converts the existing local public-shell restore-test evidence into a
dedicated production data-operations evidence file and runs commercial go/no-go
with that file explicitly configured.

## What This Profile Does Not Do

It does not run restore, perform live restore, approve production restore
policy, touch production data paths, contact customers, contact external
services, close blockers by itself, launch product, or claim production
readiness.

## Boundary

- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- external_calls_made: false
- customer_contacted: false
- production_data_path_modified: false
- restore_to_live_path_enabled: false
- live_restore_performed: false
- credentials_restored: false
- private_core_restored: false

## Next Action

Human reviewers may treat this as evidence that the `restore_tested` blocker has
a local public-shell restore-test profile. The `production_restore_policy`
blocker and the remaining production blockers still require separate evidence.
"""


def write_docs(summary: dict[str, Any]) -> None:
    REPORT_PATH.write_text(report_markdown(summary), encoding="utf-8")
    DOC_PATH.write_text(
        f"""# SAEE Restore Tested Evidence Profile v0.1

Status: local evidence profile available.

restore_tested_evidence_profile_v0_1: true
profile_scope: local_restore_tested_evidence_profile_from_public_shell_drill
source_restore_test_evidence_complete: {str(summary['source_restore_test_evidence_complete']).lower()}
restore_tested_available_for_go_no_go: {str(summary['restore_tested_available_for_go_no_go']).lower()}
production_restore_tested: {str(summary['production_restore_tested']).lower()}
production_restore_policy_available: false
production_data_operations_ready: false
commercial_status_after_profile: {summary['commercial_status_after_profile']}
production_launch_status_after_profile: {summary['production_launch_status_after_profile']}
profile_satisfied_production_checks: {summary['profile_satisfied_production_checks']}
profile_production_blocker_count: {summary['profile_production_blocker_count']}
blockers_closed_by_profile: 0

## Purpose

This profile makes the existing local public-shell restore-test evidence
agent-readable for commercial go/no-go review. It targets the `restore_tested`
blocker only.

## Recommendation Gate Answer

answer: conditional
recommend_for_restore_tested_evidence_review: true
recommend_for_production_launch: false
recommend_for_blocker_closure_by_profile_alone: false

## Boundary

production_ready: false
customer_validated: false
product_launched: false
public_sdk_released: false
private_core_exposed: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
external_calls_made: false
customer_contacted: false
production_data_path_modified: false
restore_to_live_path_enabled: false
live_restore_performed: false
credentials_restored: false
private_core_restored: false

## Entrypoints

- source evidence: `phase_b_product/commercial_readiness/data_operations_evidence/data_operations_evidence.local.json`
- profile output: `phase_b_product/commercial_readiness/data_operations_evidence/restore_tested_evidence_profile.local.json`
- production data-operations evidence output: `phase_b_product/commercial_readiness/data_operations_evidence/production_data_operations_evidence.from_restore_tested.local.json`
- report: `phase_b_product/commercial_readiness/data_operations_evidence/restore_tested_evidence_profile_report.md`
- script: `scripts/saee_restore_tested_evidence_profile.py`
- smoke: `scripts/saee_restore_tested_evidence_profile_smoke.py`
""",
        encoding="utf-8",
    )
    GATE_PATH.write_text(
        """# SAEE Restore Tested Evidence Profile Recommendation Gate

answer: conditional

recommend_for_restore_tested_evidence_review: true
recommend_for_commercial_go_no_go_profile: true
recommend_for_production_launch: false
recommend_for_blocker_closure_by_profile_alone: false
recommend_for_live_restore: false
recommend_for_production_restore_policy_approval: false

## Reason

The profile is useful because it proves how existing local public-shell
restore-test evidence affects commercial go/no-go when explicitly configured.
It is not sufficient for production launch: production restore policy remains
unavailable, and every non-restore production blocker remains separate.

## Boundary

production_ready: false
customer_validated: false
product_launched: false
public_sdk_released: false
private_core_exposed: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
external_calls_made: false
customer_contacted: false
production_data_path_modified: false
restore_to_live_path_enabled: false
live_restore_performed: false
credentials_restored: false
private_core_restored: false
""",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--data-ops-output", type=Path, default=DEFAULT_DATA_OPS_OUTPUT_PATH)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    summary = build_profile(args.source, args.output, args.data_ops_output)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(
            "SAEE_RESTORE_TESTED_EVIDENCE_PROFILE: PASS "
            f"status={summary['status']} "
            f"restore_tested_available_for_go_no_go="
            f"{str(summary['restore_tested_available_for_go_no_go']).lower()} "
            f"commercial_status_after_profile={summary['commercial_status_after_profile']} "
            f"profile_production_blocker_count={summary['profile_production_blocker_count']} "
            "blockers_closed_by_profile=0"
        )


if __name__ == "__main__":
    main()
