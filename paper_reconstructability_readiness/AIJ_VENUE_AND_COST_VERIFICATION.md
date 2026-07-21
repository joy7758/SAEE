# AIJ venue identity and zero-cost verification

Verification date: 2026-07-19

## Decision

```text
venue=Artificial Intelligence
abbreviation=AIJ
venue_type=peer_reviewed_scholarly_journal
real_journal_verified=true
selected_publishing_route=subscription
mandatory_author_cost=0
optional_paid_open_access_selected=false
venue_eligible=true
payment_authorized=false
submitted=true
manuscript_number=ARTINT-D-26-01262
portal_status=Submitted to Journal
```

AIJ is eligible only through its normal `Subscription`（订阅制 / 传统发表）
route. Optional Open Access（开放获取）is not selected.

## Official identity evidence

Official journal page:
`https://www.sciencedirect.com/journal/artificial-intelligence`

The publisher's journal page identifies:

```text
official_title=Artificial Intelligence
publisher=Elsevier
online_issn=1872-7921
print_issn=0004-3702
editors_in_chief=Sylvie Thiebaux; Michael Wooldridge
issue_and_article_archive_present=true
official_submission_link_present=true
```

These are publisher-controlled identity surfaces, not a third-party journal
list or an inferred reputation claim.

## Official peer-review evidence

Official Guide for Authors:
`https://www.sciencedirect.com/journal/artificial-intelligence/publish/guide-for-authors`

The guide states that AIJ uses single-anonymized peer review, performs an
initial editorial suitability assessment, and normally sends suitable
submissions to at least two independent reviewers. This satisfies the current
repository requirement for a real peer-reviewed scholarly journal.

## Official cost evidence

The official journal page separates two routes:

| Route | Official author-side statement | Selection |
|---|---|---|
| Open Access | APC `USD 4,050`, excluding taxes | REJECTED_NOT_SELECTED |
| Subscription | “No publication fee charged to authors” | SELECTED |

Therefore:

```text
mandatory_apc=false_for_selected_route
submission_fee=not_listed_as_mandatory
page_charge=not_listed_as_mandatory
registration_fee=false
waiver_dependency=false
selected_route_author_publication_fee=0
```

This verification does not claim that optional services are free or that the
publisher can never change its policy. It proves only that the currently
selected standard route has no publication fee on the official page.

## Reverification stop rules

Recheck the official journal and portal immediately before final submission
and again before accepting any publishing agreement. Stop without payment if:

- the portal makes Open Access mandatory;
- any APC, submission, page, mandatory color, registration, or publication
  fee becomes unavoidable;
- the free route depends on an unapproved waiver;
- official pages conflict or the cost becomes unknown; or
- the publisher redirects the manuscript to a different journal whose
  identity and cost have not passed a fresh gate.

```text
portal_draft_authorized=true
upload_authorized=true
final_submission_authorized=true
payment_authorized=false
```

The paper was submitted through the verified subscription route on 2026-07-19.
This document verifies venue and cost eligibility; the portal receipt is
recorded separately in `SUBMISSION_RECEIPT.json`. Submission does not guarantee
technical-check completion, peer review, acceptance, publication, indexing, or
a DOI.
