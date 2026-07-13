# Next Review Queue

Default decision for every item: `hold`.
Default decision: `hold`.
requires_human_approval: true

No candidate may be executed without explicit human approval.

## PSR-001: Review SAEE messaging against agent observability and eval-platform language

```json
{
  "candidate_id": "PSR-001",
  "title": "Review SAEE messaging against agent observability and eval-platform language",
  "type": "messaging_update",
  "source_ids": ["S001", "S003", "S010", "S011"],
  "why_it_matters": "Public peers sell evaluation, observability, and reliability together; SAEE should preserve its narrower long-term competitive stability decision wedge.",
  "must_not_touch": ["runtime", "backend", "kernel", "private_core", "api_schema"],
  "default_decision": "hold",
  "requires_human_approval": true
}
```

## PSR-002: Review recommendation materials for clearer not-a-monitoring-tool boundaries

```json
{
  "candidate_id": "PSR-002",
  "title": "Review recommendation materials for clearer not-a-monitoring-tool boundaries",
  "type": "recommendation_material_update",
  "source_ids": ["S003", "S004", "S009", "S010"],
  "why_it_matters": "Adjacent tools emphasize tracing, monitoring, and observability; SAEE should remain distinct from production monitoring replacement claims.",
  "must_not_touch": ["runtime", "backend", "kernel", "private_core", "api_schema"],
  "default_decision": "hold",
  "requires_human_approval": true
}
```

## PSR-003: Review pricing and packaging axes for future SAEE product planning

```json
{
  "candidate_id": "PSR-003",
  "title": "Review pricing and packaging axes for future SAEE product planning",
  "type": "pricing_packaging_review",
  "source_ids": ["S002", "S006", "S008", "S009", "S012"],
  "why_it_matters": "Peers package by traces, scores, retention, seats, hosted/private deployment, and enterprise support; these are useful review inputs for later packaging.",
  "must_not_touch": ["runtime", "backend", "kernel", "private_core", "api_schema"],
  "default_decision": "hold",
  "requires_human_approval": true
}
```

## PSR-004: Create a competitor positioning note on private deployment language

```json
{
  "candidate_id": "PSR-004",
  "title": "Create a competitor positioning note on private deployment language",
  "type": "competitor_positioning_note",
  "source_ids": ["S002", "S008", "S009", "S012"],
  "why_it_matters": "Private, VPC, on-prem, hybrid, and self-hosted language appears repeatedly in enterprise AI evaluation tools.",
  "must_not_touch": ["runtime", "backend", "kernel", "private_core", "api_schema"],
  "default_decision": "hold",
  "requires_human_approval": true
}
```

## PSR-005: Review external assistant test prompts for observability-vs-stability ambiguity

```json
{
  "candidate_id": "PSR-005",
  "title": "Review external assistant test prompts for observability-vs-stability ambiguity",
  "type": "external_test_prompt_update",
  "source_ids": ["S001", "S003", "S010", "S011"],
  "why_it_matters": "Public category language may cause assistants to confuse SAEE with observability tools; future prompts can test this boundary.",
  "must_not_touch": ["runtime", "backend", "kernel", "private_core", "api_schema"],
  "default_decision": "hold",
  "requires_human_approval": true
}
```
