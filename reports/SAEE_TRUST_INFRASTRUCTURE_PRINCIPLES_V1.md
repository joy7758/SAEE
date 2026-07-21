# SAEE Trust Infrastructure Principles v1

中文名称：SAEE 可信基础设施原则 v1<br>
阶段：`PHASE_3_TRUST_PRINCIPLES_DEFINITION`<br>
文档类型：`PUBLIC_CATEGORY_PRINCIPLES_STATEMENT`<br>
文档状态：`FUTURE_DIRECTION_RESEARCH_DRAFT`<br>
日期：`2026-07-17`

```text
CATEGORY=MULTI_AGENT_LONG_RUNNING_TRUST_INFRASTRUCTURE
PRINCIPLES_VERSION=1.0
PRINCIPLE_COUNT=6
CURRENT_AUTHORITY=SAEE_DEVELOPMENT_CONSTITUTION_V1.1
THIS_DOCUMENT_IS_CURRENT_CONSTITUTION=false
THIS_DOCUMENT_IS_CODE_SPECIFICATION=false
THIS_DOCUMENT_IS_PRODUCT_COMMITMENT=false
FUTURE_ARCHITECTURE_IS_CURRENT_CAPABILITY=false
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
MAINLINE_DRIFT_DETECTED=false
```

## 0. Principle Declaration

未来的企业 Agent 不再只是完成一次短任务。它们会长期运行、持有记忆、改变状态、接受委托、
调用工具，并与其他 Agent 共同影响业务结果。

在这种环境中，可信不能被压缩成一次认证、一次测试、一个 dashboard 或一个总分。

> **SAEE Trust Principles：长期可信必须围绕具体 claim，在时间变化中持续解释 Evidence、State、
> Delegation 与 Authority 之间的关系。**

这组原则定义 `Multi-Agent Long-Running Trust Infrastructure` 的思想边界。它不描述一个当前已经
实现的 SAEE 产品，也不改变当前 SAEE 工程主线、能力清单、宪法或发布路线。

## 1. Principles at a Glance

| # | Principle | 核心问题 | 一句话结论 |
|---|---|---|---|
| 1 | **Trust Continuity Principle** | 信任能否跨时间延续？ | 信任前提变化后必须重新解释，不能永久继承一次认证或测试结果。 |
| 2 | **Evidence-Reality Separation Principle** | 证据究竟证明什么？ | Evidence 支持有限 claim，但不自动等于 Reality、事实全貌或责任结论。 |
| 3 | **Interpretation-Authority Separation Principle** | 可信解释能否直接产生权力？ | 解释、评分和建议不得自动变成授权、执行或责任裁决。 |
| 4 | **Infrastructure Composition Principle** | 是否需要替代现有基础设施？ | 可信基础设施应组合 OTel、SPIFFE、SCITT、MCP、A2A 等生态，而不是复制它们。 |
| 5 | **Claim-Scoped Trust Principle** | 我们具体相信什么？ | 可信判断必须绑定明确 claim，不能用一个总分代表系统整体可信。 |
| 6 | **Human Authority Boundary Principle** | 重大行动最终由谁决定？ | 权限扩大、责任认定和生产变更必须保留人类或独立外部权威。 |

## 2. SAEE Trust Principles Map

```text
                    Trust Continuity
                           |
                           |
       Evidence -------- Claim -------- Authority
                           |
                           |
                 Governance Boundary

       Evidence: Evidence-Reality Separation
          Claim: Claim-Scoped Trust
      Authority: Interpretation-Authority Separation
     Continuity: Trust Continuity
       Boundary: Human Authority Boundary

     Infrastructure Composition surrounds the map:
       OTel + SPIFFE + SCITT + MCP + A2A + existing enterprise systems
```

这张图表达六条原则之间的依赖关系：

- `Trust Continuity` 决定 claim 是否仍能跨时间成立；
- `Evidence` 只能在其来源、覆盖与限制内支持 claim；
- `Claim` 是可信判断的最小语义单位；
- `Authority` 与解释分离，不能由可信结论自动生成；
- `Governance Boundary` 决定何时必须暂停、复核或重新授权；
- `Infrastructure Composition` 提供身份、遥测、声明、连接与协作信号，但不被 SAEE 替代。

## 3. Principle 1 — Trust Continuity Principle

中文名称：**可信连续性原则**

### 一句话定义

长期运行 Agent 的可信不是一次认证；身份、时间、状态、目标、委托或记忆发生实质变化后，
先前的可信判断必须被重新解释。

### 为什么重要

短任务通常把身份、目标、状态和人类监督压缩在一个较小时间窗口内。长期多 Agent 系统则会
经历版本更新、角色轮换、handoff、状态分叉、记忆写入、目标修订和组织政策变化。即使每次
局部行动都看似正常，原始信任关系也可能已经失效。

可信连续性要求持续回答：

- 当前行动主体与最初被信任的主体是什么关系；
- 当前目标是否仍继承有效授权；
- 状态变化是否可解释、被允许且未产生未解决分叉；
- 当前使用的记忆是否仍有来源、时效和适用范围；
- 委托范围是否被保持、修订、撤销或扩大。

### 防止什么错误方向

- 把一次测试通过写成永久可信；
- 把初始 authentication 写成持续行为可信；
- 无条件继承旧目标、旧权限、旧状态和旧 evidence；
- 把 state、memory 或 delegation drift 当作普通运行噪音；
- 用 uptime 或任务成功率替代信任连续性。

### 与现有生态关系

Agent Framework、checkpoint、memory store、IAM 和 A2A task state 可以提供变化信号；它们不因
保存了状态或维持了连接就自动证明可信连续。未来 SAEE 的候选职责是解释这些变化对具体 claim
的影响，而不是接管 runtime 或状态存储。

## 4. Principle 2 — Evidence-Reality Separation Principle

中文名称：**证据与现实分离原则**

### 一句话定义

Evidence 在明确来源、覆盖、时间和适用范围内支持或反驳 claim；Evidence 不等于 Reality。

### 为什么重要

日志、trace、签名、receipt、evaluation 和人工记录都只是对现实的部分观察或声明。它们可能
存在采样、缺失、错误映射、生产者偏差、时钟差异、过期内容或错误声明。证据数量增加，不会
自动消除这些限制。

因此，可信判断必须同时保留：

- 证据由谁产生、如何取得；
- 哪些事件和时间范围被覆盖；
- 哪些关键关系缺失或无法验证；
- 是否存在反证、冲突或后续修订；
- 证据能够支持什么，以及明确不能支持什么。

### 防止什么错误方向

- `log = fact`；
- `trace = responsibility`；
- `signature = truth`；
- `receipt = correctness`；
- `evaluation pass = production trust`；
- 用 evidence volume 掩盖 evidence adequacy。

### 与现有生态关系

OpenTelemetry 提供遥测语义与传输基础，SCITT 提供可验证声明与透明历史，Observability 平台
提供查询、关联和评估。它们都是重要 evidence infrastructure；SAEE 不否定也不替代它们，而是
保留其来源边界，解释它们是否足以支持某个有限 claim。

## 5. Principle 3 — Interpretation-Authority Separation Principle

中文名称：**解释与权力分离原则**

### 一句话定义

可信解释、evidence adequacy、risk signal、readiness 或 recommendation 只能形成决策上下文，
不能自动成为授权、执行或责任裁决。

### 为什么重要

如果同一系统既解释证据、又授予权限、执行动作并批准自身结果，就会形成自证、自授权和责任
集中。长期运行 Agent 的复杂性越高，越需要让“我们为什么相信或不相信”与“谁有权采取行动”
保持独立、可复核的关系。

### 防止什么错误方向

- trust score 直接触发不可逆外部动作；
- evaluator 自动批准自己的变更；
- recommendation 被描述为 authorization；
- 技术 evidence 被升级为法律、合规或组织责任裁决；
- 可信解释层演变为未经授权的 Policy Engine 或 control plane。

### 与现有生态关系

IAM 负责身份与访问权，Policy Engine 负责规则决策与执行，Governance Platform 负责组织控制，
Human Authority 负责重大授权与责任决定。未来 SAEE 可以向这些系统提供有限解释，但不取得它们
的权力。

## 6. Principle 4 — Infrastructure Composition Principle

中文名称：**基础设施组合原则**

### 一句话定义

SAEE 未来可信基础设施方向应组合现有身份、遥测、透明声明、连接和 Agent 通信标准，而不是
重新发明或替代它们。

### 为什么重要

长期可信依赖多个独立事实来源，没有一个系统能够可靠承担全部职责。开放、可组合的基础设施
允许企业保留既有投资，也允许来源、解释与权力相互制衡。私有平行协议会增加接入成本、制造
不可验证边界，并把类别主张误变成协议占有。

组合关系包括但不限于：

| Existing infrastructure | 它提供什么 | 它不被要求提供什么 |
|---|---|---|
| OpenTelemetry | trace、log、metric、event 的遥测语义与传输 | 最终 trust judgment |
| SPIFFE / SPIRE | workload identity、credential 与 trust domain | 目标、状态和记忆连续性 |
| SCITT | signed statement、receipt、provenance 与透明历史 | 声明内容必然真实 |
| MCP | Agent 与 tool/resource 的连接和授权传输 | 长期可信判断 |
| A2A | Agent discovery、communication、delegation 与 task lifecycle | 跨 Agent 责任和状态完整性证明 |

### 防止什么错误方向

- 创建平行的 telemetry、identity、transport 或 Agent communication 协议；
- 把内部 Schema 宣称为行业标准；
- 为类别占位而复制 OTel、SPIFFE、SCITT、MCP 或 A2A；
- 通过封闭格式制造 lock-in；
- 忽略来源系统本身的真实性、完整性和适用性限制。

### 与现有生态关系

SAEE 的候选位置是 `bounded trust interpretation`：向上组合现有基础设施的事实与证据，向下为
Governance、Policy 和 Human Authority 提供 claim-scoped context。组合优先不代表已经完成任何
集成，也不授权修改现有协议。

## 7. Principle 5 — Claim-Scoped Trust Principle

中文名称：**有限主张可信原则**

### 一句话定义

任何可信判断都必须先回答“相信什么”，并把结论限制在该 claim 的主体、行动、时间、状态和
证据边界内。

### 为什么重要

Agent 可能在一个维度可信、在另一个维度未知或不可信。例如：工作负载身份可以被认证，但其
目标继承尚未证明；执行 trace 可以完整，但共享记忆来源不明；某次工具调用符合权限，却超出
当前业务委托。一个整体 trust score 会压平这些差异。

可接受的可信表达应类似：

> 现有 evidence 在时间窗口 T 内支持 Agent A 按 Delegation D 执行动作 X 的 claim；它不支持
> Memory M 的真实性、后续状态 S2 的合法性或责任主体 R 的最终认定。

### 防止什么错误方向

- 一个总分代表全部可信；
- 把 identity trust 扩张为 behavior trust；
- 把 action success 扩张为 goal alignment；
- 把局部 evidence coverage 扩张为端到端责任证明；
- 隐藏 `unknown`、`insufficient_evidence` 和反证。

### 与现有生态关系

Observability、evaluation、identity、policy 和 transparency systems 可以分别提供 claim input。
SAEE 的候选差异不是创造更大的分数，而是明确 claim、证据适用性、不确定性和 non-claims，
让下游系统能够知道一个结论可以怎样使用。

## 8. Principle 6 — Human Authority Boundary Principle

中文名称：**人类权力边界原则**

### 一句话定义

权限扩大、责任认定、生产变更及其他重大行动，必须保留人类或独立外部权威的明确决定权。

### 为什么重要

Interpretation-Authority Separation 规定可信结论不能自行产生权力；Human Authority Boundary
进一步规定重大权力必须落在哪里。长期多 Agent 系统会跨越多个团队、系统、合同和法律边界，
技术解释无法独立拥有这些组织或法律权力。

至少以下行动不得仅由 SAEE 可信解释自动完成：

- 扩大 Agent、用户、workload 或工具权限；
- 生产部署、生产配置修改、不可逆数据变更或外部执行；
- 最终认定个人、组织或 Agent 的法律与合规责任；
- 解除风险限制、批准例外或跳过 required review；
- 将研究结论升级为客户、生产或监管事实。

### 防止什么错误方向

- 把“人类可监督”写成“系统已获授权”；
- 由同一 Agent 生成、评估并批准重大变更；
- 以自动化效率为理由取消责任主体；
- 把告警、暂停建议或 reauthorization request 当作最终决定；
- 让未来 Trust Infrastructure 取代企业治理和法律权威。

### 与现有生态关系

Human Authority 可以通过企业 IAM、GRC、change management、Policy Engine、审批系统或监管程序
表达。SAEE 不规定企业必须采用哪一种治理产品；它只要求重大权力来源独立、可识别、可追溯，
并且不能由可信解释层自行伪造。

## 9. 六条原则与四层参考架构

| Reference Architecture | 主要回答 | 直接约束它的原则 |
|---|---|---|
| Agent Identity Layer | `Who is acting?` | Trust Continuity、Infrastructure Composition、Claim-Scoped Trust |
| Agent Execution Evidence Layer | `What happened?` | Evidence-Reality Separation、Claim-Scoped Trust |
| Agent State Continuity Layer | `Is it still the same trusted state?` | Trust Continuity、Evidence-Reality Separation |
| Multi-Agent Governance Layer | `Who decides?` | Interpretation-Authority Separation、Human Authority Boundary |
| Bounded Trust Interpretation Plane | 现有信号是否仍支持下一步 | 六条原则共同约束 |

这张映射不增加第五个架构层，也不把 `Bounded Trust Interpretation Plane` 变成 authority。它只是
说明六条原则如何约束四层之间的可信解释关系。

## 10. 为什么企业需要这些原则

### 10.1 长期运行需要新的可信模型

企业对单次 Agent 调用的信任，可以主要依赖访问控制、测试、监控和人工复核。长期多 Agent
系统则会让信任前提持续变化：身份轮换、目标调整、状态分叉、记忆污染、委托扩张和 Agent
handoff 会把一次局部错误传播为长期系统行为。

企业真正缺少的不是“是否看见一次调用”，而是：

> 经过这些变化后，最初允许 Agent 行动的前提是否仍然成立？

Trust Continuity、Claim Scope 和 Human Authority Boundary 共同提供一种比“认证一次、长期默认”
更适合长期 Agent 的可信模型。

### 10.2 为什么日志、监控和治理仍然不足

| Existing capability | 能回答 | 不能单独回答 |
|---|---|---|
| Logs / traces | 记录或观察到什么 | 记录是否完整、真实且足以支持目标 claim |
| Observability | 系统怎样运行、哪里异常 | 身份、目标、状态、记忆和委托是否持续可信 |
| IAM | 谁可以访问什么 | 获得权限的 Agent 是否仍按原始信任前提行动 |
| Policy Engine | 当前属性下是否 allow/deny | 输入状态、目标和证据本身是否仍有效 |
| Governance Platform | 谁制定规则、如何控制和复核 | 多来源 evidence 是否足以证明跨时间连续性 |

这些基础设施不是失败，而是职责不同。SAEE Trust Principles 要求它们保持各自权力，同时通过
Evidence、Claim、Continuity 和 Authority 的明确关系形成更完整的决策上下文。

### 10.3 为什么 SAEE 不是安全工具

安全工具通常回答漏洞、攻击、恶意行为、访问违规或配置风险。未来 SAEE 可信基础设施方向关注
的是更广的关系问题：即使身份真实、系统无已知漏洞、调用符合权限，经过长期状态、记忆、目标
和委托变化后，现有 evidence 是否仍支持某个明确的 trust claim。

因此，SAEE 不替代 Security Scanner、IAM、SIEM、Policy Engine 或 Governance Platform。它的
未来类别方向是**可信解释基础设施**，不是安全扫描、执行控制或责任裁决工具。

## 11. Public Communication Form

以下表述可用于未来官网、白皮书、生态交流、云厂商沟通和学术讨论，但必须同时保留
`FUTURE_DIRECTION_ONLY` 边界：

> Framework 让 Agent 运行，Observability 让企业看见，IAM 让主体获得访问权，Policy Engine
> 执行规则；Multi-Agent Long-Running Trust Infrastructure 解释这些信号是否仍共同支持 Agent
> 的下一步。

> Evidence supports a claim. Evidence is not reality.

> Trust across time requires continuity, not a permanent score.

> Trust interpretation informs authority; it does not become authority.

这些句子是类别原则，不是当前 capability、客户验证、生产就绪或市场采用声明。本文创建本地
可引用材料，不表示已经完成官网发布、白皮书发布或任何对外传播。

## 12. Source Materials

本文只压缩以下既有 SAEE 未来研究材料，不新增竞争研究或工程设计：

1. [SAEE_TRUST_INFRASTRUCTURE_PROJECT_CHARTER.md](./SAEE_TRUST_INFRASTRUCTURE_PROJECT_CHARTER.md)
2. [SAEE_TRUST_INFRASTRUCTURE_REFERENCE_ARCHITECTURE.md](./SAEE_TRUST_INFRASTRUCTURE_REFERENCE_ARCHITECTURE.md)
3. [SAEE_TRUST_INFRASTRUCTURE_COMPETITIVE_LANDSCAPE.md](./SAEE_TRUST_INFRASTRUCTURE_COMPETITIVE_LANDSCAPE.md)
4. [SAEE_CONSTITUTION_PRINCIPLES_CANDIDATES.md](./SAEE_CONSTITUTION_PRINCIPLES_CANDIDATES.md)

## 13. Non-Claims

本文不声称当前 SAEE 已经实现：

- Multi-Agent Long-Running Trust Infrastructure；
- 完整 Agent Identity、State、Memory 或 Goal continuity；
- 外部可信 identity/delegation binding；
- 自动 governance、reauthorization 或责任判定；
- OTel、SPIFFE、SCITT、MCP 或 A2A 集成；
- 面向客户的生产能力、商业 offer、生态采用或行业标准地位。

本文不修改或授权修改：

- `SAEE Development Constitution v1.1`；
- 当前 canonical capability inventory；
- 现有代码、MCP、Schema、API、服务或测试；
- 当前 SAEE mainline、产品路线、发布计划或 GitHub 项目。

## 14. Final Boundary Check

```text
PRINCIPLE_COUNT=6
PUBLIC_PRINCIPLES_DEFINED=true
PUBLICATION_EXECUTED=false
THIS_DOCUMENT_IS_CURRENT_CONSTITUTION=false
CURRENT_CONSTITUTION_UNCHANGED=true
CURRENT_CAPABILITY_UNCHANGED=true
FUTURE_DIRECTION_ONLY=true
CURRENT_SAEE_MAINLINE_UNCHANGED=true
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
CODE_CHANGED=false
MCP_CHANGED=false
SCHEMA_CHANGED=false
NEW_PRODUCTION_CAPABILITY_CREATED=false
NEW_GITHUB_PROJECT_CREATED=false
SAEE_TRUST_INFRASTRUCTURE_IMPLEMENTED=false
CUSTOMER_VALIDATED=false
PRODUCTION_READY=false
```
