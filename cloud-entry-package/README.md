# SAEE Cloud Entry Package v0.1

## Product

```text
SAEE Agent Readiness Platform
SAEE 智能体上线准备平台
```

SAEE evaluates whether an AI Agent has sufficient execution evidence before
real-world deployment. This package is a local, read-only Alpha prepared for
Baidu Qianfan technical review.

## Public operations

Exactly two operations are public:

1. `saee.evaluate_agent_run`
2. `saee.evaluate_evidence`

`rehearse_agent`, `describe_saee`, and `compare_observed_traces` are excluded
from the product package. They remain internal engineering/debug assets.

## 30-minute reviewer path

1. Read `快速开始.md` and `capability-card.json`.
2. Run `python3 scripts/saee_cloud_entry_package_smoke.py` from the repository root.
3. Run the customer-service and coding-Agent commands in `快速开始.md`.
4. Inspect `demo/`, `screenshots/`, `architecture.png`, and `FAQ.md`.
5. Confirm every result preserves `deployment_authorized=false` and
   `production_ready=false`.

No provider credential, network access, dependency installation, cloud upload,
or customer data is required for this review path.

## Package map

- `openapi.yaml`: two-operation HTTP contract projection;
- `mcp.json`: local two-tool MCP entry;
- `capability-card.json`: Agent-readable use/non-use and composition boundary;
- `demo/`: reviewed request/response pairs;
- `security/`: consent, data, and non-authorization boundaries;
- `architecture.svg` / `architecture.png`: Baidu composition diagram;
- `screenshots/`: local demo result previews;
- `materials/SAEE_BAIDU_TECHNICAL_WHITEPAPER_V1.md`: 10-page PDF source;
- `materials/SAEE_BAIDU_DEMO_VIDEO_STORYBOARD_V1.md`: 3-minute video storyboard;
- `materials/SAEE_BAIDU_PARTNER_PRODUCT_SOLUTION_V1.docx`: human-fillable partner application attachment candidate;
- `FAQ.md`: technical and commercial-review questions.

Locally rendered review outputs are stored outside this package at
`output/pdf/SAEE_Baidu_Cloud_Technical_Whitepaper_v1.0.pdf` and
`output/video/SAEE_Baidu_Cloud_Demo_v1.0.mp4`. Their existence does not mean
they were published or submitted.

## Truth boundary

```text
package_stage=local_review_alpha
local_cli_available=true
local_stdio_mcp_available=true
remote_mcp_available=false
public_http_endpoint=false
official_qianfan_integration=false
baidu_partner_contacted=false
marketplace_submission=false
marketplace_listed=false
customer_validated=false
production_ready=false
external_action_authorized=false
```
