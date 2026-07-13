# SAEE Pilot Execution Readiness Review v0.1

当前审查结论：`NO_GO`；`execution_started=false`。

```text
Readiness Review ≠ Pilot Execution
GO/NO-GO Decision ≠ Validation Result
Preparation Complete ≠ Experiment Successful
NO_GO ≠ Experiment Failure
```

本机制服务于 SAEE 数字生物圈进化引擎的 `Global Sensing`、`Sandbox Development`、`Pareto Fitness Evaluation` 和档案/回滚免疫系统。它是试点前停止门，不是审计优先重构或执行许可。

## 1 Purpose

就绪审查在未来试点执行前判断数据、治理、技术、标注和安全前提是否满足。审查可以正确输出 `NO_GO`；这表示不应启动，不表示实验失败，也不产生实验结果。

机器可读真源为 `agent-interface/evaluation/saee-pilot-readiness-review.v0.1.json`。所有决定由 requirement 重新计算，不直接相信声明的 decision。

## 2 Readiness Dimensions

维度 `READY` 只表示该维度在本地审查中列出的必需控制面已有证据引用，不等于整体 GO、试点批准或现实有效性。

### A. Dataset Readiness

检查：source identified、ownership clear、permissions approved、schema frozen、sample availability。

当前 `NOT_READY`：未选择来源，所有权与权限未批准，schema 未冻结，没有批准的 sample。

### B. Privacy and Governance Readiness

检查：privacy review、sensitive data assessment、retention policy、deletion procedure、access control。

当前 `NOT_READY`：PR-11 清单仍为未审查，没有隐私、保留、删除和访问批准证据。

### C. Technical Readiness

检查：environment declared、local reproducibility verified、controlled evaluation pipeline tested、artifact version fixed。

当前 `READY` 仅限本地合成验证控制面：环境声明、复现 smoke、PR-10 controlled prototype 和研究 artifact manifest 已存在并通过本轮回归。这不证明 pilot-specific fixed environment、外部复现或真实数据管线。

### D. Annotation Readiness

检查：codebook frozen、instructions prepared、review process defined、agreement measurement planned。

当前 `NOT_READY`：说明、复核和一致性计划已定义，但码本仍是 `draft_not_approved`，未冻结。

### E. Safety Readiness

检查：sandbox policy、network policy、external execution policy、stop conditions。

当前 `READY` 仅表示安全规则已在 [SAEE_PILOT_EXECUTION_SAFETY_GATE.md](SAEE_PILOT_EXECUTION_SAFETY_GATE.md) 文件化。该安全门自身仍保持 `STOP`，因为整体数据和隐私前提不满足；本维度 READY 不会覆盖 STOP。

## 3 Decision Rules

### `GO`

所有 mandatory requirement 均为 satisfied，五个维度均为 `READY`。`GO` 仍只是审查结论；具体执行需要独立授权记录。

### `CONDITIONAL_GO`

仅当全部未完成项同时满足：非 critical、明确标记 `conditional_go_allowed=true`，才可输出。条件必须保留在结果中，不能静默忽略。

### `NO_GO`

以下任一情况触发：

- critical requirement 缺失；
- mandatory 且不可延期的 requirement 缺失；
- 数据所有权、权限、隐私、安全或复现要求不完整；
- matrix 内维度状态、missing list 或声明 decision 与计算结果不一致。

若 `execution_started=true` 且没有批准，返回 `PILOT_EXECUTION_WITHOUT_APPROVAL`；readiness review 发现 execution 已开始也会拒绝。`external_validation_completed=true` 同样被拒绝，因为本机制不能产生外部验证。

当前为 `NO_GO`，关键原因是没有获批数据集、所有权/权限证据和完成的隐私审查。

## 4 Readiness Matrix

| Dimension | Status | Evidence Required | Current State |
|---|---|---|---|
| Dataset | `NOT_READY` | 来源、所有权、权限、冻结 schema、批准 sample | 全部未满足 |
| Privacy | `NOT_READY` | 隐私、敏感数据、保留、删除、访问审批 | 全部未满足 |
| Technical | `READY` | 本地环境、复现、controlled pipeline、artifact manifest | 本地合成控制面已引用；不代表真实 pilot |
| Annotation | `NOT_READY` | 冻结码本、说明、复核、agreement 计划 | 仅码本冻结未满足 |
| Safety | `READY` | 沙盒、网络、外部执行、停止规则 | 规则已定义；整体 safety gate 仍 STOP |

当前缺失 11 项，其中数据所有权、权限与隐私项目属于 critical。审查输出：

```text
SAEE_PILOT_READINESS_RESULT
decision=NO_GO
execution_authorized_by_review=false
```

运行本地审查：

```bash
python3 scripts/saee_agent_cli.py review-pilot-readiness \
  --input agent-interface/evaluation/saee-pilot-readiness-review.v0.1.json
```

或：

```bash
make check-saee-pilot-readiness
```

