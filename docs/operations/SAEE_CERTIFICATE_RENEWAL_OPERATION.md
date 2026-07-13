# SAEE Certificate Renewal Operation v0.1

## 1. Current method

```text
domain=redcrag.cn
certificate_authority=Let's Encrypt
challenge_type=webroot_http_01
webroot=/var/www/letsencrypt
challenge_url=http://redcrag.cn/.well-known/acme-challenge/<TOKEN>
renewal_timer=enabled_active
deploy_hook=nginx_test_then_reload
```

当前证书有效，Nginx、HTTP challenge route、80/443、防火墙和 reload hook 均已验证。当前 renewal config 与 Nginx config 未在 Phase 3.7 中修改。

最新 staging renewal：

```text
observed_at=2026-07-11T13:28:58Z
command=certbot renew --dry-run --no-random-sleep-on-renew
exit_code=0
result=all_simulated_renewals_succeeded
certificate_renewal_dry_run_passed=true
```

## 2. Diagnosis

续期 dry-run 的失败不是本机路由或端口故障。Let’s Encrypt staging 二次观察点收到：

```text
type=unauthorized
response_host=domainwall.cloud.baidu.com
response_status=403
```

百度智能云官方规则说明：域名即使已在其他服务商备案，迁移到百度智能云服务器时仍需完成百度“新增接入”；未通过接入审核时会被百度备案监测系统阻断。

因此没有通过修改 Nginx 或绕过备案拦截来“修复”。随后在相同配置下重试 staging renewal，二次观察点不再返回 domain-wall，dry-run 成功。百度新增接入状态没有被本任务从控制台独立确认；先前失败仍作为历史故障保留。

## 3. Chosen renewal flow

### Current method retained

保持以下项目不变：

- 当前有效证书；
- HTTP-01 renewal authenticator；
- Certbot timer；
- ACME challenge location；
- Nginx reload hook。

### Normal renewal validation

定期执行：

```bash
certbot renew --dry-run --no-random-sleep-on-renew
```

本次命令已 PASS，允许把 `certificate_renewal_dry_run_passed` 和 `renewal_reliability_fixed` 更新为 true。若未来再次失败并出现 domain-wall：

1. 备案主体登录百度智能云备案系统；
2. 核验 `redcrag.cn`、备案主体、BCC/EIP `180.76.115.193` 的新增接入状态；
3. 确认随机 HTTP challenge 文件不会返回百度拦截页；
4. 修复外部接入状态后再运行 staging dry-run。

## 4. DNS-01 fallback

若新增接入完成后 HTTP-01 仍不可靠，单独审批 DNS-01：

```text
record_name=_acme-challenge.redcrag.cn
record_type=TXT
record_value=<ACME_GENERATED_VALUE>
```

DNS-01 实施前必须具备：

- 专用 DNS 自动化身份；
- 最小权限，仅管理目标 zone 的 TXT，最好限制到 `_acme-challenge.redcrag.cn`；
- 受控 secret store；
- TXT 创建、权威传播确认和删除的 fail-closed hook；
- staging dry-run；
- 当前证书和 HTTP-01 配置的可回滚备份。

当前没有专用 DNS 凭据，没有切换 DNS-01。不得复用千帆 Key、root 凭据或其他无关 API key。

## 5. Failure prevention

- 不在域名接入状态未知时反复触发 ACME 请求；
- 不删除当前有效证书；
- 不禁用 Certbot timer；
- 不把单次正式签发解释成续期可靠；
- 不在 Nginx redirect 之前吞掉 ACME path；
- 不把 challenge token 或 DNS secret 写入仓库和报告；
- staging PASS 后再修改正式 renewal configuration。

## 6. Recovery steps

如果未来续期变更失败：

1. 保留 `/etc/letsencrypt/live/redcrag.cn/` 当前 lineage；
2. 恢复 root-only 的 renewal 和 Nginx config 备份；
3. 运行 `nginx -t`；
4. reload Nginx；
5. 使用 SNI 验证当前证书 subject、SAN 和有效期；
6. 将 renewal truth 保持 false；
7. 停止进一步 ACME 或 DNS 变更，等待人工审核。

## 7. Credential handling

```text
dns_credential_available=false
credential_stored=false
credential_output_allowed=false
private_key_output_allowed=false
unrelated_api_key_reuse_allowed=false
```

任何后续 DNS 凭据只能通过独立 secret 管理流程进入运行环境，不能写入 Git、公开目录、shell history、日志、报告或 Agent capability documents。

## 8. Limitations

- 当前证书有效，最新续期 dry-run 已通过；
- 单次 staging PASS 不能保证未来所有续期永不失败；
- 百度新增接入状态没有被本任务从控制台独立确认；
- 本文件不完成新增接入；
- DNS-01 只是已评估的 fallback，尚未配置；
- TLS 可用不构成安全认证、生产就绪或外部信任。
