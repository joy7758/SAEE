# SAEE MVP API Implementation Boundary

Status: implementation boundary for future backend work.

## Black-Box Rule

The API is a black-box long-term competition evaluator.

Public users may see:

- requests;
- statuses;
- stability scores;
- failure modes;
- survival curves;
- comparison rankings;
- exportable reports.

Public users must not see:

- kernel implementation;
- private evolution mechanism;
- private scoring formula;
- private selection procedure;
- mutation or reproduction mechanism;
- lineage internals;
- private runtime orchestration.

## Safe Implementation Layers

Future backend work may implement:

- request validation;
- experiment routing;
- job status handling;
- report storage;
- report retrieval;
- report export.

Future backend work must keep private:

- evaluation engine internals;
- scenario execution internals;
- metrics implementation internals;
- trace and lineage internals.

## Input Safety Boundary

Default MVP input must be descriptor-based:

- agent id;
- strategy config;
- workflow descriptor;
- policy configuration;
- scenario parameters.

Forbidden inputs:

- executable repositories;
- install scripts;
- secrets;
- raw private customer production data without enterprise deployment review;
- external code copied as genome.

## Output Safety Boundary

Default MVP output must be report-based:

- `EvaluationRunSummary`;
- `StabilityReport`;
- `FailureModeReport`;
- `SurvivalCurve`;
- `ComparisonRanking`.

Forbidden outputs:

- source code;
- internal runtime traces;
- private scoring formula;
- private selection details;
- mutation/reproduction details;
- lineage internal graph.

## Current Boundary

```text
implementation_boundary_recorded: true
runnable_api_shell_implemented: true
private_core_backend_implemented: false
private_core_exported: false
implementation_disclosed: false
kernel_modified: false
runtime_modified: false
```
