# SAEE 论文支持 Artifact 结构

## 结构总览

| 组件 | Purpose | Input | Output | Validation command |
|---|---|---|---|---|
| `schemas/` | 定义闭合对象、profile、映射和 benchmark 数据结构 | JSON 实例 | 结构错误或合法实例 | 各组件 `make check-*` |
| `examples/` | 提供合成正例和候选映射样例 | 固定合成 JSON | 应接受或可映射结果 | 资源、充分性、OTel 聚焦检查 |
| `fixtures/` | 提供缺字段、错误关系和越界声明反例 | 固定变换后的 JSON | 稳定拒绝原因 | 对应组件 smoke |
| `profiles/` | 定义四类 claim 的字段与关系要求 | claim type 与证据包 | `PASS/FAIL`、缺失项、原因码 | `make check-evidence-adequacy` |
| `benchmarks/` | 组织 12 个合成场景和四个证据级别 | profile、fixture、预期结果 | 逐场景与汇总结果 | `make check-evidence-adequacy-benchmark` |
| `scripts/` | 提供离线验证、回归和边界检查入口 | 仓库内固定路径 | 稳定 PASS 标识或非零退出 | 本文件下列命令 |
| `reproducibility/` | 声明文件、环境、命令与预期结果 | manifest 与环境声明 | 可复查的本地复现边界 | `make check-saee-reproducibility` |

## 1. schemas/

Purpose：让编码智能体和检索智能体发现证据对象与研究数据的显式结构契约。

Input：资源解析收据、充分性 profile、OTel 风格候选映射、benchmark 和复现 manifest。

Output：结构校验结果。结构通过不表示真实性、充分性或外部有效性通过。

主要入口：

- `agent-interface/schemas/resource-resolution-receipt.schema.json`
- `agent-interface/schemas/evidence-adequacy-profile.schema.json`
- `agent-interface/schemas/otel-candidate-evidence-mapping.schema.json`
- `agent-interface/schemas/evidence-adequacy-benchmark.schema.json`
- `agent-interface/schemas/reproducibility-manifest.schema.json`

## 2. examples/

Purpose：提供完全合成、无凭据、无真实身份、无真实外部资源的正例。

Input：固定 JSON 文件。

Output：正例被本地验证器接受，或轨迹字段被标记为候选字段。

Validation commands：

```bash
make check-resource-resolution-receipt
make check-evidence-adequacy
make check-otel-candidate-mapping
```

## 3. fixtures/

Purpose：证明缺少发布者、摘要、策略引用、审批上下文或因果关系时系统能够稳定拒绝。

Input：仓库内固定负例，不接受外部路径。

Output：非零或 `FAIL`，并返回稳定原因码。负例拒绝不是现实攻击防御率。

Validation commands：由相应组件 smoke 自动覆盖。

## 4. profiles/

Purpose：把“某个 claim 需要什么证据”从隐含规则改为文件化契约。

Input：claim type、证据字段和语义关系。

Output：`profile_requirements_satisfied`、缺失要求、关系错误和稳定原因码；`accountability_claim_established` 仍为 false。

Validation command：

```bash
make check-evidence-adequacy
```

## 5. benchmarks/

Purpose：在四个证据级别上复查字段缺失、引用不一致、时间错误和摘要不一致等策划场景。

Input：`benchmark.v0.1.json` 中的 12 个合成场景。

Output：5 个本地 `PASS`、7 个本地 `FAIL` 及预期匹配计数。这些是固定回归值，不是现实准确率。

Validation command：

```bash
make check-evidence-adequacy-benchmark
```

## 6. scripts/

Purpose：提供离线、确定性、可被智能体调用的验证入口。

Input：仅仓库内声明文件和合成 fixture。

Output：稳定的 `SAEE_*: PASS` 标识或明确失败。

本 artifact 自检：

```bash
make check-saee-research-artifact
```

## 7. reproducibility/

Purpose：声明本地复现所需的文件、命令、Python 技术下限、实测版本与依赖范围。

Input：复现 manifest、预期结果和 `saee_backend/requirements.txt`。

Output：环境声明与 artifact 引用完整性结果，不自动安装依赖，不执行外部代码。

Validation commands：

```bash
make check-saee-environment-requirements
make check-saee-reproducibility
```

## 边界

该结构是未来论文支持材料的本地组织形式。目录完整不等于 artifact 已发布，命令可运行不等于第三方已复现，固定预期匹配不等于现实世界性能得到验证。
