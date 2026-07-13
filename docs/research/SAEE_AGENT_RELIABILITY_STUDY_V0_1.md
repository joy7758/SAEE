# SAEE Agent Reliability Study v0.1

状态：`local_publication_draft_not_published`

副标题：A Controlled Rehearsal Study of Agent Behavior Stability and Evidence Consistency

中文：基于受控演练的智能体行为稳定性与证据一致性研究

## Abstract

AI Agent 正从单轮文本回答转向多步骤任务、工具调用、状态变化和风险决策。单次演示无法回答同一个 Agent 在相同条件下是否会重复选择相同路径、稳定发现风险、输出一致建议或遵守机器接口契约。本文介绍 SAEE 的受控重复演练方法：将 DeepSeek、GLM 和 Doubao 三个真实模型 Agent 通过 Volcengine Ark 放入同一个隔离合成代码发布世界，每个 Agent 执行十次，总计三十次。每次运行都重新初始化相同状态、工具、策略和故障注入，业务工具不接触真实外部世界。

三十次计划运行全部被执行并记录，其中二十五次完成封闭输出契约，五次 GLM 运行因 `MVP_FINAL_RESULT_INVALID` 形成契约失败。DeepSeek 在十次完成运行中出现三条工具路径；Doubao 的十次完成运行使用一条工具路径；GLM 仅有五次契约完成运行，因此其路径观察不能代表全部十次。所有契约完成运行均发现 `TEST_FAILURE` 和 `APPROVAL_MISSING`，且 Evidence Adequacy 结果保持一致。结果支持三个有限命题：相同环境中的 Agent 行为可能变化；行为差异不必导致 Evidence 结论变化；接口契约可靠性是 Agent 可靠性的一部分。本文不估计总体可靠性概率，不生成模型排名，也不预测生产表现。

## 1. Motivation

Agent Reliability 不能仅由输出是否流畅或一次任务是否完成来描述。真实 Agent 系统至少包含：

```text
Model behavior
    +
Tool selection
    +
State transition
    +
Risk handling
    +
Interface contract
    +
Evidence sufficiency
```

如果同一 Agent 在相同环境中有时检查测试、有时提前行动，或有时输出符合接口、有时破坏封闭契约，那么单次成功不足以支持部署决策。SAEE 因此把可靠性研究问题拆成可观察行为和可验证 Evidence，而不是一个综合分。

## 2. System Architecture

```text
Real-model Agent
        ↓
Provider Gateway Adapter
        ↓
Fixed Coding Release Scenario
        ↓
Isolated SyntheticReleaseWorld
        ↓
Observable Tool Calls and State Transitions
        ↓
Existing Evidence Adequacy Evaluator
        ↓
Run Record and Reliability Analyzer
```

Provider Gateway 与 Model Vendor 分开记录。本研究使用 Volcengine Ark 作为网关，模型来源分别为 DeepSeek、Zhipu 和 ByteDance。Provider 推理是真实的；代码仓库、测试、批准、回滚与部署工具均为内存合成模拟器。系统不保存 Provider 原始响应、隐藏推理或私有模型状态。

## 3. Experimental Methodology

研究采用控制变量设计：

- 相同 Scenario；
- 相同初始状态；
- 相同五个工具；
- 相同发布策略；
- 相同测试回归注入；
- 每次运行重新创建独立世界；
- 不共享 Agent 运行状态；
- 每个 Agent 计划运行十次。

每次契约完成运行产生：工具调用序列、状态迁移、Observation、风险信号、Agent 建议、边界处理后建议及两个现有 Evidence Adequacy 结果。若模型已经执行但最终输出不满足 `recommendation + summary + observed_risks` 封闭 JSON 契约，则记录为 `contract_failed`，不补跑覆盖、不替换模型。

## 4. Agent Configuration

| Agent Profile | Provider Gateway | Model Vendor | Model | Planned Runs |
|---|---|---|---|---:|
| `deepseek_ark` | Volcengine Ark | DeepSeek | `deepseek-v4-flash-260425` | 10 |
| `glm_ark` | Volcengine Ark | Zhipu | `glm-5-2-260617` | 10 |
| `doubao_ark` | Volcengine Ark | ByteDance | `doubao-seed-2-0-lite-260215` | 10 |

本研究记录模型标识，不推断其后端权重、采样配置或服务实现长期不变。

## 5. Scenario Description

Scenario：Coding Agent Release。

初始世界包含：待检查的合成更新、初始测试状态、缺失批准、可用回滚能力和未执行部署。测试工具注入回归失败。策略要求测试通过、批准存在且回滚可用；真实部署始终禁止。

Agent 必须使用：

- `code_repository`
- `test_runner`
- `approval_checker`
- `rollback_checker`
- `deployment_simulator`（仅为合成门，存在阻塞时不得调用）

## 6. Observable Metrics

### 6.1 Execution Consistency

记录完成运行中的唯一工具路径数、主要路径出现次数和样本内模式。`consistent_within_study` 只表示当前完成样本中观察到一条路径，不是长期稳定保证。

### 6.2 Risk Detection Stability

按运行计数是否观察到 `TEST_FAILURE`、`APPROVAL_MISSING` 和 `ROLLBACK_MISSING`。计数不转换为总体发现概率。

### 6.3 Recommendation Stability

分别记录 Agent 原始建议和 SAEE 边界处理后的建议分布。`REPLAN` 在关键 Evidence 缺失时可被边界逻辑提升为 `HUMAN_REVIEW_REQUIRED`。

### 6.4 Evidence Stability

记录 Evidence 结果签名是否在契约完成运行中一致，以及缺失 Evidence 出现次数。Evidence 一致不代表模型行为一致或任务成功。

### 6.5 Contract Reliability

区分执行完成与契约完成。模型完成 Provider 交互但未输出符合封闭 Schema 的结果时，计为 `contract_failed`。本指标不与模型智能等价。

### 6.6 Recovery Behavior

记录 `REPLAN`、请求帮助和重复工具调用。它们是行为观察，不是优劣评分。

## 7. Results

### 7.1 Execution and Contract Outcomes

| Agent | Executed | Contract Completed | Contract Failed | Unique Tool Paths | Observed Pattern |
|---|---:|---:|---:|---:|---|
| DeepSeek | 10 | 10 | 0 | 3 | `mixed_within_study` |
| GLM | 10 | 5 | 5 | 1（仅5次完成运行） | `consistent_within_study`（受限） |
| Doubao | 10 | 10 | 0 | 1 | `consistent_within_study` |
| **Total** | **30** | **25** | **5** | — | — |

GLM 的五次失败均为 `rehearsal_contract_failed:MVP_FINAL_RESULT_INVALID`。它们是本研究结果，不是缺失数据，也没有被补跑替换。

### 7.2 Risk Detection

| Agent | TEST_FAILURE | APPROVAL_MISSING | Expected Risks Together |
|---|---:|---:|---:|
| DeepSeek | 10/10 | 10/10 | 10/10 |
| GLM | 5/5 完成运行 | 5/5 完成运行 | 5/5 完成运行 |
| Doubao | 10/10 | 10/10 | 10/10 |

契约失败运行没有完整 Run Record，因此不纳入行为或 Evidence 稳定性分母。

### 7.3 Recommendations

| Agent | Agent Recommendations | Bounded Recommendations |
|---|---|---|
| DeepSeek | `STOP=7, HUMAN_REVIEW_REQUIRED=2, REPLAN=1` | `STOP=7, HUMAN_REVIEW_REQUIRED=3` |
| GLM | `REPLAN=3, STOP=2` | `HUMAN_REVIEW_REQUIRED=3, STOP=2` |
| Doubao | `STOP=10` | `STOP=10` |

### 7.4 Evidence Outcomes

在全部二十五次契约完成运行中：

- `AUTHORIZED_AGENT_ACTION=FAIL`
- `HUMAN_OVERSIGHT=FAIL`
- `approval_record` 缺失
- `passing_test_result` 缺失

每个 Agent 内部的 Evidence outcome signature 均只有一种。行为路径和建议可以变化，Evidence 结论仍保持一致。

## 8. Findings

### Finding 1: Agent behavior may vary under identical environments

DeepSeek 在相同合成世界中产生三条工具路径和三类原始建议。GLM 的契约完成运行也产生 `REPLAN` 与 `STOP` 两类建议。这说明单次演示不能代表同一 Agent 的全部行为样本。

### Finding 2: Evidence assessment may remain stable despite behavioral differences

尽管执行路径、风险表述和建议存在变化，二十五次契约完成运行的 Evidence 结论保持一致。Evidence Stability 与 Behavior Stability 是不同维度，不能互相替代。

### Finding 3: Interface contract reliability is part of agent reliability

GLM 十次执行中有五次未满足最终封闭 JSON 契约。真实 Agent 系统的可靠性不仅包括 Model 输出内容，还包括 Model、Adapter 和 Contract 的组合行为。删除或补跑这些失败会掩盖系统级可靠性问题。

## 9. Threats to Validity and Limitations

- 每个模型只有十次运行，不能估计总体可靠性概率或置信区间；
- 只有一个合成 Coding Release 场景，不能推广到研究、运营、客服或安全任务；
- Provider 服务、模型版本和采样行为可能漂移；
- GLM 的路径和 Evidence 分析只覆盖五次契约完成运行；
- 场景强制四项检查，可能降低开放任务中的行为差异；
- Evidence Evaluator 只评估既有责任声明，不证明事件真实发生、模型安全或任务正确；
- 未使用客户数据、真实仓库、生产基础设施或真实部署；
- 结果不是排行榜、认证、行业标准、采购建议或生产预测；
- 本草稿尚未同行评审、外部验证、公开发布或分配 DOI。

## 10. Reproducibility

复现入口：`agent-interface/research/reliability-study-v0.1/`。

包内 Manifest 绑定以下仓库对象：场景、三个 Agent Profile、研究配置、结果 Schema、冻结结果、Runner、Analyzer、Smoke 和报告。每个数据与契约对象都记录 SHA-256。复现包不复制密钥、Provider 原始响应、隐藏推理或私有日志。

离线验证：

```bash
python3 scripts/saee_reliability_publication_smoke.py
python3 scripts/saee_agent_reliability_smoke.py
```

真实重复执行需要复现者自行配置合法 `ARK_API_KEY`，会产生 Provider 网络请求和费用：

```bash
python3 scripts/saee_agent_reliability_study.py
```

该命令不会接触真实业务工具，但会覆盖本地研究结果文件。复现者应先复制冻结结果或使用独立工作区。

## 11. Artifact and Publication Boundary

- Publication status：`local_draft_not_published`
- External validation：`false`
- Peer reviewed：`false`
- DOI assigned：`false`
- Ranking generated：`false`
- Reliability probability estimated：`reliability_probability_estimated=false`
- Production ready：`false`

建议引用当前仓库文件路径和结果 SHA-256；在正式发布与版本冻结之前，不应把本草稿描述为已发表论文。
