#!/usr/bin/env python3
"""Smoke check for controlled-preview tenant-scoped storage."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.models.request import EnvironmentConfig, EvaluationConfig, ScenarioBatchRequest
from saee_backend.services.experiment_service import ExperimentNotFound, ExperimentService
from saee_backend.storage.factory import create_experiment_store
from saee_backend.storage.sqlite_store import SQLiteExperimentStore


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_CONTROLLED_PREVIEW_TENANT_STORAGE_SMOKE: FAIL: {message}")


def build_request(agent_b_config) -> ScenarioBatchRequest:
    return ScenarioBatchRequest(
        experiment_id="tenant-storage-same-id",
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
            scenario_type="controlled_preview_tenant_scope",
            noise_level=0.25,
            competition_intensity=0.55,
            time_horizon=60,
        ),
        evaluation_config=EvaluationConfig(
            metrics=["stability", "survival", "failure_mode", "ranking"],
            repeat_runs=5,
        ),
    )


def assert_invalid_tenant_ids_rejected(service: ExperimentService) -> None:
    invalid_tenant_ids = [
        "",
        " tenant-a",
        "tenant-a ",
        "tenant:a",
        "tenant/a",
        "../tenant-a",
        "a" * 65,
    ]
    for tenant_id in invalid_tenant_ids:
        try:
            service.list_experiments(tenant_id=tenant_id)
        except ValueError:
            pass
        else:
            raise SystemExit(
                "SAEE_CONTROLLED_PREVIEW_TENANT_STORAGE_SMOKE: FAIL: "
                f"invalid storage tenant ID was accepted: {tenant_id!r}"
            )
        try:
            service.run_experiment(
                build_request({"workflow": "guarded-stable-monitor-retry-bounded-safe"}),
                tenant_id=tenant_id,
            )
        except ValueError:
            pass
        else:
            raise SystemExit(
                "SAEE_CONTROLLED_PREVIEW_TENANT_STORAGE_SMOKE: FAIL: "
                f"invalid tenant write was accepted: {tenant_id!r}"
            )


def assert_tenant_scope(service: ExperimentService) -> None:
    tenant_a_request = build_request({"workflow": "guarded-stable-monitor-retry-bounded-safe"})
    tenant_b_request = build_request({"workflow": "aggressive-experimental-risky-unguarded-fragile"})

    tenant_a_summary = service.run_experiment(tenant_a_request, tenant_id="tenant-a")
    tenant_b_summary = service.run_experiment(tenant_b_request, tenant_id="tenant-b")

    require(tenant_a_summary.experiment_id == tenant_b_summary.experiment_id, "base IDs must match")
    require(
        tenant_a_summary.recommended_agent != tenant_b_summary.recommended_agent,
        "tenant-scoped records must preserve different results for same base ID",
    )
    require(
        service.get_ranking("tenant-storage-same-id", tenant_id="tenant-a").ranking[0].agent_id
        == tenant_a_summary.recommended_agent,
        "tenant-a ranking must read tenant-a record",
    )
    require(
        service.get_ranking("tenant-storage-same-id", tenant_id="tenant-b").ranking[0].agent_id
        == tenant_b_summary.recommended_agent,
        "tenant-b ranking must read tenant-b record",
    )
    tenant_a_list = service.list_experiments(tenant_id="tenant-a")
    tenant_b_list = service.list_experiments(tenant_id="tenant-b")
    try:
        unscoped_list = service.list_experiments()
    except ValueError:
        unscoped_list = None
    require(tenant_a_list.count == 1, "tenant-a list must include one scoped record")
    require(tenant_b_list.count == 1, "tenant-b list must include one scoped record")
    if unscoped_list is not None:
        require(unscoped_list.count == 0, "unscoped list must not see tenant-scoped records")
    require(
        tenant_a_list.experiments[0].recommended_agent == tenant_a_summary.recommended_agent,
        "tenant-a list must expose tenant-a summary only",
    )
    require(
        tenant_b_list.experiments[0].recommended_agent == tenant_b_summary.recommended_agent,
        "tenant-b list must expose tenant-b summary only",
    )
    try:
        service.get_ranking("tenant-storage-same-id")
    except (ExperimentNotFound, ValueError):
        pass
    else:
        raise SystemExit(
            "SAEE_CONTROLLED_PREVIEW_TENANT_STORAGE_SMOKE: FAIL: "
            "unscoped read must not see tenant-scoped records"
        )


def assert_storage_operations_denied(store, scoped_result, tenant_id: str | None) -> None:
    for operation in (
        lambda: store.create("boundary-create", tenant_id=tenant_id),
        lambda: store.save(scoped_result, tenant_id=tenant_id),
        lambda: store.exists("boundary-exists", tenant_id=tenant_id),
        lambda: store.get("boundary-get", tenant_id=tenant_id),
        lambda: store.get_runs("boundary-get-runs", tenant_id=tenant_id),
        lambda: store.get_metrics("boundary-get-metrics", tenant_id=tenant_id),
        lambda: store.list(tenant_id=tenant_id),
    ):
        try:
            operation()
        except ValueError:
            continue
        raise SystemExit(
            "SAEE_CONTROLLED_PREVIEW_TENANT_STORAGE_SMOKE: FAIL: "
            "tenant-required store accepted an unscoped or unlisted-tenant operation"
        )


def assert_factory_configuration_fail_closed(storage_backend: str, storage_path: str) -> None:
    base = {
        "SAEE_STORAGE_BACKEND": storage_backend,
        "SAEE_STORAGE_PATH": storage_path,
        "SAEE_REQUIRE_TENANT_ID": "true",
    }
    for allowed_tenants in ("", "tenant/a"):
        settings = load_settings({**base, "SAEE_ALLOWED_TENANT_IDS": allowed_tenants})
        try:
            create_experiment_store(settings)
        except ValueError:
            continue
        raise SystemExit(
            "SAEE_CONTROLLED_PREVIEW_TENANT_STORAGE_SMOKE: FAIL: "
            "strict storage accepted an empty or invalid tenant allowlist"
        )


def main() -> None:
    preview_settings = load_settings(
        {
            "SAEE_ENV": "preview",
            "SAEE_REQUIRE_TENANT_ID": "true",
            "SAEE_ALLOWED_TENANT_IDS": "tenant-a,tenant-b",
        }
    )
    readiness = preview_settings.readiness_payload()
    require(
        readiness["preview_storage_scoped_by_tenant"] is True,
        "preview storage scope flag must be true when tenant guard is configured",
    )
    require(readiness["tenant_storage_isolated"] is False, "must not claim production tenant storage")
    require(readiness["tenant_billing_isolated"] is False, "must not claim tenant billing isolation")
    require(
        readiness["multi_tenant_production_ready"] is False,
        "must not claim production multi-tenancy",
    )

    memory_store = create_experiment_store(preview_settings)
    memory_service = ExperimentService(memory_store)
    assert_invalid_tenant_ids_rejected(memory_service)
    assert_tenant_scope(memory_service)
    memory_scoped_result = memory_store.get("tenant-storage-same-id", tenant_id="tenant-a")
    require(memory_scoped_result is not None, "tenant-a memory result must exist")
    assert_storage_operations_denied(memory_store, memory_scoped_result, None)
    assert_storage_operations_denied(memory_store, memory_scoped_result, "tenant-c")
    assert_factory_configuration_fail_closed("memory", "ignored")

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "saee.sqlite3"
        sqlite_settings = load_settings(
            {
                "SAEE_STORAGE_BACKEND": "sqlite",
                "SAEE_STORAGE_PATH": str(db_path),
                "SAEE_REQUIRE_TENANT_ID": "true",
                "SAEE_ALLOWED_TENANT_IDS": "tenant-a,tenant-b",
            }
        )
        sqlite_store = create_experiment_store(sqlite_settings)
        sqlite_service = ExperimentService(sqlite_store)
        assert_invalid_tenant_ids_rejected(sqlite_service)
        assert_tenant_scope(sqlite_service)
        sqlite_scoped_result = sqlite_store.get(
            "tenant-storage-same-id", tenant_id="tenant-a"
        )
        require(sqlite_scoped_result is not None, "tenant-a SQLite result must exist")
        assert_storage_operations_denied(sqlite_store, sqlite_scoped_result, None)
        assert_storage_operations_denied(sqlite_store, sqlite_scoped_result, "tenant-c")
        assert_factory_configuration_fail_closed("sqlite", str(Path(tmpdir) / "invalid.sqlite3"))
        reloaded = SQLiteExperimentStore(
            db_path,
            require_tenant_id=True,
            allowed_tenant_ids=("tenant-a", "tenant-b"),
        )
        require(
            reloaded.get("tenant-storage-same-id", tenant_id="tenant-a") is not None,
            "tenant-a record must survive sqlite reload",
        )
        require(
            reloaded.get("tenant-storage-same-id", tenant_id="tenant-b") is not None,
            "tenant-b record must survive sqlite reload",
        )
        reloaded_scoped_result = reloaded.get(
            "tenant-storage-same-id", tenant_id="tenant-a"
        )
        require(reloaded_scoped_result is not None, "reloaded tenant-a result must exist")
        assert_storage_operations_denied(reloaded, reloaded_scoped_result, None)
        assert_storage_operations_denied(reloaded, reloaded_scoped_result, "tenant-c")
        require(
            reloaded.list(tenant_id="tenant-a")[0].recommended_agent
            == sqlite_service.get_ranking(
                "tenant-storage-same-id", tenant_id="tenant-a"
            ).ranking[0].agent_id,
            "tenant-a sqlite list must preserve tenant-a result",
        )
        try:
            reloaded.list()
        except ValueError:
            pass
        else:
            raise SystemExit(
                "SAEE_CONTROLLED_PREVIEW_TENANT_STORAGE_SMOKE: FAIL: "
                "strict sqlite unscoped list must be denied"
            )

    doc = (
        ROOT / "phase_b_product/commercial_readiness/CONTROLLED_PREVIEW_TENANT_STORAGE_V0_1.md"
    ).read_text(encoding="utf-8")
    gate = (
        ROOT / "docs/strategy/SAEE_CONTROLLED_PREVIEW_TENANT_STORAGE_RECOMMENDATION_GATE.md"
    ).read_text(encoding="utf-8")
    require("preview_storage_scoped_by_tenant: true" in doc, "doc missing preview storage scope")
    require(
        "storage_tenant_key_guard_available: true" in doc,
        "doc missing storage tenant key guard",
    )
    require(
        "invalid_storage_tenant_id_rejected: true" in doc,
        "doc missing invalid storage tenant ID rejection",
    )
    require("tenant_storage_isolated: false" in doc, "doc must keep production tenant storage false")
    require("multi_tenant_production_ready: false" in doc, "doc must keep production multi-tenant false")
    require("answer: conditional" in gate, "gate must remain conditional")

    print(
        "SAEE_CONTROLLED_PREVIEW_TENANT_STORAGE_SMOKE: PASS "
        "preview_storage_scoped_by_tenant=true "
        "same_experiment_id_partitioned=true "
        "invalid_storage_tenant_id_rejected=true "
        "tenant_scoped_listing=true "
        "sqlite_reload_preserves_scope=true "
        "tenant_required_store_unscoped_denied=true "
        "unlisted_tenant_operations_denied=true "
        "strict_allowlist_configuration_fail_closed=true "
        "tenant_storage_isolated=false "
        "multi_tenant_production_ready=false"
    )


if __name__ == "__main__":
    main()
