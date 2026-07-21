# SAEE 智能体上线前飞行检查：5 分钟 Demo

## 一句话

当一个自主编码智能体准备修改并发布软件时，SAEE 帮它在行动前检查演练记录是否可靠、责任声明是否有足够证据，并给出有边界的下一步上下文。

```text
Agent Task
  -> discover SAEE
  -> controlled rehearsal context
  -> evaluate_rehearsal_run
  -> evaluate_evidence
  -> bounded decision context
  -> Agent chooses REPLAN
```

## 五分钟路径

1. 用 60 秒阅读 [`scenario/coding-agent-preflight.json`](scenario/coding-agent-preflight.json)，了解任务与风险。
2. 用 90 秒阅读 [`agent-flow.md`](agent-flow.md)，理解 Agent 为什么选择 SAEE。
3. 用 60 秒阅读 [`mcp-demo.md`](mcp-demo.md)，理解本地 MCP 调用链。
4. 用 60 秒查看 [`result-example.json`](result-example.json)，看到 `REPLAN` 和缺失证据。
5. 用 30 秒阅读 [`interpretation.md`](interpretation.md) 与 [`limitations.md`](limitations.md)，避免过度解释。

## 价值

普通 trace 能说明系统观察到了什么。本 Demo 展示 SAEE 如何把运行记录、证据充分性和下一步行为调整放入同一个有边界的 Agent 工作流。

## 本地验证

```bash
python3 scripts/saee_ecosystem_demo_smoke.py
```

本包不连接外部 Agent，不启动公共 MCP Server，不执行真实软件发布，也不证明外部兼容、市场采用或生产就绪。

未来验证候选类别入口：`first_validation_candidate_reference=agent-interface/ecosystem/saee-first-validation-candidate-matrix.v0.1.json`。该引用不表示已选择或联系候选对象。

```text
ecosystem_demo=true
local_demo_only=true
external_agent=false
external_execution=false
customer_validated=false
marketplace_listed=false
production_ready=false
```
