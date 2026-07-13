# SAEE Certificate Renewal Plan v0.1

## 1. Current status

```text
domain=redcrag.cn
canonical_url=https://redcrag.cn/
certificate_authority=Let's Encrypt
certificate_not_after=2026-10-09T11:55:43Z
certbot_timer=enabled_active
renewal_authenticator=webroot_http_01
renewal_dry_run_passed=false
active_certificate_changed_by_this_plan=false
credentials_stored_by_this_plan=false
```

当前正式证书有效，Nginx 80/443 正常，HTTP-01 Webroot 和续期后 Nginx reload hook 已配置。

## 2. Observed failure

`certbot renew --dry-run --no-random-sleep-on-renew` 的 staging 二次验证失败：

```text
challenge=http-01
result=unauthorized
secondary_response_host=domainwall.cloud.baidu.com
secondary_response_ip=220.181.33.205
secondary_response_status=403
authoritative_a_record=180.76.115.193
```

Let’s Encrypt HTTP-01 会从多个观察点读取 `/.well-known/acme-challenge/<TOKEN>`。本地、服务器直连和正式签发路径成功，但 staging 的一个二次观察点被百度域名墙拦截。因此不能把当前证书有效解释成自动续期已经可靠。

Phase 3.7 进一步确认：百度智能云官方备案文档说明，已经在其他服务商备案的域名迁移到百度智能云时仍需完成“新增接入”；未完成百度接入审核时，域名指向百度云服务会被备案监测系统阻断。该事实与二次验证返回的 `domainwall` 403 一致。

## 3. Recommended sequence

### Option A — first restore HTTP-01 consistency

优先选择，因为无需在服务器保存 DNS 凭据：

1. 在百度云域名接入/备案控制面确认 `redcrag.cn` 与当前实例、备案主体和公网 IP 的放行状态。
2. 用多个中国大陆递归 DNS 和权威 nameserver 复核 A 记录一致。
3. 从独立网络请求随机 ACME preflight 文件，确认没有返回百度 domain-wall 页面。
4. 重新运行 staging renewal dry-run。
5. 只有 dry-run 通过后，才把 `certificate_renewal_dry_run_passed` 更新为 true。

### Option B — migrate to automated DNS-01 after approval

如果 HTTP-01 的百度域名墙无法稳定消除，建议使用 DNS-01。Let’s Encrypt 要求在以下名称创建动态 TXT：

```text
record_name=_acme-challenge.redcrag.cn
record_type=TXT
record_value=<ACME_GENERATED_TOKEN_VALUE>
```

百度智能云公网 DNS API公开了添加、查询、修改和删除解析记录能力，调用需要 AK/SK 签名。迁移前需要：

- 确认 `redcrag.cn` zone 位于授权百度云账户；
- 创建专用于 ACME DNS 更新的最小权限凭据；
- 确认凭据能否限制到该 zone 和 TXT record；
- 选择经过审查的 ACME DNS hook 或独立验证执行器；
- 定义 TXT 创建、权威传播确认和删除的 fail-closed 流程；
- 将凭据保存在受控 secret store，不写入仓库、公开服务器目录、日志或报告。

本阶段没有确认可直接采用的官方 Certbot 百度 DNS plugin，因此不得假设安装一个 plugin 就能安全完成自动化。

### Option C — delegate the challenge zone

如果百度 DNS 凭据无法做到最小权限，可按 Let’s Encrypt 支持的方式，把 `_acme-challenge.redcrag.cn` 通过 CNAME 或 NS 委派到专用验证 zone。该 zone 应由独立、受限的 ACME 自动化身份管理。

## 4. DNS-01 migration validation steps

1. 记录当前证书、renewal config 和 Nginx config 的 root-only 备份与摘要。
2. 在 staging ACME 环境生成 challenge，不覆盖当前正式证书。
3. 创建唯一 TXT，轮询 `ns1.bdydns.cn`、`ns2.bdydns.cn` 直到一致。
4. 等待配置的安全传播窗口，再触发验证。
5. staging dry-run 必须 PASS。
6. 删除 challenge TXT，并验证权威 DNS 已清理。
7. 仅在明确批准后切换正式 renewal authenticator。
8. 正式续期成功后运行 `nginx -t`、reload hook 和 HTTPS hostname 验证。
9. 任何失败均保留当前有效证书和 HTTP-01 配置，不禁用现有证书。

## 5. Credential boundary

```text
required_future_secret=Baidu_DNS_scoped_AK_SK_or_delegated_zone_credential
credential_value_recorded=false
existing_Qianfan_key_reuse_for_dns=false
credential_upload_authorized=false
renewal_mode_switch_authorized=false
```

本计划不创建、不读取、不保存、不上传凭据，也不修改当前证书或 renewal authenticator。

## 6. Decision

Phase 3.7 复测结果：在不修改 Nginx、Certbot renewal config 或当前证书的情况下，`certbot renew --dry-run --no-random-sleep-on-renew` 返回退出码 0，日志记录 `all simulated renewals succeeded`。当前选择是保留 HTTP-01，不切换 DNS-01。

百度接入状态没有被本任务从控制台独立确认，因此把先前 `domainwall` 403 保留为历史故障。若未来再次出现，优先检查百度新增接入状态；若 HTTP-01 再次不稳定，再单独批准 DNS-01 或 challenge-zone delegation。
