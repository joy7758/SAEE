# 验证计划

## 前置状态

当前只定义未来流程。开始任何真实验证前，必须另行获得外部验证授权，并重新确认参与者、数据、网络和执行边界。

## 固定测试范围

1. `capability_discovery`：从公开安全的机器入口定位 SAEE。
2. `mcp_tool_discovery`：识别三个工具及其实现状态。
3. `local_invocation`：仅以合成数据调用本地能力。
4. `result_interpretation`：不把结果解释为批准、认证、安全或部署。
5. `documentation_feedback`：评价用途、限制和组合方式是否清晰。

## 固定场景

复用 `examples/ecosystem-demo-v1/scenario/coding-agent-preflight.json`。未来验证者只需判断发现、调用和解释链是否清晰，不接触客户或生产系统。

## 禁止范围

- `production_execution`
- `customer_data`
- `private_system_access`
- `external_side_effects`

## 证据输出

未来若获得授权，只允许生成结构化发现结果、本地 invocation result、结果解释选择和四类反馈枚举。当前不生成这些外部证据。
