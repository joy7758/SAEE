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

## 最终客户版本目标

SAEE 与 Agent Evidence Project 完成受控合并后的目标产品族固定为三个客户版本：

```text
SAEE Evidence
      ↓
SAEE Evaluation
      ↓
SAEE Governance
```

- `SAEE Evidence`：证据对象、收据、来源、完整性与免疫档案。
- `SAEE Evaluation`：就绪度、证据充分性、可靠性与选择上下文。
- `SAEE Governance`：受控变更、决策边界、演化档案与回滚治理。

这是最终目标，不是当前发布事实。当前 product registry、capability inventory 与
truth boundary 仍保持权威；三个版本尚不得宣称全部实现、客户验证、发布或生产就绪。

当前主线是受控完成 SAEE 与 Agent Evidence 的合并；利用 SAEE 监督和测试合并过程
属于副线 Dogfooding，不得取代主线或自我授权。

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
- Agent Evidence Project（历史 `Agent Evidence Receipt` / `agent-evidence-layer`）归属该子系统，提供待迁移的 receipt、integrity、provenance 与 source-completeness 实现来源；不得形成第二套平行 evidence stack。
- Capability Runtime：复用规范服务的本地调用路由。
- MCP / HTTP：运输适配器，不产生信任或授权。
- Cloud Mappings：候选映射和受控研究入口，不代表官方集成。

## 非目标

SAEE 不是 Agent OS、通用多智能体工作流、授权系统、安全认证机构或自动部署控制器。

当前合并边界：`constitutional_ownership=implemented`，`source_code_migrated=false`，`runtime_integrated=false`，`external_integration_validated=false`，`customer_validated=false`，`product_launched=false`，`production_ready=false`。能力实现状态仍只从 `capability-package/manifest.json#canonical_inventory` 读取。

## English technical summary

SAEE exposes an agent-facing reliability capability projection over the Digital Biosphere Evolution Engine. Rehearsal, reliability, evidence, runtime and transport surfaces remain bounded modules. Evidence and audit support evolutionary selection and rollback; they do not replace the evolutionary core.
