# Codex Governance Rules

Every Codex or AI Agent change must read the constitution, governance entry and
canonical capability inventory before planning implementation.

## Mandatory pre-change answers

1. **Affected Layer** — Evidence, Evaluation, Governance, Autonomous or Outside?
2. **Affected Object** — exact repository, capability, MCP, product, schema,
   runtime, website or external system ID?
3. **Capability Impact** — implemented behavior, contract, projection or no
   capability fact change?
4. **Duplication Check** — which canonical inventory, code, schema, test,
   example and historical artifact was searched?
5. **Standard Alignment** — which constitution rule, ADR, schema and external
   protocol/version applies?
6. **Non Claims** — what does the change explicitly not prove or authorize?
7. **Validation Plan** — which deterministic checks, negative cases, staged
   truth checks and rollback evidence will be used?

Use `governance/codex/change-template.md` to record the answers.

## Prohibitions

Codex must not:

- create duplicate Evidence implementations;
- create a second Capability Registry or capability fact source;
- create a second canonical SAEE MCP entrance;
- promote an experiment, local pass, synthetic pass, package, endpoint smoke,
  submission or review state into production;
- treat a signature or digest as event authenticity;
- treat a Trace as responsibility proof;
- infer repository ownership, canonicality or merge authority from a name;
- change external systems, pricing, contracts, marketplace state, customer data
  use, permissions or deployment without explicit authorization.

## Required routing

```text
constitution -> governance registries -> canonical capability inventory
-> existing implementation/tests -> recommendation gate -> bounded change
-> validator -> staged truth report
```

If records disagree, use the narrowest verified state, report the drift and
stop before consequential mutation.
