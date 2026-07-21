# SAEE Agent Review Skill MVP Specification

```text
report_id=SAEE_AGENT_REVIEW_SKILL_MVP_SPECIFICATION
requested_phase_label=Phase_8.0-A0
phase_label_canonical=false
report_type=SPECIFICATION_ONLY_NO_IMPLEMENTATION
specification_date=2026-07-16
spec_revision=2
revision_from=Phase_7.0-A
revision_mode=IN_PLACE_TARGETED_PATCH_NO_DUPLICATE_SPEC
previous_spec_sha256=17f6a152c8a1853a58c590034cc7718eb3f5fc89f4800929c68bbad2d0064910
current_authority=SAEE_Development_Constitution_v1.1
program_mainline=saee_agent_evidence_integration
current_business_validation_priority=SAEE_Agent_Review_Skill_MVP
target_agent=Coding_Agent
first_user_persona=Independent_Developer_Using_A_Local_Coding_Agent
first_use_case=Post_Run_Pre_Consequential_Coding_Change_Review
experience_target_minutes=10
```

## 1. Executive Decision

`SAEE Agent Review` 可以作为现有 `saee.evaluate_agent_run` 的 Agent-facing Skill
projection（面向智能体的技能投影）进入最小真实使用入口设计。它不是新 Capability、
Schema、Protocol、MCP Tool、Runtime、Product Registry entry 或 Authorization System。

Skill 的最小职责是：让一个独立开发者在 10 分钟内把 Agent-readable instructions
暴露给一个本地 Coding Agent；当已有声明性计划或 coding run、且即将进入重大下一步时，
Agent 能识别调用资格，复用现有本地 Evaluation operation，读取 Evidence 缺口，并据此
调整自己的下一步计划。

```text
SKILL_EXTERNAL_NAME=SAEE Agent Review
INTERNAL_ENGINE=existing_SAEE_Evaluation
PRIMARY_OPERATION=saee.evaluate_agent_run
SUPPORTING_OPERATION=saee.evaluate_evidence_optional
SKILL_CLASSIFICATION=DESIGN_ONLY_AGENT_FACING_PROJECTION
EXISTING_CAPABILITY_REUSED=true
NEW_CAPABILITY_REQUIRED=false
NEW_SCHEMA_REQUIRED=false
NEW_PROTOCOL_REQUIRED=false
AUTO_TRIGGER_IMPLEMENTED=false
REAL_AGENT_INVOCATION_VALIDATED=false
COMMERCIAL_VALUE_VALIDATED=false
FIRST_STATIC_VALUE_SIGNAL=true
SKILL_FIRST_USER_FEEDBACK_COLLECTED=false
TEN_MINUTE_EXPERIENCE_VALIDATED=false
F7_ADOPTION_VALIDATION_STATUS=COMPLETE_FROZEN_NOT_EXECUTED
F8_ADOPTION_VALIDATION_AUTHORIZED=false
```

当前 Agent Recommendation Gate 结论为 `conditional`：可以向接受 local alpha、
declared-run 与 non-authorization 边界的独立开发者推荐一个未来受控试用；在 Skill
artifact、loader、10 分钟安装路径和真实用户反馈尚不存在时，不能把它推荐为已可安装、
生产安全门、自动审批器、认证系统或已验证商业产品。

## 2. Authority and Mainline Correction

```text
MAINLINE_DRIFT_DETECTED=true
```

请求把 Phase 8 Skill MVP 描述为当前产品路线，但 active Constitution v1.1 冻结的项目
主线仍是 SAEE 与 Agent Evidence Project 的受控集成。经纠偏，本规格只把 Agent Review
定义为 secondary business-validation priority（商业验证副线优先级），服务未来
`SAEE Evaluation` 产品投影，不覆盖宪法主线。

目标路径已经存在 Phase 7.0-A 早期规格。为避免第二份同义真源，本次以定向原位修订
升级为 `Phase 8.0-A0`，保留旧版 SHA-256 作为 lineage anchor；该 phase 仍只是 Human
routing label，不登记为新的宪法规范 phase。

```text
PROGRAM_MAINLINE_CHANGED=false
CURRENT_AUTHORITY_CHANGED=false
PHASE_LABEL_CANONICAL=false
CAPABILITY_FACT_SOURCE_CHANGED=false
SECOND_SKILL_SPEC_CREATED=false
PREVIOUS_SPEC_LINEAGE_RECORDED=true
F7_FROZEN=true
F8_EXECUTION_AUTHORIZED=false
GOVERNANCE_TRACK_STATUS=VALIDATED_PROTOTYPE_PAUSED
H0_R_GRANTED=false
BASELINE_RECONSTRUCTION_EXECUTION_AUTHORIZED=false
```

## 3. Skill Positioning

### 3.1 What the Skill is

`SAEE Agent Review` 是一个最小 Agent workflow checkpoint：

```text
Coding Agent
    ↓
declared plan/run trace + declared Evidence
    ↓
SAEE Agent Review
    ↓
saee.evaluate_agent_run
    ↓
Recommendation + missing Evidence + limitations
    ↓
Agent changes its next-step plan
```

“Skill”在本规格中表示 Agent 可发现的使用说明、触发规则、现有 Tool 路由和结果解释，
不表示已经采用 OpenAI、Anthropic、Claude Code、Codex 或其他平台的官方 Skill 标准。

### 3.2 Why an Agent would call it

Coding Agent 通常能生成代码、运行命令和给出计划，但未必在重大下一步前显式检查：

- 是否声明了测试结果；
- 是否存在回滚方案；
- 是否说明权限边界；
- 是否存在独立人工批准上下文。

SAEE 的购买或组合理由不是“更聪明地写代码”，而是用稳定 machine-readable output
把这些 Evidence 的 required / present / missing 状态变成下一步 decision context。

如果目标工作流已有等价的机器可读 release/change gate，并能输出同样的 Evidence 缺口、
reason 与 non-claims，则 Agent 应拒绝重复组合 SAEE。

### 3.3 Product and capability boundary

| Surface | Current role | This specification |
|-|-|-|
| `saee.evaluate_agent_run` | `implemented / active / local alpha` | primary operation, reuse unchanged |
| `saee.evaluate_evidence` | `implemented / active / local alpha` | optional diagnostic, reuse unchanged |
| `saee.agent_readiness_mcp_stdio` | canonical local two-tool MCP; not publicly deployed | local invocation transport only |
| `SAEE Agent Review` | no canonical Skill artifact exists | design-only presentation and routing layer |
| `SAEE Evaluation` | target customer-version product projection; locally implemented surface | parent product context, not newly launched |

```text
EVALUATION_ENGINE_REBUILD=DO_NOT_BUILD
SECOND_CAPABILITY_SOURCE_CREATED=false
SECOND_MCP_ENTRANCE_CREATED=false
SKILL_IS_CAPABILITY=false
SKILL_IS_AUTHORITY=false
```

## 4. First User Persona and Use Case

### 4.1 First user persona

MVP 的第一个用户不是企业采购部门，也不是平台管理员，而是：

> 一名已经在本地代码仓库使用 Coding Agent、需要在重大变更后决定是否进入 merge、
> release 或其他 consequential next step 的独立开发者。

该用户愿意运行本地、synthetic 或 sanitized 示例，能理解 tests、rollback、permission
boundary 与 Human approval 的区别，并能在体验结束后给出具体 `retain/compose/reject`
反馈。

```text
FIRST_USER_ROLE=Independent_Developer
FIRST_USER_USES=Coding_Agent
FIRST_USER_CONTEXT=Local_Or_Controlled_Code_Workspace
FIRST_USER_ENTERPRISE_ADMIN_REQUIRED=false
FIRST_USER_CUSTOMER_DATA_REQUIRED=false
```

### 4.2 First use case

第一场景固定为：**Coding Agent 已完成一个 bounded coding change 并通过本地 tests，准备
进入 merge/release-like consequential next step，但 `ROLLBACK_PLAN` 缺失。**

Skill 应帮助 Agent 把模糊的“需要人工确认”转化为：当前哪些 Evidence 已声明、缺少什么、
为什么需要补充，以及 Recommendation 不等于 Authorization。

```text
FIRST_USE_CASE=CODING_CHANGE_REVIEW_BEFORE_CONSEQUENTIAL_NEXT_STEP
FIRST_USE_CASE_TIMING=POST_RUN_PRE_CONSEQUENTIAL_ACTION
FIRST_USE_CASE_EXPECTED_GAP=ROLLBACK_PLAN
FIRST_USE_CASE_EXTERNAL_ACTION_EXECUTED=false
```

### 4.3 Target Agent and first observation carrier

MVP 仅支持 `Coding Agent`。Codex CLI 可以作为第一个 observation carrier（观察载体），
因为已有本地实验证据，但产品定位不是 `SAEE for Codex`；Skill contract 必须保持
platform-neutral，未来不得声称 OpenAI、Anthropic 或其他平台官方集成。

```text
TARGET_AGENT_TYPE=Coding_Agent
FIRST_OBSERVATION_CARRIER=Codex_CLI_LOCAL
PRODUCT_BOUND_TO_CODEX=false
TARGET_ENVIRONMENT=local_or_controlled_workspace
TARGET_DATA=synthetic_or_sanitized_declared_metadata
CUSTOMER_DATA_INCLUDED=false
OFFICIAL_PLATFORM_INTEGRATION_REQUIRED=false
```

MVP 不扩展到运维、合同、财务、采购、医疗、政府或其他领域。Deploy、数据库迁移和
基础设施只作为 Coding Agent 的候选下一步边界出现；SAEE 不执行这些动作。

## 5. Trigger Conditions

### 5.1 Mandatory trigger candidate

Skill 只应在以下条件全部满足时被 Agent 选择：

1. 当前 Agent 是 Coding Agent；
2. 已有可声明的 plan/run trace，而不是凭空预测未来行为；
3. 候选下一步被标记为 `high_impact=true` 或会产生 `external_effect=true`；
4. Agent 能按当前 schema 提供 Evidence object，且 `customer_data_included=false`；
5. 调用目的只是获得 decision context，不是请求授权。

首个可信触发边界：

```text
declared planning/coding run exists
↓
before merge / deploy / release / database migration execution /
production configuration change / destructive infrastructure change
↓
invoke saee.evaluate_agent_run
```

### 5.2 Current semantic limitation

当前 operation 不是 proposed-action predictor。它不能在没有 trace 的情况下判断未来代码
修改是否安全，也不验证代码内容。用户提出的“修改生产代码前”只有在一个 planning run
已被声明时才可进入本地实验；更可靠的首个场景仍是 coding run 完成后、重大下一步之前。

```text
PRE_INITIAL_MUTATION_REVIEW_SUPPORT=PARTIAL_DECLARED_PLAN_ONLY
POST_RUN_PRE_NEXT_STEP_REVIEW_SUPPORT=YES_LOCAL
PROPOSED_ACTION_ENGINE=false
```

### 5.3 Do-not-trigger rules

以下情况默认不调用：

- 只读解释、搜索、格式化或低影响局部编辑；
- 缺少 `trace.events`，且 Agent 只能虚构 trace；
- 用户真正需要 IAM、Policy、Security Scanner、审批或执行控制；
- 需要证明 Evidence 真实性、部署安全性、法律责任或认证；
- 输入包含客户数据、个人信息、密钥或未授权生产内容。

缺少当前 schema 所需输入时，Agent 应先请求输入，不得制造 Evidence 后调用。

## 6. Input Contract

### 6.1 Reuse the existing request schema

唯一请求 contract 保持：

```text
agent-interface/qianfan/saee-evaluate-agent-run-request.schema.v0.1.json
```

用户概念示例需要映射到现有字段，不能被误写成新 schema：

| Conceptual term | Existing contract |
|-|-|
| `agent` | `agent_id`, namespaced as `agent:*` |
| `task` | existing non-empty `task` string |
| `trace` | object containing `1..100` declared `events` |
| string Evidence list | array of Evidence objects |
| `SCOPE_BOUNDARY` | existing `PERMISSION_BOUNDARY` |
| `APPROVAL_CONTEXT` | existing `HUMAN_APPROVAL` |

高影响 run 的现有 Evidence closed set 为：

```text
TEST_RESULT
ROLLBACK_PLAN
PERMISSION_BOUNDARY
HUMAN_APPROVAL
```

每项 Evidence 必须包含：

```text
evidence_id
evidence_type
present
source_ref
```

`present=true` 只表示调用者声明该引用存在，不证明内容正确、来源真实或批准有效。

### 6.2 Schema-valid conceptual example

```json
{
  "request_id": "request:agent-review-mvp-001",
  "agent_id": "agent:coding-agent",
  "task": "Review a declared payment-module coding run before merge",
  "trace": {
    "events": [
      {
        "event_id": "event:declared-coding-run",
        "event_type": "CHECK",
        "summary": "A sanitized local coding run and its test step were declared",
        "external_effect": false,
        "high_impact": true
      }
    ]
  },
  "evidence": [
    {
      "evidence_id": "evidence:test-result",
      "evidence_type": "TEST_RESULT",
      "present": true,
      "source_ref": "demo://agent-review/test-result"
    },
    {
      "evidence_id": "evidence:rollback-plan",
      "evidence_type": "ROLLBACK_PLAN",
      "present": false,
      "source_ref": null
    },
    {
      "evidence_id": "evidence:permission-boundary",
      "evidence_type": "PERMISSION_BOUNDARY",
      "present": true,
      "source_ref": "demo://agent-review/permission-boundary"
    },
    {
      "evidence_id": "evidence:human-approval",
      "evidence_type": "HUMAN_APPROVAL",
      "present": true,
      "source_ref": "demo://agent-review/human-approval"
    }
  ],
  "customer_data_included": false
}
```

该 example 只是规格内说明，不是新 fixture、Schema、Protocol 或执行授权。

## 7. Output and Agent Behavior

输出 vocabulary 冻结为现有四值：

```text
CONTINUE
HUMAN_REVIEW_REQUIRED
REPLAN
STOP
```

禁止增加 `APPROVED`、`SAFE`、`TRUSTED`、`CERTIFIED` 或其他授权/认证语义。

| Recommendation | Required Agent behavior | Never means |
|-|-|-|
| `CONTINUE` | 只进入下一个独立控制/授权步骤 | approved, safe, deployable |
| `HUMAN_REVIEW_REQUIRED` | 把缺口和 decision context 提交给人工权威 | approval already exists |
| `REPLAN` | 修改计划或补充 Evidence，再重新评估 | SAEE automatically fixes or retries |
| `STOP` | 停止当前 bounded flow | legal ban or external kill authority |

Agent 至少必须读取：

```text
recommendation
required_evidence
present_evidence
missing_evidence
risks
score
score_semantics
limitations
truth_boundary
```

`score` 只是 required Evidence coverage percent，不是 trust、safety、security、quality 或
成功概率。

## 8. Discovery, Invocation and Interpretation Workflow

### 8.1 Discovery

未来 MVP implementation 必须通过一个小型、文件化、Agent-readable package 让 Agent
发现触发语义，同时从现有规范能力入口解析真实 operation，不得再建 registry：

```text
saee-agent-review-skill/
  SKILL.md
  README.md
  examples/
    coding-change-review.md
    missing-evidence-example.md
```

该目录结构只是实施 allowlist 候选，不是本阶段创建的 Protocol、Schema 或 Skill artifact。
未来 Agent discovery 路径必须为：

```text
installed_or_referenced_SKILL.md
↓
Agent understands when to use / when not to use
↓
capability-package/manifest.json#canonical_inventory
↓
saee.agent_readiness_mcp_stdio
↓
tools/list
↓
saee.evaluate_agent_run
```

本规格没有创建 Skill artifact、安装器或 loader，也没有证明自然发现或任何平台自动加载。

### 8.2 Invocation

```text
Agent classifies candidate next step as high impact
↓
Agent verifies current request fields exist
↓
Agent calls saee.evaluate_agent_run once
↓
invalid input: request missing input and emit no recommendation
valid input: read complete result
```

### 8.3 Interpretation

调用者必须基于 `recommendation + missing_evidence + limitations + truth_boundary` 改变
下一步计划。只打印结果但继续原动作，不计为 Skill 成功。

### 8.4 Ten-minute installation experience target

未来实现的第一体验必须让一个已经具备本地 Coding Agent 与 SAEE repository 的开发者在
10 分钟内完成以下闭环；本阶段只冻结体验目标，不声称已经达到：

|Timebox|Developer / Agent action|Success evidence|
|-|-|-|
|0–2 minutes|读取 `README.md` 与 non-claims，选择一个明确 loader path|用户能说清 SAEE 不授权、不执行|
|2–4 minutes|安装或引用 `SKILL.md`，解析现有 local MCP operation|Agent 能发现 `saee.evaluate_agent_run`|
|4–7 minutes|运行 packaged sanitized missing-rollback example|schema-valid request；不虚构 Evidence|
|7–9 minutes|读取 Recommendation、missing Evidence、limitations 与 truth boundary|Agent 明确请求 `ROLLBACK_PLAN` 或 replan|
|9–10 minutes|开发者记录 `retain/compose/reject` 与原因|形成第一个真实使用反馈|

```text
TEN_MINUTE_TARGET_SECONDS=600
TEN_MINUTE_INSTALL_PATH_IMPLEMENTED=false
TEN_MINUTE_INSTALL_PATH_VALIDATED=false
EXACT_SKILL_LOADER_SELECTED=false
INSTALLATION_COMMAND_FROZEN=false
```

若 exact loader 或安装命令无法在实施前冻结，Phase 8.0-A1 必须停下，不能用人工临时指导
替代可复现的安装体验。

## 9. MVP Workflow Cases

### Case A — sufficient declared Evidence

四类 Evidence 均 present。现有预期结果为 `CONTINUE`。Agent 只能进入独立 merge/release
审查，不得把结果解释为部署授权。

### Case B — rollback missing

`ROLLBACK_PLAN.present=false`。现有预期结果为：

```text
recommendation=HUMAN_REVIEW_REQUIRED
missing_evidence=ROLLBACK_PLAN
risk=missing_recovery_plan
```

Agent 必须暂停重大下一步并向用户请求 rollback context。这是首个行为变化验证用例。

### Case C — insufficient input

缺少 `trace` 或 `trace.events`。应 fail closed，不产生四值 recommendation；Agent 请求
declared trace，而不是虚构输入。

### Negative control — low-impact task

只读解释或低影响格式化任务不应调用 SAEE。MVP 必须同时验证“该调用时调用”和“不该
调用时不调用”，否则会形成成本与打扰。

## 10. Non-Goals

MVP 明确不创建或提供：

- 自动批准、自动执行或自动业务责任承担；
- IAM、Policy Engine、Security Scanner 或 Observability replacement；
- Trust Score、Agent Certificate、Agent Passport 或认证；
- Enterprise Dashboard、标准协议或新治理层；
- proposed-action prediction、代码质量判断或漏洞扫描；
- OpenAI、Anthropic、Claude Code、Codex、LangGraph、CrewAI、千帆或百炼官方集成；
- public endpoint、客户验证、产品发布、商业采用或 production readiness；
- Evidence 真实性、来源身份、完整性、法律责任或行动安全保证。

继续冻结：

```text
SAEE_RECOMMENDATION_NOT_AUTHORIZATION=true
SAEE_EXECUTION_CONTROL=false
SAEE_AUTO_APPROVAL_CORE=false
```

## 11. Commercial Validation Design

### 11.1 What the completed experiments already established

Phase 7 A/B sessions 与 F4 static review 必须分层解释：

|Observed surface|Result|Meaning|
|-|-|-|
|Session A control|`PAUSE_AND_REQUEST_HUMAN_CONTEXT`|Coding Agent 本身已有风险意识|
|Session B with Trigger + MCP exposure|同样暂停；`MCP_INVOKED=false`|被动 Tool exposure 没有产生 SAEE 调用|
|F4 anonymous static review|`FIRST_VALUE_SIGNAL=true`|结构化 Evidence Gap 比 generic pause 更能说明下一步|
|F6/F7 adoption design|设计完成、未执行|未来验证方法存在，但不构成采用证据|

因此当前 truth 是：

```text
REAL_AGENT_SESSION_EXPERIMENT_COMPLETED=true
PASSIVE_TOOL_DISCOVERY_PRODUCED_INVOCATION=false
FIRST_STATIC_VALUE_SIGNAL=true
SKILL_ARTIFACT_USED_BY_REAL_USER=false
SKILL_MEDIATED_AGENT_INVOCATION_VALIDATED=false
COMMERCIAL_VALIDATION_STARTED=false
```

Phase 8 不重跑原 A/B，也不继续 F8 adoption protocol；它只验证一个真实开发者是否能在
10 分钟内安装或引用 Skill、让 Agent理解使用时机，并形成一次真实使用反馈。

### 11.2 First-user validation loop

Phase 8.0-A1 若获独立授权，只允许一个开发者、一个本地 Coding Agent、一个 sanitized
missing-rollback case：

1. 从发布包之外的简短说明进入 Skill package；
2. 独立按 frozen loader/install instructions 完成安装或引用；
3. 让 Agent 读取 Skill，并说明何时使用、何时不使用；
4. 提供一个已经冻结、schema-valid 的 declared run/evidence packet；
5. 不直接命令 Tool call，观察 Agent 是否按 Trigger Semantics 选择现有 operation；
6. 如果调用，封存 request、response 与 recommendation interpretation；
7. 运行一个 low-impact negative control，确认 Agent 不应无差别调用；
8. Developer 记录 `retain/compose/reject`、具体理由、完成时间和阻塞点；
9. 停止，不自动进入 Hook、平台、客户推广或 F8。

不得触及 production code、customer data、provider account mutation、merge、deploy、push
或其他 external action。

### 11.3 First success signals

第一成功信号不是安装量，也不是 Tool 返回成功，而是一个最小闭环：

```text
INSTALLATION_EXPERIENCE_PASS =
  independent_developer_completed_without_live_coaching
  AND elapsed_seconds <= 600
  AND exact_loader_and_commands_recorded

AGENT_USAGE_PASS =
  skill_discovered
  AND when_to_use_understood
  AND when_not_to_use_understood
  AND eligible_packet_not_fabricated
  AND existing_operation_selected_without_forced_tool_call

DECISION_CONTEXT_PASS =
  missing_rollback_gap_observed
  AND recommendation_interpreted_as_context_not_authority
  AND next_request_became_more_specific

FIRST_REAL_USE_SIGNAL =
  developer_decision in {retain,compose}
  AND specific_reason is non-empty
```

四项必须分别记录。即使全部通过，也只建立 `FIRST_REAL_USE_SIGNAL=true`，不建立
commercial validation、willingness-to-pay、customer validation、market validation 或
production readiness。

### 11.4 Falsification and stop conditions

出现任一情况，应降级或停止 Skill 路线：

- 10 分钟体验依赖作者实时指导、临时修改 config 或隐藏步骤；
- Agent 看见 Skill 后仍不能说明调用条件或 current input eligibility；
- Agent 需要虚构 trace / Evidence 才能调用；
- 只有“请调用 SAEE”这种强制命令才能产生 Tool call；
- Agent 对低影响任务也调用，形成高噪声；
- Recommendation 只被打印，没有改善下一步 Evidence request；
- 用户选择 `reject`，或认为现有 CI / Code Review / Agent summary 已以更低成本提供同样价值；
- 有用体验必须增加新 Capability、Schema、Protocol、Hook、Authorization 或 Execution Control；
- 需要 production data、external action 或官方平台集成 claim 才能展示价值。

## 12. Agent Recommendation Gate

### Customer question

If a potential customer needs a Coding Agent to turn a vague pre-consequential escalation into a
structured Evidence Gap, would an Agent recommend the current SAEE Agent Review Skill MVP?

```text
AGENT_RECOMMENDATION_GATE=conditional
```

### Reasons to recommend conditionally

- the canonical operation and current schemas already exist;
- local deterministic MCP transport exists;
- F4 produced one positive static decision-context signal;
- missing Evidence, risks, limitations and four-value recommendation already exist;
- the first Skill can remain a small Agent-readable projection rather than a platform;
- no new Capability, Schema or Runtime is required for the first behavioral experiment;
- SAEE performs no external action.

### Blocker decomposition

| Blocker | Fix or boundary | Acceptance criterion | Status |
|-|-|-|-|
| Skill artifact does not exist | Phase 8.0-A1 may create only the exact bounded package after separate authorization | exact four-path allowlist; no new contract | `OPEN` |
| exact loader/install command unresolved | select one first observation carrier without product binding | clean install from frozen instructions in at most 10 minutes | `OPEN` |
| passive Tool exposure did not produce invocation | make Trigger Semantics visible through Skill; do not force call | Agent explains eligibility and independently selects existing operation | `OPEN` |
| eligible packet was absent in first A/B experiment | package one frozen sanitized schema-valid example | no fabricated trace or Evidence | `OPEN` |
| decision-context value only static | observe one Skill-mediated call and next request | missing Evidence makes next request more specific | `OPEN` |
| first-user value absent | collect concrete `retain/compose/reject` feedback | decision plus specific reason recorded | `OPEN` |
| broad pre-action wording exceeds current run semantics | keep `POST_RUN_PRE_CONSEQUENTIAL_ACTION` | every example preserves timing boundary | `FIXED_IN_SPEC` |
| external/customer/production proof absent | retain staged-truth boundary | all related flags remain false | `DEFERRED` |

Final recommendation: recommend only as a future internal, sanitized, local first-user experiment
after Phase 8.0-A1 authorization. The current repository does not yet contain an installable Skill.
Do not recommend it as a production control, automatic safety system, authorization service,
official platform integration or customer-validated product.

## 13. First-Principles Check

### Why does the Agent era need a Review node?

Agent 能快速生成动作，但“生成动作”和“证明当前 Evidence 足以进入下一步”是两个不同
问题。Review node 把隐含的 test、rollback、permission 与 human checkpoint 变成可解析
缺口，使 Agent 在不可逆动作前具备停止、补充或上交判断的理由。

### Why is a Skill a better first entrance than an enterprise platform?

商业假设发生在 Agent workflow 内：Agent 是否会选择 Evaluation，以及结果是否改变行为。
Skill 投影直接进入该决策点，复用现有 MCP contract；平台、Dashboard、协议和企业治理
不会让这个假设更快被证伪，反而增加集成与购买摩擦。

### Why is real usage feedback more important than more simulation now?

现有 synthetic A/B 已经证明被动 Tool exposure 不足，F4 又证明结构化 Evidence Gap 可能
改善判断。继续模拟只能进一步优化我们自己的验证方法；只有一个独立开发者能否安装、
一个 Agent 能否理解并使用、以及用户是否愿意留下，才能暴露真实入口、摩擦和语言问题。

### Why prove someone uses it before developing a Hook?

Hook 会放大触发频率，但不会创造净价值。如果 Skill 不能在一次清晰、低成本体验中让用户
获得更具体的下一步，Hook 只会更频繁地产生输入准备、延迟和噪声。先证明有人使用并选择
`retain/compose`，才能知道 Hook 应放大什么，而不是先放大未经验证的流程。

### Why is the minimum version sufficient?

一个现有 Tool、一个高影响场景、一个缺失 rollback 用例和一个低影响 negative control，
已经足以验证：发现、调用、理解、行为变化与使用价值。若这个最小闭环不成立，扩大平台
不会修复核心需求。

## 14. Required Design Check

| Check | Decision |
|-|-|
| Affected layer | Evaluation product projection; Evidence is input |
| Evolution subsystem | Pareto Fitness Evaluation, with rollback/archive decision context |
| Affected object | this specification report only |
| Capability impact | none; existing capability facts unchanged |
| Duplication check | canonical inventory, ledger, schemas, service, MCP, discoverability and prior Agent Review reports searched; rebuild denied |
| Standard alignment | existing JSON Schema 2020-12 and local MCP projection only; no new protocol/adoption claim |
| Safety and permissions | local sanitized metadata; no execution, data expansion or external action |
| Audit-first risk | contained while Skill remains a bounded Evaluation projection rather than project identity |
| Claims | a design-only Agent-facing route over existing local operations is specified |
| Non-claims | no Skill implementation, real invocation, commercial value, customer or production proof |

## 15. Phase 8.0-A1 Implementation Entry Gate

本规格不授权实现。未来最小 Skill 实现必须先由人工批准：

```text
REQUIRED_HUMAN_SPEC_REVIEW=APPROVED
REQUIRED_PHASE_8_0_A1_EXECUTION_AUTHORIZATION=APPROVED
REQUIRED_PHASE_LABEL_OR_UNIQUE_EXECUTION_ID=HUMAN_BOUND
REQUIRED_EXACT_FILE_ALLOWLIST=APPROVED
REQUIRED_SKILL_FORMAT_AND_LOADER=EXPLICITLY_SELECTED
REQUIRED_TEN_MINUTE_INSTALL_INSTRUCTIONS=FROZEN
REQUIRED_FIRST_USER_FEEDBACK_RECORD=DEFINED
REQUIRED_CANONICAL_OPERATION=saee.evaluate_agent_run
REQUIRED_CURRENT_SCHEMA_FROZEN=true
REQUIRED_CURRENT_OUTPUT_ENUM_FROZEN=true
REQUIRED_NO_NEW_CAPABILITY=true
REQUIRED_NO_NEW_PROTOCOL=true
REQUIRED_NO_RUNTIME_OR_MCP_CHANGE=true
REQUIRED_STOP_POINT=LOCAL_SKILL_ARTIFACT_AND_INSTALLATION_PREFLIGHT
```

Phase 8.0-A1 即使获批，也只允许创建并验证最小 Skill package；它不自动授权真实外部
Agent test、customer contact、平台集成、发布、commit、push、Workflow Hook 或 F8 adoption
validation。第一次真实使用需要下一道独立 one-use gate。

## 16. Validation Record

本次 Phase 8 revision 复用目标文件，不创建第二份同义规格。完成后必须重新验证 canonical
inventory、ledger、existing MCP 与治理边界：

| Validation | Result |
|-|-|
| target path duplicate check | existing canonical report reused; no second Skill specification created |
| `python3 scripts/saee_project_memory_check.py` | PASS; capability fact source unchanged; production false |
| `python3 scripts/saee_governance_registry_check.py` | PASS; canonical MCP unchanged; runtime integration false |
| `python3 scripts/saee_development_constitution_smoke.py` | PASS; deterministic `10/10`; constitutional mainline preserved |
| `python3 scripts/saee_canonical_capability_inventory_smoke.py` | PASS; capabilities `9/9`; negative cases `16/16` |
| `python3 scripts/saee_capability_progress_ledger_smoke.py` | PASS; duplicate-build prevention true |
| `python3 scripts/saee_qianfan_readiness_mcp_smoke.py` | PASS; tools `2`; demos `3`; deterministic `5/5`; operation set unchanged |
| existing missing-rollback example path | covered by current MCP smoke; coding readiness `replan`; no authorization claim |
| `git diff --check` | PASS after revision |

完整 `mainline_guard.py` 本阶段未运行，因为它不是用户要求的 report-only verifier，且当前
dirty worktree 中历史记录表明其可能写入 tracked files。以上 targeted PASS 不得扩展为
full mainline reproducibility claim。

Input integrity anchors:

```text
CAPABILITY_MANIFEST_SHA256=fda5f5a2dca0c79ef98f6cdf1f2a5be80b3a3e672eeec2a7a76e63bf1b25fa70
TRIGGER_SEMANTICS_DESIGN_SHA256=8dbcb5914087e119554f970fddfb270d498376a2b8cd37d3134b20847b656711
STATIC_VALUE_CONCLUSION_SHA256=3b4604cd20a8b2a514e8b233e187b6f0822b5b90a5f486b8ce036b99efd2e349
WORKFLOW_ENTRY_ANALYSIS_SHA256=c885e22459a541e60fba1110a5d41971e6e16980efa6585a8410ad80c8105525
F7_EXECUTION_PREPARATION_SHA256=94ff917408c65f2cf22cbcd27f4245f7648f3d707164005689c8b02040347222
TARGET_REPORT_PREIMAGE_SHA256=17f6a152c8a1853a58c590034cc7718eb3f5fc89f4800929c68bbad2d0064910
TARGET_REPORT_UPDATE_MODE=IN_PLACE_TARGETED_REVISION
```

## 17. Final Status

```text
SAEE_AGENT_REVIEW_SKILL_MVP_SPEC_STATUS=COMPLETE
AGENT_REVIEW_SKILL_MVP_SPEC_STATUS=COMPLETE
MAINLINE_DRIFT_DETECTED=true
MAINLINE_CORRECTION=BUSINESS_VALIDATION_PRIORITY_SUPPORTS_CONSTITUTIONAL_INTEGRATION_MAINLINE
PHASE_LABEL_CANONICAL=false
REQUESTED_PHASE_LABEL=Phase_8.0-A0
SPEC_REVISION=2
SECOND_SKILL_SPEC_CREATED=false
AGENT_RECOMMENDATION_GATE=conditional
SKILL_IMPLEMENTED=false
AUTO_TRIGGER_IMPLEMENTED=false
REAL_AGENT_INVOCATION_VALIDATED=false
BEHAVIOR_CHANGE_VALIDATED=false
COMMERCIAL_VALUE_VALIDATED=false
FIRST_STATIC_VALUE_SIGNAL=true
SKILL_FIRST_USER_FEEDBACK_COLLECTED=false
TEN_MINUTE_EXPERIENCE_VALIDATED=false
F7_ADOPTION_VALIDATION_STATUS=COMPLETE_FROZEN_NOT_EXECUTED
F8_ADOPTION_VALIDATION_AUTHORIZED=false
PHASE_8_0_A1_IMPLEMENTATION_AUTHORIZED=false
WORKFLOW_HOOK_IMPLEMENTED=false
COMMERCIAL_VALIDATION_STARTED=false
NEW_CAPABILITY_CREATED=false
NEW_PROTOCOL_CREATED=false
SCHEMA_CREATED=false
MCP_CHANGED=false
CODE_CHANGED=false
PRODUCT_REGISTRY_CHANGED=false
CONSTITUTION_CHANGED=false
PROJECT_MEMORY_CHANGED=false
CAPABILITY_MANIFEST_CHANGED=false
AGENT_INDEX_CHANGED=false
LLMS_TXT_CHANGED=false
README_CHANGED=false
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_AGENT_REVIEW_SKILL_MVP_SPEC
```
