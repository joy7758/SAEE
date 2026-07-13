# Evolution Space Model

## Purpose

v0.4 treats the space where evolution happens as a mutable system object. The
runtime does not only change genomes or rule weights; it changes dimensions,
fitness geometry, selection topology, and mutation operator modes.

## Agent-Readable Contract

The current state is emitted as `evolution_space.json`:

```json
{
  "space_id": "evolution_space_v0_4_g001_diversification",
  "version": 1,
  "dimensions": {
    "technical": {"weight": 0.2, "active": true},
    "market": {"weight": 0.16, "active": true}
  },
  "geometry_type": "multi_niche_manifold",
  "selection_topology": "niche_graph",
  "mutation_operator_mode": "recombination_expansion",
  "history": []
}
```

## Mutable Fields

| Field | Meaning | Mutation source |
| --- | --- | --- |
| `dimensions` | Active fitness axes and weights. | Regime-specific evolution-space mutation. |
| `geometry_type` | Shape used by the fitness geometry layer. | Phase and regime. |
| `selection_topology` | Structural selection method. | Phase and regime. |
| `mutation_operator_mode` | Active mutation operator family. | Phase and regime. |
| `history` | Evolution-space mutation events. | Runtime loop. |

## Supported Geometry Types

Fitness Geometry is represented by one of these geometry structures:

| Geometry | Role |
| --- | --- |
| `weighted_manifold` | Optimization and local refinement. |
| `expanding_simplex` | Exploration under divergent pressure. |
| `multi_niche_manifold` | Diversification when niches emerge. |
| `stability_basin` | Collapse/reset under safety and cost pressure. |

## Supported Selection Topologies

| Topology | Role |
| --- | --- |
| `graph_competition` | Parent-lineage-aware local competition. |
| `pressure_field` | Environment-pressure-driven selection. |
| `niche_graph` | Preserve representatives across niches. |
| `competition_field` | Stronger extinction under collapse pressure. |

## Supported Mutation Operator Modes

| Mode | Operators |
| --- | --- |
| `local_refinement` | `trait_shift`, `threshold_adjustment` |
| `operator_discovery` | `trait_shift`, `niche_split`, `novel_operator_seed` |
| `recombination_expansion` | `recombination`, `niche_split`, `cross_niche_bridge` |
| `conservative_repair` | `threshold_adjustment`, `stability_repair` |

## Boundary

Evolution-space mutation changes local simulation structure only. It does not
grant new permissions, call real APIs, run external repositories, or copy
external code into genome state.
