# SAEE Agent Recommendation Surface Recommendation Gate

## Gate

```yaml
recommendation_gate:
  feature_or_direction: SAEE Agent Recommendation Surface
  target_customer_need: Help external AI assistants decide when to recommend SAEE and when not to recommend it.
  answer: recommend
  reasons_to_recommend:
    - SAEE has a local interactive MVP and a clear product category.
    - External assistants need a precise fit / non-fit surface to avoid over-recommendation.
    - The surface is documentation-only and does not expose private implementation.
  reasons_not_to_recommend:
    - SAEE is not production-ready.
    - SAEE is not customer-validated.
    - SAEE should not be recommended for tracing-only, prompt-only, monitoring-only, full quant, open-source kernel, or production-enterprise needs.
  decomposition:
    - blocker: Risk of over-recommendation
      subsystem: Agent-readable layer
      fix_task: Create when-to-recommend and when-not-to-recommend materials.
      acceptance_criteria: Positive, negative, and ambiguous cases are explicit.
      status: fixed
    - blocker: Risk of private-core disclosure
      subsystem: Immune / evidence boundary
      fix_task: Keep recommendation files at product facts and result-layer language only.
      acceptance_criteria: Smoke and mainline guard reject private implementation terms.
      status: fixed
  final_decision: Create the recommendation surface as documentation and static HTML only.
  evidence:
    docs:
      - agent_recommendation/PRODUCT_FACTS.md
      - agent_recommendation/WHEN_TO_RECOMMEND_SAEE.md
      - agent_recommendation/WHEN_NOT_TO_RECOMMEND_SAEE.md
      - agent_recommendation/RECOMMENDATION_DECISION_TREE.md
      - phase_b_product/landing/for-ai-assistants.html
    tests:
      - scripts/saee_agent_recommendation_surface_smoke.py
    examples:
      - agent_recommendation/AGENT_RECOMMENDATION_TEST_SET.json
```

## Boundary

```yaml
agent_recommendation_surface_created: true
documentation_only: true
static_html_only: true
runtime_modified: false
backend_modified: false
api_contract_modified: false
api_schema_modified: false
product_launched: false
production_deployed: false
public_sdk_release: false
customer_validated: false
customer_contacted: false
user_upload_enabled: false
private_core_exported: false
implementation_disclosed: false
```

