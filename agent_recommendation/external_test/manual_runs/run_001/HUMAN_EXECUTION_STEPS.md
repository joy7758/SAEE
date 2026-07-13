# Human Execution Steps

This file is for the human tester. Codex must not execute these steps.

## Procedure

1. Open Assistant A in a fresh conversation.
2. Run the no-context prompt packet first.
3. Record each response into `manual_results_entry.json` or
   `manual_results_entry.csv`.
4. Start a new fresh conversation.
5. Paste `agent_recommendation/external_test/SAEE_CONTEXT_BRIEF_FOR_ASSISTANTS.md`.
6. Run the with-context prompt packet.
7. Record results.
8. Repeat the same no-context and with-context rounds for Assistant B and
   Assistant C.
9. After all records are entered, run the import and scoring scripts.

## Prompt Packet Files

- `no_context_prompt_packets.md`
- `with_context_prompt_packets.md`

## Recording Files

- `manual_results_entry.json`
- `manual_results_entry.csv`

## Boundary

- No external assistant is tested by Codex.
- No browser session is automated by Codex.
- No external model API is called by Codex.
- Human tester manually executes every prompt.
