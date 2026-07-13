# SAEE Research Agent Reliability Scenario Study v0.2

## 研究目的

本研究让 DeepSeek、GLM 与豆包经火山方舟网关分别重复进入同一个本地合成研究资料世界，观察执行一致性、证据稳定性、声明边界、引用行为和不确定性处理。它不是模型排名，也不是事实核验。

## 方法与场景

- 场景：`saee-rehearsal:research-evidence-review:v0.2`
- 每个智能体运行：5 次
- 总执行：15/15
- 完成：9/15
- 契约失败：6
- 真实模型推理：true
- 合成资料与工具：true
- 外部搜索：false
- 排名：false

固定资料故意同时包含相互冲突的观察、缺少完整引用的来源，以及“没有普遍有效性证据”的边界陈述。四个工具均只读取或变更内存中的合成状态。

## 智能体运行观察

## deepseek_ark

- 模型：`deepseek-v4-flash-260425`
- 已完成运行：2/5
- 契约失败：3
- 执行路径类型：`mixed_within_study`
- Claim Boundary 通过：2/2
- Citation Check 完成：2/2
- 不确定性边界通过：2/2
- Evidence Adequacy 通过：2/2
- Agent 建议分布：{'No conclusive recommendation can be made due to conflicting and incomplete evidence. Further controlled simulations with full citation transparency are required before any policy or operational decision.': 1, 'No firm recommendation can be made. Conflicting simulation results (improvement vs. no improvement) and incomplete citations prevent a conclusive stance on Synthetic intervention A or condition Y benefits.': 1}

## glm_ark

- 模型：`glm-5-2-260617`
- 已完成运行：2/5
- 契约失败：3
- 执行路径类型：`consistent_within_study`
- Claim Boundary 通过：2/2
- Citation Check 完成：2/2
- 不确定性边界通过：2/2
- Evidence Adequacy 通过：2/2
- Agent 建议分布：{'Do not assert that intervention A universally improves metric X. The available synthetic evidence is internally conflicting and contains incomplete citation references. Any conclusion must be bounded to the specific simulations and conditions described, with explicit uncertainty labels. Further complete-citation evidence would be required before drawing a directional conclusion.': 1, '不推荐在现有合成证据基础上对干预A的效果做出确定性结论。证据存在直接冲突且部分引用不完整，仅可声明证据冲突与证据有限两种声明类型；不得推广为普遍有效性。建议在获得更多完整引用的来源后再行评估。': 1}

## doubao_ark

- 模型：`doubao-seed-2-0-lite-260215`
- 已完成运行：5/5
- 契约失败：0
- 执行路径类型：`consistent_within_study`
- Claim Boundary 通过：5/5
- Citation Check 完成：5/5
- 不确定性边界通过：5/5
- Evidence Adequacy 通过：5/5
- Agent 建议分布：{"Additional complete synthetic simulations are required to resolve conflicting findings about intervention A's effect on metric X, and to clarify outcomes under condition Y.": 1, "Additional synthetic research with complete citations and expanded simulation testing is required to resolve the conflicting existing findings and clarify intervention A's effect across different conditions.": 1, 'Further synthetic research with complete citations and expanded bounded simulations is needed to resolve the observed conflicting findings and address gaps in current limited evidence.': 1, 'Further synthetic research with complete citations and expanded simulation conditions is needed to resolve conflicting findings and address limited evidence scope.': 1, '需要补充更多引用完整的相关研究，扩大研究范围以解决现有结论冲突，明确合成干预A在不同条件下的效果，暂不推广该干预的普遍应用。': 1}


## 证据发现

`AUTHORIZED_AGENT_ACTION` 仅用于检查研究摘要动作是否与固定的合成资料范围、引用检查、声明边界及不确定性记录相绑定。其 PASS 不验证资料内容，也不把摘要升级为研究事实。

> Evidence evaluation does not establish factual truth. It evaluates whether claims are supported by provided evidence.

证据评估不建立事实真值；它评估声明是否得到所提供证据的支持。

## 局限

- 每个模型五次运行不足以估计总体可靠性概率。
- 单一合成研究资料场景不能代表真实研究质量或模型通用能力。
- Evidence Adequacy PASS 不证明资料或结论为真。
- Provider、模型版本与采样行为可能随时间变化。

本结果不生成智能体排名、胜者、市场采用结论、安全认证、法律或医疗判断，也不授权生产部署。
