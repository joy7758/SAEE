# Capability Map

Status: product-facing abstraction map.

## Included Capabilities

| Capability | Public Surface | Boundary |
| --- | --- | --- |
| Bounded run request | SDK abstraction | No kernel disclosure |
| Phase-space summary | Report abstraction | Aggregate labels only |
| Stability summary | Report abstraction | No fitness internals |
| Collapse event summary | Report abstraction | Counts only |
| Survival ranking | Report abstraction | Ranking only, no private selection procedure |
| Robustness comparison | Report abstraction | Comparison output only |
| Regression report | Report abstraction | No runtime internals |
| Policy tournament | Scenario abstraction | No private mutation or reproduction logic |
| Lineage summary | Report abstraction | No lineage construction internals |
| Academic-safe export | Documentation layer | No source code |
| Reproducibility metadata | Metadata layer | No private orchestration |

## Excluded Capabilities

| Excluded Item | Reason |
| --- | --- |
| Kernel source | Private core |
| Runtime orchestration | Private core |
| Fitness logic | Commercial confidentiality |
| Selection logic | Commercial confidentiality |
| Mutation logic | Commercial confidentiality |
| Reproduction logic | Commercial confidentiality |
| Lineage internals | Commercial confidentiality |
| External repository execution | Safety boundary |

## Product Principle

```text
Expose what users can request and read.
Do not expose how the core produces it.
```

## Commercial Wedge

```text
primary_wedge: AI agent evaluation and policy stress testing
product_identity: competition-testing and stability-evaluation platform
commercial_lock_active: true
```
