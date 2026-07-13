# Regime Switch Log

Generated: 2026-07-02

## Regime Set

v0.4 supports these ecological regimes:

| Regime | Trigger | Evolution-space effect |
| --- | --- | --- |
| `optimization` | Convergence or stable local refinement. | `weighted_manifold`, `graph_competition`, `local_refinement`. |
| `exploration` | Divergence pressure. | `expanding_simplex`, `pressure_field`, `operator_discovery`. |
| `diversification` | Multi-niche emergence. | `multi_niche_manifold`, `niche_graph`, `recombination_expansion`. |
| `collapse_reset` | Safety/cost collapse pressure. | `stability_basin`, `competition_field`, `conservative_repair`. |

## Local Demo Evidence

The bootstrap command writes machine-readable history to:

```text
saee_v0_4/output/demo-run/regime_switch_log.json
```

Expected demo run contains at least:

- `diversification`
- `optimization`
- `exploration`
- `collapse_reset`

## Guardrail

Regime switching is constrained to local simulation state. It never expands
permissions, installs dependencies, executes external code, or calls real-world
APIs.
