# SAEE Qianfan Agent Host Recommendation Gate
# SAEE 百度千帆智能体宿主推荐门

## Recommendation question

If a potential customer wants to use Baidu Qianfan as an external agent host
to discover and call SAEE, would we recommend the integration?

如果潜在客户希望用百度千帆作为外部智能体宿主，发现并调用 SAEE，我们会推荐
这个集成吗？

## Verdict

`recommend_limited_user_supplied_qianfan_host_bridge`

Independent agent recommendation: `recommend` (3/3 profiles, 0 blockers).

The integration is recommendable only as a local, user-supplied-credential,
fixed-tool host adapter. It is not Qianfan-native MCP support, a remote MCP
service, a generic agent framework, a production SaaS feature, or customer
validation.

## Required design check

- Strengthened subsystems: Global Sensing, Trait Extraction, Counterfactual
  Simulation, Pareto Fitness Evaluation, and Evolutionary Archive.
- The external host selects tools; SAEE remains the fixed evolutionary sensing
  and fitness interface. The bridge must not move network capability into
  `scripts/saee_mcp_stdio.py`.
- The only allowed MCP tools are `describe_saee` and
  `compare_observed_traces`. The bridge accepts only the pre-approved sanitized
  fixture for this validation run.
- The provider key is read from `QIANFAN_API_KEY`, never placed in prompts,
  tool arguments, receipts, logs, source files, or evidence.

## Blocker decomposition and closure

1. **Provider roundtrip evidence**
   - Fix: perform a real Qianfan function-calling roundtrip through the fixed
     local MCP server and record redacted provider/MCP transcripts.
   - Acceptance: provider tool calls, MCP calls, schema-valid receipt, and final
     answer are all observed in one replayable evidence package.
   - Status: `closed`; `run_005/roundtrips/run_001..003` each contains a redacted
     provider/MCP transcript, receipt hash, and final-answer hash.
2. **Crosswalk and receipt integrity**
   - Fix: derive Qianfan function definitions from MCP `tools/list`, validate the
     returned arguments against the canonical observed bundle, and compare CLI,
     MCP, and bridge hashes.
   - Acceptance: tool list is exactly two tools; request/content hashes and rank
     match; schema errors are zero.
   - Status: `closed`; the three per-run manifests and `tool_schema_crosswalk.json`
     independently match the canonical receipt and hashes.
3. **Fail-closed and secret boundary**
   - Fix: hard-code the bridge argv and tool allowlist, cap rounds/size/depth,
     reject path/URL/command/code/secret/raw-log fields, strip the key from the
     MCP subprocess environment, and redact evidence.
   - Acceptance: at least eight negative cases pass; secret leakage count is
     zero; SAEE MCP remains network/socket/subprocess-free.
   - Status: `closed`; `negative_cases.local.json` records 13/13 case-level
     fail-closed outcomes with no side effects, and evidence smoke reports zero
     secret leakage.

## Development decision

Proceed only as a bounded user-supplied-credential integration. The provider
network call is external; SAEE's MCP server remains local and offline. This
limited recommendation does not authorize production launch, customer claims,
or external-world execution.

Evidence: `agent_recommendation/agent_first_validation/run_005/VALIDATION_REPORT.md`.

## Protocol basis

- Qianfan chat completions: `https://qianfan.baidubce.com/v2/chat/completions`
- Authentication: `Authorization: Bearer <API Key>`
- Function calling: tools are JSON Schema definitions; the model returns tool
  calls and the host executes them before sending tool results back.
- References: Baidu Qianfan official function-calling and API documentation.
