# lb120 Post-submission Paper Hardening

Status: `local_postsubmission_support_only`

This directory hardens the paper-facing explanation of **SAEE as a Frozen
Reflexive Evolutionary Dynamical Object** without changing the submitted
artifact, SAEE theory, runtime, kernel, experiments, candidate laws, or GSP
semantics.

## Frozen submission boundary

- Submission ID: `lb120`
- Portal state observed on 2026-07-18: `Accept (Confirmed)`
- Acceptance confirmation performed on 2026-07-18: `true`
- Submitted PDF: `paper_alife_lba/build/main.pdf`
- Submitted PDF SHA-256:
  `aef09e556b2e91b2374b51371164d887e2db40c39a260b3dac2ef7772d15ece8`
- Submitted PDF page count: `1`
- Portal upload changed by this package: `false`
- New experiment introduced: `false`
- Existing result value changed: `false`

`Accept (Confirmed)` means the submission was accepted and the author confirmed
the intent to present. It does not mean published, included in proceedings,
assigned a DOI, registered for the conference, externally validated, or
released. The Late-Breaking Abstract route is explicitly excluded from the
proceedings.

## What this package fixes

1. It replaces generic reviewer assumptions with the repository's real
   measurement rules.
2. It states that `808/1590` means `808` lineage DAG nodes and `1590` directed
   edges, not retained nodes versus raw events.
3. It defines the Phase II attractor as a repeated discrete state signature,
   not a continuous-state attractor proof and not a windowed clustering result.
4. It separates the 100-generation long-horizon evidence from the six-generation
   Phase II classification surface.
5. It records provenance gaps explicitly instead of inventing a numeric random
   seed, original execution command, original execution commit, package lock,
   CPU/GPU model, or original Python/OS version.
6. It narrows all interpretation to local, single-run, observational evidence.

## Files

- `HOSTILE_REVIEW_REMEDIATION.md`: disposition of each hostile-review point.
- `OPERATIONAL_DEFINITIONS.md`: exact observable definitions traced to code.
- `SUPPLEMENT_lb120_METHODS.md`: artifact paths, hashes, reconstruction notes,
  and known provenance gaps.
- `NOVELTY_AND_RELATED_WORK.md`: conservative positioning against primary
  literature.
- `REVIEW_RESPONSE_lb120.md`: reusable response notes; not an actual reviewer
  response and not externally sent.
- `SUBMITTED_ARTIFACT_MANIFEST.json`: machine-readable frozen-artifact boundary.
- `lb120_postsubmission_support.tex`: standalone support document source.
- `output/pdf/lb120-postsubmission-support.pdf`: compiled and visually checked
  local support PDF; it is not the submitted LBA.
- `figures/operational_definition_flow.mmd`: agent-readable measurement flow.

## State separation

```text
submitted_pdf=frozen
portal_state_observed=Accept (Confirmed)
postsubmission_support=local_only
portal_artifact_update_performed=false
reviewer_response_received=false
acceptance=true
acceptance_confirmation=true
acceptance_confirmation_observed_on=2026-07-18
publication=false
proceedings_inclusion=false
doi_assigned=false
conference_registration_verified=false
external_validation=false
```

The official ALIFE 2026 call describes Late-Breaking Abstracts as at most two
pages excluding references, suitable for new ideas and work in progress,
reviewed for relevance and quality, excluded from proceedings, and presented
as posters if accepted. It also states that submissions are non-anonymous and
the review process is single-blind:
<https://2026.alife.org/call-for-papers/>.

The conference home page separately says a limited number of LBAs are decided
on a rolling basis until capacity is reached:
<https://2026.alife.org/>.
