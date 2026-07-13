# SAEE MCP stdio Adapter

> Routing status: this document describes the internal legacy observed-trace
> surface. New local external-Agent integrations use `.mcp.json` and
> `python3 scripts/saee_agent_readiness_mcp_stdio.py`. Canonical classification
> and migration rules are in `docs/CAPABILITY_INVENTORY.md` and
> `capability-package/manifest.json#canonical_inventory`.

启动命令 / Start command:

```bash
python3 scripts/saee_mcp_stdio.py
```

固定工具 / Fixed tools:

- `describe_saee`
- `compare_observed_traces`

协议 / Protocol:

- MCP revision `2025-11-25`
- UTF-8 newline-delimited JSON-RPC over stdio
- `initialize` → `notifications/initialized` → `tools/list` / `tools/call`

边界 / Boundary:

The adapter accepts the observed bundle inline as `arguments`; it accepts no
path, URL, command, module, prompt, message, tool payload, code, secret, or raw
log field. It has no network, subprocess, dynamic tool, resources, prompts,
workflow orchestration, trace capture, or private-core capability.

## Evidence Adequacy MCP Design (not implemented)

Phase 4.7 defines a separate design-only mapping for a future
`evaluate_evidence_adequacy` Tool:

- mapping schema: `saee-mcp-capability-mapping.schema.v0.1.json`;
- design instance: `examples/saee-evaluate-evidence-mcp-tool-design.v0.1.json`;
- design specification: `docs/architecture/SAEE_MCP_CAPABILITY_DESIGN.md`;
- validation: `python3 scripts/saee_mcp_capability_design_smoke.py`.

This mapping does not modify the stdio adapter above and does not add a Tool,
server, endpoint, MCP compatibility claim, external Agent connection, or
production capability. For the target Tool, `implementation_status=design_only`
and `server_available=false`.

## Evidence Adequacy Local Prototype

Phase 4.8 adds a separate dependency-free, in-memory single-Tool prototype:

- service: `saee_backend/services/local_mcp_server.py`;
- handler: `saee_backend/services/mcp_evidence_tool_handler.py`;
- request schema: `saee-mcp-local-request.schema.v0.1.json`;
- response schema: `saee-mcp-local-response.schema.v0.1.json`;
- examples: `examples/local-mcp/`;
- validation: `python3 scripts/saee_local_mcp_prototype_smoke.py`.

It does not modify the stdio adapter, listen on a port, provide public access,
authenticate users, connect external Agents, or establish MCP interoperability
or production readiness.

## Local Invocation Evaluation

The synthetic caller evaluation is available at:

- scenarios: `invocation-evaluation/examples/`;
- machine result: `saee-mcp-invocation-evaluation-result.v0.1.json`;
- scenario schema: `../../schemas/saee-mcp-invocation-evaluation.schema.v0.1.json`;
- evaluator: `saee_backend/services/mcp_invocation_evaluator.py`;
- validation: `python3 scripts/saee_mcp_invocation_evaluation_smoke.py`.

It tests usage correctness only. `mcp_public=false`,
`external_clients_tested=false`, `external_agents_tested=false`, and
`production_ready=false`.

## Future External Agent Integration Design

The design-only boundary contract is:

- architecture: `docs/architecture/SAEE_EXTERNAL_AGENT_INTEGRATION_DESIGN.md`;
- machine design: `../integration/saee-external-agent-integration-design.v0.1.json`;
- validation: `python3 scripts/saee_external_agent_integration_design_smoke.py`.

It creates no Agent connection, authentication, Tenant system, credentials,
public MCP Server or Pilot authorization. `readiness_gate=HOLD`.
