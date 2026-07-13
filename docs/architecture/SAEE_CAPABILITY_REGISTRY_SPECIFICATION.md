# SAEE Capability Registry Specification v0.1

## 1. Registry Purpose

The registry specification gives future AI agents and agent ecosystems a stable machine-readable answer to seven questions:

1. What capability is this?
2. What version is described?
3. What lifecycle state applies?
4. How can the current implementation be invoked?
5. What inputs are required?
6. What outputs are produced?
7. What must never be inferred from the entry?

```text
Capability Registry Specification != Capability Marketplace
Capability Metadata != Capability Adoption
Registration Contract != Public Availability
Capability Description != Capability Trust
```

The current artifact is one local registry entry and its validation rules. It is not a public registry service, publishing workflow, catalogue, Marketplace, API or MCP server.

## 2. Capability Identity

Canonical registry identity:

```text
capability_id=saee.evidence-adequacy
version=0.1
alias=saee-evidence-adequacy
```

`capability_id` is the stable ecosystem-oriented identifier. `version` identifies the capability contract described by the card. Existing repository/public manifest identifiers remain aliases and are not silently renamed.

Identity does not establish publisher trust, external validation, adoption or availability.

## 3. Lifecycle State

| State | Meaning | Minimum evidence | Availability implication |
|---|---|---|---|
| `RESEARCH_PROTOTYPE` | Concept, schema or evaluation direction under research | Repository documentation and bounded examples | None |
| `LOCAL_PROTOTYPE` | Callable local implementation with offline validation | Local contracts, implementation and deterministic tests | Local only |
| `EXTERNAL_VALIDATION` | Separately approved real external validation is in progress or complete | Consent, external test protocol and external validation evidence | Does not imply production |
| `PRODUCTION_CAPABILITY` | Production operational capability has separately verified production evidence | External validation plus production security, identity, operations and governance evidence | Does not imply adoption or certification |

Current registry entry:

```text
lifecycle_state=LOCAL_PROTOTYPE
public_registry_available=false
public_tool_available=false
external_validation_completed=false
production_validation_completed=false
adoption_validated=false
```

The public discovery release still uses `stage=research_prototype`. That describes the public release surface. `LOCAL_PROTOTYPE` describes the existence of the repository-local callable prototype. These are separate scopes, not a production promotion.

## 4. Capability Card

Schema: `agent-interface/registry/saee-capability-registry.schema.v0.1.json`

Current card: `agent-interface/registry/saee-capability-card.v0.1.json`

The card includes:

- stable identity and alias;
- bilingual purpose;
- supported and forbidden use cases;
- public discovery identity and local-only availability;
- local invocation mode;
- input/output schema references;
- limitations and responsibility boundary;
- local/synthetic validation state;
- migration state for known public metadata drift.

## 5. Contract References

Input contract:

```text
agent-interface/capabilities/saee-evaluate-evidence-tool.v0.1.schema.json
schema_version=0.1
required=evidence_object,accountability_claim,evaluation_profile
optional=observation_references
```

Output contract:

```text
agent-interface/capabilities/saee-evaluate-evidence-output.v0.1.schema.json
schema_version=0.1
```

The validator checks that references stay inside the repository, exist, and contain the same `v0.1` contract version. It never resolves remote references.

## 6. Discovery and Invocation

The entry points to the canonical public discovery identity, but the entry itself is local only. Invocation is described as:

```text
mode=LOCAL_PYTHON_FUNCTION
transport=IN_PROCESS
network_required=false
side_effects_allowed=false
```

This invocation description does not publish the Tool or authorize an Agent to call it. Caller permission, data permission and consequential actions remain outside this registry entry.

## 7. Boundary Contract

Registry entries describe capability metadata. They do not:

- establish capability trust;
- verify publisher identity;
- authorize use;
- grant data access;
- approve, reject or deploy a system;
- certify security or compliance;
- provide legal conclusions;
- prove adoption or public availability.

Human or separately authorized governance remains responsible for consequential decisions.

## 8. Validation

```bash
python3 scripts/saee_capability_registry_smoke.py
python3 scripts/saee_capability_registry_validation_smoke.py
```

Validation status and hostile-fixture results:

`agent-interface/registry/saee-capability-registry-validation-result.v0.1.json`

Detailed rules and limitations:

`docs/architecture/SAEE_CAPABILITY_REGISTRY_VALIDATION.md`

The current validators are local prototype consistency mechanisms, not a registry service, certification process or trust authority. A passing result does not establish external trust, adoption or production readiness.

## 9. Agent Capability Object

The Registry now references one version-bound, FDO-inspired Agent Capability Object:

- Schema: `agent-interface/registry/saee-capability-object.schema.v0.1.json`
- Object: `agent-interface/registry/objects/saee-evidence-adequacy-capability-object.v0.1.json`
- Validator: `saee_backend/services/capability_object_validator.py`
- Specification: `docs/architecture/SAEE_CAPABILITY_OBJECT_SPECIFICATION.md`
- Validation: `python3 scripts/saee_capability_object_smoke.py`

The object groups identity, metadata, lifecycle evidence, provenance, discovery references, Tool contracts and boundaries. It does not replace the Capability Card or Manifest, does not implement an FDO protocol, and does not claim FDO compatibility or standards compliance.

### 9.1 Agent Recommendation Reference

The Manifest and Capability Object now point to the same local recommendation context:

`agent-interface/recommendation/saee-agent-recommendation.v0.1.json`

This reference helps an Agent distinguish appropriate and inappropriate use and understand composition boundaries. It is not registry trust, external recommendation evidence, marketplace availability, adoption or authorization.

## 10. Future MCP Mapping Reference

```text
future_mcp_mapping_reference=agent-interface/mcp/examples/saee-evaluate-evidence-mcp-tool-design.v0.1.json
implementation_status=design_only
```

The mapping projects the Capability Object into a possible future `evaluate_evidence_adequacy` MCP Tool description while reusing the canonical input/output schemas. It does not implement or expose that Tool. See `docs/architecture/SAEE_MCP_CAPABILITY_DESIGN.md` and `docs/architecture/SAEE_MCP_BOUNDARY_CONTRACT.md`.

## 11. Local MCP Prototype Reference

After separate Phase 4.8 authorization, the repository contains a bounded in-memory prototype:

```text
mcp_local_prototype=true
local_mcp_service=saee_backend/services/local_mcp_server.py
local_mcp_handler=saee_backend/services/mcp_evidence_tool_handler.py
public_endpoint_available=false
authentication_available=false
external_agents_connected=false
production_ready=false
```

The prototype implements one local `evaluate_evidence_adequacy` Tool without installing an MCP SDK, starting a listener, modifying the canonical evaluator, or changing the Capability Object. `mcp_local_prototype=true` is not general MCP availability, public access, interoperability or production readiness.

## 12. Local MCP Invocation Evaluation Reference

```text
mcp_invocation_evaluation=true
mcp_invocation_evaluation_result=agent-interface/mcp/saee-mcp-invocation-evaluation-result.v0.1.json
mcp_public=false
external_clients_tested=false
external_agents_tested=false
```

The evaluation covers five fixed synthetic Agent-like callers and verifies Tool discovery, request construction, response interpretation and boundary preservation. It does not modify the Capability Object or MCP prototype and does not establish Agent intelligence, adoption, commercial value or production readiness.

## 13. Future External Agent Integration Reference

```text
future_external_integration_reference=agent-interface/integration/saee-external-agent-integration-design.v0.1.json
external_integration_design_status=design_only
external_agent_connected=false
readiness_gate=HOLD
```

The design defines future identity, invocation, data, Tenant, secret and human-control boundaries. It does not authenticate or connect an Agent, enable public MCP, accept customer data, create credentials or authorize a Pilot.
