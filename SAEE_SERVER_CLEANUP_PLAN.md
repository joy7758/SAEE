# SAEE Dedicated Server Cleanup Plan

状态：`executed_and_validated`  
目标实例：`i-8xOwPKN3`  
SSH 别名：`hongyan-4cj`  
公网地址：`180.76.115.193`  
盘点日期：`2026-07-11`  

本文件是破坏性操作前的人工审核清单。用户已于 2026-07-11 明确授权按本清单执行；实际执行证据见 `SAEE_SERVER_CLEANUP_EXECUTION_REPORT.md`。

```text
CLEANUP_READY_FOR_CONFIRMATION=false
cleanup_approved=true
deletion_executed=true
services_stopped=true
nginx_modified=true
saee_foundation_created=true
full_saee_discovery_release_deployed=false
```

## 1. 当前服务器摘要

| 项目 | 当前状态 |
|---|---|
| OS | Ubuntu 24.04.4 LTS |
| 磁盘 | 99G 总量，16G 已用，79G 可用，17% 使用率 |
| SSH | root SSH 可用，22/tcp 对外开放 |
| Nginx | 1.24.0，active/enabled，80/tcp 对外开放 |
| HTTPS | 443/tcp 防火墙允许，但无监听、无证书 |
| 当前网页 | `HTTP 500`；Nginx root 指向不存在的 `/opt/jdcm-signal-dashboard/site` |
| Docker | 服务运行；0 containers、0 images、3 个旧 Hongyan volumes |
| Root Cron | 0 条活动任务 |
| `/var/www` | 空 |
| `/srv` | 空 |

## 2. 删除前系统信息备份

获得明确确认后、执行任何停止或删除前，先创建 root-only 备份区：

```text
/srv/saee/config/pre-cleanup-private-20260711/
owner=root:root
mode=0700
```

只备份必要系统信息：

- OS、磁盘、网络监听和 UFW 状态；
- 已安装软件包清单；
- running/enabled systemd unit 清单；
- 当前 `nginx -T` 与 `nginx -t` 结果；
- 待移除 systemd/Nginx 配置的 root-only 副本；
- 待删除路径的 path、size、mode、mtime、SHA-256 元数据清单；
- Docker container/image/volume 清单；
- SSH 连通性验证结果。

不备份以下内容本体，只记录路径、大小、权限和摘要后删除：

- `/root/secrets/`；
- `/root/.env.external.*`；
- OpenClaw token/config/session 数据；
- BaiduPCS-Go 或 ClawHub 用户凭据配置；
- Mihomo 代理配置中的潜在凭据；
- shell、Python、Vim 等历史记录。

该私有备份不得放入 `/srv/saee/public/`，不得通过 Nginx 暴露。

## 3. 文件系统分类

### KEEP

| 路径 | 大小 | 用途 | 动作 | 理由 |
|---|---:|---|---|---|
| `/etc`, `/usr`, `/bin`, `/lib`, `/boot`, `/var/lib/systemd` | 系统 | Ubuntu 基础系统 | KEEP | 明确禁止删除 |
| `/root/.ssh`, `/.ssh` | 小 | SSH 访问 | KEEP | 保持远程管理能力 |
| `/etc/nginx/nginx.conf`, `/etc/nginx/mime.types`, Nginx package | 系统 | Web 基础能力 | KEEP | 仅重置项目 server block |
| `/etc/ufw`, UFW service | 系统 | 防火墙 | KEEP | 保留 22/80/443 策略 |
| Fail2Ban、Chrony、SSH、日志、自动更新 | 系统 | 基础运维 | KEEP | 专用服务器仍需要 |
| `/opt/bcm-agent` | 492M | 百度云监控代理 | KEEP | `bcm-agent.service`，端口 781 |
| `/opt/bsm-agent` | 33M | 百度云代理升级组件 | KEEP | `bsm-agent-upgrader.service` |
| `/opt/heyeAgent` | 544M | 百度 HIDS | KEEP | `heyeAgent-install.service` |
| `/home/opt/has` | 349M | 百度硬件健康/诊断 | KEEP | 系统运维组件 |
| `/opt/avalokita` | 3M | 被百度 `has-agent`、`bcm-agent` 引用 | KEEP | 不是旧业务项目 |
| `/opt/mellanox`, `/opt/knem-1.1.4.90mlnx3` | 107M | 网络/RDMA 驱动组件 | KEEP | 硬件与云环境组件 |
| `/opt/containerd` | 12K | containerd 配套路径 | KEEP | 先保留基础包 |
| `/root/.bashrc`, `/root/.profile` | 小 | root shell 基础配置 | KEEP | SSH 运维需要 |
| `/var/www` | 空 | 标准 Web 父目录 | KEEP | 不需要删除，SAEE 使用 `/srv/saee` |

### REMOVE CANDIDATES — 旧项目文件

| 路径/匹配范围 | 大小 | 识别用途 | 动作 | 备注 |
|---|---:|---|---|---|
| `/root/apps/` | 376M | Hongyan Workbench 及 11 个备份 | REMOVE | 完整旧项目树 |
| `/root/hongyan*.tgz*` | 约 50M+ | Hongyan 发布包和摘要 | REMOVE | 旧部署产物 |
| `/root/v4.8-workspace-*.tgz*`、manifest | 约 11M+ | 旧 Workbench 发布包 | REMOVE | 旧部署产物 |
| `/root/hongyan-workbench.tar.gz`、`hongyan-workbench-sprint31.tar.gz` | 约 14M | 旧部署包 | REMOVE | 旧项目资产 |
| `/root/deploy-4cj.sh`, `/root/fix-4cj.sh`, `/root/run-4cj-smoke.sh*` | 小 | 旧项目部署/修复脚本 | REMOVE | 不适用于 SAEE |
| `/root/hongyan-server-patches.tgz`, `/root/hongyan-compose-cors-patch.tgz` | 小 | 旧补丁 | REMOVE | 不适用于 SAEE |
| `/root/700`, `/root/chmod` | 小 | 异常遗留目录 | REMOVE | 无系统引用 |
| `/root/.openclaw/` | 157M | OpenClaw workspace、插件、sessions、logs | REMOVE | 含旧 Agent/聊天集成数据 |
| `/root/.codex/` | 217M | 旧远端 Codex 0.130 包和状态 | REMOVE | 两个 abandoned sessions |
| `/root/.npm/` | 923M | OpenClaw/Node 缓存 | REMOVE | 旧项目缓存 |
| `/root/.cache/ms-playwright` | 1.2G | 旧浏览器自动化缓存 | REMOVE | 静态 SAEE 服务器不需要 |
| `/root/.cache/pip` | 163M | 旧 Python 下载缓存 | REMOVE | 可重建缓存 |
| `/root/.docker/` | 212K | 旧 root Docker 客户端状态 | REMOVE | 先记录配置元数据，不保留凭据 |
| `/root/.config/clawhub/` | 小 | OpenClaw 用户配置 | REMOVE | 旧项目配置 |
| `/root/.config/BaiduPCS-Go/` | 小 | 用户态网盘客户端配置 | REMOVE | 不是百度云系统代理，可能含凭据 |
| `/root/secrets/` | 12K | 旧项目 secrets | REMOVE | 不备份内容 |
| `/root/.env.external.*` | 小 | Hongyan 旧环境变量 | REMOVE | 不备份内容 |
| `/root/.bash_history`, `.python_history`, `.viminfo`, `.lesshst` | 小 | 历史记录 | REMOVE | 降低旧 secrets/路径残留风险 |

预计可回收至少约 `3.0G`，不含系统日志和包缓存。

### REVIEW

| 路径/组件 | 当前状态 | 动作 | 决策建议 |
|---|---|---|---|
| Docker package + `docker.service` | 运行，无容器/镜像 | REVIEW | 保留安装；清除旧 volumes 后可选择 disable，不卸载 |
| `containerd.service` | 运行，无业务容器 | REVIEW | 若 Docker 保持 enabled 则 KEEP；否则后续单独评估 |
| `/root/.local`, `/root/.pip`, `/root/.pydistutils.cfg` | 小 | REVIEW | 可保留，不影响 SAEE 专用边界 |
| `/etc/nginx/sites-available/default` | inactive，无 enabled link | REVIEW/KEEP | 保留包示例，不会对外生效 |

## 4. 服务与启动项分类

### KEEP services

- `ssh.service`
- `nginx.service`
- `ufw.service`
- `fail2ban.service`
- `cron.service`
- `chrony.service`
- `rsyslog.service`
- `systemd-networkd.service`
- `systemd-resolved.service`
- `unattended-upgrades.service`
- `bcm-agent.service`
- `bsm-agent-upgrader.service`
- `heyeAgent-install.service`
- RDMA/Mellanox/百度硬件相关服务

### REMOVE services

| 服务/进程 | 当前状态 | 关联资产 | 计划动作 |
|---|---|---|---|
| root user `openclaw-gateway.service` | enabled/running | `/root/.openclaw`, public port 18789 | stop → disable → remove user unit |
| `openclaw.token.service` | enabled/exited | OpenClaw token/origin/base-path setup | disable → remove system unit |
| `mihomo.service` | enabled/running | `/etc/mihomo`, `/var/lib/mihomo`, `/usr/local/bin/mihomo` | stop → validate SSH/network → disable/remove |
| Codex PID `179156` | abandoned since 2026-05-20 | `/root/.codex` | terminate after backup metadata |
| Codex PID `3003460` | abandoned since 2026-06-03 | `/root/.codex` | terminate after backup metadata |

`mihomo` 必须两阶段处理：先停止，立即验证新 SSH 会话、DNS 和必要系统更新网络；若基础联网异常则回滚启动，不直接删除配置。

## 5. Docker 分类

当前：

```text
containers=0
images=0
volumes=3
volume_size=225.5K
```

REMOVE volumes：

- `hongyan-workbench_caddy_external_config`
- `hongyan-workbench_caddy_external_data`
- `hongyan-workbench_hongyan_external_data`

不执行 `docker system prune --all`；只删除上述精确白名单 volumes。

## 6. Nginx 分类

REMOVE：

```text
/etc/nginx/conf.d/jdcm-signal-dashboard.conf
```

原因：该配置是旧 JDCM dashboard，root `/opt/jdcm-signal-dashboard/site` 已不存在，当前导致公网首页返回 HTTP 500。

KEEP：Nginx package、主配置、MIME type、基础 snippets。

新配置在获得清理确认后创建：

```text
/etc/nginx/conf.d/saee.conf
document_root=/srv/saee/public
public_path=/saee/
```

旧配置删除后不立即 reload。必须先创建 SAEE 目录和最小静态占位、写入新配置、执行 `nginx -t`，成功后才 reload。

## 7. 端口目标

| 端口 | 当前进程 | 动作 |
|---:|---|---|
| 22 | SSH | KEEP |
| 80 | Nginx | KEEP，重置为 SAEE-only server block |
| 443 | 无监听，UFW allowed | KEEP firewall allowance；HTTPS 后续单独配置 |
| 781 | Baidu `bcm-agent` | KEEP |
| 18789 | OpenClaw Gateway | REMOVE |
| 18791/18792 localhost | OpenClaw Gateway | REMOVE |
| 7890/9090 localhost | Mihomo | REMOVE after connectivity validation |
| 40533 localhost | containerd | REVIEW/KEEP with containerd |

## 8. Cron 与启动状态

- root crontab：0 条活动任务；无需删除。
- `/etc/cron.d/hosteye_upgrade`：KEEP，百度 HIDS 更新。
- Ubuntu apt、logrotate、sysstat、man-db 等系统 cron：KEEP。
- `/root/.openclaw/cron/jobs.json`：随 OpenClaw 目录 REMOVE。

## 9. 获得确认后的精确执行顺序

1. 建立 root-only pre-cleanup backup，并写入 inventory/hash manifest。
2. 验证第二个 SSH 会话能够登录。
3. 停止并禁用 OpenClaw user/system units；确认端口 18789/18791/18792 消失。
4. 终止两个 abandoned Codex session；确认没有远端 Codex 残留进程。
5. 停止 Mihomo；验证 SSH、DNS 和基础网络；通过后禁用并删除其精确资产。
6. 删除三个精确命名的 Hongyan Docker volumes；不 prune 其他 Docker 状态。
7. 删除上述文件系统 REMOVE 白名单；禁止通配到 `/root/.ssh` 或系统目录。
8. 删除旧 JDCM Nginx conf，但暂不 reload。
9. 创建 `/srv/saee/{public,releases,logs,config}`；root ownership，public 默认只读。
10. 创建 `/srv/saee/SERVER_IDENTITY.json`，初始 `legacy_projects_removed` 仅在验证通过后设为 true。
11. 创建 SAEE-only Nginx 配置；运行 `nginx -t`。
12. 仅在 `nginx -t` 成功后 reload Nginx。
13. 执行 SSH、filesystem、process、port、Nginx 和 sensitive-path 验证。
14. 生成 Cleanup Execution Report；此时仍不自动部署完整 SAEE Discovery release，除非同步范围已另行确认。

## 10. 永久禁止范围

任何清理命令不得指向：

```text
/
/etc
/usr
/bin
/lib
/boot
/var/lib/systemd
/root/.ssh
/.ssh
/opt/bcm-agent
/opt/bsm-agent
/opt/heyeAgent
/home/opt/has
/opt/avalokita
/opt/mellanox
```

不得使用无边界的 `rm -rf /`、`find / -delete`、`docker system prune --all` 或全盘通配删除。

## 11. Approval Gate

```text
CLEANUP_READY_FOR_CONFIRMATION=false
DESTRUCTIVE_ACTION_PERFORMED=true
EXECUTION_VALIDATED=true
```

只有用户明确确认本文件中的 REMOVE services、REMOVE paths、三个 Docker volumes、旧 Nginx conf，以及 Mihomo 两阶段处理方式后，才进入清理执行。
