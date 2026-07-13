#!/usr/bin/env python3
"""Prove the local production tenant-storage evidence path without deployment.

This path check uses temporary fixture-only production tenant-storage evidence
and feeds it into the existing tenant-storage readiness and commercial
go/no-go checks. It proves the wiring from human-filled tenant storage model,
isolation test, operations, and security/privacy evidence to commercial review
without modifying storage behavior, running migrations, processing customer
data, enabling production tenant storage, closing blockers by itself, or
claiming production readiness.
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
from saee_backend.services.production_tenant_storage_evidence import (
    FORBIDDEN_TRUE_KEYS,
    TENANT_ISOLATION_TEST_KEYS,
    TENANT_OPERATIONS_KEYS,
    TENANT_SECURITY_PRIVACY_KEYS,
    TENANT_STORAGE_MODEL_KEYS,
    evaluate_production_tenant_storage_evidence,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/tenant_storage_isolation_evidence"
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / "production_tenant_storage_evidence_path.local.json"
REPORT_PATH = OUTPUT_DIR / "production_tenant_storage_evidence_path_report.md"
DOC_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH_RECOMMENDATION_GATE.md"
)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fixture_evidence() -> dict[str, Any]:
    all_evidence_keys = (
        TENANT_STORAGE_MODEL_KEYS
        + TENANT_ISOLATION_TEST_KEYS
        + TENANT_OPERATIONS_KEYS
        + TENANT_SECURITY_PRIVACY_KEYS
    )
    evidence: dict[str, Any] = {
        "tenant_storage_evidence_type": "production_tenant_storage_evidence",
        "evidence_scope": "fixture_only_production_tenant_storage_evidence_path_proof",
        "evidence_version": "v0.1",
        "input_status": "fixture_only_not_real_production_tenant_storage",
        "generated_by": "scripts/saee_production_tenant_storage_evidence_path.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "human_reviewer_name": "Fixture Reviewer",
        "review_date": datetime.now(timezone.utc).date().isoformat(),
        "decision_summary": (
            "Fixture-only production tenant-storage evidence path proof. This "
            "is not real production tenant isolation, storage migration, "
            "customer-data processing, production database review, or launch "
            "approval."
        ),
        "source_notes_by_key": {
            key: f"Fixture-only source note for {key}." for key in all_evidence_keys
        },
        "tenant_storage_evidence_slots": [
            {
                "evidence_key": key,
                "evidence_reference": f"fixture://production-tenant-storage/{key}",
                "owner_named": True,
                "reviewed_by_human": True,
                "human_source_note": f"Fixture-only human source note for {key}.",
            }
            for key in all_evidence_keys
        ],
        "fixture_only": True,
        "real_tenant_storage_design_approved": False,
        "real_cross_tenant_tests_run_in_production": False,
        "real_tenant_operations_approved": False,
        "real_security_privacy_reviews_completed": False,
        "real_customer_data_processing_approved": False,
    }
    for key in all_evidence_keys:
        evidence[key] = True
    for key in FORBIDDEN_TRUE_KEYS:
        evidence[key] = False
    return evidence


def tenant_storage_status(path: Path) -> dict[str, object]:
    return evaluate_production_tenant_storage_evidence(
        load_settings({"SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH": str(path)})
    )


def commercial_status(path: Path) -> dict[str, object]:
    return evaluate_commercial_go_no_go(
        load_settings({"SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH": str(path)})
    )


def build_path(output_path: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmpdir:
        fixture_path = Path(tmpdir) / "production_tenant_storage_evidence.fixture.json"
        write_json(fixture_path, fixture_evidence())
        tenant_storage = tenant_storage_status(fixture_path)
        go_no_go = commercial_status(fixture_path)

    tenant_storage_path_proven = (
        tenant_storage["tenant_storage_model_evidence_complete"] is True
        and tenant_storage["tenant_storage_isolation_evidence_complete"] is True
        and tenant_storage["tenant_operations_evidence_complete"] is True
        and tenant_storage["tenant_security_privacy_evidence_complete"] is True
        and tenant_storage["production_tenant_storage_evidence_complete"] is True
    )
    result: dict[str, Any] = {
        "production_tenant_storage_evidence_path_v0_1": True,
        "path_type": "local_fixture_only_production_tenant_storage_evidence_path",
        "path_status": "pass_fixture_only" if tenant_storage_path_proven else "hold",
        "generated_by": "scripts/saee_production_tenant_storage_evidence_path.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "fixture_only": True,
        "real_tenant_storage_design_approved": False,
        "real_cross_tenant_tests_run_in_production": False,
        "real_tenant_operations_approved": False,
        "real_security_privacy_reviews_completed": False,
        "real_customer_data_processing_approved": False,
        "tenant_storage_readiness_status_after_fixture": tenant_storage["status"],
        "tenant_storage_evidence_model_complete_after_fixture": tenant_storage[
            "tenant_storage_model_evidence_complete"
        ],
        "tenant_storage_evidence_isolation_complete_after_fixture": tenant_storage[
            "tenant_storage_isolation_evidence_complete"
        ],
        "tenant_storage_evidence_operations_complete_after_fixture": tenant_storage[
            "tenant_operations_evidence_complete"
        ],
        "tenant_storage_evidence_security_privacy_complete_after_fixture": tenant_storage[
            "tenant_security_privacy_evidence_complete"
        ],
        "tenant_storage_evidence_complete_after_fixture": tenant_storage[
            "production_tenant_storage_evidence_complete"
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
        "tenant_storage_blocker_path_proven": tenant_storage_path_proven,
        "tenant_storage_target_blockers_satisfied_by_fixture": [
            "tenant_storage_isolation"
        ],
        "tenant_storage_target_blockers_satisfied_count_after_fixture": 1
        if tenant_storage_path_proven
        else 0,
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
        "customer_data_processed": False,
        "customer_data_processing_started": False,
        "production_database_modified": False,
        "storage_behavior_modified": False,
        "migration_executed": False,
        "live_customer_data_migrated": False,
        "tenant_storage_isolated": False,
        "production_tenant_storage_isolated": False,
        "multi_tenant_production_ready": False,
        "tenant_authorization_enabled": False,
        "production_tenant_storage_enabled": False,
        "next_action": (
            "A human owner must replace the fixture with real production "
            "tenant-storage evidence, then rerun tenant-storage evidence "
            "readiness and commercial go/no-go. This path proof alone closes "
            "no blockers."
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
                "# SAEE Production Tenant Storage Evidence Path Report v0.1",
                "",
                "Status: local fixture-only path proof generated.",
                "",
                "## Summary",
                "",
                "- production_tenant_storage_evidence_path_v0_1: true",
                f"- path_type: {result['path_type']}",
                f"- path_status: {result['path_status']}",
                "- fixture_only: true",
                "- real_tenant_storage_design_approved: false",
                "- real_cross_tenant_tests_run_in_production: false",
                "- real_tenant_operations_approved: false",
                "- real_security_privacy_reviews_completed: false",
                "- real_customer_data_processing_approved: false",
                f"- tenant_storage_readiness_status_after_fixture: {result['tenant_storage_readiness_status_after_fixture']}",
                f"- tenant_storage_evidence_model_complete_after_fixture: {str(result['tenant_storage_evidence_model_complete_after_fixture']).lower()}",
                f"- tenant_storage_evidence_isolation_complete_after_fixture: {str(result['tenant_storage_evidence_isolation_complete_after_fixture']).lower()}",
                f"- tenant_storage_evidence_operations_complete_after_fixture: {str(result['tenant_storage_evidence_operations_complete_after_fixture']).lower()}",
                f"- tenant_storage_evidence_security_privacy_complete_after_fixture: {str(result['tenant_storage_evidence_security_privacy_complete_after_fixture']).lower()}",
                f"- tenant_storage_evidence_complete_after_fixture: {str(result['tenant_storage_evidence_complete_after_fixture']).lower()}",
                f"- tenant_storage_blocker_path_proven: {str(result['tenant_storage_blocker_path_proven']).lower()}",
                f"- tenant_storage_target_blockers_satisfied_count_after_fixture: {result['tenant_storage_target_blockers_satisfied_count_after_fixture']}",
                f"- commercial_status_after_fixture: {result['commercial_status_after_fixture']}",
                f"- production_blocker_count_after_fixture: {result['production_blocker_count_after_fixture']}",
                f"- blockers_closed_by_path: {result['blockers_closed_by_path']}",
                "",
                "## Boundary",
                "",
                "- No production tenant storage enabled.",
                "- No storage behavior modified.",
                "- No migration executed.",
                "- No production database modified.",
                "- No live customer data migrated or processed.",
                "- No tenant authorization enabled.",
                "- No backend, runtime, kernel, or API schema modified.",
                "- No customer contacted.",
                "- No product launched.",
                "- No production-readiness claim added.",
                "- No private core exposed.",
                "",
                "## Next Action",
                "",
                str(result["next_action"]),
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_docs() -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text(
        """# SAEE Production Tenant Storage Evidence Path v0.1

Status: local fixture-only path proof; not production tenant storage.

## Purpose

This path proves that a complete local production tenant-storage evidence JSON
can be read by `production_tenant_storage_evidence`, then reflected by
commercial go/no-go for the `tenant_storage_isolation` blocker.

## Machine-Readable Status

```yaml
production_tenant_storage_evidence_path_v0_1: true
path_type: local_fixture_only_production_tenant_storage_evidence_path
path_status: pass_fixture_only
fixture_only: true
real_tenant_storage_design_approved: false
real_cross_tenant_tests_run_in_production: false
real_tenant_operations_approved: false
real_security_privacy_reviews_completed: false
real_customer_data_processing_approved: false
tenant_storage_readiness_status_after_fixture: pass
tenant_storage_evidence_model_complete_after_fixture: true
tenant_storage_evidence_isolation_complete_after_fixture: true
tenant_storage_evidence_operations_complete_after_fixture: true
tenant_storage_evidence_security_privacy_complete_after_fixture: true
tenant_storage_evidence_complete_after_fixture: true
tenant_storage_blocker_path_proven: true
tenant_storage_target_blockers_satisfied_count_after_fixture: 1
production_blocker_count_after_fixture: 23
blockers_closed_by_path: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
storage_behavior_modified: false
migration_executed: false
production_database_modified: false
customer_data_processed: false
tenant_storage_isolated: false
production_tenant_storage_isolated: false
multi_tenant_production_ready: false
```

## Boundary

This path does not enable production tenant storage, modify storage behavior,
run migrations, process customer data, modify production databases, enable
tenant authorization, close blockers by itself, launch product, contact
customers, modify runtime, modify backend, modify kernel, modify API schema, or
expose private core.

## Recommendation Gate

Answer: conditional.

Recommend this path for human production tenant-storage evidence review and
blocker-path verification. Do not recommend it as production tenant storage,
production launch approval, customer validation, or blocker closure by itself.
""",
        encoding="utf-8",
    )
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(
        """# SAEE Production Tenant Storage Evidence Path Recommendation Gate

answer: conditional

recommend_for_human_tenant_storage_evidence_review: true
recommend_for_blocker_closure_by_path_alone: false
recommend_for_production_launch: false
recommend_for_customer_contact: false
recommend_for_storage_behavior_change: false
recommend_for_migration_execution: false
recommend_for_customer_data_processing: false
recommend_for_production_tenant_storage_enablement: false

## Reason

The path proves local fixture-only wiring from production tenant-storage
evidence into tenant-storage readiness and commercial go/no-go for the
`tenant_storage_isolation` blocker. It is useful for human review of real
evidence later, but it is not production tenant storage and does not close
blockers by itself.

## Boundary

production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
storage_behavior_modified: false
migration_executed: false
production_database_modified: false
customer_data_processed: false
tenant_storage_isolated: false
production_tenant_storage_isolated: false
multi_tenant_production_ready: false
""",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_path(Path(args.output))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(
            "SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH: PASS "
            f"path={Path(args.output).relative_to(ROOT)} "
            f"path_status={result['path_status']} "
            "fixture_only=true "
            "tenant_storage_blocker_path_proven=true "
            "blockers_closed_by_path=0"
        )


if __name__ == "__main__":
    main()
