# SAEE Controlled Trial Observations

Status: local MVP demo observation records only.

This directory stores machine-checkable local observation results for the
controlled trial operator packet. The runner uses the existing public
request models, public experiment service, and in-memory experiment store.

Generate the current local observation with:

```bash
python3 scripts/saee_controlled_trial_observation_runner.py
```

Primary files:

- `local_trial_observation_input.json`
- `local_trial_observation_result.json`
- `local_trial_observation_result.md`

Boundary:

- production_ready: false
- customer_validated: false
- customer_contacted: false
- customer_data_collected: false
- product_launched: false
- external_calls_made: false
- external_ai_assistant_tested: false
- private_core_exposed: false
- blockers_closed_by_observation: 0
