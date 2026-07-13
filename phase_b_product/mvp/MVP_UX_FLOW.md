# SAEE MVP UX Flow

Status: product UX specification, not implemented UI and not a public product.

## Screen 1: Dashboard

Title:

```text
SAEE Evaluation Dashboard
```

Primary action:

```text
+ Create New Experiment
```

Recent runs:

- `GPT-Agent-v3 vs v2`
- `AutoGen workflow test`
- `RAG policy stress test`

Dashboard cards:

- recent stability score;
- latest collapse-risk flag;
- saved report count;
- scenario pack used.

## Screen 2: Experiment Setup

Title:

```text
Experiment Setup
```

Sections:

### Agents

Controls:

- `Upload Agent A`
- `Upload Agent B`
- `Upload Agent C`

Accepted MVP input types:

- prompt strategy descriptor;
- workflow structure descriptor;
- policy configuration;
- safe metadata file.

Forbidden MVP input types:

- unknown external repositories;
- install scripts;
- secrets;
- production customer data without private deployment review.

### Environment

Controls:

- `Select scenario`
- `Noise level`
- `Adversarial pressure`
- `Time horizon`

### Constraints

Controls:

- cost limit;
- time horizon;
- noise level;
- maximum episode count.

## Screen 3: Running Simulation

Title:

```text
Running Simulation
```

Visible status:

```text
Generation: 1 -> 100
Population: 8 agents
Status: evaluating competition...
```

MVP progress fields:

- current generation or episode;
- evaluated variant count;
- current scenario;
- queued reports;
- estimated completion state.

Boundary:

- do not display kernel internals;
- do not display private fitness or selection logic;
- do not expose runtime orchestration.

## Screen 4: Results

Title:

```text
Results Summary
```

Required sections:

### Stability Ranking

Example:

```text
1. Agent B (stable)
2. Agent A (unstable)
3. Agent C (collapsed)
```

### Failure Modes

Example:

```text
Agent A: drift after 40 steps
Agent C: early collapse
```

### Survival Curve

Chart:

- x-axis: episode or generation;
- y-axis: survival or stability;
- one line per agent or strategy.

### Conclusion

Example:

```text
Best long-term strategy: Agent B
```

## Exportable Report

Required export sections:

- experiment summary;
- scenario configuration;
- stability score;
- survival curve;
- failure modes;
- comparison ranking;
- limitations;
- implementation non-disclosure boundary.

## Current Boundary

```text
ui_implemented: false
frontend_code_created: false
product_launched: false
implementation_disclosed: false
```
