# SAEE MCP Capability Prototype Design v0.1

## 1. Purpose

This document defines a future MCP representation for the SAEE Evidence Adequacy Capability Object.

MCP is a transport/interface concept. SAEE remains responsible for evidence adequacy evaluation through its existing fixed local evaluator and Tool contracts.

This phase defines metadata, mappings and boundaries only. It does not implement an MCP server, advertise a public endpoint, connect an external Agent or establish MCP compatibility.

```text
Capability Object
        ↓
MCP Tool Description
        ↓
MCP Invocation
        ↓
SAEE Evaluation
```

## 2. Capability Object Mapping

| Capability Object field | Future MCP tool metadata | Rule |
|---|---|---|
| `object_id` | capability provenance reference | Must remain `saee:capability:evidence-adequacy:0.1` |
| `identity.capability_id` | logical capability identity | Does not become caller authorization |
| `identity.version` | mapping and contract version | Must remain aligned with both schemas |
| `metadata.description` | bounded Tool description | No marketing, trust or certification claim |
| `contracts.input` | Tool input schema reference | Reuse; do not duplicate schema |
| `contracts.output` | Tool output schema reference | Reuse; do not duplicate schema |
| `boundaries` | MCP boundary contract | Must remain fail closed |
| `lifecycle.state` | exposure state mapping | `LOCAL_PROTOTYPE` maps only to `DESIGN_ONLY` |

Conceptual mapping:

```json
{
  "capability_object_id": "saee:capability:evidence-adequacy:0.1",
  "mcp_tool_name": "evaluate_evidence_adequacy",
  "implementation_status": "design_only"
}
```

## 3. MCP Tool Definition

Design-only Tool name:

`evaluate_evidence_adequacy`

Description:

`Evaluate evidence sufficiency for defined accountability claims.`

Input contract reference:

`agent-interface/capabilities/saee-evaluate-evidence-tool.v0.1.schema.json`

Output contract reference:

`agent-interface/capabilities/saee-evaluate-evidence-output.v0.1.schema.json`

The mapping does not copy either schema. A later prototype must load and validate against the canonical contracts rather than maintain MCP-specific duplicates.

Repository scope note: an older local stdio MCP adapter already exposes `describe_saee` and `compare_observed_traces` for an observed-trace workflow. It is a separate capability surface. This design neither extends that adapter nor treats its existence as implementation evidence for `evaluate_evidence_adequacy`.

## 4. Input Mapping

```text
MCP input field        SAEE Tool input field       Required
evidence_object        evidence_object             yes
accountability_claim   accountability_claim        yes
evaluation_profile     evaluation_profile          yes
observation_references observation_references      no
```

Mapping is one-to-one. Unknown root fields remain forbidden. The MCP layer must not fetch, resolve or execute any reference.

`observation_references` are inert provenance references. They are not evidence and cannot satisfy an evidence profile.

## 5. Output Mapping

The canonical SAEE Tool output remains authoritative. A future MCP response would preserve:

- `claim_assessment`;
- `evidence_sufficiency_status`;
- `missing_requirements`;
- `reason_codes`;
- `limitations`;
- `boundary_statement`.

`tool_result` remains the transport/domain status field. The MCP layer must not rename `SUPPORTED` to `APPROVED`, omit limitations, or suppress the boundary statement.

## 6. Security Boundary

The MCP layer must not authorize, approve, block, deploy, certify or make a legal judgment. It must not execute the submitted evidence, install dependencies, resolve external URLs, persist customer data by default or broaden caller permissions.

The caller must not infer:

```text
SUPPORTED = event truth
SUPPORTED = system safety
SUPPORTED = compliance
SUPPORTED = deployment approval
```

Full contract: `docs/architecture/SAEE_MCP_BOUNDARY_CONTRACT.md`.

## 7. Error Handling

| Condition | Required domain result |
|---|---|
| Invalid or undeclared input | `REJECTED_INPUT` |
| Unknown or mismatched profile | `REJECTED_INPUT` |
| Evidence package lacks required fields or relationships | `INSUFFICIENT_EVIDENCE` |
| Missing information | Never guessed; report missing requirements or reject input |

Protocol framing errors and SAEE domain results must remain distinguishable in a later implementation. Phase 4.7 does not select an MCP SDK or protocol runtime.

## 8. Lifecycle Mapping

```text
Capability Object lifecycle: LOCAL_PROTOTYPE
MCP exposure state:          DESIGN_ONLY
server_available:            false
production_ready:            false
```

The design cannot promote the Capability Object to `EXTERNAL_VALIDATION` or `PRODUCTION_CAPABILITY`. A future local prototype requires a separate explicit gate and implementation review.

## 9. Security Considerations

A future prototype must retain:

- local-only, closed JSON request handling;
- canonical request size, depth and node limits;
- duplicate-key and unknown-field rejection;
- no observation fetching;
- no evidence value reflection beyond the existing output contract;
- no network requirement or persistence by default;
- no dynamic Tool registration;
- human authority for consequential decisions.

Caller identity, host permissions, tenant isolation, secret handling and protocol-version selection remain unresolved design inputs for anything beyond a local prototype.

## 10. Validation Plan

Current design validation checks:

- Capability Object identity and reference;
- canonical Tool name;
- canonical input/output schema references and versions;
- one-to-one input field mapping;
- required output and boundary fields;
- error semantics;
- `LOCAL_PROTOTYPE → DESIGN_ONLY` lifecycle mapping;
- false availability, compatibility and production flags;
- rejection of authorization or certification claims.

Run:

```bash
python3 scripts/saee_mcp_capability_design_smoke.py
```

Passing design validation does not establish MCP interoperability, server availability, external Agent integration or production readiness.

## 11. Post-Design Implementation Status

After separate Phase 4.8 approval, the design was projected into a dependency-free in-memory local prototype. The design instance remains an immutable `design_only` record; implementation truth is documented separately in `docs/architecture/SAEE_LOCAL_MCP_PROTOTYPE.md`.

The prototype does not establish a public Server, standardized-runtime interoperability, external Agent integration, authentication or production readiness.

## 12. Future External Agent Boundary

External-Agent use remains gated by `docs/architecture/SAEE_EXTERNAL_AGENT_INTEGRATION_DESIGN.md` and the machine-readable design at `agent-interface/integration/saee-external-agent-integration-design.v0.1.json`.

The gate remains `HOLD`. Identity declaration, discovery and invocation do not establish authentication, trust, authorization or permission.
