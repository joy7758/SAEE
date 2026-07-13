# SAEE Capability Registry Validation Prototype v0.1

## 1. Purpose

This local, deterministic prototype answers one bounded question:

> Is this checked-in capability declaration internally consistent?

It validates machine-readable registry metadata before an AI agent relies on the declaration for local capability selection. It does not answer whether the capability is externally trusted.

This validation checks registry consistency. It does not establish external trust, adoption, or production readiness.

该验证检查能力注册一致性，不建立外部信任、采用状态或生产就绪性。

## 2. Validation Dimensions

| Dimension | Check | Failure examples |
|---|---|---|
| Identity | Non-empty, formatted capability identifier and version | Empty identifier, malformed version |
| Contract references | Local input/output schemas exist and match the declared version | Missing schema, `0.1`/`0.2` mismatch |
| Lifecycle | State is allowed and higher states have explicit evidence | Production without production evidence; adoption asserted |
| Boundary | No affirmative certification, guarantee, approval or compliance claim | `SAEE is certified and compliant.` |
| Reference chain | Capability Card → Registry Entry → Manifest → Tool Contract remain consistent | Alias, version, schema reference or field mismatch |

The validator first reuses the Phase 4.4 strict registry-entry validation. Only a structurally valid entry proceeds to boundary-language and cross-object reference-chain checks. All references remain repository-local.

## 3. Hostile Fixture Model

The seven files under `agent-interface/registry/validation-fixtures/` are synthetic, declarative mutation recipes. Each recipe names the canonical local capability card, applies only an allowlisted `SET` or `DELETE` mutation to an in-memory copy, and records the expected result and reason code. The recipes are not executable code and do not change the canonical card.

Fixture coverage:

| Fixture | Expected result | Stable reason |
|---|---|---|
| valid registry entry | PASS | none |
| production without evidence | FAIL | `REGISTRY_PRODUCTION_EVIDENCE_REQUIRED` |
| version mismatch | FAIL | `REGISTRY_CONTRACT_VERSION_MISMATCH` |
| missing contract | FAIL | `REGISTRY_CONTRACT_REQUIRED` |
| affirmative boundary overclaim | FAIL | `REGISTRY_BOUNDARY_OVERCLAIM` |
| broken local reference | FAIL | `REGISTRY_REFERENCE_MISSING` |
| adoption state claim | FAIL | `REGISTRY_ADOPTION_CLAIM_FORBIDDEN` |

## 4. Reference Integrity

The cross-object check confirms:

```text
Capability Card identity and aliases
  -> Manifest capability identity and registry metadata
  -> Manifest local Tool schema references
  -> Input and output Tool schema identifiers and declared fields
```

The check never resolves `manifest_url`, fetches `redcrag.cn`, or interprets mapping rules as code.

## 5. Validation

```bash
python3 scripts/saee_capability_registry_validation_smoke.py
```

Machine result:

`agent-interface/registry/saee-capability-registry-validation-result.v0.1.json`

## 6. Limitations

- A passing result proves only checked-in internal consistency.
- Publisher identity, signature validity, runtime availability and external trust are not verified.
- The boundary scanner detects a deliberately narrow set of affirmative overclaims; it is not a general natural-language policy engine.
- The fixtures are synthetic and do not establish external agent adoption.
- No registry service, database, API, MCP server, marketplace, signing mechanism or trust federation is created.
- `production_ready=false`, `adoption_validated=false`, and `trust_authority=false` remain mandatory truth surfaces.
