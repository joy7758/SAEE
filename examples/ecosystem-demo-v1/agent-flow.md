# Agent Flow：为什么调用 SAEE

## 1. Agent 接收任务

自主编码智能体收到“修改模块并准备发布候选版本”的合成任务。任务包含潜在外部影响，因此不能只依赖任务完成信号。

## 2. Agent 发现 SAEE

Agent 从 Capability Package 或 MCP Entry Package 发现：

- `evaluate_rehearsal_run`：检查受控运行记录的可靠性上下文；
- `evaluate_evidence`：检查一个责任声明是否满足固定证据剖面；
- `rehearse_agent`：当前仍为 `CONTRACT_ONLY`。

## 3. Agent 使用 `evaluate_rehearsal_run`

Agent 提交本地合成的受控运行记录。SAEE 复用 canonical Agent Reliability Service，不重新实现评分逻辑。

## 4. SAEE 返回有边界上下文

结果指出测试证据缺失、恢复计划不足。它不判断软件“安全”，也不授予发布权限。

## 5. Agent 评估证据充分性

Agent 使用 `evaluate_evidence` 检查责任声明。`SUPPORTED` 只表示固定 profile requirements（剖面要求）满足；证据缺失时应保留 reason codes 和 missing requirements。

## 6. Agent 调整行为

允许的下一步只有：

- `CONTINUE`：当前范围内继续下一轮验证；
- `REPLAN`：补充计划或证据后重新演练；
- `HUMAN_REVIEW_REQUIRED`：重大外部动作需要独立授权；
- `STOP`：当前边界不支持继续。

本场景选择 `REPLAN`：先补齐测试证据和恢复计划，再进入下一轮。它不是部署决定。
