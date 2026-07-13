# SAEE Research Artifact Paper Package v0.1 概览

## 状态与边界

本目录整理 PR-1 至 PR-6.5 的本地研究材料，为未来论文写作提供可检索、可复查的支持包。它不是论文投稿、arXiv 上传、DOI、GitHub release、第三方验证、认证或商业宣传。

```text
Research Artifact Package ≠ Paper Acceptance
Artifact Preparation ≠ Publication
Local Evidence ≠ External Validation
Synthetic Benchmark ≠ Real-World Evaluation
```

该材料属于 SAEE 数字生物圈进化引擎的演化档案／回滚免疫子系统，不重新定义 SAEE 的核心，也不把项目改写为审计优先 SDK。

## Research Problem

智能体运行系统越来越多地产生模型调用、工具调用、资源引用、人类审批和执行结果等观察记录。但“系统观察到某字段”与“该字段能够支持一个责任声明”是两个不同问题。轨迹可能缺少资源真实性、授权对象、审批上下文、内容摘要或因果关系；即使记录结构合法，也不能自动证明底层事件真实发生。

本 artifact 研究一个有限问题：能否通过本地、显式、可离线验证的对象与关系契约，区分以下四种状态？

1. 系统观察到了什么；
2. 证据对象记录了什么；
3. 证据对象的字段和关系是否满足一个定义明确的本地 claim profile；
4. 哪些更强的真实性、法律或外部结论仍不能成立。

## Research Contribution

### 1. Evidence Object Layer

资源解析收据把请求资源、解析 URI、发布者身份声明、内容摘要、策略引用和沙盒边界放入闭合 JSON 对象，并提供离线结构与摘要检查。该层只验证本地对象契约，不认证真实发布者或外部资源。

### 2. Evidence Adequacy Layer

四个本地 profile 分别描述 `RESOURCE_AUTHENTICITY`、`AUTHORIZED_AGENT_ACTION`、`HUMAN_OVERSIGHT` 和 `EXECUTION_BOUNDARY` 所需字段及关系。它区分 schema 合法、证据存在和证据对特定 claim 的充分性。

### 3. Candidate Trace Mapping Layer

OpenTelemetry 风格合成观察首先转换为不可信候选字段，再送入充分性检查。候选映射成功不等于证据充分，更不等于责任已经成立。本层不是 OpenTelemetry SDK 集成，也不声称规范兼容。

### 4. Reproducibility Layer

manifest、预期结果、环境要求和 smoke 共同描述本地文件、命令、版本边界和确定性回归结果。它改善研究材料复查，但尚无独立 clean-room 复现或第三方验证。

这些是当前仓库的实现组件和研究组织方式，不声明其为新标准，也不声明优于任何外部系统。

## 研究材料入口

- 机器可读 manifest：`agent-interface/research-artifact/saee-artifact-manifest.v0.1.json`
- 结构说明：`docs/research-artifact/SAEE_ARTIFACT_STRUCTURE.md`
- 架构说明：`docs/research-artifact/SAEE_ARCHITECTURE.md`
- 实验摘要：`docs/research-artifact/SAEE_EXPERIMENT_SUMMARY.md`
- 图规格：`docs/research-artifact/FIGURE_SPECIFICATIONS.md`
- 检查清单：`docs/research-artifact/PAPER_ARTIFACT_CHECKLIST.md`
- 聚焦校验：`make check-saee-research-artifact`

## 当前可以陈述的结论

当前可以陈述：仓库内合成对象、profile、映射、crosswalk、benchmark 和复现声明具有机器可读入口，策划场景的实际输出与固定预期一致，并保持声明边界为 false。

当前不能陈述：真实事件、身份、授权或因果关系已被证明；外部系统兼容；监管或法律有效；现实性能优越；论文已投稿或录用；artifact 已发布；系统已生产就绪。
