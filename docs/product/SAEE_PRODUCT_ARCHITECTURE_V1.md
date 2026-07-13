# SAEE 产品架构 v1

## SAEE Product Architecture v1

## 正式身份

```text
SAEE = Silicon-Amplified Evolutionary Ecology
Engineering Core = Digital Biosphere Evolution Engine
```

面向 Agent 生态的产品能力层：

```text
Agent Reliability Evaluation Capability Layer
智能体可靠性评估能力层
```

## 架构

```text
Agent / Repository / Experiment / Product Prototype
                    ↓
        Digital Biosphere Evolution Engine
                    |
     +--------------+----------------+
     |              |                |
Rehearsal       Reliability      Evidence / Immune
Engine          Evaluation       Subsystem
     |              |                |
     +--------- Capability Runtime --+
                    |
             MCP / HTTP Interfaces
                    |
          Bounded Cloud Mappings
```

## 模块责任

- Rehearsal Engine：反事实模拟、状态环境与沙盒发育。
- Reliability Evaluation：执行、恢复、边界和证据可靠性评估。
- Evidence / Immune Subsystem：证据充分性、收据、回滚与可复核档案。
- Capability Runtime：复用规范服务的本地调用路由。
- MCP / HTTP：运输适配器，不产生信任或授权。
- Cloud Mappings：候选映射和受控研究入口，不代表官方集成。

## 非目标

SAEE 不是 Agent OS、通用多智能体工作流、授权系统、安全认证机构或自动部署控制器。

## English technical summary

SAEE exposes an agent-facing reliability capability projection over the Digital Biosphere Evolution Engine. Rehearsal, reliability, evidence, runtime and transport surfaces remain bounded modules. Evidence and audit support evolutionary selection and rollback; they do not replace the evolutionary core.
