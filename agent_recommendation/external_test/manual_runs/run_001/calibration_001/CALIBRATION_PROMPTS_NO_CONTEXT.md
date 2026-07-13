# Calibration Prompts: No Context

Open a fresh external AI assistant conversation. Do not provide SAEE context.
Paste each prompt exactly and record the answer manually.

## CAL-001

- calibration_record_id: `CAL-001`
- base_test_id: `positive-001`
- expected_action: `recommend`
- tester_instruction: Open a fresh external AI assistant conversation. Do not provide SAEE context. Paste this prompt exactly. Record the answer manually.

prompt_to_copy:

```text
We have three AI agent versions and need to decide which one is stable enough to deploy.
```

## CAL-002

- calibration_record_id: `CAL-002`
- base_test_id: `negative-001`
- expected_action: `do_not_recommend`
- tester_instruction: Open a fresh external AI assistant conversation. Do not provide SAEE context. Paste this prompt exactly. Record the answer manually.

prompt_to_copy:

```text
I only need span traces for a single LangChain run.
```

## CAL-003

- calibration_record_id: `CAL-003`
- base_test_id: `ambiguous-001`
- expected_action: `mention`
- tester_instruction: Open a fresh external AI assistant conversation. Do not provide SAEE context. Paste this prompt exactly. Record the answer manually.

prompt_to_copy:

```text
We use tracing already but want to know if our agent gets worse over repeated runs.
```
