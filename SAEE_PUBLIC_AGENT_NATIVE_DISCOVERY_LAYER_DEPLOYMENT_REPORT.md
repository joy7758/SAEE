# SAEE Public Agent-Native Discovery Layer v0.1 部署报告

状态：`deployed_and_validated_static_discovery_only`

执行日期：`2026-07-11`

公开入口：`http://180.76.115.193/saee/`

```text
public_discovery_deployed=true
research_prototype=true
static_only=true
production_ready=false
commercial_service=false
external_validation=false
agent_callable_runtime=false
```

## A. Public release structure

```text
saee-agent-discovery-v0.1/
├── index.html
├── README.md
├── llms.txt
├── robots.txt
├── sitemap.xml
├── PUBLIC_RELEASE_MANIFEST.json
├── PUBLIC_RELEASE_SCAN_REPORT.md
├── .well-known/agent-index.json
├── capabilities/saee-capability-manifest.v0.1.json
├── docs/
│   ├── overview.md
│   ├── architecture-overview.md
│   ├── evidence-adequacy.md
│   ├── reproducibility-overview.md
│   └── limitations.md
└── examples/synthetic-review-example.json
```

公开包总计 15 个文件，不包含符号链接或可执行文件。

## B. Uploaded files

仅上传本地目录：

```text
public-release/saee-agent-discovery-v0.1/
```

服务器版本归档：

```text
/srv/saee/releases/saee-agent-discovery-v0.1/
```

公开部署路径：

```text
/srv/saee/public/saee/
```

服务器端 15/15 文件 SHA-256 与本地包一致。

## C. Excluded files

没有上传仓库根目录。以下类别不在公开包中：

- 非公开战略和业务准备材料；
- 参与者反馈与实验准备材料；
- 非公开评估材料；
- 源代码仓库元数据；
- 凭据材料；
- 开发产物；
- 客户数据；
- API、MCP、适配器和运行时服务。

## D. Server deployment path

Nginx document root 保持 `/srv/saee/public`，SAEE 公开版本位于 `/srv/saee/public/saee/`。清理阶段的占位页已归档至：

```text
/srv/saee/releases/pre-phase3-placeholder-20260711/
```

`/srv/saee/SERVER_IDENTITY.json` 已记录 `public_discovery_deployed=true`、release v0.1 和全部 false 边界。

## E. Nginx changes

- `/` 保持 HTTP 302 到 `/saee/`；
- `/saee/` 提供静态白名单文件；
- `autoindex off` 显式关闭目录列表；
- JSON 使用 `application/json` MIME；
- `/robots.txt` 和 `/sitemap.xml` 映射到 SAEE 公开发现文件；
- 继续保留 UTF-8 和既有安全响应头；
- `nginx -t` 通过后才 reload；未修改其他服务。

## F. Public URLs

- `http://180.76.115.193/saee/`
- `http://180.76.115.193/saee/docs/overview.md`
- `http://180.76.115.193/saee/docs/architecture-overview.md`
- `http://180.76.115.193/saee/docs/evidence-adequacy.md`
- `http://180.76.115.193/saee/docs/reproducibility-overview.md`
- `http://180.76.115.193/saee/docs/limitations.md`
- `http://180.76.115.193/saee/examples/synthetic-review-example.json`

未声明搜索引擎已经完成索引。

## G. Agent discovery endpoints

- `http://180.76.115.193/saee/llms.txt`
- `http://180.76.115.193/saee/.well-known/agent-index.json`
- `http://180.76.115.193/saee/capabilities/saee-capability-manifest.v0.1.json`
- `http://180.76.115.193/saee/robots.txt`
- `http://180.76.115.193/saee/sitemap.xml`

以上端点均返回 HTTP 200；两个 JSON 端点通过解析和关键字段验证。

## H. Security scan results

本地和服务器端扫描均通过：

```text
release_files=15
allowlist_mismatch_count=0
non_public_term_matches=0
sensitive_value_matches=0
personal_locator_matches=0
positive_forbidden_claim_matches=0
json_parse_failures=0
symlink_count=0
```

公网负向探测结果：`.git`、`.env`、`AGENTS.md`、`PROJECT_STATUS.md`、非公开文档目录、服务器配置目录、清理备份和 `.DS_Store` 均返回 403/404。目录列表返回 403，未暴露文件清单。

## I. Validation results

- `SAEE_PUBLIC_AGENT_DISCOVERY_RELEASE_SMOKE: PASS`
- `SAEE_AGENT_NATIVE_CAPABILITY_SMOKE: PASS`
- `SAEE_AGENT_INTERFACE_SMOKE: PASS`
- `MAINLINE_GUARD: PASS`
- `PUBLIC_LINK_AND_FORMAT_CHECK: PASS`
- `REMOTE_STAGED_RELEASE_VALIDATION: PASS`
- `REMOTE_PUBLIC_SECURITY_CHECK: PASS`
- `PUBLIC_JSON_CONTRACT_CHECK: PASS`
- `PUBLIC_NEGATIVE_EXPOSURE_CHECK: PASS`
- `nginx -t`: PASS

## J. Remaining limitations

1. 当前是 HTTP IP 入口，没有域名和 TLS。
2. 公开发现不证明外部智能体已发现、正确理解、推荐或采用 SAEE。
3. 公开层不提供 API、MCP、Tool、运行时适配器或动态执行能力。
4. 合成示例不是客户数据、真实智能体证据或外部验证结果。
5. SAEE 仍不是安全认证、法律判断、监管合规结论、部署批准或生产治理保证。

## Final boundary

```text
Public Discovery Layer != Product Release
Agent Discovery != Agent Adoption
Public Documentation != Capability Certification
production_ready=false
commercial_service=false
external_validation=false
```
