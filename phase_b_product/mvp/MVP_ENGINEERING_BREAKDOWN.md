# SAEE MVP Engineering Breakdown

Status: implementation planning document, not a code change and not a runtime
modification.

## MVP Build Units

### 1. Evaluation Engine Adapter

Purpose:

- expose a product-safe interface over the private evaluation core;
- schedule long-horizon competition runs;
- return report-level outputs only.

Inputs:

- scenario batch request;
- agent or strategy descriptors;
- constraints;
- deterministic seed label.

Outputs:

- run status;
- evaluated episode summaries;
- stability report;
- comparison ranking.

Private boundary:

- no kernel source exposure;
- no fitness, selection, mutation, lineage, or runtime internals.

### 2. Scenario Engine

Purpose:

- provide safe scenario templates and stress-test configurations.

MVP templates:

- RAG policy stress test;
- workflow automation stability test;
- customer-support agent tournament;
- generic adversarial-noise scenario.

Outputs:

- scenario configuration summary;
- perturbation summary;
- limitation statement.

### 3. Metrics Engine

Purpose:

- compute report-facing evaluation metrics.

Required MVP metrics:

- stability score;
- failure-mode labels;
- survival curve;
- comparison ranking.

Output boundary:

- report metrics only;
- no private scoring internals.

### 4. Trace / Logging Layer

Purpose:

- store run history and reproducibility metadata.

MVP records:

- experiment id;
- scenario id;
- agent or strategy ids;
- seed label;
- episode count;
- report outputs;
- timestamp.

Private boundary:

- no raw private orchestration traces in public reports;
- no customer secrets.

### 5. Frontend

Purpose:

- make the workflow usable by AI teams.

MVP screens:

- dashboard;
- experiment setup;
- running simulation;
- results summary.

### 6. Report Export

Purpose:

- produce product-safe benchmark reports.

Formats:

- markdown;
- PDF later;
- JSON summary later.

## Build Order

```text
1. Product-safe request/response schema
2. Scenario template definitions
3. Metrics report contract
4. Local dashboard prototype
5. Exportable markdown report
6. Guard checks for no private-core disclosure
```

## Non-Goals

- no new evolution kernel;
- no new science layer;
- no phase diagram extension;
- no public SDK release;
- no production SaaS;
- no customer data ingestion;
- no external repository execution.

## Current Boundary

```text
engineering_plan_created: true
code_created: false
kernel_modified: false
runtime_modified: false
product_launched: false
private_core_exported: false
implementation_disclosed: false
```
