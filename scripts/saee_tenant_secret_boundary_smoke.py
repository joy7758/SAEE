#!/usr/bin/env python3
"""Adversarial smoke for the local controlled-preview tenant secret boundary."""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
from copy import deepcopy
from hashlib import sha256
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.api.audit import build_request_audit_event, write_request_audit_event
from saee_backend.config import load_settings
from saee_backend.core.runner import run_scenario_batch
from saee_backend.models.request import EnvironmentConfig, EvaluationConfig, ScenarioBatchRequest
from saee_backend.storage.memory_db import MemoryExperimentStore
from saee_backend.storage.serialization import serialize_experiment_result
from saee_backend.storage.sqlite_store import SQLiteExperimentStore
from saee_backend.storage.tenant_key import tenant_storage_key


CREDENTIAL_SENTINEL = "sk-syntheticSentinel123456"
BENIGN_CONFIG_SENTINEL = "synthetic-private-config-sentinel"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_TENANT_SECRET_BOUNDARY_SMOKE: FAIL: " + message)


def require_rejected_without_echo(
    callable_,
    *,
    label: str,
    sentinel: str = CREDENTIAL_SENTINEL,
) -> None:
    try:
        callable_()
    except (ValueError, TypeError) as exc:
        require(sentinel not in str(exc), label + " reflected sentinel")
        return
    raise SystemExit("SAEE_TENANT_SECRET_BOUNDARY_SMOKE: FAIL: " + label + " accepted")


def request_payload() -> dict:
    return {
        "experiment_id": "tenant-secret-boundary",
        "agents": [
            {
                "agent_id": "agent-a",
                "config": {"policy": BENIGN_CONFIG_SENTINEL},
                "type": "llm",
            },
            {
                "agent_id": "agent-b",
                "config": "guarded-stable-bounded",
                "type": "workflow",
            },
        ],
        "environment": {
            "scenario_type": "tenant_secret_boundary",
            "noise_level": 0.2,
            "competition_intensity": 0.4,
            "time_horizon": 20,
        },
        "evaluation_config": {
            "metrics": ["stability", "survival", "failure_mode", "ranking"],
            "repeat_runs": 3,
        },
    }


def audit_boundary() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "audit.jsonl"
        settings = load_settings(
            {
                "SAEE_REQUEST_AUDIT_ENABLED": "true",
                "SAEE_REQUEST_AUDIT_PATH": str(path),
            }
        )
        event = build_request_audit_event(
            request_id="req-secret-boundary",
            method="POST",
            path="/experiment/run",
            status_code=200,
            duration_ms=2.0,
            tenant_audit_metadata={
                "tenant_boundary_checked": True,
                "tenant_id_present": True,
                "tenant_id_hash_recorded": True,
                "tenant_id_raw_recorded": False,
                "tenant_id_hash": sha256("tenant-a".encode()).hexdigest(),
                "tenant_id_hash_algorithm": "sha256",
            },
        )
        require(write_request_audit_event(event, settings), "valid audit event not written")

        for field in ("note", "authorization", "x-saee-api-key", "x-saee-tenant-id"):
            malicious = dict(event)
            malicious[field] = CREDENTIAL_SENTINEL
            require_rejected_without_echo(
                lambda malicious=malicious: write_request_audit_event(malicious, settings),
                label="unknown audit field",
            )
        require_rejected_without_echo(
            lambda: build_request_audit_event(
                request_id="req-override",
                method="GET",
                path="/ready",
                status_code=200,
                duration_ms=1.0,
                tenant_audit_metadata={"body_recorded": True},
            ),
            label="protected audit field override",
        )
        require_rejected_without_echo(
            lambda: build_request_audit_event(
                request_id="req-forged-hash",
                method="GET",
                path="/ready",
                status_code=200,
                duration_ms=1.0,
                tenant_audit_metadata={
                    "tenant_boundary_checked": True,
                    "tenant_id_present": True,
                    "tenant_id_hash_recorded": True,
                    "tenant_id_raw_recorded": False,
                    "tenant_id_hash": CREDENTIAL_SENTINEL,
                    "tenant_id_hash_algorithm": "sha256",
                },
            ),
            label="forged tenant hash",
        )
        raw_tenant = "tenant-cross-field-sentinel"
        raw_path_event = dict(event)
        raw_path_event["path"] = "/" + raw_tenant
        require_rejected_without_echo(
            lambda: write_request_audit_event(raw_path_event, settings),
            label="raw tenant audit path",
            sentinel=raw_tenant,
        )
        require(CREDENTIAL_SENTINEL not in path.read_text(), "audit JSONL contains sentinel")


def request_boundary() -> ScenarioBatchRequest:
    valid = ScenarioBatchRequest.model_validate(request_payload())
    serialized_error_cases = []
    for mutate in (
        lambda payload: payload["agents"][0].update({"agent_id": CREDENTIAL_SENTINEL}),
        lambda payload: payload.update({"experiment_id": CREDENTIAL_SENTINEL}),
        lambda payload: payload["agents"][0].update(
            {"config": {"nested": {"api_key": CREDENTIAL_SENTINEL}}}
        ),
        lambda payload: payload["agents"][1].update({"agent_id": "agent-a"}),
    ):
        payload = request_payload()
        mutate(payload)
        try:
            ScenarioBatchRequest.model_validate(payload)
        except ValueError as exc:
            serialized_error_cases.append(str(exc))
        else:
            raise SystemExit("SAEE_TENANT_SECRET_BOUNDARY_SMOKE: FAIL: malicious request accepted")
    require(
        all(CREDENTIAL_SENTINEL not in error for error in serialized_error_cases),
        "request validation reflected credential sentinel",
    )

    bypassed = ScenarioBatchRequest.model_construct(
        experiment_id=valid.experiment_id,
        agents=deepcopy(valid.agents),
        environment=valid.environment,
        evaluation_config=valid.evaluation_config,
    )
    bypassed.agents[0].config = {"authorization": CREDENTIAL_SENTINEL}
    require_rejected_without_echo(
        lambda: run_scenario_batch(bypassed),
        label="runner revalidation bypass",
    )
    return valid


def persistence_boundary(request: ScenarioBatchRequest) -> None:
    result = run_scenario_batch(request)
    payload = serialize_experiment_result(result)
    serialized = json.dumps(payload, sort_keys=True)
    require(BENIGN_CONFIG_SENTINEL not in serialized, "request config entered result payload")

    malicious = deepcopy(result)
    first_agent = next(iter(malicious.agent_outputs))
    malicious.agent_outputs[first_agent]["secret"] = CREDENTIAL_SENTINEL

    memory = MemoryExperimentStore()
    require_rejected_without_echo(
        lambda: memory.save(malicious),
        label="malicious memory result",
    )
    memory.save(result)
    result.agent_outputs[first_agent]["aggregate_scores"][0] = 0.999999
    stored = memory.get(result.summary.experiment_id)
    require(stored is not None, "memory snapshot missing")
    require(
        stored.agent_outputs[first_agent]["aggregate_scores"][0] != 0.999999,
        "save-after mutation polluted memory store",
    )
    stored.agent_outputs[first_agent]["aggregate_scores"][0] = 0.888888
    stored_again = memory.get(result.summary.experiment_id)
    require(
        stored_again is not None
        and stored_again.agent_outputs[first_agent]["aggregate_scores"][0] != 0.888888,
        "read-after mutation polluted memory store",
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "strict.sqlite3"
        sqlite_store = SQLiteExperimentStore(
            db_path,
            require_tenant_id=True,
            allowed_tenant_ids=("tenant-a", "tenant-b"),
        )
        require_rejected_without_echo(
            lambda: sqlite_store.save(malicious, tenant_id="tenant-a"),
            label="malicious SQLite result",
        )
        require_rejected_without_echo(
            lambda: sqlite_store.create(CREDENTIAL_SENTINEL, tenant_id="tenant-a"),
            label="credential-shaped direct store create",
        )
        raw_tenant = "tenant-cross-field-sentinel"
        cross_agent_payload = request_payload()
        cross_agent_payload["agents"][0]["agent_id"] = raw_tenant
        cross_agent_result = run_scenario_batch(
            ScenarioBatchRequest.model_validate(cross_agent_payload)
        )
        cross_store = SQLiteExperimentStore(
            Path(tmpdir) / "cross.sqlite3",
            require_tenant_id=True,
            allowed_tenant_ids=(raw_tenant,),
        )
        require_rejected_without_echo(
            lambda: cross_store.save(cross_agent_result, tenant_id=raw_tenant),
            label="raw tenant as agent ID",
            sentinel=raw_tenant,
        )
        cross_experiment_payload = request_payload()
        cross_experiment_payload["experiment_id"] = raw_tenant
        cross_experiment_result = run_scenario_batch(
            ScenarioBatchRequest.model_validate(cross_experiment_payload)
        )
        require_rejected_without_echo(
            lambda: cross_store.save(cross_experiment_result, tenant_id=raw_tenant),
            label="raw tenant as experiment ID",
            sentinel=raw_tenant,
        )

        clean_result = run_scenario_batch(request)
        for label, mutate in (
            (
                "bytes in run scores",
                lambda item: item.runs[0].scores.__setitem__(
                    0, CREDENTIAL_SENTINEL.encode("utf-8")
                ),
            ),
            (
                "unknown object in agent output",
                lambda item: item.agent_outputs[first_agent].__setitem__(
                    "risk_score", object()
                ),
            ),
            (
                "wrong numeric type in agent output",
                lambda item: item.agent_outputs[first_agent].__setitem__(
                    "risk_score", True
                ),
            ),
            (
                "non-finite number in agent output",
                lambda item: item.agent_outputs[first_agent].__setitem__(
                    "risk_score", float("nan")
                ),
            ),
        ):
            malformed = deepcopy(clean_result)
            mutate(malformed)
            require_rejected_without_echo(
                lambda malformed=malformed: memory.save(malformed),
                label=label,
            )

        def require_nested_decision_rejected(
            *,
            label: str,
            mutate,
            db_name: str,
        ) -> None:
            raw_tenant = "tenant-nested-decision-sentinel"
            malformed = deepcopy(clean_result)
            mutate(malformed, raw_tenant)
            require_rejected_without_echo(
                lambda: memory.save(malformed, tenant_id=raw_tenant),
                label=label + " memory save",
                sentinel=raw_tenant,
            )

            nested_db_path = Path(tmpdir) / db_name
            nested_store = SQLiteExperimentStore(
                nested_db_path,
                require_tenant_id=True,
                allowed_tenant_ids=(raw_tenant,),
            )
            require_rejected_without_echo(
                lambda: nested_store.save(malformed, tenant_id=raw_tenant),
                label=label + " SQLite save",
                sentinel=raw_tenant,
            )

            payload = json.dumps(
                serialize_experiment_result(malformed),
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
            key = tenant_storage_key(malformed.summary.experiment_id, raw_tenant)
            with sqlite3.connect(nested_db_path) as conn:
                conn.execute(
                    "INSERT INTO experiments (experiment_id, result_json) VALUES (?, ?)",
                    (key, payload),
                )
            reloaded = SQLiteExperimentStore(
                nested_db_path,
                require_tenant_id=True,
                allowed_tenant_ids=(raw_tenant,),
            )
            require_rejected_without_echo(
                lambda: reloaded.get(
                    malformed.summary.experiment_id,
                    tenant_id=raw_tenant,
                ),
                label=label + " SQLite reload get",
                sentinel=raw_tenant,
            )
            require_rejected_without_echo(
                lambda: reloaded.list(tenant_id=raw_tenant),
                label=label + " SQLite reload list",
                sentinel=raw_tenant,
            )

        require_nested_decision_rejected(
            label="raw tenant in decision ranking",
            mutate=lambda item, raw_tenant: item.summary.decision_result.ranking.__setitem__(
                0,
                item.summary.decision_result.ranking[0].model_copy(
                    update={"agent_id": raw_tenant}
                ),
            ),
            db_name="nested-ranking.sqlite3",
        )
        require_nested_decision_rejected(
            label="raw tenant in decision failure summary",
            mutate=lambda item, raw_tenant: setattr(
                item.summary.decision_result,
                "failure_modes_summary",
                {
                    **item.summary.decision_result.failure_modes_summary,
                    raw_tenant: ["synthetic_failure"],
                },
            ),
            db_name="nested-failure-summary.sqlite3",
        )
        sqlite_store.save(clean_result, tenant_id="tenant-a")
        with sqlite3.connect(db_path) as conn:
            row = conn.execute(
                "SELECT experiment_id, result_json FROM experiments"
            ).fetchone()
        require(row is not None, "SQLite row missing")
        require("tenant-a" not in str(row[0]), "raw tenant ID entered SQLite primary key")
        require(str(row[0]).startswith("tenant:v1:"), "versioned tenant digest key missing")
        require(CREDENTIAL_SENTINEL not in str(row[1]), "SQLite result contains sentinel")
        reloaded = SQLiteExperimentStore(
            db_path,
            require_tenant_id=True,
            allowed_tenant_ids=("tenant-a", "tenant-b"),
        )
        require(
            reloaded.get(clean_result.summary.experiment_id, tenant_id="tenant-a") is not None,
            "pseudonymous tenant key did not survive reload",
        )

        legacy_path = Path(tmpdir) / "legacy.sqlite3"
        SQLiteExperimentStore(legacy_path)
        with sqlite3.connect(legacy_path) as conn:
            conn.execute(
                "INSERT INTO experiments (experiment_id) VALUES (?)",
                ("tenant:tenant-a:legacy-experiment",),
            )
        require_rejected_without_echo(
            lambda: SQLiteExperimentStore(
                legacy_path,
                require_tenant_id=True,
                allowed_tenant_ids=("tenant-a",),
            ),
            label="legacy raw tenant key",
        )


def main() -> None:
    audit_boundary()
    request = request_boundary()
    persistence_boundary(request)
    print(
        "SAEE_TENANT_SECRET_BOUNDARY_SMOKE: PASS "
        "audit_closed_schema=true request_secret_rejection=true "
        "runner_revalidation=true persistence_closed_schema=true "
        "memory_copy_isolation=true sqlite_tenant_key_pseudonymous=true "
        "legacy_raw_tenant_key_fail_closed=true secret_echo_count=0 "
        "raw_tenant_cross_field_denied=true nested_type_fail_closed=true "
        "nested_decision_tenant_denied=true negative_cases=24/24 "
        "tenant_secret_boundary_reviewed=false production_ready=false blockers_closed=0"
    )


if __name__ == "__main__":
    main()
