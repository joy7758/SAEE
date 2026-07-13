# SAEE MVP API Contract v1.0

Status: API contract design with a local runnable API shell, not public SDK,
not private-core integration, and not a production API.

Generated: 2026-07-03

## Core Principle

The SAEE MVP API exposes evaluation results, not evolution internals.

The contract must preserve four hard constraints:

```text
kernel_exposed: false
evolution_mechanism_exposed: false
lineage_internal_structure_exposed: false
result_layer_only: true
```

## Product Definition

```text
SAEE API = black-box long-term competition evaluator for AI systems
```

Customer value:

- identify which AI agent or strategy is more stable;
- detect which one collapses;
- observe which one survives over time;
- decide which one is safer to move toward deployment review.

## Public Data Objects

### 1. ScenarioBatchRequest

Purpose:

```text
Submit multiple AI systems or strategies into one long-horizon competition
scenario.
```

Shape:

```json
{
  "experiment_id": "string",
  "agents": [
    {
      "agent_id": "string",
      "config": "opaque_string_or_json",
      "type": "llm|rule|workflow|agent"
    }
  ],
  "environment": {
    "scenario_type": "string",
    "noise_level": 0.0,
    "competition_intensity": 0.0,
    "time_horizon": 100
  },
  "evaluation_config": {
    "metrics": [
      "stability",
      "survival",
      "failure_mode",
      "ranking"
    ],
    "repeat_runs": 10
  }
}
```

Input boundary:

- `config` is opaque to the public API contract;
- no external repository execution;
- no install scripts;
- no secrets;
- no external code as genome.

### 2. EvaluationRunSummary

Purpose:

```text
Return run-level status and aggregate agent scores.
```

Shape:

```json
{
  "experiment_id": "string",
  "run_id": "string",
  "status": "completed|running|failed",
  "agents": [
    {
      "agent_id": "string",
      "final_score": 0.0
    }
  ],
  "overall_stats": {
    "mean_stability": 0.0,
    "mean_survival": 0.0,
    "divergence_index": 0.0
  }
}
```

### 3. StabilityReport

Purpose:

```text
Explain whether one agent remained stable, became unstable, or collapsed.
```

Shape:

```json
{
  "agent_id": "string",
  "stability_score": 0.0,
  "drift_rate": 0.0,
  "variance": 0.0,
  "convergence_status": "stable|unstable|collapsing",
  "time_series": [0.0, 0.0, 0.0]
}
```

### 4. FailureModeReport

Purpose:

```text
Describe public failure modes at report level.
```

Shape:

```json
{
  "agent_id": "string",
  "failure_modes": [
    {
      "type": "drift|collapse|oscillation|degeneration",
      "step": 0,
      "severity": 0.0,
      "description": "string"
    }
  ]
}
```

### 5. SurvivalCurve

Purpose:

```text
Show whether one agent survives over time and how its score evolves.
```

Shape:

```json
{
  "agent_id": "string",
  "curve": [
    {
      "t": 0,
      "alive": true,
      "score": 0.0
    }
  ]
}
```

### 6. ComparisonRanking

Purpose:

```text
Rank agents or strategies by long-term evaluation outcome.
```

Shape:

```json
{
  "experiment_id": "string",
  "ranking": [
    {
      "rank": 1,
      "agent_id": "string",
      "score": 0.0
    }
  ]
}
```

### 7. ExperimentListResponse

Purpose:

```text
List public-shell experiment report records visible to the current request
scope.
```

Shape:

```json
{
  "experiments": [
    {
      "experiment_id": "string",
      "status": "created|completed|running|failed",
      "recommended_agent": "string|null",
      "confidence_score": 0.0
    }
  ],
  "count": 1
}
```

Boundary:

- report directory only;
- no request body exposure;
- no private scoring internals;
- no private runtime state;
- tenant-scoped when `X-SAEE-Tenant-ID` is enabled.

## Endpoint Contract

| Method | Path | Purpose | Request | Response |
| --- | --- | --- | --- | --- |
| `GET` | `/experiment` | List visible experiment reports | request scope | `ExperimentListResponse` |
| `POST` | `/experiment/create` | Create experiment shell | experiment metadata | experiment id and status |
| `POST` | `/experiment/run` | Start scenario batch evaluation | `ScenarioBatchRequest` | `EvaluationRunSummary` |
| `GET` | `/experiment/{id}/stability` | Read stability reports | path id | `StabilityReport[]` |
| `GET` | `/experiment/{id}/failures` | Read failure-mode reports | path id | `FailureModeReport[]` |
| `GET` | `/experiment/{id}/ranking` | Read comparison ranking | path id | `ComparisonRanking` |
| `GET` | `/experiment/{id}/survival` | Read survival curves | path id | `SurvivalCurve[]` |

## Architecture Boundary

Allowed API layers:

- request validation;
- experiment routing;
- report retrieval;
- local public-shell route implementation;
- JSON output;
- exportable reports.

Private layers:

- private evaluation engine;
- competition scheduler implementation;
- scoring implementation;
- stability computation internals;
- survival analysis internals;
- failure detection internals;
- lineage-like tracking internals.

## Forbidden API Exposure

Do not expose:

- kernel implementation;
- evolution mechanism;
- private scoring formula;
- private selection procedure;
- mutation or reproduction mechanism;
- lineage internal structure;
- private runtime orchestration.

## Current Boundary

```text
api_contract_recorded: true
runnable_api_shell_implemented: true
private_core_backend_implemented: false
public_sdk_release: false
product_launched: false
private_core_exported: false
implementation_disclosed: false
kernel_modified_by_api_contract: false
runtime_modified_by_api_contract: false
```
