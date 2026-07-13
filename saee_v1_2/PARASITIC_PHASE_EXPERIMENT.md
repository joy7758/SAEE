# SAEE v1.2 Parasitic Phase Experiment

Status: local-only synthetic experiment.

## Purpose

This layer instantiates the execution-spec question:

Can a minimal multi-agent digital ecology produce a measurable parasitic phase
transition, and can bounded governance delay or suppress the local threshold
crossing?

## Placement

This experiment belongs under `saee_v1_2/` because it generates new local
simulation data for empirical alignment. It is not placed under
`saee_experiments/`, because that directory is a passive v1.0 observation layer
that must not add new mechanics. It is not placed under
`digital-biosphere-architecture`, because that repository is a public meaning
layer, not a reconstructable runtime path.

## Phi Definition

Machine field: `phi`.

```text
phi = 0.35 * resource_concentration
    + 0.35 * reward_drift
    + 0.30 * agent_dominance
```

Measured variables:

- `resource_concentration`: Gini coefficient over agent resources.
- `reward_drift`: reward-vector drift from each type baseline, normalized to
  the reachable drift interval for this local reward-vector design.
- `agent_dominance`: dominant lineage control ratio, computed from population
  share and resource share.

## Parasitic Phase Trigger

```text
if phi(t) > phi_c and phi(t) - phi(t - 1) > 0:
    parasitic_phase_entered = true
```

Default `phi_c` is `0.60`.

## Experiments

| experiment | governance | expected local outcome |
| --- | --- | --- |
| `A_no_governance` | none | crosses the parasitic phase threshold |
| `B_weak_governance` | weak cap, weak penalty, weak drift damping | delayed or suppressed crossing |
| `C_strong_governance` | strong cap, strong penalty, strong drift damping | stronger suppression or later crossing |

## SAEE Trace

Each experiment writes:

- `metrics.csv`
- `trace.jsonl`
- `summary.json`

The trace records:

- `timestep`
- `agent_actions`
- `resource_allocations`
- `reward_updates`
- `metrics`
- `governance_actions`
- `events`

This is an observational trace for local causal replay. It does not prove
real-world causality.

## Command

```bash
python3 saee_v1_2/parasitic_phase/run_parasitic_phase_experiment.py --steps 160 --output-dir saee_v1_2/results/parasitic-phase-demo
python3 scripts/saee_parasitic_phase_smoke.py
```

## Boundaries

- local-only
- standard-library only
- no external API calls
- no external repository execution
- no production governance claim
- no external scientific validation claim
- no broad-theory claim
