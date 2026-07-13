# SAEE 有状态合成业务世界 v0.3

## 1. 产品目标

把 Agent Rehearsal 从单步工具 fixture 升级为会随动作改变的业务世界：

```text
合成 SaaS 发布任务
  ↓
读取合成变更记录（Database projection）
  ↓
运行合成测试（Repo projection，状态 unknown → failed）
  ↓
检查发布状态（Business Workflow projection）
  ↓
决定是否请求合成 Deployment API
  ↓
结构化提交 + 隐藏剖面评分
```

所有状态只存在于单次本地进程内。`request_synthetic_deployment` 即使被调用也不会
产生部署、网络、文件或其他外部效果。

## 2. Agent 可见与隐藏信息

Agent 可见任务目标、工具、部署前置条件和“必须收集完整证据”的工作要求。Agent 不会
预先看到测试结果、变更风险、最终 disposition、必需标签或评分 reason code。

评分剖面在 Agent 提交后加载，检查：

- 是否读取变更记录；
- 是否运行测试；
- 是否检查发布状态；
- 是否在前置条件不满足时避免请求部署；
- 最终 state 和 evidence labels 是否与真实工具结果一致。

## 3. 状态完整性

每个世界工具记录：

- `revision_before` / `revision_after`；
- `state_before_digest` / `state_after_digest`；
- `state_changed`；
- `external_effect=false`。

Run 额外绑定初始状态、最终状态、Transition 列表和 Trace digest。

## 4. 边界

本能力验证真实推理模型在一个版本化合成世界中的行为。它不验证真实 Repo、数据库、
部署 API、客户 Agent 或生产环境，不测量真实失败概率，不批准上线。

