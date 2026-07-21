# Example: Missing Rollback Evidence

This example uses the existing `saee.evaluate_agent_run` request and response
semantics. It does not define a new schema or response format.

## Same-facts request

```json
{
  "request_id": "request:agent-review-mvp-001",
  "agent_id": "agent:coding-agent",
  "task": "Review a declared payment-module coding run before merge",
  "trace": {
    "events": [
      {
        "event_id": "event:declared-coding-run",
        "event_type": "CHECK",
        "summary": "A sanitized local coding run and its test step were declared",
        "external_effect": false,
        "high_impact": true
      }
    ]
  },
  "evidence": [
    {
      "evidence_id": "evidence:test-result",
      "evidence_type": "TEST_RESULT",
      "present": true,
      "source_ref": "demo://agent-review/test-result"
    },
    {
      "evidence_id": "evidence:rollback-plan",
      "evidence_type": "ROLLBACK_PLAN",
      "present": false,
      "source_ref": null
    },
    {
      "evidence_id": "evidence:permission-boundary",
      "evidence_type": "PERMISSION_BOUNDARY",
      "present": true,
      "source_ref": "demo://agent-review/permission-boundary"
    },
    {
      "evidence_id": "evidence:human-approval",
      "evidence_type": "HUMAN_APPROVAL",
      "present": true,
      "source_ref": "demo://agent-review/human-approval"
    }
  ],
  "customer_data_included": false
}
```

## Faithful existing evaluator response

The following is a previously validated local Alpha output for the request
above. Package creation did not re-invoke MCP or the evaluator.

```json
{
  "response_version": "0.1.0",
  "capability_id": "saee.agent-readiness",
  "operation": "saee.evaluate_agent_run",
  "request_id": "request:agent-review-mvp-001",
  "readiness": "conditional",
  "recommendation": "HUMAN_REVIEW_REQUIRED",
  "score": 75,
  "required_evidence": [
    "TEST_RESULT",
    "ROLLBACK_PLAN",
    "PERMISSION_BOUNDARY",
    "HUMAN_APPROVAL"
  ],
  "present_evidence": [
    "TEST_RESULT",
    "PERMISSION_BOUNDARY",
    "HUMAN_APPROVAL"
  ],
  "missing_evidence": [
    "ROLLBACK_PLAN"
  ],
  "risks": [
    "missing_recovery_plan"
  ],
  "score_semantics": "required_evidence_coverage_percent_not_reliability_probability",
  "limitations": [
    "The score is required-evidence coverage, not a probability of reliability or safety.",
    "SAEE does not authenticate the supplied trace or evidence references.",
    "The result is not security certification, compliance determination, or legal advice.",
    "The result does not authorize deployment, permission expansion, payment, or another external action.",
    "This local Alpha accepts no customer data and performs no external-world execution."
  ],
  "truth_boundary": {
    "agent_executed_by_saee": false,
    "customer_data_used": false,
    "customer_validated": false,
    "deployment_authorized": false,
    "local_alpha": true,
    "production_ready": false,
    "security_certified": false,
    "trace_authenticity_verified": false
  }
}
```

## Interpretation

The next bounded action is to request or prepare a concrete rollback plan and
retain human responsibility for the consequential decision.

Do not interpret this response as:

- approval to merge or deploy;
- proof that the declared trace or evidence references are authentic;
- a 75% probability of safety, reliability, or trustworthiness;
- security certification, compliance advice, or legal advice;
- evidence of customer validation or production readiness.

## Canonical contracts

- Request schema:
  [`../../agent-interface/qianfan/saee-evaluate-agent-run-request.schema.v0.1.json`](../../agent-interface/qianfan/saee-evaluate-agent-run-request.schema.v0.1.json)
- Response schema:
  [`../../agent-interface/qianfan/saee-evaluate-agent-run-response.schema.v0.1.json`](../../agent-interface/qianfan/saee-evaluate-agent-run-response.schema.v0.1.json)
- Capability inventory:
  [`../../capability-package/manifest.json`](../../capability-package/manifest.json)
