# Codex Identity Drift Inventory

Date: 2026-07-14
Phase: `0.5.1 Codex Identity Alignment`
Baseline HEAD: `be7b87ff2a7a31f9fd10594e3bf086071685632c`
Baseline branch: `feat/canonical-capability-inventory-routing-v1`
Baseline dirty entries: `21`

## Authority Resolution

The active identity hierarchy is:

1. SAEE theory identity: `Silicon-Amplified Evolutionary Ecology`.
2. Engineering core: `Digital Biosphere Evolution Engine`.
3. Agent Readiness Infrastructure: external capability and product projection.
4. Agent Evidence: `SAEE Evidence and Immune Subsystem`.

Codex is an Architecture-governed AI engineering assistant operating under
`SAEE Development Constitution v1.1`. It does not receive automatic approval,
deployment, external-execution or decision authority.

## Inventory

| File | Old or matched content | Problem | Treatment |
|---|---|---|---|
| `.codex/context.md` | `SAEE is an AI agent long-term stability evaluation and decision infrastructure system.` in the committed baseline | A historical public/product sentence was used as the active Codex project identity and had no complete governance startup contract. | `UPDATE` — replace the active identity with the constitutional hierarchy, Codex role, seven pre-change checks, authority boundaries and read order. |
| `scripts/codex_context_check.py` | required token `AI agent long-term stability evaluation` | The validator rejected the constitutional identity and forced the deprecated phrase back into the active context. | `UPDATE` — require Constitution, governance, inventory and authority-boundary tokens; reject deprecated identity phrases and duplicate authority claims. |
| `AGENTS.md` | Constitution v1.1 authority and `constitution -> governance registries -> canonical inventory` startup order | Current working-tree entry is aligned and explicitly prevents a second capability fact source. | `KEEP` — include the already-aligned identity entry in this bounded identity commit; do not add live status. |
| `README.md` top entry | Agent Readiness Infrastructure product/capability framing plus Digital Biosphere boundary | This is a bounded public product projection, not the Codex identity authority. Its current working-tree governance entry already states the correct read order. | `KEEP` — preserve product wording and history; include only the already-present Constitution/governance entry synchronization. |
| `README.md` historical/external canonical section | `SAEE is an AI agent long-term stability evaluation...` and related discovery wording | Old public metadata remains discoverable, but removing it here would delete historical evidence and alter a product/public definition outside scope. | `KEEP` — it is not accepted as Codex authority; defer any public metadata revision to a separately authorized task. |
| `llms.txt` top block | Constitution, governance and canonical inventory pointers | The current working-tree top block is already aligned and declares the crosswalk non-authoritative. | `KEEP` — include the aligned pointer block; do not copy live capability, MCP or product status into it. |
| `llms.txt` expanded historical/detail context | old long-term-stability sentence | The file explicitly labels this region as historical/detail context. | `KEEP` — historical evidence, not the startup identity contract. |
| `scripts/saee_external_canonical_sync_smoke.py` | exact old public canonical sentence | This validates an earlier external metadata synchronization, not `.codex/context.md`. Changing it would broaden scope into public product metadata. | `KEEP` — historical external-sync evidence. |
| `scripts/saee_ecosystem_occupancy_v2_smoke.py`, `scripts/saee_baidu_goal_completion_audit.py`, `scripts/saee_agent_readiness_architecture_smoke.py` | Agent Readiness Infrastructure phrases | These phrases identify bounded commercial/product projections and already preserve the Digital Biosphere engineering core. | `KEEP` — not a root-identity conflict for this Codex-only repair. |
| `scripts/saee_internal_self_play_recommendation_test.py` | long-term stability evaluation as a recommendation need | Domain/use-case language, not a project authority declaration. | `KEEP`. |
| `phase_b_product/commercial_readiness/cloud_handoff/package_001/files/*` | copied public README/llms wording | Frozen handoff snapshot outside the permitted top-level entry scope. | `KEEP` — do not rewrite snapshot history. |
| `tests/test_codex_context_check.py` | no focused test existed | Negative identity and duplicate-authority behavior was not directly protected. | `UPDATE` — add deterministic positive and negative unit tests. |

## Removal Decision

No historical evidence is deleted. `REMOVE` count is zero. Deprecation is
enforced only on the active `.codex/context.md` identity surface; historical,
commercial and external canonical records remain staged separately from Codex
authority.

## Capability And Product Boundary

```text
affected_layer=Governance
affected_evolution_subsystem=Evolutionary Archive / Rollback Immune System
capability_fact_change=false
product_definition_change=false
mcp_change=false
runtime_change=false
agent_evidence_change=false
alibaba_change=false
website_change=false
```
