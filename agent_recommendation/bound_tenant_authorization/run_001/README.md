# 绑定式租户授权链独立智能体复核

- round 1：`conditional`，4 个链路 blocker。
- round 2：`conditional`，1 个可伪造 context/permission blocker。
- round 3：`recommend`，0 个 controlled-preview blocker。
- 对抗案例：`14/14`。
- Memory 与 SQLite 均拒绝裸 tenant、伪造 capability、空 principal、伪造 source 和 permission confusion。
- HMAC capability 使用 preview JWT secret 和独立 domain separator，仅适用于单进程 controlled preview。
- capability 无独立 expiry/jti，不得长期缓存或跨进程复用；不证明生产 OIDC、KMS/HSM、密钥轮换或正式 tenant policy 审批。
