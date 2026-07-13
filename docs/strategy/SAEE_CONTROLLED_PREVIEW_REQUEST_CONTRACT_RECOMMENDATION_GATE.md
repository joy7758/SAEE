# SAEE Controlled Preview Request Contract Recommendation Gate
# SAEE 受控商业预览请求契约推荐门

## Recommendation question

If a potential customer agent needs to request a bounded SAEE commercial
preview without sending customer data or authorizing external execution, would
we recommend this contract?

如果潜在客户的智能体需要在不发送客户数据、不开启外部执行的前提下申请
SAEE 受控商业预览，我们是否推荐这个契约？

## Verdict

`recommend`

The contract is recommendable only for a local or private controlled preview.
It validates a tenant/experiment envelope and routes the agent to an existing
offline evaluation command. It does not create an account, persist production
data, contact a customer, collect payment, execute candidate code, or claim
production readiness.

## Required design check

- Strengthened subsystems: Global Sensing, Trait Extraction, Counterfactual
  Simulation, and Evolutionary Archive / Rollback Immune System.
- The request is file-backed and agent-readable. Stable identifiers remain
  ASCII so agents can call the contract consistently in Chinese deployments.
- Tenant and experiment scope is explicit; the reserved `tenant:` experiment
  prefix is rejected before storage-key construction.
- All external-world, candidate-code, payment, customer-data, trace-capture,
  and production-claim flags are fixed to `false`.
- The contract does not move network access into the local SAEE MCP adapter and
  does not expose private evolution internals.

## Blocker decomposition

| Blocker | Subsystem | Fix task | Acceptance criteria | Status |
| --- | --- | --- | --- | --- |
| Agents lack a stable preview request envelope | Global Sensing | Add a strict JSON Schema and a deterministic validator | Valid example passes; missing/forbidden fields fail with no side effects | fixed |
| Preview requests could collide with tenant storage keys | Evolutionary Archive / Rollback Immune System | Reuse the reserved-prefix storage guard | `tenant:` experiment IDs fail and tenant scope remains explicit | fixed |
| Customers could mistake a request for production authorization | Pareto Fitness Evaluation | Make boundary flags and next action machine-readable | `production_ready=false`, `customer_validated=false`, and no execution flags remain false | fixed |
| Contract might be mistaken for billing or support readiness | Commercial boundary | Link the request to the 24-blocker hold contract | No blocker is closed and the production matrix is not mutated | deferred |

## Evidence

- Contract schema: `agent-interface/schemas/controlled-preview-request.schema.json`
- Valid example: `agent-interface/examples/controlled-preview-request.json`
- Validator: `scripts/saee_controlled_preview_request_validator.py`
- Smoke: `scripts/saee_controlled_preview_request_smoke.py`
- Tenant guard: `scripts/saee_tenant_storage_key_smoke.py`
- Production truth: `agent-interface/agent-first-commercial-preview-status.json`

## Final decision

Proceed as a bounded agent-first commercial-preview onboarding surface. Keep
production launch, customer validation, billing, support, and external actions
behind their existing separate evidence and approval gates.
