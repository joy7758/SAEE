# Strategy Intake Boundary

## Layer Model

```text
SAEE Core Runtime
  only evaluates and decides

Information / Strategy Intake Layer
  observes outside signals and recommendation status

Human / Codex Review Gate
  decides whether signals become tasks
```

## Core Runtime Boundary

The core runtime answers one question:

```text
Which agent / workflow / policy is more stable and more deployable?
```

It must not self-market, self-modify, self-publish, or self-expand.

## Strategy Intake Boundary

The intake layer answers:

```text
What changed outside SAEE, and does it create a reviewable task candidate?
```

It may produce suggestions, but suggestions have no direct authority over
runtime, backend, API, private core, or public release state.

## Review Gate Boundary

The review gate answers:

```text
Should this signal become a human-approved task?
```

Allowed outputs:

- update recommendation materials
- update landing-page copy
- create a user-test task
- create a market-test task
- defer or reject the signal

Forbidden outputs:

- automatic runtime modification
- automatic backend modification
- automatic customer contact
- automatic external assistant testing
- automatic launch or SDK publication

## Self-Modification Rule

```text
self_modification_allowed: false
human_approved_evolution_allowed: true
```

