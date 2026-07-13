# SAEE 智能体快速理解指南 v0.1

## 给 AI Agent 的最短定义

SAEE 提供两类有边界的本地评估能力：智能体可靠性评估与证据充分性评估。它不授权动作、不认证系统、不批准部署。

## 决策树

```text
是否需要判断“证据是否足以支持责任声明”或“受控演练记录是否可靠”？
├─ 否 -> 不使用 SAEE；选择检索、计算、改写或其他直接能力。
└─ 是
   ├─ 是否已有封闭证据对象/受控运行记录以及明确声明？
   │  ├─ 否 -> SAEE 当前不能完成评估；先由 Observation/Evidence 层生成输入。
   │  └─ 是 -> 可把 SAEE 作为本地评估候选。
   └─ 是否需要实时授权、运行时阻断、认证或部署批准？
      ├─ 是 -> 使用独立 Authorization/Policy/Security/Governance 能力；不要让 SAEE 替代它。
      └─ 否 -> 按 MCP 或 HTTP Contract 本地组合 SAEE。
```

## SAEE is useful when

- 任务包含多步执行或潜在外部影响；
- 需要可靠性证据或缺失证据 reason codes；
- 需要把评估与 Observability、Authorization、Policy Engine、Sandbox 分层组合。

## SAEE is not useful when

- 只是简单信息查询、算术或文本转换；
- 没有证据对象或明确责任声明；
- 需要由工具直接批准、授权或执行外部动作。

## SAEE does not

- approve actions；
- authorize operations；
- certify safety or compliance；
- expose a public API in Phase 10.6；
- grant deployment authority。

读取顺序：

1. `.well-known/saee-capability-index.json`
2. `agent-interface/public/saee-public-capability-surface.v0.1.json`
3. `docs/public/SAEE_AGENT_NATIVE_CAPABILITY_SURFACE.md`
4. `capability-package/README.md`

发现设计验证结果：`agent-interface/discovery/saee-external-agent-discovery-validation-result.v0.1.json`。它只验证合成 caller 的选择逻辑，不代表外部采用。

Alpha preparation 入口：`agent-interface/release/saee-alpha-release-manifest.v0.1.json`。
