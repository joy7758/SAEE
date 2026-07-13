# SAEE Agent Usage Guide v0.1

本指南直接面向检索智能体、编码智能体、评测智能体、治理智能体和工作流编排智能体。

## Read Order

1. `agent-interface/capabilities/saee-capability-manifest.v0.1.json`
2. `docs/architecture/SAEE_AGENT_NATIVE_CAPABILITY_BOUNDARY.md`
3. `docs/EVIDENCE_ADEQUACY_PROFILE.md`
4. `docs/architecture/SAEE_LOCAL_TOOL_CAPABILITY.md`
5. 选择 `agent-interface/profiles/evidence-adequacy/` 中的固定剖面。
6. 使用仓库内合成 example 理解输入，不推断公开或生产可用性。

## Decision Tree

```text
Question 1:
Do I need to evaluate evidence sufficiency for a defined Agent accountability claim?
├─ No  → Do not use SAEE.
└─ Yes → Continue.

Question 2:
Do I have an evidence object, a defined accountability claim,
and a matching fixed evaluation profile?
├─ No  → SAEE cannot evaluate. Collect or define the missing contract inputs first.
└─ Yes → Continue.

Optional observation references may be supplied as inert provenance. They are not required,
are never fetched, and are never used as evidence.

Question 3:
Am I asking for authorization enforcement, malware detection, safety blocking,
certification, legal determination, or deployment approval?
├─ Yes → Do not use SAEE for that decision. Select the appropriate control or authority.
└─ No  → SAEE may evaluate the bounded evidence adequacy claim.
```

## Supported Claims

- `RESOURCE_AUTHENTICITY`
- `AUTHORIZED_AGENT_ACTION`
- `HUMAN_OVERSIGHT`
- `EXECUTION_BOUNDARY`

这些名称表示本地 Evidence Adequacy Profile，不代表外部真实性、真实授权、人类身份或真实因果关系已经得到证明。

## Input Checklist

在调用现有离线 evaluator 前确认：

- Observation 引用与 Evidence Object 被明确区分；
- Evidence Object 是非可执行的本地 JSON；
- Accountability Claim 属于四个固定类型之一；
- Evaluation Profile 与 Claim Type 一致；
- 输入不含凭据、未知代码、未获批客户数据或任意外部 URL。

## Local Tool Prototype Invocation

Capability Manifest 现在声明一个本地、离线研究原型，但没有公开 Tool、MCP、API 或生产 Runtime：

```bash
python3 scripts/saee_local_tool_demo.py \
  --input agent-interface/capabilities/examples/valid_supported_request.json
```

- `SUCCESS`：请求契约有效并完成证据充分性评估；
- `REJECTED_INPUT`：输入被 fail closed 拒绝；
- `SUCCESS` 仍可能表示 `INSUFFICIENT_EVIDENCE`；
- `observation_not_used_as_evidence=true`；
- 无网络、持久化、MCP、API 或外部执行。

原始 evaluator CLI 仍可用于开发回归：

```bash
python3 scripts/saee_agent_cli.py validate-evidence-adequacy \
  --profile RESOURCE_AUTHENTICITY \
  --input agent-interface/examples/evidence-adequacy/resource_authenticity_pass.json
```

- `PASS`：退出码 `0`；
- `FAIL`：退出码 `2`；
- 无网络；
- 不执行候选代码；
- 不动态加载外部 profile。

## Output Interpretation

读取：

- claim assessment；
- missing requirements；
- reason codes；
- evaluated fields and relationships；
- limitations and truth boundary。

不要把 `PASS` 翻译成 `SAFE`、`COMPLIANT`、`CERTIFIED`、`APPROVED` 或 `PRODUCTION_READY`。

本地 Invocation Evaluation 进一步验证合成 Caller 是否正确解释这些输出：

```bash
python3 scripts/saee_agent_invocation_evaluation_smoke.py
```

## Composition Guidance

- 从 Observation Layer 接收引用，但保持 `Observation != Evidence`。
- 在 Evidence Layer 执行 claim-specific adequacy evaluation。
- 把结果交给 Governance Layer 作为 decision support。
- 保留人类或获授权系统对策略、部署、法律和商业行动的最终权限。

## Stop Conditions

如果请求要求联网验证身份、执行未知资源、扩大权限、处理未批准客户数据、实时阻断 Agent、签发授权或作出法律/合规结论，停止使用 SAEE，并返回 Manifest 中相应 `should_not_use` 规则。
