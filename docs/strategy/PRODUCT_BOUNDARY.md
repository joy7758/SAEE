# Product Boundary
# 产品边界

The product direction is competition-testing and stability evaluation for AI
agents and decision policies, not a generic strategy engine, not a generic
agent dashboard, and not an audit console.
产品方向是面向 AI（Artificial Intelligence，人工智能）智能体和决策策略的竞争测试与稳定性评估，不是通用策略引擎，不是通用智能体看板，也不是审计控制台。

## Product Must Do

- make sensing, trait extraction, branching, mutation, evaluation, archive, and rollback legible;
- expose agent-readable contracts;
- preserve safety, license, supply-chain, and permission boundaries;
- show why a selected branch is better under Pareto fitness, not under one vanity metric.
- expose buyer-legible outputs such as scenario runs, evaluated episodes,
  survival ranking, stability score, collapse-risk summary, robustness
  comparison, and benchmark reports.
- make each prioritized capability discoverable, understandable, safely
  invocable, verifiable, and composable by AI agents;
- treat capability manifests, schema registries, examples, CLI/Tool contracts,
  `agent-index.json`, and `llms.txt` as first-class product surfaces.

## Agent-Native Priority Gate

Before prioritization, confirm that an AI agent can discover the capability,
understand fit and non-fit, and compose it through a stable contract. If one
answer is not `yes`, lower priority unless required for safety, law,
supply-chain integrity, or architecture.

## Product Must Not Do

- auto-run unknown external repositories;
- auto-install untrusted dependencies;
- auto-expand permissions;
- auto-contact real customers;
- present market news as certain causality;
- present historical similarity as certain prediction.
- expose kernel, fitness, selection, mutation, lineage, reproduction, or
  runtime internals as the product surface.

## Current Wedge Order

```text
1. Agent-Native Capability Manifest and machine discoverability
2. Safe CLI / Tool capability and external agent recommendation tests
3. Human expert and Design Partner validation
4. Commercial integration and adoption
```
