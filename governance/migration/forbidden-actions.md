# Forbidden Actions During Phase 0

Phase 0 must not:

- modify business logic, evaluators or capability runtime behavior;
- create a new capability or a second capability fact source;
- create a second canonical SAEE MCP entry;
- rename, merge or remove MCP tools or endpoints;
- modify the website or public product copy;
- modify Aliyun products `68657` or `68658`;
- access private provider services or read secrets;
- modify or deploy Agent Evidence Receipt runtime;
- move, merge, reset, restore or clean any repository;
- copy Agent Evidence, POP, AOP or ARO source into SAEE;
- treat host sharing as runtime integration;
- treat a signature as proof of original-event authenticity, provider origin,
  completeness, accountability or legal status;
- treat a trace as evidence or responsibility proof without an explicit trusted
  conversion contract;
- promote local, synthetic, package-ready, submitted or review states to
  customer-validated, listed, production-ready or approved;
- push, open a PR or perform any external action without separate authorization.

If a requested change requires one of these actions, stop and create a bounded
proposal for the next phase instead of implementing it.
