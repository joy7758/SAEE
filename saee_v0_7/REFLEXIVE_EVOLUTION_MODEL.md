# Reflexive Evolution Model

## Purpose

v0.7 turns explanation into evolutionary pressure. Explanation is no longer
post-hoc. Meaning feedback and self-model state are read before mutation,
epistemic fitness, and semantic selection.

## Causal Flow

```text
self-description from generation n
-> meaning_feedback for generation n+1
-> mutation_probability and epistemic_fitness
-> semantic_selection
-> interpretation_influenced_lineage
-> updated self_model
```

## Reflexive Mutation

The mutation engine emits:

- `feedback_input_id`
- `explanation_quality`
- `semantic_coherence`
- `mutation_probability`
- `self_model_id`

Poor explanation quality increases mutation probability. High explanation
quality with high semantic coherence can create `semantic_stabilization` events.

## Epistemic Fitness

Epistemic fitness combines:

- generated base fitness;
- explanation quality;
- semantic coherence;
- self-model alignment.

This means understanding quality can change survival outcome.

## Semantic Selection

Semantic selection ranks genomes with:

- epistemic score;
- meaning coherence;
- self-model alignment;
- inconsistency penalty.

The output records whether epistemic pressure changed the survival set.

## Boundary

Reflexivity changes local simulation pressure only. It does not create external
agency, expand permissions, call APIs, execute repositories, or claim
self-awareness.
