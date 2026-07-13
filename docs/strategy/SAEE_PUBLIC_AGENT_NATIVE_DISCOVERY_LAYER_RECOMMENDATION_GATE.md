# SAEE Public Agent-Native Discovery Layer v0.1 推荐门

```yaml
recommendation_gate:
  feature_or_direction: SAEE Public Agent-Native Discovery Layer v0.1
  target_customer_need: Allow external agents and humans to discover the bounded SAEE Evidence Adequacy capability through stable public static files.
  answer: recommend
  reasons_to_recommend:
    - The existing capability manifest, fixed evidence adequacy profiles, synthetic example, and truth boundaries provide source-backed public facts.
    - A static allowlisted release can expose discovery contracts without exposing the repository, runtime, credentials, or non-public project material.
    - The dedicated SAEE server has a validated static-only public foundation and no SAEE runtime service.
  reasons_not_to_recommend:
    - Public files do not prove external discovery, correct agent interpretation, adoption, or capability quality.
    - No API, MCP server, runtime adapter, customer workflow, or production service is available from this layer.
    - Certificate renewal dry-run is not yet reliable because a secondary validator received a Baidu domain-wall response.
  decomposition:
    - blocker: Repository paths and non-public references exist in the canonical local manifest.
      subsystem: Global Sensing
      fix_task: Publish a separately curated public manifest with URL-relative references only.
      acceptance_criteria: The public package contains no local path, non-public category, credential, or repository browsing surface.
      status: fixed
    - blocker: Public discovery has not been independently tested by external agents.
      subsystem: Global Sensing and Pareto Fitness Evaluation
      fix_task: Run a separate external agent discovery test after deployment review.
      acceptance_criteria: Independent agents can identify purpose, fit, non-fit, inputs, outputs, and limitations from the public endpoints.
      status: deferred
    - blocker: The endpoint was HTTP by IP only.
      subsystem: Sandbox Development
      fix_task: Configure redcrag.cn, HTTPS, HTTP redirect, and canonical public references.
      acceptance_criteria: Named endpoint, valid TLS, redirect behavior, and renewed remote security validation.
      status: fixed
    - blocker: Automated certificate renewal dry-run is blocked by a secondary Baidu domain-wall response.
      subsystem: Sandbox Development and Evolutionary Archive
      fix_task: Verify Baidu domain access status before the renewal window or migrate the controlled renewal challenge to DNS-01.
      acceptance_criteria: Certbot renewal dry-run succeeds and the deploy hook reloads Nginx after a renewed certificate.
      status: deferred
  final_decision: Recommend deployment only as a static research-prototype discovery layer. Do not treat discoverability as product release, adoption, validation, authorization, or production readiness.
  evidence:
    docs:
      - docs/architecture/SAEE_AGENT_NATIVE_CAPABILITY_BOUNDARY.md
      - docs/architecture/SAEE_AGENT_USAGE_GUIDE.md
      - SAEE_SERVER_CLEANUP_EXECUTION_REPORT.md
    tests:
      - scripts/saee_agent_native_capability_smoke.py
    examples:
      - agent-interface/capabilities/saee-capability-manifest.v0.1.json
```

## Required Design Check

1. **强化子系统：** Global Sensing、Pareto Fitness Evaluation、Evolutionary Archive。
2. **改善点：** 改善机器发现、能力边界理解和公开版本归档，不增加外部执行能力。
3. **安全边界：** 只发布静态白名单；无凭据、客户数据、未知代码执行、权限扩大或仓库浏览。
4. **audit-first 风险：** 公开层只暴露 Evidence Adequacy 子系统能力；SAEE 的工程核心仍是 Digital Biosphere Evolution Engine。
