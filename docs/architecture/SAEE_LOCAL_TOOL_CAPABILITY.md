# SAEE Local Tool Capability Prototype v0.1

## 1. Purpose

The local tool prototype lets an agent-like caller submit one closed JSON request to the existing SAEE Evidence Adequacy evaluator through a stable, offline contract.

本地工具原型让智能体式调用方通过稳定离线契约，把一份封闭 JSON 请求交给现有 SAEE 证据充分性评估器。

> SAEE tool capability evaluates evidence adequacy. It does not authorize actions or certify system safety.

> SAEE 工具能力评估证据充分性，不执行授权，也不认证系统安全。

```text
Callable Capability != Autonomous Governance
Tool Output != Authorization
Evaluation Result != Deployment Decision
Observation != Evidence
```

## 2. When an Agent Should Call It

Use the local prototype only when all conditions hold:

- one local evidence package is available;
- one supported accountability claim is defined;
- the matching repository-fixed profile is known;
- the caller needs a bounded sufficiency or missing-evidence assessment;
- a human or separately authorized governance process retains decision authority.

Do not use it for runtime blocking, action authorization, malware detection, deployment approval, safety/compliance certification, legal judgment, remote resource retrieval or external code execution.

## 3. Input Contract

Schema: `agent-interface/capabilities/saee-evaluate-evidence-tool.v0.1.schema.json`

Required:

- `evidence_object`: the complete closed package expected by the canonical evaluator;
- `accountability_claim`: one of four fixed claim types;
- `evaluation_profile`: the matching repository-fixed short profile ID.

Optional:

- `observation_references`: at most 32 inert references. They are counted only, never fetched, validated as external truth, converted into evidence or returned by value.

The guard rejects requests above 1 MiB, duplicate JSON keys, invalid JSON, nesting beyond 32 levels, excessive node counts, non-JSON types, unknown claims/profiles, claim/profile mismatch, missing evidence objects and undeclared root fields.

## 4. Output Contract

Schema: `agent-interface/capabilities/saee-evaluate-evidence-output.v0.1.schema.json`

Successful guarded evaluations return:

- `SUPPORTED` / `SUFFICIENT`; or
- `INSUFFICIENT_EVIDENCE` / `INSUFFICIENT`.

Guard or evaluator input rejection returns:

- `REJECTED_INPUT`;
- `UNKNOWN` assessment;
- stable `TOOL_*` or `EVIDENCE_INPUT_SCHEMA_INVALID` reason code.

The output contains missing requirements, failed relationship IDs, evaluated field paths, fixed limitations and a mandatory boundary statement. It never returns evidence values or observation reference values.

`observation_not_used_as_evidence=true` is mandatory in every result.

## 5. Local Invocation

```bash
python3 scripts/saee_local_tool_demo.py \
  --input agent-interface/capabilities/examples/valid_supported_request.json
```

The command prints `SAEE_LOCAL_TOOL_RESULT` followed by deterministic JSON. Exit code `0` means the request was evaluated; exit code `2` means the input was rejected. A successful invocation can still report insufficient evidence.

## 6. Limitations

- local synthetic/offline research prototype only;
- no MCP, API, network service, framework integration, database or persistence;
- no observation fetch or observation-to-evidence conversion;
- no independent authenticity, identity or authorization verification;
- no production readiness, external Agent validation or customer validation;
- no authority to approve, reject, authorize, deploy, certify or make legal decisions.

## 7. Validation

```bash
python3 scripts/saee_local_tool_capability_smoke.py
```

Machine discovery must describe this as `local_tool_prototype`, not as a publicly available or production tool.
