# SAEE Product System Overview

Status: Phase B platform-layer overview, not a product launch.

## Product Framing

SAEE is exposed to product users as a competition-testing and
stability-evaluation platform:

```text
submit scenario context -> run evaluated episodes -> read stability reports
```

The product surface focuses on usability, reporting, and integration boundaries.
It does not publish the private kernel.

## User-Facing Capabilities

- run bounded scenario batches;
- compare AI agent or decision-policy variants;
- review survival ranking, stability score, and collapse-risk summaries;
- inspect stable regime and attractor summaries;
- export benchmark-style reports;
- compare run summaries across configurations;
- preserve reproducibility metadata;
- keep implementation details confidential.

## Non-Goals

- exposing kernel implementation;
- publishing fitness, selection, mutation, or lineage internals;
- executing unknown external repositories;
- running untrusted install scripts;
- expanding permissions automatically;
- claiming open-ended evolution under current constraints.

## Status

```text
product_launch: false
public_sdk_release: false
team_cloud_available: false
private_cloud_available: false
commercial_core_exported: false
implementation_disclosed: false
```
