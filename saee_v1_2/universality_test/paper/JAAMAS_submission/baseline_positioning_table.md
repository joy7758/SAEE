# Baseline Positioning Table

agent_readable:
  schema: saee.jaamas_submission.baseline_positioning.v1
  target_venue: JAAMAS
  artifact_type: baseline_boundary_table
  experimental_code_modified: false
  simulations_rerun_for_this_package: false
  results_files_modified: false
  real_world_deployment_claim: false
  production_claim: false
  broad_theory_claim: false
  canonical_claim: empirically observed cross-system consistency within a shared synthetic multi-agent modeling framework

## Purpose

The baseline suite is used for positioning and contextualization. It is not a
claim of superiority over classical transition models.

| System or baseline | Role in submission | Generative mechanism | What it supports | What it does not support |
|---|---|---|---|---|
| DBI-1 | Primary synthetic benchmark system | finite resource pool, replication, cooperative/selfish/mutating agents | transition pattern under resource competition and reward drift | model-independent generality |
| DBI-2 | Independent synthetic DBI variant | heterogeneous resource topology and small-world interaction | cross-system consistency within the shared DBI family | proof across unrelated architectures |
| DBI-3 | Stress-test DBI variant | public-goods imitation network with graph topology presets | qualitative persistence with weaker alignment | strong uniformity across all DBIs |
| MARL-lite | Structural analog baseline | simplified public-goods learning dynamics | comparison to a lightweight multi-agent baseline | replacement for full MARL evaluation |
| Bond percolation | Classical structural analog | connectivity threshold process | transition behavior can arise in non-agent threshold systems | direct competition with DBI mechanisms |
| SIR epidemic | Classical structural analog | susceptible-infected-recovered state dynamics | transition behavior can arise from contagion dynamics | evidence that DBI transitions are epidemiological |

## Required Manuscript Wording

```text
Percolation, SIR, and MARL-lite baselines are included as structural analogs
for contextualization rather than as direct competitors or superiority tests.
Classical models such as percolation and SIR also exhibit transition behavior,
but under different generative mechanisms.
```
