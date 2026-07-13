# SAEE IP Protection Strategy

Status: local strategic release plan, not legal advice and not a release event.

## Strategic Objective

Occupy SAEE's theory definition surface while preserving the implementation
core as private commercial IP.

## Current Commercial Lock

SAEE's current commercial identity is:

```text
competition-testing and stability evaluation for AI agents and decision policies
```

The Zenodo definition-only object is public. The commercial core remains
private.

## Disclosure Strategy

### Academic Layer

Goal: establish naming, framing, observed results, and candidate law language.

Vehicle: `zenodo_release/`

Allowed disclosure:

- what SAEE means;
- what was observed;
- what candidate laws were extracted;
- why claims are bounded.

Protected:

- how the core runtime works.

### GitHub Layer

Goal: provide discoverable public entry points without releasing the core.

Vehicle: `github_release/`

Allowed disclosure:

- toy demo;
- stubs;
- public-safe interfaces;
- educational abstraction.

Protected:

- real evolution engine;
- real scoring and selection implementation;
- real lineage and mutation internals.

### Commercial Layer

Goal: preserve control over the engine and future productization.

Vehicle: `saee_core_private/`

Protected:

- v1.0 kernel;
- fitness computation logic;
- selection mechanism;
- lineage optimization;
- mutation/reproduction engine;
- runtime orchestration.

## Release Preconditions

Before any real Zenodo or GitHub publication:

1. Manual review of all files in `zenodo_release/`.
2. Manual review of all files in `github_release/`.
3. Confirm no private imports or copied implementation logic.
4. Confirm license choice for public subset.
5. Confirm authorship and ownership metadata.
6. Confirm that no DOI, release, upload, or publication claim is written before
   the external action actually happens.

## Current Boundary

```text
zenodo_uploaded: true
zenodo_doi: 10.5281/zenodo.21135472
github_released: false
core_exported: false
private_code_copied: false
doi_assigned: true
product_launched: false
customer_contacted: false
implementation_disclosed: false
```
