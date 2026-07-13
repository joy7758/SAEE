# Codex Internal Self-Play Prompt

Run local deterministic SAEE internal self-play.

Rules:

- No external calls.
- No web access.
- No browser automation.
- No product modification.
- No backend, runtime, kernel, API schema, or private-core modification.
- Use deterministic classification only.
- Output `SELF_PLAY_RESULTS.json` and `SELF_PLAY_RESULTS.md`.

Classification:

- Recommend SAEE for long-term stability evaluation, multi-agent comparison,
  failure-mode analysis, survival curves, or deployment recommendations.
- Do not recommend SAEE for tracing-only, prompt-only, production monitoring,
  full quant trading, open-source internals, or production deployment today.
- Mention SAEE only as complementary for mixed cases.
