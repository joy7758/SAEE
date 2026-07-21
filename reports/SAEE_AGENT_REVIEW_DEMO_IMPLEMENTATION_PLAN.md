# SAEE Agent Review Demo Implementation Plan

```text
report_id=SAEE_AGENT_REVIEW_DEMO_IMPLEMENTATION_PLAN
requested_phase=Phase_6.1-B-A
report_type=IMPLEMENTATION_PLAN_ONLY_NO_DEMO_IMPLEMENTATION
current_effective_authority=SAEE_Development_Constitution_v1.1
program_mainline=controlled_SAEE_Agent_Evidence_integration
product_projection=SAEE_Evaluation
target_demo=Coding_Agent_Review
plan_date=2026-07-15
```

## Executive Decision

可以用现有 canonical two-tool MCP 实现一个三分钟、完全本地、合成且不新增 Capability
的 Agent Review Demo。最小实现不开发 Agent Runtime、Evidence Builder、MCP adapter 或
Evaluation engine；它只增加：

- 三个 current-contract case 的 request/expected artifacts；
- 一份 Agent-readable README；
- 一个只读 local stdio Demo client；
- 一个 deterministic/negative smoke。

```text
PRIMARY_OPERATION=saee.evaluate_agent_run
SUPPORTING_OPERATION=saee.evaluate_evidence
CANONICAL_MCP=saee.agent_readiness_mcp_stdio
MCP_ADAPTER_DISPOSITION=REUSE_UNCHANGED
EVALUATION_SERVICE_DISPOSITION=REUSE_UNCHANGED
NEW_CAPABILITY_REQUIRED=false
NEW_SCHEMA_REQUIRED=false
NEW_PROTOCOL_REQUIRED=false
```

附件中的案例必须按已冻结 MVP specification 修正：high-impact run 要求四类 Evidence。

| Case | Correct current-contract input | Expected result |
|---|---|---|
| A — Evidence sufficient | `TEST_RESULT`, `ROLLBACK_PLAN`, `PERMISSION_BOUNDARY`, `HUMAN_APPROVAL` 全部 present | `CONTINUE`, score `100` |
| B — rollback missing | 仅 `ROLLBACK_PLAN` missing；其余三类 present | `HUMAN_REVIEW_REQUIRED`, score `75` |
| C — input insufficient | required `trace` absent | MCP fail-closed error；no recommendation |

Case A 若缺 `HUMAN_APPROVAL`，只能得到 `75 / HUMAN_REVIEW_REQUIRED`，不能为了故事效果
写成 `CONTINUE`。Case B 若同时缺 rollback 和 approval，则实际为 `50 / REPLAN`。

本阶段只创建本计划报告。Demo、files、client、smoke、branch、worktree、commit 和外部
Agent integration 均未创建或授权。

## 0. Authority and Mainline Boundary

```text
MAINLINE_DRIFT_DETECTED
```

把 `痛点 → Demo → 真实 Agent → 生态 → 商业化` 路线宣布为当前全局主线，会覆盖 v1.1
冻结的 SAEE–Agent Evidence controlled integration mainline。Phase 6.1-B-A 只有在以下纠偏
后有效：

```text
MAINLINE_CORRECTION=NON_AUTHORIZING_LOCAL_DEMO_PLAN_SUPPORTING_SAEE_EVALUATION_AND_CONTROLLED_INTEGRATION
DEMO_WORKSTREAM_ROLE=BOUNDED_SECONDARY_PRODUCT_VALIDATION
PROGRAM_MAINLINE_CHANGED=false
CURRENT_AUTHORITY_CHANGED=false
PHASE_SEQUENCE_CHANGED=false
```

当前 Project Memory 仍保持 Phase 0.5 stabilization，authority baseline 未形成，
`phase_0_5_7a_authorized=false`。Phase 6.1-A 也明确：

```text
PHASE_6_1_B_AUTHORIZED=false
EXTERNAL_DEVELOPER_TEST_AUTHORIZED=false
F2B_EXECUTION_AUTHORIZED=false
```

本计划不改变这些 gate。它只把未来本地 Demo 的 allowlist、contract 和停止点设计清楚。

## 1. Demo Goal

### 1.1 What the Demo proves

Demo 只证明：

> 一个调用者可以在受控 Coding Agent run 已产生 declared trace 和 Evidence 后、进入重大
> 下一步之前，通过 canonical local MCP 插入一次 SAEE Review，并根据明确缺口改变下一步
> 计划。

Demo 必须让观察者在三分钟内看到三个差异：

1. complete declared Evidence → `CONTINUE` only to a separately controlled next step；
2. one material Evidence gap → `HUMAN_REVIEW_REQUIRED`；
3. missing required input → fail closed and do not fabricate a recommendation。

### 1.2 What the Demo does not prove

It does not prove:

- a real Coding Agent executed code changes or tests;
- the trace/Evidence references are authentic;
- code is correct, secure, reviewed or deployable;
- an external framework is integrated;
- a customer needs, adopts or will pay for SAEE;
- SAEE is production-ready or authorized to act.

### 1.3 Before/after product narrative

Safe narrative:

```text
Without the SAEE review step:
the demo has a declared run and scattered Evidence, but no single bounded coverage/gap result.

With the SAEE review step:
the caller receives required/present/missing Evidence, risks, limitations and a bounded
recommendation, then chooses a separately governed next step.
```

禁止说“没有 SAEE 就不知道真实风险”或“SAEE 证明 Agent 安全”。Current evaluator only
interprets declared Evidence coverage.

## 2. User Story and Scenario

### 2.1 User story

> 作为使用 Coding Agent 的开发者，我希望在一个受控 coding run 完成后、进入 merge、
> deploy、database change 或 release review 前，检查它声明的测试、回滚、权限和审批
> Evidence 是否齐全，以便决定继续受控验证、补资料、停止或交给独立人类 authority。

### 2.2 Demo scenario

```text
scenario_name=Coding Agent Review
task_summary=modify_payment_module_add_interface
execution_mode=STATIC_SANITIZED_DECLARED_FIXTURE
real_repository_modified=false
real_tests_executed=false
real_payment_system_connected=false
customer_data_included=false
external_execution=false
```

“支付模块”只是合成业务语境。Demo 不打开真实仓库、不修改 payment code、不调用 payment
API、不连接数据库、不读取环境变量或 secrets。

### 2.3 Timing boundary

```text
bounded coding run complete
        ↓
declared trace and Evidence assembled
        ↓
SAEE Review
        ↓
recommendation context
        ↓
caller records next-step decision only
```

This is review-after-run / before-next-consequential-step, not future-action prediction.

## 3. Demo Architecture

### 3.1 Minimal architecture

```text
Static sanitized Coding Agent fixture
        ↓
current-schema Trace + Evidence objects
        ↓
thin local Demo client
        ↓
canonical stdio MCP
scripts/saee_agent_readiness_mcp_stdio.py
        ↓
existing qianfan_readiness_mcp_adapter
        ↓
existing evaluate_agent_run service
        ↓
current-schema structuredContent
        ↓
Demo client prints recommendation, gaps, risks, limitations and truth boundary
```

### 3.2 Component responsibilities

| Component | Future Phase 6.1-B role | Change disposition |
|---|---|---|
| static cases | represent declared Agent execution/Trace/Evidence | add new synthetic artifacts only |
| Demo client | MCP initialize → tools/list → tools/call → bounded rendering | add one thin standard-library client |
| canonical MCP stdio wrapper | process transport and two-tool discovery | reuse unchanged |
| Qianfan readiness MCP adapter | schema validation and delegation | reuse unchanged |
| readiness service | existing coverage algorithm | reuse unchanged |
| schemas | request/response contract | freeze unchanged |
| capability manifest | capability and route truth | freeze unchanged |
| caller next-step behavior | display a recommended plan only | no merge/deploy/action execution |

### 3.3 Evidence Builder boundary

The diagram's “Evidence Builder” is not implemented as a service or capability. In the local Demo it
means only checked-in, sanitized Evidence objects inside the three fixtures.

```text
EVIDENCE_BUILDER_IMPLEMENTED=false
LIVE_TRACE_COLLECTION=false
CI_RESULT_COLLECTION=false
FILESYSTEM_SCAN=false
TELEMETRY_INGESTION=false
```

Real trace/Evidence acquisition belongs to a separately authorized future integration, not Phase
6.1-B.

## 4. Existing Capability and Asset Mapping

### 4.1 Canonical reuse

| Need | Canonical asset | Status | Disposition |
|---|---|---|---|
| declared run Evaluation | `saee.evaluate_agent_run` | `implemented / active` | `REUSE` |
| optional closed Evidence diagnostic | `saee.evaluate_evidence` | `implemented / active` | `REUSE_OPTIONAL_NOT_REQUIRED_IN_MAIN_FLOW` |
| local MCP entry | `scripts/saee_agent_readiness_mcp_stdio.py` | canonical public-contract local alpha | `REUSE_UNCHANGED` |
| adapter | `saee_backend/services/qianfan_readiness_mcp_adapter.py` | shared canonical/compatibility implementation | `REUSE_UNCHANGED` |
| evaluator | `saee_backend/services/baidu_agent_readiness_service.py` | deterministic local implementation | `REUSE_UNCHANGED` |
| contract | Qianfan request/response/Evidence item schemas | current JSON Schema 2020-12 | `REUSE_UNCHANGED` |
| process-level pattern | `scripts/saee_qoder_adapter_smoke.py` | verified canonical stdio handshake/call | `REUSE_PATTERN_NOT_PRODUCT_CLAIM` |
| coding fixture precedent | `examples/qoder-saee-readiness-demo/` | local synthetic `REPLAN` example | `REUSE_TERMS_AND_BOUNDARIES` |

### 4.2 Duplicate/legacy disposition

| Existing asset | Why it is not the primary path | Disposition |
|---|---|---|
| `scripts/saee_local_mcp_client_demo.py` | uses older `local_mcp_server`, not canonical two-tool readiness MCP | `DO_NOT_REUSE_FOR_THIS_DEMO` |
| `scripts/saee_local_tool_demo.py` | evaluates older local Evidence tool only | `DO_NOT_REUSE_FOR_RUN_REVIEW` |
| `examples/agent-integrations/mcp-client-example/` | points to internal unnamespaced three-tool MCP | `HISTORICAL_INTERNAL_EXAMPLE` |
| `examples/agent-integrations/framework-agent-example/generic_agent_adapter.py` | interprets a legacy envelope/assessment shape, not current readiness response | `DO_NOT_ROUTE_CURRENT_DEMO_THROUGH_IT` |
| `examples/ecosystem-demo-v1/` | historical demo semantics and unnamespaced capability references | `PRESERVE_HISTORY_NO_REWRITE` |

Creating another server, evaluator, capability registry, Evidence type or framework adapter is
forbidden. A small Demo client is a consumer example, not a new MCP adapter or Capability.

```text
CANONICAL_CAPABILITY_SOURCE=capability-package/manifest.json#canonical_inventory
SECOND_CAPABILITY_SOURCE_CREATED=false
SECOND_CANONICAL_MCP_CREATED=false
EVALUATION_ENGINE_REBUILD=DO_NOT_BUILD
```

## 5. Three Demo Cases

### 5.1 Shared current-schema rules

Every valid case uses:

```text
agent_id prefix=agent:
request_id prefix=request:
trace.events minItems=1
event fields=event_id,event_type,summary,external_effect,high_impact
evidence object fields=evidence_id,evidence_type,present,source_ref
customer_data_included=false
```

At least one event is `high_impact=true` so the current evaluator requires all four Evidence types.

### 5.2 Case A — Evidence sufficient

Input state:

```text
TEST_RESULT.present=true
ROLLBACK_PLAN.present=true
PERMISSION_BOUNDARY.present=true
HUMAN_APPROVAL.present=true
```

Expected output:

```text
readiness=continue
score=100
present_evidence=TEST_RESULT;ROLLBACK_PLAN;PERMISSION_BOUNDARY;HUMAN_APPROVAL
missing_evidence=[]
recommendation=CONTINUE
deployment_authorized=false
production_ready=false
```

Interpretation: continue to the next separately controlled review step. Do not merge or deploy.

### 5.3 Case B — Evidence missing

Input state:

```text
TEST_RESULT.present=true
ROLLBACK_PLAN.present=false
PERMISSION_BOUNDARY.present=true
HUMAN_APPROVAL.present=true
```

Expected output:

```text
readiness=conditional
score=75
missing_evidence=ROLLBACK_PLAN
risks=missing_recovery_plan
recommendation=HUMAN_REVIEW_REQUIRED
deployment_authorized=false
```

Interpretation: identify one gap and route to independent human review. This does not mean review or
approval has occurred.

### 5.4 Case C — Input insufficient

Input deliberately omits `trace` and carries no usable Evidence.

Expected MCP result:

```text
content_text=READINESS_MCP_ARGUMENTS_INVALID
isError=true
structuredContent_absent=true
recommendation_absent=true
agent_display=INPUT_INSUFFICIENT__REQUEST_DECLARED_TRACE_AND_EVIDENCE
```

The final `agent_display` label is Demo presentation text, not a service enum, schema field or new
reason code.

### 5.5 Contrast integrity

The Demo contrast is Evidence coverage, not “Agent good/bad”:

| Case | What changes | What remains unknown |
|---|---|---|
| A | declared required set is complete | Evidence authenticity, code safety, approval validity |
| B | rollback Evidence is declared missing | whether a real rollback plan exists elsewhere |
| C | current contract input is insufficient | everything about the alleged run |

## 6. Future Phase 6.1-B Implementation Scope

No path in this section is created by Phase 6.1-B-A.

### 6.1 Exact proposed allowlist

```text
examples/saee-agent-review-demo/README.md
examples/saee-agent-review-demo/case-a.request.json
examples/saee-agent-review-demo/case-a.expected.json
examples/saee-agent-review-demo/case-b.request.json
examples/saee-agent-review-demo/case-b.expected.json
examples/saee-agent-review-demo/case-c.invalid-request.json
examples/saee-agent-review-demo/case-c.expected-error.json
scripts/saee_agent_review_demo.py
scripts/saee_agent_review_demo_smoke.py
```

All nine proposed paths are currently absent. Human review may reduce the list; expansion requires a
new allowlist decision.

### 6.2 File responsibilities

| Proposed file | Purpose | Constraints |
|---|---|---|
| Demo `README.md` | three-minute flow, run commands, case meanings, non-claims | no platform/official integration/customer claims |
| A/B request JSON | current-schema valid high-impact run inputs | synthetic, `demo://`, no customer data |
| A/B expected JSON | full current response-schema outputs | generated from unchanged service then reviewed; no hand-edited enum drift |
| C invalid request | explicit missing-trace negative fixture | filename and README must say invalid by design |
| C expected error | MCP error projection, no recommendation | not a new product response schema |
| `saee_agent_review_demo.py` | thin local JSON-RPC stdio client and stable human/Agent-readable output | standard library only; no file writes/network/secrets/provider SDK |
| `saee_agent_review_demo_smoke.py` | contract, deterministic, negative and boundary acceptance | no external Agent/process beyond repository-owned local MCP |

### 6.3 Demo client behavior

Proposed CLI:

```text
python3 scripts/saee_agent_review_demo.py --case a
python3 scripts/saee_agent_review_demo.py --case b
python3 scripts/saee_agent_review_demo.py --case c
python3 scripts/saee_agent_review_demo.py --case all
```

The client must:

1. read only the allowlisted repository fixture;
2. start only `python3 scripts/saee_agent_readiness_mcp_stdio.py`;
3. perform MCP initialize, initialized notification, `tools/list` and exact `tools/call`;
4. require exactly `saee.evaluate_agent_run` and `saee.evaluate_evidence`;
5. render required/present/missing Evidence, risks, recommendation, limitations and truth boundary;
6. for Case C, treat the expected invalid-arguments response as a successful Demo assertion;
7. exit `0` only when the selected case exactly matches its expected artifact;
8. exit non-zero on contract drift, unexpected tool, unexpected recommendation or subprocess error;
9. terminate the local child cleanly without leaving processes or files;
10. never execute a Coding Agent, repository modification, test suite, merge, deploy or external call.

The Demo client is a local consumer. It must not import or call the Evaluation service directly,
because the Demo is intended to prove insertion through the canonical MCP boundary.

### 6.4 Frozen existing paths

Future Phase 6.1-B must not modify:

```text
capability-package/manifest.json
agent-index.json
llms.txt
README.md
.mcp.json
agent-interface/qianfan/*.schema.v0.1.json
saee_backend/services/baidu_agent_readiness_service.py
saee_backend/services/qianfan_readiness_mcp_adapter.py
scripts/saee_agent_readiness_mcp_stdio.py
scripts/saee_qoder_adapter_smoke.py
examples/qoder-saee-readiness-demo/*
governance/
docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md
```

Any required modification to a frozen path stops the batch and returns to human review.

## 7. Non-Goals

Phase 6.1-B Demo implementation must not include:

- a new Capability, protocol, schema, Evidence type or response enum;
- a new/modified MCP server, adapter, route, transport or tool description;
- Agent Runtime, autonomous control, action execution or automatic approval;
- Evidence collection, repository analysis, actual code modification or test execution;
- code quality, security, trust, reliability or probability scoring;
- replacement of CI/CD, code review, IAM, policy or Security Scanner;
- Passport, Trust Score, certificate, SECO or identity/delegation work;
- F2B description update or historical surface rewrite;
- external Agent, framework, cloud, customer or Design Partner connection;
- product launch, marketplace action, price, deployment or production claim.

## 8. Validation Plan

### 8.1 New Demo acceptance

| Check | Required result |
|---|---|
| proposed path allowlist | exactly `9/9`, no existing frozen path changed |
| MCP discovery | exactly two canonical namespaced tools |
| Case A | `CONTINUE`, score `100`, no missing Evidence |
| Case B | `HUMAN_REVIEW_REQUIRED`, score `75`, only rollback missing |
| Case C | `READINESS_MCP_ARGUMENTS_INVALID`, `isError=true`, no recommendation |
| determinism | A/B/C each `10/10` identical semantic results |
| schema | A/B request and expected outputs validate current schemas; C fails request schema as designed |
| truth boundary | deployment/security/customer/production flags all false |
| side effects | network `0`, external execution `0`, repository writes `0`, surviving child processes `0` |
| Demo duration | all three cases runnable and interpretable within three minutes locally |

### 8.2 Required regression suite

```text
python3 scripts/saee_agent_review_demo_smoke.py
python3 scripts/saee_qianfan_readiness_mcp_smoke.py
python3 scripts/saee_qoder_adapter_smoke.py
python3 scripts/saee_canonical_capability_inventory_smoke.py
python3 scripts/saee_capability_progress_ledger_smoke.py
python3 scripts/saee_project_memory_check.py
python3 scripts/saee_governance_registry_check.py
python3 scripts/saee_development_constitution_smoke.py
git diff --check
```

### 8.3 Immutable pre/post checks

The execution packet must freeze and recheck SHA-256 for manifest, four current request/response
schemas, service, MCP adapter, stdio wrapper, `.mcp.json`, Qoder smoke and existing Qoder fixtures.
It must also record worktree status and tracked patch hashes before/after. A matching smoke with a
changed frozen hash fails the batch.

## 9. Future Agent Adapter Path

Phase 6.1-C may test a real external Agent only through a separate authorization. The preferred
composition boundary is dependency injection of the canonical local MCP call:

```text
external Agent prepares current-schema declared run
        ↓
authorized local MCP client invocation
        ↓
current structuredContent
        ↓
Agent maps CONTINUE / HUMAN_REVIEW_REQUIRED / REPLAN / STOP into its own plan
        ↓
separate authority controls every consequential action
```

Guardrails:

- do not reuse `generic_agent_adapter.py` as-is; its legacy response interpretation does not match
  current `recommendation/missing_evidence/truth_boundary` fields;
- do not use the internal unnamespaced three-tool MCP as the public contract;
- no Codex, Claude Code, OpenAI, Anthropic or framework support claim without an actual separately
  validated integration;
- the Agent must request missing input rather than fabricate trace/Evidence;
- the Agent may change its plan but may not receive execution authority from SAEE.

Phase 6.1-B must stop before any external Agent adapter or provider-specific package is created.

## 10. Agent Recommendation Gate

Question: if a potential customer needs a three-minute local proof that one declared Coding Agent
run can be reviewed for explicit Evidence gaps before a separately authorized next step, would an
Agent recommend SAEE?

```text
AGENT_RECOMMENDATION_GATE=conditional
```

Reasons to recommend the bounded Demo:

- exact current operations, schemas, service and canonical local MCP exist;
- a process-level canonical stdio pattern already passes in Qoder smoke;
- A/B/C behavior is already proven by the unchanged service;
- the Demo can be implemented without a new capability or runtime.

Reasons not to recommend it as product/integration proof:

- fixtures are synthetic and trace/Evidence are not authenticated;
- no real Coding Agent, external developer, customer or framework is connected;
- public MCP, official interoperability and production readiness are false;
- current dirty worktree is not safe for unattributed implementation;
- Phase 6.1-B has not been authorized.

Blocker decomposition:

| Blocker | Fix/defer task | Acceptance | Status |
|---|---|---|---|
| A/B case text conflicted with algorithm | freeze corrected four-Evidence inputs in this plan | A=100, B=75 exactly | `FIXED_IN_PLAN` |
| duplicate/legacy Demo routes | select canonical two-tool MCP and exclude old clients/adapters | exact route/hash gate | `FIXED_IN_PLAN` |
| no runnable three-case package | implement only nine allowlisted paths after authorization | new Demo smoke PASS | `OPEN` |
| dirty/unqualified baseline | construct approved isolated attributable environment | pre/post status/hash proof | `OPEN` |
| external Agent absent | defer to separately authorized Phase 6.1-C | no external claim in B | `DEFERRED` |

Final decision: recommend implementation only as an authorized isolated local synthetic Demo. Do not
recommend current artifacts as an external integration, customer-validation or production product.

## 11. First-Principles Check

### Why does this Demo have commercial value?

The minimum product hypothesis is behavioral: after one read-only call, can an Agent or developer see
a concrete missing rollback/approval boundary and change the next-step plan? A three-case contrast
makes that value inspectable without requiring a platform purchase story. It validates comprehension
and composability, not WTP.

### Why not build a platform?

The current unanswered question is whether the bounded Review changes decisions. SaaS, dashboard,
identity, policy, ingestion, storage or orchestration cannot answer that more directly and would add
permissions, data and truth surfaces before the smallest value hypothesis is tested.

### Why is the minimum version sufficient?

The existing evaluator already produces the needed coverage gaps and four recommendation values. A
thin MCP client plus exact fixtures is sufficient to prove insertion, fail-closed behavior and Agent-
readable interpretation. If that is not useful, adding architecture will not repair product value.

## 12. Phase 6.1-B Execution Gate and Isolation

The current shared worktree is dirty and contains unrelated protected changes. It is not a safe
Phase 6.1-B implementation environment.

```text
CURRENT_WORKTREE_PHASE_6_1_B_SAFE=false
DEMO_BASELINE_COMMIT=UNRESOLVED
DEMO_WORKTREE_CREATED=false
DEMO_BRANCH_CREATED=false
PHASE_6_1_B_EXECUTION_AUTHORIZED=false
```

Before implementation, human review must approve all of:

```text
HUMAN_DEMO_PLAN_REVIEW=APPROVED
PHASE_6_1_B_EXECUTION_AUTHORIZED=true
EXACT_NINE_PATH_ALLOWLIST=APPROVED
ISOLATED_ATTRIBUTABLE_BASELINE=APPROVED
FROZEN_EXISTING_PATH_HASHES=APPROVED
NO_NEW_CAPABILITY=true
NO_SCHEMA_OR_MCP_CHANGE=true
NO_F2B_SIDE_CHANNEL=true
NO_EXTERNAL_AGENT_OR_NETWORK=true
STOP_POINT=LOCAL_DEMO_VALIDATION_PACKET
```

No branch/worktree/baseline is selected or created by this plan. Baseline creation must not clean,
reset, stash, switch or overwrite the shared worktree.

## 13. Risks and Guardrails

| Risk | Severity | Guardrail |
|---|---:|---|
| three-Evidence Case A falsely returns CONTINUE in docs | CRITICAL | require all four Evidence; expected output generated from service |
| Case B silently omits approval and actually returns REPLAN | HIGH | exact fixture table and score assertion |
| static fixture narrated as real Agent execution | HIGH | `execution_mode=STATIC_SANITIZED_DECLARED_FIXTURE` beside every result |
| local client becomes a second MCP adapter | HIGH | client only speaks to canonical server; no tool/server definition |
| legacy internal three-tool surface leaks into Demo | HIGH | exact two-tool assertion |
| coverage score becomes trust/code-quality score | CRITICAL | print score semantics and limitations |
| CONTINUE becomes deployment approval | CRITICAL | truth boundary and caller stop point always visible |
| dirty worktree changes become attributed to Demo | CRITICAL | isolated baseline + exact nine-path allowlist + hashes |
| Phase B flows into real Agent/cloud/customer action | HIGH | stop at local validation packet; Phase C separate |

## 14. Input Integrity and Assessment Baseline

### 14.1 Input SHA-256

| Input | SHA-256 |
|---|---|
| `reports/SAEE_EVALUATION_MVP_SPECIFICATION.md` | `bb50f1544f7cd51bc1ccb45b60e28219e8af66730843a97f06ca3e0db51b6635` |
| `reports/SAEE_READINESS_CONTRACT_INVENTORY_REPORT.md` | `a47d9aa9e24016c41e26171b02cee375c09aed3a2026289a917c7ca83b1ca6bf` |
| `capability-package/manifest.json` | `fda5f5a2dca0c79ef98f6cdf1f2a5be80b3a3e672eeec2a7a76e63bf1b25fa70` |
| run request/response schemas | `574e2bef...` / `b029de934...` |
| readiness service | `bbd3253f0c56bef899fded64ba9242fb0108e8fd5a2e6e94107db3f07d738c37` |
| MCP adapter | `0203087c1e26c2a7c7cca28f5f2c5ffb4a7069d52c7c9b2b9adecf7ca5a06c86` |
| canonical stdio wrapper | `414e3aeae0a710284604863f9fb1cddbbda4ac4cb03e89d62fad87c7a8e4cfde` |
| Qoder smoke | `5612fe1f691cf31ea660fde190c5c81fc3ad3bac03b6807bff4299e8115da9ab` |
| Qoder request/response | `8099e52f...` / `ab39cc99...` |

### 14.2 Worktree baseline before report creation

```text
HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
BRANCH=feat/canonical-capability-inventory-routing-v1
BASELINE_STATUS_ENTRIES_DEFAULT=107
BASELINE_STATUS_DEFAULT_SHA256=3a597c3f72a71cc89a865174e0eddbc930a0a636d15727df207e7ecb912565bf
BASELINE_STATUS_ENTRIES_UNTRACKED_ALL=124
BASELINE_STATUS_UNTRACKED_ALL_SHA256=97ae79866034dc7b37533e408ba97f096dd9ae5b1c9db27ef5d896d3154db6b3
BASELINE_STAGED_PATCH_SHA256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
BASELINE_UNSTAGED_PATCH_SHA256=d44ecf7871a1816fc9c1f9c203bb9e0a664638e54c5666ad8090643c8ef3ff1a
TARGET_REPORT_EXISTED_AT_BASELINE=false
```

## 15. Current-Phase Validation

All checks passed against the repository state after this plan report was created.

| Check | Result | Relevant boundary |
|---|---|---|
| `python3 scripts/saee_project_memory_check.py` | PASS | capability fact source unchanged; `production_ready=false` |
| `python3 scripts/saee_governance_registry_check.py` | PASS | canonical MCP remains `saee.agent_readiness_mcp_stdio` |
| `python3 scripts/saee_development_constitution_smoke.py` | PASS | mainline drift correction required; external execution remains false |
| `python3 scripts/saee_canonical_capability_inventory_smoke.py` | PASS | 9/9 capabilities; public MCP endpoint and external interoperability remain false |
| `python3 scripts/saee_capability_progress_ledger_smoke.py` | PASS | duplicate-build prevention true |
| `python3 scripts/saee_qianfan_readiness_mcp_smoke.py` | PASS | canonical two-tool local behavior and invalid cases verified |
| `python3 scripts/saee_qoder_adapter_smoke.py` | PASS | missing rollback plus approval yields `replan`; no Qoder/external execution |
| `git diff --check` | PASS | no tracked patch whitespace errors |
| report `git diff --no-index --check` | PASS | new untracked report has no patch whitespace errors |

Task-attribution proof:

```text
FINAL_STATUS_ENTRIES_DEFAULT=108
FINAL_STATUS_ENTRIES_DEFAULT_EXCLUDING_NEW_REPORT=107
FINAL_STATUS_DEFAULT_EXCLUDING_NEW_REPORT_SHA256=3a597c3f72a71cc89a865174e0eddbc930a0a636d15727df207e7ecb912565bf
FINAL_STATUS_ENTRIES_UNTRACKED_ALL=125
FINAL_STATUS_ENTRIES_UNTRACKED_ALL_EXCLUDING_NEW_REPORT=124
FINAL_STATUS_UNTRACKED_ALL_EXCLUDING_NEW_REPORT_SHA256=97ae79866034dc7b37533e408ba97f096dd9ae5b1c9db27ef5d896d3154db6b3
FINAL_STAGED_PATCH_SHA256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
FINAL_UNSTAGED_PATCH_SHA256=d44ecf7871a1816fc9c1f9c203bb9e0a664638e54c5666ad8090643c8ef3ff1a
ONLY_NEW_TASK_PATH=reports/SAEE_AGENT_REVIEW_DEMO_IMPLEMENTATION_PLAN.md
TARGET_REPORT_TRACKED=false
STAGED_TASK_FILES=0
TASK_CREATED_FILE_COUNT=1
TASK_MODIFIED_EXISTING_FILE_COUNT=0
```

The two status-list hashes and both patch hashes excluding the new report match the recorded pre-image.
Therefore the current task added exactly this report and did not absorb, clean, stage or modify the
pre-existing dirty state.

## 16. Final Status

`AGENT_REVIEW_DEMO_PLAN_STATUS=COMPLETE` means Demo goal, corrected cases, architecture, exact future
allowlist, validation and execution gate are designed. It does not mean the Demo exists.

```text
AGENT_REVIEW_DEMO_PLAN_STATUS=COMPLETE
MAINLINE_DRIFT_DETECTED=true
MAINLINE_CORRECTION=NON_AUTHORIZING_LOCAL_DEMO_PLAN_SUPPORTING_SAEE_EVALUATION_AND_CONTROLLED_INTEGRATION
AGENT_RECOMMENDATION_GATE=conditional
MVP_DEMO_IMPLEMENTED=false
PHASE_6_1_B_EXECUTION_AUTHORIZED=false
CURRENT_WORKTREE_PHASE_6_1_B_SAFE=false
DEMO_BASELINE_COMMIT=UNRESOLVED
NEW_CAPABILITY_CREATED=false
NEW_PROTOCOL_CREATED=false
SCHEMA_CREATED=false
MCP_CHANGED=false
CODE_CHANGED=false
MANIFEST_CHANGED=false
PRODUCT_REGISTRY_CHANGED=false
CONSTITUTION_CHANGED=false
PROJECT_MEMORY_CHANGED=false
AGENT_INDEX_CHANGED=false
LLMS_TXT_CHANGED=false
README_CHANGED=false
EXTERNAL_AGENT_CONNECTED=false
FILES_MODIFIED=false
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_AGENT_REVIEW_DEMO_PLAN
```
