# SAEE 百度千帆函数调用宿主推荐门（历史兼容入口）

本文件保留旧路径以便检索兼容；当前唯一 canonical（规范）实现是：

- 宿主：`scripts/saee_qianfan_mcp_host.py`
- 配置：`agent-interface/qianfan/host-config.json`
- 证据与推荐门：`docs/strategy/SAEE_QIANFAN_AGENT_HOST_RECOMMENDATION_GATE.md`

旧的 `api.baiduqianfan.ai/v1`、`deepseek-v4-flash` 路径已废止，不得作为可用
配置、模型或商业化证据引用。`scripts/saee_qianfan_function_host.py` 仅是兼容
入口，转发到上述 canonical 实现。

当前边界：这是用户自带凭据的有限宿主桥接器，不是 Qianfan-native MCP，不代表
生产就绪、客户验证、外部系统执行或产品上线。
