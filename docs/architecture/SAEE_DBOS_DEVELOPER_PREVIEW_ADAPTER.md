# SAEE–DBOS Developer Preview Adapter v0.1

Status: `LOCAL_READ_ONLY_COMPATIBILITY_ADAPTER`

This adapter lets SAEE read the synthetic `dbos_to_saee_envelope` produced by
the DBOS Multi-Agent Trust Demo. It strengthens Global Sensing（全局感知）and
Pareto Fitness Evaluation（帕累托适应度评价）as a bounded test-engineering
path; it does not replace the controlled SAEE / Agent Evidence integration
mainline.

## Agent-readable entry

```bash
python3 scripts/saee_evaluate_dbos_preview.py --input /path/to/dbos-demo.json
```

Input contract:

```text
dba.dbos-saee-developer-preview/v0.1
```

Output sections:

- `reliability_assessment`: existing Reliability Framework observations;
- `stability_assessment`: availability gate for repeated completed runs;
- `risk_assessment`: existing `saee.evaluate_agent_run` risk context;
- `evolution_recommendation`: advisory-only projection of that context.

## Truth boundary

The DBOS v0.1 demo contains `CREATED` Execution Object representations and
`PENDING` Evidence References. These are not completed runs or canonical
verified evidence. The expected honest result is therefore:

```text
Reliability=NOT_ASSESSED
Stability=NOT_ASSESSED
Risk=RISKS_IDENTIFIED
EvolutionRecommendation=HOLD
```

`HOLD` is a Recommendation（建议）, not a Decision（决策）, Authorization（授权）,
Permission（许可）, Command（命令）, or DBOS state transition.

The adapter does not create a new public capability, authenticate a trace,
establish evidence truth, modify DBOS, call a model or network, execute an
Agent, or grant permission. It reuses:

- `saee_backend.services.reliability_framework.assessment_adapter.assess_reliability_run`;
- `saee_backend.services.baidu_agent_readiness_service.evaluate_agent_run`.

## Responsibility and duplication check

| Question | Result |
|---|---|
| Responsibility domain | SAEE read-only evaluation compatibility |
| Problem | DBOS preview envelope had no direct bounded SAEE input adapter |
| Existing capability reused | `saee.evaluate_agent_run` and Reliability Framework |
| Duplicate evaluator created | `false` |
| DBOS execution/control added | `false` |
| DBA decision needed | ADR-017 already authorizes the bounded Developer Preview path |
