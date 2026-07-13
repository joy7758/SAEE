# SAEE Open Abstraction Release

Status: local GitHub-ready subset, not released.

## Purpose

This folder is a public-safe abstraction layer. It gives readers a runnable toy
demonstration and analysis stubs without exposing the private SAEE core.

## Included

- `experiment_layer/experiment_runner_stub.py`: toy observation runner.
- `experiment_layer/logging_tools.py`: JSONL logging helper.
- `analysis_layer/regime_classifier_stub.py`: toy regime classifier.
- `analysis_layer/attractor_mapper_stub.py`: toy attractor mapper.
- `demo/minimal_evolution_demo.py`: standalone toy demo.

## Not Included

- SAEE v1.0 kernel;
- proprietary fitness computation logic;
- proprietary selection mechanism;
- lineage optimization system;
- mutation/reproduction engine;
- runtime orchestration internals;
- private configuration.

## Run

```bash
python3 github_release/demo/minimal_evolution_demo.py
```

## Boundary

This is not the SAEE runtime. It is a toy abstraction for public education and
interface orientation. It does not import `saee_v1_0`, `kernel`, or private
engine modules.

No GitHub release, tag, package upload, or public distribution has been
performed by this local package.

