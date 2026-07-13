# SAEE Local Tool Capability Prototype v0.1 Result Report

## A. Tool prototype summary

Phase 4.1 已实现首个本地、离线、确定性、可组合 SAEE Tool Capability 原型。

```text
local_tool_prototype_implemented=true
public_tool_available=false
external_agent_invocation_validated=false
mcp_available=false
api_available=false
authorization_performed=false
deployment_authorized=false
production_ready=false
```

原型只评估证据充分性，不控制 Agent、不阻断 Runtime、不执行授权、不批准部署、不认证安全/合规，也不形成法律结论。

## B. Contract design

请求契约：`agent-interface/capabilities/saee-evaluate-evidence-tool.v0.1.schema.json`

必需输入：

- `evidence_object`
- `accountability_claim`
- `evaluation_profile`

`observation_references` 是可选 inert provenance，只计数、不拉取、不验证外部来源、不转换为 evidence。

输出契约：`agent-interface/capabilities/saee-evaluate-evidence-output.v0.1.schema.json`

允许：

- `SUPPORTED`
- `INSUFFICIENT_EVIDENCE`
- `UNKNOWN`
- `SUCCESS`
- `REJECTED_INPUT`

不允许：`APPROVED`、`CERTIFIED`、`SAFE`、`COMPLIANT`。

## C. Input guard implementation

`saee_backend/services/local_tool_guard.py` 实现：

- 解析前 1 MiB 限制；
- duplicate JSON key 拒绝；
- invalid JSON/UTF-8 拒绝；
- 32 层 nesting 限制；
- 50,000 node 上限；
- 非 JSON 类型、NaN/Infinity 拒绝；
- unknown claim/profile、claim/profile mismatch 拒绝；
- missing/empty evidence object 和 undeclared root field 拒绝；
- fail closed，不猜测、不修补输入。

## D. Evaluator reuse confirmation

`saee_backend/services/local_evidence_tool.py` 直接调用既有：

```python
evaluate_evidence_adequacy(claim_type, evidence_object)
```

没有复制 evidence profile、field requirement 或 relationship evaluation 规则。Smoke 使用 evaluator probe 验证每次 Tool invocation 只调用 canonical evaluator 一次，并对比 direct evaluator 的 reason codes 和 missing requirements。

## E. Output boundary

输出不反射 evidence values 或 observation reference values，只返回：

- bounded assessment/status；
- missing requirements；
- failed relationship IDs；
- evaluated field paths；
- stable reason codes；
- fixed limitations；
- mandatory boundary statement；
- Observation reference count；
- `observation_not_used_as_evidence=true`。

## F. Added files

- `agent-interface/capabilities/saee-evaluate-evidence-tool.v0.1.schema.json`
- `agent-interface/capabilities/saee-evaluate-evidence-output.v0.1.schema.json`
- `saee_backend/services/local_tool_guard.py`
- `saee_backend/services/local_evidence_tool.py`
- `scripts/saee_local_tool_demo.py`
- `scripts/saee_local_tool_capability_smoke.py`
- `agent-interface/capabilities/examples/valid_supported_request.json`
- `agent-interface/capabilities/examples/valid_insufficient_request.json`
- `agent-interface/capabilities/examples/invalid_unknown_claim.json`
- `agent-interface/capabilities/examples/invalid_oversized_request.json`
- `agent-interface/capabilities/examples/invalid_missing_profile.json`
- `docs/architecture/SAEE_LOCAL_TOOL_CAPABILITY.md`
- `docs/strategy/SAEE_LOCAL_TOOL_CAPABILITY_RECOMMENDATION_GATE.md`
- `SAEE_LOCAL_TOOL_CAPABILITY_RESULT_REPORT.md`

## G. Modified files

- `agent-interface/capabilities/saee-capability-manifest.v0.1.json`
- `agent-index.json`
- `scripts/saee_agent_native_capability_smoke.py`
- `agent-interface/capabilities/saee-tool-capability-gate.v0.1.json`
- `docs/architecture/SAEE_AGENT_NATIVE_TOOL_CAPABILITY_GATE_REVIEW.md`
- `docs/architecture/SAEE_AGENT_DISCOVERY_VALIDATION.md`
- `scripts/saee_tool_capability_gate_smoke.py`

Phase 4.0 Gate 被显式标为实施前历史快照；当前本地原型状态由 Capability Manifest 定义，避免 `implementation_authorized=false` 与 Phase 4.1 实现状态被误读为同一时间面的冲突。

## H. Validation results

执行：

```bash
python3 scripts/saee_local_tool_capability_smoke.py
python3 scripts/saee_local_tool_demo.py --input agent-interface/capabilities/examples/valid_supported_request.json
python3 scripts/saee_local_tool_demo.py --input agent-interface/capabilities/examples/invalid_unknown_claim.json
python3 scripts/saee_tool_capability_gate_smoke.py
python3 scripts/saee_agent_native_capability_smoke.py
python3 scripts/saee_evidence_adequacy_smoke.py
python3 scripts/saee_review_report_smoke.py
python3 scripts/saee_phase2b_completion_review_smoke.py
python3 scripts/saee_public_discovery_validation_smoke.py
python3 scripts/mainline_guard.py
python3 -m py_compile saee_backend/services/local_tool_guard.py saee_backend/services/local_evidence_tool.py scripts/saee_local_tool_demo.py scripts/saee_local_tool_capability_smoke.py
git diff --check
```

结果：

- Local Tool：`PASS`，有效案例 `2/2`，无效/对抗案例 `13/13`，确定性复跑 `5/5`；
- canonical evaluator reuse：`true`；
- supported CLI：exit `0`，`SUPPORTED/SUFFICIENT`；
- rejected CLI：exit `2`，`TOOL_CLAIM_UNKNOWN`；
- Phase 4.0 Gate：`PASS`，历史快照与当前 Manifest 分层；
- Capability Manifest：`PASS`，本地原型已实现、公开 Tool 仍不可用；
- Evidence Adequacy、Review Report、Phase 2B、Public Discovery、Mainline Guard：`PASS`；
- network/subprocess/persistence/external execution：均为 `false`。
- Python 编译和 10 个相关 JSON 文件解析：通过；
- 本阶段文件敏感值扫描：`matches=0`；
- `git diff --check` 与新增文件尾随空白检查：通过。

Evidence Adequacy 回归仍产生既有 `jsonschema.RefResolver` 弃用警告，不影响退出码或测试结果，本任务未修改该无关依赖路径。

## I. Limitations

- 仅限本地、合成、离线研究原型；
- 没有 MCP、API、网络服务、数据库、持久化或框架集成；
- 没有外部 Agent invocation evaluation；
- 没有独立验证 evidence authenticity、identity 或 authorization；
- `invalid_oversized_request.json` 是合成生成 recipe，Smoke 在内存中生成超过 1 MiB 的真实测试请求，避免提交无意义的大文件；
- Tool assessment 不能被解释为授权、部署批准、安全/合规认证或法律结论；
- `production_ready=false`、`external_agent_validation_completed=false`。

## J. Recommended next PR

`SAEE Agent-Native Invocation Evaluation v0.1`

下一阶段应评估不同 agent-like callers 是否能正确发现契约、构造请求、解释输出和保持边界；不要直接进入 MCP/API。
