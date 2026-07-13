# SAEE Review Report Traceability v0.1

## 目标

本文件说明本地合成审查报告中的每一项 Finding（审查发现）如何回溯到仓库内证据引用和 Evidence Adequacy Profile（证据充分性剖面）。它服务于可解释性和复核，不赋予报告认证、合规、安全或部署决定效力。

## 可追溯链

```text
Finding
  ↓
Evidence Reference
  ↓
Adequacy Profile
  ↓
Missing Requirement
  ↓
Report Statement
```

| 层级 | 报告字段 | 含义 | 不代表 |
|---|---|---|---|
| Finding | `claim_assessments[].assessment` | 对指定责任声明的证据充分性判断 | 系统整体安全或可部署 |
| Evidence Reference | `supporting_evidence[]` | 本次判断引用的仓库内合成证据文件 | 外部真实性已经验证 |
| Adequacy Profile | `adequacy_profile_ref` | 判断所依据的证据要求集合 | 法律或监管标准 |
| Missing Requirement | `missing_requirements[]` | 支持责任声明仍缺少的证据 | 已经证明系统不安全 |
| Report Statement | `assessment_statement*` | 面向人类阅读者的边界化表述 | 自动风险决定或批准 |

## 映射规则

- `PASS` 仅映射为 `SUPPORTED`，并限定在声明的本地合成审查范围内。
- `FAIL` 映射为 `INSUFFICIENT_EVIDENCE`，必须携带至少一个缺失要求。
- `UNKNOWN` 映射为 `UNKNOWN`，不得被提升为支持、拒绝或批准。
- 输入中的 Observation、Evidence Package 和 Adequacy Profile 引用必须原样或排序去重后保留。
- 生成器不得补造证据、推断客户状态或生成认证、合规、安全、批准措辞。

## 当前边界

本映射验证的是信息能否从合成 Evidence Adequacy 输出稳定进入审查报告。它不验证引用文件中的声明在外部世界真实成立，也不把 Observation 自动提升为 Evidence。
