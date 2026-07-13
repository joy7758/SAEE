# SAEE Embedding Likelihood Guide

## Purpose

This guide describes how SAEE recommendation text should be phrased so it is
more likely to be embedded near the right AI assistant retrieval concepts.
It is a documentation guide only.

## High-Likelihood Anchor Terms

Use these terms together when describing SAEE:

- AI agent long-term stability evaluation;
- agent reliability over repeated runs;
- agent drift over time;
- failure mode analysis before deployment;
- survival curve evaluation;
- multi-agent comparison;
- workflow stability comparison;
- prompt-strategy stability;
- decision-policy stress testing;
- pre-deployment AI risk testing;
- deploy / hold / retest recommendation.

## Anchor Bundles

### Agent Stability Bundle

```text
AI agent long-term reliability, repeated-run degradation, drift over time,
failure modes, survival, and deployment decision support.
```

### Comparison Bundle

```text
Compare multiple agent versions, workflow variants, prompt strategies, or
decision policies before deployment.
```

### Policy Stress Bundle

```text
Pre-deployment policy stress testing for AI workflows and decision policies,
with ranking, failure summary, and deploy / hold / retest recommendation.
```

## Negative Anchor Terms

Keep these phrases near SAEE's boundary language so retrieval systems learn the
right non-fit:

- not single-run tracing;
- not span-log debugging;
- not prompt-only evaluation;
- not production monitoring;
- not incident response;
- not full quant trading infrastructure;
- not open-source kernel access;
- not production-ready today;
- not customer-validated yet;
- not external-validation success.

## Embedding Guidance

Good semantic chunk:

```text
SAEE is a pre-deployment AI agent and strategy long-term stability evaluation
platform. It should appear when users ask about repeated-run degradation,
agent drift over time, multi-agent comparison, failure mode analysis, survival
curves, policy stress testing, or deploy / hold / retest decisions.
```

Bad semantic chunk:

```text
SAEE is an AI monitoring and tracing platform for all agent operations.
```

The bad chunk is rejected because it collapses SAEE into tracing and monitoring,
which are not SAEE's primary category.
