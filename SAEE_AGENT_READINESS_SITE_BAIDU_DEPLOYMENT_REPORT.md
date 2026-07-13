# SAEE Agent Readiness Site Baidu Deployment Report

Date: `2026-07-13`

Status: `deployed_and_validated`

Latest repository synchronization target:
`phases_0_to_3_local_complete_phase_4_human_gate`.

Latest synchronization deployment:

```text
sites_version=42
sites_deployment_status=succeeded
baidu_static_file_count=113
baidu_ip_home_validation=pass
baidu_ip_agent_json_validation=pass
redcrag_https_home_validation=pass
redcrag_https_release_json_validation=pass
production_blocker_count_rendered=24
production_checks_satisfied_rendered=0
```

Human-first clarity refresh:

```text
sites_version=43
homepage_plain_chinese=true
homepage_raw_json_links=false
homepage_long_status_constants=false
technical_file_warning=true
chrome_visual_review=pass
baidu_static_file_count=112
redcrag_live_review=pass
latest_rollback=/srv/saee/releases/saee-pre-human-first-v43-20260713T041434
```

Company, research, patent-ledger, and readiness-foundation synchronization:

```text
sites_version=44
sites_deployment_status=succeeded
sites_source_commit=b47aa472e8c400af736bfe5723ff23a95bffb840
company_name_public=true
public_contact_name=张斌
public_contact_phone=18518485118
manuscript_main_route_count=36
patent_ledger_record_count=15
utility_model_count=3
invention_patent_count=12
awaiting_acceptance_document_count=1
granted_patent_count=0
pre_customer_foundation_recommendation_count=6
baidu_static_file_count=114
redcrag_home_validation=pass
redcrag_research_page_validation=pass
redcrag_research_portfolio_json_validation=pass
latest_rollback=/srv/saee/releases/saee-pre-research-patents-v44-20260712T204039
```

Patent states are synchronized from the user-provided `专利情况(2).xlsx`.
`等待受理书`, `审核中`, `修改中`, `撰写中`, and `待确认` are preserved as
workflow states and are not promoted to grant claims. The supplied ledger does
not include application numbers, acceptance notice numbers, or grant
certificates.

Human-readable structured-data viewer:

```text
sites_version=45
sites_deployment_status=succeeded
human_json_viewer=/data/?file={public_json_filename}
human_facing_json_links_routed_to_viewer=40
direct_raw_json_links_on_technical_page=0
raw_agent_contract_urls_preserved=true
same_origin_json_only=true
data_mutation=false
redcrag_for_agents_validation=pass
redcrag_data_viewer_validation=pass
latest_rollback=/srv/saee/releases/saee-pre-human-json-viewer-v45-20260712T205014
```

The viewer renders JSON objects and arrays as Chinese-labeled rows, cards, and
expandable groups. Raw JSON remains available at the canonical URLs for coding
and retrieval agents, but it is no longer the default human click target.

Security and public-architecture audit remediation:

```text
sites_version=47
sites_deployment_status=succeeded
sites_source_commit=84cc93c7be607058d08b80998d64db3a5ee58d07
safe_dom_rendering=true
persistent_browser_token_storage=false
human_json_viewer_explicit_allowlist_count=42
public_local_path_disclosure_count=0
public_security_policy=true
content_security_policy=true
strict_transport_security=true
permissions_policy=true
public_quality_gate=true
baidu_static_file_count=123
redcrag_security_page_validation=pass
redcrag_baidu_demo_page_validation=pass
redcrag_public_index_redaction_validation=pass
latest_rollback=/srv/saee/releases/saee-pre-security-hardening-v47-20260713T070028Z
nginx_config_rollback=/etc/nginx/conf.d/saee.conf.pre-v47-20260713T070028Z
```

The audit remediation removes dynamic `innerHTML` rendering and persistent
`localStorage` preview credentials from the legacy local landing demo, adds an
explicit allowlist to the public data reader, publishes a bounded vulnerability
reporting policy, adds automated public-surface checks, and generates the public
agent index with workstation paths redacted. This does not close the separate
formal penetration-test, production security-review, customer-validation, or
production-readiness gates.

## Result

```text
ssh_recovered=true
ssh_active=true
ssh_enabled=true
operator_source_unbanned=true
unrelated_fail2ban_bans_preserved=true
baidu_static_site_deployed=true
ip_entry_validated=true
server_side_tls_entry_validated=true
official_qianfan_integration=false
marketplace_submission=false
customer_validated=false
production_ready=false
```

The current public site presents `SAEE Agent Readiness Platform` and exactly
two public read-only operations:

1. `saee.evaluate_agent_run`
2. `saee.evaluate_evidence`

The synchronized development snapshot also separates two tracks:

- engineering mainline: local SAEE v1.0 stable runtime, long-horizon
  experiment layer, and v1.2 empirical alignment layer available;
- Baidu productization: 29-file Cloud Entry Package, three synthetic demos,
  10-page whitepaper, 180.021-second video, and `SAEE-v0.1-alpha` local
  release candidate validated; Phase 4 remains a human authorization gate.

## SSH recovery

The server was running and `sshd` was listening on port 22, but the operator
source address had been blocked by the existing `sshd` Fail2Ban jail. Recovery
used the Baidu VNC console to:

- confirm `sshd` was active and listening;
- enable `ssh.service` for future boots;
- identify the operator address through a bounded Nginx access-log probe;
- unban only that operator address;
- preserve all unrelated Fail2Ban bans.

Local key-based verification returned `SAEE_SSH_OK`.

## Deployment

- validated file count: `108`;
- deployment root: `/srv/saee/public/saee`;
- rollback archive: `/srv/saee/releases/saee-pre-agent-readiness-v40-20260713T0350`;
- latest rollback archive: `/srv/saee/releases/saee-pre-current-status-v42-20260713T040135`;
- current v44 rollback archive: `/srv/saee/releases/saee-pre-research-patents-v44-20260712T204039`;
- current v45 rollback archive: `/srv/saee/releases/saee-pre-human-json-viewer-v45-20260712T205014`;
- external IP entry: `http://180.76.115.193/saee/`;
- canonical HTTPS entry: `https://redcrag.cn/`;
- certificate expiry observed on server: `2026-10-09T11:55:43Z`.

The staged package passed title, ICP footer, JSON contract, symlink, local-path,
and secret-pattern checks before the atomic directory swap. Nginx configuration
validated before deployment. The previous public directory remains available
as the rollback archive above.

## Boundary

```text
Website Deployment != Product Launch
Baidu Server Hosting != Official Qianfan Integration
Local Read-Only Adapter != Remote MCP
Assessment Result != Deployment Authorization
production_ready=false
```
