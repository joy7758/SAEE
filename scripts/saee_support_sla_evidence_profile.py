#!/usr/bin/env python3
"""Build a combined SAEE support/SLA evidence profile.

This profile combines support-contact, customer-support, SLA, and on-call
evidence into the single production support/SLA evidence file consumed by
commercial go/no-go checks. It does not publish a support contact, start a
support desk, approve SLA terms, start on-call, contact customers or vendors,
close blockers by itself, modify product behavior, or claim production
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
from saee_backend.services.production_support_evidence import (
    CUSTOMER_SUPPORT_KEYS,
    FORBIDDEN_TRUE_KEYS,
    ON_CALL_KEYS,
    SLA_KEYS,
    SUPPORT_CONTACT_KEYS,
    evaluate_production_support_evidence,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
DEFAULT_SOURCE_PATHS = {
    "support_contact": OUTPUT_DIR
    / "production_support_sla_evidence.from_support_contact.local.json",
    "customer_support": OUTPUT_DIR
    / "production_support_sla_evidence.from_customer_support.local.json",
    "sla": OUTPUT_DIR / "production_support_sla_evidence.from_sla.local.json",
    "on_call_rotation": OUTPUT_DIR
    / "production_support_sla_evidence.from_on_call.local.json",
}
SOURCE_KEY_GROUPS = {
    "support_contact": SUPPORT_CONTACT_KEYS,
    "customer_support": CUSTOMER_SUPPORT_KEYS,
    "sla": SLA_KEYS,
    "on_call_rotation": ON_CALL_KEYS,
}
TARGET_BLOCKERS = tuple(SOURCE_KEY_GROUPS)
DEFAULT_PROFILE_JSON = OUTPUT_DIR / "support_sla_evidence_profile.local.json"
DEFAULT_COMBINED_EVIDENCE = (
    OUTPUT_DIR / "production_support_sla_evidence.combined_profile.local.json"
)
REPORT_PATH = OUTPUT_DIR / "support_sla_evidence_profile_report.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/SUPPORT_SLA_EVIDENCE_PROFILE_V0_1.md"
GATE_PATH = (
    ROOT / "docs/strategy/SAEE_SUPPORT_SLA_EVIDENCE_PROFILE_RECOMMENDATION_GATE.md"
)

EXTRA_FORBIDDEN_SOURCE_TRUE_KEYS = (
    "backend_modified",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "codex_published_support_contact",
    "codex_sent_support_contact_test",
    "support_process_started_by_codex",
    "support_case_created_by_codex",
    "customer_communication_sent_by_codex",
    "support_vendor_contacted_by_codex",
    "sla_published_by_codex",
    "sla_approved_by_codex",
    "legal_review_completed_by_codex",
    "support_hours_published_by_codex",
    "response_targets_published_by_codex",
    "on_call_rotation_started_by_codex",
    "escalation_schedule_published_by_codex",
    "incident_commander_assigned_by_codex",
    "support_operations_started",
    "codex_contacted_customer",
    "codex_contacted_vendor",
    "codex_inferred_missing_evidence",
    "execution_authorized",
    "blockers_closed_by_builder",
    "customer_support_claim_published",
    "production_sla_claim_published",
    "production_on_call_claim_published",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_SUPPORT_SLA_EVIDENCE_PROFILE: FAIL: " + message)


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
            f"SAEE_SUPPORT_SLA_EVIDENCE_PROFILE: FAIL: invalid evidence {path}: {exc}"
        ) from exc
    require(isinstance(data, dict), f"evidence file must be an object: {path}")
    return data


def source_is_support_evidence(data: dict[str, Any]) -> bool:
    return data.get("support_evidence_type") == "production_support_sla_evidence"


def all_true(data: dict[str, Any], keys: tuple[str, ...]) -> bool:
    return all(data.get(key) is True for key in keys)


def source_boundary_violations(label: str, data: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    if data and not source_is_support_evidence(data):
        violations.append(f"{label}.support_evidence_type_invalid")
    if int(data.get("source_boundary_violation_count", 0) or 0) > 0:
        violations.append(f"{label}.source_boundary_violation_count")
    for key in FORBIDDEN_TRUE_KEYS + EXTRA_FORBIDDEN_SOURCE_TRUE_KEYS:
        if data.get(key) is True:
            violations.append(f"{label}.{key}")
    return violations


def build_combined_evidence(
    sources: dict[str, dict[str, Any]],
    *,
    source_violation_count: int,
) -> dict[str, Any]:
    evidence: dict[str, Any] = {
        "support_evidence_type": "production_support_sla_evidence",
        "evidence_scope": "combined_support_sla_evidence_profile_to_go_no_go",
        "evidence_version": "v0.1",
        "generated_by": "scripts/saee_support_sla_evidence_profile.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_boundary_violation_count": source_violation_count,
        "profile_note": (
            "Combined support/SLA profile. Support contact, customer-support, "
            "SLA, and on-call evidence remain separately sourced."
        ),
    }
    safe = source_violation_count == 0
    for label, keys in SOURCE_KEY_GROUPS.items():
        source = sources.get(label, {})
        evidence[f"{label}_source_scope"] = source.get("evidence_scope", "")
        for key in keys:
            evidence[key] = safe and source.get(key) is True
    for key in FORBIDDEN_TRUE_KEYS:
        evidence[key] = False
    for key in EXTRA_FORBIDDEN_SOURCE_TRUE_KEYS:
        evidence[key] = False
    return evidence


def support_readiness(path: Path, support_contact: str) -> dict[str, object]:
    return evaluate_production_support_evidence(
        load_settings(
            {
                "SAEE_PRODUCTION_SUPPORT_EVIDENCE_PATH": str(path),
                "SAEE_SUPPORT_CONTACT": support_contact,
            }
        )
    )


def commercial_status(path: Path, support_contact: str) -> dict[str, object]:
    return evaluate_commercial_go_no_go(
        load_settings(
            {
                "SAEE_PRODUCTION_SUPPORT_EVIDENCE_PATH": str(path),
                "SAEE_SUPPORT_CONTACT": support_contact,
            }
        )
    )


def profile_status(readiness: dict[str, object], source_violations: list[str]) -> str:
    if source_violations or readiness["status"] == "stop":
        return "stop"
    if readiness["production_support_available"] is True:
        return "pass"
    return "hold"


def target_blocker_state(go_no_go: dict[str, Any]) -> tuple[list[str], list[str]]:
    blockers = go_no_go.get("blockers", [])
    require(isinstance(blockers, list), "go/no-go blockers must be a list")
    satisfied: list[str] = []
    unsatisfied: list[str] = []
    for item in blockers:
        if not isinstance(item, dict):
            continue
        blocker_id = item.get("blocker_id")
        if blocker_id not in TARGET_BLOCKERS:
            continue
        if item.get("satisfied") is True:
            satisfied.append(str(blocker_id))
        else:
            unsatisfied.append(str(blocker_id))
    return satisfied, unsatisfied


def build_profile(
    source_paths: dict[str, Path],
    profile_output_path: Path,
    combined_evidence_path: Path,
    *,
    support_contact: str,
    write_documentation: bool = True,
) -> dict[str, Any]:
    sources = {label: read_evidence(path) for label, path in source_paths.items()}
    source_violations = [
        violation
        for label, data in sources.items()
        for violation in source_boundary_violations(f"{label}_source", data)
    ]
    combined_evidence = build_combined_evidence(
        sources,
        source_violation_count=len(source_violations),
    )
    write_json(combined_evidence_path, combined_evidence)
    readiness = support_readiness(combined_evidence_path, support_contact)
    go_no_go = commercial_status(combined_evidence_path, support_contact)
    target_satisfied, target_unsatisfied = target_blocker_state(go_no_go)
    status = profile_status(readiness, source_violations)

    profile: dict[str, Any] = {
        "support_sla_evidence_profile_v0_1": True,
        "profile_type": "saee_support_sla_evidence_profile",
        "profile_version": "v0.1",
        "profile_scope": "combined_support_sla_evidence_profile_to_go_no_go",
        "generated_by": "scripts/saee_support_sla_evidence_profile.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "profile_output_path": str(profile_output_path),
        "combined_support_sla_evidence_path": str(combined_evidence_path),
        "source_paths": {label: str(path) for label, path in source_paths.items()},
        "profile_status": status,
        "source_boundary_violation_count": len(source_violations),
        "source_boundary_violations": source_violations,
        "source_completion": {
            label: all_true(sources.get(label, {}), keys)
            for label, keys in SOURCE_KEY_GROUPS.items()
        },
        "support_contact_configured_for_go_no_go": bool(support_contact),
        "support_contact_evidence_complete": readiness["support_contact_available"],
        "customer_support_evidence_complete": readiness["customer_support_available"],
        "sla_evidence_complete": readiness["sla_available"],
        "on_call_rotation_evidence_complete": readiness["on_call_rotation_available"],
        "production_support_available": readiness["production_support_available"],
        "support_evidence_readiness_status": readiness["status"],
        "commercial_status_after_profile": go_no_go["commercial_status"],
        "production_launch_status_after_profile": go_no_go["production_launch_status"],
        "profile_satisfied_production_checks": go_no_go["satisfied_production_checks"],
        "profile_total_production_checks": go_no_go["total_production_checks"],
        "profile_production_blocker_count": go_no_go["production_blocker_count"],
        "target_blocker_ids": list(TARGET_BLOCKERS),
        "target_blockers_satisfied": target_satisfied,
        "target_blockers_unsatisfied": target_unsatisfied,
        "target_blockers_satisfied_count": len(target_satisfied),
        "blockers_closed_by_profile": 0,
        "accepted_for_blocker_closure_count": 0,
        "human_review_required": True,
        "separate_human_launch_approval_required": True,
        "development_permission_granted": False,
        "task_candidates_executed": False,
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
        "support_vendor_contacted": False,
        "customer_facing_support_contact_configured": False,
        "support_contact_published": False,
        "support_contact_test_sent": False,
        "staffed_support_started": False,
        "support_case_created": False,
        "sla_published": False,
        "on_call_rotation_started": False,
        "support_operations_started": False,
        "next_action": (
            "Use this profile only after all four support/SLA evidence sources "
            "are human-filled and a support contact is explicitly configured. "
            "Even if support/SLA evidence passes, all remaining production "
            "blockers and separate human launch approval remain."
        ),
    }
    write_json(profile_output_path, profile)
    if write_documentation:
        write_report(profile, sources)
        write_docs()
    return profile


def write_report(profile: dict[str, Any], sources: dict[str, dict[str, Any]]) -> None:
    satisfied = profile["target_blockers_satisfied"] or ["none"]
    source_lines = [
        f"- {label}: `{path}`"
        for label, path in profile["source_paths"].items()
    ]
    REPORT_PATH.write_text(
        "\n".join(
            [
                "# SAEE Support / SLA Evidence Profile v0.1",
                "",
                "Status: local combined support/SLA profile generated; default output is hold.",
                "",
                "## Summary",
                "",
                "- support_sla_evidence_profile_v0_1: true",
                f"- profile_scope: {profile['profile_scope']}",
                f"- profile_status: {profile['profile_status']}",
                f"- support_contact_configured_for_go_no_go: {str(profile['support_contact_configured_for_go_no_go']).lower()}",
                f"- support_contact_evidence_complete: {str(profile['support_contact_evidence_complete']).lower()}",
                f"- customer_support_evidence_complete: {str(profile['customer_support_evidence_complete']).lower()}",
                f"- sla_evidence_complete: {str(profile['sla_evidence_complete']).lower()}",
                f"- on_call_rotation_evidence_complete: {str(profile['on_call_rotation_evidence_complete']).lower()}",
                f"- production_support_available: {str(profile['production_support_available']).lower()}",
                f"- commercial_status_after_profile: {profile['commercial_status_after_profile']}",
                f"- production_launch_status_after_profile: {profile['production_launch_status_after_profile']}",
                f"- profile_satisfied_production_checks: {profile['profile_satisfied_production_checks']}",
                f"- profile_total_production_checks: {profile['profile_total_production_checks']}",
                f"- profile_production_blocker_count: {profile['profile_production_blocker_count']}",
                f"- target_blockers_satisfied_count: {profile['target_blockers_satisfied_count']}",
                f"- blockers_closed_by_profile: {profile['blockers_closed_by_profile']}",
                "",
                "## What This Profile Combines",
                "",
                *source_lines,
                "",
                "## Satisfied Support / SLA Signals",
                "",
                *[f"- {item}" for item in satisfied],
                "",
                "## Boundary",
                "",
                "- production_ready: false",
                "- customer_validated: false",
                "- product_launched: false",
                "- private_core_exposed: false",
                "- runtime_modified: false",
                "- backend_modified: false",
                "- kernel_modified: false",
                "- api_schema_modified: false",
                "- external_calls_made: false",
                "- customer_contacted: false",
                "- support_vendor_contacted: false",
                "- support_contact_published: false",
                "- support_contact_test_sent: false",
                "- staffed_support_started: false",
                "- support_case_created: false",
                "- sla_published: false",
                "- on_call_rotation_started: false",
                "- support_operations_started: false",
                "",
                "## Non-Closure Statement",
                "",
                "This profile feeds current support/SLA evidence into commercial go/no-go.",
                "It does not publish support contact details, staff support, create support cases,",
                "publish SLA terms, start on-call, contact customers or vendors, close blockers by itself,",
                "or claim production readiness.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_docs() -> None:
    DOC_PATH.write_text(
        """# SAEE Support / SLA Evidence Profile v0.1

Status: local combined support/SLA go/no-go profile; default output is hold.

support_sla_evidence_profile_v0_1: true
profile_scope: combined_support_sla_evidence_profile_to_go_no_go
default_profile_status: hold
support_contact_configured_for_go_no_go: false
support_contact_evidence_complete: false
customer_support_evidence_complete: false
sla_evidence_complete: false
on_call_rotation_evidence_complete: false
production_support_available: false
profile_production_blocker_count: 24
blockers_closed_by_profile: 0

## Purpose

This profile is the review layer between four separate support/SLA evidence
sources and the commercial go/no-go aggregator:

1. support-contact evidence;
2. customer-support process evidence;
3. SLA evidence;
4. on-call rotation evidence.

It produces a single support/SLA evidence file for go/no-go evaluation without
publishing support contacts, staffing support, creating cases, publishing SLA
terms, starting on-call, contacting customers or vendors, or changing product
behavior.

## Required Design Check

1. Evolution subsystem strengthened: Evolutionary Archive / Rollback Immune
   System.
2. It improves commercial evidence review by combining support/SLA evidence
   sources into one explicit go/no-go input.
3. It preserves safety, license, supply-chain, permission, customer-data, and
   private-core boundaries.
4. It does not push SAEE into audit-first framing; it is a commercial
   readiness profile around support, SLA, and operations evidence.

## Recommendation Gate Answer

answer: conditional
recommend_for_human_go_no_go_review: true
recommend_for_blocker_closure_by_profile_alone: false
recommend_for_production_launch: false
recommend_for_support_operations: false
recommend_for_customer_contact: false

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
support_vendor_contacted: false
support_contact_published: false
support_contact_test_sent: false
staffed_support_started: false
support_case_created: false
sla_published: false
on_call_rotation_started: false
support_operations_started: false

## Entrypoints

- profile JSON: `phase_b_product/commercial_readiness/support_evidence/support_sla_evidence_profile.local.json`
- combined evidence JSON: `phase_b_product/commercial_readiness/support_evidence/production_support_sla_evidence.combined_profile.local.json`
- report: `phase_b_product/commercial_readiness/support_evidence/support_sla_evidence_profile_report.md`
- runner: `scripts/saee_support_sla_evidence_profile.py`
- smoke: `scripts/saee_support_sla_evidence_profile_smoke.py`
""",
        encoding="utf-8",
    )
    GATE_PATH.write_text(
        """# SAEE Support / SLA Evidence Profile Recommendation Gate

answer: conditional

recommend_for_human_go_no_go_review: true
recommend_for_blocker_closure_by_profile_alone: false
recommend_for_production_launch: false
recommend_for_support_operations: false
recommend_for_customer_contact: false
recommend_for_external_execution: false

## Reason

The profile is useful because commercial go/no-go accepts one support/SLA
evidence path. This profile combines support-contact, customer-support, SLA,
and on-call evidence into that one path. It does not create any evidence
source, configure or publish a support contact, staff support, publish SLA
terms, start on-call, contact customers or vendors, or close blockers by
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
support_vendor_contacted: false
support_contact_published: false
support_contact_test_sent: false
staffed_support_started: false
support_case_created: false
sla_published: false
on_call_rotation_started: false
support_operations_started: false
blockers_closed_by_profile: 0
""",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build SAEE combined support/SLA evidence profile"
    )
    parser.add_argument("--support-contact-source", type=Path, default=DEFAULT_SOURCE_PATHS["support_contact"])
    parser.add_argument("--customer-support-source", type=Path, default=DEFAULT_SOURCE_PATHS["customer_support"])
    parser.add_argument("--sla-source", type=Path, default=DEFAULT_SOURCE_PATHS["sla"])
    parser.add_argument("--on-call-source", type=Path, default=DEFAULT_SOURCE_PATHS["on_call_rotation"])
    parser.add_argument("--support-contact", default="")
    parser.add_argument("--profile-output", type=Path, default=DEFAULT_PROFILE_JSON)
    parser.add_argument("--combined-evidence-output", type=Path, default=DEFAULT_COMBINED_EVIDENCE)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_paths = {
        "support_contact": args.support_contact_source,
        "customer_support": args.customer_support_source,
        "sla": args.sla_source,
        "on_call_rotation": args.on_call_source,
    }
    profile = build_profile(
        source_paths,
        args.profile_output,
        args.combined_evidence_output,
        support_contact=args.support_contact.strip(),
    )
    if args.json:
        print(json.dumps(profile, indent=2, sort_keys=True))
        return
    print(
        "SAEE_SUPPORT_SLA_EVIDENCE_PROFILE: PASS "
        f"profile_status={profile['profile_status']} "
        f"production_support_available={str(profile['production_support_available']).lower()} "
        f"target_blockers_satisfied={profile['target_blockers_satisfied_count']} "
        f"production_blockers={profile['profile_production_blocker_count']} "
        "blockers_closed_by_profile=0"
    )


if __name__ == "__main__":
    main()
