# SAEE v1.2 Experiment Report

## Local Demo Command

```bash
python3 saee_v1_2/bootstrap/v1_2_bootstrap.py --generations 24 --output-dir saee_v1_2/results/demo-run
python3 saee_v1_2/parasitic_phase/run_parasitic_phase_experiment.py --output-dir saee_v1_2/results/parasitic-phase-demo
```

## Expected Outputs

- `simulation_logs/saee_trace.json`
- `metric_reports/metric_report.json`
- `metric_reports/attractor_report.json`
- `metric_reports/regime_transition_report.json`
- `metric_reports/coupling_report.json`
- `comparison_reports/baseline_comparison.json`
- `experiment_summary.json`
- `saee_v1_2/results/parasitic-phase-demo/summary.json`
- `saee_v1_2/results/parasitic-phase-demo/*/metrics.csv`
- `saee_v1_2/results/parasitic-phase-demo/*/trace.jsonl`
- `saee_v1_2/results/parasitic-phase-demo/parasitic_phase_curves.svg`

## Evaluation Questions

1. Does the minimal SAEE instantiation produce measurable population
   trajectories?
2. Does lineage entropy change across generations?
3. Are attractors detectable in simulation space?
4. Are regime transitions measurable?
5. Is reflexive coupling quantifiable?
6. Do baseline comparisons execute on the same metrics?
7. Does the local parasitic phase experiment detect a `phi` threshold crossing
   without governance?
8. Does weak or strong governance delay or suppress the crossing?

## Boundary

This report is local empirical alignment. It is not external validation,
publication, broad proof, or production scientific evidence.

The parasitic phase experiment is also local synthetic evidence only. It does
not validate production governance and does not modify the frozen v1.0
long-horizon experiment boundary.
