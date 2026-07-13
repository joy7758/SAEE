# Generic Framework Agent Example

`generic_agent_adapter.py` 使用依赖注入表示任意 Agent Framework 的决策点，不安装或声称支持 LangGraph、CrewAI、OpenAI Agents SDK 等具体框架。

调用者注入本地 MCP 或 HTTP invocation function，Adapter 只将结果映射为：`CONTINUE`、`REPLAN`、`HUMAN_REVIEW_REQUIRED`、`STOP`。

