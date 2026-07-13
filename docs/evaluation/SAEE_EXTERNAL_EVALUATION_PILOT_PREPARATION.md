# SAEE External Evaluation Pilot Preparation v0.1

状态：`preparation_only`；当前就绪判定：`NOT_READY`。

```text
Pilot Preparation ≠ Pilot Execution
Dataset Plan ≠ Dataset Collection
Annotation Protocol ≠ Human Annotation Completed
Readiness Criteria ≠ Validation Result
```

本准备包服务于 SAEE 数字生物圈进化引擎的 `Global Sensing`、`Pareto Fitness Evaluation` 与 `Evolutionary Archive / Rollback Immune System`。它只定义未来试点的输入、控制和停止条件，不把 SAEE 重构为审计优先系统。

## 1 Pilot Objective

未来试点拟在受控、近似外部的场景中评估 SAEE 对 claim-level evidence adequacy（声明级证据充分性）的判断。v0.1 只准备协议，不运行智能体、不采集数据、不产生实验结果，也不证明外部有效性。

试点的最小研究单位是一个 `claim_attempt`：一个任务尝试、一个责任声明、一个证据条件和一个独立参考标注。

## 2 Proposed Pilot Scenario

候选场景为 `Code Agent Tool Execution`，尚未授权执行。

| 阶段 | 拟记录内容 | 当前状态 |
|---|---|---|
| Task input | `task_id`、目标、允许动作、禁止动作、预期输出 | 仅定义 |
| Agent actions | `agent_id`、`action_id`、动作类型、时间 | 仅定义 |
| Tool interactions | 工具名、参数摘要、调用结果、拒绝原因 | 仅定义 |
| Resource references | 请求资源、解析 URI、发布者、内容摘要 | 仅定义 |
| Authorization context | 策略引用、范围、决定、有效时间 | 仅定义 |
| Human oversight | 审批身份、上下文、范围、时间 | 仅定义 |
| Execution effects | effect 引用、因果绑定、沙盒引用 | 仅定义 |

任何未来执行都必须使用固定环境、允许列表工具、研究者拥有或明确获准的资产，并禁止未知外部代码、自动安装、权限扩大和不受控网络。

## 3 Data Requirements

| 数据对象 | 用途 | 必需字段 | 敏感级别 | 保留考虑 |
|---|---|---|---|---|
| Task description | 界定任务和允许边界 | `task_id`、目标、允许/禁止动作、预期结果 | 低；可能含业务上下文 | 版本固定；研究结束后按批准期限删除 |
| Agent action trace | 记录观察到的动作序列 | `agent_id`、`action_id`、事件类型、RFC 3339 时间 | 中；可能含提示词或路径 | 优先保留摘要；原始载荷分离保存 |
| Resource metadata | 区分请求与实际解析资源 | requested resource、resolved URI、publisher、digest | 中；URI 可能泄露私有资产 | 私有地址脱敏；保留摘要与来源清单 |
| Authorization records | 判断动作是否在授权范围内 | policy ref、decision、scope、valid time、action ref | 中高；可能暴露策略 | 最小披露；限制访问；记录删除 |
| Human approval records | 支持人工监督声明 | identity pseudonym、context、scope、approval time | 高；可能含个人数据 | 默认假名化；需同意与最短保留期 |
| Execution outcomes | 绑定允许或拒绝后的效果 | effect ref、status、sandbox ref、causal binding | 中；可能含输出内容 | 保留结构化结果；敏感输出分离 |
| Evidence package | 承载声明级评估输入 | profile、receipts、relationships、manifest | 取决于组成数据 | 保留版本、摘要、访问与删除记录 |

数据字段需求不构成采集授权。任何源进入试点前必须单独完成所有权、许可、隐私、保留和删除审查。

## 4 Data Source Options

三种选项均为 `option_not_selected`。

| 选项 | 优势 | 风险 | 启用要求 |
|---|---|---|---|
| A Synthetic controlled dataset | 关系真值可控、便于注入失败、无真实个人数据 | 泛化有限；研究者偏差 | 冻结生成规则、场景清单和 pilot/main 分割 |
| B Researcher-controlled local agent runs | 更接近真实执行且环境可控 | 仍会产生工具/提示词记录；可能执行未知内容 | 非联网沙盒、允许列表、资产所有权、完整审计轨迹、人工停止机制 |
| C Approved external dataset | 可评估跨来源适用性 | 权限、许可、个人数据、标签真值与来源不确定 | 书面批准、许可审查、隐私审查、溯源清单、删除与访问方案 |

本准备包不选择数据源。若权限或来源不清晰，试点保持 `NOT_READY`。

## 5 Annotation Protocol

标注单位为 claim-level evidence adequacy。每个单位包含固定 claim、profile、证据包和允许查看的参考材料。主标签使用 `SUPPORTED`、`INSUFFICIENT_EVIDENCE`、`INVALID_RELATIONSHIP`、`UNKNOWN`；缺失字段、错误关系和不确定原因另作结构化附注，因此同时覆盖“支持/不支持、缺失证据、错误关系、不确定性”。

拟定流程：

1. 两名标注者独立阅读 claim 与 profile，不推断未提供事实。
2. 先判断是否存在无法解释的歧义，再检查缺失要求，然后检查关系，最后判断支持。
3. 分歧先由标注者引用规则复核；仍不一致时交给未参与初标的裁决者。
4. 报告标签一致率、分歧率、裁决率；类别标签目标为 Cohen's kappa 或 Krippendorff's alpha `>= 0.80`，集合字段报告 Jaccard/F1。
5. 未达到目标时只能修订码本并重新 pilot，不能进入主评估。

v0.1 没有招募标注者、没有创建标注、没有计算一致性。详细规则见 [SAEE_ANNOTATION_CODEBOOK.md](SAEE_ANNOTATION_CODEBOOK.md)。

## 6 Annotation Codebook

规范入口：[SAEE_ANNOTATION_CODEBOOK.md](SAEE_ANNOTATION_CODEBOOK.md)。码本当前为待审批草案，不等于标注已经开始或完成。

## 7 Privacy and Licensing Checklist

检查入口：[SAEE_PILOT_PRIVACY_CHECKLIST.md](SAEE_PILOT_PRIVACY_CHECKLIST.md)。所有项目当前均未完成；本文不声称符合任何法规、许可或认证。

## 8 Execution Safety Gate

停止门入口：[SAEE_PILOT_EXECUTION_SAFETY_GATE.md](SAEE_PILOT_EXECUTION_SAFETY_GATE.md)。该门只定义未来执行前置条件，不授予执行、联网、安装、数据处理或权限扩大许可。

## 9 Pilot Readiness Criteria

只有以下条件全部满足，才可把未来试点评估为 `READY`：

- dataset source approved；
- annotation protocol approved；
- privacy and licensing review completed；
- execution environment fixed and independently identifiable；
- reproduction steps tested in that fixed environment；
- safety gate approved and stop authority assigned。

出现以下任一情况必须为 `NOT_READY`：数据源不清晰、权限不清晰、标签未定义或未批准、环境未固定、复现未测试、安全停止责任不清晰。

当前评估为 `NOT_READY`：数据源未选择，数据权限未批准，码本未获审批，隐私/许可检查未完成，试点环境未冻结，试点复现未测试。PR-10 的合成 prototype 通过不替代这些条件。

验证本准备包：

```bash
make check-saee-pilot-preparation
```

