# SAEE Commercial Blocker Dependency Plan

Status: local commercial blocker dependency planning, not production readiness.

This directory contains generated local planning artifacts that stage the 24
current production-launch blockers into dependency-aware phases.

It does not execute blocker work, close blockers, contact customers, call
external services, launch product, claim customer validation, claim production
readiness, or expose private core.

Primary files:

```text
dependency_plan.local.json
dependency_plan.local.md
dependency_plan.local.csv
```

Generate them with:

```bash
python3 scripts/saee_commercial_blocker_dependency_plan.py
```

Boundary:

```yaml
plan_scope: local_commercial_blocker_dependency_planning
production_launch_status: hold
production_blocker_count: 24
planned_blocker_count: 24
phase_count: 5
blockers_closed_by_plan: 0
execution_authorized: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
external_calls_made: false
```
