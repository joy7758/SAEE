# Security Model

Status: productization security boundary, not a certification.

## Core Rule

```text
The organism may observe the world, but it may not execute the world.
```

## Input Safety

Allowed:

- abstract context;
- numeric configuration;
- local metadata;
- non-sensitive report labels.

Forbidden:

- executable repositories;
- install scripts;
- untrusted dependencies;
- secrets;
- credential material;
- external code as genome;
- permission expansion requests.

## Confidentiality Boundary

The public product layer must not expose:

- kernel implementation;
- runtime orchestration;
- fitness logic;
- selection logic;
- mutation logic;
- lineage internals;
- reproduction implementation;
- private architecture details.

## Operational Status

```text
security_certified: false
production_deployed: false
public_api_released: false
private_core_exported: false
implementation_disclosed: false
```
