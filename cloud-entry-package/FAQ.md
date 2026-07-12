# SAEE Cloud Entry Package FAQ

## Is this an official Baidu Qianfan integration?

No. It is a local two-tool contract and controlled review package.
`official_qianfan_integration=false`.

## Is this a Marketplace product already?

No. There has been no marketplace submission or listing.

## Why are there only two tools?

The product surface is intentionally narrow: evaluate one declared Agent run or
evaluate one evidence bundle. Rehearsal and trace-comparison tools remain
internal engineering surfaces.

## Does `score=75` mean 75% reliable or safe?

No. It means 75% of the explicit required evidence types are present. Source
authenticity is not verified by this Alpha.

## Does `continue` authorize deployment?

No. Every response preserves `deployment_authorized=false`. Authorization is a
separate human/platform responsibility.

## Can customer data be submitted?

No. The schema requires `customer_data_included=false`; the local Alpha is for
synthetic or separately approved sanitized inputs only.

## Does SAEE replace Qianfan governance or security?

No. SAEE supplies bounded readiness context and complements identity,
observability, policy, sandbox, authorization, and execution systems.

## What would be required before production?

Remote service security, authentication, tenant isolation, privacy/legal
review, operations/SLA, customer validation, independent interoperability,
pricing approval, and explicit external authorization remain open.
