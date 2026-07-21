# SAEE lb120 Review-response Notes

Status: `author_preparation_only`

No reviewer comments have been received in this repository. This document is a
prepared response surface, not a rebuttal that has been sent.

## Overall boundary

Thank you for examining the scope and measurement clarity of this Late-Breaking
Abstract. The submission reports a local, single-artifact characterization of a
frozen reflexive evolutionary software object. No post-submission experiment,
result change, theory change, runtime change, kernel change, candidate-law
change, or GSP semantic change is introduced. The clarification materials only
make the existing artifact-to-claim mapping explicit.

## If novelty is challenged

We do not claim a new universal evolutionary theory or algorithmic superiority
over Tierra, Avida, self-modifying evolutionary systems, or open-ended-evolution
toolkits. The bounded contribution is an operational observation protocol for
one frozen SAEE object, linking identity-bounded feedback, a lineage DAG,
discrete regime labels, and local evidence-compression surfaces to inspectable
repository artifacts.

Evidence:

- `paper_alife_lba/postsubmission_lb120/NOVELTY_AND_RELATED_WORK.md`
- `paper_alife_lba/postsubmission_lb120/OPERATIONAL_DEFINITIONS.md`

## If the single-run boundary is challenged

We agree that the reported artifacts do not support statistical generalization.
The result is limited to one 100-generation long-horizon artifact set and one
six-generation Phase II analysis artifact set. We make no cross-seed,
cross-parameter, or cross-substrate claim.

Evidence:

- `paper_alife_lba/postsubmission_lb120/SUPPLEMENT_lb120_METHODS.md`

## If attractor terminology is challenged

We use attractor only in an empirical, discretized sense. The implementation
forms an exact four-part categorical state signature and emits a candidate when
the same signature occurs at least twice. The current signature occurs in six
of six analyzed generations. No sliding-window clustering, continuous distance,
basin-volume estimation, or formal dynamical-systems proof is claimed.

Evidence:

- `saee_phase2/analysis/attractor_engine/engine.py`
- `saee_phase2/output/demo-run/attractor_map.json`
- `paper_alife_lba/postsubmission_lb120/OPERATIONAL_DEFINITIONS.md`

## If regime stability is challenged

The regime is assigned by an ordered point classifier. All six Phase II points
receive `stable_regime`; the classifier records zero label changes. The later
phase-diagram projection counts five adjacent self-transitions. We do not
interpret `5/5` as an externally calibrated transition probability.

Evidence:

- `saee_phase2/analysis/regime_classifier/classifier.py`
- `saee_phase2/output/demo-run/regime_transition_log.json`
- `docs/science/phase_diagram/REGIME_TRANSITION_GRAPH.json`

## If `808/1590` is challenged

The values are `808` nodes and `1590` directed edges in the reported lineage
DAG. They are not unique retained nodes versus raw lineage events. Endpoint
integrity is checked by confirming that every edge endpoint exists in the node
set and that the graph declares type `lineage_dag`.

Evidence:

- `saee_experiments/analysis/report_generator.py`
- `saee_experiments/reports/lineage_statistics.json`

## If provenance is challenged

The supplement records paths and SHA-256 hashes for the submitted PDF and the
current evidence artifacts. It also explicitly leaves the original execution
commit, original command, original OS/Python, package lock, hardware, and a
numeric random seed unknown. The current repository HEAD and workstation
environment are not retroactively promoted to original-run provenance.

Evidence:

- `paper_alife_lba/postsubmission_lb120/SUBMITTED_ARTIFACT_MANIFEST.json`
- `paper_alife_lba/postsubmission_lb120/SUPPLEMENT_lb120_METHODS.md`

## If the portal-submission non-claim is challenged

The submitted PDF contains a stale non-claim that includes `portal submission`,
while the portal ledger records `lb120` as accepted and author-confirmed on
2026-07-18. We preserve the uploaded PDF byte-for-byte and document the
inconsistency rather than silently rewriting the frozen artifact. The current
truth is: accepted with intent to present confirmed, but not published, included
in proceedings, assigned a DOI, or verified as conference-registered.
