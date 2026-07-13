# Canonical Capability Inventory, Routing and Deprecation Map v1 — Implementation Report

Date: 2026-07-13
Scope: repository-local governance and routing; no new OTLP receiver, mapper,
MCP service or production control plane.

> Merge-readiness update, 2026-07-14: an independent isolated-worktree review
> found that the only GitHub repository candidate has no common ancestor with
> this checkout, and that `make check` leaves generated changes before a second
> `mainline_guard.py` run fails. The implementation remains locally reviewable,
> but push, Draft PR and merge readiness are blocked. See
> `reports/CANONICAL_CAPABILITY_MERGE_READINESS_REVIEW.md`.

## 1. Preflight Recommendation

The preflight result was `conditional`. SAEE was recommendable only for
controlled local evaluation because capability facts and MCP roles did not have
one machine-verifiable authority. The provisional best-evidenced entry was
`.mcp.json` -> `scripts/saee_agent_readiness_mcp_stdio.py`.

Evidence: `reports/CANONICAL_CAPABILITY_ROUTING_PREFLIGHT.md`.

## 2. Existing Truth Sources Found

| Existing source | Relevant object or symbol | Finding | Evidence strength |
|---|---|---|---|
| `capability-package/manifest.json` | package manifest and now `canonical_inventory` | Existing runtime-consumed package metadata was the strongest reusable authority | `VERIFIED` |
| `saee_backend/services/capability_runtime/capability_registry_loader.py` | `load_capability_registry` | Runtime already loaded and cross-checked Capability Package projections | `VERIFIED` |
| `agent-index.json` | capability objects, `recommended_next_pr`, `capability_progress_ledger_v1` | Mixed durable capability facts with time-sensitive roadmap advice | `VERIFIED` |
| `capability-package/capability-card.json` | operation list | Useful package projection, but too narrow for lifecycle, aliases and all MCP surfaces | `VERIFIED` |
| `capability-package/mcp-tool.json` | MCP tool descriptions | Tool projection, not a complete capability authority | `VERIFIED` |
| `agent-interface/public/saee-public-capability-surface.v0.1.json` | `available_operations` | Public operation projection; it does not classify all runtime surfaces | `VERIFIED` |
| `.well-known/saee-capability-index.json` | `public_operations` | Discovery projection, not implementation truth | `VERIFIED` |
| README and Agent-readable documents | startup and integration guidance | Previously recommended different MCP paths in different contexts | `VERIFIED` |

Revalidated findings:

- `synthetic_opentelemetry_style` is implemented by
  `saee_backend/services/otel_candidate_mapping.py` and exercised by
  `scripts/saee_otel_candidate_mapping_smoke.py`. It accepts a closed synthetic
  candidate shape and produces non-authoritative candidate fields.
- No OpenTelemetry SDK import, OTLP receiver, Collector receiver or network
  listener exists in that path: `VERIFIED`.
- Trace authenticity is not established: `VERIFIED` from mapper non-claims and
  smoke output `accountability_claim_established=false`.
- End-to-end external identity binding and delegation binding are not
  implemented: `VERIFIED` by repository search and the absence of executable,
  tested end-to-end entries; both are canonical `missing` records.
- The stale OTEL recommendations were the historical
  `evidence_adequacy_profile_v0_1.recommended_next_pr` and
  `external_resource_resolution_receipt_v0_1.recommended_next_pr` objects in
  `agent-index.json`; both are now superseded compatibility records.

## 3. Canonical Source Selected

`capability-package/manifest.json#canonical_inventory`

It is the sole machine-readable source for current capability identity,
implementation status, lifecycle, canonical implementation, entry point,
interfaces, aliases, evidence, claims, non-claims, compatibility and MCP
surface roles.

## 4. Why It Was Selected

- It extends an existing Capability Package rather than creating a fifth
  parallel inventory.
- The runtime loader already consumes the parent manifest.
- JSON and `jsonschema` were already used by the repository; no dependency was
  added.
- The source can express current facts while keeping roadmap advice outside the
  runtime contract.
- The validation direction is one-way: manifest authority -> strict validation
  of projections and real repository paths.

Decision record: `docs/adr/0005-canonical-capability-source-v1.md`.

## 5. Files Added

- `docs/CAPABILITY_INVENTORY.md`
- `docs/adr/0005-canonical-capability-source-v1.md`
- `docs/strategy/SAEE_CAPABILITY_PROGRESS_LEDGER_RECOMMENDATION_GATE.md`
- `reports/CANONICAL_CAPABILITY_ROUTING_PREFLIGHT.md`
- `reports/CANONICAL_CAPABILITY_ROUTING_POSTFLIGHT.md`
- `reports/CANONICAL_CAPABILITY_INVENTORY_IMPLEMENTATION_REPORT.md`
- `saee_backend/services/capability_runtime/canonical_capability_inventory.py`
- `schemas/saee-canonical-capability-inventory.schema.v1.json`
- `scripts/saee_canonical_capability_inventory_smoke.py`
- `scripts/saee_capability_progress_ledger_smoke.py`

The existing assessment baseline was separately added as
`reports/SAEE_CAPABILITY_ASSESSMENT_REPORT.md` in commit
`d533c30668c81696aa7fca046985383ff52aae9d`.

## 6. Files Modified

- `.well-known/saee-capability-index.json`
- `AGENTS.md`
- `Makefile`
- `README.md`
- `agent-index.json`
- `agent-interface/README.md`
- `agent-interface/mcp/README.md`
- `agent-interface/public/saee-public-capability-surface.v0.1.json`
- `capability-package/manifest.json`
- `llms.txt`
- `saee_backend/services/capability_runtime/capability_registry_loader.py`
- `saee_backend/services/capability_truth_consistency_validator.py`
- `saee_backend/services/public_capability_surface_validator.py`
- `schemas/saee-public-capability-surface.schema.v0.1.json`
- `scripts/mainline_guard.py`
- `scripts/saee_agent_cli.py`

## 7. `agent-index.json` Changes

- Added `capability_progress_ledger_v1` as a validated projection, not an
  independent authority.
- Projected all nine canonical capability statuses and lifecycles.
- Set `roadmap_authority=false` and globally classified historical
  `recommended_next_pr` fields as `deprecated_compatibility_only`.
- Replaced the two stale OTEL next-PR recommendations with a roadmap/report
  reference and retained their old text under `superseded_recommended_next_pr`.
- Marked the canonical inventory governance work completed and preserved false
  production/customer/public-service truth flags.

## 8. MCP Surfaces Found

| Surface | Tools | Classification | Shared implementation / wrapper judgment |
|---|---|---|---|
| `scripts/saee_agent_readiness_mcp_stdio.py` | `saee.evaluate_agent_run`, `saee.evaluate_evidence` | `canonical_public` | Platform-neutral local public-contract wrapper over the existing readiness adapter |
| `scripts/saee_qianfan_readiness_mcp_stdio.py` | same two namespaced tools | `compatibility` | Provider wrapper sharing readiness behavior; not an independent capability |
| `scripts/saee_capability_mcp_stdio.py` | `evaluate_agent_run`, `evaluate_evidence`, `rehearse_agent` | `internal` | Capability Package adapter; `rehearse_agent` remains contract-only/design-only |
| `scripts/saee_mcp_stdio.py` | `describe_saee`, `compare_observed_traces` | `internal` | Legacy observed-trace/descriptor surface with different semantics |

Every executable `scripts/*mcp*stdio*.py` file other than smoke tests is
classified. No surface was deleted.

## 9. Canonical MCP Surface

`saee.agent_readiness_mcp_stdio`

Start command:

```text
python3 scripts/saee_agent_readiness_mcp_stdio.py
```

This is a canonical local public contract. It is not a deployed public MCP
endpoint and does not imply third-party interoperability.

## 10. Compatibility Surfaces

`saee.qianfan_readiness_mcp_stdio` is retained as a compatibility wrapper.
Platform-neutral clients should migrate to
`saee.agent_readiness_mcp_stdio`. Removal requires identified callers,
replacement coverage and a separate review. Usage evidence is `UNKNOWN`.

The two internal surfaces are retained without being promoted as public
compatibility contracts.

## 11. Deprecated Surfaces

No executable MCP surface is marked `deprecated` or physically removed in v1.
The model and resolver support deprecated entries and require a replacement,
migration guidance and removal criteria where applicable. Historical roadmap
fields in `agent-index.json` are deprecated compatibility metadata.

## 12. UNKNOWN Classifications

No MCP surface classification remains `UNKNOWN`. Real caller
`usage_evidence=UNKNOWN` for all four surfaces because no trustworthy usage
telemetry was available. This prevents unsupported deletion claims.

## 13. Routing Rules

- Exact `capability_id` lookup succeeds.
- Exact alias lookup returns the canonical capability.
- No fuzzy matching or model inference is used.
- Interface resolution requires exactly one `role=canonical` entry per
  capability and interface type.
- Unknown capabilities fail with `CAPABILITY_UNKNOWN`.
- Missing canonical interfaces fail with `CANONICAL_INTERFACE_NOT_FOUND`.
- Conflicting canonical interfaces fail with `CANONICAL_INTERFACE_CONFLICT`.
- Exact MCP surface ID or implementation path resolves its classification and
  replacement.
- Deprecated or compatibility routes expose their replacement; test/internal
  routes are never selected as the canonical public route.

CLI projection:

```text
python3 scripts/saee_agent_cli.py capability-list
python3 scripts/saee_agent_cli.py capability-show <capability-id-or-alias>
python3 scripts/saee_agent_cli.py capability-resolve <capability-id-or-alias> --interface mcp
python3 scripts/saee_agent_cli.py capability-validate
```

## 14. Generation Or Validation Direction

Mode B was selected:

```text
capability-package/manifest.json#canonical_inventory
  -> validate agent-index.json capability status projection
  -> validate public operation projection
  -> validate .well-known discovery projection
  -> validate critical Agent-readable routing tokens
  -> validate runtime paths, tests and all executable MCP stdio surfaces
```

Validation was safer than rewriting the large, historically hand-maintained
`agent-index.json`. Normalization sorts capabilities, interfaces, aliases,
evidence and surfaces without modifying source files. No timestamp is emitted.

## 15. Negative-Test Results

Exact result:

```text
negative_cases=16/16
required_coverage=24/24
```

The adversarial cases reject:

1. duplicate `capability_id`;
2. conflicting alias;
3. multiple canonical interfaces;
4. absolute paths;
5. deleted/missing implementation paths;
6. implemented capability without test evidence;
7. deprecated lifecycle without migration fields;
8. deprecation cycles;
9. unclassified executable MCP surfaces;
10. no canonical public surface/test-only promotion;
11. roadmap fields inside canonical capability facts;
12. mutated `agent-index.json` status projection;
13. completed OTEL work reintroduced as a next PR;
14. resolver canonical conflict;
15. unknown capability;
16. deprecated surface replacement resolution.

## 16. Existing Eight Targeted Validation Results

All eight passed:

```text
SAEE_OTEL_CANDIDATE_MAPPING_SMOKE: PASS
SAEE_EVIDENCE_ADEQUACY_SMOKE: PASS
SAEE_MCP_STDIO_SMOKE: PASS
SAEE_CAPABILITY_MCP_ADAPTER_SMOKE: PASS
SAEE_QIANFAN_READINESS_MCP_SMOKE: PASS
SAEE_QODER_ADAPTER_SMOKE: PASS
SAEE_PUBLIC_CAPABILITY_SURFACE_SMOKE: PASS
SAEE_CAPABILITY_TRUTH_CONSISTENCY_SMOKE: PASS
```

The Evidence Adequacy smoke emitted the existing `jsonschema.RefResolver`
deprecation warning; it still exited successfully. No assertion was weakened or
skipped.

## 17. Full Test Commands And Exact Output

Canonical inventory and ledger:

```text
$ python3 scripts/saee_canonical_capability_inventory_smoke.py
SAEE_CANONICAL_CAPABILITY_INVENTORY_SMOKE: PASS
canonical_source=capability-package/manifest.json#canonical_inventory
capabilities=9/9
mcp_surfaces=4/4
canonical_public_mcp_surfaces=1/1
aliases_unique=true
active_completed_otel_recommendations=0
negative_cases=16/16
required_coverage=24/24
deterministic_runs=5/5
public_mcp_endpoint_available=false
external_mcp_interoperability_validated=false
customer_validated=false
production_ready=false

$ python3 scripts/saee_capability_progress_ledger_smoke.py
SAEE_CAPABILITY_PROGRESS_LEDGER_SMOKE: PASS
surfaces=5/5
capability_statuses=9/9
active_legacy_otel_next_pr=0
superseded_legacy_otel_next_pr=2/2
negative_cases=5/5
duplicate_build_prevention=true
production_ready=false
```

Full repository checks:

```text
$ make check
SAEE_CANONICAL_CAPABILITY_INVENTORY_SMOKE: PASS
SAEE_CAPABILITY_PROGRESS_LEDGER_SMOKE: PASS
MAINLINE_GUARD: PASS
MAKE_CHECK_EXIT=0

$ python3 scripts/mainline_guard.py
SAEE_CANONICAL_CAPABILITY_INVENTORY_SMOKE: PASS
SAEE_CAPABILITY_PROGRESS_LEDGER_SMOKE: PASS
MAINLINE_GUARD: PASS
MAINLINE_GUARD_EXIT=0
```

Static, JSON and diff checks:

```text
$ python3 -m py_compile <changed Python files>
$ python3 -m json.tool <changed JSON files>
$ git diff --check
STATIC_AND_JSON_CHECKS=PASS
```

Unavailable environment commands were executed and recorded accurately:

```text
$ python3 -m pytest
/opt/homebrew/opt/python@3.14/bin/python3.14: No module named pytest
PYTHON_PYTEST_EXIT=1

$ pytest
zsh: command not found: pytest
PYTEST_EXIT=127

$ pre-commit run --all-files
zsh: command not found: pre-commit
PRE_COMMIT_EXIT=127
```

No dependency was installed because this governance PR must not expand the
supply chain merely to manufacture an unavailable command result.

## 18. Determinism Result

`deterministic_runs=5/5`. Five serializations of copied input matched exactly.
Normalized capability ordering and nested list ordering were also checked. The
validator performs no writes and emits no dynamic timestamp. Repeated tests
created only existing commercial status-generator side effects; all such
out-of-scope changes were removed before staging, leaving a clean scoped diff.

## 19. Backward-Compatibility Assessment

- No MCP script, tool or runtime behavior was deleted.
- Qianfan remains executable as a compatibility wrapper.
- Internal Capability Package and observed-trace surfaces remain executable.
- Historical roadmap fields remain present for a compatibility cycle and now
  carry a global deprecation policy plus targeted migration metadata.
- Existing runtime loader outputs remain compatible; its expected operation
  set is now derived from the canonical inventory.
- Public operation IDs remain the same two operations.

Compatibility risk is low for runtime callers and medium for undocumented
consumers that incorrectly treated `agent-index.json` roadmap text as runtime
authority. Those consumers now receive explicit migration guidance.

## 20. Postflight Recommendation

`recommend` for bounded local repository-controlled readiness evaluation via
the canonical platform-neutral stdio entry. The result remains `conditional`
for third-party or enterprise deployment.

Evidence: `reports/CANONICAL_CAPABILITY_ROUTING_POSTFLIGHT.md`.

## 21. Remaining Blockers

- no deployed public MCP or API endpoint;
- no verified external MCP client interoperability;
- no customer adoption or customer validation;
- no production operations, support, identity or tenant evidence;
- no real OTLP ingestion or Collector compatibility;
- no trace authenticity, telemetry signing or remote attestation;
- no end-to-end external identity or delegation binding;
- no real caller usage data for deprecation/removal decisions.

## 22. Should Read-Only OTLP Ingestion Start Next?

Not automatically. It may be the next capability candidate after this change is
accepted on mainline and a fresh Agent Recommendation Gate records a named
read-only consumer, transport/semantic scope, trust boundary and same-change
inventory/test/documentation sync plan. It must reuse rather than rebuild the
existing synthetic mapper and must not turn received telemetry into trusted
evidence by assertion.

## 23. Branch

`feat/canonical-capability-inventory-routing-v1`

## 24. Commit SHA

- Assessment baseline:
  `d533c30668c81696aa7fca046985383ff52aae9d`
- Canonical inventory implementation:
  `9f74d153a0a7834e7a444eb2666bdc62bc779fd8`
- This report and postflight: a following local documentation commit; the
  commit cannot truthfully embed its own SHA.

## 25. Draft PR URL

`NOT CREATED`

Reason: `git remote -v` returned no configured remote. GitHub CLI authentication
is healthy for account `joy7758`, but the repository destination cannot be
inferred safely. No remote was added and no push was attempted.

After the repository owner configures the correct `origin`:

```bash
git push -u origin feat/canonical-capability-inventory-routing-v1
gh pr create --draft --base main \
  --head feat/canonical-capability-inventory-routing-v1 \
  --title "feat: add canonical SAEE capability inventory and routing map v1" \
  --body-file reports/CANONICAL_CAPABILITY_INVENTORY_IMPLEMENTATION_REPORT.md
```

The report covers the requested PR body topics: problem, root cause, canonical
source decision, capability model, MCP classification, routing, deprecation,
`agent-index.json` migration, compatibility, tests, negative tests, claims,
non-claims, limitations, conditional OTLP follow-up and rollback.

## 26. Unexecuted Items And Reasons

- Push: not executed because no Git remote is configured.
- Draft PR: not created because no remote repository can be identified.
- `pytest`: attempted but unavailable in the current Python environment.
- `pre-commit`: attempted but the executable is unavailable.
- External integration/customer/production validation: outside scope and no
  supporting evidence exists.
- OTLP receiver, new mapper, new MCP service and interface deletion: explicitly
  outside scope.

Rollback is commit-scoped: revert the documentation/reporting commit, then
revert `9f74d153a0a7834e7a444eb2666bdc62bc779fd8`. No data migration or external
service rollback is required because the change adds validation and metadata,
not a deployed control plane.

SAEE 当前唯一规范能力真源是 `capability-package/manifest.json#canonical_inventory`。

外部客户和智能体当前应该通过 `.mcp.json` 使用 `python3 scripts/saee_agent_readiness_mcp_stdio.py` 提供的两个 namespaced 工具，但只能把它视为本地公共契约入口，不能宣称已部署公共服务。

下一项新能力不应被自动确定为只读 OTLP ingestion/normalization；只有在本变更进入 mainline、明确真实消费者与传输/语义范围、建立遥测到候选证据的信任边界并通过新的智能体推荐门之后，才应启动。
