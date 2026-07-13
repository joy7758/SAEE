# Integration Guide

Status: conceptual integration guide only.

## Integration Pattern

```text
Application -> SAEE Product API -> Private SAEE Core -> Benchmark Reports
```

Applications should interact with SAEE through documented request and report
objects. They must not import private runtime modules or depend on kernel file
paths.

## Recommended Workflow

1. Prepare abstract scenario context.
2. Submit a bounded scenario batch request.
3. Read evaluated episode summaries.
4. Read the stability, robustness, and collapse-risk report.
5. Export a product-safe benchmark report.

## Safety Requirements

- Do not submit executable repositories as input.
- Do not submit install scripts as input.
- Do not submit secrets as input.
- Do not request permission expansion.
- Do not treat external code as genome.

## Integration Non-Claims

This guide does not represent a released SDK, production deployment, public API
contract, service-level agreement, security certification, or external
validation.
