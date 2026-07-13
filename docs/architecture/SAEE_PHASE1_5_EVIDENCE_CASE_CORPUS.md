# SAEE Phase 1.5 Evidence Case Benchmark Corpus v0.1

状态：`implemented_local_synthetic_corpus_only`。

中文名称：SAEE 证据案例基准库 v0.1。

## 1. 目标

Phase 1 已证明单个 Case 可以完成本地合成闭环。Phase 1.5 不扩展架构，而是验证同一转换链能否覆盖多类失败压力：

```text
Evaluation Input Object
        ↓
Existing SAEE Case Builder
        ↓
Derived Evidence Case Object
        ↓
Transformation Integrity Check
```

完成标准是五个严格输入、五个派生对象、五份有效报告和零边界违规，不是简单增加 JSON 数量。

## 2. 两阶段对象模型

### Stage A：Evaluation Input Object

Source Case 严格遵循 `saee-evidence-case.v0.1.schema.json`：

```text
identity
task_contract
environment_contract
candidates
observations
evidence_packages
risk_policy
truth_boundary
```

根对象还包含 schema marker、version、case ID、status 和 timestamp。`additionalProperties=false` 保持不变。Source Case 不允许出现 `evaluation`、`risk` 或 `decision`。

### Stage B：Derived Evidence Case Object

现有 `saee_evidence_case.py` 生成：

```text
identity
task_contract
environment
agent_reference
observation
evaluation
evidence
risk
decision
```

输入契约和派生对象不合并。前者定义评测，后者组织评测结果、Evidence Adequacy、风险估计与 Decision Support。

## 3. Corpus 分类

目录：`agent-interface/architecture/examples/phase1_5_cases/`

| Case | Category | 主要压力 |
|---|---|---|
| `case-001-baseline-stability.json` | baseline stability | 正常查询和稳定 follow-up |
| `case-002-context-drift.json` | context drift | 多轮信息遗漏、状态与指令漂移 |
| `case-003-tool-failure.json` | tool failure | timeout、invalid response、missing dependency 的合成声明 |
| `case-004-instruction-conflict.json` | instruction conflict | 用户要求与系统约束冲突 |
| `case-005-adversarial-input.json` | adversarial input | 恶意诱导和越界行为压力 |

所有 Candidate、Observation、Environment 和 Evidence 都是合成声明。Tool Failure Case 不运行工具，也不检查真实依赖。

## 4. Transformation Integrity Check

`scripts/saee_phase1_5_case_corpus_smoke.py` 对每个 Case 验证：

- `identity` 与 `case_id` 被绑定；
- `task_contract` 原样保留；
- `environment_contract` 映射为 `environment`；
- `candidates` 映射为 `agent_reference`；
- `observations` 映射为 `observation` 和 evaluation rows；
- 每条 evaluation 保留 reason、failure class 和 evidence reference；
- `evidence_packages` 与 Adequacy result 一一对应；
- 风险公式按 scenario 重算；
- decision 绑定原 Evidence Contract 和 scenario scope；
- Source truth boundary 在输出继续保持 fail-closed。

## 5. Risk Estimate 边界

Corpus 沿用 Phase 1 reference slice：

```text
R_s = P_s × I_s × X_s × (1 - C_s) + U_s
R_total = Σ_s w_s × R_s
```

每个派生 risk 必须包含：

```text
risk_estimate_not_measurement=true
risk_probability_measured=false
```

数值只是该合成 Case 与本地阈值下的参考估计，不是现实失败概率、经外部校准的 Risk Model 或跨行业通用结论。

## 6. Decision Support 边界

每个派生 decision 必须包含：

```text
scenario_scope=local_synthetic_case_only
automatic_decision=false
customer_execution_authorized=false
```

根 truth boundary 继续保持 `deployment_authorized=false`。`DEPLOY_LIMITED`、`RETEST` 或 `HOLD` 都只是合成场景内的 Decision Support，不是人类或组织的最终部署决定。

## 7. 验证

```bash
python3 scripts/saee_phase1_5_case_corpus_smoke.py
```

完整聚焦门：

```bash
make check-saee-phase1-5-case-corpus
```

期望摘要：

```text
input_cases=5/5
evidence_case_objects=5/5
valid_reports=5/5
transformation_integrity=5/5
boundary_violations=0
```

## 8. 当前限制

- 不修改 canonical architecture 或 `FINAL_ARCHITECTURE_SPEC.md`；
- 不修改 `saee-evidence-case.v0.1.schema.json`；
- 不接入 Runtime、Memory 或 Tool Trace Adapter；
- 不运行真实 Agent、工具、依赖或攻击载荷；
- 不访问网络或客户数据；
- 不形成真实概率、外部 validation、customer validation 或 production readiness；
- 不创建 pilot、商业 API、Dashboard 或网站功能。

## 9. 下一阶段入口

Phase 1.5 通过后先进行只读架构审查，检查 Case Object 稳定性、schema 复杂度、Risk Estimate 边界和 human-in-the-loop。该审查通过也不会自动授权 Phase 2。

