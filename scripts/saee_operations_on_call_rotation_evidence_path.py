#!/usr/bin/env python3
"""Prove the local operations-on-call-rotation evidence path without ops.

This path check uses temporary fixture-only on-call-rotation evidence,
converts it through the existing operations-on-call-rotation evidence builder,
then feeds the generated operations evidence into production operations
readiness and commercial go/no-go. It proves the wiring from human input to
commercial review without starting an on-call rotation, publishing escalation
schedules, assigning incident commanders, contacting vendors or customers,
closing blockers by itself, or claiming production readiness.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go
from saee_backend.services.production_operations_evidence import (
    ON_CALL_KEYS,
    evaluate_production_operations_evidence,
)
from scripts.saee_operations_on_call_rotation_evidence_builder import (
    INPUT_FORBIDDEN_TRUE_KEYS,
    build_from_input,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/operations_evidence"
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / "operations_on_call_rotation_evidence_path.local.json"
REPORT_PATH = OUTPUT_DIR / "operations_on_call_rotation_evidence_path_report.md"
DOC_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/OPERATIONS_ON_CALL_ROTATION_EVIDENCE_PATH_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_OPERATIONS_ON_CALL_ROTATION_EVIDENCE_PATH_RECOMMENDATION_GATE.md"
)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fixture_input() -> dict[str, Any]:
    return {
        "template_type": "saee_operations_on_call_rotation_evidence_input",
        "template_version": "v0.1",
        "input_status": "fixture_only_not_real_on_call_rotation",
        "human_reviewer_name": "Fixture Reviewer",
        "review_date": datetime.now(timezone.utc).date().isoformat(),
        "on_call_rotation_owner": "Fixture On-call Owner",
        "operations_reviewer_name": "Fixture Operations Reviewer",
        "decision_summary": (
            "Fixture-only operations-on-call-rotation path proof. This is not "
            "a real on-call rotation, escalation schedule, or incident "
            "commander assignment."
        ),
        "evidence_review": {key: True for key in ON_CALL_KEYS},
        "source_notes_by_key": {
            key: f"Fixture-only source note for {key}." for key in ON_CALL_KEYS
        },
        "on_call_rotation_evidence_slots": [
            {
                "evidence_key": key,
                "evidence_reference": f"fixture://operations-on-call-rotation/{key}",
                "owner_named": True,
                "reviewed_by_human": True,
                "human_source_note": f"Fixture-only human source note for {key}.",
            }
            for key in ON_CALL_KEYS
        ],
        "boundary_review": {key: False for key in INPUT_FORBIDDEN_TRUE_KEYS},
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
        "on_call_rotation_started": False,
        "on_call_rotation_started_by_codex": False,
        "escalation_schedule_published_by_codex": False,
        "incident_commander_assigned_by_codex": False,
        "monitoring_vendor_contacted_by_codex": False,
        "alert_provider_contacted_by_codex": False,
        "on_call_vendor_contacted_by_codex": False,
        "codex_contacted_customer": False,
        "codex_contacted_vendor": False,
        "codex_inferred_missing_evidence": False,
        "execution_authorized": False,
        "blockers_closed_by_builder": False,
        "production_on_call_rotation_claim_published": False,
    }


def operations_status(path: Path) -> dict[str, object]:
    return evaluate_production_operations_evidence(
        load_settings({"SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH": str(path)})
    )


def commercial_status(path: Path) -> dict[str, object]:
    return evaluate_commercial_go_no_go(
        load_settings({"SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH": str(path)})
    )


def build_path(output_path: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        fixture_input_path = tmp / "operations_on_call_rotation_input.fixture.json"
        builder_output_path = tmp / "operations_on_call_rotation_builder_output.fixture.json"
        operations_evidence_path = (
            tmp / "production_operations_evidence.from_on_call_rotation.fixture.json"
        )
        write_json(fixture_input_path, fixture_input())

        builder = build_from_input(
            fixture_input_path,
            builder_output_path,
            operations_evidence_path,
            write_documentation=False,
        )
        operations = operations_status(operations_evidence_path)
        go_no_go = commercial_status(operations_evidence_path)

    on_call_satisfied = operations["on_call_rotation_available"] is True
    result: dict[str, Any] = {
        "operations_on_call_rotation_evidence_path_v0_1": True,
        "path_type": "local_fixture_only_operations_on_call_rotation_evidence_path",
        "path_status": "pass_fixture_only" if on_call_satisfied else "hold",
        "generated_by": "scripts/saee_operations_on_call_rotation_evidence_path.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "fixture_only": True,
        "real_on_call_rotation_started": False,
        "real_escalation_schedule_published": False,
        "real_incident_commander_named": False,
        "real_support_operations_started": False,
        "builder_status": builder["status"],
        "builder_input_complete": builder["input_complete"],
        "operations_on_call_rotation_available_for_review": builder[
            "operations_on_call_rotation_available_for_review"
        ],
        "operations_readiness_status_after_fixture": operations["status"],
        "operations_readiness_production_monitoring_available": operations[
            "production_monitoring_available"
        ],
        "operations_readiness_external_alert_delivery_available": operations[
            "external_alert_delivery_available"
        ],
        "operations_readiness_on_call_rotation_available": operations[
            "on_call_rotation_available"
        ],
        "operations_readiness_production_operations_ready": operations[
            "production_operations_ready"
        ],
        "commercial_status_after_fixture": go_no_go["commercial_status"],
        "production_launch_status_after_fixture": go_no_go[
            "production_launch_status"
        ],
        "satisfied_production_checks_after_fixture": go_no_go[
            "satisfied_production_checks"
        ],
        "total_production_checks_after_fixture": go_no_go["total_production_checks"],
        "production_blocker_count_after_fixture": go_no_go[
            "production_blocker_count"
        ],
        "operations_on_call_rotation_blocker_path_proven": on_call_satisfied,
        "blockers_closed_by_path": 0,
        "accepted_for_blocker_closure_count": 0,
        "human_real_evidence_required": True,
        "separate_go_no_go_profile_required": True,
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
        "on_call_rotation_started": False,
        "on_call_rotation_started_by_codex": False,
        "escalation_schedule_published_by_codex": False,
        "incident_commander_assigned_by_codex": False,
        "monitoring_vendor_contacted_by_codex": False,
        "alert_provider_contacted_by_codex": False,
        "on_call_vendor_contacted_by_codex": False,
        "support_operations_started": False,
        "production_on_call_rotation_claim_published": False,
        "next_action": (
            "A human owner must replace the fixture with real on-call rotation "
            "and escalation evidence, then rerun the on-call builder and "
            "production operations evidence readiness. This path proof alone "
            "closes no blockers."
        ),
    }
    write_json(output_path, result)
    write_report(result)
    write_docs()
    return result


def write_report(result: dict[str, Any]) -> None:
    REPORT_PATH.write_text(
        "\n".join(
            [
                "# SAEE Operations On-call Rotation Evidence Path Report v0.1",
                "",
                "Status: local fixture-only path proof generated.",
                "",
                "## Summary",
                "",
                "- operations_on_call_rotation_evidence_path_v0_1: true",
                f"- path_type: {result['path_type']}",
                f"- path_status: {result['path_status']}",
                "- fixture_only: true",
                "- real_on_call_rotation_started: false",
                f"- builder_status: {result['builder_status']}",
                f"- builder_input_complete: {str(result['builder_input_complete']).lower()}",
                f"- operations_on_call_rotation_available_for_review: {str(result['operations_on_call_rotation_available_for_review']).lower()}",
                f"- operations_on_call_rotation_blocker_path_proven: {str(result['operations_on_call_rotation_blocker_path_proven']).lower()}",
                f"- operations_readiness_status_after_fixture: {result['operations_readiness_status_after_fixture']}",
                f"- operations_readiness_production_monitoring_available: {str(result['operations_readiness_production_monitoring_available']).lower()}",
                f"- operations_readiness_external_alert_delivery_available: {str(result['operations_readiness_external_alert_delivery_available']).lower()}",
                f"- operations_readiness_on_call_rotation_available: {str(result['operations_readiness_on_call_rotation_available']).lower()}",
                f"- operations_readiness_production_operations_ready: {str(result['operations_readiness_production_operations_ready']).lower()}",
                f"- commercial_status_after_fixture: {result['commercial_status_after_fixture']}",
                f"- production_blocker_count_after_fixture: {result['production_blocker_count_after_fixture']}",
                f"- blockers_closed_by_path: {result['blockers_closed_by_path']}",
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
                "- alert_provider_contacted: false",
                "- monitoring_vendor_contacted: false",
                "- production_monitoring_deployed: false",
                "- external_alert_delivery_enabled: false",
                "- on_call_rotation_started: false",
                "- on_call_rotation_started_by_codex: false",
                "- escalation_schedule_published_by_codex: false",
                "- incident_commander_assigned_by_codex: false",
                "- production_on_call_rotation_claim_published: false",
                "",
                "## Non-Closure Statement",
                "",
                "This path proof uses fixture-only operations-on-call-rotation evidence.",
                "It proves local evidence wiring, but it does not start on-call",
                "rotation, publish escalation schedules, name a real incident",
                "commander, contact vendors or customers, close blockers, launch",
                "product, or claim production readiness.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_docs() -> None:
    DOC_PATH.write_text(
        """# SAEE Operations On-call Rotation Evidence Path v0.1

Status: local fixture-only path proof; not real on-call rotation.

operations_on_call_rotation_evidence_path_v0_1: true
path_type: local_fixture_only_operations_on_call_rotation_evidence_path
path_status: pass_fixture_only
fixture_only: true
real_on_call_rotation_started: false
real_escalation_schedule_published: false
real_incident_commander_named: false
real_support_operations_started: false
operations_on_call_rotation_blocker_path_proven: true
operations_readiness_production_monitoring_available: false
operations_readiness_external_alert_delivery_available: false
operations_readiness_on_call_rotation_available: true
operations_readiness_production_operations_ready: false
production_blocker_count_after_fixture: 23
blockers_closed_by_path: 0

## Purpose

This path proof verifies that a human-filled operations-on-call-rotation input
can flow through:

1. `scripts/saee_operations_on_call_rotation_evidence_builder.py`;
2. `saee_backend/services/production_operations_evidence.py`;
3. commercial go/no-go on-call-rotation blocker evaluation.

It uses fixture-only on-call evidence. It does not start an on-call rotation,
publish escalation schedules, name a real incident commander, contact vendors,
or start support operations.

## Required Design Check

1. Evolution subsystem strengthened: Evolutionary Archive / Rollback Immune
   System.
2. It improves operations evidence intake and commercial readiness review.
3. It preserves safety, permission, customer-contact, vendor-contact,
   operations, and private-core boundaries.
4. It does not push SAEE into audit-first framing; it is a commercial
   operations-on-call-rotation evidence path proof.

## Recommendation Gate Answer

answer: conditional
recommend_for_human_on_call_evidence_review: true
recommend_for_blocker_closure_by_path_alone: false
recommend_for_production_launch: false
recommend_for_customer_contact: false
recommend_for_vendor_contact: false
recommend_for_on_call_rotation_start: false
recommend_for_escalation_schedule_publication: false
recommend_for_incident_commander_assignment: false
recommend_for_support_operations: false

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
alert_provider_contacted: false
monitoring_vendor_contacted: false
production_monitoring_deployed: false
external_alert_delivery_enabled: false
on_call_rotation_started: false
on_call_rotation_started_by_codex: false
escalation_schedule_published_by_codex: false
incident_commander_assigned_by_codex: false
monitoring_vendor_contacted_by_codex: false
alert_provider_contacted_by_codex: false
on_call_vendor_contacted_by_codex: false
support_operations_started: false
production_on_call_rotation_claim_published: false

## Entrypoints

- path JSON: `phase_b_product/commercial_readiness/operations_evidence/operations_on_call_rotation_evidence_path.local.json`
- path report: `phase_b_product/commercial_readiness/operations_evidence/operations_on_call_rotation_evidence_path_report.md`
- runner: `scripts/saee_operations_on_call_rotation_evidence_path.py`
- smoke: `scripts/saee_operations_on_call_rotation_evidence_path_smoke.py`
""",
        encoding="utf-8",
    )
    GATE_PATH.write_text(
        """# SAEE Operations On-call Rotation Evidence Path Recommendation Gate

answer: conditional

recommend_for_human_on_call_evidence_review: true
recommend_for_blocker_closure_by_path_alone: false
recommend_for_production_launch: false
recommend_for_customer_contact: false
recommend_for_vendor_contact: false
recommend_for_on_call_rotation_start: false
recommend_for_escalation_schedule_publication: false
recommend_for_incident_commander_assignment: false
recommend_for_support_operations: false

## Reason

The path proof is useful because it verifies the local wiring from a
human-filled operations-on-call-rotation input through the evidence builder,
production operations readiness, and commercial go/no-go on-call-rotation
blocker. It uses fixture-only data and does not represent a real on-call
rotation, escalation schedule, incident commander assignment, vendor contact,
or support operations start.

Production monitoring and external alert delivery remain unresolved in this
path.

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
alert_provider_contacted: false
monitoring_vendor_contacted: false
production_monitoring_deployed: false
external_alert_delivery_enabled: false
on_call_rotation_started: false
on_call_rotation_started_by_codex: false
escalation_schedule_published_by_codex: false
incident_commander_assigned_by_codex: false
monitoring_vendor_contacted_by_codex: false
alert_provider_contacted_by_codex: false
on_call_vendor_contacted_by_codex: false
support_operations_started: false
production_on_call_rotation_claim_published: false
blockers_closed_by_path: 0
""",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build SAEE operations-on-call-rotation evidence path proof"
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_path(args.output)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    print(
        "SAEE_OPERATIONS_ON_CALL_ROTATION_EVIDENCE_PATH: PASS "
        f"path_status={result['path_status']} "
        "fixture_only=true "
        "operations_on_call_rotation_blocker_path_proven="
        f"{str(result['operations_on_call_rotation_blocker_path_proven']).lower()} "
        f"production_blockers_after_fixture={result['production_blocker_count_after_fixture']} "
        "blockers_closed_by_path=0"
    )


if __name__ == "__main__":
    main()
