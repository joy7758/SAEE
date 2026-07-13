# SAEE MCP Local Prototype v0.1

## 1. Purpose

This local MCP prototype demonstrates protocol mapping. It is not a production MCP service.

该本地 MCP 原型用于验证协议映射，不是生产 MCP 服务。

The prototype validates one local closed loop:

```text
Capability Object
        ↓
MCP Tool Mapping
        ↓
in-memory LocalMCPServer
        ↓
MCP Evidence Tool Handler
        ↓
existing evaluate_evidence_tool()
        ↓
canonical Evidence Adequacy evaluator
```

MCP remains a communication/interface layer. SAEE remains responsible for the bounded evidence adequacy evaluation.

## 2. Dependency Decision

Repository dependency inspection found no MCP SDK or `modelcontextprotocol` package in `saee_backend/requirements.txt`.

Phase 4.8 therefore uses Option B: a dependency-free, protocol-compatible local abstraction with fixed `list_tools` and `call_tool` methods. No package was installed, no network was accessed, and no subprocess or stdio listener was started.

This abstraction is not a claim of completed MCP interoperability. A later interoperability phase must select and validate an approved protocol runtime separately.

## 3. Tool Definition

The prototype originally exposed one in-memory Tool and now exposes two fixed,
read-only Tools:

```text
name=evaluate_evidence_adequacy
name=evaluate_agent_run
read_only_intent=true
side_effects_allowed=false
```

The repository's older observed-trace stdio adapter remains separate. Phase 4.8 neither modifies it nor adds this Tool to it.

## 4. Input

Request schema:

`agent-interface/mcp/saee-mcp-local-request.schema.v0.1.json`

Required root fields:

- `tool_name`;
- `arguments`.

Arguments reuse the canonical Tool request schema rather than duplicating it:

`agent-interface/capabilities/saee-evaluate-evidence-tool.v0.1.schema.json`

Required arguments are `evidence_object`, `accountability_claim` and `evaluation_profile`. `observation_references` remains optional and inert. Unknown fields, authorization requests, unknown profiles and malformed arguments fail closed.

## 5. Output

Response schema:

`agent-interface/mcp/saee-mcp-local-response.schema.v0.1.json`

The Handler projects only:

- `tool_result`;
- `claim_assessment`;
- `evidence_sufficiency_status`;
- `missing_requirements`;
- `reason_codes`;
- `limitations`;
- `boundary_statement`.

It preserves the canonical Local Tool limitations and appends one transport-specific clarification: the Local Tool has no built-in MCP runtime, while this response is projected by a separate dependency-free in-memory prototype. The Local Tool source remains unchanged.

Allowed domain outcomes remain `SUPPORTED`, `INSUFFICIENT_EVIDENCE` and `UNKNOWN`. `APPROVED`, `CERTIFIED`, `SAFE` and `COMPLIANT` are not allowed assessment values.

## 6. Error Handling

| Error | Result |
|---|---|
| Unknown Tool | `MCP_TOOL_NAME_INVALID` / `REJECTED_INPUT` |
| Missing or malformed arguments | `MCP_ARGUMENTS_INVALID` / `REJECTED_INPUT` |
| Undeclared request field | `MCP_REQUEST_SCHEMA_INVALID` / `REJECTED_INPUT` |
| Invalid Tool arguments | Existing stable `TOOL_*` or `EVIDENCE_*` rejection |
| Missing evidence relationships | `INSUFFICIENT_EVIDENCE`, not input rejection |

The prototype never guesses missing information.

## 7. Security Boundaries

```text
MCP Server Prototype != Production Service
Tool Availability != Public Access
MCP Result != Authorization
MCP Transport != Trust Authority
```

The prototype has:

```text
mcp_local_prototype=true
network_accessed=false
subprocess_started=false
persistence_performed=false
public_endpoint_available=false
authentication_available=false
external_agents_connected=false
production_ready=false
```

It does not authorize, approve, certify, deploy, block, fetch references, execute evidence, persist input, authenticate users or isolate tenants. Human or separately authorized governance retains decision authority.

## 8. Local Simulation

```bash
python3 scripts/saee_local_mcp_client_demo.py \
  --input agent-interface/mcp/examples/local-mcp/valid_supported_request.json
```

This is an in-process synthetic caller, not an external Agent.

## 9. Validation

```bash
python3 scripts/saee_local_mcp_prototype_smoke.py
```

The Smoke verifies the fixed two-Tool registry, evidence Tool valid/invalid cases,
deterministic output, canonical Tool reuse, response Schema validity and absence
of network, subprocess, persistence, public endpoint or authentication capability.

## 10. Limitations

- no actual MCP SDK or standardized runtime handshake;
- no stdio or network transport for this Tool;
- no authentication, identity, tenant isolation or secrets model;
- no external Agent integration or interoperability result;
- no public deployment or production operations;
- no capability trust, authorization, safety, compliance or legal conclusion.
