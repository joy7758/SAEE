# SAEE 专用服务器清理执行报告

状态：`executed_and_validated`

执行日期：`2026-07-11`

目标实例：`i-8xOwPKN3`

公网地址：`180.76.115.193`

公开基础入口：`http://180.76.115.193/saee/`

```text
cleanup_approved=true
deletion_executed=true
keep_list_preserved=true
saee_foundation_created=true
nginx_validated=true
full_saee_discovery_release_deployed=false
production_ready=false
```

## A. 执行摘要

已按 `SAEE_SERVER_CLEANUP_PLAN.md` 的 REMOVE 白名单完成专用服务器清理，并严格保留 KEEP 清单。清理前创建了 root-only 系统信息快照；Mihomo 按“先停止、后验证、再删除”的两阶段门处理。服务器目前是 SAEE 单项目基础环境，但尚未部署完整 SAEE Agent-Native Discovery release。

## B. 清理前私有快照

路径：

```text
/srv/saee/config/pre-cleanup-private-20260711/
owner=root:root
mode=0700
files=0600
```

快照保存系统身份、服务、软件包、网络/防火墙、Docker、Nginx 和删除候选元数据，不保存待删除 secret 本体。`BACKUP_SHA256SUMS.txt` 的全部条目在清理后复验通过。该目录不位于 Nginx document root，HTTP 探测返回 `404`。

## C. 已停止并移除

- OpenClaw：root user `openclaw-gateway.service` 与 system `openclaw.token.service` 均停止、禁用并移除；18789、18791、18792 端口关闭。
- Codex：PID `179156`、`3003460` 在确认 `comm=codex` 且可执行文件位于 `/root/.codex/` 后终止。
- Mihomo：停止后，新 SSH、DNS 和不使用代理的 HTTPS 直连均通过；随后禁用并移除服务、配置、状态目录与二进制；7890、9090 端口关闭。
- Docker：仅删除三个批准的 Hongyan volumes；未执行 prune，Docker/containerd 基础能力保留。
- Nginx：删除 `/etc/nginx/conf.d/jdcm-signal-dashboard.conf`，未删除 Nginx package 或主配置。
- 文件：删除计划中列出的 Hongyan、OpenClaw、旧 Codex、缓存、凭据目录、历史文件和异常遗留路径。

删除后的精确 REMOVE 路径检查与批准通配匹配均为 `0`；活动 Nginx/systemd 配置中没有 `hongyan`、`jdcm`、`openclaw` 或 `mihomo` 项目引用。

## D. KEEP 清单验证

以下路径逐项确认存在：

```text
/root/.ssh
/etc/nginx/nginx.conf
/etc/ufw
/opt/bcm-agent
/opt/bsm-agent
/opt/heyeAgent
/home/opt/has
/opt/avalokita
/opt/mellanox
/opt/containerd
```

以下关键服务保持 active：SSH、Nginx、UFW、Fail2Ban、cron、Chrony、rsyslog、systemd-networkd、systemd-resolved、bcm-agent、bsm-agent-upgrader、heyeAgent-install。

Docker 保持 `active/enabled`；未卸载基础运行组件。

## E. 新 SAEE 基础结构

```text
/srv/saee/
├── SERVER_IDENTITY.json       root:root 0444
├── public/                    root:root 0755
│   └── saee/index.html        root:root 0444
├── releases/                  root:root 0750
├── logs/                      root:root 0750
└── config/                    root:root 0700
```

`SERVER_IDENTITY.json` 声明：

```json
{
  "server_role": "SAEE dedicated discovery server",
  "project": "SAEE",
  "environment": "public-discovery",
  "legacy_projects_removed": true,
  "runtime_services": false
}
```

## F. Nginx 状态

- 新配置：`/etc/nginx/conf.d/saee.conf`
- document root：`/srv/saee/public`
- `/`：HTTP `302` 到 `/saee/`
- `/saee/`：公网 HTTP `200`
- 私有备份探测：HTTP `404`
- `nginx -t`：PASS
- `nginx.service`：active
- 安全响应头：`X-Content-Type-Options`、`X-Frame-Options`、`Referrer-Policy`

当前仅监听 HTTP 80；443 仍只在 UFW 中保留允许规则，尚未配置 TLS 证书或 HTTPS listener。

## G. 安全与连通性检查

- 清理前、Mihomo 停止后、最终状态三次独立 SSH：PASS。
- DNS：PASS。
- 不使用代理的外部 HTTPS：HTTP `200`。
- UFW：active，仅保留既有 SSH、80、443 入站规则。
- 公共目录 symlink 数：`0`。
- 公共目录敏感信息模式匹配：`0`。
- 目标旧端口：7890、9090、18789、18791、18792 均无监听。
- 保留监听：22/SSH、80/Nginx、781/Baidu bcm-agent。
- 根盘：从清理前约 `16G/17%` 降至约 `11G/12%`，可用约 `84G`。

## H. 边界与剩余事项

1. 当前页面只是 SAEE 专用公开基础环境占位，不是完整 Discovery Layer。
2. `runtime_services=false`；未部署 API、MCP、Agent Adapter、Evidence evaluator 或动态运行时。
3. 未配置 TLS；公网目前是 HTTP。
4. 本次未声明 `production_ready`、`customer_ready`、安全认证、合规认证或商业交付。
5. 下一阶段必须单独审核拟公开文件白名单、脱敏结果、机器可读入口和 HTTPS 方案后，再同步完整 Agent-Native Discovery release。

## I. 结论

```text
SAEE_SERVER_CLEANUP_RESULT=PASS
legacy_projects_removed=true
keep_list_preserved=true
private_backup_integrity=PASS
public_foundation_http=PASS
production_ready=false
```
