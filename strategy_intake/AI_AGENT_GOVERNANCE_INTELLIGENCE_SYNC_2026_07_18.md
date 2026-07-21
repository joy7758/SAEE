# AI Agent Governance Intelligence Sync — 2026-07-18

```text
sync_id=SAEE_AI_AGENT_GOVERNANCE_INTELLIGENCE_SYNC_2026_07_18
source_brief_date=2026-07-18
sync_status=COMPLETE
overall_decision=ADOPT_VERIFIED_DELTAS_AS_REFERENCE_AND_RESEARCH_INPUT_ONLY
new_capability_required=false
new_competitive_report_required=false
runtime_change=NONE
schema_change=NONE
mcp_change=NONE
product_change=NONE
constitution_change=NONE
mainline_change=NONE
external_action_authorized=false
submission_authorized=false
production_ready=false
```

## 1. 同步结论

本批简报大部分内容已在 2026-07-16—17 的 Strategy Intake 中完成同步：

- Microsoft Agent Governance Toolkit 已作为强相邻 runtime-governance 类别记录；
- WAICO / WAIC 已进入 institution watch；
- OpenTelemetry GenAI 仍只允许只读 mapping 和上游 drift observation；
- DAI 2026 当前周期仍为 `hold_current_cycle`；
- Phase 0.5 稳定化与 Agent Evidence Integration 主线没有改变。

因此本次不重复创建竞争报告，也不把新闻转换为 capability、runtime roadmap、产品
状态或外部行动。经原始来源核验后，仅采纳四项增量：

1. Microsoft 的 evidence-led red-team RFC 已有未合并实现 PR；
2. xChk 提供 `verifier-determined sufficiency` 身份证据原则；
3. `Load-Bearing Evidence` 预印本把 reconstructability 变成可运行的评估有效性指标；
4. AgentBound 与 Vera 进一步明确 runtime governance、safety testing 与 SAEE 当前
   bounded evidence adequacy 的类别边界。

## 2. 防重复建设结果

```text
existing_microsoft_route=reports/SAEE_TRUST_INFRASTRUCTURE_COMPETITIVE_LANDSCAPE.md#4.7
existing_intelligence_sync=strategy_intake/AI_AGENT_GOVERNANCE_INTELLIGENCE_SYNC_2026_07_17.md
existing_otel_candidate=SI-016
existing_related_work_candidate=SI-018
existing_dai_decision=SI-020_hold_current_cycle
existing_microsoft_candidate=SI-021
existing_waico_candidate=SI-022
new_competitive_report_required=false
```

新信息只追加 verified delta、研究假设与候选映射，不新增：

- red-team framework；
- identity provider；
- policy engine；
- sandbox 或 runtime enforcement；
- reconstructability evaluator；
- OTLP ingestion 或新 trace schema；
- 第二套 evidence adequacy evaluator。

## 3. 经核验的增量信号

| 信号 | 当前核验状态 | SAEE 处理 |
|---|---|---|
| Microsoft AGT issue `#3349` | RFC 仍为 open，标签为 `needs-review:MEDIUM`；由 contributor 提出，不等于 Microsoft 正式 roadmap | 记录竞争方向，不升级为已发布 Toolkit capability |
| Microsoft AGT PR `#3362` | open、未合并；实现 24 个 deterministic smoke scenarios 和 `L2_mock_behavioural` detection-to-action matrix；live/corpus/public CLI 仍延期 | 说明相邻项目正在吸收 evidence-level 与 action-outcome 语义；只提取测试设计性状，不复制代码 |
| xChk `arXiv:2607.13369v1` | 2026-07-15 预印本；作者报告 reference deployment 与一个 relying party，未做独立生产/安全复现 | 采纳“证据由提供方携带、充分性由验证方按任务策略判断”的原则；不声称 POP 或 SAEE 已实现外部身份绑定 |
| Load-Bearing Evidence `arXiv:2607.12469v1` | 2026-07-14 预印本；提出八类 decision properties、Evidence Sufficiency Cards、reconstructability 与 replay precondition probe | 进入 related-work 和 falsifiable hypothesis；不声称 SAEE 已实现 reconstructability metric |
| AgentBound `arXiv:2606.30970v2` | 预印本，重点是 delegated authorization、owner policy、site contract 的 pre-action permit/review/deny 与治理回执 | 作为 runtime behavioral governance 相邻类别；SAEE 不重建 action authorization |
| Vera public repository | 仓库把自己定位为自动化 safety testing framework，包含风险发现、测试生成、隔离执行和基于环境状态/工具记录的 deterministic verification | 作为 safety-testing 相邻类别；SAEE 不重建测试生成和攻击执行框架 |

所有论文中的部署、测试数量、生产状态和安全效果均按作者自述记录；没有完成独立复现。

## 4. 我们真正可取的五点

### 4.1 把“充分性由验证方决定”固定为研究原则

最可取的不是 xChk 的身份栈，而是它的权力分离：

```text
evidence_provider=provides_claims_and_evidence
verifier=applies_task_specific_sufficiency_policy
evidence_provider_does_not_self_authorize=true
```

SAEE 可在研究与说明材料中采用这一原则：身份、委托、trace 或 receipt 提供证据；
SAEE 针对具体 claim 检查证据是否充分；最终行动授权仍属于外部授权方和 Human
Authority。

当前不能把这条原则写成已实现的 POP/identity capability，因为 canonical inventory
明确记录：

```text
saee.external_identity_binding=missing
saee.delegation_binding=missing
```

### 4.2 将 reconstructability 作为必要但不充分条件

推荐研究命题：

> **Reconstructability is necessary but not sufficient for readiness.**

一个判断可重建，仍可能存在：

- 身份未被外部认证；
- 委托无效、过期或超出 scope；
- trace 来源真实性未建立；
- 每一步单独允许，但组合路径违反政策；
- 缺少人工接管或回滚条件。

这比直接复制论文的总分或卡片格式更有 SAEE 差异性，也更符合 non-authorizing
readiness context。

### 4.3 明确“检测、尝试、执行、阻止”是不同事实

Microsoft RFC/PR 中最值得吸收的测试语义是：

```text
detected != contained
attempted != executed
executed != external_effect_proven
blocked_at must_be_explicit
```

这可用于未来测试设计和 evidence relationship review，但当前不新增 red-team runtime。
特别要保留两个容易被单一分数隐藏的 off-diagonal：

- `detected -> executed`：检测存在，但控制失败；
- `undetected -> contained`：检测失败，但下游防线生效。

### 4.4 继续强化 evidence level 不得自动升级

Microsoft 的 `declared -> static -> mock behavioural -> live behavioural` 层级与 SAEE
既有 staged truth 原则高度一致。可取之处是把证据级别与主张上限绑定，而不是复制
其四级名称：

```text
local_or_declared_evidence_cannot_claim_live_execution=true
mock_execution_cannot_claim_external_effect=true
live_trace_cannot_claim_authenticity_without_binding=true
passing_evaluation_cannot_grant_authority=true
```

### 4.5 用相邻工具强化“不竞争什么”

- Microsoft AGT / AgentBound：擅长 runtime policy 与 pre-action governance；
- Vera：擅长安全风险发现、测试生成和执行验证；
- xChk：擅长 heterogeneous identity claims 与 relying-party sufficiency；
- OpenTelemetry：擅长公共遥测语义；
- 当前 SAEE：只推荐 bounded local/offline claim-specific evidence adequacy。

因此可防守的当前表述不是“更大的治理平台”，而是：

> SAEE checks whether a declared closed evidence bundle covers explicit,
> repository-controlled requirements for a bounded readiness claim, while
> returning missing evidence and non-authorizing decision context.

这与 canonical inventory 当前的 `saee.evaluate_evidence` 一致，不把未来能力说成现在。

## 5. 不能直接吸收的内容

### 5.1 不采用 POP / ARO 五对象链作为当前架构事实

简报使用 `ARO=Agent Runtime Object`，但当前 SAEE registry 中 `aro-audit` 是
receipt/audit-format reference，并明确不是 Execution Object。术语未解决前，不得把：

```text
POP -> ARO -> Agent Evidence -> SAEE
```

写入 schema、API、canonical product story 或 capability inventory。

### 5.2 不把“人类控制”政策语言升级为技术能力

WAIC/WAICO 仍只属于 institution and policy watch。SAEE 当前的 non-authorizing
evaluation boundary 与 meaningful human control 方向相容，但不证明已实现失控检测、
kill switch、应急响应或国际标准合规。

### 5.3 不抢做 identity、red team、policy 或 trace runtime

外部项目已经各自覆盖这些类别。复制它们会造成 mainline drift，并违反
duplicate-build prevention 与“提取性状、不复制代码”的宪法约束。

### 5.4 不因窗口缩短而仓促投稿或扩 PR

DAI 2026 当前周期仍保持 `hold_current_cycle`。本批研究信号也不改变 Phase 0.5
稳定化候选 PR 的范围，不授权论文投稿、workshop proposal、branch、commit、push 或 PR。

## 6. 当前能力交叉检查

| 相关问题 | Canonical capability status | 当前结论 |
|---|---|---|
| 闭合 evidence bundle 对显式要求的覆盖 | `saee.evaluate_evidence=implemented/active` | 可推荐 bounded local/offline scope |
| 一般 trace normalization | `saee.general_trace_normalization=partial/experimental` | 不支持任意 OTel/Agent trace |
| trusted trace-to-evidence | `saee.trusted_trace_to_evidence_conversion=missing` | trace 不得自动升级为可信 evidence |
| external identity binding | `saee.external_identity_binding=missing` | xChk 只作为研究参考 |
| delegation binding | `saee.delegation_binding=missing` | AgentBound 委托能力不可归为当前 SAEE |

当前没有新的 canonical capability fact，也没有必要新增 capability ID。

## 7. Agent Recommendation Gate

### Question A

如果潜在客户已有闭合、声明式 evidence bundle，需要检查它是否覆盖一个显式的、仓库
控制的 readiness evidence set，是否推荐当前 SAEE？

```text
recommendation=RECOMMEND
scope=bounded_local_offline_claim_specific_evidence_adequacy
```

### Question B

如果潜在客户需要外部身份核验、delegation enforcement、runtime policy、sandbox、
red-team execution、OTLP ingestion 或 production authorization，是否推荐当前 SAEE？

```text
recommendation=DO_NOT_RECOMMEND
preferred_route=specialized_identity_runtime_governance_testing_or_observability_system
```

### Question C

如果客户需要 reconstructability metric、Evidence Sufficiency Card 或 verifier-determined
identity sufficiency 的完整实现，是否推荐当前 SAEE？

```text
recommendation=CONDITIONAL
current_value=research_crosswalk_and_bounded_existing_evidence_adequacy_only
missing=independent_comparative_validation_and_authorized_contract_design
```

## 8. 新增候选任务及优先级

| Priority | Candidate | Decision |
|---:|---|---|
| 1 | 完成 Phase 0.5 mainline idempotency / formal-history stabilization | 保持不变；本批不得扩 scope |
| 2 | 对 `Load-Bearing Evidence` 做逐项 related-work 与 falsifiable-hypothesis crosswalk | 新增 `SI-025`，研究文档候选，不实现 metric |
| 3 | 记录 Microsoft `#3349/#3362` 的 evidence-level 与 detection-to-action delta | 扩展 `SI-021` 并新增 `SI-023`，不复制 benchmark |
| 4 | 写 xChk verifier-determined sufficiency 到当前 identity/delegation missing 边界的只读映射 | 新增 `SI-024`，稳定化后评审，不改 schema |
| 5 | 将 AgentBound 与 Vera 作为相邻类别增量并入既有 competitive landscape | 新增 `SI-026`，不创建第二竞争报告 |

## 9. Mainline and action boundary

```text
MAINLINE_DRIFT_DETECTED=false
MAINLINE_PRIORITY=PHASE_0_5_IDEMPOTENCY_AND_FORMAL_HISTORY_STABILIZATION
PROGRAM_MAINLINE=saee_agent_evidence_integration
MICROSOFT_BENCHMARK_ROLE=UNMERGED_COMPETITOR_DELTA_AND_TEST_DESIGN_REFERENCE
XCHK_ROLE=IDENTITY_SUFFICIENCY_RESEARCH_REFERENCE
RECONSTRUCTABILITY_ROLE=RELATED_WORK_AND_FALSIFIABLE_HYPOTHESIS
AGENTBOUND_ROLE=RUNTIME_GOVERNANCE_ADJACENT
VERA_ROLE=SAFETY_TESTING_ADJACENT
RUNTIME_IMPLEMENTATION_AUTHORIZED=false
EXTERNAL_ACTION_AUTHORIZED=false
```

如果任何任务把竞争追踪、reconstructability 研究、POP/ARO 或红队测试提升到
Agent Evidence Integration 主线之上，则输出：

```text
MAINLINE_DRIFT_DETECTED
required_correction=return_to_phase0_5_stabilization_and_controlled_integration
```

## 10. Primary sources

- Microsoft AGT RFC `#3349`: https://github.com/microsoft/agent-governance-toolkit/issues/3349
- Microsoft AGT PR `#3362`: https://github.com/microsoft/agent-governance-toolkit/pull/3362
- xChk: https://arxiv.org/abs/2607.13369
- Load-Bearing Evidence: https://arxiv.org/abs/2607.12469
- AgentBound: https://arxiv.org/abs/2606.30970
- Vera: https://github.com/Yunhao-Feng/Vera
- OpenTelemetry GenAI semantic conventions: https://github.com/open-telemetry/semantic-conventions-genai

## 11. Validation boundary

本同步只更新 Strategy Intake 的 reference、research hypothesis 和 pending-review task
surfaces。PASS 只表示本地治理表面一致，不表示：

- 外部仓库已独立复现；
- 论文已经同行评审；
- Microsoft PR 已合并或进入正式路线图；
- xChk 的生产/安全声明已验证；
- SAEE 已实现 reconstructability、identity/delegation binding 或 runtime governance；
- 客户验证、商业采用、标准参与或 production readiness 已建立。
