# Agent Evidence Receipt v0.x Baseline Freeze

Date: 2026-07-14
Mode: read-only stabilization audit
Legacy repository: `/Users/zhangbin/GitHub/agent-evidence-layer`
Constitutional owner: `SAEE Evidence and Immune Subsystem`

This record freezes discoverable facts about the legacy Agent Evidence Project. It does not migrate source code, integrate a runtime, approve a product launch, or authorize repository consolidation.

```text
source_code_migrated=false
runtime_integrated=false
```

## Git Baseline

| Field | Frozen value |
|---|---|
| Branch | `main` |
| HEAD | `e5f3ab67dfc3f0d86c1d83c2fee8d3014a5c6219` |
| Remote | `NONE` |
| Tags | none discovered |
| Tracked dirty entries | `90` |
| Untracked entries | `435` |
| Total dirty entries | `525` |
| Status fingerprint (SHA-256) | `0414b1ce649fbbae1db8fda8b09a6192199f23578ebab91cdf02fb3696008270` |
| Tracked diff stat | `90 files changed, 34694 insertions(+), 1322 deletions(-)` |

The earlier planning number `516` is superseded by this read-time observation. The repository is not a safe migration source while the 525-entry state lacks clean provenance and a remote recovery point.

## Product And Runtime Identity

- Product identity: `Agent Evidence Receipt` / `智能体运行记录验证工具`.
- Backend classification: `baidu_cloud_single_node`.
- Public MCP endpoint: `https://redcrag.cn/mcp` using `StreamableHttp`.
- Public auxiliary endpoints: `/healthz` and `/mcp/signing-key.json`.
- Product API version: `0.2.0.dev0`.
- Runtime release commit recorded by deployment evidence: `428ad220e461c1993607b4d285d328fd4d088db2`.
- Public runtime evidence exists; this does not establish customer traffic, high availability, production SLOs, restore readiness, or SAEE integration.

## MCP Tools

The frozen public tool set is:

1. `submit_evidence_job`
2. `get_evidence_job_status`
3. `get_evidence_job_result`

Observed smoke evidence covers exact tool discovery, asynchronous job processing, signature verification, event-chain verification, source-completeness output, five artifacts, single-use download tokens, cross-tenant rejection, and test-job purge. These are bounded runtime checks, not customer validation.

## API Surface

The frozen HTTP surface is:

- `POST /v1/jobs`
- `GET /v1/jobs/{job_id}`
- `GET /v1/jobs/{job_id}/result`
- `GET /v1/artifacts/{artifact_id}`
- `POST /v1/download-tokens`

## Schemas

- `schemas/artifact_digest.schema.json`
- `schemas/manifest.schema.json`
- `schemas/normalized_event.schema.json`
- `schemas/project-ledger-entry.schema.json`
- `schemas/source_completeness.schema.json`
- `schemas/verification_receipt.schema.json`

## Deployment And Signing Assets

- Deployment shape: Baidu Cloud single-node Docker Compose.
- Host evidence: `redcrag.cn`.
- Recorded services: Redis, MCP/API, worker, cleanup, and metering components.
- Signing: Ed25519; secret material is mapped read-only and public-key metadata is exposed.
- Signature scope is package integrity. It does not prove original-event truth, provider truth, completeness beyond declared inputs, legal responsibility, or customer acceptance.

Protected evidence digests:

| Asset | SHA-256 |
|---|---|
| `deploy/aliyun-mcp/product-manifest.json` | `4255e8597b33956d18d557e43c7f58b3ca9168592a793ec94c4cab78b2b47f5c` |
| `deploy/aliyun-mcp/runtime-evidence.json` | `106bfa9587d98f95e6dd37d08c827a08a33f03d94582a238742651b742b36f8f` |
| `deploy/aliyun-mcp/marketplace/submission-status.json` | `b220c9f16f5e0249dd02499b437509a6c3092e0769340f17e80aa42074bb98c1` |

## Marketplace Relationship

- Alibaba Cloud product: `68658` / `cmapi00074658`.
- Recorded review status: `审核中`.
- Submission acceptance evidence: `true`.
- Approval: `false`.
- Listing/publication: `未上架` / `false`.
- Metering runtime enabled and verified: `false`.
- Outstanding operational items include token rotation and Chinese material synchronization.

Marketplace submission, runtime availability, listing approval, customer use, and SAEE integration are separate truth surfaces.

## Frozen Classification

### KEEP

- Product and API identities required to understand the legacy contract.
- MCP tool names and bounded public contract.
- Schema identities and receipt semantics.

### PROTECT

- Git HEAD, branch, status counts, and status fingerprint.
- Deployment, signing, runtime, and marketplace evidence.
- The three critical manifests and their hashes.
- Claims/non-claims separating runtime smoke from customer and production proof.

### MIGRATION_REQUIRED

No source file is approved for migration by this freeze. A future bounded crosswalk or adapter may be considered only after:

1. all 525 dirty entries have owner and provenance classification;
2. the intended source state has a clean immutable commit and recovery remote;
3. license and supply-chain review is complete;
4. contract/version compatibility with SAEE canonical capabilities is established;
5. the Agent Recommendation Gate authorizes a specific internal integration proposal.

### UNKNOWN

- Ownership and final disposition of the 435 untracked entries.
- Canonical remote and recovery posture.
- Real usage/customer traffic and adoption evidence.
- HA, SLO, backup, restore, and disaster-recovery readiness.
- Exact subset, if any, eligible for future migration.

## Freeze Decision

The baseline is frozen as evidence for later capability alignment, but it is not migration-ready. Phase 1 must not copy this repository or create a parallel receipt stack. It may first create a read-only contract crosswalk against SAEE's canonical capability inventory.
