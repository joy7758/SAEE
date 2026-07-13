# Open-Ended Physics Model

## Purpose

v0.5 models generated evolution physics. It does not choose from fixed fitness
types, selection topology names, mutation operator lists, or dimension sets.
Instead, each generation produces machine-readable physics records from local
observations.

## Generated Records

| Record | Output | Generated from |
| --- | --- | --- |
| Evolution law | `generated_laws.json` | Novelty tokens, lineage span, active dimensions, phase signals. |
| Fitness function | `generated_fitness_functions.json` | Generated law clauses and current dimensions. |
| Selection mechanism | `selection_mechanisms.json` | Law, generated fitness function, and observation signature. |
| Dimension state | `dimensions.json` | Novel tokens and collapse pressure. |
| Regime | `regimes.json` | Law, dimensions, and phase emergence. |
| Hypergraph | `hyper_graph.json` | All generated physics objects and their causal edges. |

## No Fixed Evolution-Space Assumptions

The runtime starts from a seed genome but does not preserve a fixed dimension
list. Dimension identifiers are born from runtime token signatures. Dimension
events can include:

- `dimension_birth`
- `dimension_merge`
- `dimension_collapse`

## No Fixed Fitness Function Structure

Fitness functions are emitted as expression-term records:

```json
{
  "fitness_function_id": "fitness_g001_...",
  "source_law": "law_g001_...",
  "expression_terms": [
    {
      "term_id": "term_...",
      "dimension_id": "dim_...",
      "coefficient": 0.42,
      "measurement": "trait_overlap::runtime_token"
    }
  ]
}
```

The expression terms change when dimensions and laws change.

## No Fixed Selection Topology Types

Selection mechanisms are generated entities:

```json
{
  "mechanism_id": "selection_g002_...",
  "parents": ["selection_g001_..."],
  "mutation_record": {
    "is_reproduction": true
  },
  "pressure_expression": {}
}
```

The mechanism can reproduce and mutate. It is not selected from a predefined
topology enum.

## Boundary

The physics model is local-only. Open-ended structure generation does not grant
new permissions, call real APIs, execute external repositories, or copy external
code into genome state.
