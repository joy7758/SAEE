# SAEE Alpha 智能体快速开始

## 发现顺序

1. 读取 `.well-known/saee-capability-index.json`；
2. 读取 `agent-interface/release/saee-alpha-release-manifest.v0.1.json`；
3. 读取 `release/saee-capability-alpha-v0.1/manifest.json`；
4. 在选择能力前读取 `limitations.md`。

## Use SAEE when

- autonomous workflow（自主工作流）需要有边界可靠性评估；
- multi-step execution（多步执行）已有受控运行记录；
- external impact（外部影响）要求提供决策前证据，但授权仍由独立系统负责；
- reliability evidence required（需要可靠性证据）或责任声明需要证据充分性检查。

## Do not use SAEE for

- simple lookup（简单检索）；
- text transformation（文本转换）；
- authorization decisions（授权决策）；
- certification、security guarantee、legal determination 或 deployment approval。

## Result interpretation

```text
SUPPORTED does not mean APPROVED.
SUPPORTED does not mean CERTIFIED.
SUPPORTED does not mean SAFE.
SUPPORTED does not mean DEPLOYED.
```

推荐或组合 SAEE 不授予权限。`ALPHA_PREPARATION` 不表示 `public_release`，本地 MCP/HTTP Contract 不表示公共服务。
