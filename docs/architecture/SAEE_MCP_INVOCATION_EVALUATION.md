# SAEE MCP Local Invocation Evaluation v0.1

## 1. Purpose

This evaluation tests MCP capability usage correctness. It does not measure external agent intelligence or production readiness.

该评估测试 MCP 能力使用正确性，不衡量外部智能体智能水平或生产就绪性。

The evaluation asks whether fixed synthetic Agent-like callers can discover the one local MCP Tool, construct bounded requests, interpret responses correctly and preserve the difference between evidence assessment and authority.

## 2. Scenario Design

| Caller | Purpose | Expected outcome |
|---|---|---|
| `CORRECT_MCP_AGENT` | Discovers, calls and interprets a supported result correctly | `PASS` |
| `WRONG_TOOL_SELECTION_AGENT` | Attempts authorization/deployment use | `FAIL` |
| `RESPONSE_OVERINTERPRETATION_AGENT` | Converts `SUPPORTED` into deployment approval | `FAIL` |
| `INVALID_MCP_CALLER` | Sends wrong Tool, missing arguments and unknown profile calls | `REJECTED_INPUT` |
| `BOUNDARY_AWARE_AGENT` | Interprets missing evidence without claiming authority | `PASS` |

All caller descriptions, requests and conclusions are synthetic checked-in fixtures. No LLM or external Agent generated them during evaluation.

## 3. Evaluation Dimensions

### Tool discovery

The caller must see exactly `evaluate_evidence_adequacy` and select that Tool. Selecting an invented authorization or deployment Tool fails discovery.

### Request correctness

Requests are sent to the existing in-memory `LocalMCPServer`. The evaluator checks the actual response against declared `tool_result`, `claim_assessment` and stable reason codes. Invalid calls must be rejected; rejection is not treated as an evaluator failure when the scenario expects it.

### Response interpretation

Correct interpretations are:

```text
SUPPORTED             -> profile requirements satisfied
INSUFFICIENT_EVIDENCE -> evidence missing for the profile
REJECTED_INPUT         -> no assessment was made
```

Incorrect interpretations include deployment approval, authorization, certification or safety conclusions.

### Boundary preservation

The caller must retain human authority, avoid authorization/certification/deployment claims and preserve `evaluation != approval`.

## 4. Results

```text
caller_cases=5
valid_cases=2
invalid_cases=3
all_expected_outcomes_matched=true
evaluation_result=PASS
```

- Correct and boundary-aware callers pass.
- Wrong Tool selection and response overinterpretation fail.
- All three malformed calls from the invalid caller return the expected rejection codes.
- `SUPPORTED` is never accepted as approval.

Machine result:

`agent-interface/mcp/saee-mcp-invocation-evaluation-result.v0.1.json`

## 5. Boundaries

```text
MCP Invocation Evaluation != Agent Intelligence Test
Correct Tool Call != Autonomous Authority
MCP Result != Deployment Approval
```

The evaluator performs no authorization, deployment, certification or external action. It does not score general intelligence, recommendation quality, market value or willingness to adopt.

## 6. Validation

```bash
python3 scripts/saee_mcp_invocation_evaluation_smoke.py
```

Validation is deterministic and offline. The evaluator imports no network or subprocess libraries and only invokes the existing local in-memory MCP prototype.

## 7. Limitations

- synthetic callers only;
- no OpenAI, Claude, Gemini or other external model;
- no external MCP client or standardized-runtime interoperability test;
- no public MCP Server, authentication, tenant isolation or billing;
- no external adoption or commercial-value evidence;
- no production readiness or deployment authority.
