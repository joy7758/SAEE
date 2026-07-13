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

Official references:

- <https://docs.qoder.com/en/cli/mcp-servers>
- <https://docs.qoder.com/user-guide/chat/model-context-protocol>

`qoder_configuration_ready=true` means the configuration follows the documented
shape and the same JSON-RPC flow passed a local client test. It does not mean a
Qoder process invoked SAEE, Alibaba Cloud approved a plugin, or official
integration exists.
