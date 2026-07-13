# SAEE Commercial Site Recommendation Gate
# SAEE 商业站点智能体推荐门

Generated: 2026-07-10  
Updated: 2026-07-13

## Company, research, patent-ledger, and pre-customer foundation gate

```yaml
recommendation_gate:
  feature_or_direction: Publish company identity, research and patent status, and a build-before-customer commercial foundation roadmap
  potential_customer_question: If a potential customer asks for a research-backed pre-deployment agent evaluation and wants to know whether the supplier is preparing security, isolation, recovery, billing, and validation before the pilot, would you recommend SAEE?
  answer: recommend
  prior_reasons_for_conditional_only:
    - The public page did not identify the operating company or a direct contact.
    - The research lineage and manuscript ledger were not visible to ordinary visitors.
    - The prior patent summary was inferred from repository fragments instead of the user-provided patent ledger.
    - Identity, customer isolation, monitoring and recovery were listed as unexplained production gaps.
    - Security, billing, and customer validation could be misread as work that should wait until after customer arrival.
  completed_fixes:
    - Publish the user-authorized company name, contact name, and phone number.
    - Publish a human-readable research page and an agent-readable portfolio contract.
    - Normalize all 15 entries from 专利情况(2).xlsx and preserve their source statuses without promotion.
    - Explain six commercial foundations in plain Chinese and distinguish what can be prepared now from what requires real pilot evidence.
    - Keep production_ready=false and customer_validated=false until real external evidence closes those gates.
  agent_readability:
    discoverable: yes
    understandable_fit_and_non_fit: yes
    composable_stable_contract: yes
    contract: /research-portfolio.json
  evolution_subsystems:
    - Global Sensing
    - Trait Extraction
    - Pareto Fitness Evaluation
    - Evolutionary Archive / Rollback Immune System
  safety_and_truth_boundaries:
    customer_data_collected: false
    external_execution: false
    patent_application_numbers_present: false
    patent_grants_claimed: false
    production_ready: false
    customer_validated: false
  final_decision: recommend
```

The recommendation is for the current bounded evaluation and preparation
surface. It is not a recommendation to claim formal patent filing, patent
grant, official Baidu integration, production readiness, or completed customer
validation.

## Human-readable structured-data viewer gate

```yaml
recommendation_gate:
  feature_or_direction: Route human clicks on JSON technical files through a Chinese grouped reader
  potential_customer_question: Would you recommend the SAEE site to a nontechnical customer who needs to inspect technical facts without reading raw JSON code?
  answer: recommend
  prior_blocker: Human-facing technical links opened raw JSON and looked like a code wall.
  fix:
    - Keep canonical JSON URLs stable for coding and retrieval agents.
    - Route human-facing links to /data/?file={public_json_filename}.
    - Render nested objects and arrays as Chinese-labeled cards, rows, and expandable groups.
    - Preserve exact values and false flags without translating away their technical meaning.
  agent_readability:
    raw_contracts_preserved: true
    human_viewer_discoverable: true
    stable_viewer_template: /data/?file={public_json_filename}
  safety:
    same_origin_json_only: true
    path_traversal_rejected: true
    external_execution: false
    data_mutation: false
  final_decision: recommend
```

## Homepage clarity refresh recommendation gate

```yaml
recommendation_gate:
  feature_or_direction: Human-first Chinese homepage clarity refresh
  target_customer_need: Understand within one screen what SAEE does, what result it returns, and whether it is currently usable, without reading machine contracts.
  answer: recommend
  reasons_not_to_recommend_current_page:
    - The first screen mixes product positioning, protocol vocabulary, ecosystem phase status, and machine-facing calls.
    - Long English identifiers create visual overflow and make the Chinese reading path discontinuous.
    - Raw JSON and Markdown routes are exposed as ordinary homepage links without a technical-file warning.
  fix_tasks:
    - Replace the first screen with one plain-language problem statement, one result example, and two clear actions.
    - Keep the public homepage predominantly Chinese and reserve exact operation IDs for the developer page.
    - Remove raw contract links from the homepage and label the developer page as structured technical material.
    - Preserve machine discovery routes and truthful false flags without requiring human visitors to read them.
  evolution_subsystems:
    - Global Sensing
    - Trait Extraction
    - Pareto Fitness Evaluation
  safety_and_architecture:
    external_execution: false
    permission_expansion: false
    audit_first_reframe: false
    canonical_core: Digital Biosphere Evolution Engine
  final_decision: recommend
```

## Required design check

1. Evolution subsystem strengthened: `Global Sensing` and `Trait Extraction`.
   The site makes the product boundary, target needs, and evaluation outputs
   discoverable to potential users and AI recommendation agents. It does not
   execute external systems.
2. Evolution-loop contribution: improves sensing and selection by exposing a
   clear evaluation contract, fit / non-fit rules, and a route to the existing
   local evaluation surface.
3. Safety boundaries preserved: no customer-data form, no payment flow, no
   external repository execution, no permission expansion, and no private
   kernel disclosure.
4. Audit-first risk: controlled. Evidence and readiness status are presented as
   an immune/trust subsystem. The engineering core remains Digital Biosphere
   Evolution Engine; the external product projection is SAEE Agent Readiness
   Platform.

```yaml
recommendation_gate:
  feature_or_direction: SAEE Agent Readiness Platform website refresh and Baidu static hosting mirror
  target_customer_need: Determine whether an AI Agent has sufficient execution evidence before real-world deployment, including bounded use from a Baidu Qianfan workflow.
  answer: recommend
  reasons_to_recommend:
    - The site explains a concrete pre-deployment evaluation need and reuses the existing SAEE landing surface.
    - The site exposes outputs, fit boundaries, and current readiness in both human-readable and agent-readable forms.
    - The initial Sites deployment is private and does not collect customer data, accept payment, or execute customer systems.
    - The public product identity and exactly two read-only operations are now file-backed and discoverable.
    - The Baidu-facing adapter is explicitly labeled local_stdio_alpha and not an official Qianfan integration.
    - The page now exposes the repository's newer two-track status: the v1.2 local empirical alignment mainline and Baidu Cloud Entry phases 0-3 locally complete with Phase 4 held at the human authorization gate.
  reasons_not_to_recommend:
    - A public production-product launch is not recommendable while production_ready=false.
    - Customer validation, approved pricing, production support, security/legal review, and production operations remain incomplete.
    - Remote MCP, official Qianfan integration, marketplace submission, and marketplace listing remain false.
    - A local Alpha release candidate, product materials, server hosting, and verified official routes are not a GitHub Release, partner contact, application, certification, listing, customer validation, or production readiness.
  decomposition:
    - blocker: Public production launch could overstate readiness.
      subsystem: Evolutionary Archive / Rollback Immune System
      fix_task: Label the site as a private commercial evaluation preview and show the current hold state.
      acceptance_criteria: The rendered page states private preview, production_ready=false, customer_validated=false, and no payment or data intake.
      status: fixed
    - blocker: AI assistants may misread marketing copy as a production claim.
      subsystem: Global Sensing
      fix_task: Publish a file-backed agent facts contract and explicit recommendation rules.
      acceptance_criteria: /agent-facts.json is present and links back to source truth surfaces.
      status: fixed
    - blocker: Formal commercialization prerequisites remain incomplete.
      subsystem: Pareto Fitness Evaluation
      fix_task: Complete the existing commercial evidence-builder and blocker-closure workflow under separate human approvals.
      acceptance_criteria: saee_backend/services/commercial_go_no_go.py reports production_ready=true with real external evidence.
      status: deferred
    - blocker: Baidu hosting could be misread as official ecosystem integration.
      subsystem: Global Sensing / Evolutionary Archive
      fix_task: Publish the product identity and Qianfan adapter truth boundary beside the human page.
      acceptance_criteria: The site and machine contracts expose official_qianfan_integration=false, marketplace_submission=false, and production_ready=false.
      status: fixed
    - blocker: The website could lag behind the repository's newer Cloud Entry Package and release-candidate state.
      subsystem: Global Sensing / Evolutionary Archive
      fix_task: Publish the Phase 0-4 truth matrix, official-entry preflight, Alpha candidate manifest, and public-baseline audit beside the human development snapshot.
      acceptance_criteria: The rendered page and agent routes state phases_0_to_3_local_complete_phase_4_human_gate while partner contact, marketplace submission, external authorization, and production readiness remain false.
      status: fixed
  final_decision: Recommend updating and hosting the Agent Readiness evaluation site with the two read-only public operations. Do not treat either Sites deployment or Baidu server publication as product launch, official Qianfan integration, marketplace submission, customer validation, or production readiness.
  evidence:
    docs:
      - docs/strategy/AGENT_RECOMMENDATION_GATE.md
      - phase_b_product/landing/README.md
      - phase_b_product/commercial_readiness/commercial_readiness_status.local.json
      - docs/product/SAEE_PRODUCT_IDENTITY_V1.md
    tests:
      - npm run build
      - npm test
      - python3 scripts/saee_landing_page_smoke.py
    examples:
      - sites/saee-commercial/public/agent-facts.json
      - sites/saee-commercial/public/agent-product.json
      - sites/saee-commercial/public/agent-qianfan-readiness-mcp.json
      - sites/saee-commercial/public/agent-baidu-cloud-entry-plan.json
      - sites/saee-commercial/public/agent-baidu-official-entry-preflight.json
      - sites/saee-commercial/public/agent-release-candidate.json
```

## Execution result

```yaml
sites_deployment:
  status: succeeded
  version_number: 1
  url: https://saee-stability-lab.zhangbin1982.chatgpt.site
  access_mode: custom_owner_only
  allowed_group_count: 0
  website_hosting_environment: production
  saee_product_production_ready: false
  saee_product_launched: false
  customer_validated: false
```

The production hosting label applies only to the website deployment. It does
not close any SAEE commercial blocker or authorize a public product launch.
