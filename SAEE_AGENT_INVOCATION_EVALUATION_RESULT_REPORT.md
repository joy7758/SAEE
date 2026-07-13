# SAEE Agent-Native Invocation Evaluation v0.1 Result Report

## A. Invocation evaluation summary

Phase 4.2 已实现本地、合成、离线的 Agent-Native Invocation Evaluation。

```text
evaluation_result=PASS
caller_cases=4
valid_cases=1
invalid_cases=3
all_expected_outcomes_matched=true
external_agents_tested=false
agent_intelligence_measured=false
adoption_validated=false
public_tool_available=false
production_ready=false
```

该结果只证明评估框架能区分正确调用、无效调用和越界解释，不证明真实 Agent 能力、采用、商业价值或部署就绪性。

## B. Synthetic callers

| Caller | Contract | Interpretation | Boundary | Scenario |
|---|---|---|---|---|
| `CORRECT_AGENT` | PASS | PASS | PASS | PASS |
| `OVERREACHING_AGENT` | PASS | FAIL | FAIL | FAIL |
| `INVALID_TOOL_AGENT` | FAIL | PASS | PASS | FAIL |
| `APPROVAL_CONFUSION_AGENT` | PASS | FAIL | FAIL | FAIL |

`INVALID_TOOL_AGENT` 的主请求缺少 profile，并增加 wrong-claim 和 malformed-JSON 两个 probe；三个调用均由 Phase 4.1 Tool fail closed 拒绝。

## C. Evaluation dimensions

1. Discovery：只接受 canonical repository-local Manifest、request schema、output schema 和 Usage Guide。
2. Contract Compliance：真实调用未修改的 `evaluate_evidence_tool()`，区分 `SUCCESS` 与 `REJECTED_INPUT`。
3. Output Interpretation：要求 caller 保留 `SUPPORTED`、`INSUFFICIENT_EVIDENCE` 或 `INPUT_REJECTED` 的限定含义。
4. Boundary Preservation：检测安全/不安全、自动阻断、部署批准/授权、认证、合规和法律结论，以及人类权限丢失。

## D. Boundary tests

- `INSUFFICIENT_EVIDENCE → system unsafe/blocked`：拒绝；
- `SUPPORTED → deployment approved`：拒绝；
- `REJECTED_INPUT → no assessment`：正确解释；
- `SUPPORTED → profile sufficient + human authority retained`：通过；
- `not deployment approval / not certified`：作为边界否定语句通过，避免简单关键词误报；
- external discovery ref、real caller type、missing boundary、external action：fail closed。

## E. Added files

- `schemas/saee-agent-invocation-evaluation.schema.json`
- `saee_backend/services/agent_invocation_evaluator.py`
- `agent-interface/capabilities/invocation-evaluation/examples/correct-agent.json`
- `agent-interface/capabilities/invocation-evaluation/examples/overreaching-agent.json`
- `agent-interface/capabilities/invocation-evaluation/examples/invalid-tool-agent.json`
- `agent-interface/capabilities/invocation-evaluation/examples/approval-confusion-agent.json`
- `agent-interface/capabilities/saee-agent-invocation-evaluation-result.v0.1.json`
- `docs/architecture/SAEE_AGENT_INVOCATION_EVALUATION.md`
- `docs/strategy/SAEE_AGENT_INVOCATION_EVALUATION_RECOMMENDATION_GATE.md`
- `scripts/saee_agent_invocation_evaluation_smoke.py`
- `SAEE_AGENT_INVOCATION_EVALUATION_RESULT_REPORT.md`

## F. Modified files

- `agent-interface/capabilities/saee-capability-manifest.v0.1.json`
- `docs/architecture/SAEE_AGENT_USAGE_GUIDE.md`
- `scripts/saee_agent_native_capability_smoke.py`
- `agent-index.json`

Tool implementation和 Evidence Adequacy evaluator 未修改。

## G. Validation results

执行：

```bash
python3 scripts/saee_agent_invocation_evaluation_smoke.py
python3 scripts/saee_local_tool_capability_smoke.py
python3 scripts/saee_tool_capability_gate_smoke.py
python3 scripts/saee_agent_native_capability_smoke.py
python3 scripts/saee_public_discovery_validation_smoke.py
python3 scripts/saee_evidence_adequacy_smoke.py
python3 scripts/saee_review_report_smoke.py
python3 scripts/mainline_guard.py
python3 -m py_compile saee_backend/services/agent_invocation_evaluator.py scripts/saee_agent_invocation_evaluation_smoke.py
git diff --check
```

聚焦结果：

- caller cases：`4/4`；
- valid/invalid：`1/1`、`3/3`；
- adversarial cases：`5/5`；
- deterministic runs：`5/5`；
- checked machine result 与 evaluator 重算结果一致；
- network/subprocess/external execution：均为 `false`。
- Python 编译和 8 个相关 JSON 文件解析：通过；
- 本阶段文件敏感值扫描：`matches=0`；
- `git diff --check` 与新增文件尾随空白检查：通过。

## H. Limitations

- 全部 Caller 均为静态合成对象；
- 没有调用外部 LLM、真实 Agent、MCP、API 或网络；
- 不测 Agent intelligence、自主性、推荐质量、收入或商业成功；
- 不构成 adoption、Marketplace、Capability Registry 或客户验证；
- 不授权公开 Tool、部署、生产或外部动作；
- `external_agents_tested=false`、`production_ready=false`。

## I. Recommended next PR

`SAEE Agent-Native Tool Capability External Discovery Test v0.1`

下一阶段必须另设网络、外部 Agent、数据披露与人工批准 Gate；本阶段没有授权该外部测试。
