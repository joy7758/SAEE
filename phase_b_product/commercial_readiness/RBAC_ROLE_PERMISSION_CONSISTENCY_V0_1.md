# RBAC 角色—权限—路由一致性 v0.1

rbac_role_permission_consistency_v0_1: true
scope: local_phase_1_rbac_template_consistency
status: pass_local_template_consistency
production_auth_ready: false
external_identity_provider_contacted: false
blockers_closed: 0

## 验证内容

- 角色名、角色权限列表和路由作用域不得重复。
- 不接受角色或权限通配符。
- 每个路由引用的角色必须存在。
- 每个获准角色必须真正拥有该路由声明的 `required_permission`。
- 模板不得把生产认证、外部调用、客户验证或发布状态写成 `true`。
- 未知角色和未知路由保持默认拒绝。

运行：

```bash
python3 scripts/saee_rbac_role_permission_consistency_profile.py
python3 scripts/saee_rbac_policy_consistency_smoke.py
```

该证据只用于第一阶段本地准备，不启用 OAuth/OIDC，不接触身份供应商，也不关闭生产 blocker。
