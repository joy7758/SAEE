# SAEE Pilot Annotation Codebook v0.1

状态：`draft_not_approved`；未开展人工标注。

## 标注单位与输出

每个标注单位是一个固定的 `claim_attempt`。标注者只能依据提供的 claim、adequacy profile、证据对象和关系作答，不得把日志存在、系统声称或个人常识当成缺失证据。

输出一个主标签，并可附：`missing_evidence_set`、`invalid_relationship_set`、`uncertainty_reason`。

决策顺序：无法可靠解释材料时选 `UNKNOWN`；存在必需证据缺失时选 `INSUFFICIENT_EVIDENCE`；字段齐全但必需关系失败时选 `INVALID_RELATIONSHIP`；全部必需证据和关系满足本地 profile 时才选 `SUPPORTED`。

## `SUPPORTED`

- 定义：提供的证据满足选定 claim profile 的所有必需字段和关系。
- 正例：合成 action 的 policy ref、scope、time 和 action identity 均存在且一致。
- 反例：只有一条 tool-call trace，没有 policy decision。
- 决策规则：缺失集合与错误关系集合均为空，且不存在阻止判断的歧义。

## `INSUFFICIENT_EVIDENCE`

- 定义：至少一个 profile 必需字段或证据对象未提供，无法支持 claim。
- 正例：资源真实性 claim 缺少 `content_digest`。
- 反例：digest 已提供，但 causal digest 指向另一资源；该情况属于 `INVALID_RELATIONSHIP`。
- 决策规则：记录精确 `missing_evidence_set`；不要臆造缺失值，也不要因其他字段看似合理而升级为支持。

## `INVALID_RELATIONSHIP`

- 定义：相关证据字段存在，但一个或多个必需引用、时间、范围、身份或因果关系不成立。
- 正例：审批时间晚于动作时间，或 effect digest 与 resource digest 不一致。
- 反例：审批时间字段完全缺失；该情况属于 `INSUFFICIENT_EVIDENCE`。
- 决策规则：只有在关系两端的必要材料可检查时使用，并记录精确 `invalid_relationship_set`。

## `UNKNOWN`

- 定义：材料歧义、不可读、相互冲突但无法裁决，或必要来源因权限/脱敏边界不可用于判断。
- 正例：两个未确定权威性的 manifest 对同一 action 给出冲突身份，且协议没有优先级。
- 反例：明确缺少 publisher identity；该情况属于 `INSUFFICIENT_EVIDENCE`。
- 决策规则：记录可复核的 `uncertainty_reason`；`UNKNOWN` 不是支持，也不能计入支持覆盖。

## 分歧与裁决

两名标注者独立标注。分歧时双方先引用上述规则复核，仍不一致则由独立裁决者确定标签并保留原始标注、理由与裁决记录。不得静默覆盖分歧。

