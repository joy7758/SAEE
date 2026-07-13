# Scenario Template

```yaml
scenario_id: synthetic-example
agent_reference: local-agent-reference
workflow:
  objective: "描述要完成的业务目标"
  steps: []
environment:
  type: local_synthetic
  allowed_tools: []
  forbidden_actions: []
expected_observations: []
accountability_claims: []
truth_boundary:
  customer_data: false
  external_world_actions: false
  deployment_authorized: false
```

场景必须明确成功条件、失败条件、工具边界和证据要求。模板本身不授权执行。

