# SAEE 智能体商业阻塞优先级索引

状态：按五阶段依赖顺序推进；智能体验证为主；不使用真人验证。

当前第一阻塞：`production_identity_provider`  
当前工程动作：`provider_neutral_offline_signed_oidc_jwks_verifier_core`  
生产阻塞：`24` 项，关闭 `0` 项。

旧索引把 `support_contact` 置于首位，但它属于 Phase 3，现已作为历史人工复核队列被本索引取代，不再作为开发真源。

| 排名 | 阶段 | 阻塞 | 状态 |
| ---: | ---: | --- | --- |
| 1 | 1 | `production_identity_provider` | `open` |
| 2 | 1 | `oauth_oidc` | `open` |
| 3 | 1 | `rbac` | `open` |
| 4 | 1 | `tenant_storage_isolation` | `open` |
| 5 | 2 | `production_monitoring` | `open` |
| 6 | 2 | `external_alert_delivery` | `open` |
| 7 | 2 | `on_call_rotation` | `open` |
| 8 | 2 | `production_restore_policy` | `open` |
| 9 | 2 | `restore_tested` | `open` |
| 10 | 3 | `support_contact` | `open` |
| 11 | 3 | `customer_support` | `open` |
| 12 | 3 | `sla` | `open` |
| 13 | 3 | `formal_security_review` | `open` |
| 14 | 3 | `privacy_legal_review` | `open` |
| 15 | 3 | `data_processing_agreement` | `open` |
| 16 | 3 | `vulnerability_management` | `open` |
| 17 | 4 | `pricing_page` | `open` |
| 18 | 4 | `tax_review` | `open` |
| 19 | 4 | `invoice_process` | `open` |
| 20 | 4 | `refund_policy` | `open` |
| 21 | 4 | `payment_provider` | `open` |
| 22 | 4 | `tenant_billing_isolation` | `open` |
| 23 | 5 | `pilot_results` | `open` |
| 24 | 5 | `customer_validated` | `open` |

本索引只授权本地、可逆、智能体可复核的工程缺口压缩；真实 IdP、外部 JWKS、生产 token、客户验证和产品上线均保持未完成。
