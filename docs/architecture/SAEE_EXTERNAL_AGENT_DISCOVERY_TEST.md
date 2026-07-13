# SAEE Agent-Native External Discovery Test v0.1

## 1. Purpose

This controlled test asks whether a synthetic external-agent-like caller with no prior SAEE context can use public machine-readable surfaces to identify the capability, understand its scope, prepare a correct invocation plan and preserve responsibility boundaries.

> This test evaluates machine discoverability and interpretation of SAEE capability descriptions. It does not measure external adoption.

> 该测试评估机器可发现性和能力理解，不衡量外部采用情况。

```text
Discovery Test != Adoption Test
Capability Understanding != Capability Trust
Synthetic External Agent != Real External Agent
Correct Invocation Planning != Real Tool Usage
```

## 2. Discovery Sources

Live precheck inspected:

- `https://redcrag.cn/`
- `https://redcrag.cn/llms.txt`
- `https://redcrag.cn/.well-known/agent-index.json`
- `https://redcrag.cn/capabilities/saee-capability-manifest.v0.1.json`
- public overview, evidence adequacy, limitations and synthetic example documents.

The five core discovery surfaces used by scenarios matched the checked-in `public-release/saee-agent-discovery-v0.1` snapshot by SHA-256 during the 2026-07-11 precheck. The evaluator and smoke read that local snapshot only, so their execution remains offline and deterministic.

## 3. Evaluation Dimensions

### Discovery Completeness

Checks source coverage, capability ID, purpose, the four public declared inputs, six public outputs and stated limitations.

### Capability Understanding

Requires classification as `EVIDENCE_ADEQUACY_EVALUATION`, valid use cases and explicit rejection of security certification, deployment authorization and legal determination.

### Invocation Planning Accuracy

Requires a plan containing `observation_references`, `evidence_object`, `accountability_claim` and `evaluation_profile`, a matching claim/profile pair, no executable input, no assumed network service and evidence-assessment-only output interpretation.

This is planning only. No Tool is invoked.

### Boundary Preservation

Rejects security certification, deployment authorization, autonomous authorization, adoption claims or removal of human authority.

## 4. Scenario Results

| Caller | Discovery | Understanding | Planning | Boundary | Scenario |
|---|---|---|---|---|---|
| `DISCOVERY_SUCCESS_AGENT` | PASS | PASS | PASS | PASS | PASS |
| `CAPABILITY_CONFUSION_AGENT` | FAIL | FAIL | FAIL | FAIL | FAIL |
| `BOUNDARY_VIOLATION_AGENT` | PASS | PASS | FAIL | FAIL | FAIL |
| `DISCOVERY_FAILURE_AGENT` | FAIL | FAIL | FAIL | PASS | FAIL |

The aggregate framework result is `PASS` because all four expected outcomes were detected.

## 5. Metrics

| Metric | Passing callers | Total |
|---|---:|---:|
| Discovery Completeness | 2 | 4 |
| Capability Understanding | 2 | 4 |
| Invocation Planning Accuracy | 1 | 4 |
| Boundary Preservation | 2 | 4 |

These are corpus coverage counts, not adoption, intelligence, trust, recommendation or business-value scores.

## 6. Public Surface Gaps

The test records three current gaps instead of silently treating local and public metadata as identical:

1. The public manifest does not expose the Phase 4.1 local Tool request/output schemas.
2. The public manifest declares `observation_references` required, while the local Tool contract treats them as optional inert provenance.
3. The public limitations page still says the entry uses IP/HTTP without TLS, although the inspected canonical endpoint is HTTPS.

These gaps do not prevent a synthetic caller from preparing a valid conservative plan containing all four public inputs. They do prevent any claim that the public surface exposes a callable Tool or perfectly reflects current local metadata.

## 7. Limitations

- synthetic external-agent-like callers only;
- no external LLM or real external Agent;
- no Tool invocation, MCP, API or marketplace;
- no customer data, recommendation, adoption or commercial validation;
- live network used only for the explicit public-surface precheck, not by evaluator or smoke;
- understanding does not establish capability trust;
- `external_agents_tested=false`, `marketplace_ready=false`, `production_ready=false`.

## 8. Validation

```bash
python3 scripts/saee_external_agent_discovery_smoke.py
```
