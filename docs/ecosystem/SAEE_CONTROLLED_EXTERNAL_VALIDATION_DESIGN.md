# SAEE Phase 12 受控外部验证设计 v0.1

## 1. Validation objectives

未来验证只回答：在明确参与者、版本、范围和受控环境下，SAEE 能力能否被发现、集成、正确解释并保持边界。它不测量采用、市场、客户成功或生产可靠性。

## 2. Participant categories

允许的类别为 `agent_framework`、`developer`、`research_group`、`cloud_platform`。类别不是授权；每个真实参与者必须拥有独立、可撤销、限范围的 `AUTHORIZED_FOR_VALIDATION` 记录。当前 `participants_authorized=0`。

## 3. Validation scope

允许：能力发现测试、受控集成测试、结果解释测试和结构化兼容反馈。

禁止：生产执行、客户数据访问、私有系统访问和任何外部副作用。授权不得由 Capability Manifest、Dry Run PASS 或智能体推荐自动推导。

## 4. Allowed evidence

- test execution record；
- compatibility result；
- structured feedback；
- version information。

所有证据必须绑定参与者 ID、范围、版本和限制，并通过数据最小化检查。

## 5. Forbidden evidence

禁止客户成功或采用声明、安全认证、生产可靠性声明、私有日志、私有 prompt、凭据、客户数据和 chain of thought。

## 6. Exit criteria

只有已授权参与者完成批准范围、形成结构化证据、记录限制且无边界违规时，单次验证才可标记为 `VALIDATION_SCOPE_COMPLETED`。该状态不升级生产、市场、认证或采用真值。

## 7. Rollback and termination conditions

凭据暴露、收到客户数据、未授权执行、虚假采用声明或其他边界违规必须立即停止。冻结证据接收，隔离最小化记录，撤销本次范围，并转入人工授权的事故处理；不得自动重试或扩大权限。

## Agent-readable flow

```text
Participant Authorization
  -> Scope Contract
  -> Controlled Test
  -> Evidence Allowlist
  -> Exit Criteria OR Immediate Termination
```

`external_validation_design=true` 只表示设计完成，不表示验证执行。

