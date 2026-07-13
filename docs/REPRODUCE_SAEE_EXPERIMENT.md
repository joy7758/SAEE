# 本地复现 SAEE 证据充分性实验

“This reproducibility package describes local execution requirements and expected outputs. It does not represent independent validation, certification, or proof that underlying events occurred.”

“该复现包描述本地执行要求和预期输出，不代表独立验证、认证，也不证明底层事件一定真实发生。”

## 复现范围

本指南只说明如何在当前 SAEE 仓库本地运行 PR-1 至 PR-5 的合成验证命令。它不下载数据、不访问外部服务、不发布 artifact，也不声称任何第三方已经完成复现。

## 环境约束

环境声明的完整解释见 `docs/REPRODUCIBILITY_ENVIRONMENT_REQUIREMENTS.md`。当前记录为：

```text
python_command=python3
python_version_observed=3.14.5
python_syntax_minimum=3.10
python_minimum_supported_version=not_formally_declared
execution_mode=offline_synthetic
network_required=false
```

仓库代码包含 Python 3.10 运行特性，因此 `3.10` 是可识别的技术下限；CI 只使用滚动 `3.x` 且没有版本矩阵，所以最低支持版本仍为 `not_formally_declared`。`3.14.5` 只是本次观察和运行值，不能外推为所有中间版本均已测试。

依赖状态：

- `saee_backend/requirements.txt` 是当前依赖声明真源；
- PR-1 至 PR-5 的 schema validator 使用 `jsonschema>=4.18,<5.0`；
- 现有后端数据契约使用 `pydantic>=2.0,<3.0`；
- 环境检查不自动安装包，也不访问网络。

复现者必须在运行前使用受控、本地或组织批准的依赖提供方式确保 `pydantic` 和 `jsonschema` 可导入。不要把临时联网安装描述成离线复现成功。

可进行只读环境检查：

```bash
python3 --version
python3 -c "import jsonschema, pydantic"
make check-saee-environment-requirements
```

## 步骤 1：准备仓库

进入已经包含 manifest 所列文件的当前 SAEE 工作区。不要在本流程中克隆未知仓库、执行外部安装脚本或下载外部数据。

先检查：

```text
agent-interface/reproducibility/saee-reproducibility-manifest.v0.1.json
agent-interface/reproducibility/expected-results.v0.1.json
```

## 步骤 2：检查依赖

阅读已有依赖声明：

```text
saee_backend/requirements.txt
```

确认当前解释器可以导入 `pydantic` 和 `jsonschema`。如果缺失，应先停止，并通过单独批准的依赖管理流程准备离线或可信来源环境。本复现规范不提供网络安装命令。

环境 smoke 只验证本地环境与声明是否一致：

```bash
make check-saee-environment-requirements
```

预期首行是 `SAEE_ENVIRONMENT_REQUIREMENTS_SMOKE: PASS`。这不是 clean-room 第三方复现证明。

## 步骤 3：运行五个 artifact 检查

以下均为仓库现有 Makefile 命令：

```bash
make check-resource-resolution-receipt
make check-evidence-adequacy
make check-otel-candidate-mapping
make check-agent-receipt-crosswalk
make check-evidence-adequacy-benchmark
```

对应的首行成功标识：

```text
SAEE_RESOURCE_RESOLUTION_RECEIPT_SMOKE: PASS
SAEE_EVIDENCE_ADEQUACY_SMOKE: PASS
SAEE_OTEL_CANDIDATE_MAPPING_SMOKE: PASS
SAEE_AGENT_RECEIPT_CROSSWALK_SMOKE: PASS
SAEE_EVIDENCE_ADEQUACY_BENCHMARK_SMOKE: PASS
```

## 步骤 4：运行复现规范完整性检查

```bash
make check-saee-reproducibility
```

预期标识：

```text
SAEE_REPRODUCIBILITY_SMOKE: PASS
```

该命令只检查 manifest、文件、命令声明和预期结果结构，不执行五个 artifact 命令，也不访问网络。

## 步骤 5：运行 benchmark 并比较预期输出

benchmark 已包含在步骤 3 的 Makefile 检查中。需要单独查看机器可读结果时，可运行仓库现有 CLI：

```bash
python3 scripts/saee_agent_cli.py benchmark-evidence-adequacy \
  --input agent-interface/benchmarks/evidence-adequacy/
```

将输出与以下文件比较：

`agent-interface/reproducibility/expected-results.v0.1.json`

关键回归基线：

```text
scenario_cases=12
PASS=5
FAIL=7
expected_result_matches=12/12
missing_evidence_accuracy=12/12
reason_code_accuracy=12/12
false_positive_count=0
boundary_violation_count=0
```

这些是策划合成数据集的确定性回归值，不是 SAEE 准确率或科学性能分数。

## 失败处理

- 依赖无法导入：停止并记录环境缺口，不联网自动修复。
- manifest 文件缺失：复现规范不完整，不运行未知替代文件。
- 预期原因码变化：检查是否发生 evaluator 或 profile 契约漂移。
- 全量仓库检查出现无关失败：单独报告，不把它混入本 artifact 的成功或失败结论。

## 结论边界

本地所有命令通过，只能说明：在已记录环境中，当前文件和本地合成预期可以重复得到一致结果。它不表示：

- artifact 已公开发布；
- 已获得 DOI 或 release tag；
- 外部研究者已经独立复现；
- 第三方验证、认证或科学接受已经完成；
- 底层事件、身份、授权或因果关系在现实中成立；
- 系统生产就绪。
