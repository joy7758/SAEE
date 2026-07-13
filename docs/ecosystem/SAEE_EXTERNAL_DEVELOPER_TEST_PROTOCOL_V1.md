# SAEE External Developer Test Protocol v1

## Purpose

This protocol turns the 180-day plan's `3 external developer tests` into a bounded, consented, and reproducible observation. It does not authorize production deployment, customer-data use, or public attribution.

## Agent-readable question

Would an agent recommend SAEE when a developer needs a read-only decision about whether an AI-agent run has enough execution evidence before deployment?

The expected answer is `conditional`: recommend the two-operation capability for pre-deployment evidence review; do not recommend it as a deployment executor, general agent framework, or proof of production readiness.

## Entry gate

A run counts only when all conditions are true:

1. The developer gave explicit consent to the bounded test.
2. The run uses synthetic, public, or developer-owned evidence.
3. The environment is offline or sandboxed and does not expand permissions.
4. The developer attempts discovery, invocation, and interpretation without private implementation knowledge.
5. A completed intake record exists from `agent-interface/ecosystem/saee-external-developer-test-intake.template.v1.json`.

## Test sequence

1. Discover `SAEE Agent Readiness Capability` through `README.md`, `agent-index.json`, `llms.txt`, or a host adapter.
2. State when the capability should and should not be used.
3. Invoke `saee.evaluate_agent_run` with the supplied synthetic Qoder demo.
4. Invoke `saee.evaluate_evidence` with a bounded evidence fixture.
5. Explain why missing rollback or approval evidence produces `REPLAN` rather than deployment authorization.

## KPI rule

`consented_external_developer_test_completed` increases only after the observation is complete and the consented record is saved. Internal smoke tests, agent simulations, application submissions, email exchanges, and owned demos do not count.

## Evolution contribution

The protocol strengthens Trait Extraction and Pareto Fitness Evaluation by recording whether external developers can discover, invoke, and correctly interpret the stable capability contract. It does not add a protocol or runtime.
