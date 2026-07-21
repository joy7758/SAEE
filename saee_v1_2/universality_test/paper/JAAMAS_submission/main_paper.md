# A Synthetic Benchmark for Parasitic Transition Patterns in Multi-Agent Systems

agent_readable:
  schema: saee.jaamas_submission.main_paper.v2
  target_venue: JAAMAS
  artifact_type: manuscript_draft
  paper_line_status: frozen_closed_after_editorial_reject
  external_resubmission_allowed: false
  title_only_reframe_allowed: false
  successor_route_allowed: false
  reuse_scope: local_evidence_only
  freeze_record: saee_v1_2/universality_test/submission/PAPER_LINE_FREEZE.md
  experimental_code_modified: false
  simulations_rerun_for_this_package: false
  real_world_deployment_claim: false
  broad_theory_claim: false
  production_claim: false
  canonical_claim: empirically observed cross-system consistency within a shared synthetic multi-agent modeling framework

## Post-Decision Freeze

This manuscript line is closed and frozen. The JAAMAS submission was rejected
on 2026-07-17, and the manuscript shares its research lineage with an active
SAEE scientific submission. It must not be resubmitted, transferred, retitled
as a new paper, or used to open a successor manuscript route. The DBI code,
results, and figures remain available as local historical evidence only.

Canonical freeze record:

```text
saee_v1_2/universality_test/submission/PAPER_LINE_FREEZE.md
```

## Abstract

In the tested synthetic multi-agent systems, local reward adaptation, resource
competition, and replication pressure can be associated with an observable
transition from a distributed regime to a more concentrated regime. We introduce
a controlled synthetic benchmark that measures this behavior across three
Digital Biosphere Instances (DBIs) with distinct resource, policy, and
interaction dynamics. The benchmark uses `Phi in [0, 1]` as an operational
transition indicator combining resource concentration, reward or policy drift,
and lineage dominance, with entropy and dominance reported as supporting
observables. Under no governance, transition probabilities are `0.933333` in
DBI-1, `1.0` in DBI-2, and `0.886111` in DBI-3; DBI-3 introduces a distinct
interaction topology that reduces transition alignment while preserving
qualitative phase structure. Ablations, random-weight controls, sensitivity
tests, and structural analog baselines indicate that the observed pattern is
robust under tested conditions but not uniquely explained by `Phi`. We report
empirically observed cross-system consistency within a shared synthetic
multi-agent modeling framework, with architecture-dependent governance response.
The manuscript does not claim a universality class, a general law, or real-world
deployment validity.

## 1. Introduction

Adaptive multi-agent systems are usually studied through equilibria,
incentives, or coordination mechanisms. This paper studies a complementary
question: whether local gain amplification can produce a measurable transition
from a distributed regime to a concentrated, low-diversity regime in synthetic
multi-agent systems.

The contribution is a benchmark, not a deployment claim. We construct three
DBI systems, measure a bounded macrostate variable `Phi`, test no/weak/strong
governance intervention policies, and compare the observed pattern against
ablation and structural analog baselines. The paper is intentionally
claim-limited: it reports empirically observed cross-system consistency within a
shared synthetic multi-agent modeling framework, not a broad theory over all
multi-agent systems.

## 2. Method

### 2.1 Benchmark Systems

The benchmark contains three DBIs:

| System | Distinguishing mechanism |
|---|---|
| DBI-1 | finite global resource pool with cooperative, selfish, and reward-mutating agents |
| DBI-2 | heterogeneous resource topology with randomized policy vectors and small-world interactions |
| DBI-3 | graph-local public-goods imitation network with ER/WS/BA topology presets |

DBI-3 introduces a distinct interaction topology that reduces transition
alignment while preserving qualitative phase structure.

### 2.2 Canonical Measurement

At timestep `t`, the benchmark computes:

```text
Phi(t) = alpha RC(t) + beta RD(t) + gamma AD(t)
```

where `RC` is resource concentration, `RD` is reward or policy drift, `AD` is
lineage dominance, and `alpha + beta + gamma = 1`. The experiments use:

```text
alpha = 0.35
beta = 0.35
gamma = 0.30
Phi_c = 0.60
```

A transition event is detected when:

```text
Phi(t) > Phi_c and Phi(t) - Phi(t - 1) > epsilon
```

`Phi` is one of several valid transition indicators that capture the observed
regime change. It is not claimed to be unique. Entropy and dominance curves
provide supporting observables.

### 2.3 Governance Intervention

Governance is implemented as an intervention policy over replication caps,
monopoly penalties, and reward or policy drift damping. We evaluate no, weak,
and strong regimes. This is an empirical intervention policy, not a
control-theoretic guarantee.

## 3. Results

### 3.1 Transition Pattern Across DBIs

No-governance transition probabilities are:

| System | Transition probability | Notes |
|---|---:|---|
| DBI-1 | `0.933333` | finite-resource ecology |
| DBI-2 | `1.0` | heterogeneous resource topology |
| DBI-3 | `0.886111` | public-goods imitation network |

DBI-3 lowers transition alignment relative to DBI-1 and DBI-2, which is a
finding rather than a failure: the qualitative pattern persists under a
different micro-dynamic regime.

This is a negative-result boundary condition for the benchmark. DBI-3 introduces
a distinct interaction topology that reduces transition alignment while
preserving qualitative phase structure. The result weakens strong cross-system
consistency claims and motivates the conservative framing used throughout this
manuscript.

### 3.2 Governance Response

Governance response is architecture-dependent:

| System | None | Weak | Strong |
|---|---:|---:|---:|
| DBI-1 | `0.933333` | `0.8` | `0.0` |
| DBI-2 | `1.0` | `1.0` | `1.0` |
| DBI-3 | `0.886111` | `0.533333` | `0.0` |

The tested systems support the same conservative interpretation: transition
emergence is empirically observed across DBIs, while suppression by governance
is architecture-dependent.

### 3.3 Phi Stress Tests

The full `Phi` ablation suite gives transition probabilities:

```text
DBI-1: 0.95
DBI-2: 1.0
DBI-3: 0.733333
```

This reduces the risk that `Phi` is arbitrary, but it does not prove uniqueness
or necessity.
Sensitivity analysis reports robustness scores of `0.913426` for DBI-1,
`0.99838` for DBI-2, and `0.828318` for DBI-3.

### 3.4 Structural Analog Baselines

The baseline suite includes MARL-lite public goods, bond percolation, and SIR
epidemic models. Percolation and SIR are structural analog baselines for
contextualization rather than direct competitors or superiority tests.
Classical models such as percolation and SIR also exhibit transition behavior,
but under different generative mechanisms.

## 4. Discussion

The benchmark supports a claim-minimal conclusion: empirically observed
cross-system consistency within a shared synthetic multi-agent modeling
framework. DBI-3 is especially important because it weakens any
strong-consistency narrative while preserving the qualitative structure of the
transition. The presented results do not establish a claim beyond the tested
synthetic family. DBI-1, DBI-2, and DBI-3 remain members of a shared synthetic
agent-based modeling family. The contribution is therefore a
stress-tested benchmark for cross-system consistency under this modeling family,
not a proof beyond the tested family.

The governance result should also be read conservatively. Governance can shift
or suppress transitions in some architectures, but it does not provide a
control guarantee. The paper does not claim real-world deployment validity,
production readiness, or theoretical completeness.

The scope is limited to synthetic environments, post-hoc sensitivity analysis,
and sampled parameter settings. The results should not be read as evidence of
real-world deployment validity, production governance readiness, or complete
coverage of multi-agent system architectures.

## 5. Limitations

- Synthetic systems only.
- Three DBI architectures, not exhaustive model coverage.
- `Phi` is an operational transition indicator and is non-unique.
- Governance is an intervention policy, not a certified controller.
- Structural analog baselines show related transition behavior under different
  mechanisms.

## 6. Reproducibility

Primary evidence surfaces:

- `saee_v1_2/universality_test/results/dbi3/dbi3_summary.json`
- `saee_v1_2/universality_test/results/phi_ablation/phi_ablation_summary.json`
- `saee_v1_2/universality_test/results/baselines/baseline_suite_summary.json`
- `saee_v1_2/universality_test/results/statistics_upgrade/statistical_upgrade_summary.json`
- `saee_v1_2/universality_test/results/reviewer_proofing_manifest.json`

Submission boundary:

```text
synthetic_validated: true
real_world_validated: false
broad_theory_claim: false
production_ready: false
```
