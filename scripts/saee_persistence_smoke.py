#!/usr/bin/env python3
"""Smoke check for SAEE local persistence v0.1."""

from __future__ import annotations

import tempfile
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.models.request import EnvironmentConfig, EvaluationConfig, ScenarioBatchRequest
from saee_backend.services.experiment_service import ExperimentService
from saee_backend.storage.factory import create_experiment_store
from saee_backend.storage.sqlite_store import SQLiteExperimentStore


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_PERSISTENCE_SMOKE: FAIL: {message}")


def build_request() -> ScenarioBatchRequest:
    return ScenarioBatchRequest(
        experiment_id="persistence-smoke",
        agents=[
            {
                "agent_id": "agent-a",
                "config": {"policy": "aggressive-experimental-risky-unguarded-fragile"},
                "type": "llm",
            },
            {
                "agent_id": "agent-b",
                "config": {"workflow": "guarded-stable-monitor-retry-bounded-safe"},
                "type": "workflow",
            },
        ],
        environment=EnvironmentConfig(
            scenario_type="persistence_check",
            noise_level=0.2,
            competition_intensity=0.5,
            time_horizon=20,
        ),
        evaluation_config=EvaluationConfig(
            metrics=["stability", "survival", "failure_mode", "ranking"],
            repeat_runs=3,
        ),
    )


def main() -> None:
    memory_settings = load_settings({})
    memory_store = create_experiment_store(memory_settings)
    require(memory_store.__class__.__name__ == "MemoryExperimentStore", "default store must be memory")
    require(memory_settings.storage_backend == "memory", "default storage backend must be memory")

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "saee.sqlite3"
        sqlite_settings = load_settings(
            {
                "SAEE_STORAGE_BACKEND": "sqlite",
                "SAEE_STORAGE_PATH": str(db_path),
            }
        )
        require(sqlite_settings.storage_backend == "sqlite", "sqlite backend must be configurable")
        require(sqlite_settings.storage_path == str(db_path), "sqlite path must be configurable")
        require(
            sqlite_settings.readiness_payload()["durable_persistence"] is True,
            "sqlite readiness must report durable persistence",
        )

        service = ExperimentService(create_experiment_store(sqlite_settings))
        summary = service.run_experiment(build_request())
        stored_ranking = service.get_ranking(summary.experiment_id)
        require(db_path.is_file(), "sqlite database file must be created")
        require(stored_ranking.ranking[0].agent_id == summary.recommended_agent, "stored ranking mismatch")

        reloaded_store = SQLiteExperimentStore(db_path)
        reloaded = reloaded_store.get(summary.experiment_id)
        require(reloaded is not None, "reloaded result must exist")
        require(
            reloaded.summary.model_dump() == summary.model_dump(),
            "summary must survive store reconstruction",
        )
        require(len(reloaded_store.get_runs(summary.experiment_id)) == 6, "run records must persist")
        require(len(reloaded_store.get_metrics(summary.experiment_id)) == 2, "metric records must persist")

    doc = (ROOT / "phase_b_product/commercial_readiness/PERSISTENCE_V0_1.md").read_text(
        encoding="utf-8"
    )
    gate = (ROOT / "docs/strategy/SAEE_PERSISTENCE_RECOMMENDATION_GATE.md").read_text(
        encoding="utf-8"
    )
    require("durable_persistence_option: true" in doc, "persistence doc missing durable option")
    require("production_database_ready: false" in doc, "persistence doc must not claim production DB")
    require("answer: conditional" in gate, "persistence gate must remain conditional")

    print(
        "SAEE_PERSISTENCE_SMOKE: PASS "
        "default_memory=true "
        "sqlite_option=true "
        "reload_survives=true "
        "production_database_ready=false"
    )


if __name__ == "__main__":
    main()
