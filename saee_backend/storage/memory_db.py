"""In-memory persistence for the SAEE MVP API shell."""

from __future__ import annotations

from dataclasses import dataclass, field
from copy import deepcopy
import os
from typing import Any

from saee_backend.models.response import (
    ComparisonRanking,
    EvaluationRunSummary,
    FailureModeReport,
    StabilityReport,
    SurvivalCurve,
)
from saee_backend.storage.tenant_key import (
    tenant_public_experiment_id,
    tenant_storage_key,
    validate_required_storage_tenant_id,
    validate_storage_tenant_allowlist,
)
from saee_backend.storage.secret_boundary import (
    validate_identifier_not_tenant,
    validate_persistable_experiment_result,
)
from saee_backend.services.authorization_context import (
    AuthorizedPrincipalContext,
    TenantAuthorization,
    tenant_id_from_authorization,
    validate_authorized_principal_context,
)


CREATE_PERMISSIONS = frozenset({"experiment:create"})
RUN_PERMISSIONS = frozenset({"experiment:run"})
READ_PERMISSIONS = frozenset({"experiment:read"})


@dataclass(frozen=True)
class AgentRunRecord:
    agent_id: str
    run_index: int
    scores: list[float]
    alive: list[bool]
    collapse_step: int | None


@dataclass(frozen=True)
class AgentMetricRecord:
    agent_id: str
    stability_score: float
    survival_score: float
    failure_rate: float
    collapse_events: int
    drift_index: float
    risk_score: float
    ranking_score: float


@dataclass(frozen=True)
class ExperimentListRecord:
    experiment_id: str
    status: str
    recommended_agent: str | None = None
    confidence_score: float = 0.0


@dataclass
class ExperimentResult:
    summary: EvaluationRunSummary
    stability_reports: list[StabilityReport]
    failure_reports: list[FailureModeReport]
    survival_curves: list[SurvivalCurve]
    ranking: ComparisonRanking
    runs: list[AgentRunRecord] = field(default_factory=list)
    metrics: list[AgentMetricRecord] = field(default_factory=list)
    agent_outputs: dict[str, dict[str, Any]] = field(default_factory=dict)


class MemoryExperimentStore:
    def __init__(
        self,
        *,
        require_tenant_id: bool = False,
        allowed_tenant_ids: tuple[str, ...] = (),
        require_authorized_context: bool = False,
    ) -> None:
        self._records: dict[str, ExperimentResult] = {}
        self._created: set[str] = set()
        self.require_tenant_id = require_tenant_id
        self.allowed_tenant_ids = validate_storage_tenant_allowlist(
            required=require_tenant_id,
            allowed_tenant_ids=tuple(allowed_tenant_ids),
        )
        self.require_authorized_context = require_authorized_context

    def _tenant_id(
        self,
        authorization: TenantAuthorization,
        required_permissions: frozenset[str],
    ) -> str | None:
        if self.require_authorized_context:
            if not isinstance(authorization, AuthorizedPrincipalContext):
                raise ValueError("an authorized principal context is required by storage")
            return validate_authorized_principal_context(
                authorization,
                capability_secret=os.environ.get(
                    "SAEE_PREVIEW_JWT_HS256_SECRET", ""
                ).strip(),
                allowed_tenant_ids=self.allowed_tenant_ids,
                required_permissions=required_permissions,
            )
        return tenant_id_from_authorization(authorization)

    def _key(
        self,
        experiment_id: str,
        tenant_id: TenantAuthorization = None,
        required_permissions: frozenset[str] = READ_PERMISSIONS,
    ) -> str:
        tenant_id = self._tenant_id(tenant_id, required_permissions)
        safe_tenant_id = validate_required_storage_tenant_id(
            tenant_id,
            required=self.require_tenant_id,
            allowed_tenant_ids=self.allowed_tenant_ids,
        )
        return tenant_storage_key(experiment_id, safe_tenant_id)

    def _public_id(self, key: str, tenant_id: str | None = None) -> str | None:
        return tenant_public_experiment_id(key, tenant_id)

    def create(self, experiment_id: str, tenant_id: str | None = None) -> None:
        safe_tenant_id = self._tenant_id(tenant_id, CREATE_PERMISSIONS)
        validate_identifier_not_tenant(experiment_id, safe_tenant_id)
        self._created.add(self._key(experiment_id, tenant_id, CREATE_PERMISSIONS))

    def save(self, result: ExperimentResult, tenant_id: str | None = None) -> None:
        safe_tenant_id = self._tenant_id(tenant_id, RUN_PERMISSIONS)
        validate_persistable_experiment_result(result, tenant_id=safe_tenant_id)
        key = self._key(result.summary.experiment_id, tenant_id, RUN_PERMISSIONS)
        self._records[key] = deepcopy(result)
        self._created.add(key)

    def exists(self, experiment_id: str, tenant_id: str | None = None) -> bool:
        key = self._key(experiment_id, tenant_id)
        return key in self._created or key in self._records

    def get(self, experiment_id: str, tenant_id: str | None = None) -> ExperimentResult | None:
        result = self._records.get(self._key(experiment_id, tenant_id))
        if result is None:
            return None
        validate_persistable_experiment_result(
            result,
            tenant_id=self._tenant_id(tenant_id, READ_PERMISSIONS),
        )
        return deepcopy(result)

    def get_runs(self, experiment_id: str, tenant_id: str | None = None) -> list[AgentRunRecord]:
        result = self.get(experiment_id, tenant_id)
        return [] if result is None else result.runs

    def get_metrics(
        self, experiment_id: str, tenant_id: str | None = None
    ) -> list[AgentMetricRecord]:
        result = self.get(experiment_id, tenant_id)
        return [] if result is None else result.metrics

    def list(self, tenant_id: str | None = None) -> list[ExperimentListRecord]:
        tenant_id = self._tenant_id(tenant_id, READ_PERMISSIONS)
        safe_tenant_id = validate_required_storage_tenant_id(
            tenant_id,
            required=self.require_tenant_id,
            allowed_tenant_ids=self.allowed_tenant_ids,
        )
        records: list[ExperimentListRecord] = []
        for key in sorted(self._created | set(self._records)):
            public_id = self._public_id(key, safe_tenant_id)
            if public_id is None:
                continue
            result = self._records.get(key)
            if result is None:
                records.append(ExperimentListRecord(experiment_id=public_id, status="created"))
                continue
            validate_persistable_experiment_result(result, tenant_id=safe_tenant_id)
            summary = result.summary
            records.append(
                ExperimentListRecord(
                    experiment_id=public_id,
                    status=summary.status,
                    recommended_agent=summary.recommended_agent,
                    confidence_score=summary.confidence_score,
                )
            )
        return records
