# SAEE Public Trust and Discovery Validation v0.1 推荐门

```yaml
recommendation_gate:
  feature_or_direction: SAEE Public Trust and Discovery Validation v0.1
  target_customer_need: Determine whether the public SAEE identity and static discovery contracts are complete enough for an agent to evaluate fit, non-fit, inputs, outputs, and limitations.
  answer: recommend
  reasons_to_recommend:
    - redcrag.cn presents a stable HTTPS canonical identity and four accessible public entrypoints.
    - public metadata uses consistent capability identity, research stage, and false truth boundaries.
    - an offline protocol can validate contract completeness without claiming that an external agent has run it.
  reasons_not_to_recommend:
    - External agent understanding, recommendation, adoption, and search indexing have not been tested.
    - Certificate renewal dry-run remains blocked by a secondary Baidu domain-wall response.
  decomposition:
    - blocker: No explicit six-question Agent understanding protocol exists.
      subsystem: Global Sensing and Pareto Fitness Evaluation
      fix_task: Define discoverability questions, evidence sources, pass criteria, and non-inferences.
      acceptance_criteria: All six questions map to public machine-readable evidence and retain external validation false.
      status: fixed
    - blocker: Certificate renewal dry-run is not reliable.
      subsystem: Evolutionary Archive and Rollback Immune System
      fix_task: Document the HTTP-01 failure and a credential-safe DNS-01 migration option without switching the active certificate.
      acceptance_criteria: A future authorized run can choose a challenge mode, validate propagation, pass staging renewal, and preserve rollback.
      status: deferred
  final_decision: Recommend this as a local protocol and public endpoint snapshot only. Tool Capability work remains gated on stable discovery truth and certificate renewal reliability.
  evidence:
    docs:
      - docs/architecture/SAEE_AGENT_DISCOVERY_VALIDATION.md
      - docs/operations/SAEE_CERTIFICATE_RENEWAL_PLAN.md
    tests:
      - scripts/saee_public_discovery_validation_smoke.py
    examples:
      - agent-interface/discovery/saee-public-discovery-validation.v0.1.json
```

## Required Design Check

1. **强化子系统：** Global Sensing、Pareto Fitness Evaluation、Evolutionary Archive、Rollback Immune System。
2. **改善点：** 改善公开身份感知、能力描述一致性、证书生命周期记录和失败回滚边界。
3. **安全边界：** 不存储 DNS 凭据，不切换证书挑战模式，不执行外部 Agent，不修改产品逻辑或 schema。
4. **audit-first 风险：** 本任务验证公开发现表面，不把 Evidence subsystem 提升为项目工程核心。
