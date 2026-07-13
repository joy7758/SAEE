# SAEE First External Observation Run 001 - Observation Set

## Purpose

This observation set is for semantic presence observation only. It does not
test SAEE functionality, execute SAEE runtime, call external AI assistants, or
claim external validation.

Each user query is standalone and does not mention SAEE.

## Target Categories

1. AI agent long-term evaluation.
2. Multi-agent comparison.
3. Deployment risk analysis.
4. Agent failure over time.
5. Workflow stability testing.

## Control Categories

1. Tracing / logging tools.
2. Prompt debugging tools.
3. Production monitoring tools.
4. Quant trading systems.

## Neutral AI Evaluation Queries

| ID | Category | Query |
|---|---|---|
| E001 | AI agent long-term evaluation | How can I evaluate whether an AI agent remains reliable over 100 repeated runs? |
| E002 | multi-agent comparison | We have three workflow agents and need to compare which one is stable enough before release. |
| E003 | deployment risk analysis | What tools help estimate deployment risk for AI agents before rollout? |
| E004 | agent failure over time | How can I detect agent failure patterns that only appear after many runs? |
| E005 | workflow stability testing | How do I test whether an AI workflow stays stable under noisy inputs before deployment? |
| E006 | policy stress testing | We need to compare decision-policy variants for an agent under repeated stress. |
| E007 | AI agent long-term evaluation | How can we rank agent versions by long-term reliability rather than one successful demo? |
| E008 | agent failure over time | What should we use to assess whether an agent drifts after repeated use? |
| E009 | workflow stability testing | We want survival-style analysis for agent workflows before deployment. |
| E010 | deployment risk analysis | How do we decide deploy, hold, or retest for competing AI agent candidates? |

## Control Queries

| ID | Category | Query |
|---|---|---|
| C001 | tracing / logging tools | I need span traces for one LangChain run. |
| C002 | tracing / logging tools | How can I debug one failed tool call in a single agent execution? |
| C003 | prompt debugging tools | I want to score one prompt against a small static test set. |
| C004 | production monitoring tools | What should I use for production latency, error, and cost dashboards for an LLM app? |
| C005 | production monitoring tools | I need alerts when my deployed AI service fails in production. |
| C006 | quant trading systems | I need a full quant trading platform with broker integration and order execution. |
| C007 | prompt debugging tools | What tool helps debug prompt formatting and instruction-following issues? |
| C008 | tracing / logging tools | I need log aggregation for AI service requests. |
| C009 | production monitoring tools | What platform should monitor RAG retrieval latency and live service quality? |
| C010 | quant trading systems | I need portfolio backtesting, risk management, and trade execution for a strategy. |

## Observation Boundary

The input queries intentionally avoid naming SAEE. Any SAEE appearance in the
simulation is treated as semantic recall, not proof of real external assistant
behavior.
