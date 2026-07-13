# SAEE MCP Capability Boundary Contract v0.1

## Scope

This boundary applies only to the design for the future `evaluate_evidence_adequacy` MCP tool. It does not modify or describe the authority of other historical/local MCP adapters in the repository.

SAEE MCP exposure would provide evidence adequacy evaluation capability. It would not provide authorization, deployment approval, or certification.

SAEE 的 MCP 暴露提供证据充分性评估能力，不提供授权、部署批准或认证。

## Mandatory Boundaries

```text
MCP Interface != Capability Trust
Tool Exposure != Authorization
Tool Result != Deployment Decision
MCP Availability != Production Readiness
```

The future MCP layer must not:

- authorize, approve, reject, block or deploy an Agent or system;
- certify safety, security, compliance or legal status;
- retrieve observation references or silently promote them into evidence;
- guess missing evidence, profiles or accountability claims;
- expand caller permissions or execute evidence content;
- reinterpret `SUPPORTED` as deployment approval.

Human or separately authorized governance retains consequential decision authority.

## Current Truth Surface

```text
implementation_status=design_only
server_available=false
public_endpoint_available=false
external_agents_connected=false
mcp_compatibility_completed=false
production_ready=false
```

`server_available=false` is scoped to the proposed `evaluate_evidence_adequacy` tool. The repository has a separate historical local stdio adapter for observed-trace evaluation; Phase 4.7 does not modify, extend or validate that adapter.
