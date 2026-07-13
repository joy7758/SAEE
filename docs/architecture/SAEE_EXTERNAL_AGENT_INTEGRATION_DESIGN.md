# SAEE External Agent Capability Integration Design v0.1

## 1. Purpose

This document defines the identity, invocation, data, tenant, secret and human-control boundaries required before any future external Agent may use the SAEE Evidence Adequacy capability.

It does not establish external integration.

```text
Agent Identity != Agent Trust
Agent Invocation != Agent Authorization
SAEE Evaluation != Autonomous Decision
External Integration Design != External Integration Completed
```

## 2. Integration Architecture

```text
External Agent
        ↓ declared identity and purpose only
Agent Capability Discovery
        ↓ capability fit and non-use boundaries
MCP / Capability Interface
        ↓ bounded request, no permission expansion
SAEE Capability Object
        ↓ versioned identity, contracts and provenance
Evidence Adequacy Evaluation
        ↓ assessment, gaps, limitations and reason codes
Human Review Boundary
        ↓ separately authorized consequential decision
```

### Responsibilities

| Component | Responsibility | Explicit non-responsibility |
|---|---|---|
| External Agent | Declare identity context, purpose and bounded request | Does not self-authorize or establish trust |
| Discovery layer | Describe capability fit, contracts and limitations | Does not grant access or permission |
| MCP interface | Validate and transport a closed request | Does not authenticate, authorize or execute the world |
| Capability Object | Bind versioned metadata and contracts | Does not certify the capability or caller |
| SAEE evaluator | Assess profile-specific evidence sufficiency | Does not approve, deploy, block or certify |
| Human review | Interpret results under authorized governance | Remains outside automatic SAEE control |

The digital organism may observe declared external inputs but may not execute external-world actions.

## 3. Agent Identity Model

Future callers must provide an Agent Identity Object containing:

```json
{
  "agent_id": "",
  "agent_type": "",
  "declared_purpose": "",
  "organization_context": "",
  "capability_context": ""
}
```

- `agent_id` is a caller-supplied correlation identifier, not verified identity.
- `agent_type` describes the caller category, not its intelligence or safety.
- `declared_purpose` is untrusted input until policy and human review accept it.
- `organization_context` does not establish organizational authority.
- `capability_context` identifies intended capability use, not permission.

Identity declaration is not authentication. Identity declaration is not trust. No trusted-Agent allowlist exists in this phase.

## 4. Invocation Policy Model

Future policy may allow an authenticated and separately authorized caller to:

- submit a bounded evidence package;
- request one supported accountability assessment;
- select one fixed evaluation profile;
- receive a bounded assessment, missing-evidence list, reason codes and limitations.

It must not allow the caller to:

- authorize an action;
- approve deployment;
- modify source evidence through the evaluation interface;
- bypass human review;
- register dynamic Tools or profiles;
- cause external execution;
- convert a result into automatic blocking or release.

Declared purpose is not trusted purpose. Capability access is not a permission grant.

## 5. Data Boundary Model

Allowed input classes:

- `evidence_object`;
- `accountability_claim`;
- `evaluation_profile`;
- explicitly approved inert references.

Forbidden input classes:

- passwords, API keys, access tokens, private keys or other secrets;
- hidden reasoning or chain-of-thought;
- uncontrolled customer or personal data;
- unrestricted external resources or executable content;
- raw production logs without separate data approval;
- data from another Tenant namespace.

References must not be fetched automatically or promoted into Evidence. Customer data remains forbidden until a separately approved policy, consent, retention and deletion model exists.

## 6. Tenant Isolation Model

Design-only namespace model:

```text
Agent A / Tenant A
        ↓
Evidence Namespace A

Agent B / Tenant B
        ↓
Evidence Namespace B
```

Required future properties:

- explicit Tenant identity and namespace binding;
- deny-by-default cross-Tenant access;
- Tenant-scoped request, evidence, result and audit identifiers;
- no shared mutable working directory;
- deletion and retention applied per Tenant;
- failure must not disclose existence or content of another namespace.

No Tenant system or namespace isolation is implemented by this design.

## 7. Secret Management Model

Before external integration, a separately reviewed secret system must provide:

- credential isolation from requests and evidence;
- least-privilege credentials;
- rotation and revocation;
- environment- or secret-manager injection rather than repository storage;
- redaction from logs, reports, fixtures and error messages;
- incident response for suspected exposure.

No credential, token, private key, OAuth secret or authentication material is created or stored in this phase.

## 8. Human Control Boundary

SAEE may:

- evaluate evidence sufficiency against a fixed profile;
- identify missing fields and relationships;
- return stable reason codes, limitations and bounded reports.

SAEE may not:

- authenticate or trust an Agent;
- authorize actions;
- approve or reject deployment;
- execute, block or mutate external systems;
- certify safety, security or compliance;
- make a legal judgment;
- bypass the responsible human or separately authorized governance process.

Human approval remains required before any real integration, data acceptance, Pilot action or consequential use of a result.

## 9. External Integration Readiness Gate

Current gate:

```text
gate_status=HOLD
external_agent_connected=false
real_integration_authorized=false
pilot_start_authorized=false
```

Required before a real integration request can be considered:

1. approved external-data and retention policy;
2. reviewed identity and authentication design;
3. Tenant namespace and isolation design;
4. secret-management and credential-rotation design;
5. security and privacy review;
6. logging, failure handling and incident-response model;
7. human escalation and approval path.

Completion of documents alone does not open the gate. Each control requires implementation evidence, negative testing and explicit human authorization.

## 10. Future Pilot Requirements

A future Pilot must additionally define:

- named scope owner and termination authority;
- synthetic-first or explicitly consented data;
- one allowlisted Agent and one allowlisted capability;
- bounded request count, size and duration;
- no external side effects;
- rollback and deletion procedure;
- evidence package and post-Pilot human review;
- separate approval to move beyond simulation.

## 11. Current Truth Surface

```text
design_status=design_only
external_agent_connected=false
authentication_available=false
oauth_available=false
public_mcp_server_available=false
trusted_external_agent=false
autonomous_execution=false
tenant_system_implemented=false
credentials_stored=false
production_enabled=false
production_ready=false
human_approval_required=true
```

## 12. Synthetic Simulation Reference

Phase 5.1 provides a local offline simulation at:

- identity schema: `agent-interface/integration/synthetic-agent.schema.v0.1.json`;
- Tenant label schema: `agent-interface/integration/tenant-context.schema.v0.1.json`;
- scenarios: `agent-interface/integration/simulation/`;
- simulator: `saee_backend/services/external_agent_simulator.py`;
- machine result: `agent-interface/integration/saee-external-agent-simulation-result.v0.1.json`;
- documentation: `docs/architecture/SAEE_EXTERNAL_AGENT_SIMULATION.md`.

The simulation demonstrates fail-closed boundary ordering with synthetic inputs only. It does not complete external integration, implement authentication or Tenant isolation, validate a real Agent, open the readiness gate, or authorize a Pilot.

## 13. Controlled Pilot Design Reference

Phase 5.2 defines a future controlled external Agent Pilot design at:

- machine contract: `agent-interface/integration/saee-controlled-pilot-design.v0.1.json`;
- design document: `docs/commercial/SAEE_CONTROLLED_EXTERNAL_AGENT_PILOT_DESIGN.md`;
- offline validator: `saee_backend/services/pilot_design_validator.py`;
- validation command: `python3 scripts/saee_controlled_pilot_design_smoke.py`.

The controlled external Agent Pilot design freezes scope, eligibility, data boundaries, five approval gates, metrics, exit conditions and rollback requirements. It does not grant any gate, connect an Agent, collect data, authorize or execute a Pilot, validate a customer, or change the Phase 5.0 readiness gate from `HOLD`.
