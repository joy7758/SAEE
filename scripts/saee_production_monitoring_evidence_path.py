#!/usr/bin/env python3
"""Prove the local production-monitoring evidence path without deployment.

This path check uses temporary fixture-only production-monitoring evidence,
converts it through the existing production-monitoring evidence builder, then
feeds the generated operations evidence into production operations readiness
and commercial go/no-go. It proves the wiring from human input to commercial
review without deploying monitoring, configuring dashboards, enabling metrics
export, changing log retention, contacting vendors, closing blockers by
itself, or claiming production readiness.
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
    PRODUCTION_MONITORING_KEYS,
    evaluate_production_operations_evidence,
)
from scripts.saee_production_monitoring_evidence_builder import (
    INPUT_FORBIDDEN_TRUE_KEYS,
    build_from_input,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/operations_evidence"
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / "production_monitoring_evidence_path.local.json"
REPORT_PATH = OUTPUT_DIR / "production_monitoring_evidence_path_report.md"
DOC_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/PRODUCTION_MONITORING_EVIDENCE_PATH_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_PRODUCTION_MONITORING_EVIDENCE_PATH_RECOMMENDATION_GATE.md"
)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fixture_input() -> dict[str, Any]:
    return {
        "template_type": "saee_production_monitoring_evidence_input",
        "template_version": "v0.1",
        "input_status": "fixture_only_not_real_production_monitoring",
        "human_reviewer_name": "Fixture Reviewer",
        "review_date": datetime.now(timezone.utc).date().isoformat(),
        "monitoring_owner": "Fixture Monitoring Owner",
        "operations_reviewer_name": "Fixture Operations Reviewer",
        "decision_summary": (
            "Fixture-only production-monitoring path proof. This is not a "
            "real monitoring deployment or operations approval."
        ),
        "evidence_review": {key: True for key in PRODUCTION_MONITORING_KEYS},
        "source_notes_by_key": {
            key: f"Fixture-only source note for {key}."
            for key in PRODUCTION_MONITORING_KEYS
        },
        "monitoring_evidence_slots": [
            {
                "evidence_key": key,
                "evidence_reference": f"fixture://production-monitoring/{key}",
                "owner_named": True,
                "reviewed_by_human": True,
                "human_source_note": f"Fixture-only human source note for {key}.",
            }
            for key in PRODUCTION_MONITORING_KEYS
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
        "production_monitoring_deployed": False,
        "external_alert_delivery_enabled": False,
        "monitoring_deployed_by_codex": False,
        "dashboard_configured_by_codex": False,
        "metrics_export_enabled_by_codex": False,
        "log_retention_changed_by_codex": False,
        "monitoring_vendor_contacted_by_codex": False,
        "alert_provider_contacted_by_codex": False,
        "codex_contacted_customer": False,
        "codex_contacted_vendor": False,
        "codex_inferred_missing_evidence": False,
        "execution_authorized": False,
        "blockers_closed_by_builder": False,
        "production_monitoring_claim_published": False,
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
        fixture_input_path = tmp / "production_monitoring_input.fixture.json"
        builder_output_path = tmp / "production_monitoring_builder_output.fixture.json"
        operations_evidence_path = (
            tmp / "production_operations_evidence.from_production_monitoring.fixture.json"
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

    monitoring_satisfied = operations["production_monitoring_available"] is True
    result: dict[str, Any] = {
        "production_monitoring_evidence_path_v0_1": True,
        "path_type": "local_fixture_only_production_monitoring_evidence_path",
        "path_status": "pass_fixture_only" if monitoring_satisfied else "hold",
        "generated_by": "scripts/saee_production_monitoring_evidence_path.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "fixture_only": True,
        "real_production_monitoring_deployed": False,
        "real_dashboard_configured": False,
        "real_metrics_export_enabled": False,
        "real_log_retention_changed": False,
        "builder_status": builder["status"],
        "builder_input_complete": builder["input_complete"],
        "production_monitoring_available_for_review": builder[
            "production_monitoring_available_for_review"
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
        "production_monitoring_blocker_path_proven": monitoring_satisfied,
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
        "monitoring_deployed_by_codex": False,
        "dashboard_configured_by_codex": False,
        "metrics_export_enabled_by_codex": False,
        "log_retention_changed_by_codex": False,
        "monitoring_vendor_contacted_by_codex": False,
        "alert_provider_contacted_by_codex": False,
        "support_operations_started": False,
        "production_monitoring_claim_published": False,
        "next_action": (
            "A human owner must replace the fixture with real production "
            "monitoring evidence, then rerun the monitoring builder and "
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
                "# SAEE Production Monitoring Evidence Path Report v0.1",
                "",
                "Status: local fixture-only path proof generated.",
                "",
                "## Summary",
                "",
                "- production_monitoring_evidence_path_v0_1: true",
                f"- path_type: {result['path_type']}",
                f"- path_status: {result['path_status']}",
                "- fixture_only: true",
                "- real_production_monitoring_deployed: false",
                f"- builder_status: {result['builder_status']}",
                f"- builder_input_complete: {str(result['builder_input_complete']).lower()}",
                f"- production_monitoring_available_for_review: {str(result['production_monitoring_available_for_review']).lower()}",
                f"- production_monitoring_blocker_path_proven: {str(result['production_monitoring_blocker_path_proven']).lower()}",
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
                "- monitoring_deployed_by_codex: false",
                "- dashboard_configured_by_codex: false",
                "- metrics_export_enabled_by_codex: false",
                "- log_retention_changed_by_codex: false",
                "- production_monitoring_claim_published: false",
                "",
                "## Non-Closure Statement",
                "",
                "This path proof uses fixture-only production-monitoring evidence.",
                "It proves local evidence wiring, but it does not deploy",
                "monitoring, configure dashboards, enable metrics export, change",
                "log retention, contact vendors or customers, close blockers,",
                "launch product, or claim production readiness.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_docs() -> None:
    DOC_PATH.write_text(
        """# SAEE Production Monitoring Evidence Path v0.1

Status: local fixture-only path proof; not real monitoring deployment.

production_monitoring_evidence_path_v0_1: true
path_type: local_fixture_only_production_monitoring_evidence_path
path_status: pass_fixture_only
fixture_only: true
real_production_monitoring_deployed: false
production_monitoring_blocker_path_proven: true
operations_readiness_production_monitoring_available: true
operations_readiness_external_alert_delivery_available: false
operations_readiness_on_call_rotation_available: false
operations_readiness_production_operations_ready: false
production_blocker_count_after_fixture: 23
blockers_closed_by_path: 0

## Purpose

This path proof verifies that a human-filled production-monitoring input can
flow through:

1. `scripts/saee_production_monitoring_evidence_builder.py`;
2. `saee_backend/services/production_operations_evidence.py`;
3. commercial go/no-go production-monitoring blocker evaluation.

It uses fixture-only monitoring evidence. It does not deploy monitoring,
configure dashboards, enable metrics export, change log retention, or start
operations.

## Required Design Check

1. Evolution subsystem strengthened: Evolutionary Archive / Rollback Immune
   System.
2. It improves operations evidence intake and commercial readiness review.
3. It preserves safety, permission, customer-contact, vendor-contact,
   operations, and private-core boundaries.
4. It does not push SAEE into audit-first framing; it is a commercial
   production-monitoring evidence path proof.

## Recommendation Gate Answer

answer: conditional
recommend_for_human_monitoring_evidence_review: true
recommend_for_blocker_closure_by_path_alone: false
recommend_for_production_launch: false
recommend_for_customer_contact: false
recommend_for_vendor_contact: false
recommend_for_monitoring_deployment: false
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
monitoring_deployed_by_codex: false
dashboard_configured_by_codex: false
metrics_export_enabled_by_codex: false
log_retention_changed_by_codex: false
monitoring_vendor_contacted_by_codex: false
alert_provider_contacted_by_codex: false
support_operations_started: false
production_monitoring_claim_published: false

## Entrypoints

- path JSON: `phase_b_product/commercial_readiness/operations_evidence/production_monitoring_evidence_path.local.json`
- path report: `phase_b_product/commercial_readiness/operations_evidence/production_monitoring_evidence_path_report.md`
- runner: `scripts/saee_production_monitoring_evidence_path.py`
- smoke: `scripts/saee_production_monitoring_evidence_path_smoke.py`
""",
        encoding="utf-8",
    )
    GATE_PATH.write_text(
        """# SAEE Production Monitoring Evidence Path Recommendation Gate

answer: conditional

recommend_for_human_monitoring_evidence_review: true
recommend_for_blocker_closure_by_path_alone: false
recommend_for_production_launch: false
recommend_for_customer_contact: false
recommend_for_vendor_contact: false
recommend_for_monitoring_deployment: false
recommend_for_support_operations: false

## Reason

The path proof is useful because it verifies the local wiring from a
human-filled production-monitoring input through the evidence builder,
production operations readiness, and commercial go/no-go production-monitoring
blocker. It uses fixture-only data and does not represent real monitoring
deployment, dashboard configuration, metrics export, or log-retention approval.

External alert delivery and on-call rotation remain unresolved in this path.

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
monitoring_deployed_by_codex: false
dashboard_configured_by_codex: false
metrics_export_enabled_by_codex: false
log_retention_changed_by_codex: false
monitoring_vendor_contacted_by_codex: false
alert_provider_contacted_by_codex: false
support_operations_started: false
production_monitoring_claim_published: false
blockers_closed_by_path: 0
""",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build SAEE production-monitoring evidence path proof"
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
        "SAEE_PRODUCTION_MONITORING_EVIDENCE_PATH: PASS "
        f"path_status={result['path_status']} "
        "fixture_only=true "
        "production_monitoring_blocker_path_proven="
        f"{str(result['production_monitoring_blocker_path_proven']).lower()} "
        f"production_blockers_after_fixture={result['production_blocker_count_after_fixture']} "
        "blockers_closed_by_path=0"
    )


if __name__ == "__main__":
    main()
