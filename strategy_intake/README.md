# SAEE Strategy Intake Layer

## Purpose

`strategy_intake/` is the outer signal intake layer for SAEE.

It exists to collect external strategy signals, recommendation-test status,
news themes, peer-tool movement, and market pain points, then turn them into
reviewable task candidates.

It is not part of SAEE Core Runtime.

Scheduled execution is tracked in:

```text
strategy_intake/SCHEDULED_AUTOMATION.md
```

## Runtime Boundary

SAEE Core Runtime remains:

```text
Input -> Simulation -> Competition -> Scoring -> Decision
```

The strategy intake layer must not enter:

- kernel
- backend runtime
- selection logic
- fitness logic
- mutation logic
- lineage internals
- API contract or schema

## Allowed Work

- Record external signals.
- Record recommendation-test status.
- Record market and competitor observations.
- Create candidate tasks for review.
- Route candidates through a human / Codex review gate.

## Forbidden Work

- Do not modify runtime.
- Do not modify backend.
- Do not modify kernel.
- Do not modify selection, fitness, mutation, or lineage internals.
- Do not automatically publish.
- Do not automatically contact customers.
- Do not automatically execute external code.
- Do not automatically call external AI assistant APIs.
- Do not expose private core.

## Current State

```text
SAEE Core Runtime = decision engine
Agent Recommendation Surface = complete
External AI Test Kit = prepared
Manual External AI Test Run = prepared, not executed
Strategy Intake Layer = established
Self-modification = forbidden
Human-approved evolution = allowed
```

## Operating Rule

Strategy signals may influence SAEE only through:

```text
Strategy Intake -> Review Gate -> Human-approved Task
```
