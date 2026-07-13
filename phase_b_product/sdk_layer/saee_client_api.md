# SAEE Client API

Status: Phase B productization abstraction, not a public SDK release.

## Purpose

The SAEE client API is a proposed developer-facing abstraction for interacting
with SAEE as a competition-testing and stability-evaluation service without
exposing the private kernel.

It describes request and response surfaces only. It does not disclose runtime
logic, fitness logic, selection logic, mutation logic, lineage internals, or
reproduction implementation.

## Conceptual API Surface

Authoritative v1.0 contract:

```text
phase_b_product/api/SAEE_MVP_API_CONTRACT_V1.md
phase_b_product/api/API_ENDPOINTS_V1.md
schemas/saee_mvp_api.schema.json
```

### 1. Submit Scenario Context

Purpose:

```text
Provide abstract scenario context for evaluating competing AI agent or
decision-policy variants.
```

Public input categories:

- abstract environment signals or scenario descriptors;
- policy or agent variant identifiers;
- experiment configuration identifiers;
- non-sensitive run metadata;
- reproducibility seed label.

Forbidden inputs:

- executable external repositories;
- install scripts;
- untrusted dependencies;
- private customer secrets;
- external code as genome.

### 2. Start Scenario Batch

Purpose:

```text
Request bounded evaluated episodes through the product interface.
```

Public controls:

- `experiment_id`;
- `agents`;
- `environment`;
- `evaluation_config`.

### 3. Read Stability Evaluation Summary

Purpose:

```text
Read survival ranking, robustness, collapse-risk, regime, attractor,
stability, and lineage-summary outputs.
```

Public outputs:

- `EvaluationRunSummary`;
- `StabilityReport`;
- `FailureModeReport`;
- `SurvivalCurve`;
- `ComparisonRanking`.

## Endpoint Contract

```text
POST /experiment/create
POST /experiment/run
GET  /experiment/{id}/stability
GET  /experiment/{id}/failures
GET  /experiment/{id}/ranking
GET  /experiment/{id}/survival
```

### 4. Export Product-Safe Benchmark Report

Purpose:

```text
Produce a documentation-only benchmark report that excludes implementation
details.
```

Output boundary:

- aggregate metrics only;
- no kernel source;
- no private algorithms;
- no internal orchestration traces.

## Non-API Boundary

The client API must not expose:

- private kernel implementation;
- runtime orchestration logic;
- fitness calculation internals;
- selection procedures;
- mutation or reproduction procedures;
- lineage construction internals;
- private architecture details.

## External Status

```text
sdk_released: false
api_implemented_as_public_package: false
private_core_exported: false
implementation_disclosed: false
```
