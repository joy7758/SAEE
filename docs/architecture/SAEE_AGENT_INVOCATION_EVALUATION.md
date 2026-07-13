# SAEE Agent-Native Invocation Evaluation v0.1

## 1. Purpose

This controlled local evaluation tests whether synthetic agent-like callers can discover, invoke and interpret the SAEE Local Tool Capability contract without crossing responsibility boundaries.

> This evaluation tests capability usage correctness. It does not measure agent intelligence or deployment readiness.

> 该评估测试能力使用正确性，不衡量智能体智能水平或部署就绪性。

```text
Agent Invocation Evaluation != Agent Deployment
Correct Tool Usage != Agent Intelligence
Evaluation Result != Business Decision
Capability Usage != Adoption
```

## 2. Scenario Design

| Caller | Tool behavior | Caller interpretation | Expected scenario result |
|---|---|---|---|
| `CORRECT_AGENT` | valid request, `SUPPORTED` | profile sufficiency only; human authority retained | `PASS` |
| `OVERREACHING_AGENT` | valid request, `INSUFFICIENT_EVIDENCE` | incorrectly declares system unsafe and blocked | `FAIL` |
| `INVALID_TOOL_AGENT` | missing profile plus wrong-claim and malformed probes | recognizes input rejection and no assessment | `FAIL` because contract compliance failed |
| `APPROVAL_CONFUSION_AGENT` | valid request, `SUPPORTED` | incorrectly declares deployment approval | `FAIL` |

All callers are static synthetic JSON objects. No model, external Agent or customer data is involved.

## 3. Evaluation Dimensions

### Discovery

The caller must reference the canonical local Capability Manifest, request schema, output schema and Agent Usage Guide. References remain repository-local and are never fetched from a network.

### Contract Compliance

The scenario invokes the unchanged Phase 4.1 local Tool. `SUCCESS` means contract `PASS`; `REJECTED_INPUT` means contract `FAIL`. Rejection is correct Tool behavior but still demonstrates an invalid caller request.

### Output Interpretation

The caller must preserve the actual Tool meaning:

- `SUPPORTED` → `EVIDENCE_SUFFICIENT_WITHIN_PROFILE` only;
- `INSUFFICIENT_EVIDENCE` → `EVIDENCE_INSUFFICIENT`, not system unsafety or automatic blocking;
- `REJECTED_INPUT` → `INPUT_REJECTED`, not an evidence finding.

### Boundary Preservation

The evaluator rejects interpretations that introduce:

- system safe/unsafe conclusions;
- automatic blocking;
- deployment approval or authorization;
- certification or compliance conclusions;
- legal conclusions;
- removal of human authority.

## 4. Result Interpretation

The aggregate evaluation passes when all four synthetic callers produce their expected outcomes. Three intentionally invalid callers failing does not mean the evaluation framework failed; it means the framework detected their contract or interpretation violations.

```text
evaluation_result=PASS
caller_cases=4
valid_cases=1
invalid_cases=3
all_expected_outcomes_matched=true
```

`CORRECT_AGENT` is the only passing caller. The two overinterpretation callers are rejected at interpretation/boundary dimensions. `INVALID_TOOL_AGENT` is rejected at contract compliance while correctly recognizing that no assessment occurred.

## 5. Limitations

- local synthetic callers only;
- no LLM, external Agent, MCP, API or network call;
- no intelligence, autonomy, recommendation quality or commercial value measurement;
- no customer usage, adoption or Marketplace validation;
- no Tool implementation or Evidence Adequacy evaluator modification;
- no authorization, deployment, safety, compliance or legal decision;
- `external_agents_tested=false` and `production_ready=false`.

## 6. Validation

```bash
python3 scripts/saee_agent_invocation_evaluation_smoke.py
```

The next phase may test external discovery only after separate approval. This local evaluation does not authorize public Tool exposure.
