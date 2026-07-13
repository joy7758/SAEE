# SAEE MCP stdio Adapter Recommendation Gate

## Recommendation question

If a potential customer wants an AI agent to discover and call SAEE through a
standard tool protocol, should SAEE provide a fixed local stdio adapter?

## Agent verdict

`recommend`

The adapter may expose exactly two existing capabilities:
`describe_saee` and `compare_observed_traces`. It is a transport for the SAEE
evolutionary sensing and fitness interface, not a generic agent framework.

## Required design check

1. **Subsystem:** Global Sensing and Trait Extraction; secondarily Pareto
   Fitness Evaluation and Evolutionary Archive / Rollback Immune System.
2. **Loop effect:** improves evidence sensing, selection input, and archived
   receipts; does not claim branching or mutation improvement.
3. **Safety:** local newline-delimited JSON-RPC only; inline allowlisted bundle;
   no arbitrary file path, URL, command, dynamic import, subprocess, socket,
   trace capture, permission expansion, or private-core access.
4. **Framing risk:** generic-agent risk is medium-high and audit-first risk is
   medium-low. The fixed two-tool surface and no dynamic registration are
   non-negotiable.

## Protocol basis

- MCP protocol revision: `2025-11-25`.
- stdio messages: UTF-8 JSON-RPC objects delimited by newlines.
- Lifecycle: `initialize`, `notifications/initialized`, operation, EOF shutdown.
- Operations: `ping`, `tools/list`, `tools/call` only.
- Structured tool output is returned in `structuredContent` and duplicated as
  serialized JSON text for compatibility.

## Acceptance criteria

- Lifecycle and JSON-RPC transcript requests pass 20/20.
- `tools/list` always returns exactly two fixed tools.
- MCP input schema equals the canonical observed bundle schema; returned receipt
  validates with zero errors and matches CLI hashes 10/10.
- Unknown tools and command/code/URL/secret-shaped fields are rejected.
- stdout contains JSON-RPC frames only; stderr contains no sensitive data.
- No socket, subprocess, dynamic import, arbitrary file input, or trace capture.
- Oversized/deep/invalid requests fail without terminating the server; 100 mixed
  requests show no state leakage or filesystem writes.

Development is authorized only inside this fixed contract. Hosted HTTP MCP,
dynamic tools, resources, prompts, orchestration, monitoring, audit, production
readiness, or external adoption claims require separate gates.
