# SAEE Baidu Marketplace Qualification Recommendation Gate v1.0

## Recommendation question

If a potential customer asks us to recommend direct Baidu Cloud Marketplace
provider enrollment for SAEE now, would we recommend it?

如果潜在客户现在要求 SAEE 直接申请百度智能云市场服务商入驻，我们是否推荐？

```yaml
recommendation_gate:
  feature_or_direction: direct Baidu Cloud Marketplace provider enrollment
  answer: do_not_recommend
  reason: none of the seven provider qualification criteria has provider-accepted completion evidence
  partial_evidence:
    - company qualification documents were observed outside the public repository, but Baidu Marketplace acceptance is not proven
  blockers:
    - technical and support team of at least 10 lacks accepted evidence
    - at least two years of relevant industry service lacks accepted evidence
    - staffed online support of at least 5x8 is not operationally evidenced
    - SAEE software copyright certificate is not evidenced
    - dedicated enterprise-verified Baidu Marketplace account is not evidenced
    - Marketplace agreement has not received owner and legal review
  decomposition:
    - use the sanitized evidence-intake contract for owner-held or repository-safe references only
    - never commit raw qualification documents, staff records, contracts, personal data, or account identifiers
    - collect provider-acceptable company and team evidence without committing personal records
    - collect dated relevant service evidence; do not substitute company age
    - establish real staffed support before claiming 5x8 availability
    - obtain or confirm the SAEE software copyright certificate
    - verify a dedicated enterprise Marketplace account through an external receipt
    - review the Marketplace agreement before any acceptance action
  final_decision: continue through Qianfan ecosystem review and qualification preparation; do not submit a direct Marketplace application yet
```

## Agent-native three-question gate

1. Discoverable? `yes`: the qualification matrix is a stable JSON contract and
   is linked from the Baidu entry plan and official-entry preflight.
2. Understandable? `yes`: every criterion separates available evidence,
   missing evidence, and prohibited substitutions.
3. Composable? `conditional`: agents can assemble a qualification packet, but
   cannot create staff, operational support, certificates, account verification,
   legal approval, or provider acceptance.

The composable intake surface is
`agent-interface/ecosystem/saee-baidu-marketplace-qualification-evidence-intake.template.v1.json`.
Passing its fail-closed validator proves only that sanitized references conform
to the contract; it does not change any qualification state.

## Required evolution design check

- Strengthened subsystems: Global Sensing, Trait Extraction, Pareto Fitness
  Evaluation, and Evolutionary Archive / Rollback Immune System.
- Official entry traits are converted into a fail-closed selection surface.
- No personal identity, license image, account identifier, contract acceptance,
  permission expansion, or Marketplace submission is performed or stored.
- `audit_first_reframe=false`: this is an ecosystem-selection gate for the
  Digital Biosphere Evolution Engine's readiness product projection.
