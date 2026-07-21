# SAEE Decision Log

本日志采用 append-only（仅追加）原则。已有条目不得静默改写或删除；如需纠正，新增
后继条目并引用被纠正的 decision ID。日志记录决策历史，不替代对应 ADR、commit、
registry 或外部证据。

## D-001

日期：

2026-07-14

主题：

建立 Phase 0 治理

决定：

建立 Governance Foundation，提供 registry、ADR、Codex 规则和离线 validator。

状态：

COMPLETED

证据：

Commit `307cebd6c`。

---

## D-002

日期：

2026-07-14

主题：

Codex 身份治理

决定：

Codex 必须服从 SAEE Development Constitution v1.1，并通过身份与上下文验证。

状态：

COMPLETED

证据：

Commit `e12f62a2cd8aa39f70c2ec48f3ffa1b8ba7c3b81`。

---

## D-003

日期：

2026-07-14

主题：

SAEE 自用验证

决定：

建立 Dogfooding Protocol；SAEE 可以评估自身工程变化，但不能批准自身变化。

状态：

COMPLETED

证据：

Commit `f6ac41f4b068377e7778e8c3d83b99bd8382debc`；decision `CONTINUE`；candidate capability `DESIGN_ONLY`。

---

## D-004

日期：

2026-07-14

主题：

产品族与子系统方向

决定：

SAEE 与 Agent Evidence 在宪法架构层形成产品族/子系统关系：Agent Evidence 属于
SAEE Evidence and Immune Subsystem，同时保留源仓库、runtime 和 marketplace 的
分阶段独立性；治理作为支持面服务 Evidence 与 Evaluation 演化。

状态：

DECIDED

证据：

`docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md`；
`governance/decisions/ADR-0002-agent-evidence-boundary.md`。

---

## D-005

日期：

2026-07-14

主题：

主线任务、监督测试副线与三个客户版本纠偏

决定：

冻结当前项目主线为 SAEE 与 Agent Evidence Project 的受控合并；冻结副线为利用
SAEE 监督、测试和评估合并过程；冻结最终客户版本为 `SAEE Evidence`、`SAEE
Evaluation`、`SAEE Governance`。任何 Commander/role prompt 或局部路线若把副线
提升为主线，Agent 必须指出漂移并提出修正。

状态：

DECIDED

证据：

明确人类指令；`governance/project-memory/decision-change-proposals/DCP-001-mainline-and-three-customer-versions.md`。

---

## Trust Semantic Alignment Human Approval — Phase 0.5.5D

日期：

2026-07-15

主题：

Trust Semantic 人工批准与语义对齐同步。

决定：

人工批准 Trust Semantic 设计方向：`Trust Semantic Layer` 是 `Agent Readiness
Infrastructure` 内跨 Evidence 与 Evaluation 的 `Technical Semantic Role`；`Trust Claim`
是 Evidence 与 Evaluation Result 之间的 bounded semantic relation；OpenTelemetry 是可选
Observation Source，SAEE 提供限定范围的 Trust Semantic Interpretation。

状态：

```text
APPROVED_DESIGN_DIRECTION
```

范围：

```text
semantic_only=true
behavior_change=none
```

边界：

本记录不是新的 `Frozen Decision`，不改变 v1.1 authority，不创建 architecture layer、
product、capability、Object、Schema、MCP 或 implementation，也不授权 Truth、Authorization、
Security Certification、Compliance Proof、Production Readiness 或外部行动主张。

证据：

Phase 0.5.5B Trust Semantic Decision Packet、Phase 0.5.5C Alignment Synchronization Plan、
Phase 0.5.5D 明确人工批准指令。

---

## D-006

日期：

2026-07-15

主题：

V2 设计方向决策事实对齐与 Q-V2-001 关闭。

决定：

人工批准以下五项 transition design directions，并把其 Project Memory 状态从
`PROPOSED_FREEZE` 对齐为 `APPROVED_DESIGN_DIRECTION`：

- `V2-F-001` Identity Layer；
- `V2-F-002` GitHub Asset Relationship；
- `V2-F-003` ARO / SECO Direction；
- `V2-F-004` Product Family；
- `V2-F-005` Ecosystem Entry。

人工同时批准以下三项 constitutional principle design directions：

- `V2-P-001` Trust Semantic Principle；
- `V2-P-002` Agent Discoverability Principle；
- `V2-P-003` Complexity Encapsulation Principle。

状态：

```text
APPROVED_DESIGN_DIRECTION
```

问题关闭：

```text
question_id=Q-V2-001
previous_status=OPEN
resolution_status=RESOLVED_BY_HUMAN_DESIGN_APPROVAL
```

`Q-V2-001` 原问题是：是否批准 `V2 Authority and Term Crosswalk Decision Packet` 中
登记的五项 `PROPOSED_FREEZE` 建议。此前等待人类逐项确认分层身份、GitHub 资产关系、
ARO/SECO 术语、三个客户版本与 Autonomous 边界，以及组合式生态入口。本条记录保留该
历史问题和关闭依据；它从 active list 移出，不删除其历史。

范围：

```text
semantic_and_design_only=true
frozen_decision=false
active_authority=false
authority_switch=false
```

边界：

- `APPROVED_DESIGN_DIRECTION` 不等于 `FROZEN` 或 `ACTIVE_AUTHORITY`；
- v1.1 继续是唯一 active repository development authority；
- v2 继续 inactive，G1 继续 ineffective，Phase 0.5.7A 继续 unauthorized；
- 本决定不创建 v2 Constitution、authority family、schema、capability、MCP、product、
  runtime integration 或 ecosystem adoption；
- canonical capability facts、product facts、MCP facts、Evidence lineage 与现行主线不变。

证据：

- Phase 0.5.4 对 `V2-F-001..V2-F-005` 的明确人工批准及
  `governance/constitution-migration/README.md`；
- Phase 0.5.6F 对 `V2-P-001..V2-P-003` 的明确人工批准；
- `reports/SAEE_V2_CONSTITUTION_PRINCIPLE_CANDIDATE_REGISTRATION.md`；
- Phase 0.5.6G-1 明确授权执行 Decision Truth Alignment。

下一动作：

只允许进入 Pre-G1 下一批次的 human review。Migration baseline、immutable manifest、
role assignment、G1 reconfirmation、Commit A/B 与 authority switch 均未由本条授权。
