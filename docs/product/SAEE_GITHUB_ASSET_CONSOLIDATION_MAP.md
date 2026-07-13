# SAEE GitHub 资产整合地图

## SAEE GitHub Asset Consolidation Map

本地图把相邻研究与实现资产映射到统一发现层。映射表示概念角色，不表示代码已经迁移、仓库被并入、官方集成完成或可公开重建端到端系统。

| 旧项目/资产 | SAEE 角色 | 作用 | 当前状态 | 未来定位 |
|---|---|---|---|---|
| `digital-biosphere-architecture` | Architecture Foundation | 术语、概念边界、引用语境 | 公开独立仓库；工作区有未提交变化 | 保持 public meaning layer，不公布执行依赖图 |
| `persona-object-protocol` | Agent Identity Module | Persona 与 Agent identity 参考 | 公开独立仓库；有 DOI；工作区有未提交变化 | 关联身份模块，保留独立发布和引用 |
| `aro-audit` | Audit Evidence Module | Receipt / audit format 示例 | 公开解耦参考；工作区有未提交变化 | 免疫/证据子系统参考，不提升为核心 |
| `agent-evidence` | Evidence Engine Reference | EEOAP schema、CLI 与验证器参考 | 公开解耦参考；有仓库级边界；工作区有未提交变化 | 保持独立 callable surface，不公开桥接全栈 |
| `agent-evidence-layer` | Agent Evidence Receipt Product | 相邻本地商业证据产品 | 无 `origin`；509 项工作区变化 | HOLD，不声称 GitHub 模块 |
| `token-governor` | Resource Governance Module | Budget-window policy 示例 | 公开解耦参考；工作区有未提交变化 | 资源治理参考模块 |
| `verifiable-agent-demo` | Demo Module | 单路径 toy validation | 公开独立仓库；工作区有未提交变化 | 最小演示入口，保持 toy 边界 |
| `paper-udi-dicom-profile` | Vertical Case Study | 医疗设备证据 profile 论文 | 独立 research org 的 paper-only 仓库 | 相关案例研究，不自动改标为产品模块 |
| Capability Runtime | Capability Runtime | 本地能力路由 | 当前 SAEE 内部组件 | 不虚构独立仓库 |
| MCP Adapter | Agent Interface | 本地 MCP transport adapter | 当前 SAEE 内部组件 | 不虚构外部 MCP 兼容或独立仓库 |

## Notice 状态

当前没有修改任何历史仓库 README：

```text
historical_repository_notice_written=false
```

原因：工作区全部非干净，且部分仓库有明确自治和公开边界规则。每个 Notice 必须在对应仓库单独审查、验证和提交。

## English technical summary

The map preserves repository autonomy, DOI and citation continuity. Relationships are descriptive module projections only. No code moves, repository renames, history rewrites, dependency publication, or external announcements are performed.
