# SAEE Public Demo Index

本索引帮助人类和智能体定位四类可复现演示。所有演示均为 `local`、`synthetic`、`non-production`，不得解释为外部 Agent 接入或生产验证。

## Demo 1：Agent Rehearsal

```bash
python3 scripts/saee_agent_rehearsal.py --scenario agent-interface/rehearsal/scenarios/baseline-metadata-inspection.json
```

展示固定合成场景中的受控演练，不执行外部工具或真实业务动作。

## Demo 2：Reliability Assessment

```bash
python3 scripts/saee_evaluate_agent_run.py --scenario agent-interface/rehearsal/scenarios/baseline-metadata-inspection.json
```

输出有边界的本地可靠性结果；结果不是生产批准。

## Demo 3：Evidence Evaluation

```bash
python3 scripts/saee_agent_cli.py validate-evidence-adequacy --profile RESOURCE_AUTHENTICITY --input agent-interface/examples/evidence-adequacy/resource_authenticity_pass.json
```

验证固定 Profile 要求是否满足，不证明真实世界事件一定发生。

## Demo 4：MCP Capability Invocation

```bash
python3 scripts/saee_capability_mcp_adapter_smoke.py
```

验证本地 MCP Adapter 到 Capability Runtime 的映射，不启动公网 MCP 服务。

## 机器索引

| demo_id | capability | canonical_input | validation |
|---|---|---|---|
| `rehearsal.local.synthetic` | controlled rehearsal | `agent-interface/rehearsal/scenarios/baseline-metadata-inspection.json` | `scripts/saee_agent_rehearsal.py` |
| `reliability.local.synthetic` | agent reliability | 同上 | `scripts/saee_evaluate_agent_run.py` |
| `evidence.local.synthetic` | evidence adequacy | `agent-interface/examples/evidence-adequacy/resource_authenticity_pass.json` | `scripts/saee_agent_cli.py` |
| `mcp.local.contract` | MCP adapter | `examples/agent-integrations/mcp-client-example/example_config.json` | `scripts/saee_capability_mcp_adapter_smoke.py` |

