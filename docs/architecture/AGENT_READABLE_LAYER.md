# Agent-Readable Layer
# 智能体可读层

Every meaningful code or protocol surface must help future agents answer:
每个重要代码或协议表面都必须帮助未来智能体回答：

1. What is this component for?
2. Which SAEE subsystem does it strengthen?
3. What inputs and outputs does it accept?
4. What schema, examples, or tests prove the contract?
5. What safety, license, supply-chain, and permission boundaries apply?
6. What should not be inferred from this component?

## First-Class Product Surface

The agent-readable layer is not supporting documentation. Under the active
Agent-Native Commercial Logic v2.0, it is a first-class product and discovery
surface. A future agent should be able to discover the capability, understand
fit and non-fit, invoke or validate it safely, and compose it through stable
contracts before recommending it to a human.

Every prioritized capability must answer:

1. Can an AI agent discover it?
2. Can an AI agent understand when to use it?
3. Can an AI agent compose it into workflows?

See `docs/strategy/SAEE_AGENT_NATIVE_COMMERCIAL_LOGIC_V2.md`.

## Minimum Files for New Components

For a new component, add or update:

- local `README.md`;
- related schema under `schemas/` when structured records are used;
- example input/output under `examples/` when practical;
- guard or test command;
- `agent-index.json` when public entrypoints change;
- `llms.txt` when the retrieval or citation surface changes.
