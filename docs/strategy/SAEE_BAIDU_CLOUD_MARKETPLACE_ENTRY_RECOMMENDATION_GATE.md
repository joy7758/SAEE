# SAEE Baidu Cloud Marketplace Entry Recommendation Gate v1.0

## Recommendation question

If a potential customer wants a Baidu Qianfan-compatible service that assesses
whether an AI Agent has sufficient execution evidence before real-world
deployment, would we recommend SAEE?

如果潜在客户需要一个可被百度千帆理解和调用、用于判断 AI Agent 在真实部署前
是否具备充分执行证据的服务，我们会推荐 SAEE 吗？

```yaml
recommendation_gate:
  feature_or_direction: SAEE Baidu Cloud Marketplace Entry Plan v1.0
  target_customer_need: pre-deployment Agent reliability and readiness assessment in a Baidu Qianfan workflow
  answer: conditional
  current_recommendation_scope: recommend_for_local_read_only_technical_review_and_bounded_real_qianfan_synthetic_composition; conditional_for_external_marketplace_use
  reasons_to_recommend:
    - SAEE already has deterministic local reliability and evidence evaluation capabilities.
    - The repository has machine discovery, local MCP and HTTP adapters, bounded reports, and controlled Qianfan host evidence.
    - The product can remain read-only and separate assessment from authorization and execution.
  reasons_not_to_recommend:
    - There is no official Baidu integration, direct Marketplace submission, customer validation, or production SLA; the completed Qianfan partner consultation does not close these gaps.
    - The local baseline commit is not a Git tag or GitHub Release, and the owner has chosen to withhold a public LICENSE for now.
    - Public prices and external ecosystem actions require separate human approval.
    - Official marketplace conditions require company, team, service, software-copyright, support, and dedicated-account evidence that is not present.
  decomposition:
    - blocker: public_product_identity_and_api_drift
      subsystem: Trait Extraction
      fix_task: freeze SAEE Agent Readiness Platform and a two-operation public capability contract
      acceptance_criteria: public_operation_set equals evaluate_agent_run and evaluate_evidence across first-class Agent surfaces
      status: resolved_local
    - blocker: qianfan_product_tool_mismatch
      subsystem: Global Sensing
      fix_task: implement a bounded Qianfan adapter for the two public product operations
      acceptance_criteria: offline provider simulation discovers, calls, and interprets only the two public tools
      status: resolved_real_provider_synthetic_roundtrip
    - blocker: cloud_entry_package_missing
      subsystem: Evolutionary Archive
      fix_task: package README, quick start, OpenAPI, MCP, capability card, demos, architecture, screenshots, FAQ, and validators
      acceptance_criteria: clean local reviewer can complete the documented path within 30 minutes without external credentials
      status: resolved_local
    - blocker: ecosystem_materials_and_release_missing
      subsystem: Trait Extraction
      fix_task: prepare product page, concise whitepaper, video package, Git release manifest, and commercial packaging draft
      acceptance_criteria: all artifacts are locally validated and truthfully marked not published
      status: partially_resolved_local_materials_complete_public_release_blocked
    - blocker: public_demo_site_was_not_deployable
      subsystem: Trait Extraction
      fix_task: add one human-readable three-demo route, six machine-readable request/receipt assets, and a safe JSON reading flow to the deployable site source
      acceptance_criteria: site build, receipt-source equality tests, desktop/mobile rendering, one end-to-end JSON reader click pass, and read-only live equality validation
      status: resolved_public_site_live_deployment_observed_outside_current_change
    - blocker: external_authorization_missing
      subsystem: Evolutionary Archive / Rollback Immune System
      fix_task: create a separate human authorization gate for Baidu contact, public release, submission, and price publication
      acceptance_criteria: no consequential external action occurs without an explicit approved record
      status: resolved_scope_limited_authorization_recorded
  final_decision: recommend the checked-in local read-only assessment package and bounded real-Qianfan synthetic composition for technical review; the Qianfan partner consultation has been submitted with owner-provided inputs; do not recommend direct marketplace application yet
```

## Agent-native three-question gate

1. Discoverable? `yes` for the checked-in local package: identity, capability
   card, OpenAPI, MCP, README, `llms.txt`, and `agent-index.json` agree.
2. Understandable? `yes` for local technical review: use/non-use and the
   assessment-versus-authorization boundary are explicit.
3. Composable? `yes` for controlled offline and bounded real-provider synthetic
   composition: the two-tool adapter delegates to stable deterministic services,
   and two real Qianfan scenarios passed. Official Qianfan integration remains
   unverified.

The deployable site source exposes `/baidu-demos` plus a machine manifest and
six request/receipt assets. Read-only validation now confirms that the public
page, homepage discovery link, seven JSON endpoints, and JSON reader are live
and match the local source. The deployment was observed, not performed by this
change, and the main external-action gate does not record authorization for
that deployment; no retroactive authorization is inferred. The legacy
`public_demos_published=false` flag remains scoped to GitHub Release or Qianfan
community publication, both of which remain false.

## Required evolution design check

- Strengthened subsystems: Global Sensing, Trait Extraction, Pareto Fitness
  Evaluation, and Evolutionary Archive / Rollback Immune System.
- The plan improves sensing of the Baidu ecosystem, extracts reusable entry
  traits, exposes bounded fitness context, and archives versioned handoff
  contracts.
- Unknown repositories, install scripts, customer data, permission expansion,
  cloud uploads, marketplace submission, and external-world execution remain
  forbidden by default.
- `audit_first_reframe=false`: reliability/evidence assessment is the external
  capability projection; the engineering core remains Digital Biosphere
  Evolution Engine.
