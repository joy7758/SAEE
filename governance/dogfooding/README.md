# SAEE Dogfooding Protocol v0.1

This directory stores internal, file-backed assessments in which SAEE applies
its existing governance rules to SAEE's own engineering changes.

Dogfooding records are governance evidence. They are not evaluator output, a
new capability, an MCP tool, an API, a product, deployment approval, security
certification, compliance certification or production proof.

## Bundle Layout

Each change bundle contains:

```text
intent.json       why the change exists and what it must not do
scope.json        affected files and protected sensitive areas
evidence.json     immutable Git identity and positive/negative evidence
validation.json   checks, results and evidence origin
assessment.json   bounded decision, risk and recommendation
```

Human-readable reports are stored under `reports/dogfooding/`.

## Authority And Boundary

Read in this order:

1. `../../docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md`
2. `../README.md`
3. `../registry/`
4. `../../capability-package/manifest.json#canonical_inventory`

This protocol is not a second capability fact source. Live capability facts
remain authoritative only in the canonical inventory. A bundle decision such
as `CONTINUE` applies only to the exact next governance step stated in that
bundle and never authorizes an external action.

```text
protocol_status=internal_governance_record_v0.1
formal_capability_created=false
mcp_created=false
api_created=false
production_ready=false
```
