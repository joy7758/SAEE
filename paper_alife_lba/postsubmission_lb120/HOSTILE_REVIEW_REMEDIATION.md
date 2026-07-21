# lb120 Hostile-review Remediation Record

Status: `local_paper_layer_remediation_complete`

This record converts the supplied hostile-review report into repository-backed
clarifications. It does not assert that reviewers raised these points and does
not represent an actual rebuttal submission.

## Disposition summary

| Review risk | Disposition | Evidence surface |
|---|---|---|
| Novelty unclear | Narrowed to a local observation and characterization protocol; no solver-superiority or universal-theory claim | `NOVELTY_AND_RELATED_WORK.md` |
| Operational definitions weak | Replaced generic placeholders with exact implemented rules | `OPERATIONAL_DEFINITIONS.md` |
| Single trajectory overinterpreted | Explicitly bounded to the observed artifacts; no cross-seed, cross-parameter, or cross-substrate inference | All support files |
| Attractor/regime claim too strong | Downgraded to an empirical discrete-signature recurrence and ordered rule-based label | `OPERATIONAL_DEFINITIONS.md` |
| `808/1590` accounting unclear | Corrected to 808 DAG nodes and 1590 directed edges | `OPERATIONAL_DEFINITIONS.md` |
| Provenance incomplete | Added hashes and paths; unknown provenance remains explicit | `SUPPLEMENT_lb120_METHODS.md` |
| Venue fit unclear | Mapped only to official ALIFE topics that the local object actually supports | `NOVELTY_AND_RELATED_WORK.md` |
| Submitted-version truth conflict | Recorded `no portal submission` as a frozen-text inconsistency; did not rewrite the uploaded PDF | `SUBMITTED_ARTIFACT_MANIFEST.json` |

## Corrections to the supplied generic report

### Lineage accounting

The suggested prose "808 retained unique nodes out of 1590 recorded lineage
events" is not supported by the implementation. The actual report generator
computes:

```text
node_count = len(lineage_dag.nodes) = 808
edge_count = len(lineage_dag.edges) = 1590
branching_density = edge_count / node_count = 1.967822
```

No event-to-node deduplication rule is present in this accounting surface.

### Attractor detection

The supplied window, distance, clustering, dominance, and recurrence template
does not match the code. Phase II creates a categorical state signature at each
generation and calls any signature with support count at least two an attractor
candidate. The reported signature occurs at generations 1--6.

### Regime stability

The implementation does not assign regimes over sliding windows. It applies an
ordered point classifier. In the current Phase II artifact, all six points are
`stable_regime`, producing zero cross-regime changes. The phase-diagram
projection then counts five consecutive `stable_regime -> stable_regime`
self-transitions. This local ratio must not be presented as a general transition
probability.

### Random seed and environment

`deterministic_seed: enabled` is a mode flag, not a recorded numeric random
seed. The v1.0 implementation uses deterministic SHA-256-derived identifiers
and deterministic weight shifts. The original execution OS, Python version,
package lock, hardware, exact command, and execution commit are not recorded in
the current artifacts. The present workstation environment is not substituted
for those unknowns.

## Remaining reviewer-visible weaknesses

The hardening reduces ambiguity but cannot create evidence that the run never
contained:

- one long-horizon run is not a distribution over seeds or configurations;
- a six-generation repeated categorical signature is a weak empirical
  attractor indicator, not a formal dynamical-systems proof;
- `lineage_integrity_preserved` checks the declared `lineage_dag` type and edge
  endpoint existence but does not independently perform a topological cycle
  test in the reporting function;
- no MODES, phylogenetic-richness, or other published open-ended-evolution
  metric is reported;
- the original execution commit and environment are not reconstructable from
  the current artifact set alone.

These are declared limitations, not silently repaired claims.
