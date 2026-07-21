# AIJ-targeted paper completion audit

Last updated: 2026-07-19

## Objective

```text
objective=prepare a high-risk AIJ Research Note submission package
manuscript=main.tex
compiled_pdf=../output/pdf/evidence-presence-not-semantic-support-aij-final.pdf
external_submission=true
manuscript_number=ARTINT-D-26-01262
portal_status=Submitted to Journal
```

## Scientific gates

| Gate | Status | Evidence |
|---|---|---|
| General AI contribution | PASS | Claim-separating evidence abstractions for AI-agent evaluation |
| Formal result | PASS | Sufficiency theorem plus two corollaries |
| Matched-pair construction | PASS | 16 pairs; four claim profiles |
| Presence equivalence | PASS | 16/16 identical required-field vectors |
| Structure equivalence | PASS | 16/16 identical JSON key/type signatures |
| Baseline gradient | PASS | False supports 16, 16, 14, and 0 |
| Exact authored labels/reasons | PASS | 32/32 each |
| Pre-study component pinning | PASS | Commit `be6ab578...`; nine SHA-256 values |
| Determinism | PASS | 5/5 runs; one result hash |
| Authority boundary | PASS | 0/32 protected-field violations |
| External/generalization claim | NOT_CLAIMED | White-box synthetic construct validation only |

## AIJ format gates

| Gate | Status | Evidence |
|---|---|---|
| Article type | PASS | Research Note |
| Word limit | PASS | Below 4,500 words by both PDF and source-derived counts |
| Page range | PASS | 13 pages; official typical range 5–14 |
| Abstract | PASS | 223 words, below 250 |
| Keywords | PASS | 6 |
| Highlights | PASS | 5 bullets, each below 85 characters |
| Elsevier source | PASS | `elsarticle.cls`, BibTeX, editable TikZ figures |
| References | PASS | Mature testing literature plus current agent evidence work |
| Declarations | PASS | Funding, interests, AI use, CRediT, originality, and final approval confirmed 2026-07-19 |
| PDF visual inspection | PASS | All 13 pages rendered; no clipping, overlap, blank page, or unreadable figure/table |
| Postal author address | PASS_PRIVATE_PORTAL_ONLY | Private correspondence address and postal code authorized for Elsevier portal only |

## Current artifact fingerprints

```text
canonical_result_sha256=4d101bb8633e4acf6cf4d38c08734afddb47d52c6c8b1748d23f6494c4962f44
canonical_dataset_sha256=1d9cf1ddd52636a1504b78c7b2e7ed577300e6fecdb81b67c2bd222c03f687b0
results_file_sha256=479de2f2916fcb7fe27c91306a3313d45dafb27b1258c31f21efa7eabd1bdf87
final_submission_pdf_sha256=42d2119d3d609e60eb095216b839ee14cbcbb60383a1fc693b3caaf4253b3863
supplementary_archive_sha256=0044cb96072cfd08fa87152c4f8e61753fd42911aabb40213a850faba9c03453
supplementary_archive_isolated_verification=PASS
```

## Completion boundary

The scientific content, authorship declarations, consent, and local AIJ support
package are complete. Editorial Manager lists the final manuscript as
`ARTINT-D-26-01262` under `Submissions Being Processed`, with current status
`Submitted to Journal` and initial submission date `2026-07-19`. The earlier
`ARTINT-S-26-01763` is only a pre-approval build reference. The new experiment,
the earlier 12-case evidence
regression, capability ledger, governance registry, development-constitution
checks, and repository-wide `mainline_guard.py` pass.

The generic hostile-review checklist was applied selectively. Claim,
selection-bias, statistical-estimand, reproducibility, and ethics/privacy
audits are present. An isolated-directory reproduction passes with the same
canonical result hash. This is not a fresh environment or cross-platform
reproduction. The analysis was not preregistered, and no population confidence
interval or significance claim is made.

The second hostile-review report's reconstruction as AI-text detection,
human--AI authorship attribution, or RAG citation-faithfulness research was
rejected as a task mismatch. The manuscript now states that boundary directly,
adds two adjacent primary references, and records prohibited legal/editorial
uses and the absent DOI-archive state in `SCOPE_DISAMBIGUATION_AUDIT.md`.

The author explicitly authorized portal drafting, upload, and submission on
2026-07-19, and the portal receipt has now been recorded. This does not mean
technical check completed, editor assigned, under review, accepted, published,
DOI assigned, or externally validated.
