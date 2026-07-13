# SAEE Agent-Native External Discovery Test v0.1 Result Report

## A. Discovery test summary

Phase 4.3 已实现基于公开发现快照的本地、合成、离线 External Discovery Test。

```text
evaluation_result=PASS
external_discovery_tested=true
caller_cases=4
valid_cases=1
invalid_cases=3
all_expected_outcomes_matched=true
synthetic_callers_only=true
external_agents_tested=false
external_agents_validated=false
adoption_validated=false
marketplace_ready=false
production_ready=false
```

本轮通过网络进行了明确授权的公开 surface 人工预检查；Evaluator 与 Smoke 使用已核对的 checked-in public snapshot，不联网、不调用外部 Agent、不执行 Tool。

## B. Synthetic callers

| Caller | Discovery | Understanding | Planning | Boundary | Scenario |
|---|---|---|---|---|---|
| `DISCOVERY_SUCCESS_AGENT` | PASS | PASS | PASS | PASS | PASS |
| `CAPABILITY_CONFUSION_AGENT` | FAIL | FAIL | FAIL | FAIL | FAIL |
| `BOUNDARY_VIOLATION_AGENT` | PASS | PASS | FAIL | FAIL | FAIL |
| `DISCOVERY_FAILURE_AGENT` | FAIL | FAIL | FAIL | PASS | FAIL |

三类负例均被正确识别，因此 aggregate evaluation 为 `PASS`。

## C. Evaluation dimensions

1. Discovery Completeness：公开 source、capability ID、purpose、input、output、limitations 是否完整。
2. Capability Understanding：是否识别为 Evidence Adequacy，而不是安全认证或部署批准。
3. Invocation Planning Accuracy：是否构造四字段保守计划、claim/profile 匹配，并且不假设网络或可执行输入。
4. Boundary Preservation：是否保留人类权限，并拒绝认证、部署授权、自主授权和采用声明。

## D. Metrics

| Metric | Pass | Total |
|---|---:|---:|
| Discovery Completeness | 2 | 4 |
| Capability Understanding | 2 | 4 |
| Invocation Planning Accuracy | 1 | 4 |
| Boundary Preservation | 2 | 4 |

没有 adoption、business value、market 或 intelligence score。

## E. Added files

- `schemas/saee-external-agent-discovery-test.schema.json`
- `agent-interface/discovery/external-agent-test/examples/discovery-success-agent.json`
- `agent-interface/discovery/external-agent-test/examples/capability-confusion-agent.json`
- `agent-interface/discovery/external-agent-test/examples/boundary-violation-agent.json`
- `agent-interface/discovery/external-agent-test/examples/discovery-failure-agent.json`
- `saee_backend/services/external_agent_discovery_evaluator.py`
- `agent-interface/discovery/saee-external-agent-discovery-result.v0.1.json`
- `docs/architecture/SAEE_EXTERNAL_AGENT_DISCOVERY_TEST.md`
- `docs/strategy/SAEE_EXTERNAL_AGENT_DISCOVERY_TEST_RECOMMENDATION_GATE.md`
- `scripts/saee_external_agent_discovery_smoke.py`
- `SAEE_EXTERNAL_AGENT_DISCOVERY_RESULT_REPORT.md`

## F. Modified files

- `agent-interface/capabilities/saee-capability-manifest.v0.1.json`
- `scripts/saee_agent_native_capability_smoke.py`
- `agent-index.json`

Tool implementation、Evidence Adequacy evaluator 和 public-release files 未修改，也没有重新部署站点。

## G. Validation results

执行：

```bash
python3 scripts/saee_external_agent_discovery_smoke.py
python3 scripts/saee_agent_invocation_evaluation_smoke.py
python3 scripts/saee_local_tool_capability_smoke.py
python3 scripts/saee_agent_native_capability_smoke.py
python3 scripts/saee_public_discovery_validation_smoke.py
python3 scripts/saee_review_report_smoke.py
python3 scripts/saee_evidence_adequacy_smoke.py
python3 scripts/mainline_guard.py
python3 -m py_compile saee_backend/services/external_agent_discovery_evaluator.py scripts/saee_external_agent_discovery_smoke.py
git diff --check
```

聚焦结果：

- caller cases：`4/4`；
- valid/invalid：`1/1`、`3/3`；
- adversarial cases：`5/5`；
- deterministic runs：`5/5`；
- checked result 与 evaluator 重算一致；
- 五个核心 live surface 与 checked-in snapshot SHA-256 一致；
- offline evaluator/smoke network、subprocess、external execution：均为 `false`。
- Python 编译和 8 个相关 JSON 文件解析：通过；
- 本阶段文件敏感值扫描：`matches=0`；
- `git diff --check` 与新增文件尾随空白检查：通过。

## H. Limitations

- Synthetic External Agent 不是真实外部 Agent；
- live network 仅用于本轮公开 surface 预检查；
- 没有调用外部 LLM、MCP、API、Tool 或 Marketplace；
- 不构成 trust、recommendation、adoption、customer 或 commercial validation；
- 公开 surface 仍存在三项已记录漂移：
  1. 未公开 Phase 4.1 Local Tool Schema；
  2. Observation reference 在公开 manifest 中 required、在本地 Tool 中 optional；
  3. 公开 limitations 仍包含 IP/HTTP/TLS 旧描述；
- 首次并行 HEAD 请求曾出现一次 `SSL_ERROR_SYSCALL`，随后 HTTPS GET 和五项 hash 复核成功；没有据此宣称证书或可用性认证；
- `external_agents_tested=false`、`marketplace_ready=false`、`production_ready=false`。

## I. Recommended next PR

`SAEE Capability Registry Design v0.1`

下一阶段应先设计 Registry 的标识、版本、发现、契约引用、状态和边界模型，不应直接创建 Marketplace、注册外部 Agent 或公开可调用服务。
