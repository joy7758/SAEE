# 外部资源解析证据收据

## 要解决的威胁

智能体运行轨迹可能写着“克隆了仓库”“安装了技能”“下载了软件包”或“调用了外部工具”。这类记录只能说明运行时声称观察到了某个动作，不能单独证明：请求的资源是否解析到预期位置、发布者是谁、检索是否经过授权、获得的内容是否未变化，或后续执行效果是否确实来自这份内容。

SAEE v0.1 增加一个严格、离线、合成范围的资源解析收据，把这些声明放进同一份可重算的 JSON 证据对象。它是数字生物圈受控发育环境的免疫/档案边界，不是新的执行框架。

“Trace records what the system observed. A resource-resolution receipt binds the requested resource, resolved resource, authorization decision, retrieved content, and resulting execution effect into a separately verifiable evidence object.”

“轨迹记录系统观察到了什么。资源解析收据把请求资源、实际解析资源、授权决策、获取内容及其执行结果绑定为一个可独立验证的证据对象。”

## 请求资源与实际解析 URI

`requested_resource` 是智能体原本提出的逻辑标识，例如带版本的仓库或软件包名称。`resolved_uri` 是该标识最终对应的具体 HTTPS 地址。两者必须分别记录，不能用“请求了 X”替代“实际访问的是 Y”。

v0.1 只离线解析 URI 语法并要求规范形式。它拒绝 `file:`、`data:`、`ssh:`、`git+ssh:`、userinfo、查询参数、片段、控制字符、反斜杠、百分号别名和路径穿越。验证器不会访问 URI，也不会证明资源存在。

## 发布者身份与内容摘要是两类声明

`publisher_identity` 记录发布者身份声明，`publisher_verification_method` 记录声明采用了什么核验方法。当前正例明确写为 `declared_not_independently_verified`；SAEE 不把这个字段升级为真实身份认证。

`content_digest` 则绑定获得的字节。两份内容即使声称来自同一发布者，只要字节不同，SHA-256 就应不同；反过来，内容摘要相同也不能证明发布者身份。v0.1 为了完全离线复核，只接受尺寸受限的合成 inline bytes，并重算其 SHA-256。它不读取任意本地路径或外部资源。

## 授权、沙盒与执行效果

`policy_decision_ref` 指向允许本次解析的策略决定。收据同时把授权动作闭合为 `inspect_metadata_and_hash_only`，并固定 `install=false`、`import=false`、`execute=false`、`network=false`、`permission_expansion=false`。因此，一个资源被记录并不等于它被允许安装或执行。

`sandbox_ref` 标识受控环境；`sandbox_boundary` 固定为 `offline_non_execution_boundary`。`execution_effect_ref` 在 schema 中是可选引用，但当前 v0.1 不执行资源，任何该字段都会以 `RESOURCE_EXECUTION_EFFECT_UNBOUND` 拒绝。未来只有在独立的执行收据能同时绑定解析 URI、内容摘要、沙盒和效果时，才可以扩展这一边界。

## 完整性

`integrity.receipt_digest` 使用 SHA-256 覆盖除 `integrity` 本身之外的所有收据字段。规范化规则是项目现有的 `saee-canonical-json-v0.1`：UTF-8、对象键排序、无非必要空白、保留 Unicode。它能发现本地收据字段被修改，但不是数字签名，也不证明谁创建了收据。

## 收据证明什么

- JSON 结构符合闭合 schema；
- 请求资源与实际解析 URI 被分别记录；
- 合成 inline 内容与声明的 SHA-256 一致；
- 策略引用、只读授权边界和非执行沙盒同时存在；
- 收据自身摘要可重算；
- 所有验证都可离线、确定性执行。

## 收据不证明什么

- 不证明发布者身份真实或已获独立认证；
- 不证明 URI 对应资源存在、可访问或来自声明发布者；
- 不证明许可证、安全性、恶意代码扫描或供应链可信；
- 不证明外部下载、安装、导入或执行发生过；
- 不证明真实执行效果、生产就绪或任何法律、标准、认证合规。

## 验证示例

```bash
python3 scripts/saee_agent_cli.py validate-resource-resolution \
  --input agent-interface/examples/verified-resource-resolution.json
```

成功退出码为 `0`，`valid=true`。四个负例分别稳定返回：

- `RESOURCE_PUBLISHER_IDENTITY_REQUIRED`
- `RESOURCE_DIGEST_INVALID`
- `RESOURCE_POLICY_DECISION_REQUIRED`
- `RESOURCE_EXECUTION_EFFECT_UNBOUND`

运行完整聚焦检查：

```bash
python3 scripts/saee_resource_resolution_receipt_smoke.py
```

## 未来的 OpenTelemetry 映射边界

未来可以在独立变更中，把 OpenTelemetry 事件里的资源名、URL、时间和调用结果映射为本收据的候选输入。但 OpenTelemetry 事件本身不提供发布者真实性、内容摘要、授权决定或收据完整性；映射也不能自动升级为证据真实性。当前任务没有实现任何 OpenTelemetry 兼容层或标准映射。
