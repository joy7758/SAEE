# SAEE Confidentiality Boundary Map

Status: local boundary map, not a release event.

Rule: Never mix layers.

Current commercial lock:

```text
academic_definition_public: true
zenodo_doi: 10.5281/zenodo.21135472
commercial_core_private: true
product_launch: false
implementation_disclosed: false
```

## Layer Model

```text
Academic Layer = knowledge
GitHub Layer   = abstraction
Core Layer     = intellectual property
```

## Layer 1: Zenodo Academic Package

Path:

```text
zenodo_release/
```

Allowed content:

- theory definitions;
- phase diagram summary;
- aggregate results;
- candidate laws;
- non-claims.

Forbidden content:

- implementation code;
- runtime orchestration;
- private scoring, selection, lineage, mutation, or reproduction details.

## Layer 2: GitHub Public Subset

Path:

```text
github_release/
```

Allowed content:

- toy demo;
- stubs;
- simple JSONL logging helper;
- public-safe regime and attractor abstraction.

Forbidden content:

- imports from private runtime;
- SAEE kernel implementation;
- proprietary fitness or selection logic;
- lineage optimization;
- mutation/reproduction implementation.

## Layer 3: Private Commercial Core

Path:

```text
saee_core_private/
```

Protected content classes:

- kernel;
- fitness engine;
- selection engine;
- lineage engine;
- mutation engine;
- v1.0 runtime;
- future commercial implementation details.

## Layer 4: Commercial Product Interface

Path:

```text
phase_b_product/
```

Allowed content:

- scenario request concepts;
- evaluated episode summaries;
- stability score summaries;
- collapse-risk summaries;
- survival ranking output shapes;
- product-safe benchmark report shapes.

Forbidden content:

- source implementation for the core;
- private deployment automation;
- real customer traces, policies, or data;
- private benchmark reports;
- claims of product launch, private-cloud readiness, customer adoption, or
  benchmark superiority.

## Cross-Contamination Checks

Required before any actual release:

```bash
rg -n "saee_v1_0|fitness|selection|lineage|mutation|runtime" zenodo_release github_release
python3 github_release/demo/minimal_evolution_demo.py
python3 scripts/mainline_guard.py
```

Review any hit manually. Descriptive boundary hits are allowed only when they
state non-disclosure rules. Implementation imports or copied code are not
allowed.
