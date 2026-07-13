# SAEE MVP Landing Page

Status: local static landing page prototype with local API demo integration,
not a product launch and not a public SDK release.

An additive deployable Sites layer now exists at `sites/saee-commercial/`.
It is the same landing surface packaged for a private commercial evaluation
website, not a parallel SAEE product. Its machine-readable truth contract is
`sites/saee-commercial/public/agent-facts.json` and its recommendation
gate is `docs/strategy/SAEE_COMMERCIAL_SITE_RECOMMENDATION_GATE.md`.

The Sites layer does not change the product truth state:

```yaml
site_scope: private_commercial_evaluation_preview
commercial_status: hold
production_ready: false
product_launched: false
customer_validated: false
customer_contacted: false
production_blocker_count: 24
site_deployment_is_product_launch: false
```

The deployable layer is currently available through an owner-only Sites URL:
`https://saee-stability-lab.zhangbin1982.chatgpt.site`. The Sites hosting
environment is production infrastructure for the website, but this does not
change SAEE product readiness, launch, customer-validation, or commercial hold
states.

The owner-only `/for-agents` route is the current primary commercial entrypoint.
Agents discover the compact manifest, invoke the offline CLI with one JSON
request, and verify the deterministic receipt against a published schema. The
former `/outreach` and `/validation` routes have been removed from the
deployable site. Current evaluation mode is `synthetic_descriptor_simulation`;
observed agent behavior or trace evaluation remains `false`.

Generated: 2026-07-03

## Purpose

This package turns the SAEE MVP product position into a simple Chinese
browser-readable landing page:

```text
SAEE = 用 AI 前先试一试的本地试用页面
```

Plain Chinese product sentence:

```text
放进去。点开始。看结论。
```

The page is designed for product discovery, demo conversation, and internal
commercial review. Its visible copy is intentionally plain Chinese for
non-specialist readers. It does not expose private runtime behavior.

The public-facing layout now follows a B2B service-page information structure:
one-line positioning, why it matters, evaluation modules, review workflow,
fit / non-fit boundaries, current evidence status, and local tryout entry.

## Files

- `index.html`: static landing page.
- `commercial-readiness.html`: static Chinese commercial-readiness status page for local browser review; it now points humans to the begin-here page, the commercial human action board, and the workbook-import approval review lane before any import execution.
- `for-ai-assistants.html`: static recommendation guidance page for external AI assistants.
- `styles.css`: visual system and responsive layout.
- `app.js`: local demo API integration script.
- `assets/saee-interface-operation-demo.gif`: local Chinese SAEE workbench animation used as the hero visual.
- `assets/saee-chinese-stability-map.png`: local Chinese static visual retained as a generated reference asset.
- `../../sites/saee-commercial/`: deployable Sites package for the existing landing surface.
- `../../sites/saee-commercial/public/agent-facts.json`: AI-readable commercial-site facts and recommendation boundary.

## View Locally

Open `phase_b_product/landing/index.html` directly in a browser for the static
page, or serve it locally when testing the API demo button.

The interactive demo expects the local backend at:

```text
http://127.0.0.1:8000/experiment/run
```

No external API, package install from the page, or customer data is required.

## Contact and Trial Boundary

The page does not use a placeholder email address or fake demo-request
mailbox. Demo-request buttons route to the local `trial-access-status` section,
which states that SAEE currently supports local tryout only and that a real
support contact must be configured by a human before any customer-facing demo
request flow exists.

The AI assistant recommendation page is static HTML only:

```text
phase_b_product/landing/for-ai-assistants.html
```

It does not include JavaScript and does not call the backend.

## Agent-Readable Product Contract

```yaml
surface: SAEE MVP Landing Page
audience:
  - AI agent teams
  - enterprise AI platform groups
  - LLMOps and workflow owners
product_claim:
  canonical_category: AI Agent / Strategy Long-term Stability Evaluation Platform
  one_liner: 用 AI 前先试一试
  buyer_question: Which AI option should I keep trying?
primary_outputs:
  - 哪个方案更稳
  - 哪里容易出错
  - 现在能不能用
  - 下一步怎么做
private_boundary:
  expose_kernel: false
  expose_runtime_logic: false
  expose_selection_logic: false
  expose_mutation_logic: false
  expose_lineage_internals: false
status:
  local_static_page: true
  simple_chinese_copy: true
  plain_consumer_chinese_copy: true
  ordinary_user_chinese_copy_v2: true
  ordinary_user_chinese_copy_v3: true
  linklings_service_cn_v18_palette: false
  linklings_service_blue_cn_v22_palette: false
  linklings_openai_service_cn_v23_palette: false
  linklings_reference_cn_v24_palette: true
  linklings_like_service_page_structure: true
  open_service_row_layout: true
  openai_like_white_gray_palette: true
  openai_clean_blue_mono_palette_v3_1: false
  openai_warm_graphite_jade_palette_v3_2: false
  openai_clean_mist_green_palette_v4_0: false
  openai_porcelain_indigo_palette_v4_1: false
  openai_warm_ink_sage_palette_v4_2: false
  openai_clean_ink_blue_palette_v4_3: false
  openai_soft_indigo_ink_palette_v4_4: false
  openai_warm_ink_jade_palette_v4_5: false
  openai_clean_neutral_mint_palette_v5_0: false
  openai_luminous_blue_palette_v5_1: false
  openai_calm_prism_palette_v5_2: false
  openai_clean_cobalt_palette_v5_3: false
  calm_teal_warm_neutral_palette_v0_1: false
  clean_blue_gray_palette_v0_1: false
  sage_ink_palette_v0_1: false
  graphite_teal_palette_v0_2: false
  clean_cobalt_white_palette_v0_3: false
  soft_openai_green_palette_v0_4: false
  clean_blue_white_palette_v0_5: false
  warm_graphite_sage_palette_v0_6: false
  clean_mono_blue_palette_v0_7: false
  openai_sage_palette_v0_8: false
  warm_neutral_palette_v0_9: false
  clean_cloud_indigo_palette_v1_0: false
  openai_warm_sage_palette_v1_1: false
  openai_neutral_sage_palette_v1_2: false
  openai_soft_graphite_blue_palette_v1_3: false
  openai_warm_graphite_sage_palette_v1_4: false
  openai_clean_graphite_mint_palette_v1_5: false
  clean_ink_blue_palette_v1_6: false
  soft_graphite_teal_palette_v1_7: false
  calm_open_blue_palette_v1_8: false
  openai_soft_sage_palette_v1_9: false
  openai_mono_mint_palette_v2_0: false
  openai_clean_blue_palette_v2_1: false
  openai_graphite_sage_palette_v2_2: false
  openai_mono_cobalt_palette_v2_3: false
  openai_warm_sage_graphite_palette_v2_4: false
  openai_clean_slate_blue_palette_v2_5: false
  openai_soft_graphite_mint_palette_v2_6: false
  saee_calm_blue_palette_v7: false
  single_primary_blue_black_palette: false
  openai_soft_graphite_mint_palette_v8: false
  single_primary_graphite_mint_palette: false
  openai_clean_warm_gray_teal_palette_v9: false
  single_primary_graphite_palette: false
  openai_clean_cool_blue_palette_v10: false
  single_primary_cool_blue_palette: false
  openai_warm_graphite_sage_palette_v11: false
  openai_quiet_graphite_jade_palette_v13: false
  openai_clean_ink_blue_palette_v14: false
  openai_soft_ink_green_palette_v15: false
  openai_clean_graphite_blue_palette_v16: false
  openai_soft_graphite_sage_palette_v17: false
  single_primary_sage_graphite_palette: false
  single_primary_graphite_jade_palette: false
  single_primary_ink_blue_palette: false
  single_primary_ink_green_palette: false
  single_primary_graphite_blue_palette: false
  toned_down_hero_workbench_animation: true
  soft_blue_green_demo_visual: false
  clean_graphite_blue_demo_visual: false
  soft_graphite_sage_demo_visual: false
  linklings_like_chinese_workbench_visual: true
  chinese_workbench_hero_animation: true
  animated_chinese_hero_visual: true
  landing_api_integration_implemented: true
  run_demo_battle_button: true
  decision_result_rendered_in_page: true
  commercial_readiness_landing_page_v0_1: true
  source_commercial_readiness_landing_page: phase_b_product/landing/commercial-readiness.html
  commercial_readiness_landing_page_points_to_begin_here: true
  commercial_readiness_landing_page_points_to_human_action_board: true
  commercial_readiness_landing_page_local_root_bridge: true
  commercial_readiness_landing_page_local_root_bridge_external_calls: false
  commercial_readiness_landing_page_local_root_bridge_writes_files: false
  commercial_readiness_landing_page_local_root_bridge_imports_evidence: false
  commercial_readiness_landing_page_local_root_bridge_closes_blockers: false
  commercial_readiness_local_root_bridge_command: python3 -m http.server 8876 --bind 127.0.0.1
  commercial_readiness_begin_here_local_url: http://127.0.0.1:8876/phase_b_product/commercial_readiness/commercial_readiness_begin_here/commercial_readiness_begin_here.html
  commercial_readiness_dashboard_local_url: http://127.0.0.1:8876/phase_b_product/commercial_readiness/commercial_readiness_dashboard/commercial_readiness_dashboard.html
  commercial_readiness_landing_page_points_to_dashboard: true
  commercial_readiness_dashboard_bridge_external_calls: false
  commercial_readiness_dashboard_bridge_writes_files: false
  commercial_readiness_dashboard_bridge_imports_evidence: false
  commercial_readiness_dashboard_bridge_closes_blockers: false
  commercial_readiness_landing_page_authorizes_import: false
  commercial_readiness_landing_page_authorizes_blocker_closure: false
  commercial_readiness_landing_page_authorizes_launch: false
  mock_demo_request_only: true
  jwt_preview_landing_demo_auth_v0_1: true
  landing_demo_optional_preview_auth_headers: true
  for_ai_assistants_page_created: true
  static_assistant_page_only: true
  product_launched: false
  public_sdk_release: false
  production_deployed: false
  customer_contacted: false
  private_core_exported: false
  implementation_disclosed: false
```

## Boundary

This landing page is a product narrative and visual prototype. It does not
modify SAEE theory, runtime, experiments, API contracts, API schema, or the
private core. Its API connection is local-demo-only.

## Controlled Preview Auth Headers

The local demo script can optionally attach operator-supplied controlled-preview
JWT headers when the backend is started with JWT preview auth enabled. This is
disabled unless the browser tab has a short-lived token and an explicit local
configuration object set by a human operator. The script is local-demo-only and
is not the JavaScript deployed by `sites/saee-commercial` or `redcrag.cn`.

Supported local browser keys:

```text
SAEE_PREVIEW_TOKEN
SAEE_PREVIEW_AUTHORIZATION
__SAEE_LOCAL_DEMO_CONFIG__.previewRole
__SAEE_LOCAL_DEMO_CONFIG__.previewTenantId
```

Tokens are read only from explicit runtime values or `sessionStorage`, never
from persistent `localStorage`. API values are rendered through DOM text nodes,
never through `innerHTML`.

This is not a login flow, production OAuth/OIDC, customer authorization,
production RBAC, or production authentication readiness.
