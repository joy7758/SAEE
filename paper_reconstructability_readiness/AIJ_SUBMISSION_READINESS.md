# AIJ submission readiness

Last updated: 2026-07-19

## Target decision

```text
target_journal=Artificial Intelligence (AIJ)
article_type=Research Note
route=subscription/traditional
author_publication_fee=none_under_current_journal_page
real_journal_verified=true
mandatory_author_cost=0
author_budget_for_mandatory_publication_fees=0
scientific_fit=conditional_but_defensible
desk_reject_risk=medium_high
submitted=true
submission_received=true
manuscript_number=ARTINT-D-26-01262
portal_status=Submitted to Journal
submission_ready=true
```

Venue identity, peer review, ISSNs, archive, and official zero-fee subscription
route are verified in `AIJ_VENUE_AND_COST_VERIFICATION.md`. The optional
`USD 4,050` Open Access route is explicitly rejected and is not a fallback.

AIJ is a credible high-risk target because its Research Notes accept crisp,
focused technical work presenting a theorem or experimental result. The paper
now offers both. Its central object is an AI evaluation representation, not a
SAEE product feature. The remaining risk is scientific, not formatting: the
claim-separation theorem is elementary and the experiment is synthetic and
white-box. The cover letter therefore leads with the general representation
criterion and treats the 16 pairs as executable witnesses, never as a
population benchmark.

## Official-requirement alignment

| AIJ requirement | Current state |
|---|---|
| Research Note maximum 4,500 words | PASS — PDF text has 3,695 whitespace-delimited tokens including references |
| Typical 5–14 pages | PASS — 13 pages in Elsevier preprint format |
| Abstract no more than 250 words | PASS — 223 words |
| 1–10 keywords | PASS — 6 keywords |
| Elsevier LaTeX source | PASS — `elsarticle.cls` and BibTeX |
| Highlights, 3–5 bullets, maximum 85 characters | PASS — `HIGHLIGHTS.txt`, 5 bullets |
| Data/code statement | PASS — supplementary-material statement in manuscript |
| Competing-interest statement | PASS — both authors confirmed none |
| Funding statement | PASS — both authors confirmed no specific funding |
| Generative-AI disclosure | PASS — OpenAI Codex use disclosed before references |
| CRediT author contribution | PASS — both authors' roles confirmed |
| Publication name | PASS — `Bin Zhang` (`given_name=Bin`, `family_name=Zhang`) |
| Corresponding e-mail | PASS — `joy7759@gmail.com` |
| ORCID | PASS — `0009-0002-8861-1481` |
| Affiliation | PASS — `Shanxi Youqibing E-Commerce Co., Ltd., Yuncheng, Shanxi, China` |
| GitHub profile | RECORDED — `https://github.com/joy7758`; not required in manuscript |
| Full institutional postal address | NOT_CLAIMED — private correspondence address and postal code are authorized for Elsevier portal use only and are not represented as the company address |
| Originality/not concurrently submitted | PASS — both authors confirmed |
| Second author identity | PASS — `Xiaojuan Sun` (`given_name=Xiaojuan`, `family_name=Sun`) |
| Second author e-mail | PASS — `sunxiaojuan@ycu.edu.cn` |
| Second author ORCID | PASS — `0009-0003-4705-1809` |
| Second author affiliation | PASS — Department of Physical Education, Yuncheng University, Yuncheng, Shanxi 044000, China |
| Second author consent | PASS — explicitly confirmed 2026-07-19 |
| Second author CRediT roles | PASS — Conceptualization, Investigation, Data curation, Resources |
| All-authors final manuscript approval | PASS — explicitly confirmed 2026-07-19 |

## Scientific upgrades completed

1. Replaced the title’s reconstructability collision with a broader evidence-
   representation claim.
2. Added a necessary-and-sufficient claim-separation theorem.
3. Added a matched-pair error lower bound for any deterministic presence-only
   classifier.
4. Added JSON key/type structure and affirmative-decision ablations.
5. Pinned pre-study evaluator, profile, and fixture component hashes.
6. Added mature behavioral, metamorphic, and mutation-testing literature.
7. Recast zero errors as construct validation, not general performance.
8. Converted the manuscript to Elsevier single-column preprint format and
   added AIJ declarations and supplementary-material language.
9. Audited high-strength claims against the actual formal-plus-construct design;
   formal proof language is retained only for the theorem.
10. Added a retrospective analysis plan and explained why population
    confidence intervals, power, and significance tests are not identified by
    the finite authored corpus.
11. Replaced generic train/test leakage language with the relevant
    target-aware case-selection limitation.
12. Added a pinned environment, data dictionary, ethics/privacy statement, and
    an isolated-directory reproduction rehearsal that passes on the same host.
13. Added explicit scope disambiguation against AI-text detection, human--AI
    authorship attribution, legal authorship, copyright, misconduct, and
    editorial-sanction uses.
14. Added primary literature distinguishing natural-language citation support
    and RAG attribution faithfulness from the paper's structured evidence-
    relation predicate.

The cited GitHub source snapshot is not a DOI-backed archive of this manuscript
package. No preprint or artifact DOI deposit has been made or authorized; a
future immutable deposit remains a separate author-controlled external action.

## Human gate before portal submission

The required author confirmations were completed on 2026-07-19:

```text
private_correspondence_address_approval=confirmed_for_elsevier_portal_only
xiaojuan_sun_coauthor_consent=confirmed
xiaojuan_sun_credit_roles=confirmed
all_authors_funding_statement_confirmed=none
all_authors_competing_interest_statement_confirmed=none
all_authors_not_under_consideration_elsewhere_confirmed=true
all_authors_final_manuscript_approval=true
portal_draft_upload_and_submission_authorized=true
```

Date of birth, gender, and mobile number remain only in the Git-excluded local
`PRIVATE_AUTHOR_PROFILE.md`. The residential address and postal code are
authorized only as an Elsevier portal correspondence address when explicitly
required. They are not manuscript content, a company registered address, or a
public-package field.

The source co-author `.doc` contained a credential field. No password or other
authentication secret was copied into this repository, the manuscript package,
or persistent memory.

Portal drafting, upload, and submission to AIJ were authorized and completed.
On 2026-07-19, Editorial Manager listed the manuscript under `Submissions Being
Processed` as `ARTINT-D-26-01262`, with current status `Submitted to Journal`.
The earlier `ARTINT-S-26-01763` value is retained only as a pre-approval PDF
build reference. A preprint deposit, DOI request, paid route, or other public
publication action is not authorized. This portal state does not establish
technical-check completion, editor assignment, peer review, acceptance,
publication, DOI assignment, external validation, or production readiness.

## Alternative-journal fallback

If AIJ rejects without review for scope or contribution depth, preserve this
manuscript and re-target rather than broaden claims. A software-evaluation or
AI-systems journal can accept the executable construct result with less
pressure for a deep AI theorem. That fallback is not active while
`target_journal=Artificial Intelligence`.

Every fallback must independently pass the real-journal and zero-mandatory-cost
gate. A journal is never retained merely because a waiver might be available.

## lb120 content-integration decision

```text
source_route=ALIFE_2026_LBA_lb120
author_route_decision=FINAL_ABANDONED
scientific_content_integration=DO_NOT_INTEGRATE
text_copied_into_aij_manuscript=false
data_or_result_pooled=false
```

The `lb120` paper studies a frozen reflexive evolutionary dynamical object,
stable-regime observations, lineage structure, and bounded semantic drift. The
AIJ Research Note studies whether evidence abstractions preserve the relations
needed for AI-agent readiness claims. The research questions, constructs, and
experiments are different. Merging the old local evolutionary results would
dilute the focused theorem, consume the Research Note word budget, and create
avoidable text-reuse and prior-publication questions.

The only reusable lesson is methodological: operational definitions,
provenance, and explicit claim boundaries. Those practices are already present
in the AIJ package; no `lb120` prose, table, numerical result, or scientific
claim has been imported.
