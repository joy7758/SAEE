# SAEE Current Commercial Primary Action Gate v0.3

Status: `agent_first_commercial_preview_is_current_primary_action`.

The current commercial adoption path is a fixed two-tool MCP stdio adapter:

```bash
python3 scripts/saee_mcp_stdio.py
```

It implements MCP revision `2025-11-25` and exposes only `describe_saee` and
`compare_observed_traces`. Observed input and receipt schemas remain canonical.

## Truth boundary

- Evaluation mode: `observed_trace_bundle_evaluation`.
- MCP stdio adapter / fixed tool count: `true` / `2`.
- Dynamic tools / arbitrary file input: `false` / `false`.
- Observed evidence evaluation available: `true`.
- Trace capture by SAEE: `false`.
- Source authenticity / PII absence verified: `false` / `false`.
- Candidate code and external systems executed: `false`.
- Human validation is primary: `false`.
- Production ready / product launched: `false` / `false`.
- Independent-agent rerun completed: `true`.
- Three file-backed commercial walkthroughs: `recommend_3_of_3_agents_blockers_0`.
- Limited Baidu Qianfan host bridge: `recommend_limited_user_supplied_qianfan_host_bridge`.
- Walkthroughs are real customer evidence: `false`.
- Private Sites v38 deployed: `true`.
- Phase 1 local code/contracts/tests/sanitized evidence authorized: `true`.
- Phase 1 external execution and production deployment authorized: `false` / `false`.
- Strict RBAC role-permission consistency negative cases: `5/5`.
- Tenant-required memory/SQLite stores deny unscoped operations: `true` / `true`.
- Production tenant storage isolated / migration executed: `false` / `false`.

Older human-validation and synthetic-only current-action records are historical
context, not the preferred commercial invocation.
