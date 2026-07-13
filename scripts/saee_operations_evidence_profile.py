#!/usr/bin/env python3
"""Build a combined SAEE production-operations evidence profile.

This profile combines production-monitoring, external-alert-delivery, and
on-call-rotation evidence into the single operations evidence file consumed by
commercial go/no-go checks. It does not deploy monitoring, enable alerts,
start on-call, contact customers or vendors, infer missing evidence, close
blockers by itself, modify product behavior, or claim production readiness.
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
from saee_backend.services.production_operations_evidence import (
    EXTERNAL_ALERT_DELIVERY_KEYS,
    FORBIDDEN_TRUE_KEYS,
    ON_CALL_KEYS,
    PRODUCTION_MONITORING_KEYS,
    evaluate_production_operations_evidence,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/operations_evidence"
DEFAULT_PRODUCTION_MONITORING_EVIDENCE = (
    OUTPUT_DIR / "production_operations_evidence.from_production_monitoring.local.json"
)
DEFAULT_EXTERNAL_ALERT_DELIVERY_EVIDENCE = (
    OUTPUT_DIR / "production_operations_evidence.from_external_alert_delivery.local.json"
)
DEFAULT_ON_CALL_EVIDENCE = (
    OUTPUT_DIR / "production_operations_evidence.from_operations_on_call_rotation.local.json"
)
DEFAULT_PROFILE_JSON = OUTPUT_DIR / "operations_evidence_profile.local.json"
DEFAULT_COMBINED_EVIDENCE = (
    OUTPUT_DIR / "production_operations_evidence.combined_profile.local.json"
)
REPORT_PATH = OUTPUT_DIR / "operations_evidence_profile_report.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/OPERATIONS_EVIDENCE_PROFILE_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_OPERATIONS_EVIDENCE_PROFILE_RECOMMENDATION_GATE.md"
README_PATH = OUTPUT_DIR / "README.md"

EXTRA_FORBIDDEN_TRUE_KEYS = (
    "external_model_api_called",
    "external_ai_assistant_tested",
    "alert_provider_contacted_by_codex",
    "monitoring_vendor_contacted_by_codex",
    "monitoring_deployed_by_codex",
    "dashboard_configured_by_codex",
    "metrics_export_enabled_by_codex",
    "log_retention_changed_by_codex",
    "external_alert_channel_configured_by_codex",
    "external_alert_delivery_enabled_by_codex",
    "alert_delivery_test_performed_by_codex",
    "alert_routing_policy_published_by_codex",
    "escalation_schedule_published_by_codex",
    "incident_commander_assigned_by_codex",
    "on_call_rotation_started_by_codex",
    "on_call_vendor_contacted_by_codex",
    "codex_contacted_customer",
    "codex_contacted_vendor",
    "codex_inferred_missing_evidence",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_OPERATIONS_EVIDENCE_PROFILE: FAIL: " + message)


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
            f"SAEE_OPERATIONS_EVIDENCE_PROFILE: FAIL: invalid evidence {path}: {exc}"
        ) from exc
    require(isinstance(data, dict), f"evidence file must be an object: {path}")
    return data


def source_is_operations_evidence(data: dict[str, Any]) -> bool:
    return data.get("operations_evidence_type") == "production_operations_evidence"


def all_true(data: dict[str, Any], keys: tuple[str, ...]) -> bool:
    return all(data.get(key) is True for key in keys)


def source_boundary_violations(label: str, data: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    if data and not source_is_operations_evidence(data):
        violations.append(f"{label}.operations_evidence_type_invalid")
    if int(data.get("source_boundary_violation_count", 0) or 0) > 0:
        violations.append(f"{label}.source_boundary_violation_count")
    for key in (*FORBIDDEN_TRUE_KEYS, *EXTRA_FORBIDDEN_TRUE_KEYS):
        if data.get(key) is True:
            violations.append(f"{label}.{key}")
    return violations


def build_combined_evidence(
    production_monitoring: dict[str, Any],
    external_alert_delivery: dict[str, Any],
    on_call: dict[str, Any],
    *,
    source_violation_count: int,
) -> dict[str, Any]:
    evidence: dict[str, Any] = {
        "operations_evidence_type": "production_operations_evidence",
        "evidence_scope": (
            "combined_production_monitoring_external_alert_delivery_on_call_to_go_no_go"
        ),
        "evidence_version": "v0.1",
        "generated_by": "scripts/saee_operations_evidence_profile.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "production_monitoring_source_scope": production_monitoring.get("evidence_scope", ""),
        "external_alert_delivery_source_scope": external_alert_delivery.get(
            "evidence_scope", ""
        ),
        "on_call_source_scope": on_call.get("evidence_scope", ""),
        "source_boundary_violation_count": source_violation_count,
        "profile_note": (
            "Combined operations profile. Production monitoring, external "
            "alert delivery, and on-call rotation evidence remain separately sourced."
        ),
    }
    safe = source_violation_count == 0
    for key in PRODUCTION_MONITORING_KEYS:
        evidence[key] = safe and production_monitoring.get(key) is True
    for key in EXTERNAL_ALERT_DELIVERY_KEYS:
        evidence[key] = safe and external_alert_delivery.get(key) is True
    for key in ON_CALL_KEYS:
        evidence[key] = safe and on_call.get(key) is True
    for key in (*FORBIDDEN_TRUE_KEYS, *EXTRA_FORBIDDEN_TRUE_KEYS):
        evidence[key] = False
    return evidence


def operations_readiness(path: Path) -> dict[str, object]:
    return evaluate_production_operations_evidence(
        load_settings({"SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH": str(path)})
    )


def commercial_status(path: Path) -> dict[str, object]:
    return evaluate_commercial_go_no_go(
        load_settings({"SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH": str(path)})
    )


def profile_status(readiness: dict[str, object], source_violations: list[str]) -> str:
    if source_violations or readiness["status"] == "stop":
        return "stop"
    if readiness["production_operations_ready"] is True:
        return "pass"
    return "hold"


def build_profile(
    production_monitoring_path: Path,
    external_alert_delivery_path: Path,
    on_call_path: Path,
    profile_output_path: Path,
    combined_evidence_path: Path,
) -> dict[str, Any]:
    production_monitoring = read_evidence(production_monitoring_path)
    external_alert_delivery = read_evidence(external_alert_delivery_path)
    on_call = read_evidence(on_call_path)
    source_violations = [
        *source_boundary_violations("production_monitoring_source", production_monitoring),
        *source_boundary_violations("external_alert_delivery_source", external_alert_delivery),
        *source_boundary_violations("on_call_source", on_call),
    ]
    combined_evidence = build_combined_evidence(
        production_monitoring,
        external_alert_delivery,
        on_call,
        source_violation_count=len(source_violations),
    )
    write_json(combined_evidence_path, combined_evidence)
    readiness = operations_readiness(combined_evidence_path)
    go_no_go = commercial_status(combined_evidence_path)
    unsatisfied_ids = [
        str(item.get("blocker_id"))
        for item in go_no_go.get("unsatisfied_blockers", [])
        if isinstance(item, dict)
    ]
    satisfied_operations = [
        blocker_id
        for blocker_id in (
            "production_monitoring",
            "external_alert_delivery",
            "on_call_rotation",
        )
        if blocker_id not in unsatisfied_ids
    ]
    status = profile_status(readiness, source_violations)

    profile: dict[str, Any] = {
        "operations_evidence_profile_v0_1": True,
        "profile_type": "saee_operations_evidence_profile",
        "profile_version": "v0.1",
        "profile_scope": (
            "combined_production_monitoring_external_alert_delivery_on_call_to_go_no_go"
        ),
        "generated_by": "scripts/saee_operations_evidence_profile.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "production_monitoring_evidence_path": str(production_monitoring_path),
        "external_alert_delivery_evidence_path": str(external_alert_delivery_path),
        "on_call_evidence_path": str(on_call_path),
        "combined_operations_evidence_path": str(combined_evidence_path),
        "profile_output_path": str(profile_output_path),
        "profile_status": status,
        "source_boundary_violation_count": len(source_violations),
        "source_boundary_violations": source_violations,
        "production_monitoring_source_complete": all_true(
            production_monitoring, PRODUCTION_MONITORING_KEYS
        ),
        "external_alert_delivery_source_complete": all_true(
            external_alert_delivery, EXTERNAL_ALERT_DELIVERY_KEYS
        ),
        "on_call_source_complete": all_true(on_call, ON_CALL_KEYS),
        "production_monitoring_available_for_go_no_go": readiness[
            "production_monitoring_available"
        ],
        "external_alert_delivery_available_for_go_no_go": readiness[
            "external_alert_delivery_available"
        ],
        "on_call_rotation_available_for_go_no_go": readiness["on_call_rotation_available"],
        "production_operations_ready": readiness["production_operations_ready"],
        "operations_readiness_status": readiness["status"],
        "commercial_status_after_profile": go_no_go["commercial_status"],
        "production_launch_status_after_profile": go_no_go["production_launch_status"],
        "profile_satisfied_production_checks": go_no_go["satisfied_production_checks"],
        "profile_total_production_checks": go_no_go["total_production_checks"],
        "profile_production_blocker_count": go_no_go["production_blocker_count"],
        "operations_satisfied_blockers": satisfied_operations,
        "operations_target_blockers_satisfied_count": len(satisfied_operations),
        "production_monitoring_satisfied_by_profile": (
            "production_monitoring" in satisfied_operations
        ),
        "external_alert_delivery_satisfied_by_profile": (
            "external_alert_delivery" in satisfied_operations
        ),
        "on_call_rotation_satisfied_by_profile": (
            "on_call_rotation" in satisfied_operations
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
        "alert_provider_contacted": False,
        "monitoring_vendor_contacted": False,
        "production_monitoring_deployed": False,
        "external_alert_delivery_enabled": False,
        "on_call_rotation_started_by_codex": False,
        "escalation_schedule_published_by_codex": False,
        "incident_commander_assigned_by_codex": False,
        "next_action": (
            "Use this profile only after human-filled production monitoring, "
            "external alert delivery, and on-call rotation evidence are present. "
            "Even if operations evidence passes, all remaining production blockers "
            "and separate human launch approval remain."
        ),
    }
    write_json(profile_output_path, profile)
    write_docs(profile)
    return profile


def render_markdown(profile: dict[str, Any]) -> str:
    satisfied = "\n".join(f"- {item}" for item in profile["operations_satisfied_blockers"])
    if not satisfied:
        satisfied = "- none"
    return f"""# SAEE Operations Evidence Profile v0.1

Status: local combined operations profile generated; default output is hold.

## Summary

- operations_evidence_profile_v0_1: true
- profile_scope: {profile['profile_scope']}
- profile_status: {profile['profile_status']}
- production_monitoring_available_for_go_no_go: {str(profile['production_monitoring_available_for_go_no_go']).lower()}
- external_alert_delivery_available_for_go_no_go: {str(profile['external_alert_delivery_available_for_go_no_go']).lower()}
- on_call_rotation_available_for_go_no_go: {str(profile['on_call_rotation_available_for_go_no_go']).lower()}
- production_operations_ready: {str(profile['production_operations_ready']).lower()}
- commercial_status_after_profile: {profile['commercial_status_after_profile']}
- production_launch_status_after_profile: {profile['production_launch_status_after_profile']}
- profile_satisfied_production_checks: {profile['profile_satisfied_production_checks']}
- profile_total_production_checks: {profile['profile_total_production_checks']}
- profile_production_blocker_count: {profile['profile_production_blocker_count']}
- operations_target_blockers_satisfied_count: {profile['operations_target_blockers_satisfied_count']}
- blockers_closed_by_profile: 0

## What This Profile Combines

- production monitoring evidence: `{profile['production_monitoring_evidence_path']}`
- external alert delivery evidence: `{profile['external_alert_delivery_evidence_path']}`
- on-call rotation evidence: `{profile['on_call_evidence_path']}`
- combined go/no-go evidence: `{profile['combined_operations_evidence_path']}`

## Satisfied Operations Signals

{satisfied}

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
- external_model_api_called: false
- external_ai_assistant_tested: false
- customer_contacted: false
- alert_provider_contacted: false
- monitoring_vendor_contacted: false
- production_monitoring_deployed: false
- external_alert_delivery_enabled: false
- on_call_rotation_started_by_codex: false
- escalation_schedule_published_by_codex: false
- incident_commander_assigned_by_codex: false

## Non-Closure Statement

This profile feeds current operations evidence into commercial go/no-go. It
does not deploy monitoring, enable alert delivery, start on-call rotation,
publish escalation schedules, assign incident commanders, contact customers or
vendors, close blockers by itself, or claim production readiness.
"""


def write_docs(profile: dict[str, Any]) -> None:
    REPORT_PATH.write_text(render_markdown(profile), encoding="utf-8")
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text(
        f"""# SAEE Operations Evidence Profile v0.1

Status: local combined production-operations go/no-go profile; default output is hold.

operations_evidence_profile_v0_1: true
profile_scope: combined_production_monitoring_external_alert_delivery_on_call_to_go_no_go
default_profile_status: {profile['profile_status']}
production_monitoring_available_for_go_no_go: {str(profile['production_monitoring_available_for_go_no_go']).lower()}
external_alert_delivery_available_for_go_no_go: {str(profile['external_alert_delivery_available_for_go_no_go']).lower()}
on_call_rotation_available_for_go_no_go: {str(profile['on_call_rotation_available_for_go_no_go']).lower()}
production_operations_ready: {str(profile['production_operations_ready']).lower()}
profile_production_blocker_count: {profile['profile_production_blocker_count']}
blockers_closed_by_profile: 0

## Purpose

This profile is the review layer between three separate operations evidence
sources and the commercial go/no-go aggregator:

1. human-filled production monitoring evidence;
2. human-filled external alert delivery evidence;
3. human-filled operations on-call rotation evidence.

It produces a single operations evidence file for go/no-go evaluation without
deploying monitoring, enabling alerts, starting on-call, assigning incident
command, contacting customers or vendors, or changing product behavior.

## Required Design Check

1. Evolution subsystem strengthened: Evolutionary Archive / Rollback Immune
   System.
2. It improves operations review by combining monitoring, alert-delivery, and
   on-call evidence into one explicit go/no-go input.
3. It preserves safety, license, supply-chain, permission, customer, vendor,
   and private-core boundaries.
4. It does not push SAEE into audit-first framing; it is a commercial
   readiness profile around operational safety.

## Recommendation Gate Answer

answer: conditional
recommend_for_human_go_no_go_review: true
recommend_for_blocker_closure_by_profile_alone: false
recommend_for_production_launch: false
recommend_for_monitoring_deployment: false
recommend_for_external_alert_enablement: false
recommend_for_on_call_activation: false

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
external_model_api_called: false
external_ai_assistant_tested: false
customer_contacted: false
alert_provider_contacted: false
monitoring_vendor_contacted: false
production_monitoring_deployed: false
external_alert_delivery_enabled: false
on_call_rotation_started_by_codex: false
escalation_schedule_published_by_codex: false
incident_commander_assigned_by_codex: false

## Entrypoints

- profile JSON: `phase_b_product/commercial_readiness/operations_evidence/operations_evidence_profile.local.json`
- combined evidence JSON: `phase_b_product/commercial_readiness/operations_evidence/production_operations_evidence.combined_profile.local.json`
- report: `phase_b_product/commercial_readiness/operations_evidence/operations_evidence_profile_report.md`
- runner: `scripts/saee_operations_evidence_profile.py`
- smoke: `scripts/saee_operations_evidence_profile_smoke.py`
""",
        encoding="utf-8",
    )
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(
        """# SAEE Operations Evidence Profile Recommendation Gate

answer: conditional

recommend_for_human_go_no_go_review: true
recommend_for_blocker_closure_by_profile_alone: false
recommend_for_production_launch: false
recommend_for_monitoring_deployment: false
recommend_for_external_alert_enablement: false
recommend_for_on_call_activation: false

## Reason

The profile is useful because commercial go/no-go accepts one operations
evidence path. This profile combines production monitoring, external alert
delivery, and on-call rotation evidence into that one path. It does not create
either evidence source, deploy monitoring, enable alert delivery, start
on-call rotation, assign incident command, or close blockers by itself.

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
external_model_api_called: false
external_ai_assistant_tested: false
customer_contacted: false
alert_provider_contacted: false
monitoring_vendor_contacted: false
production_monitoring_deployed: false
external_alert_delivery_enabled: false
on_call_rotation_started_by_codex: false
escalation_schedule_published_by_codex: false
incident_commander_assigned_by_codex: false
blockers_closed_by_profile: 0
""",
        encoding="utf-8",
    )
    update_operations_evidence_readme(profile)


def operations_readme_block(profile: dict[str, Any]) -> str:
    return f"""<!-- SAEE_OPERATIONS_EVIDENCE_PROFILE_START -->
## Operations Evidence Profile v0.1

operations_evidence_profile_available: true
operations_evidence_profile_status: local_combined_operations_profile_hold
operations_evidence_profile_production_monitoring_available: {str(profile['production_monitoring_available_for_go_no_go']).lower()}
operations_evidence_profile_external_alert_delivery_available: {str(profile['external_alert_delivery_available_for_go_no_go']).lower()}
operations_evidence_profile_on_call_rotation_available: {str(profile['on_call_rotation_available_for_go_no_go']).lower()}
operations_evidence_profile_production_operations_ready: {str(profile['production_operations_ready']).lower()}
operations_evidence_profile_production_blocker_count: {profile['profile_production_blocker_count']}
operations_evidence_profile_closes_blockers: false

Profile files:

```text
operations_evidence_profile.local.json
production_operations_evidence.combined_profile.local.json
operations_evidence_profile_report.md
```

The operations evidence profile combines production monitoring, external
alert delivery, and on-call rotation evidence into one local go/no-go input.
It does not deploy monitoring, enable alert delivery, start on-call rotation,
publish escalation schedules, assign incident commanders, contact vendors or
customers, close blockers by itself, or make SAEE production-ready.
<!-- SAEE_OPERATIONS_EVIDENCE_PROFILE_END -->
"""


def update_operations_evidence_readme(profile: dict[str, Any]) -> None:
    block = operations_readme_block(profile)
    start = "<!-- SAEE_OPERATIONS_EVIDENCE_PROFILE_START -->"
    end = "<!-- SAEE_OPERATIONS_EVIDENCE_PROFILE_END -->"
    if README_PATH.exists():
        text = README_PATH.read_text(encoding="utf-8")
    else:
        text = "# SAEE Operations Evidence\n\n"
    if start in text and end in text:
        before = text.split(start, 1)[0].rstrip()
        after = text.split(end, 1)[1].lstrip()
        text = before + "\n\n" + block.rstrip() + "\n\n" + after
    else:
        text = text.rstrip() + "\n\n" + block
    README_PATH.write_text(text.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--production-monitoring-evidence",
        default=str(DEFAULT_PRODUCTION_MONITORING_EVIDENCE),
    )
    parser.add_argument(
        "--external-alert-delivery-evidence",
        default=str(DEFAULT_EXTERNAL_ALERT_DELIVERY_EVIDENCE),
    )
    parser.add_argument("--on-call-evidence", default=str(DEFAULT_ON_CALL_EVIDENCE))
    parser.add_argument("--profile-output", default=str(DEFAULT_PROFILE_JSON))
    parser.add_argument("--combined-output", default=str(DEFAULT_COMBINED_EVIDENCE))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    profile = build_profile(
        Path(args.production_monitoring_evidence).expanduser(),
        Path(args.external_alert_delivery_evidence).expanduser(),
        Path(args.on_call_evidence).expanduser(),
        Path(args.profile_output).expanduser(),
        Path(args.combined_output).expanduser(),
    )
    if args.json:
        print(json.dumps(profile, indent=2, sort_keys=True))
    else:
        print(
            "SAEE_OPERATIONS_EVIDENCE_PROFILE: PASS "
            f"profile_status={profile['profile_status']} "
            "production_monitoring="
            f"{str(profile['production_monitoring_available_for_go_no_go']).lower()} "
            "external_alert_delivery="
            f"{str(profile['external_alert_delivery_available_for_go_no_go']).lower()} "
            "on_call_rotation="
            f"{str(profile['on_call_rotation_available_for_go_no_go']).lower()} "
            f"production_blockers={profile['profile_production_blocker_count']} "
            "blockers_closed_by_profile=0"
        )


if __name__ == "__main__":
    main()
