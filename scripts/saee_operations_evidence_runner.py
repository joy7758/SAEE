#!/usr/bin/env python3
"""Generate local public-shell operations evidence.

This runner creates a local request-audit sample, builds the existing
operations telemetry snapshot and alert-candidate policy output, and writes a
partial production-operations evidence JSON file for human review. It does not
deploy monitoring, enable external alert delivery, contact vendors, contact
customers, open browsers, call external services, or mark SAEE production-ready.
"""

from __future__ import annotations

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
from saee_backend.services.operations_alert_policy import evaluate_operations_alert_policy
from saee_backend.services.operations_telemetry import build_operations_telemetry_snapshot
from saee_backend.services.production_operations_evidence import (
    EXTERNAL_ALERT_DELIVERY_KEYS,
    FORBIDDEN_TRUE_KEYS,
    ON_CALL_KEYS,
    PRODUCTION_MONITORING_KEYS,
    evaluate_production_operations_evidence,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/operations_evidence"
OUTPUT_PATH = OUTPUT_DIR / "operations_evidence.local.json"
README_PATH = OUTPUT_DIR / "README.md"
PRESERVED_README_BLOCKS = [
    (
        "<!-- SAEE_OPERATIONS_EVIDENCE_PROFILE_START -->",
        "<!-- SAEE_OPERATIONS_EVIDENCE_PROFILE_END -->",
    ),
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _write_sample_audit_events(audit_path: Path) -> None:
    events = [
        {
            "timestamp": "2026-07-04T00:00:00+00:00",
            "request_id": "req-ops-evidence-001",
            "method": "GET",
            "path": "/health",
            "status_code": 200,
            "duration_ms": 3.2,
            "body_recorded": False,
            "credentials_recorded": False,
            "private_core_recorded": False,
        },
        {
            "timestamp": "2026-07-04T00:00:01+00:00",
            "request_id": "req-ops-evidence-002",
            "method": "POST",
            "path": "/experiment/run",
            "status_code": 200,
            "duration_ms": 42.5,
            "body_recorded": False,
            "credentials_recorded": False,
            "private_core_recorded": False,
        },
        {
            "timestamp": "2026-07-04T00:00:02+00:00",
            "request_id": "req-ops-evidence-003",
            "method": "GET",
            "path": "/operations/telemetry",
            "status_code": 200,
            "duration_ms": 5.4,
            "body_recorded": False,
            "credentials_recorded": False,
            "private_core_recorded": False,
        },
    ]
    audit_path.write_text(
        "".join(json.dumps(event, sort_keys=True) + "\n" for event in events),
        encoding="utf-8",
    )


def run_local_operations_evidence() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmpdir:
        audit_path = Path(tmpdir) / "request_audit.jsonl"
        _write_sample_audit_events(audit_path)
        settings = load_settings(
            {
                "SAEE_REQUEST_AUDIT_ENABLED": "true",
                "SAEE_REQUEST_AUDIT_PATH": str(audit_path),
            }
        )
        telemetry = build_operations_telemetry_snapshot(settings)
        alert_policy = evaluate_operations_alert_policy(settings)

    require(telemetry["telemetry_type"] == "local_public_shell_operations_telemetry", "wrong telemetry type")
    require(telemetry["event_count"] == 3, "expected three local audit events")
    require(telemetry["invalid_line_count"] == 0, "sample audit must parse cleanly")
    require(telemetry["local_operations_telemetry_available"] is True, "local telemetry must be available")
    require(telemetry["operations_telemetry_external_export_available"] is False, "must not export telemetry")
    require(telemetry["production_monitoring_available"] is False, "must not claim production monitoring")
    require(telemetry["external_calls_made"] is False, "must not call external services")
    require(telemetry["body_inspected"] is False, "must not inspect request bodies")
    require(telemetry["credentials_inspected"] is False, "must not inspect credentials")
    require(telemetry["private_core_inspected"] is False, "must not inspect private core")
    require(alert_policy["alert_policy_type"] == "local_public_shell_alert_policy", "wrong alert policy type")
    require(alert_policy["alert_candidates_generated"] is True, "alert candidates must be generated")
    require(alert_policy["external_alert_delivery_available"] is False, "must not claim external alert delivery")
    require(alert_policy["alerting_available"] is False, "must not claim production alerting")
    require(alert_policy["on_call_rotation_available"] is False, "must not claim on-call rotation")
    require(alert_policy["external_calls_made"] is False, "must not call external services")
    return {"telemetry": telemetry, "alert_policy": alert_policy}


def build_evidence() -> dict[str, Any]:
    result = run_local_operations_evidence()
    telemetry = result["telemetry"]
    alert_policy = result["alert_policy"]

    evidence: dict[str, Any] = {
        "operations_evidence_type": "production_operations_evidence",
        "evidence_scope": "local_public_shell_telemetry_alert_candidate_dry_run",
        "evidence_version": "v0.1",
        "generated_by": "scripts/saee_operations_evidence_runner.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_telemetry_helper": "saee_backend/services/operations_telemetry.py",
        "source_alert_policy_helper": "saee_backend/services/operations_alert_policy.py",
        "production_monitoring_plan_approved": False,
        "metrics_coverage_approved": False,
        "slo_dashboard_defined": False,
        "log_retention_reviewed": False,
        "monitoring_dry_run_recorded": True,
        "operations_monitoring_alert_review_packet_ready": True,
        "operations_monitoring_alert_approval_status": "not_approved",
        "operations_monitoring_alert_evidence_complete": False,
        "external_alert_channel_configured": False,
        "alert_routing_policy_approved": False,
        "alert_delivery_test_recorded": False,
        "alert_failure_handling_defined": False,
        "incident_escalation_path_defined": False,
        "alert_acknowledgement_process_defined": False,
        "on_call_rotation_defined": False,
        "escalation_schedule_defined": False,
        "incident_commander_named": False,
        "local_public_shell_results": {
            "telemetry_type": telemetry["telemetry_type"],
            "telemetry_source": telemetry["telemetry_source"],
            "event_count": telemetry["event_count"],
            "invalid_line_count": telemetry["invalid_line_count"],
            "error_count": telemetry["error_count"],
            "duration_ms_p95": telemetry["duration_ms_p95"],
            "alert_policy_type": alert_policy["alert_policy_type"],
            "alert_candidates_generated": alert_policy["alert_candidates_generated"],
            "alert_count": alert_policy["alert_count"],
            "external_alert_delivery_available": False,
            "production_monitoring_available": False,
            "on_call_rotation_available": False,
            "body_inspected": False,
            "credentials_inspected": False,
            "private_core_inspected": False,
        },
        "limitations": [
            "No production monitoring plan has been approved.",
            "No metrics coverage has been approved.",
            "No SLO dashboard has been defined.",
            "No log retention review has been completed.",
            "No external alert channel is configured.",
            "No alert delivery test has been recorded.",
            "No on-call rotation, escalation schedule, or incident commander is defined.",
            "This evidence is local public-shell evidence only and does not close the production launch gate.",
        ],
    }
    for key in FORBIDDEN_TRUE_KEYS:
        evidence[key] = False

    missing_expected = [
        key
        for key in PRODUCTION_MONITORING_KEYS
        + EXTERNAL_ALERT_DELIVERY_KEYS
        + ON_CALL_KEYS
        + FORBIDDEN_TRUE_KEYS
        if key not in evidence
    ]
    require(not missing_expected, "evidence missing keys: " + ", ".join(missing_expected))
    return evidence


def preserve_readme_blocks(content: str) -> str:
    if not README_PATH.exists():
        return content.rstrip() + "\n"
    existing = README_PATH.read_text(encoding="utf-8")
    preserved: list[str] = []
    for start, end in PRESERVED_README_BLOCKS:
        if start not in existing or end not in existing:
            continue
        block_body = existing.split(start, 1)[1].split(end, 1)[0]
        block = start + block_body + end
        if start not in content:
            preserved.append(block.strip())
    if preserved:
        content = content.rstrip() + "\n\n" + "\n\n".join(preserved)
    return content.rstrip() + "\n"


def write_readme() -> None:
    content = """# SAEE Operations Evidence

Status: local public-shell telemetry / alert-candidate evidence, not
production operations readiness.

This directory contains a generated local evidence JSON file for aggregate
request-audit telemetry and deterministic alert-candidate review. It records
only what the local runner can prove.

It does not approve production monitoring, metrics coverage, SLO dashboards,
log-retention review, external alert delivery, alert routing, on-call
rotation, incident-command assignment, vendor contact, customer contact,
runtime changes, kernel changes, API schema changes, or private-core exposure.

Primary file:

```text
operations_evidence.local.json
operations_monitoring_alert_review_packet.local.json
operations_monitoring_alert_review_packet.md
production_monitoring_evidence_input.template.json
production_monitoring_evidence_builder_output.local.json
production_operations_evidence.from_production_monitoring.local.json
production_monitoring_evidence_builder_report.md
production_monitoring_evidence_path.local.json
production_monitoring_evidence_path_report.md
external_alert_delivery_evidence_input.template.json
external_alert_delivery_approval_input_validation.local.json
external_alert_delivery_approval_input_validation.md
external_alert_delivery_approval_input_prompt.local.json
external_alert_delivery_approval_input_prompt.md
external_alert_delivery_evidence_builder_output.local.json
production_operations_evidence.from_external_alert_delivery.local.json
external_alert_delivery_evidence_builder_report.md
external_alert_delivery_evidence_path.local.json
external_alert_delivery_evidence_path_report.md
operations_on_call_rotation_evidence_input.template.json
operations_on_call_rotation_approval_input_validation.local.json
operations_on_call_rotation_approval_input_validation.md
operations_on_call_rotation_approval_input_prompt.local.json
operations_on_call_rotation_approval_input_prompt.md
operations_on_call_rotation_evidence_builder_output.local.json
production_operations_evidence.from_operations_on_call_rotation.local.json
operations_on_call_rotation_evidence_builder_report.md
operations_on_call_rotation_evidence_path.local.json
operations_on_call_rotation_evidence_path_report.md
```

Generate it with:

```bash
python3 scripts/saee_operations_evidence_runner.py
python3 scripts/saee_operations_monitoring_alert_review_packet.py
python3 scripts/saee_production_monitoring_evidence_builder.py
python3 scripts/saee_production_monitoring_evidence_path.py
python3 scripts/saee_external_alert_delivery_evidence_builder.py
python3 scripts/saee_external_alert_delivery_approval_input_validator.py
python3 scripts/saee_external_alert_delivery_approval_input_prompt.py
python3 scripts/saee_external_alert_delivery_evidence_path.py
python3 scripts/saee_operations_on_call_rotation_approval_input_validator.py
python3 scripts/saee_operations_on_call_rotation_approval_input_prompt.py
python3 scripts/saee_operations_on_call_rotation_evidence_builder.py
python3 scripts/saee_operations_on_call_rotation_evidence_path.py
```

Boundary:

```yaml
evidence_scope: local_public_shell_telemetry_alert_candidate_dry_run
operations_monitoring_alert_review_packet_ready: true
operations_monitoring_alert_evidence_complete: false
operations_monitoring_alert_approval_status: not_approved
production_monitoring_evidence_builder_available: true
production_monitoring_evidence_builder_status: local_builder_available_default_hold
production_monitoring_evidence_builder_closes_blockers: false
production_monitoring_evidence_path_available: true
production_monitoring_evidence_path_status: local_fixture_only_path_proof
production_monitoring_evidence_path_type: local_fixture_only_production_monitoring_evidence_path
production_monitoring_evidence_path_fixture_only: true
production_monitoring_evidence_path_real_monitoring_deployed: false
production_monitoring_evidence_path_blocker_path_proven: true
production_monitoring_evidence_path_operations_monitoring_available: true
production_monitoring_evidence_path_operations_external_alert_delivery_available: false
production_monitoring_evidence_path_operations_on_call_rotation_available: false
production_monitoring_evidence_path_production_blocker_count: 23
production_monitoring_evidence_path_closes_blockers: false
external_alert_delivery_evidence_builder_available: true
external_alert_delivery_evidence_builder_status: local_builder_available_default_hold
external_alert_delivery_evidence_builder_closes_blockers: false
external_alert_delivery_evidence_path_available: true
external_alert_delivery_evidence_path_status: local_fixture_only_path_proof
external_alert_delivery_evidence_path_type: local_fixture_only_external_alert_delivery_evidence_path
external_alert_delivery_evidence_path_fixture_only: true
external_alert_delivery_evidence_path_real_alert_delivery_enabled: false
external_alert_delivery_evidence_path_blocker_path_proven: true
external_alert_delivery_evidence_path_operations_monitoring_available: false
external_alert_delivery_evidence_path_operations_alert_delivery_available: true
external_alert_delivery_evidence_path_operations_on_call_rotation_available: false
external_alert_delivery_evidence_path_production_blocker_count: 23
external_alert_delivery_evidence_path_closes_blockers: false
operations_on_call_rotation_evidence_builder_available: true
operations_on_call_rotation_evidence_builder_status: local_builder_available_default_hold
operations_on_call_rotation_evidence_builder_closes_blockers: false
operations_on_call_rotation_evidence_path_available: true
operations_on_call_rotation_evidence_path_status: local_fixture_only_path_proof
operations_on_call_rotation_evidence_path_type: local_fixture_only_operations_on_call_rotation_evidence_path
operations_on_call_rotation_evidence_path_fixture_only: true
operations_on_call_rotation_evidence_path_real_on_call_started: false
operations_on_call_rotation_evidence_path_blocker_path_proven: true
operations_on_call_rotation_evidence_path_operations_monitoring_available: false
operations_on_call_rotation_evidence_path_operations_alert_delivery_available: false
operations_on_call_rotation_evidence_path_operations_on_call_path_available: true
operations_on_call_rotation_evidence_path_production_blocker_count: 23
operations_on_call_rotation_evidence_path_closes_blockers: false
production_operations_ready: false
production_monitoring_available: false
external_alert_delivery_available: false
on_call_rotation_available: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
external_calls_made: false
```

The operations monitoring / alert / on-call review packet is a draft for human
review only. It does not approve monitoring, enable external alert delivery,
run alert tests, start on-call rotation, contact customers, contact monitoring
or alert vendors, or make SAEE production-ready.

The production monitoring evidence builder converts a human-filled monitoring
input into a production operations evidence-shaped JSON file for the
`production_monitoring` group only. Its default output is hold. It does not
deploy monitoring, configure dashboards, enable metrics export, change log
retention, contact vendors, close blockers, or make SAEE production-ready.

The production monitoring evidence path uses fixture-only monitoring evidence
to prove the local wiring from human-filled monitoring input through the
builder, production operations readiness, and commercial go/no-go. It proves
that real monitoring evidence can later flow through the local review path,
but it does not deploy monitoring, configure dashboards, enable metrics
export, change log retention, contact vendors or customers, close blockers,
start support operations, or make SAEE production-ready.

The external alert delivery evidence builder converts a human-filled alert
delivery input into a production operations evidence-shaped JSON file for the
`external_alert_delivery` group only. Its default output is hold. It does not
configure alert channels, publish alert routing policy, perform alert delivery
tests, contact vendors or customers, enable external alert delivery, close
blockers, or make SAEE production-ready.

The external alert delivery evidence path uses fixture-only alert-delivery
evidence to prove the local wiring from human-filled alert delivery input
through the builder, production operations readiness, and commercial go/no-go.
It proves that real alert-delivery evidence can later flow through the local
review path, but it does not configure alert channels, publish alert routing,
perform alert delivery tests, contact providers or customers, enable external
alert delivery, close blockers, start support operations, or make SAEE
production-ready.

The operations on-call rotation evidence builder converts a human-filled
operations on-call rotation input into a production operations evidence-shaped
JSON file for the `on_call_rotation` group only. Its default output is hold. It
does not start on-call rotation, publish escalation schedules, assign incident
commanders, contact vendors or customers, send alerts, close blockers, or make
SAEE production-ready.

The operations on-call rotation evidence path uses fixture-only on-call
rotation evidence to prove the local wiring from human-filled on-call rotation
input through the builder, production operations readiness, and commercial
go/no-go. It proves that real on-call evidence can later flow through the
local review path, but it does not start on-call rotation, publish escalation
schedules, assign a real incident commander, contact providers or customers,
start support operations, close blockers, or make SAEE production-ready.
"""
    README_PATH.write_text(preserve_readme_blocks(content), encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    evidence = build_evidence()
    OUTPUT_PATH.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_readme()
    readiness = evaluate_production_operations_evidence(
        load_settings({"SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH": str(OUTPUT_PATH)})
    )
    print(
        "SAEE_OPERATIONS_EVIDENCE_RUNNER: PASS "
        f"path={OUTPUT_PATH} "
        f"status={readiness['status']} "
        "local_public_shell_evidence=true "
        "production_operations_ready=false"
    )


if __name__ == "__main__":
    main()
