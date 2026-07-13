#!/usr/bin/env python3
"""Build a combined SAEE data-operations evidence profile.

This profile combines restore-tested evidence and production-restore-policy
evidence into the single data-operations evidence file consumed by commercial
go/no-go checks. It does not approve policy, run restore, touch live data
paths, contact customers, infer missing evidence, close blockers by itself,
modify product behavior, or claim production readiness.
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
DEFAULT_RESTORE_TESTED_EVIDENCE = (
    OUTPUT_DIR / "production_data_operations_evidence.from_restore_tested.local.json"
)
DEFAULT_RESTORE_POLICY_EVIDENCE = (
    OUTPUT_DIR / "production_data_operations_evidence.from_restore_policy.local.json"
)
DEFAULT_PROFILE_JSON = OUTPUT_DIR / "data_operations_evidence_profile.local.json"
DEFAULT_COMBINED_EVIDENCE = (
    OUTPUT_DIR / "production_data_operations_evidence.combined_profile.local.json"
)
REPORT_PATH = OUTPUT_DIR / "data_operations_evidence_profile_report.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/DATA_OPERATIONS_EVIDENCE_PROFILE_V0_1.md"
GATE_PATH = (
    ROOT / "docs/strategy/SAEE_DATA_OPERATIONS_EVIDENCE_PROFILE_RECOMMENDATION_GATE.md"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_DATA_OPERATIONS_EVIDENCE_PROFILE: FAIL: " + message)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_evidence(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"SAEE_DATA_OPERATIONS_EVIDENCE_PROFILE: FAIL: invalid evidence {path}: {exc}"
        ) from exc
    require(isinstance(data, dict), f"evidence file must be an object: {path}")
    return data


def source_is_data_operations_evidence(data: dict[str, Any]) -> bool:
    return data.get("data_operations_evidence_type") == "production_data_operations_evidence"


def all_true(data: dict[str, Any], keys: tuple[str, ...]) -> bool:
    return all(data.get(key) is True for key in keys)


def source_boundary_violations(
    label: str,
    data: dict[str, Any],
) -> list[str]:
    violations: list[str] = []
    if data and not source_is_data_operations_evidence(data):
        violations.append(f"{label}.data_operations_evidence_type_invalid")
    if int(data.get("source_boundary_violation_count", 0) or 0) > 0:
        violations.append(f"{label}.source_boundary_violation_count")
    for key in FORBIDDEN_TRUE_KEYS:
        if data.get(key) is True:
            violations.append(f"{label}.{key}")
    for key in (
        "external_model_api_called",
        "external_ai_assistant_tested",
        "policy_approved_by_codex",
        "restore_policy_published_by_codex",
        "live_restore_authorized_by_codex",
        "production_restore_policy_claim_published",
    ):
        if data.get(key) is True:
            violations.append(f"{label}.{key}")
    return violations


def build_combined_evidence(
    restore_tested: dict[str, Any],
    restore_policy: dict[str, Any],
    *,
    source_violation_count: int,
) -> dict[str, Any]:
    evidence: dict[str, Any] = {
        "data_operations_evidence_type": "production_data_operations_evidence",
        "evidence_scope": "combined_restore_tested_and_restore_policy_evidence_to_go_no_go",
        "evidence_version": "v0.1",
        "generated_by": "scripts/saee_data_operations_evidence_profile.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "restore_tested_source_scope": restore_tested.get("evidence_scope", ""),
        "restore_policy_source_scope": restore_policy.get("evidence_scope", ""),
        "source_boundary_violation_count": source_violation_count,
        "profile_note": (
            "Combined data-operations profile. Restore-tested evidence and "
            "production restore policy evidence remain separately sourced."
        ),
    }
    safe = source_violation_count == 0
    for key in RESTORE_TEST_KEYS:
        evidence[key] = safe and restore_tested.get(key) is True
    for key in RESTORE_POLICY_KEYS:
        evidence[key] = safe and restore_policy.get(key) is True
    for key in FORBIDDEN_TRUE_KEYS:
        evidence[key] = False
    evidence["external_model_api_called"] = False
    evidence["external_ai_assistant_tested"] = False
    evidence["policy_approved_by_codex"] = False
    evidence["restore_policy_published_by_codex"] = False
    evidence["live_restore_authorized_by_codex"] = False
    evidence["production_restore_policy_claim_published"] = False
    return evidence


def data_ops_readiness(path: Path) -> dict[str, object]:
    return evaluate_production_data_operations_evidence(
        load_settings({"SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH": str(path)})
    )


def commercial_status(path: Path) -> dict[str, object]:
    return evaluate_commercial_go_no_go(
        load_settings({"SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH": str(path)})
    )


def profile_status(
    readiness: dict[str, object],
    source_violations: list[str],
) -> str:
    if source_violations or readiness["status"] == "stop":
        return "stop"
    if readiness["production_data_operations_ready"] is True:
        return "pass"
    return "hold"


def build_profile(
    restore_tested_path: Path,
    restore_policy_path: Path,
    profile_output_path: Path,
    combined_evidence_path: Path,
) -> dict[str, Any]:
    restore_tested = read_evidence(restore_tested_path)
    restore_policy = read_evidence(restore_policy_path)
    source_violations = [
        *source_boundary_violations("restore_tested_source", restore_tested),
        *source_boundary_violations("restore_policy_source", restore_policy),
    ]
    combined_evidence = build_combined_evidence(
        restore_tested,
        restore_policy,
        source_violation_count=len(source_violations),
    )
    write_json(combined_evidence_path, combined_evidence)
    readiness = data_ops_readiness(combined_evidence_path)
    go_no_go = commercial_status(combined_evidence_path)
    unsatisfied_ids = [
        str(item.get("blocker_id"))
        for item in go_no_go.get("unsatisfied_blockers", [])
        if isinstance(item, dict)
    ]
    satisfied_data_ops = [
        blocker_id
        for blocker_id in ("restore_tested", "production_restore_policy")
        if blocker_id not in unsatisfied_ids
    ]
    status = profile_status(readiness, source_violations)

    profile: dict[str, Any] = {
        "data_operations_evidence_profile_v0_1": True,
        "profile_type": "saee_data_operations_evidence_profile",
        "profile_version": "v0.1",
        "profile_scope": "combined_restore_tested_and_restore_policy_evidence_to_go_no_go",
        "generated_by": "scripts/saee_data_operations_evidence_profile.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "restore_tested_evidence_path": str(restore_tested_path),
        "restore_policy_evidence_path": str(restore_policy_path),
        "combined_data_operations_evidence_path": str(combined_evidence_path),
        "profile_output_path": str(profile_output_path),
        "profile_status": status,
        "source_boundary_violation_count": len(source_violations),
        "source_boundary_violations": source_violations,
        "restore_tested_source_complete": all_true(restore_tested, RESTORE_TEST_KEYS),
        "restore_policy_source_complete": all_true(restore_policy, RESTORE_POLICY_KEYS),
        "restore_tested_available_for_go_no_go": readiness["restore_tested"],
        "production_restore_policy_available_for_go_no_go": readiness[
            "production_restore_policy_available"
        ],
        "production_restore_tested": readiness["production_restore_tested"],
        "production_restore_policy_approved": readiness[
            "production_restore_policy_approved"
        ],
        "production_data_operations_ready": readiness["production_data_operations_ready"],
        "data_operations_readiness_status": readiness["status"],
        "commercial_status_after_profile": go_no_go["commercial_status"],
        "production_launch_status_after_profile": go_no_go["production_launch_status"],
        "profile_satisfied_production_checks": go_no_go["satisfied_production_checks"],
        "profile_total_production_checks": go_no_go["total_production_checks"],
        "profile_production_blocker_count": go_no_go["production_blocker_count"],
        "data_operations_satisfied_blockers": satisfied_data_ops,
        "data_operations_target_blockers_satisfied_count": len(satisfied_data_ops),
        "restore_tested_satisfied_by_profile": "restore_tested" in satisfied_data_ops,
        "production_restore_policy_satisfied_by_profile": (
            "production_restore_policy" in satisfied_data_ops
        ),
        "blockers_closed_by_profile": 0,
        "accepted_for_blocker_closure_count": 0,
        "human_review_required": True,
        "separate_human_launch_approval_required": True,
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
        "production_data_path_modified": False,
        "restore_to_live_path_enabled": False,
        "live_restore_performed": False,
        "credentials_restored": False,
        "private_core_restored": False,
        "next_action": (
            "Use this profile only after human-filled production restore policy "
            "evidence is present. Even if the data-operations evidence passes, "
            "all remaining production blockers and separate human launch approval remain."
        ),
    }
    write_json(profile_output_path, profile)
    write_docs(profile)
    return profile


def render_markdown(profile: dict[str, Any]) -> str:
    return f"""# SAEE Data Operations Evidence Profile v0.1

Status: local combined data-operations profile generated; default output is hold.

## Summary

- data_operations_evidence_profile_v0_1: true
- profile_scope: {profile['profile_scope']}
- profile_status: {profile['profile_status']}
- restore_tested_available_for_go_no_go: {str(profile['restore_tested_available_for_go_no_go']).lower()}
- production_restore_policy_available_for_go_no_go: {str(profile['production_restore_policy_available_for_go_no_go']).lower()}
- production_data_operations_ready: {str(profile['production_data_operations_ready']).lower()}
- commercial_status_after_profile: {profile['commercial_status_after_profile']}
- production_launch_status_after_profile: {profile['production_launch_status_after_profile']}
- profile_satisfied_production_checks: {profile['profile_satisfied_production_checks']}
- profile_total_production_checks: {profile['profile_total_production_checks']}
- profile_production_blocker_count: {profile['profile_production_blocker_count']}
- data_operations_target_blockers_satisfied_count: {profile['data_operations_target_blockers_satisfied_count']}
- blockers_closed_by_profile: 0

## What This Profile Combines

- restore-tested evidence: `{profile['restore_tested_evidence_path']}`
- production restore policy evidence: `{profile['restore_policy_evidence_path']}`
- combined go/no-go evidence: `{profile['combined_data_operations_evidence_path']}`

## Satisfied Data-operations Signals

{chr(10).join(f"- {item}" for item in profile['data_operations_satisfied_blockers']) or "- none"}

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

## Non-Closure Statement

This profile feeds current data-operations evidence into commercial go/no-go.
It does not run restore, approve production launch, close blockers by itself,
contact customers, modify production data paths, or claim production readiness.
"""


def write_docs(profile: dict[str, Any]) -> None:
    REPORT_PATH.write_text(render_markdown(profile), encoding="utf-8")
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text(
        f"""# SAEE Data Operations Evidence Profile v0.1

Status: local combined data-operations go/no-go profile; default output is hold.

data_operations_evidence_profile_v0_1: true
profile_scope: combined_restore_tested_and_restore_policy_evidence_to_go_no_go
default_profile_status: {profile['profile_status']}
restore_tested_available_for_go_no_go: {str(profile['restore_tested_available_for_go_no_go']).lower()}
production_restore_policy_available_for_go_no_go: {str(profile['production_restore_policy_available_for_go_no_go']).lower()}
production_data_operations_ready: {str(profile['production_data_operations_ready']).lower()}
profile_production_blocker_count: {profile['profile_production_blocker_count']}
blockers_closed_by_profile: 0

## Purpose

This profile is the review layer between two separate data-operations evidence
sources and the commercial go/no-go aggregator:

1. restore-tested evidence from the local public-shell restore drill;
2. human-filled production restore policy evidence.

It produces a single data-operations evidence file for go/no-go evaluation
without approving restore policy, executing restore, modifying live data paths,
or changing product behavior.

## Required Design Check

1. Evolution subsystem strengthened: Evolutionary Archive / Rollback Immune
   System.
2. It improves rollback review by combining restore-tested evidence and
   restore-policy evidence into one explicit go/no-go input.
3. It preserves safety, license, supply-chain, permission, customer-data, and
   private-core boundaries.
4. It does not push SAEE into audit-first framing; it is a commercial
   readiness profile around rollback safety.

## Recommendation Gate Answer

answer: conditional
recommend_for_human_go_no_go_review: true
recommend_for_blocker_closure_by_profile_alone: false
recommend_for_production_launch: false
recommend_for_live_restore: false

## Boundary

production_ready: false
customer_validated: false
product_launched: false
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

- profile JSON: `phase_b_product/commercial_readiness/data_operations_evidence/data_operations_evidence_profile.local.json`
- combined evidence JSON: `phase_b_product/commercial_readiness/data_operations_evidence/production_data_operations_evidence.combined_profile.local.json`
- report: `phase_b_product/commercial_readiness/data_operations_evidence/data_operations_evidence_profile_report.md`
- runner: `scripts/saee_data_operations_evidence_profile.py`
- smoke: `scripts/saee_data_operations_evidence_profile_smoke.py`
""",
        encoding="utf-8",
    )
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(
        """# SAEE Data Operations Evidence Profile Recommendation Gate

answer: conditional

recommend_for_human_go_no_go_review: true
recommend_for_blocker_closure_by_profile_alone: false
recommend_for_production_launch: false
recommend_for_live_restore: false
recommend_for_external_execution: false

## Reason

The profile is useful because commercial go/no-go accepts one
data-operations evidence path. This profile combines restore-tested evidence
and production restore policy evidence into that one path. It does not create
either evidence source, approve policy, run restore, or close blockers by
itself.

## Boundary

production_ready: false
customer_validated: false
product_launched: false
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
blockers_closed_by_profile: 0
""",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--restore-tested-evidence", default=str(DEFAULT_RESTORE_TESTED_EVIDENCE))
    parser.add_argument("--restore-policy-evidence", default=str(DEFAULT_RESTORE_POLICY_EVIDENCE))
    parser.add_argument("--profile-output", default=str(DEFAULT_PROFILE_JSON))
    parser.add_argument("--combined-output", default=str(DEFAULT_COMBINED_EVIDENCE))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    profile = build_profile(
        Path(args.restore_tested_evidence).expanduser(),
        Path(args.restore_policy_evidence).expanduser(),
        Path(args.profile_output).expanduser(),
        Path(args.combined_output).expanduser(),
    )
    if args.json:
        print(json.dumps(profile, indent=2, sort_keys=True))
    else:
        print(
            "SAEE_DATA_OPERATIONS_EVIDENCE_PROFILE: PASS "
            f"profile_status={profile['profile_status']} "
            f"restore_tested={str(profile['restore_tested_available_for_go_no_go']).lower()} "
            "production_restore_policy="
            f"{str(profile['production_restore_policy_available_for_go_no_go']).lower()} "
            f"production_blockers={profile['profile_production_blocker_count']} "
            "blockers_closed_by_profile=0"
        )


if __name__ == "__main__":
    main()
