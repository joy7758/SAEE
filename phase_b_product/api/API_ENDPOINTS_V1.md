# SAEE MVP API Endpoints v1.0

Status: endpoint contract with local FastAPI route shell implemented; not a
production API, public SDK, or private-core integration.

## Endpoint Summary

```text
GET  /experiment
POST /experiment/create
POST /experiment/run
GET  /experiment/{id}/stability
GET  /experiment/{id}/failures
GET  /experiment/{id}/ranking
GET  /experiment/{id}/survival
```

## 1. List Experiments

```text
GET /experiment
```

Purpose:

```text
List public-shell experiment report records visible to the current request scope.
```

Response:

```text
ExperimentListResponse
```

Boundary:

- lists report-level experiment IDs and summary fields only;
- when the tenant request boundary is enabled, lists only the current tenant's
  records;
- unscoped requests do not see tenant-scoped records;
- does not expose request bodies, private runtime state, scoring internals, or
  private core.

## 2. Create Experiment

```text
POST /experiment/create
```

Purpose:

```text
Create an experiment shell before submitting a scenario batch.
```

Allowed request fields:

- `experiment_id`
- `name`
- `description`
- `owner_label`
- `created_by`

Response:

- `experiment_id`
- `status`

Boundary:

- does not create a public product account;
- does not start evaluation;
- does not expose private runtime state.

## 3. Run Evaluation

```text
POST /experiment/run
```

Request:

```text
ScenarioBatchRequest
```

Response:

```text
EvaluationRunSummary
```

Boundary:

- request validation happens at the API layer;
- `agent_id`, `experiment_id`, and `scenario_type` use one bounded public-safe
  identifier contract; duplicate agent IDs are rejected;
- credential-named config fields and high-confidence Bearer/JWT/API-key/token
  forms are rejected again at the runner boundary, including direct internal
  calls that bypass normal model construction;
- validation errors do not reflect rejected input values;
- private execution remains behind the product boundary;
- response is aggregate report data only.

## 4. Get Stability Report

```text
GET /experiment/{id}/stability
```

Response:

```text
StabilityReport[]
```

Boundary:

- exposes stability scores and public time series only;
- does not expose private stability computation internals.

## 5. Get Failure Modes

```text
GET /experiment/{id}/failures
```

Response:

```text
FailureModeReport[]
```

Boundary:

- exposes public failure labels and descriptions only;
- does not expose internal detector implementation.

## 6. Get Ranking

```text
GET /experiment/{id}/ranking
```

Response:

```text
ComparisonRanking
```

Boundary:

- exposes rank and score only;
- does not expose private ranking formula or scoring internals.

## 7. Get Survival Curves

```text
GET /experiment/{id}/survival
```

Response:

```text
SurvivalCurve[]
```

Boundary:

- exposes report-level survival trajectory only;
- does not expose lineage construction internals.

## Current Boundary

```text
endpoint_contract_recorded: true
runnable_api_shell_implemented: true
api_routes_implemented: true
tenant_scoped_experiment_listing: true
fastapi_dependency_installed_in_current_environment: false
production_deployed: false
public_sdk_release: false
implementation_disclosed: false
```
