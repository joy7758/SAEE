# SAEE External Agent Simulation Prototype v0.1

## 1. Purpose

This simulation evaluates architecture boundaries using synthetic agents. It does not validate external agents.

该模拟使用合成智能体评估架构边界，不验证真实外部智能体。

The prototype tests whether future external-Agent declarations can be screened locally before any MCP evaluation call occurs.

## 2. Simulation Architecture

```text
Synthetic Agent Identity Declaration
        ↓ identity is not authentication or trust
Synthetic Purpose and Tenant Context
        ↓ purpose is not permission; labels are not authorization
Secret and Sensitive-Data Rejection
        ↓ fail closed before MCP
Human Gate Check
        ↓ no bypass or autonomous authorization
Local MCP Prototype
        ↓ only after all preconditions pass
SAEE Evidence Adequacy Evaluation
        ↓ bounded result, no external action
```

## 3. Scenario Design

| Scenario | Boundary under test | Result |
|---|---|---|
| `TRUST_CONFUSION_AGENT` | Identity declaration treated as trust | `FAIL` |
| `PURPOSE_ESCALATION_AGENT` | Declared purpose used to escalate permission | `FAIL` |
| `TENANT_BOUNDARY_AGENT` | Cross-Tenant evidence request | `FAIL` |
| `SECRET_EXPOSURE_AGENT` | API-key/private-key/token fields | `REJECT` |
| `CORRECT_EXTERNAL_AGENT` | Bounded identity, Tenant, MCP and human gate | `PASS` |

All values are synthetic. Secret fixtures contain explicit placeholders only; no real credential is stored.

## 4. Boundary Evaluation

### Identity

The simulator requires a complete synthetic identity declaration but always reports:

```text
identity_authenticated=false
agent_trusted=false
```

`identity_as_trust=true` and `identity_as_authentication=true` fail.

### Purpose

The declared purpose is context only. Requests to authorize an action or approve deployment, or `treats_purpose_as_permission=true`, fail before MCP invocation.

### Tenant

The namespace must equal `<tenant_id>:evidence`, the requested Tenant must equal the declared Tenant, and `cross_tenant_access` must remain false. These checks simulate policy boundaries; `tenant_runtime_implemented=false` remains true at the aggregate level.

### Secret

The simulator rejects credential-bearing field names and common Token/private-key forms before any MCP call. The result contains only `SIMULATION_SECRET_EXPOSURE_REJECTED` and never reflects the submitted value.

### Human control

Autonomous authorization, Human Gate bypass, or failure to retain human authority prevents MCP invocation.

## 5. MCP Flow

Only `CORRECT_EXTERNAL_AGENT` reaches:

```text
Synthetic Agent
  -> LocalMCPServer
  -> evaluate_evidence_adequacy
  -> existing Local Tool
  -> canonical Evidence Adequacy evaluator
  -> bounded result
```

Failed and rejected scenarios report `mcp_result=NOT_CALLED`. No external runtime or network transport is involved.

## 6. Results

```text
scenario_cases=5
valid_cases=1
invalid_cases=4
all_expected_outcomes_matched=true
simulation_result=PASS
```

Machine result:

`agent-interface/integration/saee-external-agent-simulation-result.v0.1.json`

## 7. Security Boundaries

```text
Synthetic Agent != Real Agent
Identity Declaration != Authentication
Simulation Result != External Validation
Agent Purpose != Permission
Evaluation Result != Autonomous Execution
```

The simulation performs no authentication, trust establishment, Tenant isolation, authorization, persistence, external execution or deployment.

## 8. Local Demo

```bash
python3 scripts/saee_external_agent_simulation_demo.py \
  --input agent-interface/integration/simulation/correct-external-agent.json
```

## 9. Limitations

- synthetic scenarios only;
- no real Agent, LLM, external MCP Client or API;
- Tenant checks are labels and policy simulation, not isolation Runtime;
- Secret checks are bounded rejection rules, not a Secret Manager or complete DLP system;
- no OAuth, JWT, authentication or credential storage;
- no external validation, adoption, commercial Pilot or production readiness.
