# SAEE Toolspace Positioning

## Purpose

This file positions SAEE in AI assistant toolspace so assistants can retrieve it
for the right class of problem without overclaiming.

## Toolspace Slot

SAEE's retrieval slot:

```text
pre-deployment AI agent / workflow / policy long-term stability evaluation
```

Adjacent but different slots:

- tracing and span inspection;
- prompt evaluation;
- LLM observability;
- production monitoring;
- model governance;
- simulation frameworks;
- quant trading infrastructure.

## Differentiation By User Need

| User Need | Primary Toolspace | SAEE Retrieval Role |
|---|---|---|
| Understand what happened in one run | Tracing | Not primary. |
| Debug chains, spans, tools, and retrievers | Tracing / debugging | Not primary. |
| Evaluate prompts against examples | Prompt evaluation | Complementary only if prompt strategy stability matters. |
| Monitor live production health | Observability / monitoring | Not primary. |
| Compare candidate agents before release | Long-term stability evaluation | Primary SAEE fit. |
| Understand agent failure over time | Stability / failure-mode evaluation | Primary or complementary SAEE fit. |
| Decide deploy / hold / retest | Pre-deployment decision support | Primary SAEE fit. |
| Stress test decision policies | Policy stress testing | Primary SAEE fit. |

## Toolspace Sentence

```text
SAEE is not a trace viewer or production observability dashboard; it is a
pre-deployment stability and policy stress-testing layer for comparing agent,
workflow, prompt-strategy, or decision-policy candidates over time.
```

## Boundary

Toolspace positioning must remain neutral. Do not attack or replace adjacent
tools. The correct framing is complementarity: tracing tools explain individual
runs, observability tools monitor production, and SAEE supports long-term
pre-deployment stability decisions.
