# Evidence Presence Is Not Semantic Support

Local AIJ `Research Note` package for:

> **Evidence Presence Is Not Semantic Support: An Impossibility Result for
> AI-Agent Readiness Claims**

## Status

```text
target_journal=Artificial Intelligence
article_type=Research Note
scientific_content_complete=true
manuscript_complete=true
authorship_declarations_complete=true
submission_ready=true
experiment_complete=true
synthetic_validation=pass
elsevier_format=pass
external_validation=false
peer_reviewed=false
submitted=true
submission_received=true
manuscript_number=ARTINT-D-26-01262
portal_status=Submitted to Journal
initial_date_submitted=2026-07-19
published=false
production_ready=false
```

This is the new evidence-representation paper. It is separate from the earlier
ALIFE 2026 submission and does not modify or replace that manuscript.

## Central result

An evidence abstraction can support a perfect binary claim classifier if and
only if the abstraction separates all packages with different semantic
labels. The 16 matched pairs instantiate the failure of presence-only and
structure-only abstractions:

```text
pairs=16
cases=32
identical_required_field_presence_vectors=16/16
identical_json_key_type_shapes=16/16
field_presence_false_supports=16
type_and_shape_false_supports=16
decision_aware_false_supports=14
relation_aware_false_supports=0
deterministic_runs=5/5
boundary_violation_count=0
```

These are controlled white-box synthetic results, not population estimates or
production-readiness evidence.

No confidence interval, power calculation, or significance test is reported:
the 32 cases exhaust an authored finite corpus and do not define a sampling
frame. The analysis is retrospective and was not preregistered. Conventional
train/test leakage is inapplicable because no model is fitted; target-aware
case construction remains an explicit limitation.

## Package map

```text
main.tex                         AIJ/Elsevier manuscript source
references.bib                   bibliography
HIGHLIGHTS.txt                   AIJ highlights file
COVER_LETTER.md                  AIJ cover-letter draft
AIJ_SUBMISSION_READINESS.md      requirement and risk audit
AIJ_VENUE_AND_COST_VERIFICATION.md real-journal and zero-fee evidence
DECLARATIONS.md                  author-confirmation statements
submission-manifest.json        machine-readable package status
CLAIMS_BOUNDARY.md               claims and non-claims
CLAIM_AUDIT.md                   design-bound high-strength wording audit
HOSTILE_REVIEW_ACTION_REPORT.md  applicability and repair decisions
SCOPE_DISAMBIGUATION_AUDIT.md    false-reconstruction and adjacent-task boundary
LEAKAGE_AND_SELECTION_AUDIT.md   train/test non-applicability and case-selection risk
ANALYSIS_PLAN.md                 retrospective frozen complete analysis
ETHICS_AND_PRIVACY.md            synthetic-data ethics/privacy boundary
LITERATURE_MATRIX.md             novelty and collision map
REPRODUCIBILITY.md               local reproduction procedure
COLD_START_REPRODUCTION_REPORT.md isolated-directory reproduction evidence
SUPPLEMENT_README.md             supplementary archive entry and safety boundary
RESEARCH_RECOMMENDATION_GATE.md  bounded recommendation decision
COMPLETION_AUDIT.md              artifact and quality gates
experiment/                      dataset, runner, results, expectations
figures/                         LaTeX-native figures
```

The evaluator, profiles, and positive fixtures are pinned to source commit
`be6ab57878dc7346da733e2f3b134aa3d3049af8`; the public judging snapshot
`f6ac41f4b068377e7778e8c3d83b99bd8382debc` contains the same components.

The confirmed two-author submission manuscript is
`../output/pdf/evidence-presence-not-semantic-support-aij-final.pdf`.
Co-author consent, CRediT roles, funding, competing interests, originality,
correspondence-address use, and final approval were confirmed on 2026-07-19.
Editorial Manager now lists the manuscript under `Submissions Being Processed`
with final manuscript number `ARTINT-D-26-01262` and current status
`Submitted to Journal`. The pre-approval build reference
`ARTINT-S-26-01763` is not the final manuscript number. Submission receipt,
technical check, review, acceptance, and publication remain separate states;
see `SUBMISSION_RECEIPT.json` and `AIJ_SUBMISSION_READINESS.md`.

`lb120` is a final-abandoned conference/LBA route. Its scientific content is
not merged into this focused AIJ Research Note; only its provenance and
claim-boundary discipline are reused as method.

Compiled and visually inspected manuscript:

```text
superseded_path=../output/pdf/evidence-presence-not-semantic-support-aij.pdf
status=superseded_one_author_build
authorship_pending_path=../output/pdf/evidence-presence-not-semantic-support-aij-authorship-pending.pdf
authorship_pending_status=superseded
current_path=../output/pdf/evidence-presence-not-semantic-support-aij-final.pdf
current_pages=13
current_sha256=42d2119d3d609e60eb095216b839ee14cbcbb60383a1fc693b3caaf4253b3863
supplement_path=../output/pdf/evidence-presence-not-semantic-support-aij-supplement.zip
supplement_sha256=0044cb96072cfd08fa87152c4f8e61753fd42911aabb40213a850faba9c03453
supplement_isolated_verification=pass
```
