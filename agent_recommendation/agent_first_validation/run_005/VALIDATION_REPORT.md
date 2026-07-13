# SAEE Baidu Qianfan External Agent Host Validation Run 005

## Verdict

- Limited scope: `recommend` from the independent recommendation gate after
  live validation.
- Three real Qianfan function-calling roundtrips: `3/3` pass.
- Provider: `baidu_qianfan`; model: `ernie-4.5-turbo-128k`.
- The host is a user-supplied-credential bridge, not Qianfan-native MCP support.

## Replayable evidence

- `provider_transcript.redacted.jsonl`: provider request/response metadata,
  tool names, tool-call argument hashes, and final response hash; no key or
  Authorization header.
- `mcp_transcript.jsonl`: initialize, initialized notification, tools/list,
  both tools/call messages, and structured responses.
- `tool_schema_crosswalk.json`: MCP tool list and Qianfan function crosswalk.
- `receipt.json`: schema-valid observed receipt from the fixed sanitized fixture.
- `roundtrip_runs.local.json`: three successful run summaries and final hashes.
- `roundtrip_evidence_manifest.json`: per-run final-answer, receipt, provider
  transcript, and MCP transcript hashes for `run_001`–`run_003`.
- `roundtrips/run_001..003/`: replayable redacted evidence for each live run.
- `negative_cases.local.json`: 13 individually named fail-closed cases, each
  recording rejection and `side_effects=none`.
- `validation_result.redacted.json`: redacted provider/MCP/receipt truth flags.

## Verified facts

- Qianfan first selected `describe_saee`, then
  `compare_observed_traces`.
- The only MCP tools were `describe_saee` and `compare_observed_traces`.
- Winner: `candidate-alpha`; score: `0.719476`.
- Evaluation mode: `observed_trace_bundle_evaluation`.
- CLI, MCP, and bridge request/content hashes match.
- MCP process return code: `0`; stderr bytes: `0`.
- Qianfan network was used by the host; SAEE MCP network usage was `false`.
- Local fail-closed smoke: `13/13` negative cases pass.

## Truth boundary

This proves a real Baidu Qianfan external host can call the fixed local SAEE
MCP adapter with an approved sanitized fixture. It does not prove Qianfan
native MCP support, customer validation, source authenticity, no-PII status,
production readiness, product launch, or external-world execution.
