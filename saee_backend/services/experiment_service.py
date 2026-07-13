"""Experiment service for the SAEE MVP API shell."""

from __future__ import annotations

import uuid

from saee_backend.core.runner import run_scenario_batch
from saee_backend.models.request import ExperimentCreateRequest, ScenarioBatchRequest
from saee_backend.models.response import (
    ComparisonRanking,
    EvaluationRunSummary,
    ExperimentListItem,
    ExperimentListResponse,
    ExperimentCreateResponse,
    FailureModeReport,
    StabilityReport,
    SurvivalCurve,
)
from saee_backend.storage.factory import create_experiment_store
from saee_backend.storage.memory_db import MemoryExperimentStore
from saee_backend.services.public_input_contract import validate_public_identifier


class ExperimentNotFound(Exception):
    """Raised when an experiment has no stored evaluation result."""


class ExperimentService:
    def __init__(self, store: MemoryExperimentStore) -> None:
        self.store = store

    def create_experiment(
        self, req: ExperimentCreateRequest, tenant_id: str | None = None
    ) -> ExperimentCreateResponse:
        experiment_id = req.experiment_id or str(uuid.uuid4())
        validate_public_identifier(experiment_id, field_name="experiment_id")
        self.store.create(experiment_id, tenant_id)
        return ExperimentCreateResponse(experiment_id=experiment_id, status="created")

    def list_experiments(self, tenant_id: str | None = None) -> ExperimentListResponse:
        records = self.store.list(tenant_id)
        experiments = [
            ExperimentListItem(
                experiment_id=record.experiment_id,
                status=record.status,
                recommended_agent=record.recommended_agent,
                confidence_score=record.confidence_score,
            )
            for record in records
        ]
        return ExperimentListResponse(experiments=experiments, count=len(experiments))

    def run_experiment(
        self, req: ScenarioBatchRequest, tenant_id: str | None = None
    ) -> EvaluationRunSummary:
        result = run_scenario_batch(req)
        self.store.save(result, tenant_id)
        return result.summary

    def get_stability(
        self, experiment_id: str, tenant_id: str | None = None
    ) -> list[StabilityReport]:
        return self._get_result(experiment_id, tenant_id).stability_reports

    def get_failures(
        self, experiment_id: str, tenant_id: str | None = None
    ) -> list[FailureModeReport]:
        return self._get_result(experiment_id, tenant_id).failure_reports

    def get_ranking(self, experiment_id: str, tenant_id: str | None = None) -> ComparisonRanking:
        return self._get_result(experiment_id, tenant_id).ranking

    def get_survival(
        self, experiment_id: str, tenant_id: str | None = None
    ) -> list[SurvivalCurve]:
        return self._get_result(experiment_id, tenant_id).survival_curves

    def _get_result(self, experiment_id: str, tenant_id: str | None = None):
        validate_public_identifier(experiment_id, field_name="experiment_id")
        result = self.store.get(experiment_id, tenant_id)
        if result is None:
            raise ExperimentNotFound("Experiment has no completed run")
        return result


experiment_service = ExperimentService(create_experiment_store())
