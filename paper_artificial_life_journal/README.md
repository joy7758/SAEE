# Artificial Life Journal Letter Submission Package

Status: `submitted_awaiting_admin_processing`

ScholarOne manuscript ID: `ARTL-2026-0186`.

Portal evidence observed on 2026-07-19:

```text
date_submitted=18-Jul-2026
portal_status=Awaiting Admin Processing
submission_completed=true
payment_requested=false
payment_made=false
technical_check_claim=false
peer_review_claim=false
acceptance_claim=false
publication_claim=false
```

Target: *Artificial Life* (MIT Press), `Letter` article type.

Authors: Bin Zhang (first and corresponding author); Xiaojuan Sun (second
author).

## Files

- `main.tex`: single-column, double-spaced initial manuscript.
- `references.bib`: APA-compatible bibliography source.
- `cover_letter.md`: journal cover letter and prior-LBA disclosure.
- `VENUE_DUE_DILIGENCE.md`: real-journal and zero-mandatory-cost gate.
- `SUBMISSION_RECEIPT.json`: sanitized ScholarOne confirmation and status record.
- `generate_figures.py`: deterministic figure projection from tracked,
  digest-bound supplement JSON only; no ignored experiment output is required.
- `figures/`: generated vector TikZ figures.
- `supplement/`: minimal source-data and provenance package.
- `build/main.pdf`: compiled submission manuscript.

## Boundaries

```text
new_experiment=false
kernel_modified=false
runtime_modified=false
new_theory=false
universal_claim=false
external_validation_claim=false
open_access_selected=false
mandatory_author_cost=0
submission_completed=true
portal_status=Awaiting Admin Processing
manuscript_id=ARTL-2026-0186
payment_requested=false
payment_made=false
technical_check_claim=false
peer_review_claim=false
acceptance_claim=false
publication_claim=false
```

The source ALIFE 2026 LBA remains frozen and is not silently rewritten by this
journal package.
