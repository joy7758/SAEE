# OpenTelemetry 风格候选证据映射 v0.1

## 定位

OpenTelemetry 对观察模型调用、工具调用、资源引用和时间信息很有价值。但轨迹由运行系统产生，字段存在并不自动证明身份真实、资源真实、授权有效、人工批准真实或事件具有法律责任意义。

本功能只接受仓库内定义的 `synthetic_opentelemetry_style` 合成事件。名称表示“OpenTelemetry 风格字段”，不是 OpenTelemetry SDK 集成，也不构成兼容或合规声明。

“OpenTelemetry traces provide observations. SAEE evaluates whether additional evidence relationships are sufficient to support an accountability claim.”

“OpenTelemetry轨迹提供系统观察结果。SAEE评估这些观察结果是否结合其他证据关系，足以支持一个责任声明。”

## 数据流

```text
合成 OpenTelemetry 风格轨迹
        ↓
候选字段提取
        ↓
SAEE Evidence Adequacy Profile
        ↓
剖面需求 PASS / FAIL
        ↓
accountability_claim_established=false
```

映射器提取可观察字段，例如：

- `agent.id` → 候选 `agent_id`
- `action.type` → 候选 `action_type`
- `tool.name` → 候选 `tool_name`
- `resource.reference` → 候选 `resource_reference`
- `observed_timestamp` → 候选 `timestamp`
- `human.id` → 候选人类身份声明

“候选”意味着这些值只能进入下一阶段检查，不能被当成身份、授权或真实性证明。

## 映射结果和充分性结果必须分开

`trace_mapping_result` 判断轨迹输入是否闭合、是否包含最小智能体和动作上下文：

- `PASS`：关键观察字段可提取；
- `PARTIAL`：有最小上下文，但缺少资源等观察字段；
- `FAIL`：输入不闭合、缺少智能体或动作上下文，或声称授权却没有策略决定引用。

即使 `trace_mapping_result=PASS`，`adequacy_result` 仍可以且通常应为 `FAIL`。例如资源检索轨迹可能提供智能体、工具和资源引用，但仍缺少：

- 发布者身份材料；
- 内容摘要；
- 策略决定对象；
- 资源解析收据完整性；
- 独立身份或授权验证材料。

CLI 成功退出只表示候选映射成功或部分成功，不表示充分性通过。

## CLI

```bash
python3 scripts/saee_agent_cli.py evaluate-trace-candidate \
  --profile RESOURCE_AUTHENTICITY \
  --input agent-interface/examples/otel-mapping/trace_candidate_resource_retrieval.json
```

映射 `PASS` 或 `PARTIAL` 返回退出码 `0`；映射 `FAIL` 返回退出码 `2`。输出同时包含：

- `mapping`
- `adequacy_evaluation`
- `trace_mapping_result`
- `adequacy_result`
- `missing_requirements`
- `accountability_claim_established=false`

聚焦验证：

```bash
python3 scripts/saee_otel_candidate_mapping_smoke.py
```

## 失败即脱敏

输入被拒绝时，映射器不会在错误输出中回显已观察的 agent、resource、tool 或其他候选值。失败输出只保留固定占位元数据和稳定原因码，防止无效轨迹把敏感标识带入日志。

## 当前限制

- 没有导入或配置 OpenTelemetry SDK。
- 没有连接 LangChain、CrewAI 或其他智能体框架。
- 没有网络、DNS、资源检索、URI 核验或工具执行。
- `resource.reference` 只作为不可信观察字符串，不做 URI 真实性判断。
- `authorization.claimed=true` 不是授权证据；即使同时观察到 `policy.decision_ref`，仍必须提供完整策略决定对象才能满足充分性剖面。
- `human.id` 只是轨迹中的身份声明，不证明真实人类参与。
- 不形成 OpenTelemetry 合规、IETF 兼容、安全认证、法律事实或生产就绪声明。

该映射属于 Global Sensing 到演化档案／回滚免疫系统之间的受控候选入口，不改变 SAEE 数字生物不能直接执行外部世界的边界。
