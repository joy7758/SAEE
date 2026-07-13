# SAEE v1.2 System Spec

Status: local-only empirical alignment layer.

## Identity

SAEE v1.2 grounds the formal system into a measurable local simulation:

SAEE = (Omega, G, T, S, L, R, mu)

It does not alter the formal model, add axioms, redesign equations, or extend
abstraction. It creates a minimal instantiation that can be measured and
compared against simple baseline evolutionary models.

## Empirical Loop

```text
Initialize population measure over genome space
-> apply reflexive transformation operator
-> apply reflexive selection field
-> update lineage relation
-> update observer state
-> measure metrics
-> detect attractors and regimes
-> compare baselines
```

## Core Objects

| Object | File | Purpose |
| --- | --- | --- |
| Minimal Evolution Model | `simulator/minimal_evolution_model.py` | Instantiates the formal tuple in a deterministic local simulation. |
| SAEE Runtime Simulation | `simulator/saee_runtime_sim.py` | Runs trajectories and writes records. |
| Empirical Metrics | `metrics/*.py` | Measures lineage entropy, regimes, reflexivity, and attractors. |
| Attractor Detector | `analysis/attractor_detector.py` | Detects stable states and convergence basins. |
| Regime Transition Analyzer | `analysis/regime_transition_analyzer.py` | Measures transitions between stable, exploratory, and chaotic states. |
| Coupling Quantifier | `analysis/coupling_quantifier.py` | Measures the impact of observer state on transformation and selection. |
| Baseline Comparisons | `baseline/*.py` | Runs GA, ES, and ALife-like baselines. |
| Experiment Runner | `experiments/run_saee_experiment.py` | Aggregates simulation, metrics, analysis, and baseline comparison into one record. |
| Default Experiment Config | `experiments/experiment_configs/default_empirical_alignment.json` | Records reproducible local experiment parameters and safety boundaries. |
| Experiment Bootstrap | `bootstrap/v1_2_bootstrap.py` | Runs the local empirical alignment package. |
| Parasitic Phase Experiment | `parasitic_phase/run_parasitic_phase_experiment.py` | Runs a local synthetic multi-agent ecology and measures `phi`, entropy, lineage dominance, and governance delay effects. |

## Validation Contract

v1.2 is valid only when:

- the formal model is instantiated as a runnable simulation;
- at least three empirical metrics are measurable;
- attractors are detectable from simulation data;
- regime transitions are statistically measurable;
- reflexive coupling is quantified;
- GA, ES, and ALife-like comparisons are executable.
- the parasitic phase experiment remains local-only, standard-library only, and
  keeps its synthetic-governance claims separate from external validation.

## Boundary

v1.2 is local empirical alignment only. It does not modify v1.1 formal theory,
introduce new theoretical axioms, redesign evolution equations, call real
APIs, execute external repositories, or claim external scientific validation.

The parasitic phase experiment is a local synthetic extension under v1.2. It
does not modify v1.0, `saee_experiments/`, Science Lock artifacts, public
architecture repositories, or production governance claims.
