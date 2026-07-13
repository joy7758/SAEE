# SAEE v1.0 Long-Horizon Experiment Spec

## Purpose

`saee_experiments/` adds a passive long-horizon experiment layer above the
immutable SAEE v1.0 runtime.

It runs the v1.0 evolution machine for 100 to 10000 generations, records full
generation traces, and produces stability, drift, emergence, lineage, and
collapse reports.

## Constitution

- v1.0 kernel files are not modified.
- One evolution loop remains the only runtime loop.
- One population pool remains the only population model.
- One unified fitness function remains the only fitness model; in guard terms,
  one unified fitness function is preserved.
- One lineage DAG remains the only lineage model.
- No phase, physics, reflexive, semantic, epistemic, or observer-feedback layer
  enters runtime logic.
- Experiment outputs are observational only.

## Modules

- `runner/experiment_runner.py`: executes `saee_v1_0.runtime.saee_runtime` for a configured long horizon.
- `logging/evolution_trace_logger.py`: writes immutable per-generation JSONL traces.
- `analysis/stability_analyzer.py`: measures variance, collapse events, branching density, and convergence tendency.
- `analysis/drift_monitor.py`: measures mutation accumulation, population turnover, and lineage structural drift.
- `analysis/emergence_observer.py`: detects repeated patterns and persistent genome structures without feedback.
- `analysis/report_generator.py`: writes report artifacts.
- `bootstrap/experiment_bootstrap.py`: deterministic one-command experiment runner.

## Configuration

`configs/experiment_config.yaml` supports:

- `generation_count`: 100 to 10000
- `population_size`: fixed v1.0 population size
- `deterministic_seed`: must be `enabled`
- `logging_level`: must be `full_trace`
- `seed_path`: local seed genome path
- `output_dir`: experiment run output directory

## Commands

```bash
python3 saee_experiments/bootstrap/experiment_bootstrap.py --generation-count 100 --output-dir saee_experiments/output/demo-run
python3 scripts/saee_experiment_smoke.py
```

## Required Report Surfaces

- `saee_experiments/reports/evolution_summary.md`
- `saee_experiments/reports/stability_report.json`
- `saee_experiments/reports/lineage_statistics.json`
- `saee_experiments/reports/collapse_events.log`

Per-run copies are also written under the configured output directory.

## Boundary

This layer is not Phase II behavior science, not meta-evolution, not
observability feedback, not reflexivity, and not an upgrade to v1.0. It is a
local, deterministic experiment harness that observes v1.0 outputs.
