# SAEE Agent Capability Object Specification v0.1

## 1. Purpose

The SAEE Agent Capability Object is a strict, local, machine-readable representation of one capability. It groups identity, descriptive metadata, lifecycle evidence, provenance, discovery references, input/output contracts and non-use boundaries so an AI agent can reason about the capability before composing it into a local workflow.

```text
Capability Object != Digital Object
Capability Metadata != Capability Trust
Object Discovery != Permission Grant
Capability Evaluation != Autonomous Decision
```

This specification adapts object-oriented metadata principles for agent capability representation. It does not claim FDO compliance.

本规范借鉴面向对象的元数据原则来表示智能体能力，不宣称符合 FDO。

## 2. FDO-Inspired Concepts

The specification selectively adapts these ideas:

| FDO-inspired idea | SAEE adaptation | Boundary |
|---|---|---|
| Persistent identity | Version-bound `object_id` | No external PID infrastructure |
| Machine-readable metadata | Strict JSON Schema metadata | Metadata is not verification |
| Object lifecycle | Four evidence-gated capability states | State does not prove readiness |
| Discoverability | Canonical, Manifest and registry references | Discovery does not authorize use |
| Provenance | Creator, source reference, timestamp and change history | No external trust or signature |
| Reusable references | Stable local contract and evidence references | No federation or marketplace |

SAEE does not copy FDO schemas, protocols, resolution infrastructure, identifiers or conformance claims.

## 3. Object Model

```text
object_id
object_type
identity
metadata
lifecycle
provenance
discovery
contracts
boundaries
truth_boundary
```

Schema: `agent-interface/registry/saee-capability-object.schema.v0.1.json`

Instance: `agent-interface/registry/objects/saee-evidence-adequacy-capability-object.v0.1.json`

## 4. Identity

```text
capability_id=saee.evidence-adequacy
version=0.1
object_id=saee:capability:evidence-adequacy:0.1
identity_scope=repository_local_specification
```

The top-level and nested object identifiers must match. A new contract version requires a different version-bound object identifier. This is a repository-local stable identity, not a globally registered persistent identifier.

## 5. Metadata and Discovery

Metadata contains a bilingual name, description and purpose plus a bounded keyword list. It is written for semantic discovery without marketing superlatives or claims such as `best`, `guaranteed`, `secure`, `certified`, `approved` or `compliant`.

Discovery identifies the current canonical human/agent entry point, public Manifest location and repository-local Registry/Card references. The object itself remains local:

```text
object_local_only=true
public_object_available=false
```

## 6. Lifecycle

Allowed states remain:

- `RESEARCH_PROTOTYPE`
- `LOCAL_PROTOTYPE`
- `EXTERNAL_VALIDATION`
- `PRODUCTION_CAPABILITY`

Every state includes local evidence references. `EXTERNAL_VALIDATION` requires completed external validation evidence. `PRODUCTION_CAPABILITY` requires both external and production validation evidence. The current object remains `LOCAL_PROTOTYPE`; object validation does not authorize state promotion.

## 7. Provenance

The provenance block records:

- the SAEE creator label;
- object specification version;
- repository-local source reference;
- RFC 3339 creation timestamp;
- versioned change history with local evidence references;
- `external_trust_established=false`.

These are declared and structurally validated provenance fields. They are not a signature, publisher proof, timestamp authority or external trust chain.

## 8. Contracts

The object binds version `0.1` to:

- `agent-interface/capabilities/saee-evaluate-evidence-tool.v0.1.schema.json`
- `agent-interface/capabilities/saee-evaluate-evidence-output.v0.1.schema.json`

The validator checks that both files exist locally, their `$id` matches the referenced filename, and their versions match the capability object. It does not invoke the Tool.

## 9. Boundaries

The object provides only `EVIDENCE_ADEQUACY_EVALUATION`. It does not provide authorization, certification, deployment approval, legal judgment, security guarantees or autonomous decisions. Human or separately authorized governance remains authoritative.

The object also states:

```text
fdo_compliant=false
trusted_capability=false
registry_service_available=false
mcp_available=false
api_available=false
external_validation_completed=false
adoption_validated=false
production_ready=false
```

## 10. Validation

```bash
python3 scripts/saee_capability_object_smoke.py
```

The validator is local, deterministic and fail closed. It rejects missing or inconsistent identity, false production promotion, missing provenance, missing or broken contracts, unsupported trust flags and schema violations. It performs no network access, subprocess execution or external code execution.

## 11. Relationship to Future Invocation

```text
FDO-inspired object concepts
        ↓
SAEE Agent Capability Object
        ↓
Agent discovery and fit reasoning
        ↓
separately designed invocation contract
```

An MCP design may reference this object later, but this phase creates no MCP server, API, public Registry, Marketplace or permission grant.

The approved design reference is now:

`future_mcp_mapping_reference=agent-interface/mcp/examples/saee-evaluate-evidence-mcp-tool-design.v0.1.json`

This reference does not change the Capability Object, its `LOCAL_PROTOTYPE` lifecycle, or `mcp_available=false`. The target `evaluate_evidence_adequacy` exposure remains `DESIGN_ONLY`.

Phase 4.8 subsequently implemented a separately tracked in-memory local prototype at `saee_backend/services/local_mcp_server.py`. The object instance remains unchanged and continues to state `mcp_available=false`; the local implementation fact is recorded as `mcp_local_prototype=true` in Registry/Manifest metadata rather than silently promoting the frozen object or claiming general availability.

Phase 4.9 also records `mcp_invocation_evaluation=true` outside the object instance. This means five synthetic caller scenarios were evaluated against the local prototype; it does not change object lifecycle, public availability, trust or external validation.

Phase 5.0 adds a future external-integration design reference at `agent-interface/integration/saee-external-agent-integration-design.v0.1.json`. The Capability Object remains unchanged. The reference defines a possible future caller boundary and does not make the object public, trusted, externally validated or production-ready.
