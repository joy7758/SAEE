# SAEE Alpha 开发者快速开始

SAEE Alpha provides capability contracts and local invocation patterns. It does not provide public production services.

SAEE Alpha 提供能力契约和本地调用方式，不提供公网生产服务。

## 1. SAEE 提供什么

- `saee.agent-reliability`：受控运行记录的本地可靠性评估；
- `saee.evidence-evaluation`：封闭证据包的证据充分性评估；
- `rehearse_agent` 目前仅为契约，不可视为已实现服务。

这些能力是 Digital Biosphere Evolution Engine 的外部能力投影，不改变项目核心。

## 2. 如何发现

```text
.well-known/saee-capability-index.json
  -> agent-interface/release/saee-alpha-release-manifest.v0.1.json
  -> release/saee-capability-alpha-v0.1/manifest.json
```

## 3. 如何本地调用

- Python Runtime：`saee_backend/services/capability_runtime/capability_invocation.py`
- MCP stdio：`python3 scripts/saee_capability_mcp_stdio.py`
- localhost HTTP demo：`python3 scripts/saee_capability_http_demo.py`

以上入口仅限本地 Alpha；没有公共 endpoint。

## 4. 如何解释结果

- `SUPPORTED` 仅表示指定证据剖面得到支持；
- `INSUFFICIENT_EVIDENCE` 仅表示当前证据不足；
- Receipt 记录调用元数据，不建立外部信任；
- 结果不能转换为授权、认证、安全保证或部署批准。

## 5. 如何验证

```bash
python3 scripts/saee_capability_alpha_release_smoke.py
```

## 6. 限制

当前未公开发布、未提供公共 API/服务、未上架 Marketplace、未获得客户验证、未建立外部采用，也未达到生产就绪。
