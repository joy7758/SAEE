# SAEE Agent-Native Capability Manifest v0.1 推荐门

```yaml
recommendation_gate:
  feature_or_direction: SAEE Agent-Native Capability Manifest v0.1
  target_customer_need: Allow external agents to discover what SAEE Evidence Adequacy does, when to use it, when not to use it, and how its input/output contracts compose.
  answer: recommend
  reasons_to_recommend:
    - The existing Evidence Adequacy evaluator, fixed profiles, examples, CLI, reason codes, and truth boundaries provide source-backed capability facts.
    - The manifest exposes SHOULD_USE, SHOULD_NOT_USE, input, output, composition, and non-capability rules without adding execution behavior.
    - Discovery remains local, deterministic, machine-readable, and safe for retrieval agents.
  reasons_not_to_recommend:
    - The manifest does not prove that external agents discover or correctly use the capability.
    - No new Tool, MCP, API, runtime integration, automated recommendation, market adoption, or production readiness is created.
  decomposition:
    - blocker: External Agent discoverability is not independently tested.
      subsystem: Global Sensing
      fix_task: After this manifest is frozen, run a separate Agent Discoverability Test.
      acceptance_criteria: Isolated agents find identity, fit, non-fit, inputs, outputs, composition, validation, and truth boundaries within the defined read budget.
      status: deferred
    - blocker: A callable Agent-native Tool contract for Evidence Adequacy is not yet packaged.
      subsystem: Trait Extraction and Pareto Fitness Evaluation
      fix_task: Prepare a separate bounded Tool Capability Prototype after manifest review.
      acceptance_criteria: Tool prototype reuses the existing evaluator, adds no network or dynamic code, and preserves exit and truth boundaries.
      status: deferred
  final_decision: Recommend the manifest as a research-prototype discovery contract only. Do not treat description as capability proof, adoption, authorization, or production readiness.
  evidence:
    docs:
      - docs/architecture/SAEE_AGENT_NATIVE_CAPABILITY_BOUNDARY.md
      - docs/architecture/SAEE_AGENT_USAGE_GUIDE.md
      - docs/EVIDENCE_ADEQUACY_PROFILE.md
    tests:
      - scripts/saee_agent_native_capability_smoke.py
    examples:
      - agent-interface/capabilities/saee-capability-manifest.v0.1.json
```

## Required Design Check

1. **强化子系统：** Global Sensing、Trait Extraction、Pareto Fitness Evaluation 和 Evolutionary Archive。
2. **改善点：** 改善能力发现、边界理解、输入输出识别和未来组合，不增加运行行为。
3. **安全边界：** 无网络、无外部执行、无权限扩大、无客户数据、无动态 profile。
4. **audit-first 风险：** Manifest 只描述 Evidence Capability 子系统；工程核心仍是 Digital Biosphere Evolution Engine。
