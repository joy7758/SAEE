# SAEE Request Limits v0.1

Status: local pre-commercial request resource guard, not production readiness.

## Purpose

SAEE Request Limits v0.1 adds bounded request-size controls to the public MVP
API shell. It protects local and preview deployments from oversized evaluation
requests without modifying the private core, scoring logic, runtime, API
schema, or landing page interaction.

## Controls

The API shell supports these environment variables:

```text
SAEE_MAX_AGENTS=100
SAEE_MAX_REPEAT_RUNS=10000
SAEE_MAX_TIME_HORIZON=100000
SAEE_MAX_PAYLOAD_BYTES=1048576
```

The defaults match the existing public request schema where applicable. A
shared preview can lower these values without changing the endpoint shape.

## Enforcement Point

```text
ScenarioBatchRequest
-> request limit validation
-> ExperimentService
-> public MVP evaluation pipeline
```

If a request exceeds configured bounds, `POST /experiment/run` returns HTTP
`413` with a bounded error message. The request is not passed into the
evaluation service.

## Required Design Check

1. Which evolution subsystem does this strengthen?

   It strengthens Sandbox Development and Evolutionary Archive access safety by
   preventing oversized public-shell evaluation requests.

2. Does it improve sensing, branching, variation, selection, archive, or rollback?

   It improves archive/report access safety and preview deployment controls. It
   does not change sensing, branching, mutation, selection, fitness, lineage,
   rollback, or runtime behavior.

3. Does it preserve safety, license, supply-chain, and permission boundaries?

   Yes. It adds no dependencies, performs no external calls, executes no
   external code, and does not expose private-core internals.

4. Could this change push the project back into audit-first framing?

   No. The limits protect the AI agent / policy stability-evaluation API shell.
   They are not an audit feature.

## Current State

```text
request_limits_v0_1: true
max_agents_configurable: true
max_repeat_runs_configurable: true
max_time_horizon_configurable: true
max_payload_bytes_configurable: true
default_schema_shape_preserved: true
api_schema_modified: false
runtime_modified: false
kernel_modified: false
private_core_exposed: false
production_ready: false
product_launched: false
customer_validated: false
```

## Remaining Gaps

These request limits are not a full production quota system. Formal commercial
use still needs tenant quotas, billing-aware metering, durable usage records,
rate limiting, abuse detection, and operational monitoring.

