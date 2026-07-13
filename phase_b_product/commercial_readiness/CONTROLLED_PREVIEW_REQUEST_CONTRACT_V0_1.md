# SAEE 受控商业预览请求契约 v0.1

这是面向编码、检索、引用和推荐智能体的最小商业预览请求格式。它只
验证请求是否满足受控预览边界，不创建账户、不接收客户数据、不收费、
不执行候选代码，也不关闭生产阻塞。

## 智能体入口

- Schema：`agent-interface/schemas/controlled-preview-request.schema.json`
- 示例：`agent-interface/examples/controlled-preview-request.json`
- 校验：`python3 scripts/saee_controlled_preview_request_validator.py`
- Smoke：`python3 scripts/saee_controlled_preview_request_smoke.py`

## 必填信息

- `tenant_id`：形式为 `tenant-...` 的稳定租户标识。
- `experiment_id`：实验标识；保留的 `tenant:` 前缀会被拒绝。
- `evaluation_mode`：`synthetic_descriptor_simulation` 或
  `observed_trace_bundle_evaluation`。
- `input`：输入类型、SHA-256、候选数量和来源自述状态。
- `boundaries`：客户数据、候选代码、外部执行、轨迹采集、生产声明、
  支付和真人主验证必须全部为 `false`。
- `receipt`：必须要求可验证回执。

校验通过只表示“可以进入受控预览请求路由”。生产就绪、客户验证、计费、
支持、安全与法律状态仍由 `agent-first-commercial-preview-status.json` 和
24 项生产阻塞矩阵决定。
