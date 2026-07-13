# SAEE Research Artifact 实验摘要

## 实验范围

实验只使用仓库内策划的合成 JSON、固定 profile 和离线验证器。它检查结构、摘要、字段、引用、时间和因果关系是否与预期一致，不测量吞吐量、延迟、模型智能、真实攻击防御率或外部系统性能。

## A. Component evaluation

| Component | Cases | Expected Result |
|---|---:|---|
| Resource Receipt | 1 正例、4 负例、38 对抗变体、10 次确定性 | 正例接受；缺发布者、摘要、策略或绑定关系时稳定拒绝 |
| Evidence Adequacy | 4 正例、4 负例、16 对抗变体、20 次确定性 | 每类 profile 正例满足；缺字段或关系错误时失败；不建立现实责任 |
| OTel Candidate Mapping | 3 正例、3 负例、7 对抗变体、15 次确定性 | 合法观察只形成候选字段；`trace_auto_accepted_as_evidence=0` |
| Agent Receipt Crosswalk | 1 合法映射、2 非法映射、9 行、10 次确定性 | 机器映射与文档边界一致；`unsupported_claims=0` |
| Evidence Adequacy Benchmark | 12 个场景、4 类 claim、4 个证据级别 | 5 个本地 PASS、7 个本地 FAIL；全部与策划预期一致 |
| Reproducibility Package | 1 合法 manifest、2 非法 manifest、23 个文件、5 次确定性 | 文件、命令、预期结果和 truth boundary 完整 |
| Environment Requirements | 1 正例、3 反例、2 个必需包、5 次确定性 | 缺依赖、版本格式错误或缺环境段时失败 |

表中“正例”“负例”和“对抗变体”都是本地测试分类，不代表现实样本量或统计显著性。

## B. Benchmark summary

| 指标 | 本地基线 | 解释边界 |
|---|---:|---|
| Scenarios | 12 | 固定、策划、合成场景 |
| Claim types | 4 | `RESOURCE_AUTHENTICITY`、`AUTHORIZED_AGENT_ACTION`、`HUMAN_OVERSIGHT`、`EXECUTION_BOUNDARY` |
| Evidence levels | 4 | `LEVEL_0` 至 `LEVEL_3`，每级 3 个场景 |
| PASS | 5 | 满足当前本地 profile，不证明现实 claim |
| FAIL | 7 | 缺字段或关系不满足当前本地 profile |
| Expected result matches | 12/12 | 与策划预期逐项一致 |
| Missing evidence accuracy | 12/12 | 缺失路径与策划标签一致，不是机器学习准确率 |
| Reason code accuracy | 12/12 | 稳定原因码与策划标签一致 |
| False positive count | 0 | 仅针对 7 个策划 FAIL 场景，不是现实假阳性率 |
| Boundary violation count | 0 | 没有把事件、法律责任、认证或生产状态升级为 true |

### Evidence level comparison

| Evidence level | Local PASS/Total | 研究解释 |
|---|---:|---|
| `LEVEL_0_TRACE_ONLY` | 0/3 | 观察字段不足以支持本地 claim profile |
| `LEVEL_1_RECEIPT` | 1/3 | 对象存在可支持有限绑定，但错误引用仍失败 |
| `LEVEL_2_RECEIPT_WITH_RELATIONSHIPS` | 1/3 | 关系字段存在仍可能因时间或摘要不一致失败 |
| `LEVEL_3_COMPLETE_EVIDENCE_PACKAGE` | 3/3 | 当前 profile 需求满足，但现实责任仍未建立 |

## 实验设计逻辑

1. 每个场景指定 claim type 和证据级别。
2. 场景引用仓库内固定合成输入，并施加显式 JSON Pointer 变换。
3. evaluator 输出 `PASS/FAIL`、缺失要求和原因码。
4. benchmark runner 将实际输出与策划预期逐项比较。
5. boundary check 确认任何本地 `PASS` 都没有升级为现实事件、法律、认证或生产结论。

## 关系反例

三个场景字段齐全但仍应失败：

- action 与 policy decision 引用不同动作；
- human approval 晚于 action；
- causal link 的摘要与 resource/effect 摘要不一致。

它们用于证明 v0.1 evaluator 不只是字段计数器。

## 可复现入口

```bash
make check-saee-environment-requirements
make check-resource-resolution-receipt
make check-evidence-adequacy
make check-otel-candidate-mapping
make check-agent-receipt-crosswalk
make check-evidence-adequacy-benchmark
make check-saee-reproducibility
make check-saee-research-artifact
```

## 不支持的实验结论

- 不比较 SAEE 与任何外部工具的性能或优越性；
- 不估计真实世界准确率、召回率、安全率或法律有效性；
- 不验证真实发布者、人类审批人、策略系统或外部执行；
- 不声称 OpenTelemetry、IETF 或其他规范兼容；
- 不声称第三方复现、论文接受、认证或生产部署。
