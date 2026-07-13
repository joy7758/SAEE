# SAEE Academic Paper Draft Figure References

Status: local figure placeholders only. No image has been generated, published, or externally reviewed.

## Figure 1: Architecture

Draft location: Section 3, before Section 3.1.

Source specification: `docs/research-artifact/FIGURE_SPECIFICATIONS.md`, Figure 1.

Purpose: show the five-stage flow from observation through candidate mapping, evidence objects, adequacy evaluation, and bounded claim evaluation.

Required boundary label: `Evidence subsystem within SAEE; not the complete SAEE architecture`.

## Figure 2: Trace to Evidence Flow

Draft location: Section 3.2.

Source specification: `docs/research-artifact/FIGURE_SPECIFICATIONS.md`, Figure 2.

Purpose: show why mapping success does not imply adequacy success and why trace fields remain candidate values.

Required boundary label: `trace_auto_accepted_as_evidence=0 in the local synthetic artifact`.

## Figure 3: Evidence Adequacy Evaluation

Draft location: Section 3.4.

Source specification: `docs/research-artifact/FIGURE_SPECIFICATIONS.md`, Figure 3.

Purpose: show claim profile, required fields, semantic relationships, `PASS/FAIL`, missing requirements, and reason codes.

Required boundary label: `accountability_claim_established=false`.

## Figure 4: Benchmark Evidence Levels

Draft location: Section 5.2.

Source specification: `docs/research-artifact/FIGURE_SPECIFICATIONS.md`, Figure 4.

Purpose: show the fixed local PASS/FAIL distribution across four evidence levels: `0/3`, `1/3`, `1/3`, and `3/3` PASS.

Required boundary label: `curated synthetic regression only; not a real-world performance curve`.

## Rendering Gate

Before any figure is generated for a later draft:

- numerical labels must be checked against `agent-interface/reproducibility/expected-results.v0.1.json`;
- captions must preserve synthetic/offline/local wording;
- no compliance badge, certification mark, legal-proof symbol, competitor ranking, or production dashboard visual may be used;
- generated images must undergo a separate accuracy and claims review.
