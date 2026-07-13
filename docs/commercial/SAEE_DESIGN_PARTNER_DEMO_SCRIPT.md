# SAEE Design Partner Synthetic Demo Script v0.1

状态：`synthetic_demo_only`。时长建议 6–8 分钟，只能嵌入获批的问题访谈，不是销售演示。

## 开场边界

主持人逐字说明：

> 下面展示的是仓库内合成案例，用于讨论证据复核方法。SAEE 不认证安全或合规，不批准部署，也没有分析任何客户数据。

## Step 1：Show Agent Trace

展示一个合成 Code Agent Tool Execution 场景：Agent 产生了工具调用和结果记录。

询问：仅凭这些记录，你会如何判断该动作是否经过授权、所用资源是否可信、是否存在充分人工监督？

边界：Trace 只表示系统观察到的记录，不自动成为 Evidence。

## Step 2：Show Evidence Gap

展示三个缺失项：

- `publisher_identity`
- `content_digest`
- `approval_context`

解释：缺失项表示当前材料不足以支持相应责任声明，不表示系统不安全，也不表示事件没有发生。

## Step 3：Show SAEE Review Report

打开：`docs/commercial/SAEE_SYNTHETIC_EVIDENCE_REVIEW_REPORT_EXAMPLE.md`。

依次展示：

1. `AUTHORIZED_AGENT_ACTION = SUPPORTED`；
2. `RESOURCE_AUTHENTICITY = INSUFFICIENT_EVIDENCE`；
3. `HUMAN_OVERSIGHT = INSUFFICIENT_EVIDENCE`；
4. 每项 Finding 对应的 Evidence Reference、Adequacy Profile、Missing Requirement 和 Reason Code。

不展示排行榜，不把 `SUPPORTED` 解释为系统整体通过。

## Step 4：Explain Boundaries

逐字说明：

> SAEE 在这里评估的是限定责任声明的证据充分性。它不验证真实发布者、身份或事件，不提供安全认证、监管合规、法律判断或部署授权。

然后进入中性提问：

- 哪一部分最接近你们当前的复核工作？
- 哪一部分无法进入你们的流程？
- 为了复核这项 Finding，你还需要看到什么？

## 停止条件

出现以下情况立即停止 Demo：参与者尝试提交私有日志、生产 trace、凭据、客户数据或个人信息；要求把 Demo 当作认证、合规、安全或部署结论；或撤回参与同意。
