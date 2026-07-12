# SAEE 智能体可靠性评估基础设施

## SAEE Agent Reliability Evaluation Infrastructure

SAEE 的正式理论身份是 **Silicon-Amplified Evolutionary Ecology（硅基放大演化生态）**，工程核心是 **Digital Biosphere Evolution Engine（数字生物圈进化引擎）**。本仓库是统一的公共产品入口；历史项目继续保留独立仓库、历史、DOI 与引用身份，并通过模块注册表进入 SAEE 产品生态。

> 在人工智能智能体进入真实业务前，先通过长期演练、可靠性评估和证据边界，看清它会不会漂移、失效或越界。

## 1. 为什么需要 SAEE

传统评测擅长回答“这次得了多少分”。SAEE 更关注智能体在长期扰动、工具失败、上下文变化和权限边界下是否仍然可靠，并把结果压缩为可复核的继续、修改、暂缓建议。

## 2. 核心能力

- **Rehearsal Engine（演练引擎）**：受控反事实模拟与沙盒发育。
- **Reliability Evaluation（可靠性评估）**：执行、证据、边界和运行可靠性。
- **Evidence / Immune Subsystem（证据与免疫子系统）**：证据充分性、回执、档案与回滚支持。
- **Capability Runtime（能力运行时）**：通过稳定契约组合规范能力。
- **MCP / HTTP Interface（智能体接口）**：运输适配，不产生授权或信任。

## 3. 产品架构

- [SAEE 产品架构](docs/product/SAEE_PRODUCT_ARCHITECTURE_V1.md)
- [SAEE 模块注册表](docs/product/SAEE_MODULE_REGISTRY.md)
- [GitHub 资产整合地图](docs/product/SAEE_GITHUB_ASSET_CONSOLIDATION_MAP.md)
- [机器可读生态映射](docs/product/saee-product-ecosystem-map.v1.0.json)

## 4. 快速开始

```bash
python3 scripts/saee_product_consolidation_smoke.py
python3 public_abstraction/demo/minimal_public_demo.py
```

公共演示只运行 toy abstraction，不包含私有内核、真实客户数据或外部系统执行。

## 5. MCP 支持

SAEE 已定义本地 MCP / HTTP 能力接口形态。公共仓库提供发现与边界说明，不提供公共运行时服务，也不声称外部 MCP 互操作、生产授权或生态采用已经完成。

## 6. 云生态路线

百度智能云千帆、火山方舟、阿里云百炼和 MCP 生态均处于“准备接入 / 受控研究”状态，尚非官方集成。详见 [云与智能体生态定位](docs/ecosystem/SAEE_CLOUD_ECOSYSTEM_POSITIONING.md)。

## 7. 研究基础

- Zenodo concept DOI: [10.5281/zenodo.21135471](https://doi.org/10.5281/zenodo.21135471)
- Current version DOI: [10.5281/zenodo.21215282](https://doi.org/10.5281/zenodo.21215282)
- Previous version DOI: [10.5281/zenodo.21135472](https://doi.org/10.5281/zenodo.21135472)
- [Publication Boundary](PUBLICATION_BOUNDARY.md)

## 8. 限制声明

SAEE 不是 Agent OS、通用多智能体工作流、实时授权系统、安全认证机构、法律判断服务或自动部署控制器。公开页面、toy demo、合成案例和机器清单不证明客户验证、外部采用或生产就绪。

```text
external_validation_claim=false
production_ready_claim=false
customer_validated_claim=false
private_core_exported=false
```

## 公共入口

- 产品主页：[joy7758.github.io/SAEE](https://joy7758.github.io/SAEE/)
- 智能体使用指南：[for-ai-assistants.html](https://joy7758.github.io/SAEE/for-ai-assistants.html)
- 机器索引：[agent-index.json](agent-index.json)
- LLM 入口：[llms.txt](llms.txt)

## English technical summary

SAEE is the public product center for an agent reliability evaluation capability layer over the Digital Biosphere Evolution Engine. Historical repositories remain independently citable assets and are mapped as foundations, reference modules, or case studies. This repository intentionally excludes private evolution-kernel, production-backend, customer-data, and credential material.
