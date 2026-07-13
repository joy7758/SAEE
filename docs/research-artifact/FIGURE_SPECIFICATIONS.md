# SAEE 未来论文 Figure Specifications

本文件只定义未来论文图片的内容规格，不生成图片，也不代表论文已经开始投稿或发表。所有图必须使用“本地合成”“候选字段”“profile 需求满足”等准确标签。

## Figure 1：SAEE architecture overview

Purpose：展示证据研究子系统在 SAEE 演化档案／回滚免疫系统中的位置，以及五层研究数据流。

Elements：

- 左侧或顶部：`Observation Layer`；
- 中间：`Candidate Evidence Mapping`、`Evidence Object Layer`、`Evidence Adequacy Layer`；
- 底部：`Accountability Claim Evaluation`；
- 每层旁标注输入、输出和失败状态；
- 外框标注 `SAEE Evolutionary Archive / Rollback Immune Subsystem`；
- 明确写出 `Not the complete SAEE architecture`。

Message：SAEE 将观察、对象、关系和结论边界分层；该证据架构只是数字生物圈进化引擎的子系统。

禁止视觉暗示：不得画成生产治理平台、监管认证链或完整 SAEE 总架构。

## Figure 2：Trace-to-evidence transformation

Purpose：解释 OpenTelemetry 风格观察为什么不能直接成为证据。

Elements：

- 合成 trace 字段：agent、action、tool、resource、timestamp；
- 候选映射框，输出 `candidate_*`；
- 缺口标记：publisher identity、content digest、policy object、approval context；
- 资源解析收据示例对象；
- 映射 `PASS` 与充分性 `FAIL` 的并列状态；
- 注记 `trace_auto_accepted_as_evidence=0`。

Message：映射只产生候选输入；需要独立对象和关系才能进入充分性判断。

禁止视觉暗示：不能把 trace 箭头直接连接到“proof”“verified event”或“legal finding”。

## Figure 3：Evidence adequacy evaluation flow

Purpose：展示 claim-specific profile 如何检查字段和语义关系。

Elements：

- 输入：`claim_type`、evidence package、profile；
- 字段检查；
- 关系检查：引用相等、时间顺序、摘要一致；
- 输出：`PASS/FAIL`、missing requirements、reason codes；
- 固定边界：`accountability_claim_established=false`。

Message：schema 合法、对象存在和 claim 充分性是三个不同判断；关系错误可以让字段齐全的对象失败。

禁止视觉暗示：本地 `PASS` 不得用“责任已成立”“法律有效”或认证徽章表达。

## Figure 4：Benchmark evidence level comparison

Purpose：可视化四个证据级别在 12 个策划场景中的本地 PASS/FAIL 分布。

Elements：

- 横轴：`LEVEL_0`、`LEVEL_1`、`LEVEL_2`、`LEVEL_3`；
- 每级总数固定为 3；
- 本地 PASS：`0、1、1、3`；
- 本地 FAIL：`3、2、2、0`；
- 图注说明 `curated synthetic regression only`；
- 附注 `false_positive_count=0` 与 `boundary_violation_count=0` 只适用于该固定数据集。

Message：随着对象和关系增加，更多场景满足当前 profile；中间级别仍会因错误引用、时间或摘要关系失败。

禁止视觉暗示：不得把柱高解释成真实准确率、供应商排名或统计泛化能力。

## 通用制图要求

- 中文正文可使用英文状态常量，但状态常量保持原样；
- 使用不同形状区分 observation、candidate、evidence object 和 evaluation result；
- 所有图注必须包含 synthetic/offline/local 边界；
- 不使用合规徽章、法律天平、生产监控大屏或竞品排名视觉；
- 图中数字必须能够回指 `expected-results.v0.1.json`。
