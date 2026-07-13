# SAEE 本地复现环境要求 v0.1

“The declared environment describes the requirements needed to reproduce local SAEE artifact validation. It does not represent production deployment requirements or external validation.”

“声明的环境描述用于复现 SAEE 本地研究产物验证所需条件，不代表生产部署要求，也不代表外部验证完成。”

## 适用范围

本文件只描述 PR-1 至 PR-6 合成证据产物的本地、离线验证环境。它强化演化档案与回滚免疫系统的可复查性，不改变数字生物圈进化引擎的核心定位，不授权下载、安装或执行外部资源。

## Python 判断

- 本地观察并执行检查的版本：`Python 3.14.5`。
- 仓库可识别的语法/运行特性下限：`Python 3.10`。依据包括 `zip(..., strict=True)` 等 Python 3.10 运行特性，以及现有类型表达方式。
- 正式最低支持版本：`not_formally_declared`（尚未正式声明）。
- CI 当前使用滚动的 `python-version: "3.x"`，没有固定版本矩阵，因此不能把 Python 3.10 至 3.14 全部表述为已测试支持。

这里的 `3.10` 是排除更低版本的技术下限，不是跨版本兼容承诺。`3.14.5` 是本地观察值，也不是第三方环境证明。

## 依赖管理

仓库使用现有文件 `saee_backend/requirements.txt` 声明 Python 运行依赖。本任务只补齐已被本地验证器直接使用的依赖，没有升级其他包：

```text
pydantic>=2.0,<3.0
jsonschema>=4.18,<5.0
```

`jsonschema` 用于 `Draft202012Validator`、`FormatChecker` 及现有离线 schema 验证路径。声明依赖只说明所需版本范围；它不证明包已从可信来源取得，也不代表供应链验证、生产部署或外部复现完成。

## 只读环境检查

在已经由本地或组织批准流程准备好的环境中运行：

```bash
python3 --version
python3 -c "import jsonschema, pydantic; print(jsonschema.__version__, pydantic.__version__)"
python3 scripts/saee_environment_requirements_smoke.py
```

也可运行 Makefile 入口：

```bash
make check-saee-environment-requirements
```

成功首行必须是：

```text
SAEE_ENVIRONMENT_REQUIREMENTS_SMOKE: PASS
```

该检查读取本地 manifest 和 requirements，核对版本格式、依赖声明、当前可导入包与边界字段。它不安装包、不创建虚拟环境、不启动子进程、不访问网络。

## 离线与失败边界

- 缺少依赖时立即停止，由单独获批的依赖准备流程处理；本仓库检查不会自动联网修复。
- 清单中的 URI、身份、授权和执行效果均为合成或声明内容，不因环境通过而变成现实事实。
- `PASS` 只表示当前已准备环境满足本地验证器的声明约束。
- 尚未运行 Python 版本矩阵，也没有第三方 clean-room（干净环境）复现证据。
- `external_reproduction_completed=false`、`third_party_validation_completed=false`、`production_ready=false` 保持不变。
