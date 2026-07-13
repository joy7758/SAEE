#!/usr/bin/env python3
"""Generate the SAEE Phase 1 identity and tenant evidence task packet.

This packet turns the first commercial dependency-plan phase into a
human-reviewable evidence collection task. It does not implement production
authentication, contact an identity provider, fetch JWKS, validate production
tokens, run migrations, process customer data, close blockers, launch product,
or claim production readiness.
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

from saee_backend.services.production_auth_evidence import (
    AUTH_IDP_KEYS,
    OAUTH_OIDC_KEYS,
    RBAC_KEYS,
)
from saee_backend.services.production_tenant_storage_evidence import (
    TENANT_ISOLATION_TEST_KEYS,
    TENANT_OPERATIONS_KEYS,
    TENANT_SECURITY_PRIVACY_KEYS,
    TENANT_STORAGE_MODEL_KEYS,
)
from scripts.saee_commercial_blocker_dependency_plan import build_dependency_plan


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_task"
TASK_JSON = OUTPUT_DIR / "phase_1_identity_tenant_evidence_task.local.json"
TASK_MD = OUTPUT_DIR / "phase_1_identity_tenant_evidence_task.md"
CHECKLIST_MD = OUTPUT_DIR / "phase_1_identity_tenant_evidence_checklist.md"
ENV_EXAMPLE = OUTPUT_DIR / "phase_1_identity_tenant_evidence.env.example"
README_PATH = OUTPUT_DIR / "README.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/PHASE_1_IDENTITY_TENANT_EVIDENCE_TASK_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PHASE_1_IDENTITY_TENANT_EVIDENCE_TASK_RECOMMENDATION_GATE.md"


PHASE_ID = "phase_1_identity_and_tenant_boundary"
PHASE_1_BLOCKERS = [
    "production_identity_provider",
    "oauth_oidc",
    "rbac",
    "tenant_storage_isolation",
]


def _evidence_items() -> list[dict[str, Any]]:
    groups = [
        (
            "production_identity_provider",
            "production_auth_evidence",
            AUTH_IDP_KEYS,
            "Human-approved production identity-provider selection and ownership evidence.",
        ),
        (
            "oauth_oidc",
            "production_auth_evidence",
            OAUTH_OIDC_KEYS,
            "Human-approved OAuth/OIDC flow, token-validation, claims, expiry, and failure-handling evidence.",
        ),
        (
            "rbac",
            "production_auth_evidence",
            RBAC_KEYS,
            "Human-approved RBAC policy, role matrix, tenant role boundary, least-privilege, and admin recovery evidence.",
        ),
        (
            "tenant_storage_isolation",
            "production_tenant_storage_evidence",
            TENANT_STORAGE_MODEL_KEYS,
            "Human-approved tenant data-model and migration-plan evidence.",
        ),
        (
            "tenant_storage_isolation",
            "production_tenant_storage_evidence",
            TENANT_ISOLATION_TEST_KEYS,
            "Tenant isolation denial-test evidence.",
        ),
        (
            "tenant_storage_isolation",
            "production_tenant_storage_evidence",
            TENANT_OPERATIONS_KEYS,
            "Tenant audit, backup/restore, retention/deletion, and observability boundary evidence.",
        ),
        (
            "tenant_storage_isolation",
            "production_tenant_storage_evidence",
            TENANT_SECURITY_PRIVACY_KEYS,
            "Tenant authorization, secret boundary, security, privacy, and customer-data non-claim review evidence.",
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
        if item["blocker_id"] in PHASE_1_BLOCKERS
    ]
    evidence_items = _evidence_items()
    return {
        "task_type": "saee_phase_1_identity_tenant_evidence_task",
        "task_version": "v0.1",
        "task_scope": "human_reviewed_phase_1_evidence_collection_plan",
        "generated_by": "scripts/saee_phase1_identity_tenant_evidence_task.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_dependency_plan": "phase_b_product/commercial_readiness/commercial_blocker_dependency_plan/dependency_plan.local.json",
        "source_phase_id": PHASE_ID,
        "phase_title": phase["title"],
        "target_blocker_ids": PHASE_1_BLOCKERS,
        "target_blocker_count": len(PHASE_1_BLOCKERS),
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
        "phase_1_blockers_ready_to_close": False,
        "auth_blockers_ready_to_close": False,
        "tenant_storage_blocker_ready_to_close": False,
        "blockers": blockers,
        "required_evidence_items": evidence_items,
        "validation_commands_after_human_evidence": [
            "SAEE_PRODUCTION_AUTH_EVIDENCE_PATH=/path/to/production_auth_evidence.json python3 scripts/saee_production_auth_evidence_readiness.py",
            "SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH=/path/to/production_tenant_storage_evidence.json python3 scripts/saee_production_tenant_storage_evidence_readiness.py",
            "SAEE_PRODUCTION_AUTH_EVIDENCE_PATH=/path/to/production_auth_evidence.json SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH=/path/to/production_tenant_storage_evidence.json python3 scripts/saee_commercial_go_no_go.py",
            "python3 scripts/mainline_guard.py",
        ],
        "forbidden_actions": [
            "do_not_contact_identity_provider_from_codex",
            "do_not_fetch_jwks_from_codex",
            "do_not_validate_production_tokens_from_codex",
            "do_not_run_storage_migrations_from_codex",
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
        "identity_provider_contacted_by_codex": False,
        "jwks_fetched_by_codex": False,
        "production_tokens_validated_by_codex": False,
        "storage_migration_executed": False,
        "customer_data_processed": False,
        "next_action": "Human reviewer must decide whether to authorize a separate Phase 1 evidence collection task; this packet itself authorizes no execution.",
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
            "# SAEE Phase 1 Identity and Tenant Evidence Task v0.1",
            "",
            "Status: ready for human review, not authorized for execution.",
            "",
            "This packet converts the first commercial dependency-plan phase into",
            "a concrete evidence collection checklist for production identity,",
            "OAuth/OIDC, RBAC, and tenant storage isolation. It does not implement",
            "production auth, contact an identity provider, fetch JWKS, validate",
            "production tokens, run migrations, process customer data, close blockers,",
            "launch product, or claim production readiness.",
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
        "# SAEE Phase 1 Identity and Tenant Evidence Checklist",
        "",
        "Use this checklist only after a human explicitly authorizes Phase 1",
        "evidence collection. Codex must not contact an identity provider, fetch",
        "JWKS, validate production tokens, run migrations, or process customer data.",
        "",
    ]
    by_blocker: dict[str, list[dict[str, Any]]] = {}
    for item in task["required_evidence_items"]:
        by_blocker.setdefault(item["blocker_id"], []).append(item)
    for blocker_id in PHASE_1_BLOCKERS:
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
            "# SAEE Phase 1 evidence paths.",
            "# Fill these with human-approved local evidence JSON paths only.",
            "# Do not put secrets in these files.",
            "export SAEE_PRODUCTION_AUTH_EVIDENCE_PATH=/absolute/path/to/production_auth_evidence.json",
            "export SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH=/absolute/path/to/production_tenant_storage_evidence.json",
            "",
        ]
    )


def render_readme() -> str:
    return """# SAEE Phase 1 Identity and Tenant Evidence Task

Status: ready for human review, not authorized for execution.

This directory contains a local Phase 1 commercial-readiness task packet for
production identity-provider, OAuth/OIDC, RBAC, and tenant storage isolation
evidence.

It does not implement production auth, contact an identity provider, fetch
JWKS, validate production tokens, run migrations, process customer data, close
blockers, launch product, claim customer validation, claim production
readiness, or expose private core.

Primary files:

```text
phase_1_identity_tenant_evidence_task.local.json
phase_1_identity_tenant_evidence_task.md
phase_1_identity_tenant_evidence_checklist.md
phase_1_identity_tenant_evidence.env.example
```

Generate them with:

```bash
python3 scripts/saee_phase1_identity_tenant_evidence_task.py
```

Boundary:

```yaml
task_scope: human_reviewed_phase_1_evidence_collection_plan
production_launch_status: hold
target_blocker_count: 4
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
    return """# SAEE Phase 1 Identity and Tenant Evidence Task v0.1

phase_1_identity_tenant_evidence_task_v0_1: true
task_scope: human_reviewed_phase_1_evidence_collection_plan
source_phase_id: phase_1_identity_and_tenant_boundary
production_launch_status: hold
target_blocker_count: 4
blockers_closed_by_task: 0
human_execution_authorized: false
evidence_collection_authorized: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
external_calls_made: false

## Purpose

This packet prepares the first formal commercial-readiness evidence task for
SAEE. It targets production identity-provider selection, OAuth/OIDC evidence,
RBAC evidence, and tenant storage isolation evidence.

It is a task packet only. It does not authorize execution, close blockers, or
claim production readiness.

## Target Blockers

- production_identity_provider
- oauth_oidc
- rbac
- tenant_storage_isolation

## Boundary

- No identity provider is contacted by Codex.
- No JWKS is fetched by Codex.
- No production tokens are validated by Codex.
- No storage migration is executed.
- No customer data is processed.
- No blocker is closed by this packet.
- No product launch, customer validation, or production readiness claim is made.
"""


def render_gate() -> str:
    return """# SAEE Phase 1 Identity and Tenant Evidence Task Recommendation Gate

answer: conditional
recommend_for_human_commercial_review: true
recommend_for_execution_authorization: false
recommend_for_production_auth_claim: false
recommend_for_tenant_storage_isolation_claim: false
recommend_for_production_readiness_claim: false
recommend_for_product_launch: false

## Reason

This task packet is useful because Phase 1 blockers must be handled before
later operations, legal, billing, and customer-validation work can be safely
interpreted. The packet is not itself execution approval and does not close
any blocker.

## Boundary

```yaml
task_scope: human_reviewed_phase_1_evidence_collection_plan
production_launch_status: hold
target_blocker_count: 4
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
Until then, all Phase 1 blockers remain open.
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
        "SAEE_PHASE1_IDENTITY_TENANT_EVIDENCE_TASK: PASS "
        f"target_blockers={task['target_blocker_count']} "
        f"evidence_items={task['evidence_item_count']} "
        f"blockers_closed_by_task={task['blockers_closed_by_task']} "
        "production_ready=false customer_validated=false"
    )


if __name__ == "__main__":
    main()
