---
schema: saee.worktree_consolidation_record.v1
record_date: 2026-07-13
status: validation_passed_ready_for_content_commit
evolution_subsystem: evolutionary_archive_and_rollback_immune_system
content_commit: pending
tracking_commit: pending
external_action_performed: false
parent_remote_push_performed: false
production_ready: false
customer_validated: false
product_launched: false
---

# SAEE Worktree Consolidation Record — 2026-07-13

## Purpose

Convert a long-running mixed worktree into a discoverable and reviewable Git
baseline without deleting owner artifacts or raising any commercial truth
state. The record is both the human handoff and the agent-readable classification
surface for this consolidation.

## Required design and recommendation check

- Evolution subsystem strengthened: `Evolutionary Archive / Rollback Immune System`.
- Sensing, branching, variation, and selection behavior: unchanged.
- Safety, license, supply-chain, and permission boundaries: preserved; no
  dependency install, unknown repository execution, external contact, or
  permission expansion is part of this operation.
- Audit-first reframing risk: `no`; this is repository provenance for the
  Digital Biosphere Evolution Engine, not a new audit product feature.
- Agent recommendation: `recommend` for repository consolidation because an
  agent can discover this record, understand the classification, reproduce the
  validation commands, and distinguish durable evidence from local runtime
  output.

## Classification

| Class | Included in parent Git | Treatment |
|---|---:|---|
| Evolution engine, research implementations, schemas, tests | yes | preserve source and reproducible evidence |
| Agent-readable surfaces (`README`, `agent-index.json`, `llms.txt`, contracts, examples) | yes | preserve as first-class product surfaces |
| Recommendation gates, commercial and ecosystem packages | yes | preserve with existing local/review truth states |
| Research result manifests, summaries, figures, and referenced raw evidence | yes | preserve reproducibility and existing hashes |
| `tmp/`, `output/`, `.playwright-cli/`, `.saee_runtime/` | no | preserve locally; ignore as regenerable or operator-local output |
| `.env*`, `.secrets/`, `.venv/`, caches and build output | no | retain existing secret/runtime exclusions |
| `sites/saee-commercial/` | no | manage as an independent clean Git repository |
| Private attachment contents | no | do not copy; retain only redacted provenance references |

## Pre-commit inventory

```text
durable_untracked_candidates=5085
durable_candidate_size_kib=100640
ignored_playwright_files=18
ignored_runtime_files=8
ignored_tmp_files=230
ignored_output_files=60
nested_site_branch=main
nested_site_head=d69e596
nested_site_worktree_clean=true
parent_remote_configured=false
```

The candidate count is a pre-commit snapshot. Git commit statistics are the
authoritative final file count.

## Portability and privacy actions

- Rewrote owner-workstation repository roots to `./` repository-relative paths.
- Rewrote sibling repository references to `~/GitHub/...` where historical
  provenance requires a local workspace reference.
- Replaced private Codex attachment roots with `<private-attachment>/...` and
  did not copy the attachments.
- Scanned candidate text for known private address, personal phone, bank account,
  private-key headers, and common provider API-key assignments; no candidate
  secret value was found.

## Validation plan

1. Validate JSON and YAML syntax for candidate files.
2. Compile Python candidates without writing bytecode into the source tree.
3. Run the repository `mainline_guard` and relevant marketplace delivery smokes.
4. Inspect staged paths, staged size, large files, and secret-pattern matches.
5. Commit the durable baseline, then update this record with the commit hash in
   a separate tracking commit.

## Validation outcome

```text
json_syntax=pass
python_syntax=pass
python_candidate_count=1440
yaml_cff_syntax=pass
yaml_cff_candidate_count=15
make_check=pass
make_check_pass_lines=638
make_check_failure_lines=0
mainline_guard=pass
baidu_cloud_handoff_package_smoke=pass
commercial_boundary_smoke=pass
tenant_security_agent_review_smoke=pass
tenant_storage_isolation_evidence_runner_smoke=pass
```

The stale commercial-boundary test fixture was aligned with the existing
fail-closed rule that preview mode must explicitly set
`SAEE_SYNTHETIC_DATA_ONLY=true`. The tenant security profile was regenerated
after its source manifest detected a changed authorization-context hash. These
repairs did not enable production auth, formal security review, privacy/legal
review, customer validation, or product launch.

## Truth boundary

This consolidation records local repository artifacts only. It is not evidence
of production deployment, provider approval, marketplace publication, customer
validation, revenue, or product launch. No parent repository push is authorized
or performed by this record.
