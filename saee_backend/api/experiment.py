"""Experiment routes for the SAEE MVP API shell."""

from fastapi import APIRouter, Depends, HTTPException

from saee_backend.models.request import ExperimentCreateRequest, ScenarioBatchRequest
from saee_backend.models.response import (
    ComparisonRanking,
    EvaluationRunSummary,
    ExperimentCreateResponse,
    ExperimentListResponse,
    FailureModeReport,
    StabilityReport,
    SurvivalCurve,
)
from saee_backend.api.security import (
    require_api_key,
    require_jwt_preview_auth,
    require_rbac_route,
    require_tenant_boundary,
)
from saee_backend.services.request_limits import RequestLimitViolation, validate_scenario_limits
from saee_backend.services.experiment_service import ExperimentNotFound, experiment_service


router = APIRouter(dependencies=[Depends(require_api_key), Depends(require_jwt_preview_auth)])


@router.get(
    "",
    response_model=ExperimentListResponse,
    dependencies=[Depends(require_rbac_route("GET /experiment"))],
)
def list_experiments(
    tenant_id: str | None = Depends(require_tenant_boundary),
) -> ExperimentListResponse:
    return experiment_service.list_experiments(tenant_id)


@router.post(
    "/create",
    response_model=ExperimentCreateResponse,
    dependencies=[Depends(require_rbac_route("POST /experiment/create"))],
)
def create_experiment(
    req: ExperimentCreateRequest,
    tenant_id: str | None = Depends(require_tenant_boundary),
) -> ExperimentCreateResponse:
    return experiment_service.create_experiment(req, tenant_id)


@router.post(
    "/run",
    response_model=EvaluationRunSummary,
    dependencies=[Depends(require_rbac_route("POST /experiment/run"))],
)
def run_experiment(
    req: ScenarioBatchRequest,
    tenant_id: str | None = Depends(require_tenant_boundary),
) -> EvaluationRunSummary:
    try:
        validate_scenario_limits(req)
    except RequestLimitViolation as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    return experiment_service.run_experiment(req, tenant_id)


@router.get(
    "/{experiment_id}/stability",
    response_model=list[StabilityReport],
    dependencies=[Depends(require_rbac_route("GET /experiment/{experiment_id}/stability"))],
)
def get_stability(
    experiment_id: str,
    tenant_id: str | None = Depends(require_tenant_boundary),
) -> list[StabilityReport]:
    try:
        return experiment_service.get_stability(experiment_id, tenant_id)
    except ExperimentNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/{experiment_id}/failures",
    response_model=list[FailureModeReport],
    dependencies=[Depends(require_rbac_route("GET /experiment/{experiment_id}/failures"))],
)
def get_failures(
    experiment_id: str,
    tenant_id: str | None = Depends(require_tenant_boundary),
) -> list[FailureModeReport]:
    try:
        return experiment_service.get_failures(experiment_id, tenant_id)
    except ExperimentNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/{experiment_id}/ranking",
    response_model=ComparisonRanking,
    dependencies=[Depends(require_rbac_route("GET /experiment/{experiment_id}/ranking"))],
)
def get_ranking(
    experiment_id: str,
    tenant_id: str | None = Depends(require_tenant_boundary),
) -> ComparisonRanking:
    try:
        return experiment_service.get_ranking(experiment_id, tenant_id)
    except ExperimentNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/{experiment_id}/survival",
    response_model=list[SurvivalCurve],
    dependencies=[Depends(require_rbac_route("GET /experiment/{experiment_id}/survival"))],
)
def get_survival(
    experiment_id: str,
    tenant_id: str | None = Depends(require_tenant_boundary),
) -> list[SurvivalCurve]:
    try:
        return experiment_service.get_survival(experiment_id, tenant_id)
    except ExperimentNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
