# SAEE Evolution Capability Router

> OpenAI Build Week 2026 judging guide. This branch is a bounded historical
> submission snapshot, not the current SAEE integration mainline and not
> evidence of customer validation, production deployment, or final Devpost
> submission.

## What was built

SAEE existed before OpenAI Build Week. The judged extension is the
Agent-readable capability routing layer added after the submission window
opened:

```text
pre_event_baseline=d533c30668c81696aa7fca046985383ff52aae9d
core_extension_start=9f74d153a
core_extension_end=f6ac41f4b068377e7778e8c3d83b99bd8382debc
core_extension_files_changed=74
core_extension_insertions=6850
core_extension_deletions=40
```

The extension reuses the existing SAEE runtime and adds one canonical,
machine-readable capability inventory, deterministic routing commands,
duplicate-build prevention, governance projections, negative cases, and
staged-truth checks. It does not create a second capability registry or a
parallel implementation.

## Why it matters

Long-running AI codebases can drift across roadmaps, documentation, runtime
adapters, and status ledgers. A coding Agent may otherwise mistake a design
for an implementation, rebuild an existing capability, or promote a local
test into a production claim.

The router gives Codex and other coding Agents one file-backed source for:

- capability lifecycle state;
- canonical implementation and entrypoint;
- public aliases and interface roles;
- implementation and test evidence;
- claims and non-claims;
- deterministic validation and fail-closed routing.

The sole capability fact source is:

```text
capability-package/manifest.json#canonical_inventory
```

## How Codex and GPT-5.6 were used

GPT-5.6 in Codex was used during the event to:

1. inventory conflicting capability, MCP, roadmap, and documentation
   surfaces;
2. trace public aliases to existing implementations instead of rebuilding
   them;
3. design canonical CLI lookups and fail-closed interface resolution;
4. generate and review negative cases for duplicate IDs, alias conflicts,
   ambiguous routes, and unsupported interfaces;
5. verify that the machine ledger remains a projection of the canonical
   inventory;
6. review all public language against explicit staged-truth non-claims.

Human decisions retained the product boundary: SAEE remains a Digital
Biosphere Evolution Engine. The router supports its Evolutionary Archive /
Rollback Immune System and does not reframe the project as an audit SDK or a
generic Agent framework.

## Supported judging platform

The submission snapshot was tested on macOS with Python 3.14.5. The judging
path is a local, offline Python CLI; no cloud account, secret, API key, private
dataset, or external service is required.

## Install

```bash
git clone --branch codex/openai-build-week-2026 --single-branch \
  https://github.com/joy7758/SAEE.git
cd SAEE
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r saee_backend/requirements.txt
```

On Windows PowerShell, replace the activation line with:

```powershell
.venv\Scripts\Activate.ps1
```

Windows and Linux are intended Python CLI targets but were not independently
validated for this submission snapshot.

## Five-minute judge test

```bash
python3 scripts/saee_agent_cli.py capability-list
python3 scripts/saee_agent_cli.py capability-show saee.evaluate_agent_run
python3 scripts/saee_agent_cli.py capability-resolve \
  saee.evaluate_agent_run --interface mcp
python3 scripts/saee_agent_cli.py capability-validate
python3 scripts/saee_canonical_capability_inventory_smoke.py
python3 scripts/saee_capability_progress_ledger_smoke.py
python3 scripts/saee_governance_registry_check.py
```

Expected bounded result:

```text
capabilities=9/9
negative_cases=16/16
deterministic_runs=5/5
capability_statuses=9/9
duplicate_build_prevention=true
governance_registries=6/6
public_mcp_endpoint_available=false
external_mcp_interoperability_validated=false
customer_validated=false
production_ready=false
```

## Capability states in this snapshot

| State | Count |
|---|---:|
| `implemented` | 3 |
| `partial` | 1 |
| `design_only` | 1 |
| `missing` | 4 |

These counts are testable repository facts for this snapshot. They are not a
claim that all planned SAEE capabilities are implemented.

## Claims

- The local canonical inventory and router are implemented in this snapshot.
- The listed CLI and offline validators run deterministically on the tested
  platform.
- Existing capability implementations are reused rather than duplicated.
- The judged core extension is distinguishable through timestamped Git
  history.

## Non-claims

```text
public_mcp_endpoint_available=false
external_mcp_interoperability_validated=false
customer_validated=false
product_launched=false
production_ready=false
devpost_final_submission_established_by_repository=false
```

Passing local validation does not authorize deployment or external action and
does not authenticate the origin or completeness of a trace.

## License

This judging snapshot is released under the Apache License 2.0. See
[`LICENSE`](LICENSE).
