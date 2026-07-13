# SAEE Capability Alpha Release Review v0.1

## A. Release purpose

将 Phase 10.1–10.7 已有能力组织成可供开发者、Agent Builder 和未来 Registry 理解与离线验证的 Alpha preparation 包。不是外部发布。

## B. Included capabilities

- `saee.agent-reliability`：`local_alpha`；
- `saee.evidence-evaluation`：`local_prototype`；
- 本地 MCP stdio 与 localhost HTTP Contract；
- Capability Package、集成示例、公共发现面、Phase 10.7 发现验证结果。

## C. Excluded capabilities

- `rehearse_agent` 独立服务实现；
- 公共 API、公共 MCP、SaaS、认证与多租户；
- Marketplace 上架、计费、客户数据和生产部署；
- 外部采用、生态支持或客户验证声明。

## D. Validation evidence

- `scripts/saee_capability_alpha_release_smoke.py`；
- `scripts/saee_public_capability_surface_smoke.py`；
- `scripts/saee_external_agent_discovery_validation_smoke.py`；
- `scripts/mainline_guard.py`。

## E. Known limitations

本包是引用型索引，不是独立安装包；依赖同一仓库中的规范源。它不保证第三方 Runtime 兼容，不提供公网 endpoint，也没有真实外部 Agent 或客户采用证据。

## F. Future path

下一阶段只做 Alpha Release 内部一致性验证，核对 Package、Registry、Capability Object、Runtime、MCP、HTTP 和公共发现面是否共享同一能力真值。完成验证仍不自动授权公开发布。
