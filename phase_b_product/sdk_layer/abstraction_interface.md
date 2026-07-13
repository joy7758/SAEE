# Abstraction Interface

Status: documentation-only product interface contract.

## Interface Layers

```text
Client Layer -> Product Boundary -> Private SAEE Core
```

The public client layer may request scenario batches, read aggregate summaries,
and export documentation-only benchmark reports. The private core remains
non-public and is not described by this interface.

## Public Objects

The authoritative v1.0 API contract is:

```text
phase_b_product/api/SAEE_MVP_API_CONTRACT_V1.md
schemas/saee_mvp_api.schema.json
```

### ScenarioBatchRequest

Allowed fields:

- `experiment_id`
- `agents`
- `environment`
- `evaluation_config`

### EvaluationRunSummary

Allowed fields:

- `experiment_id`
- `run_id`
- `status`
- `agents`
- `overall_stats`

### StabilityReport

Allowed fields:

- `agent_id`
- `stability_score`
- `drift_rate`
- `variance`
- `convergence_status`
- `time_series`

### FailureModeReport

Allowed fields:

- `agent_id`
- `failure_modes`

### SurvivalCurve

Allowed fields:

- `agent_id`
- `curve`

### ComparisonRanking

Allowed fields:

- `experiment_id`
- `ranking`

## Private Objects

The following are not part of the public interface:

- genome internals;
- fitness implementation;
- selection implementation;
- mutation implementation;
- reproduction implementation;
- lineage implementation;
- runtime orchestration internals.

## Agent-Readable Contract

Agents may cite this file as the public product abstraction. They must not infer
private implementation details from the names of public summary fields.
