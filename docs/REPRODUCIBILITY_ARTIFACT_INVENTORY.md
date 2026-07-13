# SAEE 本地复现 Artifact 清单 v0.1

“This reproducibility package describes local execution requirements and expected outputs. It does not represent independent validation, certification, or proof that underlying events occurred.”

“该复现包描述本地执行要求和预期输出，不代表独立验证、认证，也不证明底层事件一定真实发生。”

## 状态

```text
status=local_reproducibility_specification_not_published
public_release_performed=false
doi_created=false
release_tag_created=false
external_reproduction_completed=false
third_party_validation_completed=false
production_ready=false
```

本清单描述当前工作区内 PR-1 至 PR-5 的本地研究产物。它不是公开发布清单、归档记录或第三方复现报告。

## Artifact 清单

| Artifact | Purpose | Input | Output | Validation command |
|---|---|---|---|---|
| Resource Resolution Receipt | 验证合成资源请求、解析声明、内容摘要、策略引用和非执行边界 | `agent-interface/examples/verified-resource-resolution.json` 及负例 fixtures | 收据接受／拒绝结果和稳定原因码 | `make check-resource-resolution-receipt` |
| Evidence Adequacy Profile | 判断合成证据字段及引用、时间、范围、因果关系是否满足指定 claim | `agent-interface/examples/evidence-adequacy/` 和 `agent-interface/fixtures/evidence-adequacy/` | `PASS/FAIL`、缺失要求、失败关系和原因码 | `make check-evidence-adequacy` |
| OTel Candidate Mapping | 把闭合的合成 OpenTelemetry 风格观察提取为非权威候选字段，再送入充分性评估 | `agent-interface/examples/otel-mapping/` 和负例 fixtures | mapping 结果与独立 adequacy 结果 | `make check-otel-candidate-mapping` |
| Agent Receipt Crosswalk | 对任务提供的外部收据概念标签与 SAEE 本地概念进行研究级语义分析 | `agent-interface/mappings/agent-receipt-crosswalk.v0.1.json` | 九行 mapping、gap 和标准声明边界 | `make check-agent-receipt-crosswalk` |
| Evidence Adequacy Benchmark | 对十二个证据层级场景执行本地充分性回归 | `agent-interface/benchmarks/evidence-adequacy/benchmark.v0.1.json` | 逐场景结果、claim/level 计数、缺失与边界指标 | `make check-evidence-adequacy-benchmark` |

## 复现规范文件

- Manifest：`agent-interface/reproducibility/saee-reproducibility-manifest.v0.1.json`
- Manifest schema：`agent-interface/schemas/reproducibility-manifest.schema.json`
- Expected results：`agent-interface/reproducibility/expected-results.v0.1.json`
- Reproduction guide：`docs/REPRODUCE_SAEE_EXPERIMENT.md`
- Integrity smoke：`scripts/saee_reproducibility_smoke.py`

## 输入与输出边界

- 所有资源、身份、动作、审批、效果和 benchmark 场景均为合成值。
- `.invalid` host 只是保留的合成标识，不会被访问。
- 预期输出是回归基线，不是科学性能、产品准确率或外部验证结果。
- Artifact 文件存在不表示已公开发布、已归档、已获得 DOI 或已被第三方使用。
