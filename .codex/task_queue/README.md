# SAEE Codex Task Queue

Every task must have:

- objective
- allowed files
- validation
- rollback point

Do not send large mixed tasks.

Recommended workflow:

1. Create one task file using `.codex/task_template.md`.
2. Run `python3 scripts/codex_prepare_task.py .codex/task_queue/<task-file>.md`.
3. Execute only the stated scope.
4. Run the validation command listed in the task.
