# ADR-0003: MCP Namespace Boundary

## Status

Accepted for Phase 0.

## Context

SAEE contains canonical, compatibility, internal and legacy MCP surfaces.
Agent Evidence Receipt has a separate public three-tool MCP product, and the
independent validator package has another tool set. Shared transport does not
make these surfaces one product.

## Decision

```text
saee.*=SAEE_ONLY
receipt.*=AGENT_EVIDENCE_RECEIPT_ONLY
internal.saee.*=SAEE_INTERNAL_ONLY
legacy.saee.*=SAEE_LEGACY_ONLY
```

The canonical SAEE surface is:

```text
scripts/saee_agent_readiness_mcp_stdio.py
saee.evaluate_agent_run
saee.evaluate_evidence
```

The canonical Agent Evidence Receipt product surface remains its current
three-tool endpoint. Its logical governance namespace is `receipt.*`; the
currently published unprefixed tool names are recorded exactly and are not
renamed in Phase 0.

`canonical=true` is owner-scoped. The Receipt MCP may be canonical for the
Receipt product while never being canonical for SAEE.

## Rules

- different products may not claim the same canonical namespace;
- compatibility wrappers may share SAEE tool names only when they route to the
  same canonical implementation and remain `canonical=false`;
- internal or legacy tools may not be advertised as the public SAEE product;
- endpoint host sharing does not transfer namespace ownership;
- any future rename requires versioned compatibility and an explicit migration
  decision.

## Non-goals

- modifying MCP code, transport, endpoint or tools;
- deploying the SAEE MCP publicly;
- deprecating the Qianfan or legacy surface;
- changing the Agent Evidence Receipt marketplace contract.
