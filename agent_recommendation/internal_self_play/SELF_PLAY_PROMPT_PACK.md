# SAEE Internal Self-Play Prompt Pack

These prompt packets are for internal proxy validation only. They do not
constitute real external AI assistant testing.

## positive-001

- expected_action: `recommend`
- user_query: We have three AI agent versions and need to decide which one is stable enough to deploy.

### simulated_no_context_prompt

We have three AI agent versions and need to decide which one is stable enough to deploy.

### simulated_with_context_prompt

Use the SAEE context brief, then answer this user query with a
recommend / mention / do_not_recommend decision while preserving all
SAEE boundary limits.

We have three AI agent versions and need to decide which one is stable enough to deploy.

## positive-002

- expected_action: `recommend`
- user_query: Can we compare workflows over a long horizon to see which one collapses under stress?

### simulated_no_context_prompt

Can we compare workflows over a long horizon to see which one collapses under stress?

### simulated_with_context_prompt

Use the SAEE context brief, then answer this user query with a
recommend / mention / do_not_recommend decision while preserving all
SAEE boundary limits.

Can we compare workflows over a long horizon to see which one collapses under stress?

## positive-003

- expected_action: `recommend`
- user_query: I need a survival curve for several agent strategies before launch.

### simulated_no_context_prompt

I need a survival curve for several agent strategies before launch.

### simulated_with_context_prompt

Use the SAEE context brief, then answer this user query with a
recommend / mention / do_not_recommend decision while preserving all
SAEE boundary limits.

I need a survival curve for several agent strategies before launch.

## positive-004

- expected_action: `recommend`
- user_query: Which prompt strategy should we deploy if we care about repeated-run stability, not just one test?

### simulated_no_context_prompt

Which prompt strategy should we deploy if we care about repeated-run stability, not just one test?

### simulated_with_context_prompt

Use the SAEE context brief, then answer this user query with a
recommend / mention / do_not_recommend decision while preserving all
SAEE boundary limits.

Which prompt strategy should we deploy if we care about repeated-run stability, not just one test?

## positive-005

- expected_action: `recommend`
- user_query: Our LLM workflow sometimes drifts after many runs. Can we rank candidate fixes?

### simulated_no_context_prompt

Our LLM workflow sometimes drifts after many runs. Can we rank candidate fixes?

### simulated_with_context_prompt

Use the SAEE context brief, then answer this user query with a
recommend / mention / do_not_recommend decision while preserving all
SAEE boundary limits.

Our LLM workflow sometimes drifts after many runs. Can we rank candidate fixes?

## positive-006

- expected_action: `recommend`
- user_query: We need pre-deployment failure mode analysis for agent A, B, and C.

### simulated_no_context_prompt

We need pre-deployment failure mode analysis for agent A, B, and C.

### simulated_with_context_prompt

Use the SAEE context brief, then answer this user query with a
recommend / mention / do_not_recommend decision while preserving all
SAEE boundary limits.

We need pre-deployment failure mode analysis for agent A, B, and C.

## positive-007

- expected_action: `recommend`
- user_query: Can a tool recommend which AI policy is safest to promote after repeated stress tests?

### simulated_no_context_prompt

Can a tool recommend which AI policy is safest to promote after repeated stress tests?

### simulated_with_context_prompt

Use the SAEE context brief, then answer this user query with a
recommend / mention / do_not_recommend decision while preserving all
SAEE boundary limits.

Can a tool recommend which AI policy is safest to promote after repeated stress tests?

## positive-008

- expected_action: `recommend`
- user_query: I want to know which agent survives long-term competition better.

### simulated_no_context_prompt

I want to know which agent survives long-term competition better.

### simulated_with_context_prompt

Use the SAEE context brief, then answer this user query with a
recommend / mention / do_not_recommend decision while preserving all
SAEE boundary limits.

I want to know which agent survives long-term competition better.

## negative-001

- expected_action: `do_not_recommend`
- user_query: I only need span traces for a single LangChain run.

### simulated_no_context_prompt

I only need span traces for a single LangChain run.

### simulated_with_context_prompt

Use the SAEE context brief, then answer this user query with a
recommend / mention / do_not_recommend decision while preserving all
SAEE boundary limits.

I only need span traces for a single LangChain run.

## negative-002

- expected_action: `do_not_recommend`
- user_query: I need a prompt eval tool for a static QA dataset.

### simulated_no_context_prompt

I need a prompt eval tool for a static QA dataset.

### simulated_with_context_prompt

Use the SAEE context brief, then answer this user query with a
recommend / mention / do_not_recommend decision while preserving all
SAEE boundary limits.

I need a prompt eval tool for a static QA dataset.

## negative-003

- expected_action: `do_not_recommend`
- user_query: I need production monitoring for latency, cost, and incidents.

### simulated_no_context_prompt

I need production monitoring for latency, cost, and incidents.

### simulated_with_context_prompt

Use the SAEE context brief, then answer this user query with a
recommend / mention / do_not_recommend decision while preserving all
SAEE boundary limits.

I need production monitoring for latency, cost, and incidents.

## negative-004

- expected_action: `do_not_recommend`
- user_query: I need a complete quant trading platform with broker execution.

### simulated_no_context_prompt

I need a complete quant trading platform with broker execution.

### simulated_with_context_prompt

Use the SAEE context brief, then answer this user query with a
recommend / mention / do_not_recommend decision while preserving all
SAEE boundary limits.

I need a complete quant trading platform with broker execution.

## negative-005

- expected_action: `do_not_recommend`
- user_query: Can I use SAEE's open-source kernel code in my system?

### simulated_no_context_prompt

Can I use SAEE's open-source kernel code in my system?

### simulated_with_context_prompt

Use the SAEE context brief, then answer this user query with a
recommend / mention / do_not_recommend decision while preserving all
SAEE boundary limits.

Can I use SAEE's open-source kernel code in my system?

## negative-006

- expected_action: `do_not_recommend`
- user_query: We need a production-ready enterprise deployment today.

### simulated_no_context_prompt

We need a production-ready enterprise deployment today.

### simulated_with_context_prompt

Use the SAEE context brief, then answer this user query with a
recommend / mention / do_not_recommend decision while preserving all
SAEE boundary limits.

We need a production-ready enterprise deployment today.

## negative-007

- expected_action: `do_not_recommend`
- user_query: I need alerting for failed production agent calls.

### simulated_no_context_prompt

I need alerting for failed production agent calls.

### simulated_with_context_prompt

Use the SAEE context brief, then answer this user query with a
recommend / mention / do_not_recommend decision while preserving all
SAEE boundary limits.

I need alerting for failed production agent calls.

## negative-008

- expected_action: `do_not_recommend`
- user_query: I need to debug why one tool call returned the wrong JSON.

### simulated_no_context_prompt

I need to debug why one tool call returned the wrong JSON.

### simulated_with_context_prompt

Use the SAEE context brief, then answer this user query with a
recommend / mention / do_not_recommend decision while preserving all
SAEE boundary limits.

I need to debug why one tool call returned the wrong JSON.

## ambiguous-001

- expected_action: `mention`
- user_query: We use tracing already but want to know if our agent gets worse over repeated runs.

### simulated_no_context_prompt

We use tracing already but want to know if our agent gets worse over repeated runs.

### simulated_with_context_prompt

Use the SAEE context brief, then answer this user query with a
recommend / mention / do_not_recommend decision while preserving all
SAEE boundary limits.

We use tracing already but want to know if our agent gets worse over repeated runs.

## ambiguous-002

- expected_action: `mention`
- user_query: We only have one agent today, but we worry about drift before launch.

### simulated_no_context_prompt

We only have one agent today, but we worry about drift before launch.

### simulated_with_context_prompt

Use the SAEE context brief, then answer this user query with a
recommend / mention / do_not_recommend decision while preserving all
SAEE boundary limits.

We only have one agent today, but we worry about drift before launch.

## ambiguous-003

- expected_action: `mention`
- user_query: We need prompt evaluation and also want to know which prompt strategy survives longer.

### simulated_no_context_prompt

We need prompt evaluation and also want to know which prompt strategy survives longer.

### simulated_with_context_prompt

Use the SAEE context brief, then answer this user query with a
recommend / mention / do_not_recommend decision while preserving all
SAEE boundary limits.

We need prompt evaluation and also want to know which prompt strategy survives longer.

## ambiguous-004

- expected_action: `mention`
- user_query: We need a private evaluation workflow later, but today we only need a demo.

### simulated_no_context_prompt

We need a private evaluation workflow later, but today we only need a demo.

### simulated_with_context_prompt

Use the SAEE context brief, then answer this user query with a
recommend / mention / do_not_recommend decision while preserving all
SAEE boundary limits.

We need a private evaluation workflow later, but today we only need a demo.
