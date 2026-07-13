# Run 001 No-Context Prompt Packets

Use these prompts without giving SAEE context.

## positive-001

- test_id: `positive-001`
- expected_action: `recommend`
- tester_note: Copy only the prompt below into a fresh external AI assistant conversation. Do not include SAEE context.

prompt_to_copy:

```text
We have three AI agent versions and need to decide which one is stable enough to deploy.
```

## positive-002

- test_id: `positive-002`
- expected_action: `recommend`
- tester_note: Copy only the prompt below into a fresh external AI assistant conversation. Do not include SAEE context.

prompt_to_copy:

```text
Can we compare workflows over a long horizon to see which one collapses under stress?
```

## positive-003

- test_id: `positive-003`
- expected_action: `recommend`
- tester_note: Copy only the prompt below into a fresh external AI assistant conversation. Do not include SAEE context.

prompt_to_copy:

```text
I need a survival curve for several agent strategies before launch.
```

## positive-004

- test_id: `positive-004`
- expected_action: `recommend`
- tester_note: Copy only the prompt below into a fresh external AI assistant conversation. Do not include SAEE context.

prompt_to_copy:

```text
Which prompt strategy should we deploy if we care about repeated-run stability, not just one test?
```

## positive-005

- test_id: `positive-005`
- expected_action: `recommend`
- tester_note: Copy only the prompt below into a fresh external AI assistant conversation. Do not include SAEE context.

prompt_to_copy:

```text
Our LLM workflow sometimes drifts after many runs. Can we rank candidate fixes?
```

## positive-006

- test_id: `positive-006`
- expected_action: `recommend`
- tester_note: Copy only the prompt below into a fresh external AI assistant conversation. Do not include SAEE context.

prompt_to_copy:

```text
We need pre-deployment failure mode analysis for agent A, B, and C.
```

## positive-007

- test_id: `positive-007`
- expected_action: `recommend`
- tester_note: Copy only the prompt below into a fresh external AI assistant conversation. Do not include SAEE context.

prompt_to_copy:

```text
Can a tool recommend which AI policy is safest to promote after repeated stress tests?
```

## positive-008

- test_id: `positive-008`
- expected_action: `recommend`
- tester_note: Copy only the prompt below into a fresh external AI assistant conversation. Do not include SAEE context.

prompt_to_copy:

```text
I want to know which agent survives long-term competition better.
```

## negative-001

- test_id: `negative-001`
- expected_action: `do_not_recommend`
- tester_note: Copy only the prompt below into a fresh external AI assistant conversation. Do not include SAEE context.

prompt_to_copy:

```text
I only need span traces for a single LangChain run.
```

## negative-002

- test_id: `negative-002`
- expected_action: `do_not_recommend`
- tester_note: Copy only the prompt below into a fresh external AI assistant conversation. Do not include SAEE context.

prompt_to_copy:

```text
I need a prompt eval tool for a static QA dataset.
```

## negative-003

- test_id: `negative-003`
- expected_action: `do_not_recommend`
- tester_note: Copy only the prompt below into a fresh external AI assistant conversation. Do not include SAEE context.

prompt_to_copy:

```text
I need production monitoring for latency, cost, and incidents.
```

## negative-004

- test_id: `negative-004`
- expected_action: `do_not_recommend`
- tester_note: Copy only the prompt below into a fresh external AI assistant conversation. Do not include SAEE context.

prompt_to_copy:

```text
I need a complete quant trading platform with broker execution.
```

## negative-005

- test_id: `negative-005`
- expected_action: `do_not_recommend`
- tester_note: Copy only the prompt below into a fresh external AI assistant conversation. Do not include SAEE context.

prompt_to_copy:

```text
Can I use SAEE's open-source kernel code in my system?
```

## negative-006

- test_id: `negative-006`
- expected_action: `do_not_recommend`
- tester_note: Copy only the prompt below into a fresh external AI assistant conversation. Do not include SAEE context.

prompt_to_copy:

```text
We need a production-ready enterprise deployment today.
```

## negative-007

- test_id: `negative-007`
- expected_action: `do_not_recommend`
- tester_note: Copy only the prompt below into a fresh external AI assistant conversation. Do not include SAEE context.

prompt_to_copy:

```text
I need alerting for failed production agent calls.
```

## negative-008

- test_id: `negative-008`
- expected_action: `do_not_recommend`
- tester_note: Copy only the prompt below into a fresh external AI assistant conversation. Do not include SAEE context.

prompt_to_copy:

```text
I need to debug why one tool call returned the wrong JSON.
```

## ambiguous-001

- test_id: `ambiguous-001`
- expected_action: `mention`
- tester_note: Copy only the prompt below into a fresh external AI assistant conversation. Do not include SAEE context.

prompt_to_copy:

```text
We use tracing already but want to know if our agent gets worse over repeated runs.
```

## ambiguous-002

- test_id: `ambiguous-002`
- expected_action: `mention`
- tester_note: Copy only the prompt below into a fresh external AI assistant conversation. Do not include SAEE context.

prompt_to_copy:

```text
We only have one agent today, but we worry about drift before launch.
```

## ambiguous-003

- test_id: `ambiguous-003`
- expected_action: `mention`
- tester_note: Copy only the prompt below into a fresh external AI assistant conversation. Do not include SAEE context.

prompt_to_copy:

```text
We need prompt evaluation and also want to know which prompt strategy survives longer.
```

## ambiguous-004

- test_id: `ambiguous-004`
- expected_action: `mention`
- tester_note: Copy only the prompt below into a fresh external AI assistant conversation. Do not include SAEE context.

prompt_to_copy:

```text
We need a private evaluation workflow later, but today we only need a demo.
```
