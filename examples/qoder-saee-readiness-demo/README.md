# Qoder + SAEE Coding Release Demo

Scenario: a coding Agent has changed code and passed a local test, then asks
whether it should proceed toward deployment.

```text
User request
  -> Qoder Agent prepares code and tests
  -> Qoder-compatible MCP client calls saee.evaluate_agent_run
  -> SAEE finds TEST_RESULT and PERMISSION_BOUNDARY
  -> SAEE finds ROLLBACK_PLAN and HUMAN_APPROVAL missing
  -> readiness=replan, recommendation=REPLAN
  -> no deployment occurs
```

The contrast is deliberate: "code complete" is not "ready to deploy".

Run the local compatibility proof:

```bash
python3 scripts/saee_qoder_adapter_smoke.py
```

The proof launches the repository-owned stdio server directly. Qoder CLI is not
installed in the validated environment, so `qoder_runtime_validated=false` and
`official_qoder_integration=false` remain required.
