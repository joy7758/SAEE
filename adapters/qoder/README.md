# Qoder + SAEE Adapter

Qoder officially supports project-scoped MCP configuration in `.mcp.json` and
stdio servers launched as local commands. The repository root `.mcp.json` and
`qoder-project.mcp.json` expose the same server:

```text
python3 scripts/saee_agent_readiness_mcp_stdio.py
```

The server exposes exactly:

- `saee.evaluate_agent_run`
- `saee.evaluate_evidence`

Local verification:

```bash
python3 scripts/saee_qoder_adapter_smoke.py
```

If Qoder CLI is installed, the human verification sequence is:

```bash
qodercli mcp list
# Start a new Agent-mode session, or run /mcp reload in an existing session.
```

The current host does not have Qoder Desktop or `qodercli`. The official CLI
installer has been inspected but not executed because it downloads and runs a
vendor binary and may update the user's PATH or shell configuration. Read the
Agent-readable preflight before authorizing installation or login:

```text
agent-interface/ecosystem/saee-qoder-cli-installation-preflight.v1.json
```

After explicit owner authorization, validation must use the checked-in
`.mcp.json`, interactive browser login, fixture-only inputs, `dont_ask`
fail-closed permissions, only the `saee-readiness` MCP server, and no Bash,
file-write, web, subagent, deployment, or permission-expansion action.

Official references:

- <https://docs.qoder.com/en/cli/mcp-servers>
- <https://docs.qoder.com/en/cli/quick-start>
- <https://docs.qoder.com/en/cli/permissions>
- <https://docs.qoder.com/user-guide/chat/model-context-protocol>

`qoder_configuration_ready=true` means the configuration follows the documented
shape and the same JSON-RPC flow passed a local client test. It does not mean a
Qoder process invoked SAEE, Alibaba Cloud approved a plugin, or official
integration exists.
