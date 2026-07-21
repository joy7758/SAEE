# AI Agent Governance Intelligence Sync — 2026-07-20

```text
sync_id=SAEE_AI_AGENT_GOVERNANCE_INTELLIGENCE_SYNC_2026_07_20
source_brief_date=2026-07-20
sync_status=COMPLETE
overall_decision=ADOPT_VERIFIED_DELTAS_AS_LEGAL_STANDARDS_AND_RISK_REFERENCE_ONLY
new_capability_required=false
new_competitive_report_required=false
runtime_change=NONE
schema_change=NONE
mcp_change=NONE
product_change=NONE
constitution_change=NONE
mainline_change=NONE
external_action_authorized=false
legal_compliance_claim_authorized=false
standards_submission_authorized=false
paper_submission_authorized=false
production_ready=false
```

## 1. 同步结论

本批简报包含三类值得采纳的增量：ITU-T SG17（国际电信联盟电信标准化部门第 17
研究组）的已公布会议路径、EU AI Act Article 50（欧盟《人工智能法》第 50 条）的近期
适用节点，以及 OWASP B1–B4（开放全球应用安全项目 B1–B4 信任边界）和 AIVSS v0.8
（智能体漏洞严重度评分系统 v0.8）的风险语言。

采纳仅限 legal / standards / risk reference（法律、标准与风险参考）和候选任务；不产生
新的 capability（能力）事实，不改变 Phase 0.5 主线，也不授权实现、合规宣传、标准
投稿、论文投稿、会议联络、commit、push 或 PR。

附件中的三处表达需要收紧：

1. 2026-09-17 纽约加远程会议是 Q10/17、Q1/17 与 JCA-IdM 的 interim Rapporteur
   Group meeting（临时报告人组会议），不是 FG-TIDA 第一次会议；第一次会议暂列为
   2026 年 11 月巴黎，状态为 TBC（待确认）。
2. Article 50 主要规定人机交互告知及合成内容标记/披露，不能扩张为完整的智能体运行
   审计要求，也不能由此声称 SAEE 已满足 EU AI Act（欧盟《人工智能法》）。
3. DAI 2026 Research Track（分布式人工智能 2026 研究赛道）日期真实，但官方说明
   部分作者可能需要 APC（文章处理费）；当前也没有已核验的完整 8 页论文与实验包，
   因而继续保持 `hold_current_cycle`。

## 2. 防重复建设与路由

```text
existing_itu_route=SI-015
existing_otel_route=SI-016
existing_owasp_asi_route=SI-017
existing_dai_route=SI-020
new_article_50_route=SI-029
new_owasp_trust_boundary_route=SI-030
new_aivss_route=SI-031
new_competitive_report_required=false
```

OpenTelemetry GenAI semantic conventions（开放遥测生成式人工智能语义约定）中的
Schema URL TODO（模式网址待办）与 7 月 16 日记录相同，不构成新 delta（增量），继续
由 `SI-016` 观察。ITU 时间表扩展 `SI-015`；DAI 日期与费用边界扩展 `SI-020`，不新增
投稿任务。

## 3. 经核验的增量与边界

### 3.1 ITU-T SG17 / FG-TIDA：会议路径可跟踪，参与和提交未授权

ITU 官方 2026 年 6 月会议总结确认：FG-TIDA（分布式智能体可信身份焦点组）主席来自
Thales，副主席来自 Huawei；2026 年 11 月巴黎第一次会议仍为 TBC；2027-01-18—29
日内瓦窗口包含 workshop（研讨会）、第二次焦点组会议和 SG17 全会。2026-09-17
纽约加远程场次属于 interim Rapporteur Group meeting，议题包括 “Trust and agentic AI”
（信任与智能体人工智能）和 “Future work for IdM Roadmap”（身份管理路线图未来工作）。

这些日期提供 observation route（观察路径），不等于征稿、正式 liaison（联络）邀请、
SAEE 参与资格或提交授权。当前只准备内部术语与证据问题清单；不起草 contribution
（标准提案），不联系主席团。

### 3.2 EU AI Act Article 50：建立法律评审输入，不建立“合规能力”

European Commission AI Act Service Desk（欧盟委员会《人工智能法》服务台）说明，
AI agents（人工智能智能体）不是单独法律类别；具体义务取决于系统是否落入 AI system
或 GPAI model（通用人工智能模型）定义及其预定用途。自 2026-08-02 起，面向自然人
交互或生成内容的系统可能触发 Article 50 透明度义务；同日起，委员会对先进 GPAI
模型提供方的相关执法权开始适用，官方 FAQ（常见问题）列出最高可达全球年营业额 3%
的罚款边界。该 3% 说明属于 FAQ 的 GPAI 提供方执法段落，不应写成 Article 50 的
自动罚则。

Article 50 的直接文本覆盖：告知自然人正在与 AI 交互、以机器可读方式标记合成内容，
以及对 deepfake（深度伪造）和某些公共利益文本进行披露。它没有自动证明“每一次智能体
行动都必须由 SAEE 式证据包审计”，也没有把 SAEE 变成法律合规判定器。

当前未建立的事实包括：

```text
qualified_legal_interpretation=NOT_ESTABLISHED
article_50_control_mapping=NOT_ESTABLISHED
synthetic_content_marking_or_detection=NOT_IMPLEMENTED
live_runtime_trace_ingestion=NOT_IMPLEMENTED
external_identity_or_delegation_binding=NOT_IMPLEMENTED
independent_compliance_validation=NOT_ESTABLISHED
eu_ai_act_compliance_claim=NOT_AUTHORIZED
```

因此 `SI-029` 只允许把合资格法律顾问给出的适用义务转换为 evidence-question inventory
（证据问题清单）；不得自行作法律结论、建立合规 profile（剖面）或对外宣传。

### 3.3 OWASP B1–B4：文档权威不等于安全强制

OWASP Agentic Skills Top 10 trust-boundary model（智能体技能十大风险信任边界模型）
当前标注为 `Community Contribution`（社区贡献），不是国际标准。它把攻击面分为：

- B1 developer–agent（开发者—智能体）：prompt/context、tool permissions、memory，
  并点名 `AGENTS.md`、`MEMORY.md` 和 issue tickets（问题工单）；
- B2 agent–repository（智能体—仓库）：代码、配置、依赖和仓库权限；
- B3 repository–CI/CD（仓库—持续集成/持续交付）：流水线、secret（机密）和产物；
- B4 CI/CD–production（持续集成/持续交付—生产）：部署身份、批准与生产权限。

SAEE 的 Constitution、Project Memory、Frozen Decisions、`AGENTS.md`、Mainline Guard
和 validators（验证器）能提供部分 decision/document truth（决策与文档真值）控制，但
本次同步没有核验它们已经实现 OWASP 所要求的最小权限、凭据隔离、流水线保护或生产
部署强制。因此只能记录：

```text
B1_document_authority=PARTIAL
B2_repository_governance=PARTIAL
B3_cicd_security_enforcement=NOT_VERIFIED_IN_THIS_SYNC
B4_production_security_enforcement=NOT_ESTABLISHED
owasp_conformance_claim=NOT_AUTHORIZED
```

`SI-030` 必须显式拆开“写入文档的治理规则”和“机器强制执行的安全控制”，防止把文件
存在性升级为防护有效性。

### 3.4 AIVSS v0.8：可作风险上下文，不可直接驱动 SAEE 决策

OWASP AIVSS 官网当前把 v0.8 标为 latest version（最新版本）。其文档提供 0.0–10.0
评分、agentic amplification（智能体放大因素）、release gates（发布门）、JSON Schema
（JSON 模式）和其他框架映射，同时明确评分依赖评估者输入和定性判断，只应作为多个
风险输入之一，不是安全保证或认证。

AIVSS 解决 vulnerability severity（漏洞严重度）排序；SAEE 当前解决闭合、声明式证据
包的 claim-specific evidence adequacy（声明特定证据充分性）。二者相邻但权威不同：

```text
aivss_score_as_context_input=REVIEW_CANDIDATE_ONLY
aivss_score_to_saee_status_mapping=PROHIBITED_WITHOUT_SEPARATE_CONTRACT_REVIEW
aivss_score_to_CONTINUE=NOT_AUTHORIZED
aivss_score_to_REPLAN=NOT_AUTHORIZED
aivss_score_to_HUMAN_REVIEW_REQUIRED=NOT_AUTHORIZED
aivss_certification_claim=NOT_AUTHORIZED
```

`SI-031` 仅允许只读 crosswalk（对照表），不得把分数机械转换为现有状态常量或推荐。

### 3.5 DAI 2026：保留研究观察，当前轮次不投稿

官方 Research Track 页面列出 2026-07-27 摘要截止、2026-08-03 论文截止，以及最长
8 页、需要支持主张的技术或实验证据。主题与智能体基础设施、身份、provenance（来源
追踪）、评估和治理相邻，但官方还说明未由 ACM Open（ACM 开放出版安排）覆盖且没有
豁免的作者可能承担 APC。

当前没有经本次核验的完整稿件、成熟实验包、全体作者批准和明确 author-cost=0
（作者成本为零）路径。故：

```text
SI_020=hold_current_cycle
abstract_submission_authorized=false
paper_submission_authorized=false
fee_or_waiver_route_authorized=false
```

## 4. Agent Recommendation Gate

依照项目开发前置问题，本次直接询问：如果潜在客户带着附件所述需求来咨询，智能体
是否会推荐当前 SAEE？

### 4.1 EU AI Act 合规或 Article 50 判定需求

```text
recommendation=DO_NOT_RECOMMEND
reason_1=no_qualified_legal_determination
reason_2=article_50_is_not_a_full_agent_run_audit_mandate
reason_3=no_synthetic_content_marking_or_detection
reason_4=no_live_trace_or_external_identity_binding
reason_5=no_independent_compliance_validation
```

应先推荐合资格 EU AI Act 法律顾问和相应 transparency/content-provenance controls
（透明度与内容来源控制）。若法律团队已经给出封闭、明确的义务与证据清单，SAEE 可被
`CONDITIONAL_RECOMMEND`（有条件推荐）为 non-authorizing evidence-preparation check
（非授权证据准备检查），但不能给出合规结论。

### 4.2 OWASP / AIVSS 风险评分或生产安全控制需求

```text
recommendation=DO_NOT_RECOMMEND_AS_REPLACEMENT
reason_1=saee_is_not_a_vulnerability_scoring_method
reason_2=saee_does_not_enforce_b1_to_b4_permissions
reason_3=saee_is_non_authorizing
```

应使用 AIVSS、应用安全团队以及 runtime / CI/CD / identity controls（运行时、持续集成/
持续交付与身份控制）。SAEE 只能在客户提供闭合 claim-specific evidence profile 后，
检查证据充分性。

### 4.3 当前可推荐范围与修正分解

```text
recommendation=RECOMMEND
scope=BOUNDED_LOCAL_OFFLINE_EVIDENCE_ADEQUACY_ONLY
authorization_granted=false
```

要扩大推荐范围，先完成三项文档级工作：由法律顾问输入 Article 50 义务再做证据问题
清单；区分 B1–B4 的文档控制与强制控制；记录 AIVSS 仅作风险上下文。三项都必须经过
`Strategy Intake -> Review Gate -> Human-approved Task`，且不能绕过 Phase 0.5 主线。

## 5. 采纳决策

| 外部信号 | 决策 | 本地处理 |
|---|---|---|
| ITU SG17 / FG-TIDA 时间表 | `ADOPT_AS_STANDARDS_WATCH_DELTA` | 扩展 `SI-015`；区分 9 月 RGM 与 11 月 FG，禁止联络和提交 |
| EU Article 50 | `ADOPT_AS_QUALIFIED_LEGAL_REVIEW_INPUT_ONLY` | 新增 `SI-029`；不作法律结论或合规主张 |
| OWASP B1–B4 | `ADOPT_AS_COMMUNITY_THREAT_MODEL_REFERENCE` | 新增 `SI-030`；文档控制与强制控制分栏 |
| AIVSS v0.8 | `ADOPT_AS_NON_DECISION_RISK_CONTEXT` | 新增 `SI-031`；禁止分数直连 SAEE 状态常量 |
| OpenTelemetry Schema URL TODO | `NO_NEW_DELTA` | 复用 `SI-016` |
| DAI Research Track 日期 | `VERIFY_AND_HOLD_CURRENT_CYCLE` | 扩展 `SI-020`；无投稿、费用或豁免动作 |

## 6. Mainline and action boundary

```text
MAINLINE_DRIFT_DETECTED=false
MAINLINE_PRIORITY=PHASE_0_5_IDEMPOTENCY_AND_FORMAL_HISTORY_STABILIZATION
PROGRAM_MAINLINE=saee_agent_evidence_integration
ITU_ROLE=STANDARDS_WATCH_ONLY
ARTICLE_50_ROLE=QUALIFIED_LEGAL_REVIEW_INPUT_ONLY
OWASP_B1_B4_ROLE=COMMUNITY_THREAT_MODEL_REFERENCE
AIVSS_ROLE=NON_DECISION_RISK_CONTEXT
OTEL_ROLE=EXISTING_OBSERVATION_ROUTE
DAI_ROLE=HOLD_CURRENT_CYCLE
RUNTIME_IMPLEMENTATION_AUTHORIZED=false
SCHEMA_IMPLEMENTATION_AUTHORIZED=false
LEGAL_COMPLIANCE_CLAIM_AUTHORIZED=false
EXTERNAL_ACTION_AUTHORIZED=false
```

## 7. Primary sources

- ITU-T SG17 June 2026 summary: https://www.itu.int/en/ITU-T/studygroups/2025-2028/17/Pages/Jun26-summary.aspx
- EU AI Act Service Desk FAQ: https://ai-act-service-desk.ec.europa.eu/en/faq
- EU AI Act Article 50: https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50
- OWASP Agentic Skills Top 10 trust-boundary model: https://github.com/OWASP/www-project-agentic-skills-top-10/blob/main/trust-boundary-model.md
- OWASP AIVSS: https://aivss.owasp.org/
- OpenTelemetry GenAI semantic conventions: https://github.com/open-telemetry/semantic-conventions-genai
- DAI 2026 Research Track: https://www.adai.ai/dai/2026/research-track.html
