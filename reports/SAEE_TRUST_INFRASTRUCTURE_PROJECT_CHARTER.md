# SAEE Multi-Agent Long-Running Trust Infrastructure Project Charter

中文名称：SAEE 多智能体长期运行可信基础设施项目章程<br>
文件标识：`SAEE_TRUST_INFRASTRUCTURE_PROJECT_CHARTER.md`<br>
章程版本：`v1.0`<br>
项目状态：`FUTURE_RESEARCH_PROJECT`<br>
所属项目：`SAEE`<br>
当前主线替代：`false`<br>
当前能力实现：`false`<br>
生产能力创建：`false`

## 1. 项目使命

本项目的使命，是研究未来企业如何为长期自主运行、跨 Agent 协作、跨会话延续的
多智能体系统建立可信基础设施，使企业能够在不把一次授权扩大为无限授权、不把运行
记录误认为可信事实的前提下，理解并验证：

- 哪个 Agent 或 Agent 版本正在行动；
- 当前行动继承了什么目标、权限和责任；
- Agent 状态与记忆如何延续、变化或失效；
- 多 Agent 协作过程产生了什么可复核证据；
- 状态变化是否仍处于原始目标和授权边界内；
- 当系统发生偏移、冲突或证据不足时，谁有权判断、暂停或重新授权。

本项目以增强 `Agent 长期可信运行能力` 为唯一成立条件。不能明确增强该能力的研究
方向，不进入本项目的默认优先级。

本项目不是当前 `SAEE Evaluation` 功能开发，不是日志系统，不是单 Agent 工具，
也不是安全扫描工具。

## 2. 核心问题定义

长期多智能体系统的核心风险，不只是某次回答错误，而是错误身份、错误目标、错误状态
或错误记忆在长时间运行和 Agent 间协作中持续传播，并逐渐失去可定位、可解释和可归责
的边界。

本项目研究的核心问题是：

> 如何在 Agent、runtime、会话、任务和组织边界持续变化的条件下，保持身份连续性、
> 目标连续性、状态连续性、记忆可信性、执行可追溯性和责任可证明性？

该问题包含六个相互依赖的研究维度：

1. **身份连续性**：能否持续确认行动主体，以及主体、版本、角色或控制权是否发生变化。
2. **目标连续性**：能否区分目标的合法继承、明确修订、局部优化和未经授权的目标替换。
3. **状态连续性**：能否解释状态从何而来、为何变化、由谁改变，以及变化是否处于允许范围。
4. **记忆可信性**：能否识别记忆的来源、适用范围、时效、冲突、污染和失效条件。
5. **执行可追溯性**：能否重建跨 Agent 的关键决策、行动、交接和证据关系，而不只记录调用顺序。
6. **责任可证明性**：能否证明某项行动依据了什么委托、由哪个主体承担何种责任，以及何时需要人类权力介入。

普通日志、trace 或 checkpoint 可以成为观察输入，但不能单独证明身份真实性、目标有效性、
状态合法性、记忆可靠性或责任归属。因此，本项目研究的是这些对象之间的可信关系，而不是
增加更多运行记录。

## 3. 未来架构假设

以下内容是待验证的未来架构假设，不是当前 SAEE 能力声明。

### 3.1 连续信任链假设

企业能够放心扩大 Agent 自主权限的前提，是形成一条跨时间、跨 Agent 的连续信任链：

`Identity → Goal → State → Memory → Action → Evidence → Governance`

这条链必须能够说明每次关键状态变化的主体、依据、边界、证据和责任，而不能只说明事件
发生过。

### 3.2 有界状态转移假设

长期可信运行的最小判断对象不是单条日志、单次请求或最终答案，而是有界状态转移：

- 转移前的可知状态；
- 当前仍有效的目标和委托；
- 触发变化的行动或新证据；
- 转移后的可知状态；
- 对变化的解释、限制和责任归属。

若任一关键关系缺失，系统应保留 `unknown`、`insufficient_evidence` 或
`human_review_required`，而不是把可观察性自动升级为可信性。

### 3.3 多来源证据组合假设

长期可信判断不会由单一 framework、日志平台、身份系统或策略引擎独立完成。未来基础设施
需要组合运行观察、身份与委托、状态与记忆来源、证据完整性以及治理决定，同时保留每个来源
的责任边界。

### 3.4 解释与授权分离假设

可信基础设施可以诊断、解释、比较并提出建议，但不因掌握证据而自动获得授权权力。
`Recommendation` 不等于 `Authorization`；责任判断也不等于自动执行、处罚或回滚。

### 3.5 标准组合而非协议替代假设

未来更可能形成跨身份、委托、遥测、证据和治理标准的组合剖面，而不是由 SAEE 创造并控制
新的通用 transport、身份协议或 Agent runtime。SAEE 的潜在位置是受限的可信解释层，
不是替代现有基础设施。

## 4. 核心对象

### 4.1 Agent Identity（智能体身份）

表示可被持续区分和引用的 Agent 主体、版本、角色及其控制边界。

研究问题包括身份如何建立、继承、轮换、撤销和跨系统关联。调用方声明的 `agent_id` 不等于
经过外部认证的 Agent Identity；身份存在也不自动证明授权有效。

### 4.2 Agent State（智能体状态）

表示在特定时间点可观察、可引用的运行状态，以及状态之间的变化关系。

研究范围关注可观察 operational state、权威基线、允许变化、状态来源和转移解释；不声称
能够读取或证明模型内部 latent state（潜在状态）。

### 4.3 Agent Memory（智能体记忆）

表示影响未来判断或行动的持久化信息、摘要、检索结果、经验和共享记忆。

研究问题包括记忆来源、适用范围、时效、版本、冲突、继承、污染、撤销和遗忘。记忆被保存
不等于记忆真实，记忆被检索也不等于当前仍可适用。

### 4.4 Agent Evidence（智能体证据）

表示用于支持或反驳身份、状态、记忆、行动、结果和责任主张的可复核材料及其来源关系。

Evidence 不等于 log，不等于未经认证的声明，也不等于授权。未来研究关注证据如何与具体主张、
主体、时间、状态转移和委托范围绑定。

### 4.5 Agent Governance（智能体治理）

表示对多 Agent 长期行为进行边界设定、例外处理、责任分配、人工复核和重新授权的规则与权力
关系。

治理不等于 SAEE 自动控制外部世界。SAEE 可以研究治理所需的解释和证据条件，但人类或外部
权威系统仍保留重大行动、权限扩大、责任裁决和生产执行的最终权力。

## 5. 与当前 SAEE 主线关系

本项目是 SAEE 主项目下的未来研究项目，不是新项目、平行产品或当前工程主线的替代物。

当前 SAEE program mainline 仍是：

`Agent Evidence Integration → SAEE Evaluation → Agent Readiness`

本项目与当前主线的关系如下：

- 当前主线提供受限的 evidence、evaluation 和 readiness 经验，作为未来研究输入；
- 本项目不得反向扩大当前 `saee.evaluate_agent_run` 的语义或能力主张；
- 本项目不得把未来的 Identity、State、Memory 或 Governance 研究写成当前 canonical capability；
- 本项目不得修改当前 MCP、Schema、代码、产品状态或发布路线；
- 本项目产生的架构假设、研究问题和商业假设，必须经过独立验证后才能申请进入工程决策；
- 任何未来实施仍需重新执行 canonical capability inventory、duplicate-build check、
  Agent Recommendation Gate、evolution subsystem check 和明确授权。

当前能力边界保持不变：现有 `saee.evaluate_agent_run` 只支持本地、受限、声明式 evidence
readiness 判断；它不认证 trace，不提供完整 Agent Identity binding，不判断长期目标连续性，
也不授权部署或外部行动。

```text
PROJECT_RELATIONSHIP=FUTURE_RESEARCH_UNDER_SAEE
PROGRAM_MAINLINE_CHANGED=false
CURRENT_SAEE_REPLACED=false
CURRENT_EVALUATION_SCOPE_EXPANDED=false
CURRENT_CAPABILITY_FACTS_CHANGED=false
MAINLINE_DRIFT_DETECTED=false
```

Agent Recommendation Gate：

```text
RESEARCH_PROJECT_RECOMMENDATION=conditional
COMPLETE_CUSTOMER_PRODUCT_RECOMMENDATION=do_not_recommend
```

`conditional` 仅表示该问题值得继续研究；不表示已经证明客户需求、技术可行性、商业价值或
生产适用性。如果潜在客户今天要求完整的多智能体长期运行可信基础设施，当前不得推荐 SAEE
作为已完成解决方案。

## 6. Non-Claims（不承诺事项）

本章程不声称当前 SAEE 已经实现：

- 完整 Agent 状态管理；
- 连续或跨 Agent 的状态完整性判断；
- Agent Memory 真实性验证；
- 外部 Agent Identity 认证与绑定；
- 端到端委托链验证；
- Goal、Context 或 Plan 的长期连续性评估；
- Autonomous Governance（自主治理）；
- 自动审批、自动处罚或自动回滚；
- 法律、合规或组织责任的最终判定；
- 面向客户的生产级 Multi-Agent Long-Running Trust Infrastructure。

本章程也不授权：

- 修改现有 SAEE 代码；
- 修改 MCP；
- 创建或修改 Schema；
- 创建新的生产能力；
- 创建新的 GitHub 项目或平行仓库；
- 合并、替代或重新排序当前工程主线；
- 使用客户数据、扩大权限、部署生产系统或作出重大公开声明。

```text
FULL_STATE_MANAGEMENT_IMPLEMENTED=false
AUTONOMOUS_GOVERNANCE_IMPLEMENTED=false
RESPONSIBILITY_DETERMINATION_IMPLEMENTED=false
EXTERNAL_IDENTITY_BINDING_IMPLEMENTED=false
TRUSTED_MEMORY_IMPLEMENTED=false
LONGITUDINAL_MULTI_AGENT_INTEGRITY_IMPLEMENTED=false
CODE_CHANGED=false
MCP_CHANGED=false
SCHEMA_CHANGED=false
NEW_PRODUCTION_CAPABILITY_CREATED=false
PROGRAM_MAINLINE_MERGED=false
CUSTOMER_VALIDATED=false
PRODUCTION_READY=false
```
