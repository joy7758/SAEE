# Observability Model

## Purpose

v0.6 turns generated evolution physics into observable evolution physics. It
does not add new mechanics. It adds causality, semantic lineage, explanation,
and observer feedback over v0.5 run records.

## Observation Contract

Every cycle creates an `observation_event` with:

- `cause_chain`
- `semantic_claim`
- `rule_birth`
- `mutation_causes`
- `dimension_causes`
- `selection_causes`

## Reverse Mapping

Outcome-to-cause reconstruction maps:

```text
genome outcome
-> fitness explanation
-> selection mechanism
-> generated fitness function
-> generated law
-> observation event
```

## Semantic Lineage

The semantic lineage graph adds meaning-level nodes and edges:

- `semantic_generation_state`
- `fitness_selection_meaning`
- `cause_of`
- `meaning_of_rule`
- `meaning_transition`

This is not only a structural DAG. It records why transitions mattered.

## Counter-Observer Loop

The observer loop records second-order feedback:

```text
observation event -> self-description -> observer state -> next observation context
```

The feedback is observability state only. It does not introduce new mutation
types or selection mechanisms.
