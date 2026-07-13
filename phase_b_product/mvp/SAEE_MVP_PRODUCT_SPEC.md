# SAEE MVP Product Spec

Status: build-ready product specification, not a launched product and not a
public SDK release.

Generated: 2026-07-03

## Product One-Liner

```text
SAEE = AI Agent / Strategy Long-term Stability Evaluation Platform
```

Chinese product sentence:

```text
SAEE 用来测试你的 AI 系统在长期竞争中会不会崩。
```

Customer-facing English sentence:

```text
We test which AI agents survive long-term competition.
```

## Target Users

### Priority 1: AI Agent Teams

- LangChain, CrewAI, AutoGen, and similar agent-framework users;
- enterprise AI automation teams;
- RAG and workflow system teams.

### Priority 2: Enterprise AI Platform Groups

- internal AI platform teams;
- LLM system owners;
- MLOps and LLMOps teams.

### Priority 3: Research and Advanced Users

- AI researchers;
- system evaluation teams;
- advanced benchmark builders.

## MVP Scope

The MVP has exactly three core capabilities.

### 1. Agent / Strategy Upload

User inputs:

- agent version;
- prompt strategy;
- workflow structure;
- policy configuration.

MVP boundary:

- uploads are treated as abstract strategy descriptors or safe artifacts;
- no unknown external repository execution;
- no install script execution;
- no secrets accepted;
- no private customer data in default demos.

### 2. Long-Term Competition Simulation

System behavior:

- multiple strategies compete across repeated episodes;
- environment perturbations are applied;
- adversarial variation can be simulated;
- output is long-horizon behavior, not a single-run score.

MVP boundary:

- the private core is not exposed;
- users see scenario and report concepts, not kernel internals.

### 3. Evaluation Report

The MVP report must contain four core outputs:

1. `Stability Score`
   - stable convergence;
   - oscillation;
   - collapse risk.

2. `Failure Modes`
   - when failure occurs;
   - why failure is inferred;
   - which environment condition triggered it.

3. `Survival Curve`
   - time-indexed behavior;
   - early strength vs late collapse;
   - persistence across episodes.

4. `Comparison Ranking`
   - multi-agent ranking;
   - best long-term strategy;
   - unstable and collapsed variants.

## Minimum Product Loop

```text
Upload Agents
-> Run Competition
-> Simulate Long Horizon
-> Compute Stability
-> Output Report
```

## Product Architecture

### Evaluation Engine

Responsibilities:

- multi-agent simulation loop;
- competition scheduler;
- scoring system;
- bounded execution policy.

Public boundary:

- expose run status and report outputs only.

Private boundary:

- do not expose kernel, fitness, selection, mutation, lineage, reproduction, or
  runtime internals.

### Scenario Engine

Responsibilities:

- scenario templates;
- environment generator;
- noise injection;
- stress-test configuration.

Public boundary:

- expose scenario names, parameters, and safe presets.

### Metrics Engine

Responsibilities:

- stability score;
- survival curve;
- failure detection;
- ranking system.

Public boundary:

- expose metrics and explanations at report level.

### Trace / Logging System

Responsibilities:

- full run history;
- lineage-like tracking;
- reproducibility metadata.

Public boundary:

- show results and summaries, not lineage construction internals.

### Frontend

Responsibilities:

- experiment dashboard;
- setup flow;
- run progress;
- result dashboard;
- report export.

## Pricing Model

### Free Tier

Purpose:

- acquisition and demos.

Limits:

- 1 agent test;
- limited runs;
- no export.

### Pro Team

Target price band:

```text
99-499 USD / month
```

Features:

- multi-agent testing;
- full reports;
- export;
- scenario packs.

### Enterprise

Target price band:

```text
20k-200k USD / year
```

Features:

- private deployment;
- custom scenarios;
- internal model testing;
- audit logs;
- support and onboarding.

## Competitive Position

| Product | Primary category | SAEE difference |
| --- | --- | --- |
| LangSmith | trace and debugging | long-term competition and stability analysis |
| Arize | monitoring | multi-agent long-horizon behavior evaluation |
| Humanloop | prompt evaluation | competitive survival and collapse-risk reporting |
| QuantConnect | trading simulation | AI-agent and strategy stability evaluation first |

## Words to Avoid

Do not lead with:

- evolution engine;
- simulation system;
- research platform;
- phase diagram;
- scientific closure;
- open-ended evolution.

## Words to Use

Lead with:

- long-term stability evaluation;
- agent competition testing;
- failure-mode discovery;
- survival curve;
- collapse-risk report;
- comparison ranking.

## Current Boundary

```text
mvp_product_spec_created: true
product_launched: false
public_sdk_release: false
customer_contacted: false
private_core_exported: false
implementation_disclosed: false
kernel_modified_by_mvp: false
runtime_modified_by_mvp: false
```
