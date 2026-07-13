# SAEE Revised Commercial Plan

Status: internal commercial strategy, not a public launch, not legal advice,
and not an independently verified market report.

Sequencing note: this 2026-07-03 plan is retained as historical commercial
context. `docs/strategy/SAEE_AGENT_NATIVE_COMMERCIAL_LOGIC_V2.md` now controls
discovery and validation order: Agent-Native Packaging, Machine
Discoverability, Tool Capability, and External Agent Recommendation precede
Human Design Partner validation. Historical product and market hypotheses below
do not override that active route.

Generated: 2026-07-03

## Source Boundary

This plan distills the user-supplied benchmarking brief:

```text
<private-attachment>/eafc4a75-a8c9-4c9f-b7d8-3bae296d5ed7/pasted-text.txt
```

The brief benchmarks adjacent simulation, optimization, AI evaluation, and
quant infrastructure vendors. This repository records the commercial
implications only. Vendor pricing, deployment options, adoption claims, and
market facts from the brief are not independently reverified in this change.

## Commercial Thesis

SAEE should not launch as a generic strategy evolution engine for everyone.

The first commercial identity should be:

```text
SAEE is a competition-testing and stability-evaluation platform for AI agents
and decision policies.
```

The commercial value is not the engine by itself. The value is the workflow
around the engine:

- scenario setup;
- repeated competitive runs;
- evaluated episodes;
- robustness ranking;
- collapse-risk analysis;
- stability scorecards;
- experiment history;
- exportable benchmark reports;
- private deployment for sensitive customer data.

## Market Order

### Wedge 1: AI Agent Evaluation and Policy Stress Testing

Primary first market:

```text
AI agent teams and central AI platform groups
```

Why this is the first wedge:

- these buyers already budget for evaluation and observability;
- they care about robustness, regressions, failure modes, and long-horizon
  behavior;
- they understand traces, runs, reports, retention, seats, and private
  deployment;
- SAEE's strengths map naturally to repeated simulation, stability ranking,
  and policy failure discovery.

### Wedge 2: Enterprise Decision-Policy Simulation

Second market:

```text
narrow domain templates for enterprise decision policies
```

Candidate solution-pack domains:

- customer-support agent tournaments;
- RAG policy stress tests;
- workflow-automation failure simulations;
- fraud-operations policy competition;
- pricing or promotion policy stability tests.

This wedge should start only after the AI-agent evaluation workflow has
repeatable templates, reports, and service delivery patterns.

### Wedge 3: Quant Trading Infrastructure

Later market:

```text
quant trading and investment strategy testing
```

This should not be the first wedge. Quant buyers expect an end-to-end stack:
local/cloud research workflow, datasets, backtesting, optimization, live
trading path, broker integrations, encryption, controls, and institution-grade
deployment. SAEE should enter this area only after partnerships or workflow
depth close that gap.

## Product Layers

### 1. SAEE Sandbox

Purpose:

- free or academic entry point;
- synthetic-data-first demos;
- capped scenario length;
- capped exports;
- adoption, education, and design-partner lead generation.

Boundary:

- no private kernel disclosure;
- no customer-sensitive data default;
- no production claim.

### 2. SAEE Team Cloud

Purpose:

- first paid product for AI teams;
- managed workspace with seats plus usage;
- scenario batch runs and retained reports.

Expected user-visible outputs:

- survival ranking;
- stability score;
- collapse-risk summary;
- robustness comparison;
- regression report;
- exportable benchmark report.

Boundary:

- expose request, run, report, and retention concepts;
- do not expose fitness, selection, mutation, lineage, or runtime internals.

### 3. SAEE Enterprise Private Cloud

Purpose:

- high-value serious-buyer tier;
- VPC or self-hosted deployment;
- private data and regulated workflow support.

Expected controls:

- SSO/SAML;
- RBAC;
- custom retention;
- audit logs;
- data-region controls;
- encryption;
- benchmark sharing controls;
- service-level support.

Boundary:

- private core remains controlled by SAEE owner;
- customer deployment does not imply open-source kernel disclosure.

### 4. SAEE Solution Packs

Purpose:

- make the platform buyable through concrete workflows;
- package templates without creating new kernels.

Examples:

- support-agent competition pack;
- RAG regression and stress-test pack;
- workflow automation collapse-risk pack;
- enterprise policy tournament pack.

Boundary:

- solution packs are domain workflows, not kernel forks.

## Pricing Logic

Recommended commercial structure:

```text
Sandbox: free or academic/non-commercial
Team Cloud: seat-plus-usage or workspace-plus-usage
Enterprise Private Cloud: annual custom contract
Services: paid pilot, onboarding, and custom scenario-pack work
```

Avoid using a low flat subscription as the main commercial anchor. If a
sub-100 USD tier exists, treat it as education, hobby, or sandbox access, not
as the core enterprise product.

Customer-facing billing units should be:

- scenario runs;
- evaluated episodes;
- saved benchmark reports;
- retention window;
- team seats;
- deployment tier.

Avoid exposing internal engineering units such as population size or raw
simulation steps as the primary buyer-facing price metric.

## Go-To-Market Motion

Start with design partners, not mass-market self-serve.

Pilot offers should answer concrete customer questions:

- Which agent design survives longer under competitive load?
- Which workflow remains stable when environment rules change?
- Which version regresses under adversarial policies?
- Which decision policy has lower collapse risk over repeated scenarios?

Content should be benchmark-style rather than theory-first:

- tournament reports;
- robustness scorecards;
- collapse-risk examples;
- before/after regression reports;
- limited case studies with no private kernel disclosure.

Partner strategy should be considered early for assessment, proof-of-concept,
implementation, training, and solution-pack delivery.

## Commercial Lock Rule

The commercial core remains private.

Protected content classes:

- SAEE v1.0 kernel;
- fitness computation logic;
- selection mechanism;
- mutation and reproduction engine;
- lineage internals;
- runtime orchestration;
- private deployment automation;
- customer-specific scenario packs before explicit release approval.

Allowed public content classes:

- Zenodo definition-only scientific object;
- conceptual product language;
- toy abstraction demos;
- public-safe schemas and request/response examples;
- report screenshots or synthetic benchmark examples after review.

## Current Action Boundary

```text
commercial_strategy_recorded: true
product_launched: false
customer_contacted: false
github_release_created: false
private_core_exported: false
kernel_modified: false
runtime_modified: false
implementation_disclosed: false
market_claims_independently_verified_in_this_change: false
```
