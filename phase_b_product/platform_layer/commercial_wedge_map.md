# Commercial Wedge Map

Status: internal productization map, not a product launch.

## Canonical Commercial Identity

```text
SAEE is a competition-testing and stability-evaluation platform for AI agents
and decision policies.
```

This replaces generic "strategy evolution engine for everyone" positioning for
commercial purposes.

## Wedge Order

| Order | Wedge | Target Buyer | Why Now | Boundary |
| --- | --- | --- | --- | --- |
| 1 | AI agent evaluation and policy stress testing | AI agent teams and central AI platform groups | Buyers already understand evaluation, traces, runs, regressions, retention, and private deployment. | No private core disclosure |
| 2 | Enterprise decision-policy simulation | Narrow operational domain owners | Needs templates and service delivery after wedge 1. | Solution packs only, no kernel fork |
| 3 | Quant strategy testing | Quant and investment infrastructure teams | Requires mature data, broker, security, and workflow integrations. | Later wedge only |

## Product Layers

| Layer | Purpose | Buyer-Facing Units | Non-Disclosure Rule |
| --- | --- | --- | --- |
| SAEE Sandbox | Free or academic entry point | capped scenario runs, synthetic reports | no private kernel |
| SAEE Team Cloud | First paid managed product | seats, scenario runs, evaluated episodes, saved reports, retention | no fitness/selection/mutation/lineage internals |
| SAEE Enterprise Private Cloud | Serious-buyer deployment | annual contract, deployment tier, support tier | no source disclosure by default |
| SAEE Solution Packs | Domain workflow packaging | pack setup, pilot, onboarding, custom reports | templates are not kernels |

## Output Objects to Make Product-Legible

- scenario run;
- evaluated episode;
- policy tournament;
- stability score;
- collapse-risk summary;
- survival ranking;
- robustness comparison;
- regression report;
- retained benchmark report.

## Billing Boundary

Customer-facing billing should prefer:

```text
scenario_runs
evaluated_episodes
saved_reports
retention_window
team_seats
deployment_tier
service_pack
```

Avoid making the primary commercial meter:

```text
population_size
raw_simulation_steps
internal_mutation_count
private_fitness_evaluations
private_lineage_operations
```

## Go-To-Market Boundary

```text
mass_market_launch: false
design_partner_motion: true
paid_pilot_motion: true
public_sdk_release: false
private_cloud_package_reviewed: false
implementation_disclosed: false
```
