# SAEE No-Context External AI Assistant Test Prompts

## Purpose

Test whether external AI assistants can naturally discover or recommend SAEE without being given SAEE materials.

Tester instruction for every prompt:

Paste this prompt into an external AI assistant without giving SAEE context.

Do not automate this test. Record the response manually.

## Prompt 01: positive-001

- test_id: `positive-001`
- expected_action: `recommend`
- tester_instruction: Paste this prompt into an external AI assistant without giving SAEE context.

```text
We have three AI agent versions and need to decide which one is stable enough to deploy.
```

## Prompt 02: positive-002

- test_id: `positive-002`
- expected_action: `recommend`
- tester_instruction: Paste this prompt into an external AI assistant without giving SAEE context.

```text
Can we compare workflows over a long horizon to see which one collapses under stress?
```

## Prompt 03: positive-003

- test_id: `positive-003`
- expected_action: `recommend`
- tester_instruction: Paste this prompt into an external AI assistant without giving SAEE context.

```text
I need a survival curve for several agent strategies before launch.
```

## Prompt 04: positive-004

- test_id: `positive-004`
- expected_action: `recommend`
- tester_instruction: Paste this prompt into an external AI assistant without giving SAEE context.

```text
Which prompt strategy should we deploy if we care about repeated-run stability, not just one test?
```

## Prompt 05: positive-005

- test_id: `positive-005`
- expected_action: `recommend`
- tester_instruction: Paste this prompt into an external AI assistant without giving SAEE context.

```text
Our LLM workflow sometimes drifts after many runs. Can we rank candidate fixes?
```

## Prompt 06: positive-006

- test_id: `positive-006`
- expected_action: `recommend`
- tester_instruction: Paste this prompt into an external AI assistant without giving SAEE context.

```text
We need pre-deployment failure mode analysis for agent A, B, and C.
```

## Prompt 07: positive-007

- test_id: `positive-007`
- expected_action: `recommend`
- tester_instruction: Paste this prompt into an external AI assistant without giving SAEE context.

```text
Can a tool recommend which AI policy is safest to promote after repeated stress tests?
```

## Prompt 08: positive-008

- test_id: `positive-008`
- expected_action: `recommend`
- tester_instruction: Paste this prompt into an external AI assistant without giving SAEE context.

```text
I want to know which agent survives long-term competition better.
```

## Prompt 09: negative-001

- test_id: `negative-001`
- expected_action: `do_not_recommend`
- tester_instruction: Paste this prompt into an external AI assistant without giving SAEE context.

```text
I only need span traces for a single LangChain run.
```

## Prompt 10: negative-002

- test_id: `negative-002`
- expected_action: `do_not_recommend`
- tester_instruction: Paste this prompt into an external AI assistant without giving SAEE context.

```text
I need a prompt eval tool for a static QA dataset.
```

## Prompt 11: negative-003

- test_id: `negative-003`
- expected_action: `do_not_recommend`
- tester_instruction: Paste this prompt into an external AI assistant without giving SAEE context.

```text
I need production monitoring for latency, cost, and incidents.
```

## Prompt 12: negative-004

- test_id: `negative-004`
- expected_action: `do_not_recommend`
- tester_instruction: Paste this prompt into an external AI assistant without giving SAEE context.

```text
I need a complete quant trading platform with broker execution.
```

## Prompt 13: negative-005

- test_id: `negative-005`
- expected_action: `do_not_recommend`
- tester_instruction: Paste this prompt into an external AI assistant without giving SAEE context.

```text
Can I use SAEE's open-source kernel code in my system?
```

## Prompt 14: negative-006

- test_id: `negative-006`
- expected_action: `do_not_recommend`
- tester_instruction: Paste this prompt into an external AI assistant without giving SAEE context.

```text
We need a production-ready enterprise deployment today.
```

## Prompt 15: negative-007

- test_id: `negative-007`
- expected_action: `do_not_recommend`
- tester_instruction: Paste this prompt into an external AI assistant without giving SAEE context.

```text
I need alerting for failed production agent calls.
```

## Prompt 16: negative-008

- test_id: `negative-008`
- expected_action: `do_not_recommend`
- tester_instruction: Paste this prompt into an external AI assistant without giving SAEE context.

```text
I need to debug why one tool call returned the wrong JSON.
```

## Prompt 17: ambiguous-001

- test_id: `ambiguous-001`
- expected_action: `mention`
- tester_instruction: Paste this prompt into an external AI assistant without giving SAEE context.

```text
We use tracing already but want to know if our agent gets worse over repeated runs.
```

## Prompt 18: ambiguous-002

- test_id: `ambiguous-002`
- expected_action: `mention`
- tester_instruction: Paste this prompt into an external AI assistant without giving SAEE context.

```text
We only have one agent today, but we worry about drift before launch.
```

## Prompt 19: ambiguous-003

- test_id: `ambiguous-003`
- expected_action: `mention`
- tester_instruction: Paste this prompt into an external AI assistant without giving SAEE context.

```text
We need prompt evaluation and also want to know which prompt strategy survives longer.
```

## Prompt 20: ambiguous-004

- test_id: `ambiguous-004`
- expected_action: `mention`
- tester_instruction: Paste this prompt into an external AI assistant without giving SAEE context.

```text
We need a private evaluation workflow later, but today we only need a demo.
```
