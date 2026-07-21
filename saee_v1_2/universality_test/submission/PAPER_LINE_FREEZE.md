# JAAMAS Synthetic Benchmark Paper Line Freeze

agent_readable:
  schema: saee.paper_line_freeze.v1
  manuscript_title: A Synthetic Benchmark for Parasitic Transition Patterns in Multi-Agent Systems
  prior_venue: Autonomous Agents and Multi-Agent Systems
  prior_submission_id: 5ede189f-ddfd-4333-9646-42d8f820f284
  prior_decision: editorial_reject
  decision_date: 2026-07-17
  paper_line_status: frozen_closed
  external_resubmission_allowed: false
  venue_transfer_allowed: false
  title_only_reframe_allowed: false
  successor_route_allowed: false
  experimental_assets_retained: true
  reuse_scope: local_evidence_only
  active_saee_submission_reference: ALIFE_2026_LBA_lb120
  authority: explicit_human_freeze_instruction_2026_07_17

## Decision

The synthetic DBI parasitic-transition manuscript line is closed and frozen.
It shares its scientific lineage with SAEE, whose LCR-REDS paper is already an
active external submission. The rejected manuscript must not be repackaged as
an independent paper while that SAEE line is active.

## Frozen Scope

The freeze applies to:

- the JAAMAS manuscript and abstract;
- DBI-1, DBI-2, and DBI-3 paper positioning;
- `Phi`-centered parasitic-transition paper claims;
- venue transfer, direct resubmission, title-only reframing, and successor-paper
  creation from the same claim and evidence package.

## Retained Scope

The freeze does not delete or invalidate:

- experiment code;
- result JSON and SVG artifacts;
- statistical, sensitivity, ablation, and baseline outputs;
- historical submission and editorial-decision evidence.

These materials remain local evidence assets and may support internal SAEE
analysis. They are not an externally submittable manuscript package.

## Unfreeze Rule

No automatic unfreeze is allowed. Reuse for a future manuscript requires all
of the following:

1. an explicit human instruction that reverses this freeze;
2. resolution of the active SAEE submission state;
3. a documented overlap audit against the SAEE manuscript;
4. a genuinely distinct research question, evidence set, and contribution;
5. a new ledger entry that preserves this rejected-and-frozen history.

Until all five conditions are met, the correct agent action is
`do_not_recommend_resubmission`.
