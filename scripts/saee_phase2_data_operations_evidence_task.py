#!/usr/bin/env python3
"""Generate the SAEE Phase 2 data and operations evidence task packet.

This packet turns the second commercial dependency-plan phase into a
human-reviewable evidence collection task. It does not deploy monitoring,
send alerts, contact vendors, activate on-call, run restore tests, modify
production data paths, close blockers, launch product, or claim production
readiness.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.production_data_operations_evidence import (
    RESTORE_POLICY_KEYS,
    RESTORE_TEST_KEYS,
)
from saee_backend.services.production_operations_evidence import (
    EXTERNAL_ALERT_DELIVERY_KEYS,
    ON_CALL_KEYS,
    PRODUCTION_MONITORING_KEYS,
)
from scripts.saee_commercial_blocker_dependency_plan import build_dependency_plan


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/phase_2_data_operations_evidence_task"
TASK_JSON = OUTPUT_DIR / "phase_2_data_operations_evidence_task.local.json"
TASK_MD = OUTPUT_DIR / "phase_2_data_operations_evidence_task.md"
CHECKLIST_MD = OUTPUT_DIR / "phase_2_data_operations_evidence_checklist.md"
ENV_EXAMPLE = OUTPUT_DIR / "phase_2_data_operations_evidence.env.example"
README_PATH = OUTPUT_DIR / "README.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/PHASE_2_DATA_OPERATIONS_EVIDENCE_TASK_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PHASE_2_DATA_OPERATIONS_EVIDENCE_TASK_RECOMMENDATION_GATE.md"


PHASE_ID = "phase_2_data_and_operations_resilience"
PHASE_2_BLOCKERS = [
    "production_monitoring",
    "external_alert_delivery",
    "on_call_rotation",
    "restore_tested",
    "production_restore_policy",
]


def _evidence_items() -> list[dict[str, Any]]:
    groups = [
        (
            "production_monitoring",
            "production_operations_evidence",
            PRODUCTION_MONITORING_KEYS,
            "Human-approved production monitoring plan, metrics, dashboard, log retention, and dry-run evidence.",
        ),
        (
            "external_alert_delivery",
            "production_operations_evidence",
            EXTERNAL_ALERT_DELIVERY_KEYS,
            "Human-approved alert routing, delivery-test, failure-handling, escalation, and acknowledgement evidence.",
        ),
        (
            "on_call_rotation",
            "production_operations_evidence",
            ON_CALL_KEYS,
            "Human-approved on-call rotation, escalation schedule, and incident commander evidence.",
        ),
        (
            "restore_tested",
            "production_data_operations_evidence",
            RESTORE_TEST_KEYS,
            "Human-approved production-like restore test plan, isolated restore, integrity checks, RTO/RPO, tenant scope, and report review evidence.",
        ),
        (
            "production_restore_policy",
            "production_data_operations_evidence",
            RESTORE_POLICY_KEYS,
            "Human-approved restore policy, backup retention, tenant restore boundary, secret exclusion, notification boundary, and incident handoff evidence.",
        ),
    ]
    items: list[dict[str, Any]] = []
    for blocker_id, evidence_file_type, keys, description in groups:
        for key in keys:
            items.append(
                {
                    "blocker_id": blocker_id,
                    "evidence_file_type": evidence_file_type,
                    "evidence_key": key,
                    "required_value": True,
                    "description": description,
                    "provided": False,
                }
            )
    return items


def build_task() -> dict[str, Any]:
    dependency_plan = build_dependency_plan()
    phase = next(
        item for item in dependency_plan["phases"] if item["phase_id"] == PHASE_ID
    )
    blockers = [
        item
        for item in dependency_plan["blockers"]
        if item["blocker_id"] in PHASE_2_BLOCKERS
    ]
    blocker_by_id = {item["blocker_id"]: item for item in blockers}
    ordered_blockers = [blocker_by_id[blocker_id] for blocker_id in PHASE_2_BLOCKERS]
    evidence_items = _evidence_items()
    return {
        "task_type": "saee_phase_2_data_operations_evidence_task",
        "task_version": "v0.1",
        "task_scope": "human_reviewed_phase_2_data_operations_evidence_collection_plan",
        "generated_by": "scripts/saee_phase2_data_operations_evidence_task.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_dependency_plan": "phase_b_product/commercial_readiness/commercial_blocker_dependency_plan/dependency_plan.local.json",
        "source_phase_id": PHASE_ID,
        "phase_title": phase["title"],
        "target_blocker_ids": PHASE_2_BLOCKERS,
        "target_blocker_count": len(PHASE_2_BLOCKERS),
        "evidence_item_count": len(evidence_items),
        "production_launch_status": dependency_plan["production_launch_status"],
        "task_status": "ready_for_human_review_not_execution",
        "default_decision": "hold",
        "ready_for_human_review": True,
        "human_approval_required": True,
        "human_execution_authorized": False,
        "evidence_collection_authorized": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        "blockers_closed_by_task": 0,
        "phase_2_blockers_ready_to_close": False,
        "operations_blockers_ready_to_close": False,
        "data_operations_blockers_ready_to_close": False,
        "blockers": ordered_blockers,
        "required_evidence_items": evidence_items,
        "validation_commands_after_human_evidence": [
            "SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH=/path/to/production_operations_evidence.json python3 scripts/saee_production_operations_evidence_readiness.py",
            "SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH=/path/to/production_data_operations_evidence.json python3 scripts/saee_production_data_operations_evidence_readiness.py",
            "SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH=/path/to/production_operations_evidence.json SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH=/path/to/production_data_operations_evidence.json python3 scripts/saee_commercial_go_no_go.py",
            "python3 scripts/mainline_guard.py",
        ],
        "forbidden_actions": [
            "do_not_deploy_monitoring_from_codex",
            "do_not_contact_monitoring_vendor_from_codex",
            "do_not_contact_alert_provider_from_codex",
            "do_not_send_external_alerts_from_codex",
            "do_not_activate_on_call_from_codex",
            "do_not_run_restore_tests_from_codex",
            "do_not_modify_production_data_paths",
            "do_not_restore_to_live_paths",
            "do_not_restore_credentials",
            "do_not_process_customer_data",
            "do_not_contact_customers",
            "do_not_close_blockers_from_this_task_packet",
            "do_not_mark_production_ready",
            "do_not_launch_product",
            "do_not_expose_private_core",
        ],
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "landing_page_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "customer_contacted": False,
        "customer_validated": False,
        "production_ready": False,
        "public_sdk_released": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "monitoring_vendor_contacted_by_codex": False,
        "alert_provider_contacted_by_codex": False,
        "external_alert_sent_by_codex": False,
        "on_call_rotation_activated": False,
        "restore_test_executed": False,
        "production_data_path_modified": False,
        "restore_to_live_path_enabled": False,
        "live_restore_performed": False,
        "credentials_restored": False,
        "customer_data_processed": False,
        "next_action": "Human reviewer must decide whether to authorize a separate Phase 2 data/operations evidence collection task; this packet itself authorizes no execution.",
    }


def render_task_markdown(task: dict[str, Any]) -> str:
    blocker_rows = [
        "| {blocker_id} | {category} | {depends} | {lane} | no |".format(
            blocker_id=item["blocker_id"],
            category=item["category"],
            depends=", ".join(item["depends_on_blockers"]) if item["depends_on_blockers"] else "none",
            lane=item["owner_review_lane"],
        )
        for item in task["blockers"]
    ]
    evidence_rows = [
        "| {blocker_id} | {evidence_file_type} | {evidence_key} | false |".format(
            **item
        )
        for item in task["required_evidence_items"]
    ]
    return "\n".join(
        [
            "# SAEE Phase 2 Data and Operations Evidence Task v0.1",
            "",
            "Status: ready for human review, not authorized for execution.",
            "",
            "This packet converts the second commercial dependency-plan phase into",
            "a concrete evidence collection checklist for production monitoring,",
            "external alert delivery, on-call rotation, restore testing, and",
            "production restore policy. It does not deploy monitoring, contact",
            "vendors, send alerts, activate on-call, run restore tests, modify",
            "production data paths, process customer data, close blockers, launch",
            "product, or claim production readiness.",
            "",
            "## Summary",
            "",
            f"- task_scope: {task['task_scope']}",
            f"- source_phase_id: {task['source_phase_id']}",
            f"- production_launch_status: {task['production_launch_status']}",
            f"- target_blocker_count: {task['target_blocker_count']}",
            f"- evidence_item_count: {task['evidence_item_count']}",
            f"- blockers_closed_by_task: {task['blockers_closed_by_task']}",
            "- human_execution_authorized: false",
            "- evidence_collection_authorized: false",
            "- production_ready: false",
            "- customer_validated: false",
            "- product_launched: false",
            "- private_core_exposed: false",
            "",
            "## Target Blockers",
            "",
            "| Blocker | Category | Depends on | Owner lane | Closure allowed here |",
            "| --- | --- | --- | --- | --- |",
            *blocker_rows,
            "",
            "## Required Evidence Keys",
            "",
            "| Blocker | Evidence file type | Evidence key | Provided by this packet |",
            "| --- | --- | --- | --- |",
            *evidence_rows,
            "",
            "## Validation Commands After Human Evidence",
            "",
            "```bash",
            *task["validation_commands_after_human_evidence"],
            "```",
            "",
            "## Boundary",
            "",
            "- No blocker is closed by this task packet.",
            "- No execution is authorized by this task packet.",
            "- No monitoring deployment, alert delivery, on-call activation, or restore test is performed.",
            "- No production-ready claim is made.",
            "- No customer validation claim is made.",
            "- No product launch is authorized.",
            "- No customer contact is authorized.",
            "- No backend runtime, kernel, API schema, or private core is modified.",
            "",
        ]
    )


def render_checklist(task: dict[str, Any]) -> str:
    sections = [
        "# SAEE Phase 2 Data and Operations Evidence Checklist",
        "",
        "Use this checklist only after a human explicitly authorizes Phase 2",
        "evidence collection. Codex must not deploy monitoring, contact vendors,",
        "send alerts, activate on-call, run restore tests, modify production data",
        "paths, or process customer data.",
        "",
    ]
    by_blocker: dict[str, list[dict[str, Any]]] = {}
    for item in task["required_evidence_items"]:
        by_blocker.setdefault(item["blocker_id"], []).append(item)
    for blocker_id in PHASE_2_BLOCKERS:
        sections.extend([f"## {blocker_id}", ""])
        for item in by_blocker.get(blocker_id, []):
            sections.append(f"- [ ] `{item['evidence_key']}`")
        sections.append("")
    sections.extend(
        [
            "## Required Review Before Blocker Closure",
            "",
            "- [ ] Human approval confirms evidence is real and current.",
            "- [ ] Evidence JSON is parseable by the readiness checker.",
            "- [ ] No forbidden boundary flag is set to true.",
            "- [ ] Commercial go/no-go is rerun with explicit evidence paths.",
            "- [ ] Separate human launch approval remains required.",
            "",
        ]
    )
    return "\n".join(sections)


def render_env_example() -> str:
    return "\n".join(
        [
            "# SAEE Phase 2 evidence paths.",
            "# Fill these with human-approved local evidence JSON paths only.",
            "# Do not put secrets in these files.",
            "export SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH=/absolute/path/to/production_operations_evidence.json",
            "export SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH=/absolute/path/to/production_data_operations_evidence.json",
            "",
        ]
    )


def render_readme() -> str:
    return """# SAEE Phase 2 Data and Operations Evidence Task

Status: ready for human review, not authorized for execution.

This directory contains a local Phase 2 commercial-readiness task packet for
production monitoring, external alert delivery, on-call rotation, restore
testing, and production restore policy evidence.

It does not deploy monitoring, contact vendors, send external alerts, activate
on-call, run restore tests, modify production data paths, process customer
data, close blockers, launch product, claim customer validation, claim
production readiness, or expose private core.

Primary files:

```text
phase_2_data_operations_evidence_task.local.json
phase_2_data_operations_evidence_task.md
phase_2_data_operations_evidence_checklist.md
phase_2_data_operations_evidence.env.example
```

Generate them with:

```bash
python3 scripts/saee_phase2_data_operations_evidence_task.py
```

Boundary:

```yaml
task_scope: human_reviewed_phase_2_data_operations_evidence_collection_plan
production_launch_status: hold
target_blocker_count: 5
blockers_closed_by_task: 0
human_execution_authorized: false
evidence_collection_authorized: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
external_calls_made: false
```
"""


def render_doc() -> str:
    return """# SAEE Phase 2 Data and Operations Evidence Task v0.1

phase_2_data_operations_evidence_task_v0_1: true
task_scope: human_reviewed_phase_2_data_operations_evidence_collection_plan
source_phase_id: phase_2_data_and_operations_resilience
production_launch_status: hold
target_blocker_count: 5
blockers_closed_by_task: 0
human_execution_authorized: false
evidence_collection_authorized: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
external_calls_made: false

## Purpose

This packet prepares the second formal commercial-readiness evidence task for
SAEE. It targets production monitoring, external alert delivery, on-call
rotation, restore testing, and production restore policy evidence.

It is a task packet only. It does not authorize execution, close blockers, or
claim production readiness.

## Target Blockers

- production_monitoring
- external_alert_delivery
- on_call_rotation
- restore_tested
- production_restore_policy

## Boundary

- No monitoring vendor is contacted by Codex.
- No alert provider is contacted by Codex.
- No external alert is sent by Codex.
- No on-call rotation is activated.
- No restore test is executed by Codex.
- No production data path is modified.
- No customer data is processed.
- No blocker is closed by this packet.
- No product launch, customer validation, or production readiness claim is made.
"""


def render_gate() -> str:
    return """# SAEE Phase 2 Data and Operations Evidence Task Recommendation Gate

answer: conditional
recommend_for_human_commercial_review: true
recommend_for_execution_authorization: false
recommend_for_production_monitoring_claim: false
recommend_for_external_alert_delivery_claim: false
recommend_for_on_call_rotation_claim: false
recommend_for_restore_tested_claim: false
recommend_for_production_restore_policy_claim: false
recommend_for_production_readiness_claim: false
recommend_for_product_launch: false

## Reason

This task packet is useful because Phase 2 blockers must be reviewed before
SAEE can make credible production operations, alerting, on-call, and restore
claims. The packet is not itself execution approval and does not close any
blocker.

## Boundary

```yaml
task_scope: human_reviewed_phase_2_data_operations_evidence_collection_plan
production_launch_status: hold
target_blocker_count: 5
blockers_closed_by_task: 0
human_execution_authorized: false
evidence_collection_authorized: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
external_calls_made: false
```

## Next Action

Human reviewers may explicitly authorize a separate evidence collection task.
Until then, all Phase 2 blockers remain open.
"""


def write_outputs(task: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TASK_JSON.write_text(json.dumps(task, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    TASK_MD.write_text(render_task_markdown(task), encoding="utf-8")
    CHECKLIST_MD.write_text(render_checklist(task), encoding="utf-8")
    ENV_EXAMPLE.write_text(render_env_example(), encoding="utf-8")
    README_PATH.write_text(render_readme(), encoding="utf-8")
    DOC_PATH.write_text(render_doc(), encoding="utf-8")
    GATE_PATH.write_text(render_gate(), encoding="utf-8")


def main() -> None:
    task = build_task()
    write_outputs(task)
    print(
        "SAEE_PHASE2_DATA_OPERATIONS_EVIDENCE_TASK: PASS "
        f"target_blockers={task['target_blocker_count']} "
        f"evidence_items={task['evidence_item_count']} "
        f"blockers_closed_by_task={task['blockers_closed_by_task']} "
        "production_ready=false customer_validated=false"
    )


if __name__ == "__main__":
    main()
