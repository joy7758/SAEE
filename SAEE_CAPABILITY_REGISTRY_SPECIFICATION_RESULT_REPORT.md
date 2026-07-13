# SAEE Capability Registry Specification v0.1 Result Report

## A. Registry design summary

Phase 4.4 已实现严格、机器可读的本地 Capability Registry Specification 和首张 SAEE Capability Card。

```text
capability_id=saee.evidence-adequacy
version=0.1
lifecycle_state=LOCAL_PROTOTYPE
registry_entry_available_local=true
public_registry_available=false
marketplace_available=false
public_tool_available=false
external_validation_completed=false
adoption_validated=false
production_ready=false
```

Registry 描述能力身份、版本、状态、调用方式、契约和边界，不授予调用权限，不建立信任、采用或生产状态。

## B. Capability lifecycle

规范定义：

1. `RESEARCH_PROTOTYPE`
2. `LOCAL_PROTOTYPE`
3. `EXTERNAL_VALIDATION`
4. `PRODUCTION_CAPABILITY`

当前状态为 `LOCAL_PROTOTYPE`。公开 release 的 `stage=research_prototype` 描述公开层；Registry 的 `LOCAL_PROTOTYPE` 描述仓库内已有本地 Tool。两者作用域不同，均不表示公开或生产可用。

Validator 会拒绝没有相应 evidence 的 `EXTERNAL_VALIDATION` 和 `PRODUCTION_CAPABILITY` 状态。

## C. Capability card

Capability Card 包括：

- stable registry ID 和 manifest alias；
- capability version；
- 中英文用途；
- use/non-use cases；
- public discovery identity 与 local-only availability；
- local invocation mode；
- input/output contracts；
- limitations 与 boundary contract；
- local/synthetic validation state；
- public metadata migration state。

## D. Contract references

Input：

```text
agent-interface/capabilities/saee-evaluate-evidence-tool.v0.1.schema.json
required=evidence_object,accountability_claim,evaluation_profile
optional=observation_references
```

Output：

```text
agent-interface/capabilities/saee-evaluate-evidence-output.v0.1.schema.json
```

Validator 离线解析 9 个本地 schema、implementation、boundary、validation evidence 和 migration references，并校验 `v0.1` 版本一致性。

## E. Migration notes

三项发现漂移均已进入 versioned migration notes：

1. Public manifest 尚未引用 Local Tool schemas；
2. Public manifest 的 Observation reference 为 required，本地 Tool 为 optional；
3. Public limitations 仍包含旧 IP/HTTP/TLS 描述。

当前：

```text
known_public_surface_gap_count=3
historical_records_rewritten=false
public_metadata_migrated=false
```

没有修改 historical public-release 或重新部署公开站点。

## F. Added files

- `agent-interface/registry/saee-capability-registry.schema.v0.1.json`
- `agent-interface/registry/saee-capability-card.v0.1.json`
- `saee_backend/services/capability_registry_validator.py`
- `scripts/saee_capability_registry_smoke.py`
- `docs/architecture/SAEE_CAPABILITY_REGISTRY_SPECIFICATION.md`
- `docs/architecture/SAEE_CAPABILITY_REGISTRY_MIGRATION_NOTES.md`
- `docs/strategy/SAEE_CAPABILITY_REGISTRY_SPECIFICATION_RECOMMENDATION_GATE.md`
- `SAEE_CAPABILITY_REGISTRY_SPECIFICATION_RESULT_REPORT.md`

## G. Modified files

- `agent-interface/capabilities/saee-capability-manifest.v0.1.json`
- `scripts/saee_agent_native_capability_smoke.py`
- `agent-index.json`

Tool implementation、Evidence Adequacy evaluator 和 public-release 均未修改。

## H. Validation results

执行：

```bash
python3 scripts/saee_capability_registry_smoke.py
python3 scripts/saee_external_agent_discovery_smoke.py
python3 scripts/saee_agent_invocation_evaluation_smoke.py
python3 scripts/saee_local_tool_capability_smoke.py
python3 scripts/saee_agent_native_capability_smoke.py
python3 scripts/saee_public_discovery_validation_smoke.py
python3 scripts/saee_evidence_adequacy_smoke.py
python3 scripts/mainline_guard.py
python3 -m py_compile saee_backend/services/capability_registry_validator.py scripts/saee_capability_registry_smoke.py
git diff --check
```

聚焦结果：

- valid registry cards：`1/1`；
- invalid/hostile cards：`12/12`；
- deterministic runs：`5/5`；
- local references：`9/9`；
- production/adoption/public availability overclaims：全部拒绝；
- network/subprocess/external execution：均为 `false`。
- Python 编译和 4 个相关 JSON 文件解析：通过；
- 本阶段文件敏感值扫描：`matches=0`；
- `git diff --check` 与新增文件尾随空白检查：通过。

## I. Limitations

- 仅定义本地 Registry Schema、Card 和 Validator；
- 没有 public registry service、publishing workflow、search API、database、MCP 或 Marketplace；
- 没有 publisher identity、signature、revocation、federation 或 external trust model；
- Registry Entry 不授权调用、不证明采用、不代表生产；
- public metadata migration 尚未执行；
- `public_registry_available=false`、`adoption_validated=false`、`production_ready=false`。

## J. Recommended next PR

`SAEE Capability Registry Validation Prototype v0.1`

下一阶段应验证多版本、多状态、引用完整性、迁移兼容性和 hostile registry entries；不应直接创建 Registry 服务或 Marketplace。
