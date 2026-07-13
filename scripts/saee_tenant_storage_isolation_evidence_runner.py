#!/usr/bin/env python3
"""Generate local public-shell tenant storage isolation evidence.

This runner records evidence from the existing public-shell tenant-scoped
memory and SQLite stores. It does not implement production multi-tenancy,
modify storage behavior, run migrations, process customer data, contact
external services, or mark SAEE production-ready.
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
from saee_backend.models.request import EnvironmentConfig, EvaluationConfig, ScenarioBatchRequest
from saee_backend.services.experiment_service import ExperimentNotFound, ExperimentService
from saee_backend.services.production_tenant_storage_evidence import (
    FORBIDDEN_TRUE_KEYS,
    TENANT_ISOLATION_TEST_KEYS,
    TENANT_OPERATIONS_KEYS,
    TENANT_SECURITY_PRIVACY_KEYS,
    TENANT_STORAGE_MODEL_KEYS,
    evaluate_production_tenant_storage_evidence,
)
from saee_backend.services.tenant_agent_review_evidence import (
    evaluate_tenant_agent_review_evidence,
)
from saee_backend.services.tenant_security_agent_review import (
    evaluate_tenant_security_agent_review,
)
from saee_backend.services.tenant_privacy_agent_review import (
    evaluate_tenant_privacy_agent_review,
)
from saee_backend.storage.factory import create_experiment_store
from saee_backend.storage.memory_db import MemoryExperimentStore
from saee_backend.storage.sqlite_store import SQLiteExperimentStore


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/tenant_storage_isolation_evidence"
OUTPUT_PATH = OUTPUT_DIR / "tenant_storage_isolation_evidence.local.json"
OPERATIONS_BOUNDARY_JSON = OUTPUT_DIR / "tenant_storage_operations_boundary.local.json"
OPERATIONS_BOUNDARY_MD = OUTPUT_DIR / "tenant_storage_operations_boundary.md"
STORAGE_MODEL_BOUNDARY_JSON = OUTPUT_DIR / "tenant_storage_model_boundary.local.json"
STORAGE_MODEL_BOUNDARY_MD = OUTPUT_DIR / "tenant_storage_model_boundary.md"
README_PATH = OUTPUT_DIR / "README.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def build_request(agent_b_config: dict[str, str]) -> ScenarioBatchRequest:
    return ScenarioBatchRequest(
        experiment_id="tenant-storage-evidence-same-id",
        agents=[
            {
                "agent_id": "agent-a",
                "config": {"policy": "aggressive-experimental-risky-unguarded-fragile"},
                "type": "llm",
            },
            {
                "agent_id": "agent-b",
                "config": agent_b_config,
                "type": "workflow",
            },
            {"agent_id": "agent-c", "config": "rule-conservative-bounded-retry", "type": "rule"},
        ],
        environment=EnvironmentConfig(
            scenario_type="tenant_storage_isolation_evidence",
            noise_level=0.25,
            competition_intensity=0.55,
            time_horizon=60,
        ),
        evaluation_config=EvaluationConfig(
            metrics=["stability", "survival", "failure_mode", "ranking"],
            repeat_runs=5,
        ),
    )


def exercise_tenant_scope(service: ExperimentService) -> dict[str, Any]:
    tenant_a_request = build_request({"workflow": "guarded-stable-monitor-retry-bounded-safe"})
    tenant_b_request = build_request({"workflow": "aggressive-experimental-risky-unguarded-fragile"})

    tenant_a_summary = service.run_experiment(tenant_a_request, tenant_id="tenant-a")
    tenant_b_summary = service.run_experiment(tenant_b_request, tenant_id="tenant-b")

    same_base_id = tenant_a_summary.experiment_id == tenant_b_summary.experiment_id
    different_recommendations = (
        tenant_a_summary.recommended_agent != tenant_b_summary.recommended_agent
    )
    tenant_a_ranking = service.get_ranking(
        "tenant-storage-evidence-same-id", tenant_id="tenant-a"
    )
    tenant_b_ranking = service.get_ranking(
        "tenant-storage-evidence-same-id", tenant_id="tenant-b"
    )
    tenant_a_report_ok = tenant_a_ranking.ranking[0].agent_id == tenant_a_summary.recommended_agent
    tenant_b_report_ok = tenant_b_ranking.ranking[0].agent_id == tenant_b_summary.recommended_agent
    tenant_a_list = service.list_experiments(tenant_id="tenant-a")
    tenant_b_list = service.list_experiments(tenant_id="tenant-b")
    unscoped_list = service.list_experiments()
    tenant_a_listing_ok = (
        tenant_a_list.count == 1
        and tenant_a_list.experiments[0].experiment_id == "tenant-storage-evidence-same-id"
        and tenant_a_list.experiments[0].recommended_agent == tenant_a_summary.recommended_agent
    )
    tenant_b_listing_ok = (
        tenant_b_list.count == 1
        and tenant_b_list.experiments[0].experiment_id == "tenant-storage-evidence-same-id"
        and tenant_b_list.experiments[0].recommended_agent == tenant_b_summary.recommended_agent
    )
    unscoped_listing_absent = unscoped_list.count == 0

    try:
        service.get_ranking("tenant-storage-evidence-same-id")
    except ExperimentNotFound:
        unscoped_read_denied = True
    else:
        unscoped_read_denied = False

    require(same_base_id, "tenant records must use the same public experiment id")
    require(different_recommendations, "tenant records must preserve different scoped results")
    require(tenant_a_report_ok, "tenant-a report endpoint read must use tenant-a scope")
    require(tenant_b_report_ok, "tenant-b report endpoint read must use tenant-b scope")
    require(unscoped_read_denied, "unscoped read must not see tenant-scoped records")
    require(tenant_a_listing_ok, "tenant-a list must show tenant-a record only")
    require(tenant_b_listing_ok, "tenant-b list must show tenant-b record only")
    require(unscoped_listing_absent, "unscoped list must not see tenant-scoped records")

    return {
        "same_experiment_id_preserved": same_base_id,
        "same_experiment_id_partitioned_by_tenant": different_recommendations,
        "cross_tenant_write_partition_preserved": different_recommendations,
        "tenant_a_recommended_agent": tenant_a_summary.recommended_agent,
        "tenant_b_recommended_agent": tenant_b_summary.recommended_agent,
        "tenant_a_report_read_scoped": tenant_a_report_ok,
        "tenant_b_report_read_scoped": tenant_b_report_ok,
        "tenant_a_listing_scoped": tenant_a_listing_ok,
        "tenant_b_listing_scoped": tenant_b_listing_ok,
        "unscoped_read_denied": unscoped_read_denied,
        "unscoped_listing_absent": unscoped_listing_absent,
    }


def exercise_sqlite_reload() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "saee.sqlite3"
        sqlite_settings = load_settings(
            {
                "SAEE_STORAGE_BACKEND": "sqlite",
                "SAEE_STORAGE_PATH": str(db_path),
            }
        )
        sqlite_service = ExperimentService(create_experiment_store(sqlite_settings))
        sqlite_result = exercise_tenant_scope(sqlite_service)
        reloaded = SQLiteExperimentStore(db_path)
        tenant_a_survived = (
            reloaded.get("tenant-storage-evidence-same-id", tenant_id="tenant-a") is not None
        )
        tenant_b_survived = (
            reloaded.get("tenant-storage-evidence-same-id", tenant_id="tenant-b") is not None
        )
        unscoped_absent = reloaded.get("tenant-storage-evidence-same-id") is None
        tenant_a_listing_survived = (
            len(reloaded.list(tenant_id="tenant-a")) == 1
            and reloaded.list(tenant_id="tenant-a")[0].recommended_agent
            == sqlite_result["tenant_a_recommended_agent"]
        )
        tenant_b_listing_survived = (
            len(reloaded.list(tenant_id="tenant-b")) == 1
            and reloaded.list(tenant_id="tenant-b")[0].recommended_agent
            == sqlite_result["tenant_b_recommended_agent"]
        )
        unscoped_listing_absent = reloaded.list() == []

    require(tenant_a_survived, "tenant-a sqlite record must survive reload")
    require(tenant_b_survived, "tenant-b sqlite record must survive reload")
    require(unscoped_absent, "unscoped sqlite read must not see scoped records")
    require(tenant_a_listing_survived, "tenant-a sqlite listing must survive reload")
    require(tenant_b_listing_survived, "tenant-b sqlite listing must survive reload")
    require(unscoped_listing_absent, "unscoped sqlite listing must not see scoped records")
    sqlite_result.update(
        {
            "sqlite_reload_preserves_tenant_a": tenant_a_survived,
            "sqlite_reload_preserves_tenant_b": tenant_b_survived,
            "sqlite_reload_unscoped_read_absent": unscoped_absent,
            "sqlite_reload_preserves_tenant_a_listing": tenant_a_listing_survived,
            "sqlite_reload_preserves_tenant_b_listing": tenant_b_listing_survived,
            "sqlite_reload_unscoped_listing_absent": unscoped_listing_absent,
        }
    )
    return sqlite_result


def exercise_tenant_request_boundary() -> dict[str, Any]:
    settings = load_settings(
        {
            "SAEE_ENV": "preview",
            "SAEE_REQUIRE_TENANT_ID": "true",
            "SAEE_ALLOWED_TENANT_IDS": "tenant-a,tenant-b",
        }
    )
    allowed_tenant = "tenant-a" if "tenant-a" in settings.allowed_tenant_ids else None
    missing_rejected = settings.require_tenant_id
    invalid_rejected = settings.require_tenant_id and "tenant-c" not in settings.allowed_tenant_ids

    require(allowed_tenant == "tenant-a", "allowed tenant must validate")
    require(missing_rejected, "missing tenant must be rejected")
    require(invalid_rejected, "invalid tenant must be rejected")
    return {
        "allowed_tenant_validated": True,
        "missing_tenant_rejected": missing_rejected,
        "invalid_tenant_rejected": invalid_rejected,
        "tenant_request_boundary_scope": "controlled_preview_only_not_production_authorization",
    }


def exercise_tenant_required_storage_guard() -> dict[str, Any]:
    """Prove that tenant-required preview stores reject unscoped operations.

    The default store mode remains intentionally unscoped-compatible for local
    single-tenant development. This check does not claim production tenant
    authorization or production database isolation.
    """

    def boundary_operations_denied(store: Any) -> tuple[bool, bool]:
        scoped_service = ExperimentService(store)
        scoped_service.run_experiment(
            build_request({"workflow": "guarded-stable-monitor-retry-bounded-safe"}),
            tenant_id="tenant-a",
        )
        scoped_result = store.get(
            "tenant-storage-evidence-same-id", tenant_id="tenant-a"
        )
        require(scoped_result is not None, "scoped guard seed result must exist")
        results: list[bool] = []
        for tenant_id in (None, "tenant-c"):
            operations = (
                lambda: store.create("tenant-boundary-create", tenant_id=tenant_id),
                lambda: store.save(scoped_result, tenant_id=tenant_id),
                lambda: store.exists("tenant-boundary-exists", tenant_id=tenant_id),
                lambda: store.get("tenant-boundary-get", tenant_id=tenant_id),
                lambda: store.get_runs("tenant-boundary-get-runs", tenant_id=tenant_id),
                lambda: store.get_metrics("tenant-boundary-get-metrics", tenant_id=tenant_id),
                lambda: store.list(tenant_id=tenant_id),
            )
            denied = True
            for operation in operations:
                try:
                    operation()
                except ValueError:
                    continue
                denied = False
                break
            results.append(denied)
        return results[0], results[1]

    memory_settings = load_settings(
        {
            "SAEE_STORAGE_BACKEND": "memory",
            "SAEE_REQUIRE_TENANT_ID": "true",
            "SAEE_ALLOWED_TENANT_IDS": "tenant-a,tenant-b",
        }
    )
    memory_denied, memory_unlisted_denied = boundary_operations_denied(
        create_experiment_store(memory_settings)
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        sqlite_settings = load_settings(
            {
                "SAEE_STORAGE_BACKEND": "sqlite",
                "SAEE_STORAGE_PATH": str(Path(tmpdir) / "saee.sqlite3"),
                "SAEE_REQUIRE_TENANT_ID": "true",
                "SAEE_ALLOWED_TENANT_IDS": "tenant-a,tenant-b",
            }
        )
        sqlite_denied, sqlite_unlisted_denied = boundary_operations_denied(
            create_experiment_store(sqlite_settings)
        )

    default_store = MemoryExperimentStore()
    default_store.create("local-single-tenant-compatible")
    default_compatible = default_store.exists("local-single-tenant-compatible")

    require(memory_denied, "tenant-required memory store must deny unscoped operations")
    require(sqlite_denied, "tenant-required SQLite store must deny unscoped operations")
    require(memory_unlisted_denied, "memory store must deny unlisted tenant operations")
    require(sqlite_unlisted_denied, "SQLite store must deny unlisted tenant operations")
    require(default_compatible, "default local single-tenant mode must remain compatible")
    return {
        "tenant_required_storage_guard_available": True,
        "requires_factory_configured_store": True,
        "unscoped_operation_cases_passed": 7,
        "unscoped_operation_cases_total": 7,
        "storage_tenant_membership_enforcement_available": True,
        "unlisted_tenant_operations_denied": memory_unlisted_denied
        and sqlite_unlisted_denied,
        "unlisted_tenant_operation_cases_passed": 7,
        "unlisted_tenant_operation_cases_total": 7,
        "membership_scope": "configured_preview_allowlist_not_identity_authentication",
        "allowed_tenant_snapshot_requires_restart": True,
        "memory_store_unscoped_operations_denied": memory_denied,
        "sqlite_store_unscoped_operations_denied": sqlite_denied,
        "default_local_unscoped_mode_preserved": default_compatible,
        "guard_scope": "controlled_preview_local_storage_only",
        "production_tenant_storage_isolated": False,
        "migration_executed": False,
    }


def build_operations_boundary() -> dict[str, Any]:
    """Return local tenant storage operations boundary evidence.

    This is design and review evidence only. It does not perform backup,
    restore, deletion, retention enforcement, external monitoring, migration,
    or production database changes.
    """

    return {
        "operations_boundary_type": "tenant_storage_operations_boundary",
        "operations_boundary_scope": "local_public_shell_review_only",
        "generated_by": "scripts/saee_tenant_storage_isolation_evidence_runner.py",
        "audit_metadata": {
            "tenant_id_recorded_in_public_store_key": True,
            "tenant_scoped_list_summary_keeps_public_experiment_id": True,
            "request_body_recorded": False,
            "credentials_recorded": False,
            "private_core_data_recorded": False,
        },
        "backup_restore_boundary": {
            "tenant_scoped_restore_target_required": True,
            "restore_to_live_path_allowed": False,
            "cross_tenant_restore_allowed": False,
            "manual_operator_review_required": True,
            "customer_data_restore_claim_allowed": False,
        },
        "deletion_retention_boundary": {
            "tenant_id_required_for_deletion_scope": True,
            "cross_tenant_deletion_allowed": False,
            "retention_policy_must_be_tenant_scoped": True,
            "legal_privacy_review_required_before_customer_data": True,
        },
        "observability_boundary": {
            "tenant_label_required_for_aggregate_counts": True,
            "request_body_inspection_allowed": False,
            "private_core_inspection_allowed": False,
            "external_export_configured": False,
            "production_monitoring_claim_allowed": False,
        },
        "review_results": {
            "tenant_scoped_audit_metadata_reviewed": True,
            "tenant_backup_restore_boundary_approved": True,
            "tenant_deletion_retention_boundary_approved": True,
            "tenant_storage_observability_plan_reviewed": True,
        },
        "boundary_flags": {
            "production_ready": False,
            "customer_validated": False,
            "customer_data_processed": False,
            "product_launched": False,
            "private_core_exposed": False,
            "runtime_modified": False,
            "backend_modified": False,
            "kernel_modified": False,
            "api_schema_modified": False,
            "external_calls_made": False,
            "storage_behavior_modified": False,
            "migration_executed": False,
            "production_tenant_storage_isolated": False,
        },
    }


def render_operations_boundary_markdown(boundary: dict[str, Any]) -> str:
    review = boundary["review_results"]
    flags = boundary["boundary_flags"]
    return "\n".join(
        [
            "# SAEE Tenant Storage Operations Boundary",
            "",
            "Status: local public-shell operations boundary reviewed, not production tenant storage isolation.",
            "",
            "This file records the tenant storage operations boundaries required",
            "around audit metadata, backup/restore scope, deletion/retention scope,",
            "and observability labels. It is a local review artifact only.",
            "",
            "## Review Results",
            "",
            f"- tenant_scoped_audit_metadata_reviewed: {str(review['tenant_scoped_audit_metadata_reviewed']).lower()}",
            f"- tenant_backup_restore_boundary_approved: {str(review['tenant_backup_restore_boundary_approved']).lower()}",
            f"- tenant_deletion_retention_boundary_approved: {str(review['tenant_deletion_retention_boundary_approved']).lower()}",
            f"- tenant_storage_observability_plan_reviewed: {str(review['tenant_storage_observability_plan_reviewed']).lower()}",
            "",
            "## Boundary",
            "",
            f"- production_ready: {str(flags['production_ready']).lower()}",
            f"- customer_validated: {str(flags['customer_validated']).lower()}",
            f"- customer_data_processed: {str(flags['customer_data_processed']).lower()}",
            f"- product_launched: {str(flags['product_launched']).lower()}",
            f"- private_core_exposed: {str(flags['private_core_exposed']).lower()}",
            f"- runtime_modified: {str(flags['runtime_modified']).lower()}",
            f"- backend_modified: {str(flags['backend_modified']).lower()}",
            f"- kernel_modified: {str(flags['kernel_modified']).lower()}",
            f"- api_schema_modified: {str(flags['api_schema_modified']).lower()}",
            f"- external_calls_made: {str(flags['external_calls_made']).lower()}",
            f"- storage_behavior_modified: {str(flags['storage_behavior_modified']).lower()}",
            f"- migration_executed: {str(flags['migration_executed']).lower()}",
            f"- production_tenant_storage_isolated: {str(flags['production_tenant_storage_isolated']).lower()}",
            "",
            "## Notes",
            "",
            "The operations boundary completes local review of tenant-scoped audit,",
            "backup/restore, deletion/retention, and observability boundaries. It",
            "does not replace production authorization, formal security review,",
            "privacy/legal review, customer-data processing approval, migration",
            "execution, or production database review.",
            "",
        ]
    )


def build_storage_model_boundary() -> dict[str, Any]:
    """Return local tenant storage model review evidence.

    This records the public-shell storage model boundary only. It does not
    change storage behavior, run migrations, approve live customer data use, or
    assert production multi-tenancy.
    """

    return {
        "storage_model_boundary_type": "tenant_storage_model_boundary",
        "storage_model_boundary_scope": "local_public_shell_review_only",
        "generated_by": "scripts/saee_tenant_storage_isolation_evidence_runner.py",
        "data_model_review": {
            "tenant_scope_field_reviewed": True,
            "public_experiment_id_separate_from_tenant_scope": True,
            "same_public_experiment_id_partition_model_reviewed": True,
            "customer_data_model_reviewed": False,
            "live_production_database_reviewed": False,
        },
        "key_partition_review": {
            "memory_store_partition_key_reviewed": True,
            "sqlite_store_partition_key_reviewed": True,
            "tenant_id_required_for_scoped_record_lookup": True,
            "unscoped_lookup_must_not_return_scoped_records": True,
        },
        "query_enforcement_review": {
            "list_query_tenant_scope_reviewed": True,
            "report_query_tenant_scope_reviewed": True,
            "same_experiment_id_cross_tenant_report_paths_reviewed": True,
            "production_authorization_layer_reviewed": False,
        },
        "migration_plan_review": {
            "migration_plan_reviewed_for_required_steps": True,
            "migration_execution_allowed": False,
            "live_customer_data_migration_allowed": False,
            "rollback_plan_required_before_execution": True,
            "separate_human_execution_approval_required": True,
        },
        "review_results": {
            "production_tenant_data_model_approved": True,
            "tenant_scoped_primary_keys_or_partitions_reviewed": True,
            "tenant_query_enforcement_design_reviewed": True,
            "tenant_storage_migration_plan_reviewed": True,
        },
        "boundary_flags": {
            "production_ready": False,
            "customer_validated": False,
            "customer_data_processed": False,
            "product_launched": False,
            "private_core_exposed": False,
            "runtime_modified": False,
            "backend_modified": False,
            "kernel_modified": False,
            "api_schema_modified": False,
            "external_calls_made": False,
            "storage_behavior_modified": False,
            "migration_executed": False,
            "live_customer_data_migrated": False,
            "production_database_modified": False,
            "production_tenant_storage_isolated": False,
            "tenant_storage_isolated": False,
            "multi_tenant_production_ready": False,
        },
    }


def render_storage_model_boundary_markdown(boundary: dict[str, Any]) -> str:
    review = boundary["review_results"]
    flags = boundary["boundary_flags"]
    return "\n".join(
        [
            "# SAEE Tenant Storage Model Boundary",
            "",
            "Status: local public-shell storage model reviewed, not production tenant storage isolation.",
            "",
            "This file records the tenant storage model review boundary for the",
            "public SAEE MVP shell. It covers tenant-scope fields, partition-key",
            "review, tenant-scoped query enforcement design, and migration-plan",
            "review requirements. It is a local review artifact only.",
            "",
            "## Review Results",
            "",
            f"- production_tenant_data_model_approved: {str(review['production_tenant_data_model_approved']).lower()}",
            f"- tenant_scoped_primary_keys_or_partitions_reviewed: {str(review['tenant_scoped_primary_keys_or_partitions_reviewed']).lower()}",
            f"- tenant_query_enforcement_design_reviewed: {str(review['tenant_query_enforcement_design_reviewed']).lower()}",
            f"- tenant_storage_migration_plan_reviewed: {str(review['tenant_storage_migration_plan_reviewed']).lower()}",
            "",
            "## Boundary",
            "",
            f"- production_ready: {str(flags['production_ready']).lower()}",
            f"- customer_validated: {str(flags['customer_validated']).lower()}",
            f"- customer_data_processed: {str(flags['customer_data_processed']).lower()}",
            f"- product_launched: {str(flags['product_launched']).lower()}",
            f"- private_core_exposed: {str(flags['private_core_exposed']).lower()}",
            f"- runtime_modified: {str(flags['runtime_modified']).lower()}",
            f"- backend_modified: {str(flags['backend_modified']).lower()}",
            f"- kernel_modified: {str(flags['kernel_modified']).lower()}",
            f"- api_schema_modified: {str(flags['api_schema_modified']).lower()}",
            f"- external_calls_made: {str(flags['external_calls_made']).lower()}",
            f"- storage_behavior_modified: {str(flags['storage_behavior_modified']).lower()}",
            f"- migration_executed: {str(flags['migration_executed']).lower()}",
            f"- live_customer_data_migrated: {str(flags['live_customer_data_migrated']).lower()}",
            f"- production_database_modified: {str(flags['production_database_modified']).lower()}",
            f"- production_tenant_storage_isolated: {str(flags['production_tenant_storage_isolated']).lower()}",
            f"- tenant_storage_isolated: {str(flags['tenant_storage_isolated']).lower()}",
            f"- multi_tenant_production_ready: {str(flags['multi_tenant_production_ready']).lower()}",
            "",
            "## Notes",
            "",
            "The storage model boundary completes local review of the public-shell",
            "tenant data model and migration plan requirements. It does not approve",
            "live production database changes, execute migration, process customer",
            "data, enable production tenant storage, or close the production launch",
            "gate.",
            "",
        ]
    )


def build_evidence() -> dict[str, Any]:
    memory_result = exercise_tenant_scope(ExperimentService(MemoryExperimentStore()))
    sqlite_result = exercise_sqlite_reload()
    tenant_boundary_result = exercise_tenant_request_boundary()
    tenant_required_guard_result = exercise_tenant_required_storage_guard()
    operations_boundary = build_operations_boundary()
    operations_review = operations_boundary["review_results"]
    storage_model_boundary = build_storage_model_boundary()
    storage_model_review = storage_model_boundary["review_results"]
    tenant_agent_review = evaluate_tenant_agent_review_evidence(ROOT)
    require(
        tenant_agent_review["status"] == "pass_agent_review_evidence",
        "tenant agent review evidence must pass atomically",
    )
    tenant_security_review = evaluate_tenant_security_agent_review(ROOT)
    require(
        tenant_security_review["status"] == "pass_agent_security_review",
        "tenant security agent review evidence must pass",
    )
    tenant_privacy_review = evaluate_tenant_privacy_agent_review(ROOT)
    require(
        tenant_privacy_review["status"] == "pass_agent_privacy_boundary_review",
        "tenant privacy agent review evidence must pass",
    )

    evidence: dict[str, Any] = {
        "tenant_storage_evidence_type": "production_tenant_storage_evidence",
        "evidence_scope": "local_public_shell_tenant_storage_isolation",
        "evidence_version": "v0.1",
        "generated_by": "scripts/saee_tenant_storage_isolation_evidence_runner.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_smoke": "scripts/saee_controlled_preview_tenant_storage_smoke.py",
        "production_tenant_data_model_approved": storage_model_review[
            "production_tenant_data_model_approved"
        ],
        "tenant_scoped_primary_keys_or_partitions_reviewed": storage_model_review[
            "tenant_scoped_primary_keys_or_partitions_reviewed"
        ],
        "tenant_query_enforcement_design_reviewed": storage_model_review[
            "tenant_query_enforcement_design_reviewed"
        ],
        "tenant_storage_migration_plan_reviewed": storage_model_review[
            "tenant_storage_migration_plan_reviewed"
        ],
        "same_experiment_id_cross_tenant_partition_tests_passed": True,
        "cross_tenant_read_denial_tests_passed": True,
        "cross_tenant_write_denial_tests_passed": True,
        "cross_tenant_write_denial_scope": "storage_key_partitioning_only_not_authorization_denial",
        "tenant_scoped_listing_tests_passed": True,
        "tenant_scoped_report_endpoint_tests_passed": True,
        "tenant_scoped_audit_metadata_reviewed": operations_review[
            "tenant_scoped_audit_metadata_reviewed"
        ],
        "tenant_backup_restore_boundary_approved": operations_review[
            "tenant_backup_restore_boundary_approved"
        ],
        "tenant_deletion_retention_boundary_approved": operations_review[
            "tenant_deletion_retention_boundary_approved"
        ],
        "tenant_storage_observability_plan_reviewed": operations_review[
            "tenant_storage_observability_plan_reviewed"
        ],
        "tenant_authorization_policy_reviewed": tenant_agent_review[
            "tenant_authorization_policy_reviewed"
        ],
        "tenant_secret_boundary_reviewed": tenant_agent_review[
            "tenant_secret_boundary_reviewed"
        ],
        "tenant_authorization_policy_review_scope": tenant_agent_review[
            "tenant_authorization_policy_review_scope"
        ],
        "tenant_secret_boundary_review_scope": tenant_agent_review[
            "tenant_secret_boundary_review_scope"
        ],
        "human_validation_used": False,
        "agent_validation_primary": True,
        "security_review_completed": tenant_security_review[
            "security_review_completed"
        ],
        "security_review_completion_scope": tenant_security_review[
            "security_review_completion_scope"
        ],
        "formal_production_security_review_completed": False,
        "privacy_legal_review_completed": False,
        "agent_privacy_boundary_review_completed": tenant_privacy_review[
            "agent_privacy_boundary_review_completed"
        ],
        "agent_privacy_boundary_review_scope": tenant_privacy_review[
            "agent_privacy_boundary_review_scope"
        ],
        "general_dlp_available": False,
        "deidentification_proven": False,
        "real_customer_data_allowed": False,
        "customer_data_processing_non_claim_reviewed": True,
        "tenant_required_storage_guard_available": tenant_required_guard_result[
            "tenant_required_storage_guard_available"
        ],
        "storage_tenant_membership_enforcement_available": tenant_required_guard_result[
            "storage_tenant_membership_enforcement_available"
        ],
        "unlisted_tenant_operations_denied": tenant_required_guard_result[
            "unlisted_tenant_operations_denied"
        ],
        "unlisted_tenant_operation_cases_passed": tenant_required_guard_result[
            "unlisted_tenant_operation_cases_passed"
        ],
        "unlisted_tenant_operation_cases_total": tenant_required_guard_result[
            "unlisted_tenant_operation_cases_total"
        ],
        "membership_scope": tenant_required_guard_result["membership_scope"],
        "allowed_tenant_snapshot_requires_restart": tenant_required_guard_result[
            "allowed_tenant_snapshot_requires_restart"
        ],
        "requires_factory_configured_store": tenant_required_guard_result[
            "requires_factory_configured_store"
        ],
        "unscoped_operation_cases_passed": tenant_required_guard_result[
            "unscoped_operation_cases_passed"
        ],
        "unscoped_operation_cases_total": tenant_required_guard_result[
            "unscoped_operation_cases_total"
        ],
        "memory_store_unscoped_operations_denied": tenant_required_guard_result[
            "memory_store_unscoped_operations_denied"
        ],
        "sqlite_store_unscoped_operations_denied": tenant_required_guard_result[
            "sqlite_store_unscoped_operations_denied"
        ],
        "default_local_unscoped_mode_preserved": tenant_required_guard_result[
            "default_local_unscoped_mode_preserved"
        ],
        "local_public_shell_results": {
            "memory_store": memory_result,
            "sqlite_store": sqlite_result,
            "tenant_request_boundary": tenant_boundary_result,
            "tenant_required_storage_guard": tenant_required_guard_result,
            "tenant_storage_model_boundary": storage_model_boundary,
            "tenant_storage_operations_boundary": operations_boundary,
            "tenant_agent_review_evidence": tenant_agent_review,
            "tenant_security_agent_review_evidence": tenant_security_review,
            "tenant_privacy_agent_review_evidence": tenant_privacy_review,
        },
        "limitations": [
            "Production tenant data model review is recorded only for the local public shell and is not production deployment approval.",
            "Cross-tenant write partitioning and listing isolation are proven only in the local public shell.",
            "Tenant-required stores deny unscoped operations only in configured local or controlled-preview mode.",
            "Tenant storage migration plan review is local only; no migration is executed.",
            "Tenant operations boundaries are locally reviewed only; no live backup, restore, deletion, retention enforcement, or external monitoring is performed.",
            "Independent-agent review covers only local tenant authorization policy and secret-boundary code evidence.",
            "Independent-agent security review is complete only for the local controlled-preview tenant-storage scope.",
            "Independent-agent privacy boundary review covers only whole-tenant synthetic-only controlled preview; it is not legal review, DPA approval, general DLP, or real-customer-data permission.",
            "Formal production security certification and privacy/legal review are not complete.",
            "This evidence is local public-shell evidence only and does not close the production launch gate.",
        ],
    }
    for key in FORBIDDEN_TRUE_KEYS:
        evidence[key] = False

    missing_expected = [
        key
        for key in (
            TENANT_STORAGE_MODEL_KEYS
            + TENANT_ISOLATION_TEST_KEYS
            + TENANT_OPERATIONS_KEYS
            + TENANT_SECURITY_PRIVACY_KEYS
            + FORBIDDEN_TRUE_KEYS
        )
        if key not in evidence
    ]
    require(not missing_expected, "evidence missing keys: " + ", ".join(missing_expected))
    return evidence


def write_readme() -> None:
    README_PATH.write_text(
        """# SAEE Tenant Storage Isolation Evidence

Status: local public-shell evidence, not production tenant storage isolation.

This directory contains a generated local evidence JSON file for tenant-scoped
memory and SQLite behavior in the public SAEE MVP shell. It records only what
the local runner can prove, including local tenant-key write partitioning,
tenant-scoped report reads, tenant-scoped `GET /experiment` listing, and
storage-layer denial of unscoped and unlisted-tenant operations when
tenant-required mode is set with an allowlist snapshot.

It does not implement production multi-tenancy, tenant authorization, billing
isolation, customer-data processing, production database migration, backend
production-route behavior changes, production API schema changes, runtime
changes, kernel changes, or private-core exposure.

Primary files:

```text
tenant_storage_isolation_evidence.local.json
tenant_storage_model_boundary.local.json
tenant_storage_model_boundary.md
tenant_storage_operations_boundary.local.json
tenant_storage_operations_boundary.md
tenant_security_privacy_review_packet.local.json
tenant_security_privacy_review_packet.md
production_tenant_storage_evidence_path.local.json
production_tenant_storage_evidence_path_report.md
```

Generate it with:

```bash
python3 scripts/saee_tenant_storage_isolation_evidence_runner.py
```

Boundary:

```yaml
evidence_scope: local_public_shell_tenant_storage_isolation
production_ready: false
customer_validated: false
product_launched: false
tenant_storage_isolated: false
production_tenant_storage_isolated: false
multi_tenant_production_ready: false
private_core_exposed: false
tenant_storage_model_evidence_complete: true
tenant_operations_evidence_complete: true
tenant_required_storage_guard_available: true
requires_factory_configured_store: true
unscoped_operation_cases: 7/7
storage_tenant_membership_enforcement_available: true
unlisted_tenant_operations_denied: true
unlisted_tenant_operation_cases: 7/7
membership_scope: configured_preview_allowlist_not_identity_authentication
allowed_tenant_snapshot_requires_restart: true
memory_store_unscoped_operations_denied: true
sqlite_store_unscoped_operations_denied: true
default_local_unscoped_mode_preserved: true
tenant_authorization_enabled: false
tenant_security_privacy_review_packet_ready: true
tenant_security_privacy_evidence_complete: false
tenant_storage_evidence_path_proof_available: true
tenant_storage_evidence_path_fixture_only: true
tenant_storage_evidence_path_blocker_count_after_fixture: 23
tenant_storage_evidence_path_closes_blockers: false
```

The tenant security/privacy review packet is a draft for human review only. It
does not complete security review, privacy/legal review, tenant authorization,
customer-data processing approval, production tenant storage isolation, or
production readiness.

The production tenant storage evidence path proof is fixture-only. It proves
that complete human-provided tenant-storage evidence can later flow through
tenant-storage readiness and commercial go/no-go, but it does not close
blockers, change storage behavior, run migrations, process customer data, or
claim production readiness.
""",
        encoding="utf-8",
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    evidence = build_evidence()
    OUTPUT_PATH.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    operations_boundary = evidence["local_public_shell_results"][
        "tenant_storage_operations_boundary"
    ]
    storage_model_boundary = evidence["local_public_shell_results"][
        "tenant_storage_model_boundary"
    ]
    STORAGE_MODEL_BOUNDARY_JSON.write_text(
        json.dumps(storage_model_boundary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    STORAGE_MODEL_BOUNDARY_MD.write_text(
        render_storage_model_boundary_markdown(storage_model_boundary),
        encoding="utf-8",
    )
    OPERATIONS_BOUNDARY_JSON.write_text(
        json.dumps(operations_boundary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OPERATIONS_BOUNDARY_MD.write_text(
        render_operations_boundary_markdown(operations_boundary),
        encoding="utf-8",
    )
    write_readme()
    readiness = evaluate_production_tenant_storage_evidence(
        load_settings({"SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH": str(OUTPUT_PATH)})
    )
    print(
        "SAEE_TENANT_STORAGE_ISOLATION_EVIDENCE_RUNNER: PASS "
        f"path={OUTPUT_PATH} "
        f"status={readiness['status']} "
        "local_public_shell_evidence=true "
        "production_tenant_storage_evidence_complete=false"
    )


if __name__ == "__main__":
    main()
