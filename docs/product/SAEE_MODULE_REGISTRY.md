# SAEE 模块注册表

## SAEE Module Registry

| 模块 | 来源 | SAEE 定位 | 核心 | 公开 |
|---|---|---|---:|---:|
| Digital Biosphere Architecture | `digital-biosphere-architecture` | 科学与架构含义层 | 是 | 是 |
| Rehearsal Engine | 当前 SAEE `rehearsal_runtime` | 反事实模拟与沙盒发育 | 是 | 部分 |
| Reliability Evaluation | 当前 SAEE reliability services | 帕累托评估与失效分类 | 是 | 部分 |
| Evidence / Immune Subsystem | `agent-evidence`、ARO、当前 Evidence Adequacy | 证据充分性与回滚免疫支持 | 否 | 部分 |
| Agent Identity | `persona-object-protocol` | Persona / identity 参考 | 否 | 是 |
| Resource Governance | `token-governor` | 预算窗口治理参考 | 否 | 是 |
| Capability Runtime | 当前 SAEE | 本地规范能力调用 | 否 | 否 |
| MCP / HTTP Interface | 当前 SAEE | 本地运输适配 | 否 | 部分设计公开 |
| Demo | `verifiable-agent-demo` | Toy validation 演示 | 否 | 是 |
| UDI-DICOM Case | `paper-udi-dicom-profile` | 相关垂直论文案例 | 否 | 是，非产品模块 |

## 注册语义

`核心=true` 表示属于 Digital Biosphere Evolution Engine 的演化闭环核心。Evidence、Audit、MCP 和 Cloud 都不得仅因对外价值高而升级为核心。

`公开=true` 表示存在已识别的公共 Git 远程，不表示正式兼容、官方合作、生产支持或许可合并。

## English technical summary

This registry is a discovery map, not a package manager, dependency resolver, monorepo manifest, trust registry or execution graph. Source repositories retain independent identities, licenses, DOI records and histories.
