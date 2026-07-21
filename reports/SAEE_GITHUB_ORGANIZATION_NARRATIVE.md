# SAEE GitHub Organization Narrative

中文名称：SAEE GitHub 组织叙事<br>
版本：`v1.0`<br>
阶段：`PHASE_1_CATEGORY_POSITIONING`

```text
GITHUB_ROLE=UNIFIED_TECHNICAL_AND_AGENT_READABLE_ENTRY
NEW_GITHUB_PROJECT_ALLOWED=false
REPOSITORY_CONSOLIDATION_EXECUTED=false
CURRENT_FUTURE_SEPARATION_REQUIRED=true
```

## 1. 组织叙事

GitHub 对外应呈现一个统一项目：

> SAEE is building the evidence and interpretation foundations for Multi-Agent Long-Running Trust Infrastructure.

这句话中的 `is building` 表示研究与分阶段建设，不表示所有 Identity、State、Memory、Governance 能力已经实现。

所有仓库、历史模块与研究资产都必须围绕同一中心解释：它们是 SAEE 不同阶段、子系统或来源资产，而不是多个互不相关的产品。

## 2. GitHub 首屏顺序

推荐 README / profile 顺序：

1. Category statement；
2. Why long-running multi-agent systems need a trust layer；
3. Current Capability / Future Direction；
4. Architecture Overview；
5. Repository and asset map；
6. Quick evidence/readiness entry；
7. Roadmap and validation stages；
8. Standards and ecosystem composition；
9. Non-Claims；
10. Citation / contact / security。

不以内部 phase 编号、商业台账、实验数量或散落工具列表作为首屏信息。

## 3. 推荐的 GitHub 核心文案

### Title

`SAEE — Multi-Agent Long-Running Trust Infrastructure`

### One-line description

`Researching and building the evidence-to-trust foundations enterprises need to run multi-agent systems over long time horizons.`

### Plain-language explanation

`Agent frameworks help systems run. Observability helps teams see what happened. SAEE studies how identity, execution evidence, state continuity, memory provenance and governance can remain connected as agents collaborate and evolve over time.`

### Current boundary

`Today, SAEE provides bounded local evidence-readiness evaluation. It does not yet provide authenticated agent identity, trusted memory, longitudinal state continuity, autonomous governance or production trust authority.`

## 4. Architecture Overview 内容

目标文件建议：`docs/architecture/SAEE_MULTI_AGENT_TRUST_INFRASTRUCTURE_OVERVIEW.md`

本阶段只规划，不在本任务创建新的 architecture authority 或 capability contract。

Overview 应包括：

### Project Position

- 类别定义；
- 企业问题；
- SAEE 与 framework、observability、IAM、policy 的关系。

### Architecture Diagram

```text
Agent Frameworks / Cloud Agent Platforms
                  ↓
        A2A / MCP / Runtime Events
                  ↓
 Identity / Delegation / Telemetry / Evidence
                  ↓
        SAEE Trust Interpretation
                  ↓
      IAM / Policy / Human Authority
```

图中 SAEE 节点标记 `FUTURE ARCHITECTURE DIRECTION`。

### Capability Layers

1. Agent Identity；
2. Agent Execution Evidence；
3. Agent State Continuity；
4. Agent Memory Trust；
5. Multi-Agent Governance；
6. Trust Decision Context。

### Current Implementation Status

必须直接投影 canonical inventory，不手工创造第二套状态：

- implemented：`saee.evaluate_agent_run`、`saee.evaluate_evidence`、bounded synthetic mapping；
- partial：general repository-defined trace normalization；
- design_only：`saee.rehearse_agent`；
- missing：OTLP ingestion、trusted trace conversion、external identity binding、delegation binding。

### Roadmap

使用研究门和证据门，不使用无授权的 PR/implementation 承诺：

1. category and problem validation；
2. cross-runtime evidence semantics research；
3. independent decision-value validation；
4. standards composition and ecosystem experiments；
5. only then implementation proposal and authorization。

## 5. Repository / Asset Narrative

GitHub 叙事不应把多个仓库包装成已经完成的统一 runtime。建议按职责表达：

| Surface | Narrative role | Truth rule |
|---|---|---|
| SAEE main repository | constitutional project, canonical capability inventory and current bounded evaluation | canonical current facts |
| Agent Evidence Project assets | Evidence and Immune Subsystem source/integration lineage | ownership does not mean source/runtime migration completed |
| research repositories/assets | scientific and design inputs | research/probe != production capability |
| website | category and discovery surface | deployment != product launch |
| marketplace/cloud materials | ecosystem preparation | draft/review != approved/listed/adopted |

外部 README 应从 canonical registry 生成或引用仓库关系，不通过营销文案宣布代码已合并。

## 6. Current Capability / Future Direction 模板

```markdown
## Current Capability

- Local deterministic evaluation of declared run evidence readiness.
- Closed local evidence-bundle adequacy checks.
- Bounded reason codes and explicit missing-evidence output.
- Recommendation only; no deployment authorization.

## Future Direction

- Authenticated Agent Identity continuity.
- Trusted Execution Evidence across runtimes.
- Longitudinal Agent State and Memory continuity.
- Multi-Agent Governance and responsibility context.
- Standards-composable Trust Decision Infrastructure.

Future Direction is not current implementation, customer validation, or production readiness.
```

## 7. Developer Discovery Path

建议路径：

`README → Architecture Overview → Current Capability table → for-agents / llms.txt → canonical manifest → examples/tests`

Agent 应在两次以内的文件跳转中找到：

- 当前能调用什么；
- 什么尚未实现；
- 输入输出证据在哪里；
- 是否生产就绪；
- Future Direction 的研究文档在哪里；
- 哪个 authority 能批准能力事实变化。

## 8. GitHub 内容治理

- Capability facts 只来自 canonical inventory；
- roadmap advice 不写回 capability ledger；
- historical `recommended_next_pr` 不作为当前行动；
- website、README、profile 和 architecture overview 必须使用相同 category label；
- future capability 必须带 `Future Direction`；
- `local`, `synthetic`, `public`, `customer_validated`, `production_ready` 分开；
- 不新增 GitHub 项目或平行仓库；
- 不在本阶段重命名 repository 或执行代码迁移。

## 9. 对外证据层级

```text
Level 0: Research hypothesis
Level 1: Agent-readable contract/design
Level 2: Local implementation
Level 3: Synthetic/local validation
Level 4: External interoperability evidence
Level 5: Customer validation
Level 6: Production readiness
```

任何 README badge、status table 或 roadmap 只能使用有直接证据的层级。

## 10. 完成标准

- 项目描述统一为 Multi-Agent Long-Running Trust Infrastructure；
- Architecture Overview 可在 GitHub 首屏两次点击内到达；
- Current / Future 清楚分栏；
- repository roles 清楚但不虚构 migration；
- agent-readable entry 可发现；
- 不创建新 repo，不改变 capability、MCP 或 release status。
