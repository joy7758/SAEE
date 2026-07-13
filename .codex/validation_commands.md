# SAEE Validation Commands

Run the narrow smoke test for the touched area first, then the shared guard.

```bash
python3 scripts/<specific_smoke_test>.py
python3 scripts/mainline_guard.py
make check
```

Codex context layer validation:

```bash
python3 scripts/codex_context_check.py
make check-codex-context
```

Use `make check` only for local validation. It must not call external services,
contact customers, publish product, or claim production readiness.
