# SAEE Public Domain Identity and HTTPS Setup v0.1 报告

状态：`domain_https_deployed_with_renewal_dry_run_limitation`

执行日期：`2026-07-11`

Canonical URL：`https://redcrag.cn/`

```text
domain_identity_configured=true
https_enabled=true
icp_footer_visible=true
icp_agent_semantic_matches=0
production_ready=false
commercial_service=false
external_validation=false
agent_callable_runtime=false
certificate_renewal_dry_run_passed=false
```

## A. DNS status

权威 DNS 和中国大陆公共 DNS 返回：

```text
redcrag.cn A 180.76.115.193
AAAA none
authoritative_nameservers ns1.bdydns.cn, ns2.bdydns.cn
```

核验来源包括权威 nameserver、阿里公共 DNS、114DNS 和百度 DNS。未修改 DNS。

## B. Nginx changes

- 新增 `server_name redcrag.cn` 的独立 HTTP/HTTPS server block；
- HTTP 域名请求 301 到 `https://redcrag.cn$request_uri`；
- HTTPS document root 为 `/srv/saee/public/saee`；
- 保留 IP 入口 `/saee/` 的兼容访问；
- 域名 `/saee/` 兼容路径重定向到 canonical root；
- 保留 ACME HTTP-01 challenge 直通目录；
- 显式 `autoindex off`、UTF-8、JSON MIME 和既有安全响应头；
- 每次 reload 前运行 `nginx -t`。

## C. HTTPS status

```text
certificate_authority=Let's Encrypt
certificate_subject=CN=redcrag.cn
certificate_san=DNS:redcrag.cn
key_type=ECDSA
not_before=2026-07-11T11:55:44Z
not_after=2026-10-09T11:55:43Z
tls_listener=443
http_redirect=301
```

Certbot timer 为 `enabled/active`，Webroot renewal 参数正确，并安装了续期后 `nginx -t` 与 reload hook。

续期 dry-run 当前未通过。Let’s Encrypt staging 二次验证节点被百度 `domainwall.cloud.baidu.com` 返回 HTTP 403；权威 A 记录仍为目标服务器，当前正式证书和 HTTPS 不受影响。该问题必须在证书续期窗口前通过百度云域名接入/备案放行核验或改用受控 DNS-01 流程解决。

## D. ICP compliance display status

首页静态 HTML footer 已明显展示并链接至工信部备案管理系统：

```text
ICP备案号：晋ICP备2026006409号-1
```

展示无需登录、无需 JavaScript。备案号仅用于本次用户授权的对应网站；本任务不独立证明备案主体关系。

分层检查结果：

```text
icp_human_layer_files=1
icp_agent_semantic_matches=0
```

备案号未进入公开 `llms.txt`、`.well-known/agent-index.json`、capability manifest 或技术 schema。

## E. Canonical URLs

- `https://redcrag.cn/`
- `https://redcrag.cn/robots.txt`
- `https://redcrag.cn/sitemap.xml`
- `https://redcrag.cn/docs/overview.md`
- `https://redcrag.cn/docs/limitations.md`
- `https://redcrag.cn/examples/synthetic-review-example.json`

公开包内旧 IP canonical 引用为 0。未声明搜索引擎已经完成索引。

## F. Agent endpoints

- `https://redcrag.cn/llms.txt`
- `https://redcrag.cn/.well-known/agent-index.json`
- `https://redcrag.cn/capabilities/saee-capability-manifest.v0.1.json`

三个端点均返回 HTTP 200。JSON 解析、canonical base URL 与全部 false truth boundaries 通过验证。

## G. Security validation

- HTTP 到 HTTPS：301；
- HTTPS 证书 hostname 验证：PASS；
- `.git`、`.env`、仓库状态文件、非公开文档目录、配置目录和 `.DS_Store`：404；
- 目录列表：403；
- 公共文件数：15；
- 符号链接：0；
- 敏感值、个人路径、正向越界声明：0；
- Nginx、SSH、UFW：active；
- 监听端口：80、443，以及保留的系统运维端口。

## H. Remaining limitations

1. 证书自动续期 timer 已启用，但 dry-run 因百度域名拦截页 403 尚未闭环。
2. 当前仅覆盖 `redcrag.cn`，不覆盖未配置 DNS 的其他主机名。
3. HTTPS 证明传输与域名证书有效，不构成安全认证或能力认证。
4. ICP 展示属于 Human/Web Compliance Layer，不构成对 SAEE 能力的证明。
5. 外部智能体发现、理解、推荐和采用尚未经过独立测试。
6. 公开层仍无 API、MCP、Tool 或运行时能力。

## Final boundary

```text
Domain Identity != Product Release
HTTPS != Capability Certification
ICP Filing != Security Certification
Public Website Compliance Layer != Agent Capability Layer
production_ready=false
commercial_service=false
external_validation=false
agent_callable_runtime=false
```
